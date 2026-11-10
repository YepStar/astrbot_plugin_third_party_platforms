"""Read-only migration inventory. Never prints credential values or modifies source data."""
import argparse
from pathlib import Path
import json
import hashlib

GROUPS={
 'promote':('AUTONOMOUS_','BEHAVIOR_','RECOMMEND_OWNER_','SLEEP_','FIXED_','PROACTIVE_TASTE_','PROACTIVE_PREFERENCE_','PROACTIVE_EXPLORATION_'),
 'replace_with_memory_branches':('MEMORY_','EMBED_','ENABLE_VIDEO_LONG_TERM_MEMORY','VIDEO_MEMORY_'),
 'platform_media':('VIDEO_','BILI_SHARE_','IMAGE_VISION_'),
 'credentials':('SESSDATA','BILI_JCT','DEDE_USER_ID','BUVID','REFRESH_TOKEN'),
 'platform_native':('PRIVATE_','REPLY_','ENABLE_PRIVATE','ENABLE_REPLY','DYNAMIC_','ENABLE_DYNAMIC','BANGUMI_','ENABLE_BANGUMI','LIVE_','ENABLE_LIVE','SPECIAL_FOLLOW_'),
}
def classify(key):
 for group,prefixes in GROUPS.items():
  if key.startswith(prefixes):return group
 return 'needs_manual_review'

def inventory(root):
 result={'read_only':True,'config_keys':{},'sources':{},'requires_before_cutover':[
  'port native notification/DM pipelines and existing regression cases',
  'map all important platform options; do not discard manual-review keys',
  'import action/delivery ledgers before any new account writes',
  'snapshot private data outside source repository',
  'disable legacy writers before activating new plugin']}
 for name in ['bilibili_ai_bot','xiaoheihe_adapter']:
  cfg=root/'config'/f'astrbot_plugin_{name}_config.json'
  values=json.loads(cfg.read_text(encoding='utf-8-sig')) if cfg.exists() else {}
  result['config_keys'][name]={k:classify(k) if name=='bilibili_ai_bot' else ('credentials' if any(x in k.lower() for x in ['token','cookie','secret']) else 'review_nested_platform_group') for k in values}
  data=root/'plugin_data'/f'astrbot_plugin_{name}'
  result['sources'][name]=[{'path':str(p.relative_to(root)),'bytes':p.stat().st_size} for p in data.rglob('*') if p.is_file() and not p.is_symlink()] if data.exists() else []
 return result
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--data-root',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
 args=parser.parse_args();args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(inventory(args.data_root),ensure_ascii=False,indent=2));args.output.chmod(0o600)
 print('Read-only inventory saved; no credential values copied')
