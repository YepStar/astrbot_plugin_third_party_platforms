"""Persist human migration choices only; never activate a platform capability."""
import json
from pathlib import Path
import time


class ReviewConflict(ValueError):
    pass


def catalog():
    return json.loads(Path(__file__).with_name('bili_review_catalog.json').read_text())


def read(store):
    value=store.setting('bili_migration_review',{})
    allowed=catalog()
    choices={key:decision for key,decision in value.get('choices',{}).items()
             if key in allowed and decision in ('integrate','skip')}
    return {'revision':value.get('revision',0),'choices':choices,'answered':len(choices),
            'total':len(allowed),'complete':len(choices)==len(allowed),'updated_at':value.get('updated_at')}


def save(store,choices,revision):
    allowed=catalog()
    if type(revision)is not int or revision<0 or not isinstance(choices,dict) or choices.keys()-allowed.keys() or any(value not in ('integrate','skip') for value in choices.values()):
        raise ValueError('invalid_migration_choices')
    # A single revision protects different browser tabs from silently overwriting
    # each other's saved decisions. No config, task or permission is changed.
    with store.connect() as db:
        db.execute('BEGIN IMMEDIATE')
        row=db.execute('SELECT value FROM settings WHERE key=?',('bili_migration_review',)).fetchone()
        previous=json.loads(row['value']) if row else {}
        if previous.get('revision',0)!=revision:
            raise ReviewConflict('migration_choices_changed')
        value={'revision':revision+1,'choices':choices,'updated_at':time.time()}
        db.execute('INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)',('bili_migration_review',json.dumps(value,ensure_ascii=False)))
    return {**value,'answered':len(choices),'total':len(allowed),'complete':len(choices)==len(allowed)}
