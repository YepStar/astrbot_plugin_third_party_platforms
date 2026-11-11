import asyncio
import hashlib
import json
import uuid
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
from .planning import allowed_intervals,choose_provider,round_intervals
from .reading import parse_object

class DailyPlanner:
    def __init__(self,store,generate,config,clock):
        self.store,self.generate,self.config,self.clock=store,generate,config,clock
        self.lock=asyncio.Lock()
    async def ensure(self,candidates):
        async with self.lock:return await self._ensure(sorted(candidates))
    async def regenerate(self,candidates):
        async with self.lock:return await self._ensure(sorted(candidates),force=True)
    async def _ensure(self,candidates,force=False):
        cfg=self.config;now=self.clock();timezone=cfg.get('timezone','Asia/Shanghai');zone=ZoneInfo(timezone)
        midnight=datetime.fromtimestamp(now,zone).replace(hour=0,minute=0,second=0,microsecond=0)
        day=midnight.date();day_start=midnight.timestamp();day_end=(midnight+timedelta(days=1)).timestamp()
        windows=cfg.get('windows',[]);rest_windows=cfg.get('rest_windows',[])
        if not isinstance(windows,list) or len(windows)>32:raise ValueError('invalid_windows')
        if not isinstance(rest_windows,list) or len(rest_windows)>16:raise ValueError('invalid_rest_windows')
        weights=cfg.get('platform_weights',{})
        if not isinstance(weights,dict):raise ValueError('invalid_platform_weights')
        from .configuration import number
        for value in weights.values():number(value,0,100)
        candidates=[c for c in candidates if weights.get(c[0],1)>0]
        maximum=cfg.get('daily_rounds',2)
        if type(maximum)is not int or not 0<=maximum<=12:raise ValueError('invalid_round_limit')
        activity=cfg.get('activity_level',55)
        if type(activity)is not int or not 0<=activity<=100:raise ValueError('invalid_activity_level')
        if activity==0:maximum=0
        constraints={'rest':rest_windows,'activity':activity,'candidates':candidates,'windows':windows,'maximum':maximum,'timezone':timezone,
                     'public_persona':cfg.get('public_persona',''),'provider_id':cfg.get('model_ids',{}).get('daily_plan') or cfg.get('provider_id',''),
                     'exploration_ratio':cfg.get('exploration_ratio',.15),'preference_half_life_days':cfg.get('preference_half_life_days',14),
                     'session_minutes':cfg.get('session_minutes',30),'account_options':{f'{p}:{a}':cfg['platforms'][p]['accounts'][a].get('browse',{}) for p,a in candidates}}
        if weights:constraints['platform_weights']=weights
        fingerprint=hashlib.sha256(json.dumps(constraints,sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:20]
        state=self.store.setting('plan:'+str(day),{})
        if state.get('fingerprint')!=fingerprint:state={}
        if not force and (state.get('complete') or state.get('attempts',0)>=3 or now-state.get('at',0)<900):return
        intervals=allowed_intervals(day,windows,rest_windows,timezone)
        intervals=round_intervals(intervals,now,cfg.get('session_minutes',30),until=day_end if force else None)
        existing=self.store.tasks(day_start,day_end)
        protected=[t for t in existing if t['state'] in {'executing','succeeded','failed','unknown'} or (t['state']=='planned' and (t['pinned'] or (t['origin']=='automatic' and not t['id'].startswith(f'plan:{day}:'))))]
        remaining=max(0,maximum-len(protected))
        attempt=1 if force else state.get('attempts',0)+1
        self.store.set_setting('plan:'+str(day),{'fingerprint':fingerprint,'complete':False,'attempts':attempt,'at':now})
        def apply(tasks):
            return self.store.apply_daily_plan(str(day),fingerprint,tasks,self.clock(),round_limit=maximum,day_start=day_start,day_end=day_end,remaining_only=force)
        if not candidates or remaining==0 or not intervals:
            return apply([])
        try:
            prefs=self.store.preferences(now,half_life_days=cfg.get('preference_half_life_days',14))
            exploration=cfg.get('exploration_ratio',.15)
            if type(exploration)not in (int,float) or not 0<=exploration<=1:raise ValueError('invalid_exploration')
            nonce=uuid.uuid4().hex if force else ''
            allocations=[choose_provider(candidates,prefs,datetime.fromtimestamp(w['start'],zone).hour,
                f'{day}:{w["source_window"]}:{w["source_slot"]}'+(':'+nonce if nonce else ''),exploration,weights=weights) for w in intervals]
            raw=await self.generate('daily_plan',{
                'instruction':'Choose zero or more sessions within supplied remaining allowed windows, at most max_sessions, and at most ONE session for each candidate round window_index. A user permission window may contain MULTIPLE rounds: candidates with the same source_window but different round indices are independent choices; do not restrict to one round per source_window. Return JSON only {"sessions":[{"provider":str,"account":str,"window_index":int}]}. No minimum quota. Existing executed/ongoing/manual events are protected and count against the daily round limit. Completed events consume budget but do not occupy future free time. Respect manual cancellations and account permissions. Overlapping platforms are allowed. The host allocates platforms using optional user relative weights (0 excludes automatic planning); unspecified weights use learned time-of-day preferences. Never invent completed activity.',
                'candidates':candidates,'windows':[{'start':w['start'],'end':w['end'],'source_window':w['source_window'],'start_time':datetime.fromtimestamp(w['start'],zone).isoformat(),'end_time':datetime.fromtimestamp(w['end'],zone).isoformat(),'preferred_provider':allocations[i][0],'preferred_account':allocations[i][1]} for i,w in enumerate(intervals)],
                'max_sessions':min(remaining,len(intervals)),'activity_level':activity,'learned':prefs,'platform_weights':weights,
                'manual_overrides':[t for t in existing if t['pinned']],'protected_events':protected,'exploration_ratio':exploration})
            sessions=parse_object(raw).get('sessions')
            if not isinstance(sessions,list) or len(sessions)>remaining:raise ValueError('invalid_model_plan')
            tasks=[];seen=set()
            for row in sessions:
                if not isinstance(row,dict) or set(row)!={'provider','account','window_index'}:raise ValueError('invalid_plan_item')
                if (row['provider'],row['account']) not in candidates:raise ValueError('unknown_plan_account')
                index=row['window_index']
                if type(index)is not int or not 0<=index<len(intervals):raise ValueError('unknown_plan_window')
                if index in seen:raise ValueError('duplicate_plan_slot')
                seen.add(index);provider,account=allocations[index]
                start,end=intervals[index]['start'],intervals[index]['end']
                options=cfg['platforms'][provider]['accounts'][account].get('browse',{})
                tasks.append({**row,'provider':provider,'account':account,'source_window':intervals[index]['source_window'],'source_slot':intervals[index]['source_slot'],'start':start,'end':end,'action':'listen' if provider=='netease' else 'browse','params':options})
            return apply(tasks)
        except Exception as exc:
            self.store.set_setting('plan:'+str(day),{'fingerprint':fingerprint,'complete':False,'attempts':attempt,'at':now,'error':type(exc).__name__})
            raise
