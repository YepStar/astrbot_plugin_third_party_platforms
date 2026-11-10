"""Bili HTTP extraction. No old Star, scheduler, memory store or private configuration."""
import asyncio
import json
import re
from urllib.parse import urlsplit
import aiohttp
from .bili_client.bilibili import BilibiliAPIMixin
from .bili_client.network import plugin_http_session
from .bili_client.config import USER_AGENT, BILI_REPLY_URL, BILI_DYNAMIC_TEXT_URL
from ..core.models import Content,Receipt

class CredentialsConfig(dict):
    def __init__(self,values,save):super().__init__(values);self.save=save
    def save_config(self):self.save(dict(self))

class Client(BilibiliAPIMixin):
    def __init__(self,config):self.config=config
    def _headers(self):
        cookies={'SESSDATA':self.config.get('SESSDATA',''),'bili_jct':self.config.get('BILI_JCT',''),
                 'DedeUserID':self.config.get('DEDE_USER_ID',''),'buvid3':self.config.get('BUVID3',''),'buvid4':self.config.get('BUVID4','')}
        if any(any(c in str(v) for c in '\r\n;') for v in cookies.values()):raise ValueError('invalid_cookie_value')
        return {'Cookie':'; '.join(f'{k}={v}' for k,v in cookies.items() if v),'User-Agent':USER_AGENT,'Referer':'https://www.bilibili.com'}
    async def _request(self,method,url,*,headers=None,params=None,data=None,timeout=20,**ignored):
        host=urlsplit(url).hostname or ''
        trusted={'api.bilibili.com','passport.bilibili.com','api.vc.bilibili.com','message.bilibili.com'}
        cdn=host.endswith('.hdslb.com')
        if urlsplit(url).scheme!='https' or not(host in trusted or (method=='GET' and cdn)):raise ValueError('untrusted_endpoint')
        hdr=(headers or self._headers()) if host in trusted else {'User-Agent':USER_AGENT}
        async with plugin_http_session(self.config) as session:
            async with (session.get if method=='GET' else session.post)(url,headers=hdr,params=params,data=data,timeout=aiohttp.ClientTimeout(total=timeout),allow_redirects=False) as response:
                if response.status!=200:raise RuntimeError(f'http_{response.status}')
                raw=await response.content.read(2_000_001)
                if len(raw)>2_000_000:raise ValueError('response_limit')
                return json.loads(raw),response
    async def _http_get(self,url,**kwargs):return await self._request('GET',url,**kwargs)
    async def _http_post(self,url,**kwargs):return await self._request('POST',url,**kwargs) # no write retries

class Bilibili:
    id='bilibili'
    capabilities=frozenset({'browse','comment','reply','dynamic','owner_share'})
    def __init__(self,secrets,options):self.secrets=secrets;self.options=options;self.clients={};self.qr={}
    def client(self,account):
        if account not in self.clients:
            cfg=CredentialsConfig(self.secrets.read(self.id,account),lambda v:self.secrets.write(self.id,account,v))
            self.clients[account]=Client(cfg)
        return self.clients[account]
    async def status(self,account):
        client=self.client(account)
        if not client.config.get('SESSDATA'):return {'ready':False,'state':'logged_out'}
        raw,_=await client._http_get('https://api.bilibili.com/x/web-interface/nav')
        return {'ready':raw.get('code')==0,'state':'valid' if raw.get('code')==0 else 'invalid'}
    async def request_login(self,account):
        data=await self.client(account).generate_qr();self.qr[account]=data['key'];return {'url':data['url']}
    async def poll_login(self,account):
        key=self.qr[account]
        raw,response=await self.client(account)._http_get('https://passport.bilibili.com/x/passport-login/web/qrcode/poll',params={'qrcode_key':key})
        code=raw.get('data',{}).get('code',-1)
        if code==0:
            client=self.client(account);mapping={'SESSDATA':'SESSDATA','bili_jct':'BILI_JCT','DedeUserID':'DEDE_USER_ID'}
            for cookie,target in mapping.items():
                if cookie in response.cookies:client.config[target]=response.cookies[cookie].value
            if not client.config.get('SESSDATA'):raise ValueError('missing_login_credentials')
            client.config.save_config();self.qr.pop(account,None)
        return {'state':'success' if code==0 else str(code)}
    async def browse(self,account,options):
        client=self.client(account);limit=max(1,min(5,int(options.get('count',2))))
        query=options.get('query','')
        if query:rows=await client.search_bilibili_videos(query,limit)
        else:
            raw,_=await client._http_get('https://api.bilibili.com/x/web-interface/popular',params={'ps':limit,'pn':1})
            if raw.get('code')!=0:raise RuntimeError('feed_unavailable')
            rows=raw.get('data',{}).get('list',[])
        results=[]
        for row in rows[:limit]:
            bv=str(row.get('bvid',''))
            if not re.fullmatch(r'BV[0-9A-Za-z]{10}',bv):continue
            raw,_=await client._http_get('https://api.bilibili.com/x/web-interface/view',params={'bvid':bv})
            if raw.get('code')!=0:continue
            info=raw['data'];text=await client._get_video_subtitles(bv,info.get('cid'))
            mode='subtitle' if text else 'description';text=text or str(info.get('desc',''))
            results.append(Content(self.id,account,bv,f'https://www.bilibili.com/video/{bv}',str(info.get('title','')),text,
                str(info.get('owner',{}).get('mid','')),mode,{'aid':info.get('aid')}))
        return results
    async def execute(self,account,action,params,key):
        client=self.client(account);csrf=client.config.get('BILI_JCT','')
        if action in {'comment','reply'}:
            body={'oid':str(params['oid']),'type':int(params.get('type',1)),'message':str(params['text'])[:1000],'csrf':csrf}
            if action=='reply':body.update({'root':str(params['root']),'parent':str(params['parent'])})
            raw,_=await client._http_post(BILI_REPLY_URL,data=body)
            rid=str((raw.get('data') or {}).get('rpid',''))
        elif action=='dynamic':
            raw,_=await client._http_post(BILI_DYNAMIC_TEXT_URL,data={'type':4,'content':str(params['text'])[:2000],'csrf':csrf,'csrf_token':csrf})
            rid=str((raw.get('data') or {}).get('dynamic_id_str',''))
        else:raise ValueError('unsupported_action')
        if raw.get('code')!=0:return Receipt('failed',code='platform_rejected')
        return Receipt('succeeded',rid) if rid else Receipt('unknown',code='missing_external_id')
    async def close(self):self.clients.clear();self.qr.clear()
