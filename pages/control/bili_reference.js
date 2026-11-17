// Original descriptions: BiliBot by chenluQwQ, MIT. Completed selected migration.
export const biliReference=[
  {
    "key": "COOKIE_AUTO_REFRESH",
    "description": "【系统】Cookie过期自动刷新",
    "kind": "bool",
    "status": "ported",
    "target": "账号连接 → 登录维护"
  },
  {
    "key": "COOKIE_CHECK_INTERVAL",
    "description": "【系统】Cookie检查间隔（小时）",
    "kind": "int",
    "status": "ported",
    "target": "账号连接 → 登录检查间隔"
  },
  {
    "key": "OWNER_MID",
    "description": "【账号】主人的B站UID（好感度与私信推荐）",
    "kind": "string",
    "status": "ported",
    "target": "主人 UID"
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
    "status": "ported",
    "target": "全局 → 模型故障冷却"
  },
  {
    "key": "LLM_CIRCUIT_COOLDOWN_SECONDS",
    "description": "【模型可靠性】熔断冷却时间（秒）",
    "kind": "int",
    "status": "ported",
    "target": "全局 → 模型故障冷却"
  },
  {
    "key": "SUMMARY_PROVIDER_ID",
    "description": "【总结模型】选择 AstrBot 模型提供商",
    "kind": "string",
    "status": "ported",
    "target": "evaluation_model"
  },
  {
    "key": "GENERATION_PROVIDER_ID",
    "description": "【生成模型】选择 AstrBot 模型提供商",
    "kind": "string",
    "status": "ported",
    "target": "comment_model"
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
    "status": "ported",
    "target": "B站私信 → 活跃期检查间隔"
  },
  {
    "key": "PRIVATE_MESSAGE_IDLE_POLL_INTERVAL",
    "description": "【B站私信·监听】空闲期检查间隔（秒）",
    "kind": "int",
    "status": "ported",
    "target": "B站私信 → 空闲期检查间隔"
  },
  {
    "key": "PRIVATE_MESSAGE_ACTIVE_WINDOW",
    "description": "【B站私信·监听】收到消息后保持活跃多久（秒）",
    "kind": "int",
    "status": "ported",
    "target": "B站私信 → 活跃期持续时间"
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
    "status": "ported",
    "target": "B站私信 → 视频与只读查询"
  },
  {
    "key": "PRIVATE_MESSAGE_BILI_SEARCH_ENABLED",
    "description": "【B站私信·查询】允许按私信要求搜索视频和UP主",
    "kind": "bool",
    "status": "ported",
    "target": "B站私信 → 视频与只读查询"
  },
  {
    "key": "PRIVATE_MESSAGE_BILI_SEARCH_LIMIT",
    "description": "【B站私信·查询】每次最多返回几个搜索结果",
    "kind": "int",
    "status": "ported",
    "target": "B站私信 → 每次查询最多结果数"
  },
  {
    "key": "BILI_PRIVATE_SHARE_TOOL_ENABLED",
    "description": "【B站私信·分享】允许 Bot 看完视频后私信给主人",
    "kind": "bool",
    "status": "ported",
    "target": "基础设置 → 内容分享 → B站私信（由现有分享流程承担）"
  },
  {
    "key": "BILI_PRIVATE_SHARE_COOLDOWN",
    "description": "【B站私信·分享】同一视频重复分享冷却秒数",
    "kind": "int",
    "status": "ported",
    "target": "基础设置 → 分享间隔与永久视频去重"
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
    "status": "ported",
    "target": "按你的选择已接入：安全与工具。仍遵守当前账号启停、权限、额度和模型能力。"
  },
  {
    "key": "PRIVATE_MESSAGE_BLOCK_WHITELIST_UIDS",
    "description": "【B站私信·安全】永不因私信自动拉黑的UID",
    "kind": "list",
    "status": "ported",
    "target": "按你的选择已接入：安全与工具。仍遵守当前账号启停、权限、额度和模型能力。"
  },
  {
    "key": "PRIVATE_MESSAGE_TRUSTED_DOMAINS",
    "description": "【B站私信·安全】允许出现的链接域名",
    "kind": "list",
    "status": "ported",
    "target": "按你的选择已接入：安全与工具。仍遵守当前账号启停、权限、额度和模型能力。"
  },
  {
    "key": "ENABLE_MOOD",
    "description": "【功能开关】启用心情系统",
    "kind": "bool",
    "status": "ported",
    "target": "按你的选择已接入：生活与总结 / 活动回顾。仍遵守当前账号启停、权限、额度和模型能力。"
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
    "status": "ported",
    "target": "视频分析 → 长视频采样分段长度（稀疏画面，无音频）"
  },
  {
    "key": "VIDEO_SEGMENT_MAX_COUNT",
    "description": "【视频分析】长视频最多分析多少段",
    "kind": "int",
    "status": "ported",
    "target": "视频分析 → 最多采样段数（总画面不超过12张）"
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
    "status": "ported",
    "target": "基础设置 → 主动搜索词补充要求"
  },
  {
    "key": "PROACTIVE_TASTE_WINDOW_DAYS",
    "description": "【主动看片·来源2】分区评分口味统计天数",
    "kind": "int",
    "status": "ported",
    "target": "基础设置 → 观看兴趣统计天数"
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
    "status": "ported",
    "target": "基础设置 → 获取字幕与画面前筛选候选"
  },
  {
    "key": "PROACTIVE_LLM_PREFILTER_MAX_REJECTS",
    "description": "【主动看片·筛选】每轮最多拒绝几个候选",
    "kind": "int",
    "status": "ported",
    "target": "基础设置 → 每轮最多额外筛选候选数"
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
    "status": "ported",
    "target": "按你的选择已接入：生活与总结 / 活动回顾。仍遵守当前账号启停、权限、额度和模型能力。"
  },
  {
    "key": "SPECIAL_FOLLOW_ENABLED",
    "description": "【特别关注】启用定时特关巡视（独立于主动刷视频）",
    "kind": "bool",
    "status": "ported",
    "target": "浏览特别关注"
  },
  {
    "key": "ENABLE_DYNAMIC_WATCH",
    "description": "【关注动态巡视·总开关】查看关注者的新动态图文",
    "kind": "bool",
    "status": "ported",
    "target": "基础设置 → 关注动态（与视频共用浏览轮次）"
  },
  {
    "key": "DYNAMIC_WATCH_TIMES_COUNT",
    "description": "【关注动态巡视】自主计划每日最多巡视次数",
    "kind": "int",
    "status": "ported",
    "target": "统一日程，不单独重复安排轮次"
  },
  {
    "key": "DYNAMIC_WATCH_DAILY_LIMIT",
    "description": "【关注动态巡视】每天最多查看新动态数",
    "kind": "int",
    "status": "ported",
    "target": "基础设置 → 每日动态读取上限"
  },
  {
    "key": "DYNAMIC_WATCH_SPECIAL_ONLY",
    "description": "【关注动态巡视】只查看特别关注用户",
    "kind": "bool",
    "status": "ported",
    "target": "基础设置 → 只看特别关注动态"
  },
  {
    "key": "DYNAMIC_WATCH_INCLUDE_VIDEO_POSTS",
    "description": "【关注动态巡视】同时查看视频投稿动态",
    "kind": "bool",
    "status": "ported",
    "target": "基础设置 → 动态来源包含视频投稿"
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
    "status": "ported",
    "target": "按你的选择已接入：生活与总结 / 活动回顾。仍遵守当前账号启停、权限、额度和模型能力。"
  },
  {
    "key": "DYNAMIC_DAILY_COUNT",
    "description": "【动态发布】每天最多发几条动态",
    "kind": "int",
    "status": "ported",
    "target": "按你的选择已接入：生活与总结 / 活动回顾。仍遵守当前账号启停、权限、额度和模型能力。"
  },
  {
    "key": "DYNAMIC_MIN_INTERVAL_DAYS",
    "description": "【动态】自动动态最短间隔（天）",
    "kind": "int",
    "status": "ported",
    "target": "按你的选择已接入：生活与总结 / 活动回顾。仍遵守当前账号启停、权限、额度和模型能力。"
  },
  {
    "key": "DYNAMIC_TOPICS",
    "description": "【动态发布】动态主题池（每行一个）",
    "kind": "list",
    "status": "ported",
    "target": "按你的选择已接入：生活与总结 / 活动回顾。仍遵守当前账号启停、权限、额度和模型能力。"
  },
  {
    "key": "CUSTOM_DYNAMIC_INSTRUCTION",
    "description": "【动态发布】发动态的补充提示词",
    "kind": "text",
    "status": "ported",
    "target": "按你的选择已接入：生活与总结 / 活动回顾。仍遵守当前账号启停、权限、额度和模型能力。"
  },
  {
    "key": "ENABLE_DAILY_SUMMARY",
    "description": "【总结·日总结】启用每日总结",
    "kind": "bool",
    "status": "ported",
    "target": "按你的选择已接入：生活与总结 / 活动回顾。仍遵守当前账号启停、权限、额度和模型能力。"
  },
  {
    "key": "DAILY_SUMMARY_HOUR",
    "description": "【总结·日总结】生成时间（0-23点）",
    "kind": "int",
    "status": "ported",
    "target": "按你的选择已接入：生活与总结 / 活动回顾。仍遵守当前账号启停、权限、额度和模型能力。"
  },
  {
    "key": "DAILY_SUMMARY_MODE",
    "description": "【总结·日总结】投递方式",
    "kind": "string",
    "status": "ported",
    "target": "按你的选择已接入：生活与总结 / 活动回顾。仍遵守当前账号启停、权限、额度和模型能力。"
  },
  {
    "key": "DAILY_SUMMARY_QQ_UMO",
    "description": "【总结·日总结】QQ投递目标 UMO",
    "kind": "string",
    "status": "ported",
    "target": "按你的选择已接入：生活与总结 / 活动回顾。仍遵守当前账号启停、权限、额度和模型能力。"
  },
  {
    "key": "DAILY_SUMMARY_RENDER_IMAGE",
    "description": "【总结·日总结】渲染为图片",
    "kind": "bool",
    "status": "ported",
    "target": "按你的选择已接入：生活与总结 / 活动回顾。仍遵守当前账号启停、权限、额度和模型能力。"
  },
  {
    "key": "CUSTOM_DAILY_INSTRUCTION",
    "description": "【总结·日总结】补充提示词",
    "kind": "text",
    "status": "ported",
    "target": "按你的选择已接入：生活与总结 / 活动回顾。仍遵守当前账号启停、权限、额度和模型能力。"
  },
  {
    "key": "ENABLE_WEEKLY_SUMMARY",
    "description": "【周总结】启用每周总结（回顾一周的B站生活）",
    "kind": "bool",
    "status": "ported",
    "target": "按你的选择已接入：生活与总结 / 活动回顾。仍遵守当前账号启停、权限、额度和模型能力。"
  },
  {
    "key": "WEEKLY_SUMMARY_MODE",
    "description": "【周总结】总结发送方式",
    "kind": "string",
    "status": "ported",
    "target": "按你的选择已接入：生活与总结 / 活动回顾。仍遵守当前账号启停、权限、额度和模型能力。"
  },
  {
    "key": "WEEKLY_SUMMARY_DAY",
    "description": "【周总结】每周生成日（0=周一 ... 6=周日）",
    "kind": "int",
    "status": "ported",
    "target": "按你的选择已接入：生活与总结 / 活动回顾。仍遵守当前账号启停、权限、额度和模型能力。"
  },
  {
    "key": "WEEKLY_SUMMARY_QQ_UMO",
    "description": "【周总结】接收总结的 QQ 私聊 UMO（留空则复用恶意告警的 UMO）",
    "kind": "string",
    "status": "ported",
    "target": "按你的选择已接入：生活与总结 / 活动回顾。仍遵守当前账号启停、权限、额度和模型能力。"
  },
  {
    "key": "WEEKLY_SUMMARY_RENDER_IMAGE",
    "description": "【周总结】生成周总结图片卡片",
    "kind": "bool",
    "status": "ported",
    "target": "按你的选择已接入：生活与总结 / 活动回顾。仍遵守当前账号启停、权限、额度和模型能力。"
  },
  {
    "key": "SUMMARY_CJK_FONT_PATH",
    "description": "【总结·图片渲染】自定义中文字体路径（可选）",
    "kind": "string",
    "status": "ported",
    "target": "按你的选择已接入：生活与总结 / 活动回顾。仍遵守当前账号启停、权限、额度和模型能力。"
  },
  {
    "key": "CUSTOM_WEEKLY_INSTRUCTION",
    "description": "【周总结】周总结的补充提示词",
    "kind": "text",
    "status": "ported",
    "target": "按你的选择已接入：生活与总结 / 活动回顾。仍遵守当前账号启停、权限、额度和模型能力。"
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
    "key": "SCHEDULE_PLAN_PROVIDER_ID",
    "description": "【自主安排】今日计划生成模型",
    "kind": "string",
    "status": "shared",
    "target": "全局规划模型"
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
    "key": "AUTONOMOUS_REPLY_DAILY_MAX",
    "description": "【自主安排·上限】每日评论回复最多几条",
    "kind": "int",
    "status": "ported",
    "target": "回复配额"
  },
  {
    "key": "AUTONOMOUS_PRIVATE_DAILY_MAX",
    "description": "【自主安排·上限】每日私信回复最多几条",
    "kind": "int",
    "status": "ported",
    "target": "私信配额"
  },
  {
    "key": "AUTONOMOUS_DYNAMIC_DAILY_MAX",
    "description": "【自主安排·上限】每日发布动态最多几条",
    "kind": "int",
    "status": "ported",
    "target": "动态配额"
  },
  {
    "key": "FIXED_PROACTIVE_WINDOWS",
    "description": "【固定计划】主动浏览时间段",
    "kind": "list",
    "status": "shared",
    "target": "全局允许活动时间窗"
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
    "status": "ported",
    "target": "按你的选择已接入：安全与工具 / B站只读查询。仍遵守当前账号启停、权限、额度和模型能力。"
  },
  {
    "key": "BILI_ALLOW_SEARCH_TOOLS",
    "description": "【安全与工具】允许 B站端私信回复使用只读查询工具",
    "kind": "bool",
    "status": "ported",
    "target": "按你的选择已接入：安全与工具 / B站只读查询。仍遵守当前账号启停、权限、额度和模型能力。"
  },
  {
    "key": "BILI_TOOL_ALLOWLIST",
    "description": "【安全与工具】B站端私信回复工具白名单",
    "kind": "list",
    "status": "ported",
    "target": "按你的选择已接入：安全与工具 / B站只读查询。仍遵守当前账号启停、权限、额度和模型能力。"
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
    "key": "ABUSE_ALERT_MODE",
    "description": "【恶意告警】检测到恶意评论时通知主人（通过QQ私信）",
    "kind": "string",
    "status": "ported",
    "target": "按你的选择已接入：安全与工具。仍遵守当前账号启停、权限、额度和模型能力。"
  },
  {
    "key": "ABUSE_ALERT_QQ_UMO",
    "description": "【恶意告警】接收通知的 QQ 私聊 UMO（从 AstrBot 日志或读空气插件的 UMO 注册表获取）",
    "kind": "string",
    "status": "ported",
    "target": "按你的选择已接入：安全与工具。仍遵守当前账号启停、权限、额度和模型能力。"
  },
  {
    "key": "ABUSE_ALERT_SCORE_THRESHOLD",
    "description": "【恶意告警】触发告警的 score_delta 阈值",
    "kind": "int",
    "status": "ported",
    "target": "按你的选择已接入：安全与工具。仍遵守当前账号启停、权限、额度和模型能力。"
  },
  {
    "key": "ENABLE_AUTO_BLOCK",
    "description": "【拉黑】启用自动拉黑",
    "kind": "bool",
    "status": "ported",
    "target": "按你的选择已接入：安全与工具。仍遵守当前账号启停、权限、额度和模型能力。"
  },
  {
    "key": "BLOCK_WHITELIST_UIDS",
    "description": "【拉黑】永不拉黑的UID白名单",
    "kind": "list",
    "status": "ported",
    "target": "按你的选择已接入：安全与工具。仍遵守当前账号启停、权限、额度和模型能力。"
  },
  {
    "key": "AUTO_BLOCK_SCORE",
    "description": "【拉黑】好感度低于此值自动拉黑",
    "kind": "int",
    "status": "ported",
    "target": "按你的选择已接入：安全与工具。仍遵守当前账号启停、权限、额度和模型能力。"
  },
  {
    "key": "AUTO_BLOCK_NEGATIVE_TIMES",
    "description": "【拉黑】恶意评论累计次数达标自动拉黑",
    "kind": "int",
    "status": "ported",
    "target": "按你的选择已接入：安全与工具。仍遵守当前账号启停、权限、额度和模型能力。"
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
    "status": "ported",
    "target": "按你的选择已接入：视频分析 / B站私信。仍遵守当前账号启停、权限、额度和模型能力。"
  },
  {
    "key": "VIDEO_VISION_FORMAT",
    "description": "【高级·视觉】视频直读的接口格式（请根据你使用的模型选择）",
    "kind": "string",
    "status": "ported",
    "target": "按你的选择已接入：视频分析 / B站私信。仍遵守当前账号启停、权限、额度和模型能力。"
  },
  {
    "key": "VIDEO_VISION_FPS",
    "description": "【高级·视觉】视频直读抽帧率（仅Qwen格式生效）",
    "kind": "int",
    "status": "ported",
    "target": "按你的选择已接入：视频分析 / B站私信。仍遵守当前账号启停、权限、额度和模型能力。"
  },
  {
    "key": "IMAGE_VISION_PROVIDER_ID",
    "description": "【高级·视觉】图片识别使用的 AstrBot 模型提供商",
    "kind": "string",
    "status": "ported",
    "target": "按你的选择已接入：视频分析 / B站私信。仍遵守当前账号启停、权限、额度和模型能力。"
  },
  {
    "key": "IMAGE_VISION_MODEL",
    "description": "【高级·视觉】图片识别模型名称",
    "kind": "string",
    "status": "ported",
    "target": "按你的选择已接入：视频分析 / B站私信。仍遵守当前账号启停、权限、额度和模型能力。"
  }
];
