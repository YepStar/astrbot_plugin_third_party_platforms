"""Timezone-aware windows; overlaps are valid, task claims decide execution."""
from datetime import datetime,timedelta,time
from zoneinfo import ZoneInfo
import hashlib


def window_for(day,window,timezone='Asia/Shanghai'):
    zone=ZoneInfo(timezone)
    a,b=window.split('-')
    def parse(value):
        h,m=map(int,value.strip().split(':'));return time(h,m)
    start=datetime.combine(day,parse(a),zone);end=datetime.combine(day,parse(b),zone)
    if end<=start:end+=timedelta(days=1)
    return start.timestamp(),end.timestamp()


def choose_provider(candidates,preferences,hour,seed,exploration=0.15,weights=None):
    if not candidates:raise ValueError('no_eligible_provider')
    if not 0<=exploration<=1:raise ValueError('invalid_exploration')
    if weights and any(p in weights for p,_ in candidates):
        import math
        if any(type(v)not in (int,float) or not math.isfinite(v) or not 0<=v<=100 for v in weights.values()):raise ValueError('invalid_platform_weights')
        grouped={p:[c for c in candidates if c[0]==p] for p in sorted({c[0] for c in candidates})}
        def automatic_mass(pid):
            rows=[x for x in preferences if x['provider']==pid and x['hour']==hour]
            return max(.1,max((5+(x['score']-5)*min(1,x['weight']/5) for x in rows),default=5)/5)
        masses=[(p,weights[p] if p in weights else automatic_mass(p)) for p in grouped]
        total=math.fsum(v for _,v in masses)
        if total<=0:raise ValueError('no_eligible_provider')
        draw=int(hashlib.sha256(f'{seed}|platform'.encode()).hexdigest()[:12],16)/16**12*total
        selected=next(p for p,v in masses if v>0)
        for pid,mass in masses:
            if mass<=0:continue
            selected=pid;draw-=mass
            if draw<0:break
        return choose_provider(grouped[selected],preferences,hour,str(seed)+'|account',exploration)
    number=int(hashlib.sha256(str(seed).encode()).hexdigest()[:12],16)
    if number/16**12<exploration:return candidates[number%len(candidates)]
    def rank(candidate):
        rows=[x for x in preferences if (x['provider'],x['account'],x['hour'])==(*candidate,hour)]
        if not rows:return 5.0
        x=rows[0];confidence=min(1,x['weight']/5)
        return 5+(x['score']-5)*confidence
    return max(candidates,key=lambda c:(rank(c),hashlib.sha256(f'{seed}|{c}'.encode()).hexdigest()))

class Planner:
    def __init__(self,store,timezone='Asia/Shanghai'):self.store=store;self.timezone=timezone

    def ensure_day(self,day,windows,candidates,*,round_limit=2,now,exploration=.15):
        """Deterministic fallback; never overwrite manually pinned/cancelled tasks."""
        if not candidates:return []
        import sqlite3
        result=[];prefs=self.store.preferences(now)
        for index,window in enumerate(windows[:max(0,round_limit)]):
            start,end=window_for(day,window,self.timezone)
            if end<=now:continue
            seed=f'{day}|{index}|{window}'
            hour=datetime.fromtimestamp(start,ZoneInfo(self.timezone)).hour
            provider,account=choose_provider(candidates,prefs,hour,seed,exploration)
            key=hashlib.sha256(f'daily|{seed}'.encode()).hexdigest()
            try:self.store.create_task(provider,account,'browse',start,end,origin='automatic',pinned=False,task_id=key)
            except sqlite3.IntegrityError:pass
            result.append(key)
        return result

def allowed_intervals(day,windows,rest_windows,timezone='Asia/Shanghai'):
    """Subtract rest periods, including rest that started on the previous calendar day."""
    rests=[]
    for delta in (-1,0,1):
        for window in rest_windows:rests.append(window_for(day+timedelta(days=delta),window,timezone))
    result=[]
    for source_index,window in enumerate(windows):
        pieces=[window_for(day,window,timezone)]
        for low,high in rests:
            next_pieces=[]
            for start,end in pieces:
                if high<=start or low>=end:next_pieces.append((start,end));continue
                if start<low:next_pieces.append((start,low))
                if high<end:next_pieces.append((high,end))
            pieces=next_pieces
        result.extend({'start':a,'end':b,'source_window':source_index} for a,b in pieces if b>a)
    return result

def round_intervals(intervals,now,minutes=30,*,until=None,maximum_candidates=192):
    """A permission window may contain many independently selected rounds."""
    if type(minutes)is not int or not 1<=minutes<=180:raise ValueError('invalid_session_minutes')
    slots=[];length=minutes*60
    for window in intervals:
        cursor=window['start']
        while cursor<window['end']:
            finish=min(cursor+length,window['end'])
            start=max(now,cursor);end=min(finish,until) if until is not None else finish
            if end>start:slots.append({**window,'start':start,'end':end,'source_slot':cursor})
            cursor=finish
    slots.sort(key=lambda w:(w['start'],w['end'],w['source_window']))
    # Keep the full day represented even with many long, overlapping input windows.
    if len(slots)>maximum_candidates:
        slots=[slots[i*(len(slots)-1)//(maximum_candidates-1)] for i in range(maximum_candidates)]
    return slots
