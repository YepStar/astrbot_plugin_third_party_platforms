import asyncio
import importlib
from pathlib import Path
import sys
from types import SimpleNamespace as NS
from unittest.mock import AsyncMock
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
base=Path(__file__).resolve().parents[1].name
sharing=importlib.import_module(base+'.core.sharing')
models=importlib.import_module(base+'.core.models')
Store=importlib.import_module(base+'.core.store').Store
Executor=importlib.import_module(base+'.core.execution').Executor
Policy=importlib.import_module(base+'.core.policy').Policy


def setup(tmp_path,mode='all'):
    item={'enabled':True,'owner_umo':'qq:FriendMessage:1','owner_uid':'42','self_uid':'99','owner_bili_name':'owner',
          'share_delivery':mode,'actions':{'owner_share':True},'daily_limits':{'owner_share':1}}
    cfg={'enabled':True,'daily_limit':10,'minute_limit':10,'platforms':{'bilibili':{'enabled':True,'accounts':{'a':item}}}}
    provider=NS(id='bilibili',capabilities={'owner_share'},execute=AsyncMock(return_value=models.Receipt('succeeded','remote-id')))
    registry=models.Registry();registry.register(provider)
    store=Store(tmp_path/'db');executor=Executor(store,registry,Policy(cfg))
    service=NS(store=store,registry=registry,executor=executor,deliver=AsyncMock(),clock=lambda:2000000000)
    content=models.Content('bilibili','a','BV123','url','title','source',metadata={'aid':123})
    evaluation=models.Evaluation(9,'reason','source',True)
    return service,provider,item,content,evaluation


async def test_all_channels_use_one_quota_and_each_delivery_once(tmp_path):
    service,provider,item,content,evaluation=setup(tmp_path)
    result=await sharing.share(service,content,evaluation,'message',item)
    assert result.state=='succeeded'
    assert provider.execute.await_count==2 and service.deliver.await_count==1
    assert provider.execute.await_args_list[1].args[2]['at_name_to_mid']=={'owner':42}
    await sharing.share(service,content,evaluation,'message',item)
    assert provider.execute.await_count==2 and service.deliver.await_count==1
    with service.store.connect() as db:
        assert db.execute("SELECT COUNT(*) FROM reservations WHERE bucket='bilibili:a:owner_share'").fetchone()[0]==1


async def test_ambiguous_delivery_never_falls_back_or_retries_after_restart(tmp_path):
    service,provider,item,content,evaluation=setup(tmp_path)
    provider.execute.side_effect=TimeoutError
    result=await sharing.share(service,content,evaluation,'message',item)
    assert result.state=='unknown'
    assert provider.execute.await_count==1 and service.deliver.await_count==0
    service.store=Store(tmp_path/'db');service.store.recover()
    await sharing.share(service,content,evaluation,'message',item)
    assert provider.execute.await_count==1


async def test_old_uncertain_share_blocks_new_channels(tmp_path):
    service,provider,item,content,evaluation=setup(tmp_path)
    key='legacy_owner_share:bilibili:a:BV123'
    service.store.claim_action(key,'bilibili','a','owner_share',[])
    service.store.finish_action(key,models.Receipt('unknown'))
    assert await sharing.share(service,content,evaluation,'message',item) is None
    provider.execute.assert_not_awaited();service.deliver.assert_not_awaited()


def test_routes_require_explicit_known_owner_and_preserve_selected_mode(tmp_path):
    service,provider,item,content,evaluation=setup(tmp_path,'comment')
    assert sharing.routes('bilibili',item)==[('comment','42')]
    item['owner_bili_name']=''
    assert sharing.routes('bilibili',item)==[]
    item['share_delivery']='auto'
    assert sharing.routes('bilibili',item)==[('qq_private','qq:FriendMessage:1')]
    item['owner_umo']=''
    assert sharing.routes('bilibili',item)==[('private_message','42')]
    item['owner_uid']='99'
    assert sharing.routes('bilibili',item)==[]
