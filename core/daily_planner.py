import asyncio
import hashlib
import json
from datetime import datetime
from zoneinfo import ZoneInfo
from .planning import window_for,allowed_intervals,choose_provider
from .reading import parse_object

class DailyPlanner:
    def __init__(self,store,generate,config,clock):
        self.store,self.generate,self.config,self.clock=store,generate,config,clock
        self.lock=asyncio.Lock()
    async def ensure(self,candidates):
        async with self.lock:
            return await self._ensure(sorted(candidates))
    async def _ensure(self,candidates):
        cfg=self.config;now=self.clock();timezone=cfg.get('timezone','Asia/Shanghai')
        day=datetime.fromtimestamp(now,ZoneInfo(timezone)).date();windows=cfg.get('windows',[])
        if not candidates:return
        if not isinstance(windows,list) or len(windows)>32:raise ValueError('invalid_windows')
        rest_windows=cfg.get('rest_windows',[])
        if not isinstance(rest_windows,list) or len(rest_windows)>16:raise ValueError('invalid_rest_windows')
        intervals=allowed_intervals(day,windows,rest_windows,timezone)
        maximum=cfg.get('daily_rounds',2)
        if type(maximum)is not int or not 0<=maximum<=12:raise ValueError('invalid_round_limit')
        activity=cfg.get('activity_level',55)
        if type(activity)is not int or not 0<=activity<=100:raise ValueError('invalid_activity_level')
        if activity==0:maximum=0
        constraints={'rest':rest_windows,'activity':activity,'candidates':candidates,'windows':windows,'maximum':maximum,'timezone':timezone,
                     'public_persona':cfg.get('public_persona',''),'provider_id':cfg.get('provider_id',''),
                     'exploration_ratio':cfg.get('exploration_ratio',.15),'preference_half_life_days':cfg.get('preference_half_life_days',14),
                     'account_options':{f'{p}:{a}':cfg['platforms'][p]['accounts'][a].get('browse',{}) for p,a in candidates}}
        fingerprint=hashlib.sha256(json.dumps(constraints,sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:20]
        state=self.store.setting('plan:'+str(day),{})
        if state.get('fingerprint')!=fingerprint:state={}
        if state.get('complete') or state.get('attempts',0)>=3:return
        if now-state.get('at',0)<900:return
        attempt=state.get('attempts',0)+1
        self.store.set_setting('plan:'+str(day),{'fingerprint':fingerprint,'complete':False,'attempts':attempt,'at':now})
        if maximum==0 or not intervals:
            self.store.apply_daily_plan(str(day),fingerprint,[],now);return
        try:
            prefs=self.store.preferences(now,half_life_days=cfg.get('preference_half_life_days',14))
            pinned=[t for t in self.store.tasks(min(w['start'] for w in intervals),now+172800) if t['pinned']]
            exploration=cfg.get('exploration_ratio',.15)
            if type(exploration)not in (int,float) or not 0<=exploration<=1:raise ValueError('invalid_exploration')
            allocations=[choose_provider(candidates,prefs,datetime.fromtimestamp(w['start'],ZoneInfo(timezone)).hour,
                f'{day}:{w["source_window"]}',exploration) for w in intervals]
            raw=await self.generate('daily_plan',{
                'instruction':'Choose zero or more sessions within supplied allowed windows, at most max_sessions, and at most ONE session for each unique window_index. Return JSON only {"sessions":[{"provider":str,"account":str,"window_index":int}]}. No minimum quota. Respect explicit pinned/manual overrides, their cancellations and account permissions. Overlapping windows are allowed. Use real learned time-of-day preferences with their evidence counts, avoid treating limited samples as certainties. May explore other eligible platforms; never invent completed activity.',
                'candidates':candidates,'windows':[{'start':w['start'],'end':w['end'],'source_window':w['source_window'],'preferred_provider':allocations[i][0],'preferred_account':allocations[i][1]} for i,w in enumerate(intervals)],'max_sessions':min(maximum,len(intervals)),'activity_level':activity,'learned':prefs,
                'manual_overrides':pinned,'exploration_ratio':cfg.get('exploration_ratio',.15)})
            sessions=parse_object(raw).get('sessions')
            if not isinstance(sessions,list) or len(sessions)>maximum:raise ValueError('invalid_model_plan')
            tasks=[];seen=set()
            for row in sessions:
                if not isinstance(row,dict) or set(row)!={'provider','account','window_index'}:raise ValueError('invalid_plan_item')
                if (row['provider'],row['account']) not in candidates:raise ValueError('unknown_plan_account')
                index=row['window_index']
                if type(index)is not int or not 0<=index<len(intervals):raise ValueError('unknown_plan_window')
                provider,account=allocations[index]
                unique=(provider,account,index)
                if unique in seen:raise ValueError('duplicate_plan_slot')
                seen.add(unique);start,end=intervals[index]['start'],intervals[index]['end']
                options=cfg['platforms'][provider]['accounts'][account].get('browse',{})
                tasks.append({**row,'provider':provider,'account':account,'source_window':intervals[index]['source_window'],'start':start,'end':end,'action':'listen' if provider=='netease' else 'browse','params':options})
            self.store.apply_daily_plan(str(day),fingerprint,tasks,now)
        except Exception as exc:
            self.store.set_setting('plan:'+str(day),{'fingerprint':fingerprint,'complete':False,'attempts':attempt,'at':now,'error':type(exc).__name__})
            raise
