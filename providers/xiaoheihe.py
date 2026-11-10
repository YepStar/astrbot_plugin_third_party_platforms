from dataclasses import asdict
import time
from .xhh_client.api_client import XiaoheiheApiClient,SendUncertainError,CredentialInvalidError
from .xhh_client.models import Credentials,RoutingTarget
from .xhh_client.topic_service import fetch_topic_feed
from .xhh_client.security import clean_untrusted_text
from ..core.models import Content,Receipt,Incoming
from .xhh_client.models import NotificationType,Notification
from .xhh_client.context_builder import ContextBuilder
import json

class Xiaoheihe:
    id='xiaoheihe'
    capabilities=frozenset({'search','browse','comment','reply','owner_share'})
    def __init__(self,secrets,options):self.secrets=secrets;self.options=options;self.clients={};self.qr={};self.context_builder=ContextBuilder()
    def client(self,account):
        if account not in self.clients:
            raw=self.secrets.read(self.id,account)
            if raw and raw.get('profile_id')!=account:raise ValueError('credential_account_mismatch')
            credentials=Credentials(**raw) if raw else None
            network=self.options.get('platforms',{}).get(self.id,{}).get('accounts',{}).get(account,{}).get('network',{})
            self.clients[account]=XiaoheiheApiClient(account,credentials=credentials,max_retries=2,**{k:network[k] for k in ['request_timeout_seconds','connect_timeout_seconds','read_timeout_seconds','min_request_interval_seconds'] if k in network})
        return self.clients[account]
    async def status(self,account):
        client=self.client(account)
        if not client.credentials:return {'ready':False,'state':'logged_out'}
        try:await client.check_credentials()
        except CredentialInvalidError:return {'ready':False,'state':'invalid'}
        return {'ready':True,'state':'valid'}
    async def request_login(self,account):
        session=await self.client(account).request_qr();self.qr[account]=session
        return {'url':session.qr_content,'expires_at':session.expires_at}
    async def poll_login(self,account):
        session=self.qr[account]
        if session.expires_at<=time.time():
            self.qr.pop(account,None);raise ValueError('qr_expired')
        state,_,credentials=await self.client(account).check_qr(session)
        if credentials:
            self.secrets.write(self.id,account,asdict(credentials));self.qr.pop(account,None)
        return {'state':str(state)}
    async def browse(self,account,options):
        client=self.client(account);topic=str(options.get('topic_id',''))
        topics=options.get('topic_ids',[])
        if not topic and topics:
            import hashlib
            index=int(hashlib.sha256(str(options.get('_session_id','')).encode()).hexdigest()[:8],16)%len(topics)
            topic=str(topics[index])
        if options.get('query'):
            result=await self.search(account,options['query'],max(1,min(3,int(options.get('count',2)))))
            return [Content(self.id,account,row['url'].rsplit('/',1)[-1],row['url'],row['title'],row.get('body_excerpt',''),str(row.get('author_id','')),'text') for row in result['items'] if row['url'].rsplit('/',1)[-1] not in options.get('_skip_ids',[])]
        page=await fetch_topic_feed(client,topic) if topic else await client.fetch_feed()
        result=[]
        limit=max(1,min(5,int(options.get('count',2))))
        for row in page.items[:min(15,limit*3)]:
            pid=str(row.get('link_id',row.get('post_id',row.get('id',''))))
            if not pid.isdigit() or pid in options.get('_skip_ids',[]):continue
            full=await client.fetch_thread_context(pid)
            text=clean_untrusted_text(full.body,max_chars=6000)
            if len(text.strip())<30:continue
            result.append(Content(self.id,account,pid,f'https://www.xiaoheihe.cn/app/bbs/link/{pid}',
                clean_untrusted_text(full.title,max_chars=200),text,str(full.author_uid),'text'))
            if len(result)>=limit:break
        return result
    async def search(self,account,query,limit=2):
        from .xhh_client.endpoints import EndpointName
        from ..core.research import public_query
        client=self.client(account);query=public_query(query)
        response=await client._request(EndpointName.SEARCH,params={'q':query,'search_type':'link','offset':0,'limit':max(10,limit*3),'is_pull_down':0,'dw':628})
        body=response.payload.get('result',{});rows=body.get('items',[]) if isinstance(body,dict) else []
        result=[];seen=set()
        for wrapper in rows:
            if not isinstance(wrapper,dict):continue
            row=wrapper.get('info',wrapper)
            if not isinstance(row,dict):continue
            pid=str(row.get('linkid',row.get('link_id','')))
            if not pid.isdigit() or pid in seen:continue
            seen.add(pid);full=await client.fetch_thread_context(pid)
            text=clean_untrusted_text(full.body,max_chars=2200)
            result.append({'title':clean_untrusted_text(full.title,max_chars=180),
                'url':f'https://www.xiaoheihe.cn/app/bbs/link/{pid}','body_excerpt':text,'author_id':str(full.author_uid),
                'evidence':'post_body_excerpt' if text else 'search_metadata',
                'sample_comments':[clean_untrusted_text(str(x.get('text',x.get('content',''))),max_chars=160) for x in full.comments[:3] if isinstance(x,dict)]})
            if len(result)>=limit:break
        return {'platform':self.id,'status':'ok' if result else 'no_results','items':result}

    async def execute(self,account,action,params,key):
        if action not in {'comment','reply'}:raise ValueError('unsupported_action')
        route=RoutingTarget(account,str(params['post_id']),str(params.get('root','')),str(params.get('parent','')))
        try:result=await self.client(account).send_comment(route,str(params['text'])[:1000])
        except SendUncertainError:return Receipt('unknown',code='send_uncertain')
        return Receipt('succeeded',result.external_comment_id) if result.confirmed else Receipt('unknown',code='not_confirmed')
    async def poll_events(self,account,cursor):
        client=self.client(account)
        cfg=self.options.get('platforms',{}).get(self.id,{}).get('accounts',{}).get(account,{})
        if not cfg.get('actions',{}).get('reply'):return []
        streams=[]
        for kind in (NotificationType.MENTION,NotificationType.REPLY):
            if not cfg.get('reply',{}).get('poll_mentions' if kind is NotificationType.MENTION else 'poll_replies',True):continue
            stream=kind.value;previous=cursor(stream);events=[];page_cursor=''
            for page_number in range(1,4):
                page=await client.fetch_notifications(kind,cursor=page_cursor,page=page_number,page_size=20)
                boundary=False
                for wrapper in page.items:
                    n=wrapper['notification']
                    if previous and n.external_event_id==previous.get('latest'):boundary=True;break
                    if client.credentials and n.sender_uid==client.credentials.uid:continue
                    if not n.external_comment_id or not n.post_id:continue
                    route={'post_id':n.post_id,'root':n.root_comment_id or n.external_comment_id,
                        'parent':n.external_comment_id,'reply_anchor':n.external_comment_id}
                    events.append(Incoming(self.id,account,stream,n.external_event_id,n.sender_uid,n.content,n.created_at,
                        route,n.sender_uid_verified,n.explicit_wake,n.post_author_uid,context={
                            'sender_name':n.sender_nickname[:80],'image_urls':n.image_urls[:6],
                            'root':n.root_comment_id,'parent':n.parent_comment_id,'observed_at':n.observed_at,
                            'raw':n.raw if len(json.dumps(n.raw,ensure_ascii=False))<=64000 else {}}))
                if boundary or not page.has_more:break
                page_cursor=page.next_cursor
            latest=events[0].external_id if events else (previous or {}).get('latest','')
            streams.append((stream,events,{'latest':latest}))
        return streams

    async def reply_context(self,event):
        details=event.context
        notification=Notification(profile_id=event.account,external_event_id=event.external_id,
            external_comment_id=str(event.route['parent']),notification_id=event.external_id,
            event_type=NotificationType(event.stream),sender_uid=event.actor_id,
            sender_nickname=details.get('sender_name',''),post_id=str(event.route['post_id']),
            root_comment_id=details.get('root',''),parent_comment_id=details.get('parent',''),
            content=event.text,created_at=event.created,observed_at=details.get('observed_at',0),
            post_author_uid=event.author_id,explicit_wake=event.explicit,
            image_urls=details.get('image_urls',[]),raw=details.get('raw',{}))
        built=await self.context_builder.build(notification,self.client(event.account))
        return {'text':built.dynamic_context,'images':built.image_urls,
            'image_attributions':[asdict(item) for item in built.image_attributions],
            'warnings':built.warnings,'reply_target':built.reply_target_comment_id}

    async def close(self):
        await self.context_builder.clear()
        for client in self.clients.values():await client.close()
        self.clients.clear();self.qr.clear()
