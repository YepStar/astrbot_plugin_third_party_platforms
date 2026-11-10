"""Use a loaded public memory facade only. Never open another plugin's database."""
from dataclasses import asdict

class PublicMemoryGateway:
    SOURCES={'bilibili':'bilibili:public','xiaoheihe':'xiaoheihe:public'}
    def __init__(self,context,enabled=False):self.context,self.enabled=context,enabled
    def put(self,content,evaluation):
        if not self.enabled:return 'disabled'
        source=self.SOURCES.get(content.provider)
        if source is None:return 'source_not_configured'
        metadata=self.context.get_registered_star('astrbot_plugin_memory_branches')
        if metadata is None or getattr(metadata,'activated',True) is False:return 'unavailable'
        instance=getattr(metadata,'star_cls',None);facade=getattr(instance,'public_memory',None)
        if facade is None:return 'not_ready'
        # Published facade enforces route/bank membership; never infer a private bank.
        facade.put(source,content.key,evaluation.reason,payload={'provider':content.provider,'account':content.account,
            'external_id':content.external_id,'url':content.url,'evidence':evaluation.evidence,'modality':content.modality})
        return 'saved'
