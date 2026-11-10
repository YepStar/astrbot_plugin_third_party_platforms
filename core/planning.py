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


def choose_provider(candidates,preferences,hour,seed,exploration=0.15):
    if not candidates:raise ValueError('no_eligible_provider')
    if not 0<=exploration<=1:raise ValueError('invalid_exploration')
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
