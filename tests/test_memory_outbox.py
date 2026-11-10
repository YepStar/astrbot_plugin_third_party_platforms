import importlib,sys
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock
sys.path.insert(0,str(Path(__file__).resolve().parents[2]));base=Path(__file__).resolve().parents[1].name
Store=importlib.import_module(base+'.core.store').Store
models=importlib.import_module(base+'.core.models')
Gateway=importlib.import_module(base+'.integrations.memory').PublicMemoryGateway

def test_unavailable_memory_preserves_outbox_then_recovers_once(tmp_path):
 store=Store(tmp_path/'db');metadata=[None];now=[1000]
 context=NS(get_registered_star=lambda _:metadata[0]);gateway=Gateway(context,True,store=store,clock=lambda:now[0])
 c=models.Content('bilibili','one','BV1234567890','url','title','A long public source text, not a private conversation.')
 e=models.Evaluation(9,'interesting','public source',True)
 assert gateway.put(c,e)=='queued';gateway.put(c,e);gateway.drain()
 assert len(store.pending_memory(2000))==1
 facade=NS(integration_api=1,checkpoint=lambda _:{'bank':'public','generation':0},put_checkpointed=Mock());metadata[0]=NS(activated=True,star_cls=NS(public_memory=facade))
 now[0]=2000;gateway.drain();gateway.drain()
 facade.put_checkpointed.assert_called_once();assert store.pending_memory(3000)==[]

def test_disabled_memory_keeps_pending_without_writes(tmp_path):
 store=Store(tmp_path/'db');enabled=[True];facade=NS(put=Mock())
 context=NS(get_registered_star=lambda _:NS(activated=True,star_cls=NS(public_memory=facade)))
 gateway=Gateway(context,lambda:enabled[0],store=store)
 gateway.put(models.Content('xiaoheihe','a','1','url','title','text'),models.Evaluation(8,'r','e'))
 enabled[0]=False;gateway.drain();facade.put.assert_not_called()
 assert len(store.pending_memory(1e20))==1

def test_rollback_invalidates_delayed_memory_ingestion(tmp_path):
 store=Store(tmp_path/'db');generation=[0]
 facade=NS(integration_api=1,checkpoint=lambda _:{'bank':'public','generation':generation[0]},put_checkpointed=Mock())
 context=NS(get_registered_star=lambda _:NS(activated=True,star_cls=NS(public_memory=facade)))
 gateway=Gateway(context,True,store=store)
 gateway.put(models.Content('bilibili','a','1','url','title','text'),models.Evaluation(8,'r','e'))
 generation[0]=1;gateway.drain()
 facade.put_checkpointed.assert_not_called();assert store.memory_status()=={'superseded':1}


def test_public_recall_never_imports_private_or_unrecognized_scopes(tmp_path):
 facade=NS(search=Mock(return_value=[{'scope':'private:owner','content':'private fact'},
  {'scope':'bilibili:public','content':'video memory'},{'scope':'xiaoheihe:public','content':'post memory'}]))
 gateway=Gateway(NS(get_registered_star=lambda _:NS(activated=True,star_cls=NS(public_memory=facade))),True)
 assert [r['content'] for r in gateway.recall('xiaoheihe','query')]==['video memory','post memory']
 assert gateway.recall('unknown','query')==[]


def test_confirmed_public_reply_is_checkpointed_but_dm_is_not_exported(tmp_path):
 store=Store(tmp_path/'db');generation=[0]
 facade=NS(integration_api=1,checkpoint=lambda _:{'bank':'public','generation':generation[0]},put_checkpointed=Mock())
 gateway=Gateway(NS(get_registered_star=lambda _:NS(activated=True,star_cls=NS(public_memory=facade))),True,store=store)
 event=models.Incoming('xiaoheihe','a','reply','event','42','original words',1000,{'reply_anchor':'comment'},True)
 assert gateway.remember_reply(event,'bot reply')=='queued'
 from dataclasses import replace
 assert gateway.remember_reply(replace(event,stream='private'),'private text')=='disabled_or_private'
 gateway.drain();facade.put_checkpointed.assert_called_once()
 args=facade.put_checkpointed.call_args.args
 assert args[0]=='xiaoheihe:public' and 'sender UID 42' in args[2]
 assert 'private text' not in args[2]
 assert store.memory_status()=={'saved':1}


def test_public_reply_queue_obeys_memory_rollback(tmp_path):
 store=Store(tmp_path/'db');generation=[0]
 facade=NS(integration_api=1,checkpoint=lambda _:{'bank':'public','generation':generation[0]},put_checkpointed=Mock())
 gateway=Gateway(NS(get_registered_star=lambda _:NS(activated=True,star_cls=NS(public_memory=facade))),True,store=store)
 event=models.Incoming('bilibili','a','reply','event','42','words',1000,{},True)
 gateway.remember_reply(event,'reply');generation[0]=1;gateway.drain()
 facade.put_checkpointed.assert_not_called()
 assert store.memory_status()=={'superseded':1}
