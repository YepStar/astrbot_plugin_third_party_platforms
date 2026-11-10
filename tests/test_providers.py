import asyncio
import importlib
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
package=Path(__file__).resolve().parents[1].name
SecretStore=importlib.import_module(package+'.core.secrets').SecretStore


def test_bili_write_receipt_requires_external_id(tmp_path):
    module=importlib.import_module(package+'.providers.bilibili')
    async def run():
        provider=module.Bilibili(SecretStore(tmp_path/'secrets'),{})
        client=provider.client('test')
        client._http_post=AsyncMock(return_value=({'code':0,'data':{}},None))
        receipt=await provider.execute('test','comment',{'oid':'1','text':'test'},'key')
        assert receipt.state=='unknown'
        client._http_post=AsyncMock(return_value=({'code':0,'data':{'rpid':'42'}},None))
        receipt=await provider.execute('test','comment',{'oid':'1','text':'test'},'key2')
        assert receipt.state=='succeeded' and receipt.external_id=='42'
        assert client._http_post.await_count==1
    asyncio.run(run())

def test_bili_credentials_rejected_before_network(tmp_path):
    module=importlib.import_module(package+'.providers.bilibili')
    store=SecretStore(tmp_path/'secrets');store.write('bilibili','test',{'SESSDATA':'a; injected=x'})
    provider=module.Bilibili(store,{})
    with pytest.raises(ValueError):provider.client('test')._headers()
    with pytest.raises(ValueError):asyncio.run(provider.client('test')._http_get('https://evil.example/credential'))

def test_xhh_uncertain_send_not_success(tmp_path):
    module=importlib.import_module(package+'.providers.xiaoheihe')
    async def run():
        provider=module.Xiaoheihe(SecretStore(tmp_path/'secrets'),{})
        provider.clients['test']=SimpleNamespace(send_comment=AsyncMock(return_value=SimpleNamespace(confirmed=False,external_comment_id='')))
        result=await provider.execute('test','comment',{'post_id':'1','text':'test'},'key')
        assert result.state=='unknown'
    asyncio.run(run())

def test_memory_gateway_never_opens_private_database():
    module=importlib.import_module(package+'.integrations.memory')
    class Context:
        def get_registered_star(self,name):return None
    result=module.PublicMemoryGateway(Context(),True).put(SimpleNamespace(provider='bilibili'),None)
    assert result=='unavailable'

def test_music_facade_delegation_and_release():
    module=importlib.import_module(package+'.integrations.music')
    async def run():
        facade=SimpleNamespace(third_party_scheduler_api=1,
            third_party_scheduler_acquire=AsyncMock(return_value=True),
            third_party_scheduler_run=AsyncMock(return_value={'state':'succeeded','code':'decision_processed'}),
            third_party_scheduler_release=AsyncMock())
        context=SimpleNamespace(get_registered_star=lambda _:SimpleNamespace(activated=True,star_cls=facade))
        adapter=module.Music(context)
        result=await adapter.execute('default','listen',{},'key')
        assert result.code=='decision_processed'
        facade.third_party_scheduler_run.assert_awaited_once_with(adapter.owner,'key')
        await adapter.close();facade.third_party_scheduler_release.assert_awaited_once_with(adapter.owner)
    asyncio.run(run())


@pytest.mark.asyncio
async def test_bili_http_reads_complete_chunked_utf8_and_enforces_limit(tmp_path,monkeypatch):
 from contextlib import asynccontextmanager
 module=importlib.import_module(package+'.providers.bilibili')
 import json
 raw=json.dumps({'text':'汉字'*40000},ensure_ascii=False).encode()
 chunks=[raw[:65537],raw[65537:]]
 class Body:
  async def iter_chunked(self,_):
   for chunk in chunks:yield chunk
 @asynccontextmanager
 async def response(*args,**kwargs):yield SimpleNamespace(status=200,content=Body())
 @asynccontextmanager
 async def session(*args,**kwargs):yield SimpleNamespace(get=response)
 monkeypatch.setattr(module,'plugin_http_session',session)
 client=module.Client({});result,_=await client._http_get('https://api.bilibili.com/test')
 assert result['text']=='汉字'*40000
 chunks[:]=[b'x'*1_000_000,b'x'*1_000_001]
 with pytest.raises(ValueError,match='response_limit'):await client._http_get('https://api.bilibili.com/test')


@pytest.mark.asyncio
async def test_bili_network_restriction_is_not_reported_as_expired_login(tmp_path):
 module=importlib.import_module(package+'.providers.bilibili')
 store=SecretStore(tmp_path/'secret');store.write('bilibili','one',{'SESSDATA':'fixture'})
 provider=module.Bilibili(store,{})
 provider.client('one')._http_get=AsyncMock(return_value=({'code':-412},None))
 result=await provider.status('one');assert result['ready'] is None and result['state']=='unreachable'
 provider.client('one')._http_get=AsyncMock(return_value=({'code':-101},None))
 assert (await provider.status('one'))['state']=='invalid'

@pytest.mark.asyncio
async def test_bili_status_returns_authenticated_identity(tmp_path):
 module=importlib.import_module(package+'.providers.bilibili')
 secrets=SecretStore(tmp_path/'secrets');secrets.write('bilibili','default',{'SESSDATA':'fixture'})
 provider=module.Bilibili(secrets,{})
 provider.client('default')._http_get=AsyncMock(return_value=({'code':0,'data':{'uname':'真实昵称','mid':42}},None))
 assert await provider.status('default')=={'ready':True,'state':'valid','nickname':'真实昵称','uid':'42'}

@pytest.mark.asyncio
async def test_xhh_status_uses_authenticated_credential_identity(tmp_path):
 provider=importlib.import_module(package+'.providers.xiaoheihe').Xiaoheihe(SecretStore(tmp_path/'secrets'),{})
 provider.clients['default']=SimpleNamespace(credentials=SimpleNamespace(nickname='盒友昵称',uid='99'),check_credentials=AsyncMock())
 assert (await provider.status('default'))['nickname']=='盒友昵称'

@pytest.mark.asyncio
async def test_music_identity_check_separate_from_scheduler_heartbeat():
 facade=SimpleNamespace(third_party_scheduler_api=1,third_party_scheduler_status=AsyncMock(return_value={'ready':True}),third_party_account_status=AsyncMock(return_value={'login_ready':True,'nickname':'音乐昵称','uid':'7'}))
 provider=importlib.import_module(package+'.integrations.music').Music(SimpleNamespace(get_registered_star=lambda _:SimpleNamespace(activated=True,star_cls=facade)))
 await provider.status('default');facade.third_party_account_status.assert_not_awaited()
 assert (await provider.account_status('default'))['nickname']=='音乐昵称'
 facade.third_party_account_status.return_value={'login_ready':False,'nickname':'','uid':''}
 assert (await provider.account_status('default'))['ready'] is False
