# 冷月系—第三方平台

把 B站、小黑盒等平台放进同一个工作台，让机器人按自己的安排浏览内容，挑选值得分享的发现，并在你允许的范围内互动。

**目前处于开发阶段，尚不能替换原插件。请先保留 B站 AI Bot 和小黑盒适配器。**

计划提供：

- 分别登录机器人账号，管理每个平台的浏览和互动设置。
- 用统一评分挑选内容，只分享达到你设定标准的发现。
- 安排全天活动，允许时间重叠，并逐渐记住不同时间的内容偏好。
- 连接「并行记忆分支」，保存公开阅读经历；连接「网易云音乐」，统一安排自主听歌。
- 通过「自然意图分析」用日常说法查看、调整活动安排。

## 来源与致谢

本插件参考并提取了两款插件及其本机定制版本的代码。它们是初始平台接入的重要基础：

- [B站 AI Bot](https://github.com/chenluQwQ/astrbot_plugin_bilibili_ai_bot)，作者 **chenluQwQ、claude**：贡献了 B站接口与扫码登录、视频内容读取与评分、主动浏览、评论/私信/动态相关实现，以及自主规划、行为预算和内容偏好机制。
- [小黑盒适配器](https://github.com/674537331/astrbot_plugin_xiaoheihe_adapter)，作者 **RyanVaderAn**：贡献了小黑盒接口与登录、请求签名、帖子和分区读取、通知/评论流程、多账号隔离、权限校验、事件去重与发送状态管理。

原 MIT 许可证与作者声明保留在源码中。YepStar 负责冷月系整合、通用核心及本机定制的迁移；上述贡献不被重新声明为独立原创。具体提取范围见[开发状态](docs/DEVELOPMENT.md)与[源码审计清单](docs/source-audit.json)。

实际可用能力取决于各平台接口和账号状态。现有小黑盒接入并不是稳定的官方开放自动化 API；接口变化时会停止相关操作并明确报告，不保证永久可用。

## 冷月系

由 **YepStar** 维护。可搭配[并行记忆分支](https://github.com/YepStar/astrbot_plugin_memory_branches)、[网易云音乐](https://github.com/YepStar/astrbot_plugin_netease_browser)和[自然意图分析](https://github.com/YepStar/astrbot_plugin_intent_bridge)。自然意图分析把“今晚看看B站”“把小黑盒浏览挪到九点”等日常表达，转换成已授权的功能调用。
