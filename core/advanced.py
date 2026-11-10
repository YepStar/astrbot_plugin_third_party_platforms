"""Additional migrated BiliBot controls, each bound to an active runtime consumer."""
SPECS={
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
  elif kind in {'int','float'}:value=number(value,low,high,kind=='int')
  elif not isinstance(value,str) or len(value)>high:raise ValueError('invalid_text_setting')
  if key=='account_vision_policy' and value not in {'inherit','off','when_text_insufficient','always'}:raise ValueError('invalid_vision_policy')
  if key=='vision_max_mb' and value and value<8:raise ValueError('视频大小上限至少8MB，或填0沿用全局')
  out.setdefault(group,{})[key]=value
 return out
