import importlib,sys
from pathlib import Path
from types import SimpleNamespace as NS
sys.path.insert(0,str(Path(__file__).resolve().parents[2]));base=Path(__file__).resolve().parents[1].name
checks=importlib.import_module(base+'.core.deployment').checks
Store=importlib.import_module(base+'.core.store').Store

def test_cutover_requires_verified_import_and_both_old_writers_and_transport_stopped(tmp_path):
 store=Store(tmp_path/'db');active=[True];platform=[True]
 context=NS(get_registered_star=lambda _:NS(activated=active[0]),get_config=lambda:{'platform':[{'type':'xiaoheihe','enable':platform[0]}]})
 host=NS(store=store,context=context,config={'provider_id':'model','platforms':{'p':{'accounts':{'a':{'enabled':True}}}}})
 assert not all(checks(host).values())
 store.set_setting('deployment',{'schema':1,'verified':True,'mode':'comparison'})
 assert not all(checks(host).values())
 active[0]=False;assert not all(checks(host).values())
 platform[0]=False;assert all(checks(host).values())
 active[0]=True;assert not all(checks(host).values())
