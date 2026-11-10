import importlib
from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
base=Path(__file__).resolve().parents[1].name
account=importlib.import_module(base+'.core.configuration').account


def test_strategy_edit_preserves_migrated_sources_and_provider_options():
    before=account('bilibili',{'enabled':True,'owner_uid':'123','share_enabled':True,'share_delivery':'private_message',
        'pools':['排行榜:游戏','最新:单机游戏'],'follow_uids':['42'],'special_follow_enabled':True,'daily_share_limit':3})
    before['reply']['poll_mentions']=False
    before['browse']['count']=4
    after=account('bilibili',{'share_min_score':9},before)
    assert after['browse']==before['browse']
    assert after['reply']==before['reply']
    assert after['actions']==before['actions']
    assert after['daily_limits']==before['daily_limits']
    assert after['owner_uid']=='123' and after['share_delivery']=='private_message'
    assert after['share_min_score']==9


def test_xhh_edit_preserves_multi_topic_and_dry_run():
    previous=account('xiaoheihe',{'topic_ids':['1','2'],'reply_enabled':False})
    previous['reply'].update(dry_run=True,poll_replies=False,max_reply_chars=180)
    after=account('xiaoheihe',{'topic_ids':'3,4'},previous)
    assert after['browse']['topic_ids']==['3','4']
    assert after['reply']['dry_run'] and not after['reply']['poll_replies']
    assert after['reply']['max_reply_chars']==180


@pytest.mark.parametrize('values',[{'follow_uids':['not-a-uid']},{'topic_ids':['https://example.com']},
    {'pools':[]},{'pools':['popular']*9},{'share_delivery':'invented'},{'special_follow_enabled':'true'}])
def test_invalid_source_settings_rejected(values):
    with pytest.raises(ValueError):account('bilibili',values)

def test_advanced_bili_settings_and_fallback_categories_persist_without_enabling_actions():
 a=account('bilibili',{'custom_reply_instruction':'自然回应','browse_count':4,'like_enabled':False,'reply_model':'model1','private_max_per_poll':10})
 b=account('bilibili',{'comment_min_score':9},a)
 assert b['reply']['custom_reply_instruction']=='自然回应' and b['browse']['count']==4
 assert b['models']['reply_model']=='model1' and not b['interactions']['like_enabled']
 assert b['reply']['private_max_per_poll']==10
 with pytest.raises(ValueError):account('xiaoheihe',{'fallback_sources':['all','anime']})
 assert account('xiaoheihe',{'fallback_sources':['anime','daily']})['browse']['fallback_sources']==['anime','daily']

def test_video_interactions_cannot_be_granted_to_other_providers():
 with pytest.raises(ValueError):account('xiaoheihe',{'like_enabled':True})
