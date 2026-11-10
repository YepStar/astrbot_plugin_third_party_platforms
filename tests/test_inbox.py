import asyncio
import importlib
from dataclasses import replace
from pathlib import Path
import sys
from types import SimpleNamespace as NS
from unittest.mock import AsyncMock
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
base=Path(__file__).resolve().parents[1].name
models=importlib.import_module(base+'.core.models')
Store=importlib.import_module(base+'.core.store').Store
Inbox=importlib.import_module(base+'.core.inbox').Inbox
Executor=importlib.import_module(base+'.core.execution').Executor
Policy=importlib.import_module(base+'.core.policy').Policy

def setup(tmp_path,generate=None):
 store=Store(tmp_path/'db');reg=models.Registry()
 provider=NS(id='p',capabilities={'reply','private_reply'},execute=AsyncMock(return_value=models.Receipt('succeeded','42')))
 reg.register(provider)
 account={'enabled':True,'actions':{'reply':True,'private_reply':True},'daily_limits':{'reply':10,'private_reply':10},'reply':{},'self_uid':'self'}
 cfg={'enabled':True,'daily_limit':20,'minute_limit':20,'platforms':{'p':{'enabled':True,'accounts':{'a':account}}}}
 executor=Executor(store,reg,Policy(cfg),clock=lambda:1000)
 generate=generate or AsyncMock(return_value='{"reply":"你好","respond":true}')
 return store,provider,account,Inbox(store,reg,executor,generate,clock=lambda:1000)

def event(id='one',stream='reply',**kw):
 return models.Incoming('p','a',stream,id,'user','hello',990,{'post_id':'1','reply_anchor':id},True,**kw)

def test_baseline_and_cursor_are_durable(tmp_path):
 store,provider,account,engine=setup(tmp_path)
 store.ingest('p','a','reply',[event()],{'latest':'one'})
 assert not store.pending_events(1000)
 store.ingest('p','a','reply',[event('two')],{'latest':'two'})
 assert len(Store(tmp_path/'db').pending_events(1000))==1
 assert Store(tmp_path/'db').cursor('p','a','reply')['latest']=='two'

def test_scoped_ingest_is_atomic(tmp_path):
 store,*_=setup(tmp_path)
 with pytest.raises(ValueError):store.ingest('p','a','reply',[replace(event(),account='other')],{'latest':'one'})
 assert store.cursor('p','a','reply') is None

def test_same_comment_in_two_streams_sends_once(tmp_path):
 async def run():
  store,provider,account,engine=setup(tmp_path)
  for stream in ['reply','mention']:store.ingest('p','a',stream,[event(stream=stream)],{},initial_ignore=False)
  await engine.process();assert provider.execute.await_count==1
 asyncio.run(run())

def test_external_command_unverified_and_self_are_blocked(tmp_path):
 async def run():
  store,provider,account,engine=setup(tmp_path)
  events=[replace(event('cmd'),text='/third_party_schedule_change cancel'),replace(event('unknown'),actor_verified=False),replace(event('self'),actor_id='self')]
  store.ingest('p','a','reply',events,{},initial_ignore=False)
  await engine.process();provider.execute.assert_not_awaited();engine.generate.assert_not_awaited()
 asyncio.run(run())

def test_permission_revoked_during_generation(tmp_path):
 async def run():
  store,provider,account,engine=setup(tmp_path)
  async def generate(*args):account['actions']['reply']=False;return '{"reply":"你好","respond":true}'
  engine.generate=generate;store.ingest('p','a','reply',[event()],{},initial_ignore=False)
  await engine.process();provider.execute.assert_not_awaited()
 asyncio.run(run())

def test_unknown_send_is_never_replayed(tmp_path):
 async def run():
  store,provider,account,engine=setup(tmp_path)
  provider.execute.side_effect=TimeoutError
  store.ingest('p','a','reply',[event()],{},initial_ignore=False)
  await engine.process();store.recover();await engine.process()
  provider.execute.assert_awaited_once();assert store.actions()[0]['state']=='unknown'
 asyncio.run(run())

def test_generation_attempts_are_bounded(tmp_path):
 async def run():
  store,provider,account,engine=setup(tmp_path);engine.generate.side_effect=ValueError
  store.ingest('p','a','reply',[event()],{},initial_ignore=False)
  for _ in range(6):
   await engine.process()
   with store.connect() as db:db.execute('UPDATE inbox SET next_attempt=0')
  assert engine.generate.await_count==3;provider.execute.assert_not_awaited()
  with store.connect() as db:assert db.execute('SELECT state FROM inbox').fetchone()[0]=='failed'
 asyncio.run(run())


def test_reply_loads_attributed_context_after_permissions_and_honors_platform_limit(tmp_path):
 async def run():
  store,provider,account,engine=setup(tmp_path)
  provider.reply_context=AsyncMock(return_value={'text':'A third-party author wrote this post.','images':[],
    'image_attributions':[{'owner_uid':'author','source':'post'}]})
  memory=NS(recall=lambda *_:[{'scope':'bilibili:public','content':'public memory'}],remember_reply=AsyncMock())
  engine.memory=memory
  account['reply']['max_reply_chars']=1
  store.ingest('p','a','reply',[event()],{},initial_ignore=False)
  await engine.process()
  payload=engine.generate.await_args.args[1]
  assert payload['source'].startswith('A third-party author') and payload['modality']=='text_only'
  assert payload['image_attributions'][0]['owner_uid']=='author'
  provider.execute.assert_not_awaited();memory.remember_reply.assert_not_awaited()
 asyncio.run(run())
