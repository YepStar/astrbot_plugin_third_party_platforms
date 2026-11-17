"""Additional migrated BiliBot controls, each bound to an active runtime consumer."""
SPECS={
 'dynamic_daily_count':('life','int',1,0,20),
 'mood_enabled':('life', 'bool', False, None, None),
 'activity_sync':('life', 'bool', False, None, None),
 'autonomous_dynamic_enabled':('life', 'bool', False, None, None),
 'dynamic_times':('life', 'int', 1, 0, 12),
 'dynamic_gap_days':('life', 'int', 1, 1, 30),
 'dynamic_topics':('life', 'list', [], None, None),
 'dynamic_instruction':('life', 'text', '', 0, 4000),
 'daily_summary_enabled':('life', 'bool', False, None, None),
 'daily_summary_hour':('life', 'int', 22, 0, 23),
 'daily_summary_mode':('life', 'text', 'archive', 0, 20),
 'daily_summary_umo':('life', 'text', '', 0, 200),
 'daily_summary_image':('life', 'bool', False, None, None),
 'daily_summary_instruction':('life', 'text', '', 0, 4000),
 'weekly_summary_enabled':('life', 'bool', False, None, None),
 'weekly_summary_day':('life', 'int', 6, 0, 6),
 'weekly_summary_mode':('life', 'text', 'archive', 0, 20),
 'weekly_summary_umo':('life', 'text', '', 0, 200),
 'weekly_summary_image':('life', 'bool', False, None, None),
 'weekly_summary_instruction':('life', 'text', '', 0, 4000),
 'summary_font':('life', 'text', '', 0, 500),
 'auto_block':('safety', 'bool', False, None, None),
 'private_auto_block':('safety', 'bool', False, None, None),
 'block_whitelist':('safety', 'list', [], None, None),
 'private_block_whitelist':('safety', 'list', [], None, None),
 'private_trusted_domains':('safety', 'list', ['bilibili.com', 'b23.tv'], None, None),
 'block_score':('safety', 'int', -30, -1000, -1),
 'block_negative_times':('safety', 'int', 5, 0, 100),
 'abuse_alert_mode':('safety', 'text', 'off', 0, 10),
 'abuse_alert_umo':('safety', 'text', '', 0, 200),
 'abuse_alert_threshold':('safety', 'int', -3, -5, -1),
 'video_direct_provider':('models', 'text', '', 0, 200),
 'video_direct_model':('vision', 'text', '', 0, 200),
 'video_direct_format':('vision', 'text', 'none', 0, 10),
 'video_direct_fps':('vision', 'int', 2, 1, 4),
 'image_model':('models', 'text', '', 0, 200),
 'image_model_name':('vision', 'text', '', 0, 200),
 'private_image_enabled':('vision', 'bool', False, None, None),
 'tools_enabled':('life', 'bool', True, None, None),
 'private_read_tools':('reply', 'bool', True, None, None),
 'private_tool_allowlist':('reply', 'list', ['bili_up_info', 'bili_video_search', 'bili_search_and_watch', 'get_up_info', 'search_bilibili', 'watch_video'], None, None),

 'cookie_auto_refresh':('network','bool',True,None,None),
 'cookie_check_hours':('network','int',6,1,24),
 'operational_alerts':('network','bool',False,None,None),
 'private_auto_watch':('reply','bool',False,None,None),
 'private_search_enabled':('reply','bool',False,None,None),
 'private_search_limit':('reply','int',2,1,3),
 'private_poll_seconds':('reply','int',60,30,3600),
 'private_idle_poll_seconds':('reply','int',300,60,3600),
 'private_active_window':('reply','int',600,60,3600),
 'prefilter_enabled':('browse','bool',False,None,None),
 'prefilter_max_rejects':('browse','int',4,0,10),
 'interest_window_days':('browse','int',14,1,90),
 'interest_search_enabled':('browse','bool',False,None,None),
 'search_query_instruction':('browse','text','',0,2000),
 'dynamic_watch_enabled':('browse','bool',False,None,None),
 'dynamic_special_only':('browse','bool',True,None,None),
 'dynamic_include_video':('browse','bool',False,None,None),
 'dynamic_daily_limit':('browse','int',3,0,30),
 'video_segment_minutes':('vision','int',0,0,60),
 'video_segment_max_count':('vision','int',3,1,6),

 'account_vision_policy':('vision','text','inherit',0,40),
 'vision_frame_count':('vision','int',0,0,12),
 'vision_max_mb':('vision','int',0,0,256),
 'browse_enabled':('browse','bool',True,None,None),
 'video_daily_limit':('browse','int',0,0,1000),
 'custom_proactive_instruction':('expression','text','',0,4000),
 'custom_recommend_instruction':('expression','text','',0,4000),
 'custom_reply_instruction':('reply','text','',0,4000),
 'custom_private_instruction':('reply','text','',0,4000),
 'interest_selection_prompt':('reply','text','',0,4000),
 'filter_low_value':('reply','bool',False,None,None),
 'filter_duplicate':('reply','bool',True,None,None),
 'filter_ads':('reply','bool',True,None,None),
 'context_enabled':('reply','bool',True,None,None),
 'context_max_chars':('reply','int',16000,500,32000),
 'private_interest_filter':('reply','bool',False,None,None),
 'private_max_age':('reply','int',3600,60,86400),
 'private_max_per_poll':('reply','int',20,1,100),
 'reply_model':('models','text','',0,200),
 'evaluation_model':('models','text','',0,200),
 'comment_model':('models','text','',0,200),
 'vision_model':('models','text','',0,200),
 'request_timeout_seconds':('network','int',20,5,120),
 'like_enabled':('interactions','bool',False,None,None),
 'like_min_score':('interactions','float',8,1,10),
 'coin_enabled':('interactions','bool',False,None,None),
 'coin_min_score':('interactions','float',9,1,10),
 'favorite_enabled':('interactions','bool',False,None,None),
 'favorite_min_score':('interactions','float',9,1,10),
 'follow_enabled':('interactions','bool',False,None,None),
 'follow_min_score':('interactions','float',9,1,10),
 'interaction_daily_limit':('interactions','int',2,0,100),
}
def normalize(values,previous):
 from .configuration import number
 out={}
 for key,(group,kind,default,low,high) in SPECS.items():
  value=values.get(key,previous.get(group,{}).get(key,default))
  if kind=='bool':
   if type(value)is not bool:raise ValueError('invalid_switch')
  elif kind=='list':
   if isinstance(value,str):value=[x.strip() for x in value.replace('，',',').split(',') if x.strip()]
   if not isinstance(value,list) or len(value)>100 or any(not isinstance(x,str) or len(x)>200 for x in value):raise ValueError('invalid_list_setting')
  elif kind in {'int','float'}:value=number(value,low,high,kind=='int')
  elif not isinstance(value,str) or len(value)>high:raise ValueError('invalid_text_setting')
  if key=='account_vision_policy' and value not in {'inherit','off','when_text_insufficient','always'}:raise ValueError('invalid_vision_policy')
  if key=='vision_max_mb' and value and value<8:raise ValueError('视频大小上限至少8MB，或填0沿用全局')
  if key in {'daily_summary_mode','weekly_summary_mode'} and value not in {'archive','qq','dynamic','both'}:raise ValueError('invalid_summary_mode')
  if key=='abuse_alert_mode' and value not in {'off','score','model'}:raise ValueError('invalid_abuse_alert_mode')
  if key=='video_direct_format' and value not in {'none','qwen','gemini'}:raise ValueError('invalid_direct_format')
  if key in {'daily_summary_umo','weekly_summary_umo','abuse_alert_umo'} and value:
   import re
   if not re.fullmatch(r'[^:]+:FriendMessage:\d+',value):raise ValueError('private_recipient_required')
  if key in {'block_whitelist','private_block_whitelist'} and any(not x.isdigit() for x in value):raise ValueError('invalid_protected_uid')
  if key=='private_trusted_domains':
   import re
   if any(not re.fullmatch(r'[A-Za-z0-9.-]+\.[A-Za-z]{2,24}',x) for x in value):raise ValueError('invalid_trusted_domain')
  out.setdefault(group,{})[key]=value
 return out
