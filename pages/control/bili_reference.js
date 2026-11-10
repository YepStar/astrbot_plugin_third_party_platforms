// Original schema descriptions: BiliBot by chenluQwQ, MIT. No runtime values.
export const biliReference=[
  {
    "key": "COOKIE_AUTO_REFRESH",
    "description": "【系统】Cookie过期自动刷新",
    "kind": "bool",
    "status": "pending",
    "target": ""
  },
  {
    "key": "COOKIE_CHECK_INTERVAL",
    "description": "【系统】Cookie检查间隔（小时）",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "OWNER_MID",
    "description": "【账号】主人的B站UID（好感度与私信推荐）",
    "kind": "string",
    "status": "ported",
    "target": "主人 UID"
  },
  {
    "key": "OWNER_NAME",
    "description": "【账号】主人名称（用于提示词）",
    "kind": "string",
    "status": "pending",
    "target": ""
  },
  {
    "key": "OWNER_BILI_NAME",
    "description": "【账号】主人的B站昵称（用于评论区@推荐）",
    "kind": "string",
    "status": "ported",
    "target": "主人 B站昵称"
  },
  {
    "key": "OWNER_QQ_UMO",
    "description": "【跨端活动与分享】主人 QQ 私聊 UMO",
    "kind": "string",
    "status": "ported",
    "target": "主人私聊会话"
  },
  {
    "key": "LLM_PROVIDER_ID",
    "description": "【人设】选择用于回复/记忆压缩的LLM（留空用AstrBot默认）",
    "kind": "string",
    "status": "ported",
    "target": "reply_model"
  },
  {
    "key": "USE_ASTRBOT_PERSONA",
    "description": "【人设】使用AstrBot自带人设",
    "kind": "bool",
    "status": "pending",
    "target": ""
  },
  {
    "key": "CUSTOM_SYSTEM_PROMPT",
    "description": "【人设】B站活动附加系统提示词",
    "kind": "text",
    "status": "shared",
    "target": "全局公共人格"
  },
  {
    "key": "LLM_CIRCUIT_FAILURE_THRESHOLD",
    "description": "【模型可靠性】连续失败多少次后暂停调用",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "LLM_CIRCUIT_COOLDOWN_SECONDS",
    "description": "【模型可靠性】熔断冷却时间（秒）",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "SUMMARY_PROVIDER_ID",
    "description": "【总结模型】选择 AstrBot 模型提供商",
    "kind": "string",
    "status": "ported",
    "target": "evaluation_model"
  },
  {
    "key": "SUMMARY_MODEL",
    "description": "【总结模型】独立 API 模型名",
    "kind": "string",
    "status": "pending",
    "target": ""
  },
  {
    "key": "GENERATION_PROVIDER_ID",
    "description": "【生成模型】选择 AstrBot 模型提供商",
    "kind": "string",
    "status": "ported",
    "target": "comment_model"
  },
  {
    "key": "GENERATION_MODEL",
    "description": "【生成模型】独立 API 模型名",
    "kind": "string",
    "status": "pending",
    "target": ""
  },
  {
    "key": "ENABLE_REPLY",
    "description": "【功能开关】启用评论自动回复",
    "kind": "bool",
    "status": "ported",
    "target": "回复与权限"
  },
  {
    "key": "POLL_INTERVAL",
    "description": "【回复】评论轮询间隔（秒）",
    "kind": "int",
    "status": "ported",
    "target": "回复轮询"
  },
  {
    "key": "REPLY_COOLDOWN",
    "description": "【回复】回复冷却时间（秒，回复一条后等待多久再处理下一条，最低5秒）",
    "kind": "int",
    "status": "ported",
    "target": "回复冷却"
  },
  {
    "key": "REPLY_PROBABILITY_PERCENT",
    "description": "【回复】回复概率（%）",
    "kind": "int",
    "status": "ported",
    "target": "回复概率"
  },
  {
    "key": "REPLY_ALWAYS_UIDS",
    "description": "【回复】必回UID白名单",
    "kind": "list",
    "status": "ported",
    "target": "必回名单"
  },
  {
    "key": "ENABLE_INTEREST_BASED_REPLY",
    "description": "【回复筛选】让 Bot 只挑选自己感兴趣且值得回应的内容",
    "kind": "bool",
    "status": "ported",
    "target": "兴趣选择"
  },
  {
    "key": "INTEREST_SELECTION_PROMPT",
    "description": "【回复筛选】兴趣选择提示词",
    "kind": "text",
    "status": "ported",
    "target": "interest_selection_prompt"
  },
  {
    "key": "FILTER_LOW_VALUE_MESSAGES",
    "description": "【回复筛选】过滤无意义或信息量过低的消息",
    "kind": "bool",
    "status": "ported",
    "target": "filter_low_value"
  },
  {
    "key": "FILTER_DUPLICATE_MESSAGES",
    "description": "【回复筛选】过滤近期完全重复的消息",
    "kind": "bool",
    "status": "ported",
    "target": "filter_duplicate"
  },
  {
    "key": "FILTER_AD_MESSAGES",
    "description": "【回复筛选】过滤广告、引流和联系方式轰炸",
    "kind": "bool",
    "status": "ported",
    "target": "filter_ads"
  },
  {
    "key": "ENABLE_SIMILAR_SKIP",
    "description": "【回复】启用语义相似去重（相似评论不重复回复）",
    "kind": "bool",
    "status": "ported",
    "target": "相似消息过滤"
  },
  {
    "key": "REPLY_SIMILARITY_PERCENT",
    "description": "【回复】语义相似度阈值（%）",
    "kind": "int",
    "status": "ported",
    "target": "相似度门槛"
  },
  {
    "key": "CUSTOM_REPLY_INSTRUCTION",
    "description": "【回复】回复评论的补充提示词（追加到回复提示词末尾，留空用默认）",
    "kind": "text",
    "status": "ported",
    "target": "custom_reply_instruction"
  },
  {
    "key": "COMMENT_CONTEXT_ENABLED",
    "description": "【回复】自主查询总开关",
    "kind": "bool",
    "status": "ported",
    "target": "context_enabled"
  },
  {
    "key": "COMMENT_CONTEXT_MAX_CALLS",
    "description": "【回复】每条评论最多查询次数",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "ENABLE_PRIVATE_MESSAGES",
    "description": "【B站私信·总开关】监听新私信",
    "kind": "bool",
    "status": "ported",
    "target": "B站私信"
  },
  {
    "key": "PRIVATE_MESSAGE_REPLY_SCOPE",
    "description": "【B站私信·回复】允许自动回复哪些人",
    "kind": "string",
    "status": "ported",
    "target": "私信范围"
  },
  {
    "key": "PRIVATE_MESSAGE_REPLY_WHITELIST_UIDS",
    "description": "【B站私信·回复】允许回复的额外UID白名单",
    "kind": "list",
    "status": "ported",
    "target": "私信白名单"
  },
  {
    "key": "PRIVATE_MESSAGE_AUTO_REPLY",
    "description": "【B站私信·回复】自动回复安全私信",
    "kind": "bool",
    "status": "ported",
    "target": "私信回复"
  },
  {
    "key": "PRIVATE_MESSAGE_POLL_INTERVAL",
    "description": "【B站私信·监听】活跃期检查间隔（秒）",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "PRIVATE_MESSAGE_IDLE_POLL_INTERVAL",
    "description": "【B站私信·监听】空闲期检查间隔（秒）",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "PRIVATE_MESSAGE_ACTIVE_WINDOW",
    "description": "【B站私信·监听】收到消息后保持活跃多久（秒）",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "PRIVATE_MESSAGE_MAX_PER_POLL",
    "description": "【B站私信·回复】每轮最多处理几条",
    "kind": "int",
    "status": "ported",
    "target": "private_max_per_poll"
  },
  {
    "key": "PRIVATE_MESSAGE_MAX_MESSAGE_AGE",
    "description": "【B站私信·回复】只处理多少秒内的新消息",
    "kind": "int",
    "status": "ported",
    "target": "private_max_age"
  },
  {
    "key": "INTEREST_APPLY_TO_PRIVATE",
    "description": "【回复筛选】私信也使用兴趣选择",
    "kind": "bool",
    "status": "ported",
    "target": "private_interest_filter"
  },
  {
    "key": "PRIVATE_MESSAGE_AUTO_WATCH_VIDEO",
    "description": "【B站私信·视频】收到视频分享后先看完再回复",
    "kind": "bool",
    "status": "pending",
    "target": ""
  },
  {
    "key": "PRIVATE_MESSAGE_BILI_SEARCH_ENABLED",
    "description": "【B站私信·查询】允许按私信要求搜索视频和UP主",
    "kind": "bool",
    "status": "pending",
    "target": ""
  },
  {
    "key": "PRIVATE_MESSAGE_BILI_SEARCH_LIMIT",
    "description": "【B站私信·查询】每次最多返回几个搜索结果",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "BILI_PRIVATE_SHARE_TOOL_ENABLED",
    "description": "【B站私信·分享】允许 Bot 看完视频后私信给主人",
    "kind": "bool",
    "status": "pending",
    "target": ""
  },
  {
    "key": "BILI_PRIVATE_SHARE_COOLDOWN",
    "description": "【B站私信·分享】同一视频重复分享冷却秒数",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "CUSTOM_PRIVATE_MESSAGE_INSTRUCTION",
    "description": "【B站私信·回复】私信回复补充提示词",
    "kind": "text",
    "status": "ported",
    "target": "custom_private_instruction"
  },
  {
    "key": "PRIVATE_MESSAGE_AUTO_BLOCK",
    "description": "【B站私信·安全】危险私信自动拉黑",
    "kind": "bool",
    "status": "pending",
    "target": ""
  },
  {
    "key": "PRIVATE_MESSAGE_BLOCK_WHITELIST_UIDS",
    "description": "【B站私信·安全】永不因私信自动拉黑的UID",
    "kind": "list",
    "status": "pending",
    "target": ""
  },
  {
    "key": "PRIVATE_MESSAGE_TRUSTED_DOMAINS",
    "description": "【B站私信·安全】允许出现的链接域名",
    "kind": "list",
    "status": "pending",
    "target": ""
  },
  {
    "key": "ENABLE_LIVE_DANMAKU_REPLY",
    "description": "【直播互动·总开关】进入指定直播间参与弹幕互动",
    "kind": "bool",
    "status": "pending",
    "target": ""
  },
  {
    "key": "LIVE_DANMAKU_ROOM_ID",
    "description": "【直播互动】参与互动的B站直播间号",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "LIVE_DANMAKU_POLL_INTERVAL",
    "description": "【直播互动】检查新弹幕间隔（秒）",
    "kind": "float",
    "status": "pending",
    "target": ""
  },
  {
    "key": "LIVE_DANMAKU_REPLY_COOLDOWN",
    "description": "【直播互动】两次发送弹幕最短间隔（秒）",
    "kind": "float",
    "status": "pending",
    "target": ""
  },
  {
    "key": "LIVE_DANMAKU_MAX_PER_MINUTE",
    "description": "【直播互动】每分钟最多发送弹幕次数",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "LIVE_DANMAKU_REPLY_MAX_LENGTH",
    "description": "【直播互动】单次回应最大总字数",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "CUSTOM_LIVE_DANMAKU_INSTRUCTION",
    "description": "【直播互动】弹幕互动补充提示词",
    "kind": "text",
    "status": "pending",
    "target": ""
  },
  {
    "key": "ENABLE_BILI_SHARE_PARSE",
    "description": "【分享解析·总开关】识别群聊和私聊里的B站视频分享",
    "kind": "bool",
    "status": "pending",
    "target": ""
  },
  {
    "key": "BILI_SHARE_PARSE_AUTO_TRIGGER_ENABLED",
    "description": "【分享解析·触发】自动识别聊天中的B站视频",
    "kind": "bool",
    "status": "pending",
    "target": ""
  },
  {
    "key": "BILI_SHARE_PARSE_MANUAL_TRIGGER_ENABLED",
    "description": "【分享解析·触发】允许 /bili解析 手动触发",
    "kind": "bool",
    "status": "pending",
    "target": ""
  },
  {
    "key": "BILI_SHARE_PARSE_LLM_TRIGGER_ENABLED",
    "description": "【分享解析·触发】允许 LLM 工具触发",
    "kind": "bool",
    "status": "pending",
    "target": ""
  },
  {
    "key": "BILI_SHARE_PENDING_MAX_AGE",
    "description": "【分享解析】上一个待解析视频保留秒数",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "BILI_SHARE_PARSE_SEND_VIDEO",
    "description": "【分享解析】解析后发送原视频/切片",
    "kind": "bool",
    "status": "pending",
    "target": ""
  },
  {
    "key": "BILI_SHARE_PARSE_SEGMENT_SECONDS",
    "description": "【分享解析】原视频切片秒数",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "BILI_SHARE_PARSE_MAX_SEGMENTS",
    "description": "【分享解析】每次最多发送几个切片",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "BILI_SHARE_PARSE_MAX_VIDEO_MB",
    "description": "【分享解析】单个视频文件大小阈值MB",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "BILI_SHARE_PARSE_VIDEO_MAX_HEIGHT",
    "description": "【分享解析】原视频下载最高分辨率",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "BILI_SHARE_PARSE_COOLDOWN",
    "description": "【分享解析】同一视频重复解析冷却秒数",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "ENABLE_AFFECTION",
    "description": "【功能开关】启用好感度系统",
    "kind": "bool",
    "status": "pending",
    "target": ""
  },
  {
    "key": "ENABLE_MOOD",
    "description": "【功能开关】启用心情系统",
    "kind": "bool",
    "status": "pending",
    "target": ""
  },
  {
    "key": "AFFECTION_PROMPT_SPECIAL",
    "description": "【好感度提示词】主人（固定100分）",
    "kind": "text",
    "status": "pending",
    "target": ""
  },
  {
    "key": "AFFECTION_PROMPT_CLOSE",
    "description": "【好感度提示词】亲密（80-99分）",
    "kind": "text",
    "status": "pending",
    "target": ""
  },
  {
    "key": "AFFECTION_PROMPT_FRIEND",
    "description": "【好感度提示词】熟悉（50-79分）",
    "kind": "text",
    "status": "pending",
    "target": ""
  },
  {
    "key": "AFFECTION_PROMPT_NORMAL",
    "description": "【好感度提示词】普通（10-49分）",
    "kind": "text",
    "status": "pending",
    "target": ""
  },
  {
    "key": "AFFECTION_PROMPT_STRANGER",
    "description": "【好感度提示词】陌生（0-9分）",
    "kind": "text",
    "status": "pending",
    "target": ""
  },
  {
    "key": "AFFECTION_PROMPT_COLD",
    "description": "【好感度提示词】冷淡（负分）",
    "kind": "text",
    "status": "pending",
    "target": ""
  },
  {
    "key": "VIDEO_VISUAL_ANALYSIS_POLICY",
    "description": "【视频分析】视觉分析策略",
    "kind": "string",
    "status": "ported",
    "target": "抽帧策略"
  },
  {
    "key": "VIDEO_SEGMENT_MINUTES",
    "description": "【视频分析】长视频自动切片长度（分钟/段）",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "VIDEO_SEGMENT_MAX_COUNT",
    "description": "【视频分析】长视频最多分析多少段",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "ENABLE_PROACTIVE",
    "description": "【主动看片·总开关】启用主动看视频与互动",
    "kind": "bool",
    "status": "ported",
    "target": "browse_enabled"
  },
  {
    "key": "PROACTIVE_TIMES_COUNT",
    "description": "【主动看片·数量】每天最多安排几轮浏览",
    "kind": "int",
    "status": "shared",
    "target": "全局每天最多计划轮数"
  },
  {
    "key": "PROACTIVE_VIDEO_COUNT",
    "description": "【主动看片·数量】每次计划观看几个视频",
    "kind": "int",
    "status": "ported",
    "target": "browse_count"
  },
  {
    "key": "PROACTIVE_DAILY_LIMIT",
    "description": "【主动看片·数量】每天最多看几个视频（所有来源合计，0=不限制）",
    "kind": "int",
    "status": "ported",
    "target": "video_daily_limit"
  },
  {
    "key": "PROACTIVE_COMMENT_COUNT",
    "description": "【主动看片·数量】每个视频最多主动评论几条",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "PROACTIVE_COMMENT_DAILY_LIMIT",
    "description": "【主动看片·数量】每天最多主动评论几条",
    "kind": "int",
    "status": "ported",
    "target": "评论配额"
  },
  {
    "key": "PROACTIVE_FOLLOW_UIDS",
    "description": "【主动看片·来源1】特别关注的UP主UID列表",
    "kind": "list",
    "status": "ported",
    "target": "特别关注 UID"
  },
  {
    "key": "PROACTIVE_SEARCH_QUERY_PROMPT",
    "description": "【主动看片·来源2】Bot 决定B站搜索词的提示词",
    "kind": "text",
    "status": "pending",
    "target": ""
  },
  {
    "key": "PROACTIVE_TASTE_WINDOW_DAYS",
    "description": "【主动看片·来源2】分区评分口味统计天数",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "PROACTIVE_PREFERENCE_HALF_LIFE_DAYS",
    "description": "【主动行为】近期爱好证据半衰期（天）",
    "kind": "int",
    "status": "shared",
    "target": "全局偏好衰减"
  },
  {
    "key": "PROACTIVE_EXPLORATION_RATIO",
    "description": "【主动行为】新题材探索比例",
    "kind": "float",
    "status": "shared",
    "target": "全局探索比例"
  },
  {
    "key": "PROACTIVE_VIDEO_POOLS",
    "description": "【主动看片·来源3】视频池/地址池（可填中文，不用记 rid/tid）",
    "kind": "list",
    "status": "ported",
    "target": "视频来源"
  },
  {
    "key": "ENABLE_PROACTIVE_LLM_PREFILTER",
    "description": "【主动看片·筛选】观看前让 LLM 按标题筛选搜索/视频池候选",
    "kind": "bool",
    "status": "pending",
    "target": ""
  },
  {
    "key": "PROACTIVE_LLM_PREFILTER_MAX_REJECTS",
    "description": "【主动看片·筛选】每轮最多拒绝几个候选",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "PROACTIVE_LIKE",
    "description": "【主动行为】主动点赞",
    "kind": "bool",
    "status": "ported",
    "target": "like_enabled"
  },
  {
    "key": "PROACTIVE_LIKE_MIN_SCORE",
    "description": "【主动行为】点赞最低评分",
    "kind": "int",
    "status": "ported",
    "target": "like_min_score"
  },
  {
    "key": "PROACTIVE_COIN",
    "description": "【主动行为】主动投币",
    "kind": "bool",
    "status": "ported",
    "target": "coin_enabled"
  },
  {
    "key": "PROACTIVE_COIN_MIN_SCORE",
    "description": "【主动行为】投币最低评分",
    "kind": "int",
    "status": "ported",
    "target": "coin_min_score"
  },
  {
    "key": "PROACTIVE_FAV",
    "description": "【主动行为】主动收藏",
    "kind": "bool",
    "status": "ported",
    "target": "favorite_enabled"
  },
  {
    "key": "PROACTIVE_FAV_MIN_SCORE",
    "description": "【主动行为】收藏最低评分",
    "kind": "int",
    "status": "ported",
    "target": "favorite_min_score"
  },
  {
    "key": "PROACTIVE_COMMENT",
    "description": "【主动行为】主动评论",
    "kind": "bool",
    "status": "ported",
    "target": "公开评论"
  },
  {
    "key": "PROACTIVE_COMMENT_MIN_SCORE",
    "description": "【主动行为】评论最低评分",
    "kind": "int",
    "status": "ported",
    "target": "评论评分"
  },
  {
    "key": "PROACTIVE_FOLLOW",
    "description": "【主动行为】主动关注UP主",
    "kind": "bool",
    "status": "ported",
    "target": "follow_enabled"
  },
  {
    "key": "PROACTIVE_FOLLOW_MIN_SCORE",
    "description": "【主动行为】关注UP主最低评分",
    "kind": "int",
    "status": "ported",
    "target": "follow_min_score"
  },
  {
    "key": "CUSTOM_PROACTIVE_INSTRUCTION",
    "description": "【主动行为】主动评论的补充提示词",
    "kind": "text",
    "status": "ported",
    "target": "custom_proactive_instruction"
  },
  {
    "key": "ENABLE_OWNER_RECOMMEND",
    "description": "【主动行为·给主人推荐】启用给主人分享",
    "kind": "bool",
    "status": "ported",
    "target": "内容分享"
  },
  {
    "key": "RECOMMEND_OWNER_DELIVERY",
    "description": "【主动行为·给主人推荐】发送方式（B站 / QQ）",
    "kind": "string",
    "status": "ported",
    "target": "分享渠道"
  },
  {
    "key": "RECOMMEND_OWNER_MIN_SCORE",
    "description": "【主动行为·给主人推荐】最低个人喜好评分",
    "kind": "float",
    "status": "ported",
    "target": "分享评分"
  },
  {
    "key": "RECOMMEND_OWNER_DAILY_LIMIT",
    "description": "【主动行为·给主人推荐】每天最多发送几次",
    "kind": "int",
    "status": "ported",
    "target": "分享配额"
  },
  {
    "key": "RECOMMEND_OWNER_MIN_GAP_MINUTES",
    "description": "【主动行为·给主人推荐】两次推荐至少间隔（分钟）",
    "kind": "int",
    "status": "ported",
    "target": "分享间隔"
  },
  {
    "key": "CUSTOM_RECOMMEND_INSTRUCTION",
    "description": "【主动行为·给主人推荐】推荐语补充提示词",
    "kind": "text",
    "status": "ported",
    "target": "custom_recommend_instruction"
  },
  {
    "key": "ENABLE_CROSS_PLATFORM_ACTIVITY_STATUS",
    "description": "【跨端活动与分享】向已绑定主人同步当前活动",
    "kind": "bool",
    "status": "pending",
    "target": ""
  },
  {
    "key": "SPECIAL_FOLLOW_ENABLED",
    "description": "【特别关注】启用定时特关巡视（独立于主动刷视频）",
    "kind": "bool",
    "status": "ported",
    "target": "浏览特别关注"
  },
  {
    "key": "SPECIAL_FOLLOW_MODE",
    "description": "【特别关注】触发模式",
    "kind": "string",
    "status": "pending",
    "target": ""
  },
  {
    "key": "SPECIAL_FOLLOW_TIMES_COUNT",
    "description": "【特别关注】每天巡视几次（random模式生效）",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "SPECIAL_FOLLOW_FIXED_TIMES",
    "description": "【特别关注】固定触发时间（fixed模式生效）",
    "kind": "list",
    "status": "pending",
    "target": ""
  },
  {
    "key": "ENABLE_BANGUMI",
    "description": "【番剧】启用番剧功能（看番、搜番、番剧记忆）",
    "kind": "bool",
    "status": "pending",
    "target": ""
  },
  {
    "key": "BANGUMI_PROACTIVE",
    "description": "【番剧】启用主动看番（定时自动随机看番）",
    "kind": "bool",
    "status": "pending",
    "target": ""
  },
  {
    "key": "BANGUMI_POOLS",
    "description": "【番剧】番剧来源池",
    "kind": "list",
    "status": "pending",
    "target": ""
  },
  {
    "key": "BANGUMI_EPISODE_COUNT",
    "description": "【番剧】每次看番最多追更几集",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "BANGUMI_CONTINUE_SCORE",
    "description": "【番剧】追更阈值（评分≥此值才继续看下一集）",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "BANGUMI_DAILY_LIMIT",
    "description": "【番剧】每天主动看番的次数上限",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "BANGUMI_COMMENT",
    "description": "【番剧】看番时评论（≥6分）",
    "kind": "bool",
    "status": "pending",
    "target": ""
  },
  {
    "key": "BANGUMI_AUTO_FOLLOW",
    "description": "【番剧】评分≥7时自动追番",
    "kind": "bool",
    "status": "pending",
    "target": ""
  },
  {
    "key": "ENABLE_DYNAMIC_WATCH",
    "description": "【关注动态巡视·总开关】查看关注者的新动态图文",
    "kind": "bool",
    "status": "pending",
    "target": ""
  },
  {
    "key": "DYNAMIC_WATCH_TIMES_COUNT",
    "description": "【关注动态巡视】自主计划每日最多巡视次数",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "DYNAMIC_WATCH_DAILY_LIMIT",
    "description": "【关注动态巡视】每天最多查看新动态数",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "DYNAMIC_WATCH_SPECIAL_ONLY",
    "description": "【关注动态巡视】只查看特别关注用户",
    "kind": "bool",
    "status": "pending",
    "target": ""
  },
  {
    "key": "DYNAMIC_WATCH_INCLUDE_VIDEO_POSTS",
    "description": "【关注动态巡视】同时查看视频投稿动态",
    "kind": "bool",
    "status": "pending",
    "target": ""
  },
  {
    "key": "DYNAMIC_WATCH_INTEREST_PROMPT",
    "description": "【关注动态巡视】兴趣判断补充提示词",
    "kind": "text",
    "status": "pending",
    "target": ""
  },
  {
    "key": "ENABLE_DYNAMIC",
    "description": "【功能开关】启用自动发动态",
    "kind": "bool",
    "status": "ported",
    "target": "文字动态权限"
  },
  {
    "key": "DYNAMIC_TIMES_COUNT",
    "description": "【动态发布】每天触发几次动态发布",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "DYNAMIC_DAILY_COUNT",
    "description": "【动态发布】每天最多发几条动态",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "DYNAMIC_MIN_INTERVAL_DAYS",
    "description": "【动态】自动动态最短间隔（天）",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "DYNAMIC_TOPICS",
    "description": "【动态发布】动态主题池（每行一个）",
    "kind": "list",
    "status": "pending",
    "target": ""
  },
  {
    "key": "CUSTOM_DYNAMIC_INSTRUCTION",
    "description": "【动态发布】发动态的补充提示词",
    "kind": "text",
    "status": "pending",
    "target": ""
  },
  {
    "key": "ENABLE_DAILY_SUMMARY",
    "description": "【总结·日总结】启用每日总结",
    "kind": "bool",
    "status": "pending",
    "target": ""
  },
  {
    "key": "DAILY_SUMMARY_HOUR",
    "description": "【总结·日总结】生成时间（0-23点）",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "DAILY_SUMMARY_MODE",
    "description": "【总结·日总结】投递方式",
    "kind": "string",
    "status": "pending",
    "target": ""
  },
  {
    "key": "DAILY_SUMMARY_QQ_UMO",
    "description": "【总结·日总结】QQ投递目标 UMO",
    "kind": "string",
    "status": "pending",
    "target": ""
  },
  {
    "key": "DAILY_SUMMARY_RENDER_IMAGE",
    "description": "【总结·日总结】渲染为图片",
    "kind": "bool",
    "status": "pending",
    "target": ""
  },
  {
    "key": "CUSTOM_DAILY_INSTRUCTION",
    "description": "【总结·日总结】补充提示词",
    "kind": "text",
    "status": "pending",
    "target": ""
  },
  {
    "key": "ENABLE_WEEKLY_SUMMARY",
    "description": "【周总结】启用每周总结（回顾一周的B站生活）",
    "kind": "bool",
    "status": "pending",
    "target": ""
  },
  {
    "key": "WEEKLY_SUMMARY_MODE",
    "description": "【周总结】总结发送方式",
    "kind": "string",
    "status": "pending",
    "target": ""
  },
  {
    "key": "WEEKLY_SUMMARY_DAY",
    "description": "【周总结】每周生成日（0=周一 ... 6=周日）",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "WEEKLY_SUMMARY_QQ_UMO",
    "description": "【周总结】接收总结的 QQ 私聊 UMO（留空则复用恶意告警的 UMO）",
    "kind": "string",
    "status": "pending",
    "target": ""
  },
  {
    "key": "WEEKLY_SUMMARY_RENDER_IMAGE",
    "description": "【周总结】生成周总结图片卡片",
    "kind": "bool",
    "status": "pending",
    "target": ""
  },
  {
    "key": "SUMMARY_CJK_FONT_PATH",
    "description": "【总结·图片渲染】自定义中文字体路径（可选）",
    "kind": "string",
    "status": "pending",
    "target": ""
  },
  {
    "key": "CUSTOM_WEEKLY_INSTRUCTION",
    "description": "【周总结】周总结的补充提示词",
    "kind": "text",
    "status": "pending",
    "target": ""
  },
  {
    "key": "ENABLE_PERSONALITY_EVOLUTION",
    "description": "【实验性】启用每周近期状态演化",
    "kind": "bool",
    "status": "pending",
    "target": ""
  },
  {
    "key": "EVOLVE_MIN_DATA_DAYS",
    "description": "【性格演化】启用前最少真实日报天数",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "EVOLVE_WEEKDAY",
    "description": "【性格演化】每周执行日",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "EVOLVE_HOUR",
    "description": "【性格演化】每周触发时刻（0-23点）",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "EVOLVE_MAX_RETRIES",
    "description": "【兼容字段】旧版演化重试次数（不再使用）",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "EVOLVE_PROMPT",
    "description": "【性格演化】每周整理补充提示词",
    "kind": "text",
    "status": "pending",
    "target": ""
  },
  {
    "key": "ENABLE_MEME_LEARNING",
    "description": "【实验性】允许每周学习少量近期梗",
    "kind": "bool",
    "status": "pending",
    "target": ""
  },
  {
    "key": "ENABLE_AUTONOMOUS_DAILY_PLAN",
    "description": "【自主安排】允许 Bot 根据人设与活跃度生成每日计划",
    "kind": "bool",
    "status": "shared",
    "target": "全局自主活动开关"
  },
  {
    "key": "AUTONOMOUS_ACTIVITY_LEVEL",
    "description": "【自主安排】今日基础活跃度（0-100）",
    "kind": "int",
    "status": "shared",
    "target": "全局活跃度"
  },
  {
    "key": "AUTONOMOUS_PLAN_PROMPT",
    "description": "【自主安排】每日计划补充提示词",
    "kind": "text",
    "status": "pending",
    "target": ""
  },
  {
    "key": "AUTONOMOUS_PLAN_GENERATION_MODE",
    "description": "【自主安排】每日计划生成时机",
    "kind": "string",
    "status": "pending",
    "target": ""
  },
  {
    "key": "AUTONOMOUS_PLAN_AFTER_SLEEP_MINUTES",
    "description": "【自主安排】休眠结束后多少分钟生成计划",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "AUTONOMOUS_PLAN_GENERATION_TIME",
    "description": "【自主安排】每日计划固定生成时刻",
    "kind": "string",
    "status": "pending",
    "target": ""
  },
  {
    "key": "AUTONOMOUS_PLAN_RETRY_MINUTES",
    "description": "【自主安排】计划生成失败后的重试等待（分钟）",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "SCHEDULE_PLAN_PROVIDER_ID",
    "description": "【自主安排】今日计划生成模型",
    "kind": "string",
    "status": "shared",
    "target": "全局规划模型"
  },
  {
    "key": "AUTONOMOUS_PLAN_MAX_RETRIES",
    "description": "【自主安排】计划生成失败后自动重试次数",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "AUTONOMOUS_PROACTIVE_WINDOW_MINUTES",
    "description": "【自主安排】主动浏览默认时间段长度（分钟）",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "SLEEP_START",
    "description": "【系统】休眠开始时间（0-23）",
    "kind": "int",
    "status": "shared",
    "target": "全局休息时间窗"
  },
  {
    "key": "SLEEP_END",
    "description": "【系统】休眠结束时间（0-23）",
    "kind": "int",
    "status": "shared",
    "target": "全局休息时间窗"
  },
  {
    "key": "AUTONOMOUS_REPLY_DAILY_MIN",
    "description": "【兼容旧配置】每日评论回复旧版下限（已停用）",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "AUTONOMOUS_REPLY_DAILY_MAX",
    "description": "【自主安排·上限】每日评论回复最多几条",
    "kind": "int",
    "status": "ported",
    "target": "回复配额"
  },
  {
    "key": "AUTONOMOUS_PRIVATE_DAILY_MIN",
    "description": "【兼容旧配置】每日私信回复旧版下限（已停用）",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "AUTONOMOUS_PRIVATE_DAILY_MAX",
    "description": "【自主安排·上限】每日私信回复最多几条",
    "kind": "int",
    "status": "ported",
    "target": "私信配额"
  },
  {
    "key": "AUTONOMOUS_DYNAMIC_DAILY_MIN",
    "description": "【兼容旧配置】每日发布动态旧版下限（已停用）",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "AUTONOMOUS_DYNAMIC_DAILY_MAX",
    "description": "【自主安排·上限】每日发布动态最多几条",
    "kind": "int",
    "status": "ported",
    "target": "动态配额"
  },
  {
    "key": "AUTONOMOUS_PROACTIVE_DAILY_MIN",
    "description": "【兼容旧配置】每日主动浏览旧版下限（已停用）",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "AUTONOMOUS_PROACTIVE_DAILY_MAX",
    "description": "【自主安排·上限】每日主动浏览轮次最多几轮",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "AUTONOMOUS_MIN_ACTION_GAP_MINUTES",
    "description": "【自主安排·硬约束】主动事件最小间隔（分钟）",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "FIXED_REPLY_DAILY_TARGET",
    "description": "【兼容旧配置】每日评论回复旧版目标（已停用）",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "FIXED_PRIVATE_DAILY_TARGET",
    "description": "【兼容旧配置】每日私信回复旧版目标（已停用）",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "FIXED_PROACTIVE_WINDOWS",
    "description": "【固定计划】主动浏览时间段",
    "kind": "list",
    "status": "shared",
    "target": "全局允许活动时间窗"
  },
  {
    "key": "FIXED_PROACTIVE_TIMES",
    "description": "【固定计划】主动浏览准确时刻",
    "kind": "list",
    "status": "pending",
    "target": ""
  },
  {
    "key": "FIXED_DYNAMIC_TIMES",
    "description": "【固定计划】发布动态准确时刻",
    "kind": "list",
    "status": "pending",
    "target": ""
  },
  {
    "key": "FIXED_DYNAMIC_WATCH_TIMES",
    "description": "【固定计划】关注动态巡视准确时刻",
    "kind": "list",
    "status": "pending",
    "target": ""
  },
  {
    "key": "FIXED_BANGUMI_TIMES",
    "description": "【固定计划】追番准确时刻",
    "kind": "list",
    "status": "pending",
    "target": ""
  },
  {
    "key": "FIXED_SPECIAL_FOLLOW_TIMES",
    "description": "【固定计划】特别关注巡视准确时刻",
    "kind": "list",
    "status": "pending",
    "target": ""
  },
  {
    "key": "AUTONOMOUS_REPLY_DAILY_LIMIT",
    "description": "【兼容旧配置】每日评论回复旧版单值上限（请改用新上限）",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "AUTONOMOUS_PRIVATE_DAILY_LIMIT",
    "description": "【兼容旧配置】每日私信回复旧版单值上限（请改用新上限）",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "AUTONOMOUS_DYNAMIC_DAILY_LIMIT",
    "description": "【兼容旧配置】每日发布动态旧版单值上限（请改用新上限）",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "AUTONOMOUS_PROACTIVE_DAILY_LIMIT",
    "description": "【兼容旧配置】每日主动行为旧版单值上限（请改用新上限）",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "BEHAVIOR_BUDGET_ENABLED",
    "description": "【行为调度·总开关】统一限制主动看片、评论、私信、直播和动态动作",
    "kind": "bool",
    "status": "pending",
    "target": ""
  },
  {
    "key": "BEHAVIOR_GLOBAL_MAX_PER_MINUTE",
    "description": "【行为调度·全局】每分钟最多执行多少个对外动作",
    "kind": "int",
    "status": "shared",
    "target": "共用每分钟行为上限"
  },
  {
    "key": "BEHAVIOR_GLOBAL_DAILY_LIMIT",
    "description": "【行为调度·全局】每日最多执行多少个对外动作",
    "kind": "int",
    "status": "shared",
    "target": "共用每日行为上限"
  },
  {
    "key": "BEHAVIOR_ACTION_TIMEOUT_SECONDS",
    "description": "【行为调度·队列】单个发送动作超时秒数",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "BILI_TOOL_ISOLATION_ENABLED",
    "description": "【安全与工具】保持 B站端与 AstrBot/QQ 工具权限隔离",
    "kind": "bool",
    "status": "shared",
    "target": "主插件强制平台隔离"
  },
  {
    "key": "ENABLE_LLM_TOOLS",
    "description": "【功能开关】启用 LLM 工具（B站查询/看视频/搜索等函数调用）",
    "kind": "bool",
    "status": "pending",
    "target": ""
  },
  {
    "key": "BILI_ALLOW_SEARCH_TOOLS",
    "description": "【安全与工具】允许 B站端私信回复使用只读查询工具",
    "kind": "bool",
    "status": "pending",
    "target": ""
  },
  {
    "key": "BILI_TOOL_ALLOWLIST",
    "description": "【安全与工具】B站端私信回复工具白名单",
    "kind": "list",
    "status": "pending",
    "target": ""
  },
  {
    "key": "BILI_PROMPT_INJECTION_DEFENSE",
    "description": "【安全与工具】启用外部内容提示注入防护",
    "kind": "bool",
    "status": "shared",
    "target": "主插件强制外部内容防护"
  },
  {
    "key": "BILI_TOOL_AUDIT_ENABLED",
    "description": "【安全与工具】记录工具请求与拒绝原因",
    "kind": "bool",
    "status": "shared",
    "target": "统一执行记录"
  },
  {
    "key": "ENABLE_PRIVACY_REDACTION",
    "description": "【记忆隔离】跨平台输出前执行隐私脱敏",
    "kind": "bool",
    "status": "pending",
    "target": ""
  },
  {
    "key": "ABUSE_ALERT_MODE",
    "description": "【恶意告警】检测到恶意评论时通知主人（通过QQ私信）",
    "kind": "string",
    "status": "pending",
    "target": ""
  },
  {
    "key": "ABUSE_ALERT_QQ_UMO",
    "description": "【恶意告警】接收通知的 QQ 私聊 UMO（从 AstrBot 日志或读空气插件的 UMO 注册表获取）",
    "kind": "string",
    "status": "pending",
    "target": ""
  },
  {
    "key": "ABUSE_ALERT_SCORE_THRESHOLD",
    "description": "【恶意告警】触发告警的 score_delta 阈值",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "ENABLE_AUTO_BLOCK",
    "description": "【拉黑】启用自动拉黑",
    "kind": "bool",
    "status": "pending",
    "target": ""
  },
  {
    "key": "BLOCK_WHITELIST_UIDS",
    "description": "【拉黑】永不拉黑的UID白名单",
    "kind": "list",
    "status": "pending",
    "target": ""
  },
  {
    "key": "AUTO_BLOCK_SCORE",
    "description": "【拉黑】好感度低于此值自动拉黑",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "AUTO_BLOCK_NEGATIVE_TIMES",
    "description": "【拉黑】恶意评论累计次数达标自动拉黑",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "VIDEO_VISION_PROVIDER_ID",
    "description": "【高级·视觉】视频分析使用的 AstrBot 模型提供商（优先使用，失败退回独立 API）",
    "kind": "string",
    "status": "ported",
    "target": "vision_model"
  },
  {
    "key": "VIDEO_VISION_MODEL",
    "description": "【高级·视觉】视频分析模型名称",
    "kind": "string",
    "status": "pending",
    "target": ""
  },
  {
    "key": "VIDEO_VISION_FORMAT",
    "description": "【高级·视觉】视频直读的接口格式（请根据你使用的模型选择）",
    "kind": "string",
    "status": "pending",
    "target": ""
  },
  {
    "key": "VIDEO_VISION_FPS",
    "description": "【高级·视觉】视频直读抽帧率（仅Qwen格式生效）",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "IMAGE_VISION_PROVIDER_ID",
    "description": "【高级·视觉】图片识别使用的 AstrBot 模型提供商",
    "kind": "string",
    "status": "pending",
    "target": ""
  },
  {
    "key": "IMAGE_VISION_MODEL",
    "description": "【高级·视觉】图片识别模型名称",
    "kind": "string",
    "status": "pending",
    "target": ""
  },
  {
    "key": "IMAGE_GEN_BACKEND",
    "description": "【高级·图片生成】生图后端",
    "kind": "string",
    "status": "pending",
    "target": ""
  },
  {
    "key": "IMAGE_GEN_MODEL",
    "description": "【高级·图片生成】模型名称",
    "kind": "string",
    "status": "pending",
    "target": ""
  },
  {
    "key": "IMAGE_GEN_WIDTH",
    "description": "【高级·图片生成】NovelAI 图片宽度",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "IMAGE_GEN_HEIGHT",
    "description": "【高级·图片生成】NovelAI 图片高度",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "IMAGE_GEN_STEPS",
    "description": "【高级·图片生成】NovelAI 采样步数",
    "kind": "int",
    "status": "pending",
    "target": ""
  },
  {
    "key": "IMAGE_GEN_SCALE",
    "description": "【高级·图片生成】NovelAI 提示词引导强度",
    "kind": "float",
    "status": "pending",
    "target": ""
  },
  {
    "key": "IMAGE_GEN_SAMPLER",
    "description": "【高级·图片生成】NovelAI 采样器",
    "kind": "string",
    "status": "pending",
    "target": ""
  },
  {
    "key": "IMAGE_GEN_NEGATIVE_PROMPT",
    "description": "【高级·图片生成】NovelAI 负面提示词",
    "kind": "text",
    "status": "pending",
    "target": ""
  },
  {
    "key": "ENABLE_WEB_SEARCH",
    "description": "【高级·联网搜索】启用联网搜索",
    "kind": "bool",
    "status": "pending",
    "target": ""
  },
  {
    "key": "WEB_SEARCH_JUDGE_PROVIDER_ID",
    "description": "【高级·联网搜索】搜索判断模型（建议选轻量模型）",
    "kind": "string",
    "status": "pending",
    "target": ""
  },
  {
    "key": "WEB_SEARCH_BACKEND",
    "description": "【高级·联网搜索】搜索后端",
    "kind": "string",
    "status": "pending",
    "target": ""
  },
  {
    "key": "WEB_SEARCH_MODEL",
    "description": "【高级·联网搜索】搜索模型名（Grok / custom / perplexity）",
    "kind": "string",
    "status": "pending",
    "target": ""
  },
  {
    "key": "WEB_SEARCH_MAX_RESULTS",
    "description": "【高级·联网搜索】搜索返回最大条数",
    "kind": "int",
    "status": "pending",
    "target": ""
  }
];
