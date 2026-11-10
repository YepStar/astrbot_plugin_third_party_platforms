"""Import historical receipts, budget baselines and evidenced browsing observations."""
import json,sqlite3,math
from datetime import datetime
from zoneinfo import ZoneInfo
from .core.models import Content,Evaluation

def import_history(root,store,record,load,offline_db):
    budgets={};counts={'observations':0,'candidate_review':0}
    def add(bucket,window,amount):
        if isinstance(amount,(int,float)) and math.isfinite(amount) and amount>0:
            budgets[(bucket,window)]=budgets.get((bucket,window),0)+amount
    base=root/'plugin_data/astrbot_plugin_bilibili_ai_bot';database=base/'bilibot.sqlite3'
    if database.exists():
        db=offline_db(database);db.row_factory=sqlite3.Row
        try:
            mapping={'behavior:global:day':'all','behavior:global:minute':'minute',
                'behavior:comment_reply:day':'bilibili:default:reply','behavior:private_reply:day':'bilibili:default:private_reply',
                'behavior:post_dynamic:day':'bilibili:default:dynamic','behavior:proactive_comment:day':'bilibili:default:comment'}
            for row in db.execute('SELECT bucket,window_key,count FROM counters'):
                if row['bucket'] in mapping:add(mapping[row['bucket']],row['window_key'],row['count'])
            for row in db.execute('SELECT key,kind,target_id,state FROM actions'):
                state='succeeded' if row['state']=='succeeded' else 'failed' if row['state'] in {'failed','cancelled','rejected'} else 'unknown'
                record('legacy_action:bilibili:'+row['key'],'bilibili','default',row['kind'],state)
                if row['kind']=='proactive_comment':record('comment:bilibili:default:'+row['target_id'],'bilibili','default','comment',state)
                if row['kind']=='proactive_owner_recommend':
                    # Some old keys suffix the video; preserve both safe identifiers if available.
                    target=row['key'].split(':')[-1]
                    if target.startswith('BV'):record('legacy_owner_share:bilibili:default:'+target,'bilibili','default','owner_share',state)
        finally:db.close()
    for row in load(base/'watch_log.json',[]):
        if not isinstance(row,dict) or not row.get('bvid'):continue
        try:read_at=datetime.strptime(row['time'],'%Y-%m-%d %H:%M').replace(tzinfo=ZoneInfo('Asia/Shanghai')).timestamp()
        except (ValueError,KeyError,TypeError):read_at=0
        store.mark_read('bilibili','default',row['bvid'],read_at)
        score=row.get('score');reason=row.get('score_reason','')
        if type(score) not in (int,float) or not math.isfinite(score) or not 1<=score<=10 or not reason:continue
        try:dt=datetime.strptime(row['time'],'%Y-%m-%d %H:%M').replace(tzinfo=ZoneInfo('Asia/Shanghai'))
        except (ValueError,KeyError,TypeError):continue
        content=Content('bilibili','default',row['bvid'],'https://www.bilibili.com/video/'+row['bvid'],str(row.get('title','')),str(row.get('content_summary','')))
        store.observe(content,Evaluation(score,str(reason),'legacy watch record'),dt.hour,dt.timestamp());counts['observations']+=1
    base=root/'plugin_data/astrbot_plugin_xiaoheihe_adapter';database=base/'xiaoheihe.db'
    if database.exists():
        db=offline_db(database);db.row_factory=sqlite3.Row
        try:
            for row in db.execute('SELECT profile_id,parent_comment_id,status FROM outgoing_replies'):
                if row['parent_comment_id']:
                    record(f"reply:xiaoheihe:{row['profile_id']}:reply:{row['parent_comment_id']}",'xiaoheihe',row['profile_id'],'reply','succeeded' if row['status'] in {'sent','succeeded','confirmed'} else 'unknown')
            for row in db.execute('SELECT profile_id,day,reply_count,proactive_count FROM daily_counters'):
                add(f"xiaoheihe:{row['profile_id']}:reply",row['day'],row['reply_count'])
                add('all',row['day'],row['reply_count']+row['proactive_count'])
            pending=[dict(row) for row in db.execute("SELECT id,profile_id,post_id,status FROM feed_candidates WHERE status NOT IN ('sent','rejected','expired')")]
            store.set_setting('legacy_candidate_review',pending);counts['candidate_review']=len(pending)
        finally:db.close()
    for row in load(root/'plugin_data/astrbot_plugin_xiaoheihe_adapter/browse_journal.json',{}).get('observations',[]):
        if isinstance(row,dict) and row.get('post_id') and isinstance(row.get('at'),(int,float)):
            store.mark_read('xiaoheihe','default',str(row['post_id']),row['at'])
    for provider,path,account in [('bilibili',root/'plugin_data/astrbot_plugin_bilibili_ai_bot/owner_recommend_log.json','default'),
                                  ('xiaoheihe',root/'plugin_data/astrbot_plugin_xiaoheihe_adapter/browse_journal.json','default')]:
        raw=load(path,{})
        rows=list(raw.values()) if provider=='bilibili' else raw.get('shares',[])
        latest=0
        for row in rows:
            if not isinstance(row,dict):continue
            at=row.get('at') or row.get('time') or row.get('attempted_at')
            try:
                timestamp=float(at) if isinstance(at,(int,float)) else datetime.strptime(str(at),'%Y-%m-%d %H:%M').replace(tzinfo=ZoneInfo('Asia/Shanghai')).timestamp()
            except (ValueError,TypeError):continue
            day=datetime.fromtimestamp(timestamp,ZoneInfo('Asia/Shanghai')).date().isoformat()
            add(f'{provider}:{account}:owner_share',day,1);latest=max(latest,timestamp)
        if latest:store.set_setting(f'last_owner_share:{provider}:{account}',latest)
    for (bucket,window),amount in budgets.items():store.import_budget_baseline(bucket,window,amount)
    counts['budget_windows']=len(budgets)
    return counts
