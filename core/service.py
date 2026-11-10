import hashlib
import time
from datetime import datetime
from zoneinfo import ZoneInfo
from .models import Receipt

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
        try:
            rows=await provider.browse(account,task['params'])
            self.store.finish_action(key,Receipt('succeeded'))
        except BaseException:
            self.store.finish_action(key,Receipt('failed',code='browse_failed'));raise
        for content in rows:
            if self.clock()>=task['end']:break
            self.executor.policy.permit(provider.id,account,'browse')
            try:evaluation=await self.reader.evaluate(content)
            except ValueError:continue
            hour=datetime.fromtimestamp(self.clock(),ZoneInfo(self.executor.policy.config.get('timezone','Asia/Shanghai'))).hour
            self.store.observe(content,evaluation,hour,self.clock())
            try:memory_state=self.memory.put(content,evaluation)
            except (PermissionError,RuntimeError):memory_state='unavailable'
            self.store.set_setting('last_read',{'provider':provider.id,'external_id':content.external_id,'score':evaluation.score,'memory':memory_state})
            try:item=self.executor.policy.permit(provider.id,account,'owner_share',evaluation)
            except PermissionError:continue
            text=await self.reader.share_text(content,evaluation)
            recipient=item['owner_umo']
            delivery=hashlib.sha256(f'{content.provider}|{content.external_id}|{recipient}'.encode()).hexdigest()
            async def send():
                await self.deliver(recipient,text)
                return Receipt('succeeded')
            await self.executor.execute(provider.id,account,'owner_share',{},'owner_share:'+delivery,evaluation=evaluation,operation=send)
