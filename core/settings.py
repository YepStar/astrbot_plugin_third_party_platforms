"""Validated public global settings; account credentials and activation use separate APIs."""
from datetime import datetime
from zoneinfo import ZoneInfo
import re
from .configuration import number
from .planning import allowed_intervals

DEFAULTS={'platform_weights':{},'provider_id':'','model_ids':{},'public_persona':'','timezone':'Asia/Shanghai','windows':['10:00-11:00','20:00-21:00'],
 'rest_windows':[],'daily_rounds':2,'session_minutes':30,'daily_limit':20,'minute_limit':2,'share_min_score':8,'comment_min_score':8,
 'control_umos':[],'memory_enabled':False,'preference_half_life_days':14,'exploration_ratio':.15,
 'evaluation_rubric':'优先有具体内容、新意和可靠来源的作品，不因标题夸张或热度就给高分。','activity_level':55,
 'vision_policy':'when_text_insufficient','vision_frame_count':5,'vision_max_mb':96}
PHASES={'daily_plan','evaluation','platform_reply','video_frames','owner_share','public_comment','attribution_review','diagnostic'}

def public_settings(config):return {key:config.get(key,value) for key,value in DEFAULTS.items()}

def validate_settings(values,previous,providers=None):
 if not isinstance(values,dict) or values.keys()-DEFAULTS.keys():raise ValueError('invalid_global_fields')
 normalized=dict(values);combined={**public_settings(previous),**values}
 for key,maximum in [('provider_id',200),('public_persona',12000),('evaluation_rubric',6000),('timezone',80)]:
  if key in values and (not isinstance(values[key],str) or len(values[key])>maximum):raise ValueError('invalid_global_text')
 try:zone=ZoneInfo(combined['timezone'])
 except (ValueError,KeyError,TypeError):raise ValueError('invalid_timezone') from None
 for key,maximum in [('windows',32),('rest_windows',16),('control_umos',50)]:
  value=combined[key]
  if not isinstance(value,list) or len(value)>maximum or any(not isinstance(x,str) or len(x)>200 for x in value):raise ValueError('invalid_global_list')
 for route in combined['control_umos']:
  if not re.fullmatch(r'[^:]+:FriendMessage:\d+',route):raise ValueError('private_control_route_required')
 try:allowed_intervals(datetime.now(zone).date(),combined['windows'],combined['rest_windows'],combined['timezone'])
 except (ValueError,TypeError):raise ValueError('invalid_global_windows') from None
 for key,low,high,integer in [('daily_rounds',0,12,True),('session_minutes',1,180,True),('daily_limit',0,100000,True),('minute_limit',0,1000,True),
  ('activity_level',0,100,True),('share_min_score',1,10,False),('comment_min_score',1,10,False),
  ('preference_half_life_days',.1,365,False),('exploration_ratio',0,1,False),('vision_frame_count',1,12,True),('vision_max_mb',8,256,True)]:
  if key in values:
   try:normalized[key]=number(values[key],low,high,integer)
   except ValueError:raise ValueError('invalid_number:'+key) from None
 if 'platform_weights' in values:
  weights=values['platform_weights'];known=set(providers) if providers is not None else {'bilibili','xiaoheihe','netease'}|set(previous.get('platforms',{}))
  if not isinstance(weights,dict) or weights.keys()-known:raise ValueError('invalid_platform_weights')
  merged=dict(previous.get('platform_weights',{}))
  for pid,value in weights.items():
   if value is None:merged.pop(pid,None)
   else:
    try:merged[pid]=number(value,0,100)
    except ValueError:raise ValueError('invalid_platform_weights') from None
  normalized['platform_weights']=merged
 if 'memory_enabled' in values and type(values['memory_enabled'])is not bool:raise ValueError('invalid_memory_switch')
 if combined['vision_policy'] not in {'off','when_text_insufficient','always'}:raise ValueError('invalid_vision_policy')
 if 'provider_id' in values:normalized['provider_id']=values['provider_id'].strip()
 if 'model_ids' in values:
  models=values['model_ids']
  if not isinstance(models,dict) or models.keys()-PHASES or any(not isinstance(v,str) or len(v)>200 for v in models.values()):raise ValueError('invalid_phase_models')
  normalized['model_ids']={**previous.get('model_ids',{}),**{k:v.strip() for k,v in models.items()}}
 return normalized


def settings_error(error):
 code=str(error)
 if code.startswith('invalid_number:'):
  names={'daily_rounds':'每天计划轮数','session_minutes':'每轮参考时长','daily_limit':'每天行为上限','minute_limit':'每分钟行为上限','activity_level':'自主活动倾向','share_min_score':'分享评分','comment_min_score':'评论评分','exploration_ratio':'探索比例','preference_half_life_days':'偏好衰减周期','vision_frame_count':'采样画面数','vision_max_mb':'视频大小上限'}
  return names.get(code.split(':',1)[1],'数值配置')+'超出范围或格式不正确。'
 return {'invalid_platform_weights':'平台权重需为 0–100 的数字，留空表示自主规划；0 表示不自动安排该平台。','invalid_timezone':'时区不存在，例如可以填写 Asia/Shanghai。','invalid_global_windows':'时间窗请使用 HH:MM-HH:MM，每行一段，小时为 00–23。',
 'private_control_route_required':'日程管理权限仅支持私聊会话，例如 qq_bot:FriendMessage:123456。',
 'invalid_phase_models':'模型配置格式不正确，请选择已有模型。','invalid_global_fields':'包含不支持的全局配置项。启动与暂停请使用顶部按钮。',
 'invalid_vision_policy':'请选择列表中的画面分析策略。'}.get(code,'配置长度或格式不正确，请检查所填内容。')
