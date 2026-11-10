import time
from datetime import datetime
from zoneinfo import ZoneInfo
from .models import Receipt
from .sharing import share

class BrowsingService:
    def __init__(self,store,registry,executor,reader,memory,deliver,*,clock=time.time):
        self.store,self.registry,self.executor,self.reader,self.memory,self.deliver=store,registry,executor,reader,memory,deliver
        self.clock=clock
    async def browse(self,task):
        provider=self.registry.get(task['provider'],'browse');account=task['account']
        self.executor.policy.permit(provider.id,account,'browse')
        # Consume a session quota before fetching. Failure stays accounted to avoid hot error loops.
        key='browse:'+task['id']
        if not self.store.claim_action(key,provider.id,account,'browse',self.executor.policy.limits(provider.id,account,'browse',self.clock()),self.clock()):return
        self.store.set_setting(f'activity:{provider.id}:{account}',{'task_id':task['id'],'phase':'reading','updated_at':self.clock()})
        try:
            rows=await provider.browse(account,{**task['params'],'_session_id':task['id'],'_skip_ids':self.store.observed_ids(provider.id,account,self.clock()-86400)})
            self.store.finish_action(key,Receipt('succeeded'))
        except BaseException:
            self.store.finish_action(key,Receipt('failed',code='browse_failed'));raise
        for index,content in enumerate(rows):
            self.store.set_setting(f'activity:{provider.id}:{account}',{'task_id':task['id'],'phase':'evaluating','item':index+1,'total':len(rows),'title':content.title[:120],'updated_at':self.clock()})
            if self.clock()>=task['end']:break
            self.executor.policy.permit(provider.id,account,'browse')
            self.store.mark_read(content.provider,content.account,content.external_id,self.clock())
            try:evaluation=await self.reader.evaluate(content)
            except ValueError:continue
            hour=datetime.fromtimestamp(self.clock(),ZoneInfo(self.executor.policy.config.get('timezone','Asia/Shanghai'))).hour
            self.store.observe(content,evaluation,hour,self.clock())
            try:memory_state=self.memory.put(content,evaluation)
            except (PermissionError,RuntimeError):memory_state='unavailable'
            self.store.set_setting('last_read',{'provider':provider.id,'external_id':content.external_id,'score':evaluation.score,'memory':memory_state})
            if self.clock()>=task['end']:break
            try:self.executor.policy.permit(provider.id,account,'comment',evaluation)
            except PermissionError:pass
            else:
                self.store.set_setting(f'activity:{provider.id}:{account}',{'task_id':task['id'],'phase':'commenting','item':index+1,'total':len(rows),'updated_at':self.clock()})
                text=await self.reader.comment_text(content,evaluation)
                if text and self.clock()<task['end']:
                    params={'text':text}
                    if provider.id=='bilibili':params['oid']=content.metadata['aid']
                    else:params['post_id']=content.external_id
                    await self.executor.execute(provider.id,account,'comment',params,'comment:'+content.key,evaluation=evaluation)
            if self.clock()>=task['end']:break
            try:item=self.executor.policy.permit(provider.id,account,'owner_share',evaluation)
            except PermissionError:continue
            self.store.set_setting(f'activity:{provider.id}:{account}',{'task_id':task['id'],'phase':'sharing','item':index+1,'total':len(rows),'updated_at':self.clock()})
            text=await self.reader.share_text(content,evaluation)
            if self.clock()>=task['end']:break
            await share(self,content,evaluation,text,item)
        self.store.set_setting(f'activity:{provider.id}:{account}',{'task_id':task['id'],'phase':'finished','updated_at':self.clock()})
