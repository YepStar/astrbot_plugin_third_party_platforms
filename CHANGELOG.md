# 0.2.3

- Give delegated music sessions a bounded one-hour execution budget, covering real-time audio and model work; keep the normal 45-second timeout for network actions.
- Propagate music execution receipts to scheduled tasks so failed/unknown operations are not marked successful.
- Preserve invitation permissions, rating policy, idempotency and historical playback records.
