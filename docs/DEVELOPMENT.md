# Development checkpoint (not release / no cutover)

Latest user authorization supersedes the PRD's original planning-only restriction: implementation is now authorized. User requires final name 冷月系—第三方平台, eventual uninstall of both old plugins ONLY after successful migration/parity, and README upstream acknowledgements with GitHub URLs. Do not ask again for those actions. Do not uninstall during this checkpoint.

Implemented in this working tree:
- AST inventory of upstream local modules/hooks; both MIT licenses retained. Vendored XHH HTTP/auth/model/parser/security/permission/storage utility dependency closure; Bili HTTP mixin/network and a sanitized constants-only config. No legacy Star registration or background scheduler imported.
- Core SQLite store: revision-checked tasks, atomic action/budget claims, persisted unknown recovery, confirmed-failure reservation release, observations and decayed per-account/hour preferences.
- Timezone-aware overlapping/cross-midnight windows; deterministic planner utility and initial bounded daily LLM plan generation.
- Provider registry v1; Bili QR flow, nav check, popular/search -> actual video info/subtitles; XHH QR, identity check, feed/box -> full post text. Gated provider comment/reply/basic Bili text dynamic methods exist, NOT wired to autonomous/public reply flow yet. Bili media understanding is currently text/subtitles/description only.
- Shared grounded scoring and separate attribution review before private owner sharing; duplicate delivery keys, normalized receipts, no automatic unknown-write retries.
- Memory facade integration: current existing Bili/XHH public routes only; respects facade route checks, no direct DB fallback.
- Optional music facade consumer and standalone durable lease primitive. MUSIC PRODUCER FACADE NOT IMPLEMENTED/INSTALLED, provider NOT registered with scheduler yet.
- AstrBot entry point, authenticated state/action APIs, native schedule list/change tools with private UMO allowlist, read-only context/readiness hook.
- Early workbench account strategy/login/schedule/cancel/status forms; not visually QA'd in a live plugin session. No live deployment performed.
- Read-only migration inventory utility; report at this chat's work/third-party-migration-inventory.json, with config KEY classifications and file sizes only, no secret values.

Verified in isolated /tmp copy inside current AstrBot container: main import + native tool registration, 16 pytest tests covering core/leases/provider mocks. No platform APIs contacted; no actual owner messages, model requests, comments or DMs sent. Existing plugins/configuration left unchanged.

Known blockers before release/cutover (must finish, do not declare complete):
1. Deep audit/migration matrix for remaining source modules and original regression tests. Current clients cover a subset, not full Bili/XHH feature parity. XHH native AstrBot platform transport and visual preprocessing; Bili notifications/comment replies/private inbox/dynamics images/live/bangumi/special-follow features not migrated.
2. IMPORTANT legacy coexistence gate currently prevents enabling new runtime. Keep until all replacement writers are ready and cutover transaction is implemented.
3. Full validated configuration service: nested schema migration, provider settings/UI, owner aliases, routing, action thresholds/cooldowns/global caps, network/proxy options; stable public/private model context separation. Extend policy beyond sharing to all visible actions. Preserve existing settings explicitly, no silent dropped keys.
4. Planner: fingerprint invalidation/replanning, manual-pin/cancel preservation during generation, day-atomic plan commits, rest-window validation, optional model planner parameters, controlled exploration integrated into model plan, account readiness and independent failures, broad fake-clock/crash tests. Current model planner retries are bounded but config fingerprint absent; deterministic utility does not yet drive live plan generation.
5. Memory: bank mapping/status/pending ingestion and idempotent old-data import; public scopes beyond initial two require explicit memory-plugin facade support. Current write errors must not abort other providers; add bounded safe ingestion queue.
6. Music: add public API v1 in separately staged music repo for acquire/heartbeat/release/status/run; serialize with local autonomy loop, persist lease + execution key receipts, retain manual listening/room polling/confirmation. Only after tests register `netease` in unified planning; current consumer correctly reports unavailable if facade absent.
7. Native event pipelines and actual per-platform capability/rate/auth tests. Migrate existing XHH attribution/identity gates and Bili security/governance, not only HTTP. No unverified identities as owner/admin. Current auto public writes deliberately unavailable.
8. Auth lifecycle: QR rendering (XHH QR payload may not be HTTPS URL; current UI link-only path must be fixed), login import/logout/refresh/invalidation, ephemeral QR expiration and no token echo. Verify extracted legacy Bili refresh and request behavior with fixtures before reuse.
9. Storage retention/log views/structured redaction/backups, all account locks/resource shutdown, candidate schema/size limits, URL validation. Audit vendor code for original logs and retry behavior, don't infer safety from wrappers alone.
10. Migration APPLY tool: dry-run config report -> private snapshot -> import logins/historical content/memory pointers/action+unknown delivery ledgers -> stop legacy writers -> activate new capabilities -> reconcile -> uninstall old directories. Do not delete user's old data. Current inventory is not an importer.
11. Real UI and connector verification only after above readiness; update source pins/misc overlay ownership/migration docs at final delivery. No new GitHub repository created yet; choose visibility with session preferences and user when necessary. No private runtime files in source commits.

Next concrete work: expand original source tests and provider-native event models; implement configuration/migration key map, then music facade and replacement event pipelines; keep all live switches untouched. PRD contains final requirements; this file describes actual partial implementation honestly.
