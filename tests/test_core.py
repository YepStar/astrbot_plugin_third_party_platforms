import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import date,datetime
from pathlib import Path
import importlib
import sys
from types import SimpleNamespace
from zoneinfo import ZoneInfo
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
package=Path(__file__).resolve().parents[1].name
Store=importlib.import_module(package+'.core.store').Store
Conflict=importlib.import_module(package+'.core.store').Conflict
BudgetExceeded=importlib.import_module(package+'.core.store').BudgetExceeded
models=importlib.import_module(package+'.core.models')
planning=importlib.import_module(package+'.core.planning')
execution=importlib.import_module(package+'.core.execution')
Policy=importlib.import_module(package+'.core.policy').Policy

def test_task_cas_restart_and_no_replay(tmp_path):
    store=Store(tmp_path/'test.db');key=store.create_task('p','a','browse',100,200)
    store.change_task(key,1,start=110)
    with pytest.raises(Conflict):store.change_task(key,1,start=120)
    assert not store.claim_task(key,109)
    assert store.claim_task(key,120)
    assert not store.claim_task(key,120)
    Store(tmp_path/'test.db').recover()
    assert store.tasks()[0]['state']=='unknown'
    assert not store.claim_task(key,130)

def test_atomic_last_budget_slot_and_unknown(tmp_path):
    store=Store(tmp_path/'test.db')
    def reserve(i):
        try:return store.claim_action(str(i),'p','a','comment',[('global','today',1)],0)
        except BudgetExceeded:return False
    assert sum(ThreadPoolExecutor(8).map(reserve,range(16)))==1
    row=store.actions()[0];store.recover()
    assert store.actions()[0]['state']=='unknown'
    assert not store.claim_action(row['key'],'p','a','comment',[],1)
    with pytest.raises(BudgetExceeded):store.claim_action('new','p','a','comment',[('global','today',1)],1)

def test_confirmed_failure_releases_reservation(tmp_path):
    store=Store(tmp_path/'test.db');limits=[('all','today',1)]
    assert store.claim_action('a','p','a','comment',limits)
    store.finish_action('a',models.Receipt('failed'))
    assert store.claim_action('b','p','a','comment',limits)

def test_windows_overlap_midnight_timezone():
    day=date(2026,11,10)
    a,b=planning.window_for(day,'23:30-01:30')
    assert b-a==7200
    assert datetime.fromtimestamp(b,ZoneInfo('Asia/Shanghai')).day==11
    c,d=planning.window_for(day,'23:45-00:30');assert a<c<d<b
    with pytest.raises(ValueError):planning.window_for(day,'25:00-01:00')

def test_manual_cancel_survives_plan_regeneration(tmp_path):
    store=Store(tmp_path/'db');planner=planning.Planner(store)
    keys=planner.ensure_day(date(2026,11,10),['12:00-13:00'],[('p','a')],now=0)
    store.change_task(keys[0],1,cancel=True)
    planner.ensure_day(date(2026,11,10),['12:00-13:00'],[('p','a')],now=0)
    assert len(store.tasks())==1 and store.tasks()[0]['state']=='cancelled'
    assert planner.ensure_day(date(2026,11,11),['12:00-13:00'],[('p','a')],round_limit=0,now=0)==[]

def test_evidence_preference_is_persistent_not_plan_learning(tmp_path):
    store=Store(tmp_path/'db');content=models.Content('p','a','1','url','title','source')
    evaluation=models.Evaluation(9,'reason','source',True)
    for _ in range(3):store.observe(content,evaluation,15,100)
    rows=Store(tmp_path/'db').preferences(100);assert rows[0]['count']==1
    assert planning.choose_provider([('p','a'),('q','a')],rows,15,'seed',0)==('p','a')

def config():return {'enabled':True,'daily_limit':10,'minute_limit':5,'share_min_score':8,
    'platforms':{'p':{'enabled':True,'accounts':{'a':{'enabled':True,'owner_umo':'qq_bot:FriendMessage:1','actions':{'owner_share':True},'daily_limits':{'owner_share':2}}}}}}

def test_global_threshold_cannot_be_lowered():
    cfg=config();cfg['platforms']['p']['accounts']['a']['share_min_score']=3
    policy=Policy(cfg)
    with pytest.raises(PermissionError):policy.permit('p','a','owner_share',models.Evaluation(7,'r','e',True))
    assert policy.permit('p','a','owner_share',models.Evaluation(9,'r','e',True))
    with pytest.raises(PermissionError):policy.permit('p','a','comment')

def test_executor_timeout_no_resend(tmp_path):
    async def run():
        store=Store(tmp_path/'db');registry=models.Registry();calls=[]
        class Provider:
            id='p';capabilities={'owner_share'}
            async def execute(self,*args):calls.append(1);raise TimeoutError()
        registry.register(Provider());engine=execution.Executor(store,registry,Policy(config()))
        evaluation=models.Evaluation(9,'r','e',True)
        receipt=await engine.execute('p','a','owner_share',{},'key',evaluation=evaluation)
        assert receipt.state=='unknown'
        assert await engine.execute('p','a','owner_share',{},'key',evaluation=evaluation) is None
        assert len(calls)==1
    asyncio.run(run())

def test_reader_rejects_invented_evidence():
    reader_module=importlib.import_module(package+'.core.reading')
    async def generate(*args):return '{"score":9,"reason":"r","evidence":"invented","recommend":true,"interests":[]}'
    reader=reader_module.Reader(generate)
    with pytest.raises(ValueError):asyncio.run(reader.evaluate(models.Content('p','a','1','url','title','A real source paragraph with enough evidence.')))

def test_secret_paths_and_permissions(tmp_path):
    SecretStore=importlib.import_module(package+'.core.secrets').SecretStore
    secrets=SecretStore(tmp_path/'secrets');secrets.write('p','a',{'token':'local-test'})
    assert secrets.read('p','a')['token']=='local-test'
    assert secrets.path('p','a').stat().st_mode & 0o777==0o600
    with pytest.raises(ValueError):secrets.read('p','../a')

def test_persistent_lease_expiration_and_foreign_release(tmp_path):
    Lease=importlib.import_module(package+'.integrations.lease').Lease
    stamp=[100];clock=lambda:stamp[0]
    a=Lease(tmp_path/'lease',clock);b=Lease(tmp_path/'lease',clock)
    assert a.acquire('host',30) and b.owner()=='host'
    assert not b.acquire('other',30)
    b.release('other');assert a.owner()=='host'
    stamp[0]=131;assert b.acquire('other',30)
    assert not a.acquire('host',30)
    b.release('other');assert a.acquire('host',30)

def test_scheduler_claims_once_and_caps_concurrency(tmp_path):
    async def run():
        store=Store(tmp_path/'db');registry=models.Registry();registry.register(SimpleNamespace(id='p',capabilities={'browse'}))
        cfg=config();cfg['platforms']['p']['accounts']['a']['daily_limits']['browse']=5
        policy=Policy(cfg);engine=execution.Executor(store,registry,policy)
        key=store.create_task('p','a','browse',1,100);store.create_task('p','a','browse',1,100)
        gate=asyncio.Event();started=[]
        async def browse(task):started.append(task['id']);await gate.wait()
        scheduler=execution.Scheduler(store,registry,engine,{'browse':browse},clock=lambda:50,concurrency=2)
        await scheduler.tick();await scheduler.tick();await asyncio.sleep(0)
        assert started==[key] or len(started)==1
        assert len(scheduler.running)==1 # same account never runs two sessions concurrently
        gate.set();await asyncio.gather(*(f for _,f in list(scheduler.running.values())))
        await scheduler.tick();await asyncio.sleep(0)
        assert len(started)==2
        await scheduler.close()
    asyncio.run(run())
