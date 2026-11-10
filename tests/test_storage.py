import importlib,sys,time,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]));base=Path(__file__).resolve().parents[1].name
Store=importlib.import_module(base+'.core.store').Store
storage=importlib.import_module(base+'.core.storage')
def test_cleanup_only_prunes_old_terminal_bodies_for_selected_platform(tmp_path):
 store=Store(tmp_path/'db');now=time.time()
 with store.connect() as db:
  for key,pid,state,created in [('old','xiaoheihe','succeeded',0),('pending','xiaoheihe','pending',0),('recent','xiaoheihe','succeeded',now),('other','bilibili','succeeded',0)]:
   db.execute('INSERT INTO inbox(key,provider,account,stream,payload,state) VALUES(?,?,?,?,?,?)',(key,pid,'default','reply',json.dumps({'created':created,'text':'old private text'}),state))
  db.execute("INSERT INTO actions VALUES('dedupe','succeeded','xiaoheihe','default','reply',0,'{}')")
 assert storage.preview(store,'xiaoheihe',30)['body_count']==1
 assert storage.cleanup(store,'xiaoheihe',30)['pruned_bodies']==1
 with store.connect() as db:
  assert db.execute("SELECT payload FROM inbox WHERE key='old'").fetchone()[0]=='{}'
  assert all(db.execute('SELECT payload FROM inbox WHERE key=?',(k,)).fetchone()[0]!='{}' for k in ['pending','recent','other'])
 assert store.action('dedupe')
