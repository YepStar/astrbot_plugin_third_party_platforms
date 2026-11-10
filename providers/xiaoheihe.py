from dataclasses import asdict
from .xhh_client.api_client import XiaoheiheApiClient,SendUncertainError,CredentialInvalidError
from .xhh_client.models import Credentials,RoutingTarget
from .xhh_client.topic_service import fetch_topic_feed
from .xhh_client.security import clean_untrusted_text
from ..core.models import Content,Receipt

class Xiaoheihe:
    id='xiaoheihe'
    capabilities=frozenset({'browse','comment','reply','owner_share'})
    def __init__(self,secrets,options):self.secrets=secrets;self.options=options;self.clients={};self.qr={}
    def client(self,account):
        if account not in self.clients:
            raw=self.secrets.read(self.id,account)
            credentials=Credentials(**raw) if raw else None
            self.clients[account]=XiaoheiheApiClient(account,credentials=credentials,max_retries=2)
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
        state,_,credentials=await self.client(account).check_qr(self.qr[account])
        if credentials:
            self.secrets.write(self.id,account,asdict(credentials));self.qr.pop(account,None)
        return {'state':str(state)}
    async def browse(self,account,options):
        client=self.client(account);topic=str(options.get('topic_id',''))
        page=await fetch_topic_feed(client,topic) if topic else await client.fetch_feed()
        result=[]
        for row in page.items[:max(1,min(5,int(options.get('count',2))))]:
            pid=str(row.get('link_id',row.get('post_id',row.get('id',''))))
            if not pid.isdigit():continue
            full=await client.fetch_thread_context(pid)
            text=clean_untrusted_text(full.body,max_chars=6000)
            if not text:continue
            result.append(Content(self.id,account,pid,f'https://www.xiaoheihe.cn/app/bbs/link/{pid}',
                clean_untrusted_text(full.title,max_chars=200),text,str(full.author_uid),'text'))
        return result
    async def execute(self,account,action,params,key):
        if action not in {'comment','reply'}:raise ValueError('unsupported_action')
        route=RoutingTarget(account,str(params['post_id']),str(params.get('root','')),str(params.get('parent','')))
        try:result=await self.client(account).send_comment(route,str(params['text'])[:1000])
        except SendUncertainError:return Receipt('unknown',code='send_uncertain')
        return Receipt('succeeded',result.external_comment_id) if result.confirmed else Receipt('unknown',code='not_confirmed')
    async def close(self):
        for client in self.clients.values():await client.close()
        self.clients.clear();self.qr.clear()
