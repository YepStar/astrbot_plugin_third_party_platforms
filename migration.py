"""Offline, idempotent import into a NEW data directory; never overwrite source or current runtime."""
from pathlib import Path
import json
import sqlite3
import shutil
import hashlib
import time
from .core.store import Store
from .core.secrets import SecretStore
from .core.configuration import account as normalize_account
from .core.models import Receipt,Incoming
from .migration_history import import_history

BILI_KEYS={'SESSDATA','BILI_JCT','DEDE_USER_ID','BUVID3','BUVID4','REFRESH_TOKEN','AC_TIME_VALUE','PROXY_URL'}

def load(path,default=None):
    if not path.exists():return {} if default is None else default
    if path.is_symlink():raise ValueError('source_symlink')
    return json.loads(path.read_text(encoding='utf-8-sig'))

def old_data(root,name):return root/'plugin_data'/('astrbot_plugin_'+name)

def preview(root):
    root=Path(root)
    b=load(root/'config/astrbot_plugin_bilibili_ai_bot_config.json')
    x=load(root/'config/astrbot_plugin_xiaoheihe_adapter_config.json')
    profiles=x.get('profiles',[])
    return {'platforms':['bilibili','xiaoheihe'], 'xhh_profiles':[p['profile_id'] for p in profiles],
        'bili_credentials_present':bool(b.get('SESSDATA')),
        'preserve_source':True,'requires_stopped_legacy':True,
        'unmapped_bili_keys':sorted(k for k in b if k not in BILI_KEYS),
        'reply_private_scope':b.get('PRIVATE_MESSAGE_REPLY_SCOPE','owner')}

def clock_text(value):
    if isinstance(value,int) or (isinstance(value,str) and value.isdigit()):
        if not 0<=int(value)<24:raise ValueError('invalid_legacy_sleep_hour')
        return f'{int(value):02d}:00'
    return str(value)

def build_config(b,x):
    bili=normalize_account('bilibili',{
        'enabled':True,'owner_umo':b.get('OWNER_QQ_UMO',''),'owner_uid':str(b.get('OWNER_MID','')),'self_uid':str(b.get('DEDE_USER_ID','')),
        'share_delivery':b.get('RECOMMEND_OWNER_DELIVERY','private_message'),'owner_bili_name':b.get('OWNER_BILI_NAME',''),
        'share_gap_seconds':int(b.get('RECOMMEND_OWNER_MIN_GAP_MINUTES',120))*60,'share_enabled':bool(b.get('ENABLE_OWNER_RECOMMEND',False)), 'share_min_score':b.get('RECOMMEND_OWNER_MIN_SCORE',8),
        'reply_enabled':bool(b.get('ENABLE_REPLY',False)),
        'private_reply_enabled':bool(b.get('ENABLE_PRIVATE_MESSAGES',False) and b.get('PRIVATE_MESSAGE_AUTO_REPLY',True)),
        'comment_enabled':bool(b.get('PROACTIVE_COMMENT',False)), 'comment_min_score':b.get('PROACTIVE_COMMENT_MIN_SCORE',8),
        'dynamic_enabled':bool(b.get('ENABLE_DYNAMIC',False)),'daily_dynamic_limit':b.get('AUTONOMOUS_DYNAMIC_DAILY_MAX',1),
        'daily_browse_limit':b.get('PROACTIVE_DAILY_LIMIT',4), 'daily_share_limit':b.get('RECOMMEND_OWNER_DAILY_LIMIT',1),
        'daily_private_reply_limit':b.get('AUTONOMOUS_PRIVATE_DAILY_MAX',30),'daily_reply_limit':b.get('AUTONOMOUS_REPLY_DAILY_MAX',80),'daily_comment_limit':b.get('PROACTIVE_COMMENT_DAILY_LIMIT',2)})
    bili['reply'].update(poll_seconds=max(60,int(b.get('POLL_INTERVAL',120))),max_age_seconds=b.get('PRIVATE_MESSAGE_MAX_MESSAGE_AGE',3600),always_reply_uids=[str(v) for v in b.get('REPLY_ALWAYS_UIDS',[])],instruction=b.get('CUSTOM_REPLY_INSTRUCTION',''),private_instruction=b.get('CUSTOM_PRIVATE_MESSAGE_INSTRUCTION',''),private_scope=b.get('PRIVATE_MESSAGE_REPLY_SCOPE','owner'),
        private_whitelist=b.get('PRIVATE_MESSAGE_REPLY_WHITELIST_UIDS',[]),
        cooldown_seconds=b.get('REPLY_COOLDOWN',60), probability_percent=b.get('REPLY_PROBABILITY_PERCENT',100),
        interest_filter=bool(b.get('ENABLE_INTEREST_BASED_REPLY',False)),
        similar_skip=bool(b.get('ENABLE_SIMILAR_SKIP',False)),similarity_percent=b.get('REPLY_SIMILARITY_PERCENT',85))
    bili['browse'].update(count=min(5,max(1,int(b.get('PROACTIVE_VIDEO_COUNT',2)))),pools=b.get('PROACTIVE_VIDEO_POOLS',['popular']),follow_uids=b.get('PROACTIVE_FOLLOW_UIDS',[]),
        special_follow_enabled=bool(b.get('SPECIAL_FOLLOW_ENABLED',False)))
    xaccounts={};browse=x.get('browse_companion',{});permissions=x.get('permissions',{});reply=x.get('reply',{})
    for profile in x.get('profiles',[]):
        pid=profile['profile_id'];dry=profile.get('dry_run',True)
        values={'enabled':bool(profile.get('enabled',False)), 'owner_uid':str(profile.get('owner_uid','')),
            'owner_umo':browse.get('owner_umo','') if browse.get('profile_id','default')==pid else '',
            'share_enabled':bool(browse.get('enabled') and browse.get('share_enabled') and browse.get('profile_id','default')==pid),
            'reply_enabled':not dry and bool(profile.get('poll_mentions') or profile.get('poll_replies')),
            'comment_enabled':False, # Existing proactive-feed review flow is NOT an authorization for automatic publication.
            'share_gap_seconds':int(browse.get('share_gap_minutes',90))*60,'share_min_score':b.get('RECOMMEND_OWNER_MIN_SCORE',8),'daily_share_limit':browse.get('share_daily_limit',1),
            'poll_seconds':max(60,x.get('polling',{}).get('poll_interval_seconds',180)),
            **{key:permissions.get(key,[]) for key in ['user_whitelist','user_blacklist','author_whitelist','author_blacklist','keyword_blacklist']},
            'whitelist_mode':bool(permissions.get('whitelist_mode',False)),
            'only_explicit_mentions':bool(reply.get('only_explicit_mentions',True)),
            'reply_to_direct_replies':bool(reply.get('reply_to_direct_replies',True))}
        account=normalize_account('xiaoheihe',values)
        account['network']=x.get('network',{})
        account['context']=x.get('context',{})
        account['browse']['count']=min(5,max(1,int(browse.get('posts_per_session',2))))
        account['browse']['topic_ids']=x.get('proactive_feed',{}).get('topic_ids',[])
        account['reply'].update(poll_mentions=bool(profile.get('poll_mentions',True)),poll_replies=bool(profile.get('poll_replies',True)),
            dry_run=bool(dry), max_reply_chars=reply.get('max_reply_chars',300))
        xaccounts[pid]=account
    windows=list(dict.fromkeys((b.get('FIXED_PROACTIVE_WINDOWS') or ['10:00-11:00','20:00-21:00'])+(browse.get('windows') or [])))
    model=b.get('SCHEDULE_PLAN_PROVIDER_ID') or b.get('GENERATION_PROVIDER_ID') or b.get('LLM_PROVIDER_ID') or browse.get('provider_id','')
    return {'enabled':False,'public_persona':b.get('CUSTOM_SYSTEM_PROMPT',''),'activity_level':b.get('AUTONOMOUS_ACTIVITY_LEVEL',55),
        'rest_windows':[clock_text(b.get('SLEEP_START','01:00'))+'-'+clock_text(b.get('SLEEP_END','08:00'))],
        'exploration_ratio':float(b.get('PROACTIVE_EXPLORATION_RATIO',.15)),
        'preference_half_life_days':b.get('PROACTIVE_PREFERENCE_HALF_LIFE_DAYS',14),
        'model_ids':{'daily_plan':model,'evaluation':b.get('SUMMARY_PROVIDER_ID') or model,'platform_reply':b.get('LLM_PROVIDER_ID') or model},
        'comment_min_score':b.get('PROACTIVE_COMMENT_MIN_SCORE',8),'minute_limit':b.get('BEHAVIOR_GLOBAL_MAX_PER_MINUTE',12),
        'timezone':'Asia/Shanghai','memory_enabled':True,'provider_id':model,
        'platforms':{'bilibili':{'enabled':True,'accounts':{'default':bili}},'xiaoheihe':{'enabled':True,'accounts':xaccounts}},
        'windows':windows,
        'control_umos':[b['OWNER_QQ_UMO']] if b.get('OWNER_QQ_UMO') else [],
        'share_min_score':b.get('RECOMMEND_OWNER_MIN_SCORE',8),'daily_limit':b.get('BEHAVIOR_GLOBAL_DAILY_LIMIT',20),
        'daily_rounds':b.get('PROACTIVE_TIMES_COUNT',2)}

def offline_db(path):
    wal=path.with_name(path.name+'-wal')
    if wal.exists() and wal.stat().st_size:raise ValueError('offline_source_has_uncheckpointed_wal')
    return sqlite3.connect('file:'+str(path)+'?mode=ro&immutable=1',uri=True)

def backup_tree(source,dest):
    if not source.exists():return
    dest.mkdir(parents=True,exist_ok=True);dest.chmod(0o700)
    for p in source.iterdir():
        if p.is_symlink():raise ValueError('source_symlink')
        target=dest/p.name
        if p.is_dir():backup_tree(p,target)
        elif p.suffix in {'.db','.sqlite3','.sqlite'}:
            src=offline_db(p);out=sqlite3.connect(target)
            try:src.backup(out)
            finally:src.close();out.close()
            target.chmod(0o600)
        elif not p.name.endswith(('-wal','-shm')):
            shutil.copy2(p,target);target.chmod(0o600)

def apply(root,target,*,source_stopped=False):
    root,target=Path(root).resolve(),Path(target).resolve()
    if not source_stopped:raise ValueError('legacy_must_be_stopped')
    if target==root or root in target.parents:raise ValueError('target_must_be_outside_source')
    repository=Path(__file__).resolve().parent
    if target==repository or repository in target.parents:raise ValueError('private_data_must_not_enter_source_repo')
    marker=target/'migration.json'
    if marker.exists():return load(marker)
    if target.exists() and any(target.iterdir()):raise ValueError('target_must_be_empty')
    target.mkdir(parents=True,exist_ok=True);target.chmod(0o700)
    b=load(root/'config/astrbot_plugin_bilibili_ai_bot_config.json');x=load(root/'config/astrbot_plugin_xiaoheihe_adapter_config.json')
    configuration=build_config(b,x);backup=target/'legacy_backup'
    backup.mkdir();backup.chmod(0o700)
    for name in ['bilibili_ai_bot','xiaoheihe_adapter']:
        cfg=root/'config'/f'astrbot_plugin_{name}_config.json'
        if cfg.exists():shutil.copy2(cfg,backup/cfg.name);(backup/cfg.name).chmod(0o600)
        backup_tree(old_data(root,name),backup/name)
    secrets=SecretStore(target/'secrets');secrets.write('bilibili','default',{k:v for k,v in b.items() if k in BILI_KEYS})
    for pid in configuration['platforms']['xiaoheihe']['accounts']:
        source=old_data(root,'xiaoheihe_adapter')/'credentials'/f'{pid}.json'
        if source.exists():secrets.write('xiaoheihe',pid,load(source))
    store=Store(target/'platforms.sqlite3');imported=0
    def record(key,provider,account,kind,state='succeeded'):
        nonlocal imported
        if store.claim_action(key,provider,account,kind,[],0):
            store.finish_action(key,Receipt(state,code='legacy_import'));imported+=1
    data=old_data(root,'bilibili_ai_bot')
    for rpid in load(data/'replied.json',[]):record('reply:bilibili:default:reply:'+str(rpid),'bilibili','default','reply')
    for bv in load(data/'commented_videos.json',[]):record('comment:bilibili:default:'+str(bv),'bilibili','default','comment')
    private=load(data/'private_message_state.json',{})
    private_review=0
    if private:
        expected=str(b.get('DEDE_USER_ID',''))
        if str(private.get('account_uid',''))!=expected:raise ValueError('private_inbox_account_mismatch')
        sequences={key.split(':',1)[1]:int(value) for key,value in private.get('sessions',{}).items()
            if key.startswith('1:') and key.split(':',1)[1].isdigit()}
        if private.get('initialized'):
            store.ingest('bilibili','default','private',[],{'sessions':sequences,
                'started_at':float(private.get('initialized_at') or time.time())})
        for key in private.get('processed_keys',[]):
            record(f'legacy_message:bilibili:default:{key}','bilibili','default','private_reply')
        for message in private.get('pending_messages',[]):
            key=str(message.get('msg_key',''));talker=str(message.get('talker_id',''))
            if not key or not talker.isdigit():continue
            record(f'legacy_message:bilibili:default:{key}','bilibili','default','private_reply','unknown')
            event=Incoming('bilibili','default','private',talker+':'+key,str(message.get('sender_uid',talker)),
                str(message.get('content',''))[:4000],float(message.get('timestamp') or 0),
                {'receiver':talker,'reply_anchor':talker+':'+key},True,context={'legacy_event_id':key})
            store.ingest('bilibili','default','private',[event],store.cursor('bilibili','default','private') or
                {'sessions':sequences,'started_at':time.time()},initial_ignore=False)
            store.finish_event(event.key,'unknown','legacy_pending_requires_reconciliation')
            private_review+=1
    # Conservative transmission history: failed_or_uncertain is imported unknown, never resent.
    def owner_key(provider,item,recipient):return 'owner_share:'+hashlib.sha256(f'{provider}|{item}|{recipient}'.encode()).hexdigest()
    log=load(data/'owner_recommend_log.json',{})
    if isinstance(log,dict):
        for bv,row in log.items():
            if not isinstance(row,dict):continue
            recipient=row.get('target') or configuration['platforms']['bilibili']['accounts']['default']['owner_umo']
            record(f'legacy_owner_share:bilibili:default:{bv}','bilibili','default','owner_share','succeeded' if row.get('status','sent')=='sent' else 'unknown')
            record(owner_key('bilibili',bv,recipient),'bilibili','default','owner_share','succeeded' if row.get('status')=='sent' else 'unknown')
    journal=load(old_data(root,'xiaoheihe_adapter')/'browse_journal.json',{})
    for row in journal.get('shares',[]):
        record(owner_key('xiaoheihe',str(row['post_id']),row.get('owner_umo','')),'xiaoheihe',x.get('browse_companion',{}).get('profile_id','default'),'owner_share','succeeded' if row.get('status')=='sent' else 'unknown')
    database=old_data(root,'xiaoheihe_adapter')/'xiaoheihe.db'
    if database.exists():
        db=offline_db(database);db.row_factory=sqlite3.Row
        try:
            for row in db.execute('SELECT profile_id,external_comment_id,status FROM incoming_events'):
                if row['external_comment_id']:
                    record(f"reply:xiaoheihe:{row['profile_id']}:reply:{row['external_comment_id']}",'xiaoheihe',row['profile_id'],'reply', 'succeeded' if row['status']=='sent' else 'unknown')
            for row in db.execute('SELECT profile_id,event_type,last_event_id FROM notification_cursors'):
                store.ingest('xiaoheihe',row['profile_id'],row['event_type'],[],{'latest':row['last_event_id']})
        finally:db.close()
    store.set_setting('legacy_private_review',private_review)
    history=import_history(root,store,record,load,offline_db)
    configfile=target/'imported-config.json';configfile.write_text(json.dumps(configuration,ensure_ascii=False,indent=2));configfile.chmod(0o600)
    result={'schema':1,'complete':True,'legacy_stopped_asserted':True,'imported_actions':imported,
        'history':history,'private_pending_review':private_review,'config_file':'imported-config.json','activation_allowed':False,'reason':'capability parity review required',
        'at':time.time()}
    marker.write_text(json.dumps(result,indent=2));marker.chmod(0o600)
    return result
