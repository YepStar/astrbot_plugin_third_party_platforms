"""Migration behavior with synthetic platform/model IO; never publish test messages."""
import asyncio
import importlib
import json
from pathlib import Path
import sys
import time
from types import SimpleNamespace as NS
from unittest.mock import AsyncMock
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
base=Path(__file__).resolve().parents[1].name
bili=importlib.import_module(base+'.providers.bilibili')
Store=importlib.import_module(base+'.core.store').Store
Secrets=importlib.import_module(base+'.core.secrets').SecretStore
Circuit=importlib.import_module(base+'.core.reliability').ModelCircuit
models=importlib.import_module(base+'.core.models')


def provider(tmp_path, *, reply=None, browse=None, network=None, generate=None):
    config={'vision_policy':'off','platforms':{'bilibili':{'enabled':True,'accounts':{'one':{'enabled':True,'reply':reply or {},'browse':browse or {},'network':network or {}}}}}}
    return bili.Bilibili(Secrets(tmp_path/'secrets'),config,generate=generate)


@pytest.mark.asyncio
async def test_circuit_pauses_failures_then_allows_one_probe():
    now=[10];circuit=Circuit(lambda:now[0]);failure=AsyncMock(side_effect=RuntimeError('fixture'))
    for _ in range(2):
        with pytest.raises(RuntimeError):await circuit.call('model',failure,2,30)
    with pytest.raises(RuntimeError,match='circuit_open'):await circuit.call('model',failure,2,30)
    assert failure.await_count==2
    now[0]=41;entered=asyncio.Event();finish=asyncio.Event()
    async def probe():entered.set();await finish.wait();return 'ok'
    task=asyncio.create_task(circuit.call('model',probe,2,30));await entered.wait()
    with pytest.raises(RuntimeError,match='circuit_open'):await circuit.call('model',failure,2,30)
    finish.set();assert await task=='ok'
    assert circuit.states['model']['failures']==0


@pytest.mark.asyncio
async def test_cancelled_generation_does_not_count_as_model_failure():
    circuit=Circuit();operation=AsyncMock(side_effect=asyncio.CancelledError)
    with pytest.raises(asyncio.CancelledError):await circuit.call('model',operation)
    assert circuit.states['model']['failures']==0


@pytest.mark.asyncio
async def test_qr_login_retains_refresh_token_without_exposing_it(tmp_path):
    p=provider(tmp_path);p.qr['one']={'key':'fixture','expires_at':time.time()+60}
    p.client('one')._http_get=AsyncMock(return_value=({'code':0,'data':{'code':0,'refresh_token':'fixture-refresh'}},NS(cookies={'SESSDATA':NS(value='fixture-session')})))
    result=await p.poll_login('one')
    assert p.secrets.read('bilibili','one')['REFRESH_TOKEN']=='fixture-refresh'
    assert result=={'state':'success'} and 'fixture-refresh' not in json.dumps(result)


@pytest.mark.asyncio
async def test_login_maintenance_refreshes_and_respects_check_interval(tmp_path):
    p=provider(tmp_path);client=p.client('one');client.config.update(SESSDATA='fixture',REFRESH_TOKEN='fixture-refresh')
    p.status=AsyncMock(return_value={'ready':True,'state':'valid'})
    client.check_need_refresh=AsyncMock(return_value=(True,'fixture'))
    client.refresh_cookie=AsyncMock(return_value=(True,'fixture'))
    result=await p.maintain_login('one',now=100000)
    assert result['maintenance']=='refreshed'
    assert await p.maintain_login('one',now=100001) is None
    assert client.refresh_cookie.await_count==1


@pytest.mark.asyncio
async def test_missing_refresh_token_is_diagnostic_not_fabricated_success(tmp_path):
    p=provider(tmp_path);p.client('one').config['SESSDATA']='fixture'
    p.status=AsyncMock(return_value={'ready':True,'state':'valid'})
    result=await p.maintain_login('one',now=100000)
    assert result['ready'] is True and result['maintenance']=='refresh_token_missing'


@pytest.mark.asyncio
async def test_disabled_cookie_refresh_does_not_refresh(tmp_path):
    p=provider(tmp_path,network={'cookie_auto_refresh':False});client=p.client('one');client.config.update(SESSDATA='fixture',REFRESH_TOKEN='fixture')
    p.status=AsyncMock(return_value={'ready':True,'state':'valid'});client.check_need_refresh=AsyncMock()
    await p.maintain_login('one',now=100000);client.check_need_refresh.assert_not_awaited()


@pytest.mark.asyncio
async def test_private_video_uses_real_read_evidence_and_never_sends(tmp_path):
    p=provider(tmp_path,reply={'private_auto_watch':True});p.execute=AsyncMock()
    p.read_video=AsyncMock(return_value=models.Content('bilibili','one','BV1234567890','https://www.bilibili.com/video/BV1234567890','视频标题','字幕中的真实内容',modality='subtitle'))
    event=NS(account='one',text='看看这个 https://www.bilibili.com/video/BV1234567890')
    source=await p.private_context(event)
    assert '字幕中的真实内容' in source['text'] and 'subtitle' in source['text']
    p.read_video.assert_awaited_once_with('one','BV1234567890');p.execute.assert_not_awaited()


@pytest.mark.asyncio
async def test_private_video_failure_preserves_unavailable_evidence(tmp_path):
    p=provider(tmp_path,reply={'private_auto_watch':True});p.read_video=AsyncMock(side_effect=RuntimeError())
    source=await p.private_context(NS(account='one',text='BV1234567890'))
    assert 'unavailable' in source['text']


@pytest.mark.asyncio
async def test_ordinary_private_chat_never_launches_search(tmp_path):
    generate=AsyncMock();p=provider(tmp_path,reply={'private_search_enabled':True},generate=generate)
    await p.private_context(NS(account='one',text='今天心情很好'))
    generate.assert_not_awaited()


@pytest.mark.asyncio
async def test_private_explicit_video_search_is_bounded_read_only(tmp_path):
    generate=AsyncMock(return_value='{"search":true,"query":"机械键盘","kind":"video"}')
    p=provider(tmp_path,reply={'private_search_enabled':True,'private_search_limit':2},generate=generate)
    p.search=AsyncMock(return_value={'items':[{'title':'fixture'}]});p.execute=AsyncMock()
    source=await p.private_context(NS(account='one',text='搜索机械键盘视频'))
    p.search.assert_awaited_once_with('one','机械键盘',2);p.execute.assert_not_awaited()
    assert 'fixture' in source['text']


@pytest.mark.asyncio
async def test_private_search_rejects_credential_like_query(tmp_path):
    p=provider(tmp_path,reply={'private_search_enabled':True},generate=AsyncMock(return_value='{"search":true,"query":"cookie=fixture","kind":"video"}'))
    p.search=AsyncMock();source=await p.private_context(NS(account='one',text='搜索视频'))
    p.search.assert_not_awaited();assert 'unavailable' in source['text']


@pytest.mark.asyncio
async def test_private_up_search_has_explicit_read_only_route(tmp_path):
    p=provider(tmp_path,reply={'private_search_enabled':True},generate=AsyncMock(return_value='{"search":true,"query":"摄影","kind":"up"}'))
    client=p.client('one');client._http_get=AsyncMock(return_value=({'code':0,'data':{'result':[{'mid':12,'uname':'作者'}]}},None))
    source=await p.private_context(NS(account='one',text='搜索摄影UP主'))
    assert 'space.bilibili.com/12' in source['text']
    assert client._http_get.await_args.kwargs['params']['search_type']=='bili_user'


@pytest.mark.asyncio
async def test_prefilter_selects_before_video_download(tmp_path):
    p=provider(tmp_path,generate=AsyncMock(return_value='{"indices":[1]}'))
    rows=[{'title':'a'},{'title':'b'},{'title':'c'}]
    assert await p.prefilter('one',rows,{'prefilter_enabled':True},1)==[rows[1]]
    data=p.generate.await_args.args[1];assert len(data['candidates'])==3


@pytest.mark.asyncio
@pytest.mark.parametrize('raw',['{"indices":[10]}','{"indices":[true]}','{"indices":[0,0]}','not JSON'])
async def test_prefilter_invalid_output_falls_back_boundedly(tmp_path,raw):
    p=provider(tmp_path,generate=AsyncMock(return_value=raw));rows=[{'title':'a'},{'title':'b'}]
    assert await p.prefilter('one',rows,{'prefilter_enabled':True},1)==rows[:1]


@pytest.mark.asyncio
async def test_zero_remaining_video_budget_never_calls_prefilter(tmp_path):
    p=provider(tmp_path,generate=AsyncMock())
    assert await p.prefilter('one',[{'title':'fixture'}],{'prefilter_enabled':True},0)==[]
    p.generate.assert_not_awaited()


def test_interest_learning_is_account_scoped_and_excludes_low_scores(tmp_path):
    store=Store(tmp_path/'db');now=time.time()
    store.observe(models.Content('bilibili','one','x','','',''),models.Evaluation(9,'reason','evidence',False,('摄影',)),12,now)
    store.observe(models.Content('bilibili','two','y','','',''),models.Evaluation(9,'reason','evidence',False,('游戏',)),12,now)
    store.observe(models.Content('bilibili','one','z','','',''),models.Evaluation(2,'reason','evidence',False,('广告',)),12,now)
    assert [x['interest'] for x in store.interests('bilibili','one',now)]==['摄影']
    report=store.activity_report('bilibili','one',now-1,now+1)
    assert report['evaluated_count']==2 and report['average_score']==5.5 and report['actions']==[]


@pytest.mark.asyncio
async def test_explicit_search_query_overrides_interest_learning(tmp_path):
    p=provider(tmp_path,generate=AsyncMock())
    assert await p.interest_query('one',{'query':'用户指定主题','interest_search_enabled':True})=='用户指定主题'
    p.generate.assert_not_awaited()


@pytest.mark.asyncio
async def test_interest_search_consumes_only_observed_public_interests(tmp_path):
    p=provider(tmp_path,generate=AsyncMock(return_value='{"query":"相机评测"}'))
    p.interest_source=lambda account:[{'interest':'摄影','weight':3}]
    for session in range(30):
        query=await p.interest_query('one',{'interest_search_enabled':True,'_session_id':str(session)})
        if query:break
    assert query=='相机评测' and p.generate.await_args.args[1]['interests'][0]['interest']=='摄影'


@pytest.mark.asyncio
async def test_dynamic_reading_has_age_dedupe_and_special_follow_boundaries(tmp_path):
    p=provider(tmp_path);client=p.client('one');stamp=time.time()
    def item(identifier,at):return {'id_str':identifier,'type':'DYNAMIC_TYPE_WORD','modules':{'module_author':{'mid':123,'pub_ts':at},'module_dynamic':{'desc':{'text':'这是关注作者发布的实际动态文字，包含足够详细的内容供评价和阅读。'}}}}
    client._http_get=AsyncMock(return_value=({'code':0,'data':{'items':[item('1',stamp),item('2',stamp-90000),item('3',stamp)]}},None))
    rows=await p.read_dynamics('one',{'follow_uids':['123'],'_skip_ids':['dynamic:1']},3)
    assert [x.external_id for x in rows]==['dynamic:3']
    assert rows[0].metadata['kind']=='dynamic'
    assert client._http_get.await_args.kwargs['params']['host_mid']=='123'


@pytest.mark.asyncio
async def test_special_dynamic_mode_without_authors_does_not_fetch_global_feed(tmp_path):
    p=provider(tmp_path);client=p.client('one');client._http_get=AsyncMock()
    assert await p.read_dynamics('one',{'dynamic_special_only':True},2)==[]
    client._http_get.assert_not_awaited()


@pytest.mark.asyncio
async def test_refresh_html_rejects_arbitrary_host_and_paths():
    client=bili.Client({})
    for url in ['https://evil.example/correspond/1/abc','https://www.bilibili.com/video/abc','https://www.bilibili.com/correspond/1/abc?token=fixture']:
        with pytest.raises(ValueError,match='untrusted_refresh'):await client._http_get_text(url)


@pytest.mark.asyncio
async def test_native_video_card_reaches_private_inbox_as_video_reference(tmp_path):
    p=provider(tmp_path);p.account_options('one')['actions']={'private_reply':True};client=p.client('one')
    async def get(url,**kwargs):
        if 'get_sessions' in url:return {'code':0,'data':{'session_list':[{'talker_id':123,'session_type':1,'max_seqno':2}]}},None
        return {'code':0,'data':{'messages':[{'msg_seqno':2,'sender_uid':123,'msg_type':7,'timestamp':time.time(),'msg_key':'fixture','content':json.dumps({'bvid':'BV1234567890'})}]}},None
    client._http_get=AsyncMock(side_effect=get)
    streams=await p.poll_events('one',lambda _: {'sessions':{'123':1},'started_at':0})
    assert streams[0][1][0].text.endswith('BV1234567890')


@pytest.mark.asyncio
async def test_segment_sampling_covers_bounded_distant_segments(tmp_path):
    FrameSource=importlib.import_module(base+'.providers.bili_client.media').FrameSource
    source=FrameSource(tmp_path,{}, {'video_segment_minutes':5,'video_segment_max_count':3})
    async def run(*args,**kwargs):
        if args[0]=='ffprobe':return 0,'3600',''
        Path(args[-1]).write_bytes(b'jpeg-fixture');return 0,'',''
    source._run_process=run
    frames=await source._extract_video_frames(str(tmp_path/'fixture.mp4'),count=5)
    assert 3<=len(frames)<=12 and max(source.sample_points)>3300 and min(source.sample_points)<300


def test_migration_preserves_prior_switches_and_clamps_legacy_ranges():
    migration=importlib.import_module(base+'.migration')
    config=migration.build_config({'PRIVATE_MESSAGE_AUTO_WATCH_VIDEO':True,'PRIVATE_MESSAGE_BILI_SEARCH_ENABLED':True,'ENABLE_DYNAMIC_WATCH':False,'ENABLE_PROACTIVE_LLM_PREFILTER':True,'PRIVATE_MESSAGE_POLL_INTERVAL':5,'PRIVATE_MESSAGE_BILI_SEARCH_LIMIT':10},{})
    account=config['platforms']['bilibili']['accounts']['default']
    assert account['reply']['private_auto_watch'] and account['reply']['private_search_enabled']
    assert account['reply']['private_poll_seconds']==30 and account['reply']['private_search_limit']==3
    assert account['browse']['prefilter_enabled'] and not account['browse']['dynamic_watch_enabled']
    assert not account['network']['operational_alerts'] and not config['enabled']


def test_review_list_removes_rejected_options_and_keeps_actual_decisions():
    root=Path(__file__).resolve().parents[1]
    text=(root/'pages/control/bili_reference.js').read_text();rows=json.loads(text[text.index('['):].strip().rstrip(';'))
    keyed={x['key']:x for x in rows}
    assert 'ENABLE_PERSONALITY_EVOLUTION' not in keyed and 'SUMMARY_MODEL' not in keyed and 'ENABLE_AFFECTION' not in keyed
    assert 'ENABLE_LIVE_DANMAKU_REPLY' not in keyed and keyed['ENABLE_MOOD']['status']=='ported'
    assert keyed['PRIVATE_MESSAGE_AUTO_WATCH_VIDEO']['status']=='ported'
    assert keyed['ENABLE_WEEKLY_SUMMARY']['status']=='ported' and '活动回顾' in keyed['ENABLE_WEEKLY_SUMMARY']['target']

@pytest.mark.asyncio
async def test_dynamic_browse_never_reuses_video_coin_or_comment_actions(tmp_path):
    Policy=importlib.import_module(base+'.core.policy').Policy
    Executor=importlib.import_module(base+'.core.execution').Executor
    Service=importlib.import_module(base+'.core.service').BrowsingService
    now=time.time();store=Store(tmp_path/'db')
    cfg={'enabled':True,'daily_limit':20,'minute_limit':20,'platforms':{'bilibili':{'enabled':True,'accounts':{'one':{'enabled':True,'actions':{'comment':True},'daily_limits':{'browse':2,'comment':2},'browse':{'video_daily_limit':1},'interactions':{'coin_enabled':True,'coin_min_score':1}}}}}}
    content=models.Content('bilibili','one','dynamic:123','https://t.bilibili.com/123','标题','实际动态内容',metadata={'kind':'dynamic'})
    adapter=NS(id='bilibili',capabilities={'browse','comment','coin'},browse=AsyncMock(return_value=[content]),execute=AsyncMock())
    registry=models.Registry();registry.register(adapter);policy=Policy(cfg)
    reader=NS(evaluate=AsyncMock(return_value=models.Evaluation(9,'真实理由','实际动态内容',False)),comment_text=AsyncMock())
    service=Service(store,registry,Executor(store,registry,policy),reader,NS(put=lambda *args:'disabled'),AsyncMock(),clock=lambda:now)
    await service.browse({'id':'fixture','provider':'bilibili','account':'one','params':{},'end':now+100})
    adapter.execute.assert_not_awaited();reader.comment_text.assert_not_awaited()
    assert store.setting('last_read')['external_id']=='dynamic:123'


@pytest.mark.asyncio
async def test_dynamic_owner_share_uses_private_channels_without_video_comment(tmp_path):
    setup=importlib.import_module(base+'.tests.test_sharing').setup
    sharing=importlib.import_module(base+'.core.sharing')
    service,adapter,item,content,evaluation=setup(tmp_path,'all')
    from dataclasses import replace
    content=replace(content,external_id='dynamic:123',metadata={'kind':'dynamic'})
    result=await sharing.share(service,content,evaluation,'实际动态分享',item)
    assert result.state=='succeeded'
    assert adapter.execute.await_count==1 and adapter.execute.await_args.args[1]=='private_reply'
    assert service.deliver.await_count==1
