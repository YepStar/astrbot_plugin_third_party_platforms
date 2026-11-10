"""Bili HTTP extraction. No old Star, scheduler, memory store or private configuration."""
import asyncio
import json
import re
from urllib.parse import urlsplit
import aiohttp
from .bili_client.bilibili import BilibiliAPIMixin
from .bili_client.network import plugin_http_session
from .bili_client.config import USER_AGENT, BILI_REPLY_URL, BILI_DYNAMIC_TEXT_URL
from ..core.models import Content,Receipt,Incoming
import time
import uuid
import hashlib
from .bili_client.discovery import BiliDiscovery
from .bili_client.media import FrameSource
from ..core.media import describe_frames

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
        parsed=urlsplit(url);host=parsed.hostname or ''
        if parsed.username or parsed.password or parsed.port not in (None,443):raise ValueError('invalid_endpoint_authority')
        trusted={'api.bilibili.com','passport.bilibili.com','api.vc.bilibili.com','message.bilibili.com'}
        cdn=host.endswith('.hdslb.com')
        if urlsplit(url).scheme!='https' or not(host in trusted or (method=='GET' and cdn)):raise ValueError('untrusted_endpoint')
        hdr=(headers or self._headers()) if host in trusted else {'User-Agent':USER_AGENT}
        async with plugin_http_session(self.config) as session:
            async with (session.get if method=='GET' else session.post)(url,headers=hdr,params=params,data=data,timeout=aiohttp.ClientTimeout(total=timeout),allow_redirects=False) as response:
                if response.status!=200:raise RuntimeError(f'http_{response.status}')
                chunks=[];size=0
                async for chunk in response.content.iter_chunked(65536):
                    size+=len(chunk)
                    if size>2_000_000:raise ValueError('response_limit')
                    chunks.append(chunk)
                raw=b''.join(chunks)
                return json.loads(raw),response
    async def _http_get(self,url,**kwargs):return await self._request('GET',url,**kwargs)
    async def _http_post(self,url,**kwargs):return await self._request('POST',url,**kwargs) # no write retries

class PoolClient(BiliDiscovery):
    def __init__(self,client,pools):
        self.config={'PROACTIVE_VIDEO_POOLS':pools}
        self._http_get=client._http_get

class Bilibili:
    id='bilibili'
    capabilities=frozenset({'search','browse','comment','reply','dynamic','owner_share','private_reply'})
    def __init__(self,secrets,options,*,generate=None,cache_root=None):
        self.secrets=secrets;self.options=options;self.clients={};self.qr={}
        self.generate=generate;self.cache_root=cache_root or secrets.root.parent/'media_tmp';self.last_visual={};self.visual_cache={}
    def client(self,account):
        if account not in self.clients:
            cfg=CredentialsConfig(self.secrets.read(self.id,account),lambda v:self.secrets.write(self.id,account,v))
            self.clients[account]=Client(cfg)
        return self.clients[account]
    async def status(self,account):
        client=self.client(account)
        if not client.config.get('SESSDATA'):return {'ready':False,'state':'logged_out'}
        raw,_=await client._http_get('https://api.bilibili.com/x/web-interface/nav')
        code=raw.get('code')
        if code==0:return {'ready':True,'state':'valid'}
        if code in {-101,-111}:return {'ready':False,'state':'invalid'}
        return {'ready':None,'state':'unreachable'}
    async def request_login(self,account):
        data=await self.client(account).generate_qr();self.qr[account]={'key':data['key'],'expires_at':time.time()+180};return {'url':data['url'],'expires_at':self.qr[account]['expires_at']}
    async def poll_login(self,account):
        session=self.qr[account]
        if session['expires_at']<=time.time():
            self.qr.pop(account,None);raise ValueError('qr_expired')
        key=session['key']
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
        rows=[];follow=[]
        uids=options.get('follow_uids',[])
        if options.get('special_follow_enabled'):
            for mid in uids[:5]:
                if not str(mid).isdigit():continue
                latest=await client._get_up_latest_video(mid)
                if latest:follow.append(latest)
        if query:rows=await client.search_bilibili_videos(query,limit*2)
        else:
            pools=options.get('pools',['popular'])
            if not isinstance(pools,list) or not 1<=len(pools)<=8:raise ValueError('invalid_video_pools')
            pool=PoolClient(client,pools)
            for value in pools:
                if pool._resolve_video_pool_spec(value)[0] not in {'popular','rcmd','weekly','precious','ranking','newlist'}:raise ValueError('unknown_video_pool')
            rows=await pool._get_pool_videos()
            seed=str(options.get('_session_id',''))
            rows=sorted(rows,key=lambda x:hashlib.sha256((seed+str(x.get('bvid',''))).encode()).hexdigest())
        rows=follow+rows
        skipped=set(options.get('_skip_ids',[]));seen=set();candidates=[]
        for row in rows:
            bv=str(row.get('bvid',''))
            if not bv or bv in seen or bv in skipped:continue
            seen.add(bv);candidates.append(row)
            if len(candidates)>=limit:break
        results=[]
        for row in candidates:
            bv=str(row.get('bvid',''))
            if not re.fullmatch(r'BV[0-9A-Za-z]{10}',bv):continue
            raw,_=await client._http_get('https://api.bilibili.com/x/web-interface/view',params={'bvid':bv})
            if raw.get('code')!=0:continue
            info=raw['data'];text=await client._get_video_subtitles(bv,info.get('cid'))
            visual=await self.visual(account,info,text)
            mode='subtitle' if text else 'description';text=text or str(info.get('desc',''))
            if visual:
                text=text[:9000]+'\n'+visual['text'];mode='subtitle_and_sparse_frames' if mode=='subtitle' else 'sparse_frames'
            results.append(Content(self.id,account,bv,f'https://www.bilibili.com/video/{bv}',str(info.get('title','')),text,
                str(info.get('owner',{}).get('mid','')),mode,{'aid':info.get('aid')}))
        return results
    async def visual(self,account,info,subtitles=''):
        policy=self.options.get('vision_policy','when_text_insufficient')
        if policy not in {'off','when_text_insufficient','always'}:raise ValueError('invalid_vision_policy')
        if policy=='off' or (policy=='when_text_insufficient' and len(subtitles.strip())>=40):return None
        if self.generate is None:
            self.last_visual={'state':'unavailable','code':'vision_generator_unconfigured'};return None
        bvid=info.get('bvid','');key=(account,bvid,str(self.options.get('model_ids',{}).get('video_frames','')),self.options.get('vision_frame_count',5))
        cached=self.visual_cache.get(key)
        if cached and cached[0]>time.time():return cached[1]
        try:
            async with asyncio.timeout(240):
                source=FrameSource(self.cache_root,self.client(account).config,self.options)
                async with source.capture(bvid) as frames:
                    result=await describe_frames(self.generate,frames,{'provider':self.id,'external_id':bvid,
                        'title':str(info.get('title',''))[:300],'description':str(info.get('desc',''))[:800]})
            if len(self.visual_cache)>=50:self.visual_cache.pop(next(iter(self.visual_cache)))
            self.visual_cache[key]=(time.time()+3600,result)
            self.last_visual={'state':'observed','external_id':bvid,'frames':result['observed_frames'],'sample_seconds':result['sample_seconds']}
            return result
        except Exception as exc:
            self.last_visual={'state':'unavailable','external_id':bvid,'code':type(exc).__name__}
            return None

    async def search(self,account,query,limit=2):
        from ..core.research import public_query
        rows=await self.browse(account,{'query':public_query(query),'count':max(1,min(3,int(limit)))})
        items=[]
        for row in rows:
            item={'title':row.title,'url':row.url,'description':row.text[:2200],
                'evidence':'subtitle_excerpt' if row.modality=='subtitle' else 'description_only'}
            if row.modality=='subtitle':item['subtitle_excerpt']=item.pop('description')
            aid=row.metadata.get('aid')
            if aid:item['sample_comments']=await self.client(account)._get_hot_comments(aid,limit=3)
            items.append(item)
        return {'platform':self.id,'status':'ok' if items else 'no_results','items':items}

    async def execute(self,account,action,params,key):
        client=self.client(account);csrf=client.config.get('BILI_JCT','')
        if action in {'comment','reply'}:
            body={'oid':str(params['oid']),'type':int(params.get('type',1)),'message':str(params['text'])[:1000],'csrf':csrf}
            if params.get('at_name_to_mid'):body['at_name_to_mid']=json.dumps(params['at_name_to_mid'],ensure_ascii=False)
            if action=='reply':body.update({'root':str(params['root']),'parent':str(params['parent'])})
            raw,_=await client._http_post(BILI_REPLY_URL,data=body)
            rid=str((raw.get('data') or {}).get('rpid',''))
        elif action=='private_reply':
            sender=str(client.config.get('DEDE_USER_ID',''));receiver=str(params['receiver'])
            if not sender.isdigit() or not receiver.isdigit() or sender==receiver or not csrf:
                return Receipt('failed',code='invalid_private_route')
            body={'msg[sender_uid]':sender,'msg[receiver_id]':receiver,'msg[receiver_type]':1,
                'msg[msg_type]':1,'msg[msg_status]':0,'msg[dev_id]':str(uuid.uuid4()).upper(),
                'msg[timestamp]':int(time.time()),'msg[new_face_version]':0,
                'msg[content]':json.dumps({'content':str(params['text'])[:1000]},ensure_ascii=False),
                'csrf':csrf,'csrf_token':csrf,'from_firework':0,'build':0,'mobi_app':'web'}
            raw,_=await client._http_post('https://api.vc.bilibili.com/web_im/v1/web_im/send_msg',data=body)
            rid=str((raw.get('data') or {}).get('msg_key',''))
        elif action=='dynamic':
            raw,_=await client._http_post(BILI_DYNAMIC_TEXT_URL,data={'type':4,'content':str(params['text'])[:2000],'csrf':csrf,'csrf_token':csrf})
            rid=str((raw.get('data') or {}).get('dynamic_id_str',''))
        else:raise ValueError('unsupported_action')
        if raw.get('code')!=0:return Receipt('failed',code='platform_rejected')
        return Receipt('succeeded',rid) if rid else Receipt('unknown',code='missing_external_id')
    async def poll_events(self,account,cursor):
        client=self.client(account);self_uid=str(client.config.get('DEDE_USER_ID',''))
        cfg=self.options.get('platforms',{}).get(self.id,{}).get('accounts',{}).get(account,{})
        actions=cfg.get('actions',{});streams=[]
        if actions.get('reply'):
            for stream,endpoint in [('reply','reply'),('mention','at')]:
                previous=cursor(stream);events=[];head=None
                for page in range(1,4):
                    raw,_=await client._http_get('https://api.bilibili.com/x/msgfeed/'+endpoint,params={'ps':20,'pn':page})
                    if raw.get('code')!=0:raise RuntimeError('notification_unavailable')
                    rows=raw.get('data',{}).get('items',[]);boundary=False
                    for row in rows:
                        item=row.get('item',{});rpid=str(item.get('source_id',''));actor=str(row.get('user',{}).get('mid',''))
                        if rpid and head is None:head=rpid
                        if not rpid or not actor.isdigit() or actor==self_uid:continue
                        if previous and rpid==previous.get('latest'):boundary=True;break
                        route={'oid':str(item.get('subject_id','')),'type':int(item.get('business_id',1)),
                            'root':str(item.get('root_id') or rpid),'parent':rpid,'reply_anchor':rpid}
                        created=float(row.get('reply_time') or row.get('at_time') or row.get('time') or 0)
                        if previous and created<float(previous.get('started_at',0)):continue
                        events.append(Incoming(self.id,account,stream,rpid,actor,str(item.get('source_content','')),created,route,True,True))
                    if boundary or len(rows)<20:break
                latest=head or (previous or {}).get('latest','')
                streams.append((stream,events,{**(previous or {}),'latest':latest}))
        if actions.get('private_reply'):
            previous=cursor('private');sequences=dict((previous or {}).get('sessions',{}));events=[]
            raw,_=await client._http_get('https://api.vc.bilibili.com/session_svr/v1/session_svr/get_sessions',params={'session_type':1,'group_fold':1,'unfollow_fold':0,'sort_rule':2,'size':100,'build':0,'mobi_app':'web'})
            if raw.get('code')!=0:raise RuntimeError('private_sessions_unavailable')
            for session in raw.get('data',{}).get('session_list',[]):
                talker=str(session.get('talker_id',''));kind=int(session.get('session_type',1));maximum=int(session.get('max_seqno') or 0)
                if not talker.isdigit() or kind!=1:continue
                if previous is None:
                    sequences[talker]=maximum;continue # First account observation: skip historical conversations.
                old=int(sequences.get(talker,0));sequences.setdefault(talker,0)
                if maximum<=old:continue
                page,_=await client._http_get('https://api.vc.bilibili.com/svr_sync/v1/svr_sync/fetch_session_msgs',params={'talker_id':talker,'session_type':1,'begin_seqno':old,'size':20,'sender_device_id':1,'build':0,'mobi_app':'web'})
                if page.get('code')!=0:raise RuntimeError('private_messages_unavailable')
                for item in reversed(page.get('data',{}).get('messages',[])):
                    seq=int(item.get('msg_seqno') or 0);actor=str(item.get('sender_uid',''))
                    sequences[talker]=max(int(sequences[talker]),seq)
                    if seq<=old or actor!=talker or actor==self_uid or int(item.get('msg_type',0))!=1:continue
                    body=item.get('content','')
                    if isinstance(body,str):
                        try:body=json.loads(body)
                        except ValueError:continue
                    if not isinstance(body,dict) or not isinstance(body.get('content'),str):continue
                    event_id=talker+':'+str(item.get('msg_key') or seq)
                    created=float(item.get('timestamp') or 0)
                    if created>10_000_000_000:created/=1000
                    if created<float((previous or {}).get('started_at',0)):continue
                    events.append(Incoming(self.id,account,'private',event_id,actor,body['content'],created,
                        {'receiver':talker,'reply_anchor':event_id},True,context={'legacy_event_id':str(item.get('msg_key') or seq)}))
            streams.append(('private',events,{'sessions':sequences,'started_at':(previous or {}).get('started_at',time.time())}))
        return streams

    async def reply_context(self,event):
        if event.stream=='private':return {'text':'Private direct message; no public thread was attached.','images':[]}
        route=event.route
        if int(route.get('type',1))!=1:return {'text':event.source_text,'images':[],'warnings':['Non-video notification: video context is unavailable.']}
        oid=str(route.get('oid',''))
        if not oid.isdigit():raise ValueError('invalid_context_video')
        client=self.client(event.account);info=await client._get_video_info(oid)
        if not info:raise RuntimeError('reply_source_unavailable')
        subtitles=await client._get_video_subtitles(info.get('bvid',''),info.get('cid',0))
        comments=await client._get_hot_comments(oid,limit=5)
        visual=await self.visual(event.account,info,subtitles)
        return {'text':json.dumps({'source_kind':('subtitle_and_sparse_frames' if subtitles else 'sparse_frames') if visual else ('video_subtitles_and_description' if subtitles else 'video_description_only'),
            'video_author':{'uid':str(info.get('owner_mid','')),'name':info.get('owner_name','')},
            'title':info.get('title',''),'description':str(info.get('desc',''))[:3000],
            'subtitles':str(subtitles)[:8000],'visual_observations':visual['text'] if visual else '', 'other_commenters':comments,
            'trigger_comment_id':route.get('parent',''),'root_comment_id':route.get('root',''),
            'identity_rule':'The video author, trigger sender and other commenters are separate people. Refer only to the supplied subtitle/description and explicitly sampled frames if present. No audio or continuous viewing may be claimed.'},ensure_ascii=False),
            'images':[],'warnings':[] if subtitles else ['No subtitles available; use description evidence only.']}

    async def close(self):self.clients.clear();self.qr.clear();self.visual_cache.clear()
