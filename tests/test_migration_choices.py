import importlib
from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]));base=Path(__file__).resolve().parents[1].name
review=importlib.import_module(base+'.core.migration_review')
Store=importlib.import_module(base+'.core.store').Store


def test_choices_persist_across_restart_without_activating_anything(tmp_path):
    store=Store(tmp_path/'db');keys=list(review.catalog())
    before=review.read(store);assert before['answered']==0 and before['total']==54
    saved=review.save(store,{keys[0]:'integrate',keys[1]:'skip'},0)
    assert saved['revision']==1 and saved['answered']==2 and not saved['complete']
    assert review.read(Store(tmp_path/'db'))['choices']=={keys[0]:'integrate',keys[1]:'skip'}
    assert store.actions()==[] and store.tasks()==[]


def test_all_choices_complete_does_not_run_migration(tmp_path):
    store=Store(tmp_path/'db');choices={key:'integrate' for key in review.catalog()}
    assert review.save(store,choices,0)['complete']
    assert store.actions()==[] and store.tasks()==[]


def test_stale_tab_cannot_overwrite_newer_decisions(tmp_path):
    store=Store(tmp_path/'db');key=next(iter(review.catalog()));review.save(store,{key:'skip'},0)
    with pytest.raises(review.ReviewConflict):review.save(store,{key:'integrate'},0)
    assert review.read(store)['choices'][key]=='skip'


@pytest.mark.parametrize('choices,revision',[({'ENABLE_AFFECTION':'integrate'},0),({'COOKIE_AUTO_REFRESH':'skip'},0),({'ENABLE_MOOD':'run_now'},0),({'ENABLE_MOOD':'integrate'},True),({'ENABLE_MOOD':'integrate'},-1)])
def test_invalid_or_removed_option_is_rejected(tmp_path,choices,revision):
    store=Store(tmp_path/'db')
    with pytest.raises(ValueError):review.save(store,choices,revision)
    assert review.read(store)['revision']==0


def test_clearing_choice_returns_it_to_undecided(tmp_path):
    store=Store(tmp_path/'db');key=next(iter(review.catalog()));review.save(store,{key:'skip'},0)
    saved=review.save(store,{},1)
    assert saved['answered']==0 and saved['revision']==2
