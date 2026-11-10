"""Optional facade consumer. No private music internals or synthetic user events."""
from ..core.models import Receipt

class Music:
    id='netease'
    capabilities=frozenset({'listen'})
    owner='astrbot_plugin_third_party_platforms'
    def __init__(self,context):self.context=context;self.owned=False;self.publication_gate=None
    def facade(self):
        star=self.context.get_registered_star('astrbot_plugin_netease_browser')
        if star is None or getattr(star,'activated',True) is False:raise RuntimeError('music_unavailable')
        instance=getattr(star,'star_cls',None)
        if getattr(instance,'third_party_scheduler_api',0)!=1:raise RuntimeError('music_scheduler_facade_required')
        return instance
    async def status(self,account):
        try:return await self.facade().third_party_scheduler_status()
        except RuntimeError:return {'ready':False,'state':'facade_unavailable'}
    async def acquire(self):
        self.owned=await self.facade().third_party_scheduler_acquire(self.owner,90)
        return self.owned
    async def execute(self,account,action,params,key):
        if action!='listen':raise ValueError('unsupported_action')
        if not await self.acquire():return Receipt('failed',code='scheduler_owned_elsewhere')
        facade=self.facade()
        if self.publication_gate is not None:
            if getattr(facade,'third_party_scheduler_filter_api',0)!=1:return Receipt('failed',code='music_publication_filter_required')
            result=await facade.third_party_scheduler_run(self.owner,key,publication_gate=self.publication_gate)
        else:result=await facade.third_party_scheduler_run(self.owner,key)
        return Receipt(result['state'],code=result.get('code',''))
    async def close(self):
        if self.owned:
            try:await self.facade().third_party_scheduler_release(self.owner)
            except RuntimeError:pass
        self.owned=False
