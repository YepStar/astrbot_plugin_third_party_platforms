import importlib,sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]));base=Path(__file__).resolve().parents[1].name
settings=importlib.import_module(base+'.core.settings')

@pytest.mark.parametrize('values',[
 {'enabled':True},{'platforms':{}},{'token':'not-config'},{'timezone':'not/a/timezone'},
 {'windows':['25:00-26:00']},{'rest_windows':'23:00-08:00'},{'daily_rounds':True},
 {'share_min_score':float('nan')},{'exploration_ratio':1.2},{'vision_frame_count':50},
 {'control_umos':['xiaoheihe:GroupMessage:1']},{'model_ids':{'shell':'command'}},{'memory_enabled':'true'}])
def test_invalid_or_privileged_global_changes_rejected(values):
 with pytest.raises(ValueError):settings.validate_settings(values,{})

def test_partial_global_update_preserves_other_settings_and_model_overrides():
 previous={'enabled':True,'platforms':{'private':'untouched'},'model_ids':{'evaluation':'existing-evaluator','daily_plan':'existing-planner'}}
 result=settings.validate_settings({'model_ids':{'daily_plan':'new-planner'},'windows':['22:00-02:00'],'rest_windows':['23:00-01:00']},previous)
 assert result['model_ids']=={'evaluation':'existing-evaluator','daily_plan':'new-planner'}
 assert previous['model_ids']['daily_plan']=='existing-planner'
 assert 'enabled' not in result and 'platforms' not in result

@pytest.mark.parametrize('value',[True,-1,101,float('nan'),float('inf'),'3'])
def test_platform_weight_numbers_are_bounded(value):
 with pytest.raises(ValueError):settings.validate_settings({'platform_weights':{'bilibili':value}}, {})

def test_platform_weight_patch_clear_and_extension_validation():
 before={'platform_weights':{'bilibili':3,'netease':2}}
 assert settings.validate_settings({'platform_weights':{'bilibili':None,'xiaoheihe':0}},before)['platform_weights']=={'netease':2,'xiaoheihe':0}
 assert before['platform_weights']['bilibili']==3
 with pytest.raises(ValueError):settings.validate_settings({'platform_weights':{'unknown':2}},before)
 assert settings.validate_settings({'platform_weights':{'custom':1}}, {},providers={'custom'})['platform_weights']=={'custom':1}
