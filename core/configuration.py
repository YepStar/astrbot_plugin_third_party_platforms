"""Account policy is public state; login credentials are never accepted here."""
import math,re
PROVIDERS={'bilibili','xiaoheihe','netease'}
FIELDS={'fallback_sources','browse_count','share_gap_seconds','dry_run','max_reply_chars','poll_mentions','poll_replies','pools','follow_uids','topic_ids','special_follow_enabled','owner_bili_name','share_delivery','enabled','owner_umo','topic_id','query','share_enabled','share_min_score','reply_enabled','private_reply_enabled',
 'comment_enabled','comment_min_score','dynamic_enabled','listen_enabled','self_uid','owner_uid','whitelist_mode',
 'user_whitelist','user_blacklist','author_whitelist','author_blacklist','keyword_blacklist','poll_seconds','max_age_seconds',
 'only_explicit_mentions','reply_to_direct_replies','daily_browse_limit','daily_share_limit','daily_reply_limit','daily_comment_limit','daily_private_reply_limit','daily_dynamic_limit','private_scope','private_whitelist','cooldown_seconds','probability_percent','interest_filter','similar_skip','similarity_percent','always_reply_uids'}

def number(value,low,high,integer=False):
 if type(value) not in (int,float) or not math.isfinite(value) or not low<=value<=high or (integer and int(value)!=value):raise ValueError('invalid_numeric_setting')
 return int(value) if integer else float(value)
def flag(values,key,default=False):
 value=values.get(key,default)
 if type(value)is not bool:raise ValueError('invalid_switch')
 return value
def text(values,key,maximum=200):
 value=values.get(key,'')
 if not isinstance(value,str) or len(value)>maximum:raise ValueError('invalid_text_setting')
 return value.strip()
def names(values,key):
 value=values.get(key,[])
 if isinstance(value,str):value=[x.strip() for x in value.replace('，',',').split(',') if x.strip()]
 if not isinstance(value,list) or len(value)>200 or any(not isinstance(x,str) or len(x)>100 for x in value):raise ValueError('invalid_list_setting')
 return value

from .advanced import SPECS,normalize
FIELDS.update(SPECS)

def account(provider,values,previous=None,*,capabilities=None):
 if (provider not in PROVIDERS and capabilities is None) or not isinstance(values,dict) or values.keys()-FIELDS:raise ValueError('invalid_account_fields')
 previous=previous or {}
 inherited={**previous,**previous.get('reply',{}),**previous.get('browse',{})}
 for field,kind in [('share_enabled','owner_share'),('reply_enabled','reply'),('private_reply_enabled','private_reply'),('comment_enabled','comment'),('dynamic_enabled','dynamic'),('listen_enabled','listen')]:
  if kind in previous.get('actions',{}):inherited[field]=previous['actions'][kind]
 for field,kind in [('daily_browse_limit','browse'),('daily_share_limit','owner_share'),('daily_reply_limit','reply'),('daily_private_reply_limit','private_reply'),('daily_comment_limit','comment'),('daily_dynamic_limit','dynamic')]:
  if kind in previous.get('daily_limits',{}):inherited[field]=previous['daily_limits'][kind]
 values={**{k:v for k,v in inherited.items() if k in FIELDS},**values}
 umo=text(values,'owner_umo')
 if umo and not re.fullmatch(r'[^:]+:FriendMessage:\d+',umo):raise ValueError('invalid_owner_private_route')
 actions={'owner_share':flag(values,'share_enabled'),'reply':flag(values,'reply_enabled'),
  'private_reply':flag(values,'private_reply_enabled'),'comment':flag(values,'comment_enabled'),
  'dynamic':flag(values,'dynamic_enabled'),'listen':flag(values,'listen_enabled')}
 allowed=set(capabilities) if capabilities is not None else ({'reply','private_reply','comment','dynamic','owner_share'} if provider=='bilibili' else {'reply','comment','owner_share'} if provider=='xiaoheihe' else {'listen'})
 if any(enabled and kind not in allowed for kind,enabled in actions.items()):raise ValueError('unsupported_platform_action')
 if provider=='netease' and any(actions[k] for k in ['reply','comment','owner_share']):raise ValueError('music_actions_stay_in_music_plugin')
 result={**previous,'enabled':flag(values,'enabled'),'owner_umo':umo,'actions':actions,
  'share_delivery':values.get('share_delivery',previous.get('share_delivery','qq_private')),
  'owner_bili_name':text(values,'owner_bili_name',80),
  'self_uid':text(values,'self_uid',80),'owner_uid':text(values,'owner_uid',80),
  'share_gap_seconds':number(values.get('share_gap_seconds',7200),0,86400,True),
  'share_min_score':number(values.get('share_min_score',8),1,10),
  'comment_min_score':number(values.get('comment_min_score',8),1,10),
  'daily_limits':{'browse':number(values.get('daily_browse_limit',2),0,100,True),
    'owner_share':number(values.get('daily_share_limit',1),0,100,True),
    'reply':number(values.get('daily_reply_limit',20),0,1000,True),
    'private_reply':number(values.get('daily_private_reply_limit',20),0,1000,True),
    'comment':number(values.get('daily_comment_limit',2),0,100,True),'listen':number(values.get('daily_browse_limit',2),0,100,True),
    'dynamic':number(values.get('daily_dynamic_limit',1),0,20,True)},
  'browse':{**previous.get('browse',{}),'count':number(values.get('browse_count',previous.get('browse',{}).get('count',2)),1,10,True),'fallback_sources':names(values,'fallback_sources') if 'fallback_sources' in values else previous.get('browse',{}).get('fallback_sources',['all']),'query':text(values,'query'),'topic_id':text(values,'topic_id',80),
    **{key:names(values,key) if key in values else previous.get('browse',{}).get(key,default) for key,default in [('pools',['popular']),('follow_uids',[]),('topic_ids',[])]},
    'special_follow_enabled':flag(values,'special_follow_enabled',previous.get('browse',{}).get('special_follow_enabled',False))},
  'reply':{**previous.get('reply',{}),'dry_run':flag(values,'dry_run'),
    'poll_mentions':flag(values,'poll_mentions',True),'poll_replies':flag(values,'poll_replies',True),
    'max_reply_chars':number(values.get('max_reply_chars',300 if provider=='xiaoheihe' else 1000),1,1000,True),
    'private_scope':values.get('private_scope','owner'),
    'private_whitelist':names(values,'private_whitelist'),'always_reply_uids':names(values,'always_reply_uids'),
    'cooldown_seconds':number(values.get('cooldown_seconds',60),0,3600,True),
    'probability_percent':number(values.get('probability_percent',100),0,100,True),
    'interest_filter':flag(values,'interest_filter'),'similar_skip':flag(values,'similar_skip'),
    'similarity_percent':number(values.get('similarity_percent',85),0,100,True),
    'whitelist_mode':flag(values,'whitelist_mode'),'only_explicit_mentions':flag(values,'only_explicit_mentions',True),
    'reply_to_direct_replies':flag(values,'reply_to_direct_replies',True),
    'poll_seconds':number(values.get('poll_seconds',180),60,3600,True),
    'max_age_seconds':number(values.get('max_age_seconds',3600),60,86400,True),
    **{key:names(values,key) for key in ['user_whitelist','user_blacklist','author_whitelist','author_blacklist','keyword_blacklist']}}}
 for group,extra in normalize(values,previous).items():result[group]={**result.get(group,{}),**extra}
 if provider!='bilibili' and any(result['interactions'].get(k+'_enabled') for k in ('like','coin','favorite','follow')):raise ValueError('unsupported_platform_action')
 if result['share_delivery'] not in {'qq_private','private_message','comment','both','bili_private_and_qq','all','auto','off'}:raise ValueError('invalid_share_delivery')
 if provider!='bilibili' and result['share_delivery'] not in {'qq_private','off'}:raise ValueError('unsupported_share_delivery')
 if provider=='xiaoheihe':
  from ..providers.xhh_client.source_categories import SECTION_ALIASES
  sources=result['browse']['fallback_sources']
  if not sources or len(sources)!=len(set(sources)) or set(sources)-SECTION_ALIASES.keys() or ('all' in sources and len(sources)>1):raise ValueError('回退分类需至少选择一项；全部不能与其他分类同时选择')
  if len(result['browse']['topic_ids'])>20:raise ValueError('真实分区最多选择20项')
 if len(result['browse']['pools'])>8 or not result['browse']['pools']:raise ValueError('invalid_video_pools')
 for key in ['follow_uids','topic_ids']:
  if any(not str(uid).isdigit() for uid in result['browse'][key]):raise ValueError('invalid_platform_identifier')
 if result['reply']['private_scope'] not in {'owner','whitelist','all'}:raise ValueError('invalid_private_scope')
 return result
