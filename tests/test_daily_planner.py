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
