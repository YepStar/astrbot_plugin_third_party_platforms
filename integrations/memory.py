"""Published public facade only; durable outbox when the memory service is unavailable."""
from dataclasses import asdict
import time
from ..core.models import Content,Evaluation

class PublicMemoryGateway:
    SOURCES={'bilibili':'bilibili:public','xiaoheihe':'xiaoheihe:public'}
    def __init__(self,context,enabled=False,*,store=None,clock=time.time):
        self.context,self.enabled,self.store,self.clock=context,enabled,store,clock
    def active(self):return bool(self.enabled() if callable(self.enabled) else self.enabled)
    def facade(self):
        metadata=self.context.get_registered_star('astrbot_plugin_memory_branches')
        if metadata is None or getattr(metadata,'activated',True) is False:return None
        return getattr(getattr(metadata,'star_cls',None),'public_memory',None)
    def _write(self,content,evaluation):
        source=self.SOURCES.get(content.provider)
        if source is None:return 'source_not_configured'
        facade=self.facade()
        if facade is None:return 'unavailable'
        facade.put(source,content.key,evaluation.reason,payload={'provider':content.provider,'account':content.account,
            'external_id':content.external_id,'url':content.url,'evidence':evaluation.evidence,'modality':content.modality})
        return 'saved'
    def put(self,content,evaluation):
        if not self.active():return 'disabled'
        if content.provider not in self.SOURCES:return 'source_not_configured'
        if self.store is not None:
            value=asdict(content);value['text']=evaluation.evidence # Do not replicate the entire source corpus.
            source=self.SOURCES[content.provider];facade=self.facade()
            checkpoint=self.store.setting('memory_checkpoint:'+source)
            if facade is not None and getattr(facade,'integration_api',0)==1:
                try:
                    checkpoint=facade.checkpoint(source)
                    self.store.set_setting('memory_checkpoint:'+source,checkpoint)
                except (PermissionError,ValueError):pass
            self.store.enqueue_memory(content.key,{'content':value,'evaluation':asdict(evaluation),'checkpoint':checkpoint})
            return 'queued'
        return self._write(content,evaluation)
    def recall(self,provider,query):
        if not self.active() or provider not in self.SOURCES:return []
        facade=self.facade()
        if facade is None:return []
        try:rows=facade.search(str(query)[:2000],self.SOURCES[provider],limit=5)
        except (PermissionError,ValueError,RuntimeError):return []
        # Only media-platform public scopes may enter this autonomous public context.
        return [{'scope':r['scope'],'content':str(r.get('content',''))[:1800]} for r in rows[:5]
                if isinstance(r,dict) and r.get('scope') in self.SOURCES.values()]

    def remember_reply(self,event,text):
        if not self.active() or self.store is None or event.stream=='private':return 'disabled_or_private'
        source=self.SOURCES.get(event.provider)
        if source is None:return 'source_not_configured'
        facade=self.facade();checkpoint=self.store.setting('memory_checkpoint:'+source)
        if facade is not None and getattr(facade,'integration_api',0)==1:
            try:
                checkpoint=facade.checkpoint(source)
                self.store.set_setting('memory_checkpoint:'+source,checkpoint)
            except (PermissionError,ValueError):pass
        anchor=str(event.route.get('reply_anchor',event.external_id))
        key=f'interaction:{event.provider}:{event.account}:{anchor}'
        self.store.enqueue_memory(key,{'record':{'scope':source,'content':
            f'Public platform {event.provider}; sender UID {event.actor_id} said: {event.text[:2000]}\nBot replied: {text[:1000]}',
            'payload':{'provider':event.provider,'account':event.account,'external_id':event.external_id,
                'sender_uid':event.actor_id,'route':event.route,'kind':'confirmed_public_reply'}},'checkpoint':checkpoint})
        return 'queued'

    def drain(self):
        if not self.active() or self.store is None:return
        import json
        for row in self.store.pending_memory(self.clock()):
            data=json.loads(row['payload'])
            if 'record' in data:
                record=data['record'];source=record['scope'];key=row['key'];summary=record['content'];payload=record['payload']
                if source not in self.SOURCES.values():
                    self.store.retire_memory(row['key'],'invalid_public_scope');continue
            else:
                content=Content(**data['content']);evaluation=Evaluation(**data['evaluation'])
                source=self.SOURCES[content.provider];key=content.key;summary=evaluation.reason
                payload={'provider':content.provider,'account':content.account,'external_id':content.external_id,
                    'url':content.url,'evidence':evaluation.evidence,'modality':content.modality}
            try:
                facade=self.facade()
                if facade is None or getattr(facade,'integration_api',0)!=1:
                    self.store.finish_memory(row['key'],False,self.clock(),'facade_not_ready');continue
                current=facade.checkpoint(source);checkpoint=data.get('checkpoint')
                self.store.set_setting('memory_checkpoint:'+source,current)
                if checkpoint is None:
                    if current['generation']!=0:
                        self.store.retire_memory(row['key'],'unknown_generation');continue
                    checkpoint=current
                if current!=checkpoint:
                    self.store.retire_memory(row['key'],'generation_changed');continue
                facade.put_checkpointed(source,key,summary,checkpoint,payload=payload)
                self.store.finish_memory(row['key'],True,self.clock(),'saved')
            except ValueError as exc:
                if str(exc)=='integration_generation_changed':self.store.retire_memory(row['key'],'generation_changed')
                else:self.store.finish_memory(row['key'],False,self.clock(),type(exc).__name__)
            except (PermissionError,RuntimeError) as exc:
                self.store.finish_memory(row['key'],False,self.clock(),type(exc).__name__)
