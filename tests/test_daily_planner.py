import importlib,sys,asyncio
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from unittest.mock import AsyncMock
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]));base=Path(__file__).resolve().parents[1].name
Store=importlib.import_module(base+'.core.store').Store
DailyPlanner=importlib.import_module(base+'.core.daily_planner').DailyPlanner

def setup(tmp_path):
 store=Store(tmp_path/'db');now=[datetime(2026,11,10,9,tzinfo=ZoneInfo('Asia/Shanghai')).timestamp()]
 config={'timezone':'Asia/Shanghai','daily_rounds':2,'windows':['10:00-11:00','20:00-21:00'],'platforms':{'p':{'accounts':{'a':{}}}}}
 generate=AsyncMock(return_value='{"sessions":[{"provider":"p","account":"a","window_index":0}]}')
 return store,now,config,generate,DailyPlanner(store,generate,config,lambda:now[0])

def test_daily_cache_and_fingerprint(tmp_path):
 async def run():
  store,now,cfg,generate,planner=setup(tmp_path)
  await planner.ensure([('p','a')]);await planner.ensure([('p','a')]);assert generate.await_count==1
  cfg['windows'][0]='10:30-11:30';await planner.ensure([('p','a')]);assert generate.await_count==2
  assert sum(t['state']=='planned' for t in store.tasks())==1
 asyncio.run(run())

def test_manual_cancellation_survives_config_replan(tmp_path):
 async def run():
  store,now,cfg,generate,planner=setup(tmp_path);await planner.ensure([('p','a')])
  task=store.tasks()[0];store.change_task(task['id'],1,cancel=True)
  cfg['daily_rounds']=3;await planner.ensure([('p','a')])
  assert not any(t['state']=='planned' for t in store.tasks())
 asyncio.run(run())

def test_invalid_plan_has_no_partial_task_inserts(tmp_path):
 async def run():
  store,now,cfg,generate,planner=setup(tmp_path)
  generate.return_value='{"sessions":[{"provider":"p","account":"a","window_index":0},{"provider":"evil","account":"a","window_index":1}]}'
  with pytest.raises(ValueError):await planner.ensure([('p','a')])
  assert store.tasks()==[]
 asyncio.run(run())

def test_zero_activity_and_bounded_failed_retries(tmp_path):
 async def run():
  store,now,cfg,generate,planner=setup(tmp_path);cfg['daily_rounds']=0
  await planner.ensure([('p','a')]);generate.assert_not_awaited()
  cfg['daily_rounds']=1;generate.side_effect=ValueError
  for _ in range(5):
   try:await planner.ensure([('p','a')])
   except ValueError:pass
   now[0]+=901
  assert generate.await_count==3
 asyncio.run(run())

def test_rest_window_clips_cross_midnight_activity(tmp_path):
 planning=importlib.import_module(base+'.core.planning')
 from datetime import date
 intervals=planning.allowed_intervals(date(2026,11,10),['22:00-03:00'],['23:00-01:00'])
 local=lambda t:datetime.fromtimestamp(t,ZoneInfo('Asia/Shanghai')).strftime('%H:%M')
 assert [(local(w['start']),local(w['end'])) for w in intervals]==[('22:00','23:00'),('01:00','03:00')]

def test_learning_affects_actual_platform_assignment(tmp_path):
 async def run():
  store,now,cfg,generate,planner=setup(tmp_path)
  cfg['platforms']['q']={'accounts':{'a':{}}};cfg['exploration_ratio']=0
  models=importlib.import_module(base+'.core.models')
  for i in range(6):store.observe(models.Content('q','a',str(i),'url','title','evidence'),models.Evaluation(9,'reason','evidence'),10,now[0])
  # Model still proposes p; host applies the learned eligible assignment instead of ignoring learning.
  await planner.ensure([('p','a'),('q','a')]);assert store.tasks()[0]['provider']=='q'
 asyncio.run(run())


def test_strategy_and_learning_changes_invalidate_plan(tmp_path):
 async def run():
  store,now,cfg,generate,planner=setup(tmp_path)
  await planner.ensure([('p','a')])
  cfg['exploration_ratio']=.3
  await planner.ensure([('p','a')])
  cfg['preference_half_life_days']=7
  await planner.ensure([('p','a')])
  cfg['platforms']['p']['accounts']['a']['browse']={'query':'new interest'}
  await planner.ensure([('p','a')])
  assert generate.await_count==4
  planned=[t for t in store.tasks() if t['state']=='planned']
  assert len(planned)==1 and planned[0]['params']['query']=='new interest'
 asyncio.run(run())


def test_planning_model_override_invalidates_cached_daily_plan(tmp_path):
 async def run():
  store,now,cfg,generate,planner=setup(tmp_path)
  await planner.ensure([('p','a')])
  cfg['model_ids']={'daily_plan':'new-model'}
  await planner.ensure([('p','a')])
  assert generate.await_count==2
 asyncio.run(run())

def test_unchanged_slots_are_reused_on_replan(tmp_path):
 async def run():
  store,now,cfg,generate,planner=setup(tmp_path)
  await planner.ensure([('p','a')]);original=store.tasks()[0]
  cfg['exploration_ratio']=.35
  await planner.ensure([('p','a')])
  assert len(store.tasks())==1 and store.tasks()[0]['id']==original['id']
  cfg['platforms']['p']['accounts']['a']['browse']={'query':'new'}
  await planner.ensure([('p','a')])
  assert len(store.tasks())==1 and store.tasks()[0]['params']['query']=='new'
 asyncio.run(run())

def test_restoring_previous_window_does_not_collide_with_cancelled_event_id(tmp_path):
 async def run():
  store,now,cfg,generate,planner=setup(tmp_path)
  await planner.ensure([('p','a')])
  cfg['windows'][0]='10:30-11:30';await planner.ensure([('p','a')])
  cfg['windows'][0]='10:00-11:00';await planner.ensure([('p','a')])
  planned=[t for t in store.tasks() if t['state']=='planned']
  assert len(planned)==1
  assert datetime.fromtimestamp(planned[0]['start'],ZoneInfo('Asia/Shanghai')).strftime('%H:%M')=='10:00'
 asyncio.run(run())

def test_force_regenerates_remaining_time_and_preserves_completed_and_manual(tmp_path):
 async def run():
  store,now,cfg,generate,planner=setup(tmp_path)
  await planner.ensure([('p','a')]);completed=store.tasks()[0];assert store.claim_task(completed['id'],completed['start']);store.finish_task(completed['id'],'succeeded')
  now[0]+=5*3600 # 14:00: morning is over; model index zero now refers to evening.
  result=await planner.regenerate([('p','a')])
  assert generate.await_count==2 and result['planned']==1
  planned=[t for t in store.tasks() if t['state']=='planned']
  assert len(planned)==1 and planned[0]['start']>now[0]
  manual=store.create_task('p','a','browse',now[0]+3600,now[0]+4000)
  result=await planner.regenerate([('p','a')]);assert result['planned']==0
  assert next(t for t in store.tasks() if t['id']==completed['id'])['state']=='succeeded'
  assert next(t for t in store.tasks() if t['id']==manual)['state']=='planned'
 asyncio.run(run())

def test_force_failure_preserves_existing_plan_and_zero_weights_clear_only_automatic(tmp_path):
 async def run():
  store,now,cfg,generate,planner=setup(tmp_path);await planner.ensure([('p','a')]);before=store.tasks()
  generate.side_effect=ValueError('fixture failure')
  with pytest.raises(ValueError):await planner.regenerate([('p','a')])
  assert store.tasks()==before
  cfg['platform_weights']={'p':0}
  result=await planner.regenerate([('p','a')]);assert result['planned']==0
  assert not any(t['state']=='planned' for t in store.tasks())
 asyncio.run(run())

def test_force_protects_tasks_started_while_model_is_generating(tmp_path):
 async def run():
  store,now,cfg,generate,planner=setup(tmp_path);cfg['daily_rounds']=1
  await planner.ensure([('p','a')]);original=store.tasks()[0];now[0]+=3600
  async def started(*args):
   assert store.claim_task(original['id'],now[0])
   return '{"sessions":[{"provider":"p","account":"a","window_index":0}]}'
  generate.side_effect=started
  result=await planner.regenerate([('p','a')]);assert result['planned']==0
  assert len(store.tasks())==1 and store.tasks()[0]['state']=='executing'
 asyncio.run(run())

def test_force_clips_today_and_preserves_tomorrow_overnight_tail(tmp_path):
 async def run():
  store,now,cfg,generate,planner=setup(tmp_path);cfg['windows']=['22:00-02:00'];now[0]+=14*3600 # 23:00
  end=datetime(2026,11,11,2,tzinfo=ZoneInfo('Asia/Shanghai')).timestamp()
  key=store.create_task('p','a','browse',now[0],end,params={'_planner_slot':'2026-11-10:0:p:a'},origin='automatic',pinned=False,task_id='plan:2026-11-10:legacy:0');old=store.tasks()[0];now[0]+=60
  result=await planner.regenerate([('p','a')]);assert result['planned']==1
  day_end=datetime(2026,11,11,tzinfo=ZoneInfo('Asia/Shanghai')).timestamp()
  planned=[t for t in store.tasks() if t['state']=='planned']
  assert any(t['start']>=now[0] and t['end']<=day_end for t in planned)
  assert any(t['start']==day_end and t['end']==old['end'] for t in planned)
 asyncio.run(run())

def test_force_does_not_resurrect_manual_cancellation(tmp_path):
 async def run():
  store,now,cfg,generate,planner=setup(tmp_path);await planner.ensure([('p','a')]);task=store.tasks()[0]
  store.change_task(task['id'],task['revision'],cancel=True)
  await planner.regenerate([('p','a')])
  assert not any(t['state']=='planned' for t in store.tasks())
 asyncio.run(run())

def test_one_permission_window_can_schedule_multiple_independent_rounds(tmp_path):
 async def run():
  store,now,cfg,generate,planner=setup(tmp_path)
  cfg.update(windows=['10:00-12:00'],daily_rounds=3,session_minutes=30)
  generate.return_value='{"sessions":[{"provider":"p","account":"a","window_index":0},{"provider":"p","account":"a","window_index":1},{"provider":"p","account":"a","window_index":2}]}'
  result=await planner.regenerate([('p','a')]);assert result['planned']==3
  planned=[t for t in store.tasks() if t['state']=='planned']
  assert len(planned)==3 and all(t['end']-t['start']==1800 for t in planned)
  assert all(a['end']<=b['start'] for a,b in zip(planned,planned[1:]))
  store.change_task(planned[0]['id'],planned[0]['revision'],cancel=True)
  await planner.regenerate([('p','a')])
  assert len([t for t in store.tasks() if t['state']=='planned'])==2
 asyncio.run(run())

def test_overlapping_windows_do_not_create_simultaneous_rounds_for_one_account(tmp_path):
 async def run():
  store,now,cfg,generate,planner=setup(tmp_path);cfg.update(windows=['10:00-11:00','10:00-11:00'],daily_rounds=2)
  generate.return_value='{"sessions":[{"provider":"p","account":"a","window_index":0},{"provider":"p","account":"a","window_index":1}]}'
  result=await planner.regenerate([('p','a')]);assert result['planned']==1
 asyncio.run(run())
