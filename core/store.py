"""Durable task CAS, side-effect claims and shared quota reservations."""
from __future__ import annotations
from contextlib import contextmanager
from pathlib import Path
import json
import sqlite3
import time
import uuid

class Conflict(ValueError):pass
class BudgetExceeded(ValueError):pass

class Store:
    def __init__(self,path):
        self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.connect() as db:
            db.executescript('''
            CREATE TABLE IF NOT EXISTS tasks(id TEXT PRIMARY KEY, revision INTEGER NOT NULL, provider TEXT NOT NULL,
              account TEXT NOT NULL, action TEXT NOT NULL, start REAL NOT NULL, end REAL NOT NULL,
              state TEXT NOT NULL, origin TEXT NOT NULL, pinned INTEGER NOT NULL, params TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS actions(key TEXT PRIMARY KEY,state TEXT NOT NULL,provider TEXT NOT NULL,
              account TEXT NOT NULL,kind TEXT NOT NULL,created REAL NOT NULL,receipt TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS reservations(action_key TEXT NOT NULL,bucket TEXT NOT NULL,window TEXT NOT NULL,
              PRIMARY KEY(action_key,bucket,window));
            CREATE TABLE IF NOT EXISTS observations(key TEXT PRIMARY KEY,provider TEXT NOT NULL,account TEXT NOT NULL,
              hour INTEGER NOT NULL,score REAL NOT NULL,at REAL NOT NULL,interests TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS inbox(key TEXT PRIMARY KEY,provider TEXT NOT NULL,account TEXT NOT NULL,
              stream TEXT NOT NULL,payload TEXT NOT NULL,state TEXT NOT NULL,attempts INTEGER NOT NULL DEFAULT 0,
              next_attempt REAL NOT NULL DEFAULT 0,code TEXT NOT NULL DEFAULT '');
            CREATE TABLE IF NOT EXISTS cursors(provider TEXT NOT NULL,account TEXT NOT NULL,stream TEXT NOT NULL,
              value TEXT NOT NULL,PRIMARY KEY(provider,account,stream));
            CREATE TABLE IF NOT EXISTS memory_outbox(key TEXT PRIMARY KEY,payload TEXT NOT NULL,state TEXT NOT NULL,
              attempts INTEGER NOT NULL DEFAULT 0,next_attempt REAL NOT NULL DEFAULT 0,code TEXT NOT NULL DEFAULT '');
            CREATE TABLE IF NOT EXISTS budget_baselines(bucket TEXT NOT NULL,window TEXT NOT NULL,amount INTEGER NOT NULL,
              PRIMARY KEY(bucket,window));
            CREATE TABLE IF NOT EXISTS read_content(provider TEXT NOT NULL,account TEXT NOT NULL,external_id TEXT NOT NULL,at REAL NOT NULL,
              PRIMARY KEY(provider,account,external_id));
            PRAGMA user_version=5;
            ''')
        self.path.chmod(0o600)

    @contextmanager
    def connect(self):
        db=sqlite3.connect(self.path,timeout=10);db.row_factory=sqlite3.Row
        try:
            with db:yield db
        finally:db.close()

    def tasks(self,start=0,end=1e20):
        with self.connect() as db:
            return [self._task(r) for r in db.execute('SELECT * FROM tasks WHERE end>? AND start<? ORDER BY start,id',(start,end))]

    @staticmethod
    def _task(row):
        value=dict(row);value['params']=json.loads(value['params']);value['pinned']=bool(value['pinned']);return value

    def create_task(self,provider,account,action,start,end,params=None,*,origin='manual',pinned=True,task_id=None):
        if not 0<=start<end:raise ValueError('invalid_window')
        key=task_id or uuid.uuid4().hex
        with self.connect() as db:
            db.execute('INSERT INTO tasks VALUES(?,1,?,?,?,?,?,\'planned\',?,?,?)',
                       (key,provider,account,action,start,end,origin,int(pinned),json.dumps(params or {})))
        return key

    def change_task(self,key,revision,*,start=None,end=None,cancel=False):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row=db.execute('SELECT * FROM tasks WHERE id=?',(key,)).fetchone()
            if not row or row['revision']!=revision or row['state']!='planned':raise Conflict('task_changed_or_started')
            a=row['start'] if start is None else start;b=row['end'] if end is None else end
            if not 0<=a<b:raise ValueError('invalid_window')
            db.execute('UPDATE tasks SET start=?,end=?,state=?,pinned=1,revision=revision+1 WHERE id=?',
                       (a,b,'cancelled' if cancel else 'planned',key))

    def claim_task(self,key,now):
        with self.connect() as db:
            result=db.execute("UPDATE tasks SET state='executing',revision=revision+1 WHERE id=? AND state='planned' AND start<=? AND end>?",(key,now,now))
            return result.rowcount==1

    def finish_task(self,key,state):
        if state not in {'succeeded','failed','unknown','cancelled','skipped'}:raise ValueError('invalid_state')
        with self.connect() as db:
            db.execute("UPDATE tasks SET state=?,revision=revision+1 WHERE id=? AND state='executing'",(state,key))

    def expire(self,now):
        with self.connect() as db:db.execute("UPDATE tasks SET state='skipped',revision=revision+1 WHERE state='planned' AND end<=?",(now,))

    def recover(self):
        with self.connect() as db:
            db.execute("UPDATE tasks SET state='unknown',revision=revision+1 WHERE state='executing'")
            db.execute("UPDATE actions SET state='unknown' WHERE state='executing'")
            db.execute("UPDATE inbox SET state='pending' WHERE state='generating'")

    def claim_action(self,key,provider,account,kind,limits,now=None):
        """limits = [(bucket, window_key, hard_max)]. Failed confirmed actions release slots; unknown retain them."""
        now=time.time() if now is None else now
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute('SELECT 1 FROM actions WHERE key=?',(key,)).fetchone():return False
            for bucket,window,maximum in limits:
                used=db.execute('SELECT COUNT(*) FROM reservations WHERE bucket=? AND window=?',(bucket,window)).fetchone()[0]
                baseline=db.execute('SELECT amount FROM budget_baselines WHERE bucket=? AND window=?',(bucket,window)).fetchone()
                if used+(baseline[0] if baseline else 0)>=maximum:raise BudgetExceeded(bucket)
            db.execute("INSERT INTO actions VALUES(?,'executing',?,?,?,?,?)",(key,provider,account,kind,now,'{}'))
            db.executemany('INSERT INTO reservations VALUES(?,?,?)',[(key,b,w) for b,w,_ in limits])
        return True

    def import_budget_baseline(self,bucket,window,amount):
        import math
        if not isinstance(amount,(int,float)) or not math.isfinite(amount) or amount<0:raise ValueError('invalid_budget_baseline')
        with self.connect() as db:db.execute('INSERT INTO budget_baselines VALUES(?,?,?) ON CONFLICT(bucket,window) DO UPDATE SET amount=MAX(amount,excluded.amount)',(bucket,window,math.ceil(amount)))

    def finish_action(self,key,receipt):
        from dataclasses import asdict
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            result=db.execute("UPDATE actions SET state=?,receipt=? WHERE key=? AND state='executing'",(receipt.state,json.dumps(asdict(receipt)),key))
            if result.rowcount!=1:raise Conflict('action_not_executing')
            if receipt.state=='failed':db.execute('DELETE FROM reservations WHERE action_key=?',(key,))

    def action(self,key):
        with self.connect() as db:
            row=db.execute('SELECT * FROM actions WHERE key=?',(key,)).fetchone()
            return dict(row) if row else None

    def actions(self,limit=100):
        with self.connect() as db:return [dict(r) for r in db.execute('SELECT * FROM actions ORDER BY created DESC LIMIT ?',(max(1,min(limit,500)),))]

    def mark_read(self,provider,account,external_id,at):
        with self.connect() as db:db.execute('INSERT INTO read_content VALUES(?,?,?,?) ON CONFLICT(provider,account,external_id) DO UPDATE SET at=MAX(at,excluded.at)',(provider,account,external_id,at))

    def observe(self,content,evaluation,hour,now):
        if not 0<=hour<24:raise ValueError('invalid_hour')
        with self.connect() as db:db.execute('INSERT OR IGNORE INTO observations VALUES(?,?,?,?,?,?,?)',
            (content.key,content.provider,content.account,hour,evaluation.score,now,json.dumps(evaluation.interests)))

    def preferences(self,now,half_life_days=14):
        if half_life_days<=0:raise ValueError('invalid_half_life')
        with self.connect() as db:rows=db.execute('SELECT * FROM observations').fetchall()
        groups={}
        for r in rows:
            key=(r['provider'],r['account'],r['hour']);weight=2**(-max(0,now-r['at'])/(half_life_days*86400))
            item=groups.setdefault(key,{'provider':key[0],'account':key[1],'hour':key[2],'count':0,'weight':0,'score_sum':0})
            item['count']+=1;item['weight']+=weight;item['score_sum']+=r['score']*weight
        return [{**x,'score':x['score_sum']/x['weight'] if x['weight'] else 0} for x in groups.values()]

    def setting(self,key,default=None):
        with self.connect() as db:row=db.execute('SELECT value FROM settings WHERE key=?',(key,)).fetchone()
        return json.loads(row[0]) if row else default

    def set_setting(self,key,value):
        with self.connect() as db:db.execute('INSERT OR REPLACE INTO settings VALUES(?,?)',(key,json.dumps(value)))

    def ingest(self,provider,account,stream,events,cursor,*,initial_ignore=True):
        """Persist events BEFORE advancing a stream checkpoint, atomically."""
        from dataclasses import asdict
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            first=db.execute('SELECT value FROM cursors WHERE provider=? AND account=? AND stream=?',(provider,account,stream)).fetchone() is None
            for event in events:
                if (event.provider,event.account,event.stream)!=(provider,account,stream):raise ValueError('event_scope_mismatch')
                db.execute('INSERT OR IGNORE INTO inbox(key,provider,account,stream,payload,state) VALUES(?,?,?,?,?,?)',
                    (event.key,provider,account,stream,json.dumps(asdict(event)), 'ignored' if first and initial_ignore else 'pending'))
            db.execute('INSERT OR REPLACE INTO cursors VALUES(?,?,?,?)',(provider,account,stream,json.dumps(cursor)))

    def cursor(self,provider,account,stream):
        with self.connect() as db:row=db.execute('SELECT value FROM cursors WHERE provider=? AND account=? AND stream=?',(provider,account,stream)).fetchone()
        return json.loads(row[0]) if row else None

    def pending_events(self,now,limit=10):
        with self.connect() as db:return [dict(row) for row in db.execute("SELECT * FROM inbox WHERE state='pending' AND attempts<3 AND next_attempt<=? ORDER BY rowid LIMIT ?",(now,limit))]

    def claim_event(self,key):
        with self.connect() as db:return db.execute("UPDATE inbox SET state='generating',attempts=attempts+1 WHERE key=? AND state='pending' AND attempts<3",(key,)).rowcount==1

    def finish_event(self,key,state,code='',retry_at=0):
        if state not in {'pending','succeeded','unknown','failed','ignored'}:raise ValueError('invalid_inbox_state')
        with self.connect() as db:db.execute("UPDATE inbox SET state=CASE WHEN ?='pending' AND attempts>=3 THEN 'failed' ELSE ? END,code=?,next_attempt=? WHERE key=?",(state,state,code,retry_at,key))

    def apply_daily_plan(self,day,fingerprint,tasks,now):
        """Replace only unpinned future automatic slots, atomically. Never resurrect manual overrides."""
        import math
        validated=[]
        for index,task in enumerate(tasks):
            a,b=task['start'],task['end']
            if type(a)not in (int,float) or type(b)not in (int,float) or not math.isfinite(a+b) or not 0<=a<b:raise ValueError('invalid_plan_window')
            if b<=now:continue
            slot=f"{day}:{task.get('source_window',task['window_index'])}:{task['provider']}:{task['account']}"
            key=f'plan:{day}:{fingerprint}:{index}'
            params={**task.get('params',{}),'_planner_slot':slot}
            validated.append((key,task['provider'],task['account'],task['action'],a,b,json.dumps(params),slot))
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            previous=db.execute("SELECT * FROM tasks WHERE origin='automatic' AND id LIKE ?",(f'plan:{day}:%',)).fetchall()
            blocked={json.loads(row['params']).get('_planner_slot') for row in previous if row['pinned'] or row['state'] not in {'planned','skipped','cancelled'}}
            retained=set()
            for key,pid,aid,kind,a,b,params,slot in validated:
                if slot in blocked:continue
                # Reuse the same live event when only planner settings/params changed.
                existing=next((r for r in previous if r['state']=='planned' and not r['pinned'] and r['id'] not in retained and (r['provider'],r['account'],r['action'],r['start'],r['end'])==(pid,aid,kind,a,b)),None)
                if existing:
                    retained.add(existing['id'])
                    if existing['params']!=params:db.execute('UPDATE tasks SET params=?,revision=revision+1 WHERE id=?',(params,existing['id']))
                else:
                    if db.execute('SELECT 1 FROM tasks WHERE id=?',(key,)).fetchone():key+=':'+uuid.uuid4().hex[:10]
                    db.execute("INSERT OR IGNORE INTO tasks VALUES(?,1,?,?,?,?,?,'planned','automatic',0,?)",(key,pid,aid,kind,a,b,params))
                    retained.add(key)
            for row in previous:
                if row['state']=='planned' and not row['pinned'] and row['id'] not in retained:
                    params={**json.loads(row['params']),'_superseded':True}
                    db.execute("UPDATE tasks SET state='cancelled',params=?,revision=revision+1 WHERE id=?",(json.dumps(params),row['id']))
            db.execute('INSERT OR REPLACE INTO settings VALUES(?,?)',('plan:'+day,json.dumps({'complete':True,'fingerprint':fingerprint,'at':now})))

    def enqueue_memory(self,key,payload):
        with self.connect() as db:db.execute("INSERT OR IGNORE INTO memory_outbox(key,payload,state) VALUES(?,?,'pending')",(key,json.dumps(payload)))

    def pending_memory(self,now,limit=20):
        with self.connect() as db:return [dict(r) for r in db.execute("SELECT * FROM memory_outbox WHERE state='pending' AND next_attempt<=? ORDER BY rowid LIMIT ?",(now,limit))]

    def finish_memory(self,key,saved,now,code=''):
        with self.connect() as db:db.execute("UPDATE memory_outbox SET state=?,attempts=attempts+1,next_attempt=?,code=? WHERE key=?",('saved' if saved else 'pending',now+900,code,key))

    def retire_memory(self,key,reason):
        state='superseded' if reason=='generation_changed' else 'review_required'
        with self.connect() as db:db.execute('UPDATE memory_outbox SET state=?,code=? WHERE key=?',(state,reason,key))

    def memory_status(self):
        with self.connect() as db:return {r['state']:r['count'] for r in db.execute('SELECT state,COUNT(*) AS count FROM memory_outbox GROUP BY state')}

    def observed_ids(self,provider,account,since):
        with self.connect() as db:rows=db.execute('SELECT key FROM observations WHERE provider=? AND account=? AND at>=?',(provider,account,since)).fetchall()
        prefix=f'{provider}:{account}:'
        values={row['key'][len(prefix):] for row in rows if row['key'].startswith(prefix)}
        with self.connect() as db:values.update(row[0] for row in db.execute('SELECT external_id FROM read_content WHERE provider=? AND account=? AND at>=?',(provider,account,since)))
        return sorted(values)
