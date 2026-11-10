import importlib,sys,json
from pathlib import Path
from unittest.mock import AsyncMock
from types import SimpleNamespace as NS
import pytest
from quart import Quart
sys.path.insert(0,str(Path(__file__).resolve().parents[2]));base=Path(__file__).resolve().parents[1].name
main=importlib.import_module(base+'.main')

class Config(dict):
 def save_config(self):self.saved=True

@pytest.fixture
async def app(tmp_path,monkeypatch):
 monkeypatch.setattr(main.StarTools,'get_data_dir',lambda _:tmp_path)
 cfg=Config(enabled=False,platforms={})
 plugin=main.ThirdPartyPlatforms(NS(register_web_api=lambda *args:None),cfg)
 app=Quart(__name__);app.add_url_rule('/state',view_func=plugin.api_state);app.add_url_rule('/action',view_func=plugin.api_action,methods=['POST'])
 yield app,plugin
 await plugin.terminate()

async def test_account_save_and_secret_fields_rejected(app):
 app,plugin=app;client=app.test_client()
 response=await client.post('/action',json={'operation':'account_save','provider':'bilibili','account':'one','values':{'enabled':True,'share_enabled':False,'reply_enabled':True,'owner_uid':'123'}})
 assert response.status_code==200
 response=await client.get('/state');data=(await response.get_json())['data']
 assert data['platforms']['bilibili']['accounts']['one']['actions']['reply']
 assert not data['cutover_ready']
 response=await client.post('/action',json={'operation':'account_save','provider':'bilibili','account':'one','values':{'enabled':True,'token':'do-not-persist'}})
 assert response.status_code==400
 assert 'do-not-persist' not in json.dumps(plugin.config)

async def test_dev_gate_and_schedule_permissions(app):
 app,plugin=app;client=app.test_client()
 response=await client.post('/action',json={'operation':'pause','enabled':True})
 assert response.status_code==400 and not plugin.config['enabled']
 assert not plugin.authorized(NS(unified_msg_origin='xiaoheihe:GroupMessage:1'))
 plugin.config['control_umos']=['qq_bot:FriendMessage:1']
 assert plugin.authorized(NS(unified_msg_origin='qq_bot:FriendMessage:1'))

async def test_arbitrary_qr_payload_is_rendered_not_followed(app):
 app,plugin=app;client=app.test_client()
 provider=plugin.registry.get('xiaoheihe');provider.request_login=AsyncMock(return_value={'url':'heybox://login?test=opaque','expires_at':999})
 response=await client.post('/action',json={'operation':'login','provider':'xiaoheihe','account':'one'})
 data=(await response.get_json())['data']
 assert data['qr_image'].startswith('data:image/png;base64,') and 'url' not in data

async def test_logout_revokes_account_and_removes_credentials(app):
 app,plugin=app;client=app.test_client()
 plugin.config['platforms']={'bilibili':{'enabled':True,'accounts':{'one':{'enabled':True}}}}
 plugin.secrets.write('bilibili','one',{'SESSDATA':'test-fixture'})
 plugin.registry.get('bilibili').client('one')
 response=await client.post('/action',json={'operation':'logout','provider':'bilibili','account':'one'})
 assert response.status_code==200
 assert not plugin.config['platforms']['bilibili']['accounts']['one']['enabled']
 assert plugin.secrets.read('bilibili','one')=={}
 assert 'one' not in plugin.registry.get('bilibili').clients

async def test_paused_runtime_allows_preparing_and_editing_schedule(app):
 import time
 app,plugin=app;client=app.test_client()
 plugin.config['platforms']={'bilibili':{'enabled':False,'accounts':{'one':{'enabled':False,'browse':{}}}}}
 stamp=time.time()+3600
 response=await client.post('/action',json={'operation':'create','provider':'bilibili','account':'one','start':stamp,'end':stamp+3600})
 assert response.status_code==200
 key=(await response.get_json())['data']['id']
 response=await client.post('/action',json={'operation':'move','id':key,'revision':1,'start':stamp+100,'end':stamp+3700})
 assert response.status_code==200
 response=await client.post('/action',json={'operation':'cancel','id':key,'revision':1})
 assert response.status_code==400 # Stale revision never overwrites a concurrent edit.
 assert not plugin.config['enabled'] and plugin.store.actions()==[]


async def test_provider_extension_can_configure_without_changing_scheduler(app):
 app,plugin=app;client=app.test_client()
 adapter=NS(id='example_media',capabilities={'browse','owner_share'},status=AsyncMock(),browse=AsyncMock(),close=AsyncMock())
 plugin.third_party_register_provider(adapter,{'api':1,'name':'Example','fields':{
  'section':{'type':'string','default':'games'},'max_items':{'type':'int','default':2,'min':1,'max':5}}})
 response=await client.post('/action',json={'operation':'account_save','provider':'example_media','account':'one',
  'values':{'enabled':True,'share_enabled':True,'owner_umo':'qq:FriendMessage:1','provider_options':{'section':'sports'}}})
 assert response.status_code==200
 account=plugin.config['platforms']['example_media']['accounts']['one']
 assert account['browse']['provider_options']=={'section':'sports','max_items':2}
 response=await client.post('/action',json={'operation':'account_save','provider':'example_media','account':'one',
  'values':{'provider_options':{'access_token':'must-not-persist'}}})
 assert response.status_code==400 and 'must-not-persist' not in json.dumps(plugin.config)
 state=(await (await client.get('/state')).get_json())['data']
 assert state['provider_manifests']['example_media']['name']=='Example'
 with pytest.raises(ValueError):plugin.third_party_register_provider(adapter)


async def test_dynamic_requires_cutover_authority_and_deduplicates_user_message(app,monkeypatch):
 app,plugin=app
 plugin.config.update(enabled=True,control_umos=['qq:FriendMessage:1'])
 plugin.config['platforms']={'bilibili':{'enabled':True,'accounts':{'one':{'enabled':True,'actions':{'dynamic':True},'daily_limits':{'dynamic':2}}}}}
 from importlib import import_module
 Receipt=import_module(base+'.core.models').Receipt
 adapter=plugin.registry.get('bilibili');adapter.execute=AsyncMock(return_value=Receipt('succeeded','dynamic-id'))
 event=NS(unified_msg_origin='qq:FriendMessage:1',message_obj=NS(message_id='message-1'))
 assert (await plugin.publish_dynamic(event,'public text','one'))['error']=='migration_not_ready'
 monkeypatch.setattr(plugin,'cutover_ready',lambda:True)
 denied=NS(unified_msg_origin='xiaoheihe:GroupMessage:1',message_obj=NS(message_id='message-1'))
 assert (await plugin.publish_dynamic(denied,'public text','one'))['error']=='not_authorized'
 assert (await plugin.publish_dynamic(event,'SESSDATA=must-not-publish','one'))['error']=='invalid_public_text'
 assert (await plugin.publish_dynamic(event,'public text','one'))['state']=='succeeded'
 assert (await plugin.publish_dynamic(event,'different draft on retry','one'))['state']=='not_repeated'
 assert adapter.execute.await_count==1


async def test_music_takeover_publication_uses_shared_score_floor(app,monkeypatch):
 app,plugin=app
 plugin.config.update(enabled=True,share_min_score=8)
 plugin.config['platforms']={'netease':{'enabled':True,'accounts':{'default':{'enabled':True,'actions':{'listen':True}}}}}
 monkeypatch.setattr(plugin,'cutover_ready',lambda:True)
 from importlib import import_module
 Evaluation=import_module(base+'.core.models').Evaluation
 plugin.reader.evaluate=AsyncMock(return_value=Evaluation(7,'reason','evidence',True))
 assert not await plugin.music_publication_gate('share',{'id':1,'name':'song'},{'lyric':'public lyric'})
 plugin.reader.evaluate.return_value=Evaluation(9,'reason','evidence',True)
 assert await plugin.music_publication_gate('share',{'id':1,'name':'song'},{'lyric':'public lyric'})
 plugin.config['share_min_score']=10
 assert not await plugin.music_publication_gate('invite',{'id':1,'name':'song'},{'lyric':'public lyric'})
 plugin.config['enabled']=False
 assert not await plugin.music_publication_gate('share',{'id':1,'name':'song'},{'lyric':'public lyric'})
