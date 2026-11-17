"""Selected migration features; all platform writes are synthetic."""
import asyncio,importlib,json,sys,time
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import AsyncMock,Mock
from contextlib import asynccontextmanager
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]));base=Path(__file__).resolve().parents[1].name
Store=importlib.import_module(base+'.core.store').Store
models=importlib.import_module(base+'.core.models')
Life=importlib.import_module(base+'.core.bili_life').BiliLife
Moderation=importlib.import_module(base+'.core.bili_moderation').BiliModeration
Policy=importlib.import_module(base+'.core.policy').Policy
Executor=importlib.import_module(base+'.core.execution').Executor
bili=importlib.import_module(base+'.providers.bilibili')
Secrets=importlib.import_module(base+'.core.secrets').SecretStore


def setup(tmp_path,life=None,safety=None):
    cfg={'enabled':True,'daily_limit':30,'minute_limit':20,'daily_rounds':4,'timezone':'Asia/Shanghai','windows':['00:00-23:59'],'rest_windows':[],
         'platforms':{'bilibili':{'enabled':True,'accounts':{'one':{'enabled':True,'owner_uid':'42','self_uid':'99','owner_umo':'qq:FriendMessage:42','life':life or {},'safety':safety or {},'actions':{'dynamic':True},'daily_limits':{'dynamic':2}}}}}}
    h=NS(config=cfg,store=Store(tmp_path/'db'),generate=AsyncMock(),deliver=AsyncMock(),deliver_card=AsyncMock(),context=NS(get_registered_star=lambda _:None))
    h.policy=Policy(cfg);adapter=NS(id='bilibili',capabilities={'dynamic','block_user'},execute=AsyncMock(return_value=models.Receipt('succeeded','remote-id')))
    h.registry=models.Registry();h.registry.register(adapter);h.executor=Executor(h.store,h.registry,h.policy);h.life=Life(h);return h,adapter


def content():return models.Content('bilibili','one','BV1234567890','https://www.bilibili.com/video/BV1234567890','真实视频标题','真实字幕证据')
def evaluation():return models.Evaluation(9,'实际观看理由','真实字幕证据',True)
def event(key='evt',actor='123',text='明确辱骂内容',stream='reply'):
    return models.Incoming('bilibili','one',stream,key,actor,text,time.time(),{},True)


@pytest.mark.asyncio
async def test_mood_requires_real_evidence_and_expires(tmp_path):
    h,_=setup(tmp_path,{'mood_enabled':True});now=[100000];h.life.clock=lambda:now[0]
    h.generate.return_value='{"mood":"开心","evidence":"真实字幕证据"}'
    await h.life.observe(content(),evaluation());assert h.life.expression('one')['mood']=='开心'
    now[0]+=21601;assert h.life.expression('one')=={}
    assert h.life.expression('another')=={}


@pytest.mark.asyncio
async def test_invented_mood_evidence_is_not_recorded(tmp_path):
    h,_=setup(tmp_path,{'mood_enabled':True});h.generate.return_value='{"mood":"开心","evidence":"虚构证据"}'
    await h.life.observe(content(),evaluation());assert h.life.expression('one')=={}


@pytest.mark.asyncio
async def test_companion_activity_uses_active_public_facade_and_ends(tmp_path):
    h,_=setup(tmp_path,{'activity_sync':True});api=NS(bridge_lifecycle_status=lambda:{'active':True},notify_external_activity_updated=Mock(),notify_external_activity_ended=Mock())
    h.context.get_registered_star=lambda _:NS(activated=True,star_cls=NS(extension_api=api))
    await h.life.activity('one',{'id':'fixture'},'reading')
    assert api.notify_external_activity_updated.call_args.kwargs['user_id']=='42'
    assert api.notify_external_activity_updated.call_args.kwargs['source_plugin']=='astrbot_plugin_third_party_platforms'
    await h.life.activity('one',{'id':'fixture'},'finished',ended=True);api.notify_external_activity_ended.assert_called_once()


@pytest.mark.asyncio
async def test_disabled_activity_does_not_call_companion(tmp_path):
    h,_=setup(tmp_path);h.context.get_registered_star=Mock()
    await h.life.activity('one',{'id':'fixture'},'reading');h.context.get_registered_star.assert_not_called()


@pytest.mark.asyncio
async def test_summary_no_data_does_not_invent_events(tmp_path):
    h,_=setup(tmp_path)
    assert await h.life.make_summary('one','daily','period',0,time.time()) is None
    h.generate.assert_not_awaited()


@pytest.mark.asyncio
async def test_summary_is_cited_archived_and_only_generated_once(tmp_path):
    h,_=setup(tmp_path);await h.life.observe(content(),evaluation())
    h.generate.return_value='{"text":"我读到了真实视频内容。","source_indices":[0]}'
    first=await h.life.make_summary('one','daily','period',0,time.time()+1)
    second=await h.life.make_summary('one','daily','period',0,time.time()+1)
    assert first==second and first['sources'][0]['title']=='真实视频标题'
    assert h.generate.await_count==1;await h.life.deliver_summary('one',first)
    h.deliver.assert_not_awaited()


@pytest.mark.asyncio
async def test_summary_rejects_unattached_source_index(tmp_path):
    h,_=setup(tmp_path);await h.life.observe(content(),evaluation());h.generate.return_value='{"text":"虚构内容","source_indices":[42]}'
    with pytest.raises(ValueError):await h.life.make_summary('one','daily','period',0,time.time()+1)
    assert h.store.setting('bili_summary:one:daily:period') is None


@pytest.mark.asyncio
async def test_uncertain_summary_qq_send_is_never_repeated(tmp_path):
    h,_=setup(tmp_path,{'daily_summary_mode':'qq'});h.deliver.side_effect=TimeoutError
    record={'kind':'daily','period':'period','text':'实际日报'}
    await h.life.deliver_summary('one',record);await h.life.deliver_summary('one',record)
    assert h.deliver.await_count==1


@pytest.mark.asyncio
async def test_auto_dynamic_needs_evidence_and_preserves_disabled_switch(tmp_path):
    h,adapter=setup(tmp_path,{'autonomous_dynamic_enabled':True});task={'id':'fixture','account':'one','end':time.time()+100}
    assert (await h.life.publish_dynamic(task)).code=='no_actual_experiences'
    await h.life.observe(content(),evaluation());h.generate.side_effect=['{"publish":true,"text":"真实内容的感想。","source_indices":[0]}','{"grounded":true,"private_claims":false}']
    result=await h.life.publish_dynamic(task);assert result.state=='succeeded'
    assert (await h.life.publish_dynamic(task)).code=='automatic_dynamic_interval'
    assert adapter.execute.await_count==1


@pytest.mark.asyncio
async def test_dynamic_rechecks_disable_during_generation(tmp_path):
    h,adapter=setup(tmp_path,{'autonomous_dynamic_enabled':True});await h.life.observe(content(),evaluation())
    async def generate(phase,*args):
        if phase=='attribution_review':return '{"grounded":true,"private_claims":false}'
        h.config['platforms']['bilibili']['accounts']['one']['life']['autonomous_dynamic_enabled']=False;return '{"publish":true,"text":"真实感想","source_indices":[0]}'
    h.generate=generate
    result=await h.life.publish_dynamic({'id':'fixture','account':'one','end':time.time()+100})
    assert result.code=='automatic_dynamic_disabled';adapter.execute.assert_not_awaited()


@pytest.mark.asyncio
async def test_dynamic_schedule_obeys_global_daily_round_limit(tmp_path):
    h,_=setup(tmp_path,{'autonomous_dynamic_enabled':True,'dynamic_times':3});h.config['daily_rounds']=1
    now=time.time();h.store.create_task('bilibili','one','browse',now,now+600)
    await h.life.ensure_dynamic_plan('one',now)
    assert len(h.store.tasks())==1


@pytest.mark.asyncio
async def test_moderation_never_blocks_protected_owner(tmp_path):
    h,adapter=setup(tmp_path,safety={'auto_block':True,'block_negative_times':1})
    h.generate.return_value='{"abusive":true,"delta":-5,"evidence":"明确辱骂","reason":"辱骂"}'
    guard=Moderation(h);cfg=h.policy.account('bilibili','one')
    assert await guard.assess(event(actor='42'),cfg)
    adapter.execute.assert_not_awaited()


@pytest.mark.asyncio
async def test_moderation_ledger_dedupes_and_blocks_only_once(tmp_path):
    h,adapter=setup(tmp_path,safety={'auto_block':True,'block_negative_times':2})
    h.generate.return_value='{"abusive":true,"delta":-3,"evidence":"明确辱骂","reason":"辱骂"}'
    guard=Moderation(h);cfg=h.policy.account('bilibili','one')
    await guard.assess(event('one'),cfg);await guard.assess(event('one'),cfg)
    assert h.store.setting('abuse_ledger:one:public:123')['count']==1;adapter.execute.assert_not_awaited()
    await guard.assess(event('two'),cfg);await guard.assess(event('two'),cfg)
    assert adapter.execute.await_count==1


@pytest.mark.asyncio
@pytest.mark.parametrize('raw',['{"abusive":true,"delta":true,"evidence":"明确辱骂"}','{"abusive":true,"delta":-5,"evidence":"虚构"}','{"abusive":false,"delta":-5,"evidence":"明确辱骂"}'])
async def test_invalid_or_uncertain_abuse_never_blocks(tmp_path,raw):
    h,adapter=setup(tmp_path,safety={'auto_block':True,'block_negative_times':1});h.generate.return_value=raw
    assert not await Moderation(h).assess(event(),h.policy.account('bilibili','one'));adapter.execute.assert_not_awaited()


@pytest.mark.asyncio
async def test_private_untrusted_link_is_isolated_without_opening_url(tmp_path):
    h,adapter=setup(tmp_path,safety={'private_auto_block':True});h.generate=AsyncMock()
    assert await Moderation(h).assess(event(text='https://untrusted.example/path',stream='private'),h.policy.account('bilibili','one'))
    assert adapter.execute.await_count==1;h.generate.assert_not_awaited()


@pytest.mark.asyncio
async def test_private_whitelist_protects_sender(tmp_path):
    h,adapter=setup(tmp_path,safety={'private_auto_block':True,'private_block_whitelist':['123']})
    assert await Moderation(h).assess(event(text='https://untrusted.example/path',stream='private'),h.policy.account('bilibili','one'))
    adapter.execute.assert_not_awaited()


@pytest.mark.asyncio
async def test_direct_video_passes_actual_media_and_audio_contract(tmp_path):
    p=bili.Bilibili(Secrets(tmp_path/'secret'),{},generate=AsyncMock(return_value='{"observed":true,"audio_observed":true,"description":"真实视频音画观察"}'))
    video=tmp_path/'clip.mp4';video.write_bytes(b'fixture-video')
    @asynccontextmanager
    async def download(_):yield video
    result=await p.direct_video('one','BV1234567890',NS(download=download),{'video_direct_format':'qwen','video_direct_fps':3})
    assert result['modality']=='direct_video_audio'
    data=p.generate.await_args.args[1];assert data['_validated_video_parts'][0]['type']=='video_url'
    assert data['_validated_video_parts'][0]['fps']==3
    assert data['_validated_video_parts'][0]['video_url']['url'].startswith('data:video/mp4;base64,')


@pytest.mark.asyncio
async def test_direct_unsupported_media_never_claims_observed(tmp_path):
    p=bili.Bilibili(Secrets(tmp_path/'secret'),{},generate=AsyncMock(return_value='{"observed":false,"audio_observed":false,"description":""}'))
    video=tmp_path/'clip.mp4';video.write_bytes(b'fixture-video')
    @asynccontextmanager
    async def download(_):yield video
    with pytest.raises(ValueError):await p.direct_video('one','BV1234567890',NS(download=download),{'video_direct_format':'gemini'})


@pytest.mark.asyncio
async def test_private_image_uses_image_provider_evidence_before_reply(tmp_path):
    cfg={'platforms':{'bilibili':{'accounts':{'one':{'vision':{'private_image_enabled':True}}}}}}
    generate=AsyncMock(return_value='{"observed":true,"description":"图片里有一只白猫"}')
    p=bili.Bilibili(Secrets(tmp_path/'secret'),cfg,generate=generate)
    result=await p.private_context(NS(account='one',text='[图片]',context={'image_urls':['https://i0.hdslb.com/fixture.jpg']}))
    assert result['images']==[] and '白猫' in result['text'] and generate.await_args.args[0]=='private_image'


def test_summary_card_renders_chinese_without_legacy_plugin(tmp_path):
    from PIL import Image
    renderer=importlib.import_module(base+'.core.bili_life').render_card
    path=renderer('每日总结\n今天阅读了实际的视频内容。'*5,tmp_path,'fixture')
    image=Image.open(path);assert image.width==1000 and image.height>200


def test_new_settings_validate_and_keep_automatic_writes_off():
    normalize=importlib.import_module(base+'.core.configuration').account
    cfg=normalize('bilibili',{'enabled':True})
    assert not cfg['life']['autonomous_dynamic_enabled'] and not cfg['life']['daily_summary_enabled'] and not cfg['safety']['auto_block']
    assert normalize('bilibili',{'private_tool_allowlist':['get_up_info']})['reply']['private_tool_allowlist']==['get_up_info']
    for values in [{'daily_summary_mode':'unknown'},{'video_direct_fps':10},{'block_whitelist':['not-a-uid']},{'abuse_alert_umo':'qq:GroupMessage:1'}]:
        with pytest.raises(ValueError):normalize('bilibili',values)
