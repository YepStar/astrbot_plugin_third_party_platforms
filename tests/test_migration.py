import importlib
import json
from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
base=Path(__file__).resolve().parents[1].name
migration=importlib.import_module(base+'.migration')
Store=importlib.import_module(base+'.core.store').Store

def fixture(root):
 (root/'config').mkdir(parents=True)
 (root/'config/astrbot_plugin_bilibili_ai_bot_config.json').write_text(json.dumps({'SESSDATA':'fake-login','BILI_JCT':'fake-csrf','OWNER_MID':'123','DEDE_USER_ID':'456','OWNER_QQ_UMO':'qq_bot:FriendMessage:789','ENABLE_REPLY':True,'ENABLE_PRIVATE_MESSAGES':True,'PRIVATE_MESSAGE_AUTO_REPLY':True,'PRIVATE_MESSAGE_REPLY_SCOPE':'owner','ENABLE_OWNER_RECOMMEND':True}))
 (root/'config/astrbot_plugin_xiaoheihe_adapter_config.json').write_text(json.dumps({'profiles':[{'profile_id':'default','enabled':True,'dry_run':True,'poll_mentions':True,'owner_uid':'1'}]}))
 data=root/'plugin_data/astrbot_plugin_bilibili_ai_bot';data.mkdir(parents=True)
 (data/'replied.json').write_text('["already-sent"]')
 (data/'owner_recommend_log.json').write_text(json.dumps({'BV1234567890':{'channel':'qq','status':'failed_or_uncertain'}}))
 return root

def test_migration_refuses_active_or_nonempty_target(tmp_path):
 source=fixture(tmp_path/'source');target=tmp_path/'target'
 with pytest.raises(ValueError):migration.apply(source,target)
 assert not target.exists()
 target.mkdir();(target/'untouched').write_text('preserve')
 with pytest.raises(ValueError):migration.apply(source,target,source_stopped=True)
 assert (target/'untouched').read_text()=='preserve'

def test_migration_preserves_source_and_separates_secrets(tmp_path):
 source=fixture(tmp_path/'source');target=tmp_path/'new'
 before=(source/'config/astrbot_plugin_bilibili_ai_bot_config.json').read_bytes()
 report=migration.apply(source,target,source_stopped=True)
 assert not report['activation_allowed']
 config=json.loads((target/'imported-config.json').read_text())
 assert 'fake-login' not in json.dumps(config)
 assert json.loads((target/'secrets/bilibili--default.json').read_text())['SESSDATA']=='fake-login'
 assert not config['enabled']
 assert not config['platforms']['xiaoheihe']['accounts']['default']['actions']['reply'] # preserve dry run
 assert config['platforms']['bilibili']['accounts']['default']['reply']['private_scope']=='owner'
 assert (source/'config/astrbot_plugin_bilibili_ai_bot_config.json').read_bytes()==before
 states={r['key']:r['state'] for r in Store(target/'platforms.sqlite3').actions()}
 assert states['reply:bilibili:default:reply:already-sent']=='succeeded'
 assert 'unknown' in states.values()
 assert migration.apply(source,target,source_stopped=True)==report

def test_migration_cannot_write_private_data_into_source_tree(tmp_path):
 source=fixture(tmp_path/'source')
 with pytest.raises(ValueError):migration.apply(source,source/'new',source_stopped=True)

def test_migration_snapshot_refuses_symlinks(tmp_path):
 source=fixture(tmp_path/'source')
 (source/'plugin_data/astrbot_plugin_bilibili_ai_bot/link').symlink_to('/etc/hosts')
 with pytest.raises(ValueError):migration.apply(source,tmp_path/'new',source_stopped=True)
 assert not (tmp_path/'new/migration.json').exists()


def test_private_inbox_cursor_and_ambiguous_pending_are_preserved_without_replay(tmp_path):
 source=fixture(tmp_path/'source');data=source/'plugin_data/astrbot_plugin_bilibili_ai_bot'
 (data/'private_message_state.json').write_text(json.dumps({'account_uid':'456','initialized':True,
  'initialized_at':100,'sessions':{'1:123':9,'2:999':8},'processed_keys':['sent-msg'],
  'pending_messages':[{'msg_key':'pending-msg','talker_id':123,'sender_uid':'123','timestamp':200,'content':'private fixture text'}]}))
 target=tmp_path/'new';report=migration.apply(source,target,source_stopped=True);store=Store(target/'platforms.sqlite3')
 assert report['private_pending_review']==1
 assert store.cursor('bilibili','default','private')['sessions']=={'123':9}
 assert store.action('legacy_message:bilibili:default:sent-msg')['state']=='succeeded'
 assert store.action('legacy_message:bilibili:default:pending-msg')['state']=='unknown'
 assert store.pending_events(1e20)==[]
 with store.connect() as db:
  row=db.execute("SELECT payload,state FROM inbox WHERE stream='private'").fetchone()
  assert json.loads(row['payload'])['text']=='private fixture text' and row['state']=='unknown'
 assert 'private fixture text' not in (target/'imported-config.json').read_text()


def test_private_inbox_account_mismatch_does_not_commit_migration(tmp_path):
 source=fixture(tmp_path/'source');data=source/'plugin_data/astrbot_plugin_bilibili_ai_bot'
 (data/'private_message_state.json').write_text('{"account_uid":"different"}')
 target=tmp_path/'new'
 with pytest.raises(ValueError,match='account_mismatch'):migration.apply(source,target,source_stopped=True)
 assert not (target/'migration.json').exists()
