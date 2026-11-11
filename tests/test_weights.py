import importlib,sys,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]));base=Path(__file__).resolve().parents[1].name
choose=importlib.import_module(base+'.core.planning').choose_provider

def test_manual_weights_are_relative_not_winner_takes_all_and_not_account_count():
 candidates=[('p','one'),('q','one')];counts=collections.Counter()
 for seed in range(4000):
  pid=choose(candidates,[],12,seed,weights={'p':3,'q':1})[0];counts[pid]+=1
  assert pid==choose(candidates+[('p','two'),('p','three')],[],12,seed,weights={'p':3,'q':1})[0]
 assert .72<counts['p']/4000<.78

def test_zero_excludes_platform_while_blank_uses_learning():
 prefs=[{'provider':'q','account':'one','hour':12,'score':10,'weight':10}]
 for seed in range(50):
  assert choose([('p','one'),('q','one')],prefs,12,seed,exploration=0)==('q','one')
  assert choose([('p','one'),('q','one')],prefs,12,seed,weights={'q':0})==('p','one')

def test_round_candidates_respect_rest_periods_and_represent_all_day_when_bounded():
 planning=importlib.import_module(base+'.core.planning')
 slots=planning.round_intervals([{'start':0,'end':7200,'source_window':0},{'start':10800,'end':14400,'source_window':0}],1800,30)
 assert len(slots)==5 and all(not (s['start']<10800 and s['end']>7200) for s in slots)
 many=planning.round_intervals([{'start':0,'end':86400,'source_window':0}],0,1)
 assert len(many)==192 and many[0]['start']==0 and many[-1]['end']==86400
