# 0.2.4

- 补齐重排今日剩余日程的原生工具，与面板共用规划入口；查看与调整继续沿用现有工具，不新增聊天指令。
- 重排保留已有权限、迁移检查、执行中/已完成/固定任务以及预算，不立即执行外部活动。

# 0.2.3

- Give delegated music sessions a bounded one-hour execution budget, covering real-time audio and model work; keep the normal 45-second timeout for network actions.
- Propagate music execution receipts to scheduled tasks so failed/unknown operations are not marked successful.
- Preserve invitation permissions, rating policy, idempotency and historical playback records.
