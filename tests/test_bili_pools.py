import importlib,sys,asyncio
from pathlib import Path
from unittest.mock import AsyncMock
sys.path.insert(0,str(Path(__file__).resolve().parents[2]));base=Path(__file__).resolve().parents[1].name
module=importlib.import_module(base+'.providers.bilibili')

def test_chinese_and_legacy_pool_names_resolve():
 from types import SimpleNamespace
 pool=module.PoolClient(SimpleNamespace(_http_get=AsyncMock()),['popular'])
 assert pool._resolve_video_pool_spec('推荐')[0]=='rcmd'
 assert pool._resolve_video_pool_spec('排行榜:游戏')[:2]==('ranking',[4])
 assert pool._resolve_video_pool_spec('最新:单机游戏')[:2]==('newlist',[17])
 assert pool._resolve_video_pool_spec('ranking:4')[:2]==('ranking',[4])

def test_recommendation_pool_honors_page_size_and_skips_ads():
 async def run():
  requests=[]
  class Client:
   async def _http_get(self,url,**kwargs):
    requests.append((url,kwargs));return {'code':0,'data':{'item':[{'goto':'ad','bvid':'ad'},{'goto':'av','bvid':'BV1234567890','title':'title'}]}},None
  pool=module.PoolClient(Client(),['rcmd']);rows=await pool._get_rcmd_videos()
  assert requests[0][1]['params']['ps']<=14
  assert [r['bvid'] for r in rows]==['BV1234567890']
 asyncio.run(run())


def test_legacy_diagnostics_do_not_emit_cookie_values_or_url_query_secrets():
 from unittest.mock import Mock
 diagnostics=importlib.import_module(base+'.providers.bili_client.diagnostics')
 backend=Mock();logger=diagnostics.Diagnostics(backend)
 logger.warning('request failed %s','SESSDATA=test-cookie buvid3=test-device https://api.bilibili.com/a?access_token=fixture')
 text=backend.warning.call_args.args[0]
 assert 'test-cookie' not in text and 'test-device' not in text and 'fixture' not in text
 assert '[REDACTED]' in text
