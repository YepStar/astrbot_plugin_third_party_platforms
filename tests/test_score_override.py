import importlib,sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
base=Path(__file__).resolve().parents[1].name
policy=importlib.import_module(base+'.core.policy')
models=importlib.import_module(base+'.core.models')
account=importlib.import_module(base+'.core.configuration').account

@pytest.mark.parametrize('key',['share_min_score','comment_min_score'])
@pytest.mark.parametrize('value',[5,'5',9])
def test_account_value_wins_over_both_higher_and_lower_global(key,value):
    assert policy.score_threshold({key:10},{key:value},key)==float(value)
    assert policy.score_threshold({key:1},{key:value},key)==float(value)

@pytest.mark.parametrize('value',[None,'','  ','broken',float('nan'),float('inf'),True,0,11,{}])
def test_global_is_only_fallback_for_unreadable_account_value(value):
    assert policy.score_threshold({'share_min_score':7},{'share_min_score':value},'share_min_score')==7


def test_optional_override_can_be_cleared_and_stays_inherited_on_other_edits():
    saved=account('netease',{'share_min_score':5,'comment_min_score':None})
    assert saved['share_min_score']==5
    assert saved['comment_min_score'] is None
    saved=account('netease',{'share_min_score':''},saved)
    saved=account('netease',{'enabled':True},saved)
    assert saved['share_min_score'] is None
    assert policy.score_threshold({'share_min_score':7},saved,'share_min_score')==7


def test_policy_enforcement_uses_account_overrides_for_both_actions():
    cfg={'enabled':True,'share_min_score':9,'comment_min_score':9,'platforms':{'bilibili':{'enabled':True,'accounts':{'one':{
       'enabled':True,'actions':{'owner_share':True,'comment':True},'share_min_score':5,'comment_min_score':5,
       'owner_umo':'qq_bot:FriendMessage:1','share_delivery':'qq_private'}}}}}
    p=policy.Policy(cfg)
    evaluation=models.Evaluation(6,'reason','evidence',True)
    assert p.permit('bilibili','one','owner_share',evaluation)
    assert p.permit('bilibili','one','comment',evaluation)
