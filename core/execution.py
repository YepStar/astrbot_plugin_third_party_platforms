import asyncio
import time
from .models import Receipt
from .store import BudgetExceeded

class Executor:
    def __init__(self,store,registry,policy,*,clock=time.time,timeout=45):
        self.store,self.registry,self.policy=store,registry,policy
        self.clock,self.timeout=clock,timeout
        self.locks={}
    async def execute(self,provider,account,action,params,key,*,evaluation=None,operation=None):
        lock=self.locks.setdefault((provider,account),asyncio.Lock())
        async with lock:
            self.policy.permit(provider,account,action,evaluation)
            adapter=self.registry.get(provider,action if operation is None else None)
            if not self.store.claim_action(key,provider,account,action,self.policy.limits(provider,account,action,self.clock()),self.clock()):
                return None # Existing claim/unknown/success: NEVER send it again.
            try:
                # Re-evaluate configuration at the actual external-action boundary.
                self.policy.permit(provider,account,action,evaluation)
                result=await asyncio.wait_for(operation() if operation else adapter.execute(account,action,params,key),self.timeout)
                if not isinstance(result,Receipt):raise TypeError('invalid_provider_receipt')
            except asyncio.CancelledError:
                self.store.finish_action(key,Receipt('unknown',code='cancelled_during_io'));raise
            except Exception as exc:
                result=Receipt('unknown',code=type(exc).__name__)
            self.store.finish_action(key,result)
            return result

class Scheduler:
    def __init__(self,store,registry,executor,handlers,*,clock=time.time,concurrency=2):
        if concurrency<1:raise ValueError('invalid_concurrency')
        self.store,self.registry,self.executor,self.handlers=store,registry,executor,handlers
        self.clock=clock;self.running={};self.closed=False;self.concurrency=concurrency
    async def tick(self):
        now=self.clock();self.store.expire(now)
        for task in self.store.tasks(now-86400,now+1):
            if self.closed or len(self.running)>=self.concurrency:break
            if task['state']!='planned' or not task['start']<=now<task['end']:continue
            if any((r['provider'],r['account'])==(task['provider'],task['account']) for r,_ in self.running.values()):continue
            try:
                self.executor.policy.permit(task['provider'],task['account'],task['action'])
                self.registry.get(task['provider'],task['action'])
            except (PermissionError,KeyError,ValueError):continue
            if not self.store.claim_task(task['id'],now):continue
            future=asyncio.create_task(self._run(task));self.running[task['id']]=(task,future)
    async def _run(self,task):
        state='failed'
        try:
            handler=self.handlers[task['action']]
            await handler(task);state='succeeded'
        except asyncio.CancelledError:state='unknown';raise
        except Exception:state='failed'
        finally:
            self.store.finish_task(task['id'],state);self.running.pop(task['id'],None)
    async def close(self):
        self.closed=True
        tasks=[future for _,future in list(self.running.values())]
        for future in tasks:future.cancel()
        await asyncio.gather(*tasks,return_exceptions=True)
