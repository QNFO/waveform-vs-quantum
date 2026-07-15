# WORKER BINDING REGISTRY — 2026-07-15
# Canonical reference for all 28 Worker bindings. 
# Eliminates: Worker deployment binding blindness, redeployment risk.
# Updated after each Worker deployment or binding change.

## Active Workers (28 total)

### archive-worker (v3.0)
- **R2:** QNFO_BUCKET → qnfo (NEEDS UPDATE → qnfo-audit)
- **D1:** DB → qnfo-audit (35e2e573-92f3-46ac-83c6-22f6429fc5e5)
- **Queue:** qnfo-lifecycle-queue (consumer)
- **Health:** https://archive-worker.q08.workers.dev/health ✅

### paper-pipeline
- **R2:** QNFO_BUCKET → qnfo (NEEDS UPDATE → qnfo-audit)
- **D1:** QNFO_AUDIT_DB → qnfo-audit (35e2e573)
- **Vectorize:** VECTORIZE_TASKS, VECTORIZE_HANDOFFS
- **AI:** @cf/baai/bge-base-en-v1.5
- **Health:** https://paper-pipeline.q08.workers.dev/health

### qnfo-asset-api
- **R2:** ASSETS_R2 → qnfo (NEEDS UPDATE → qnfo-assets)
- **D1:** GRAPH_DB → qnfo-graph (a1954b92), AUDIT_DB → qnfo-audit (35e2e573)
- **Vectorize:** QWAV_VECTORIZE
- **AI:** @cf/baai/bge-base-en-v1.5
- **Health:** https://qnfo-asset-api.q08.workers.dev/health

### d1-backup-cron
- **R2:** BACKUP_BUCKET → qnfo (NEEDS UPDATE → qnfo-backups)
- **D1:** QNFO_GRAPH_DB, QNFO_AUDIT_DB, LIVING_PAPER_DB
- **Health:** https://d1-backup-cron.q08.workers.dev/health

### qnfo-lifecycle (v2.1)
- **D1:** QNFO_AUDIT → qnfo-audit
- **Queue:** ARCHIVE_QUEUE → qnfo-lifecycle-queue (producer)
- **Health:** https://qnfo-lifecycle.q08.workers.dev/health ✅

### r2-gateway (v2.0)
- **R2:** RELEASES(qnfo-releases), SKILLS(qnfo-skills), AUDIT(qnfo-audit), PROJECTS(qnfo-projects), BACKUPS(qnfo-backups), ASSETS(qnfo-assets)
- **Health:** https://r2-gateway.q08.workers.dev/health ✅

### infra-lock-manager (v2.0)
- **DO:** INFRA_LOCK_MANAGER (InfraLockManager class, SQLite ON)
- **Health:** https://infra-lock-manager.q08.workers.dev/health ✅

### qnfo-memory-mcp (v1.2)
- **D1:** MEMORY_DB, PAPER_DB
- **Vectorize:** MEMORY_VZ, PAPER_VZ
- **AI:** @cf/baai/bge-base-en-v1.5
- **Service:** GRAPH → graph-api

### qnfo-agent-session (v3.0)
- **DO:** SQLITE_SESSIONS (QnfoAgentSession class, SQLite ON)

### qnfo-data-api (v2.0)
- **D1:** QNFO_AUDIT, QNFO_GRAPH, QNFO_CMS, LIVING_PAPER, PORTFOLIO_STATE
- **Vectorize:** VECTORIZE
- **AI:** @cf/baai/bge-base-en-v1.5

### graph-api
- **D1:** QNFO_GRAPH (a1954b92)
- **Health:** https://graph-api.q08.workers.dev/stats

### papers-server / papers-server-production
- **D1:** DB → living-paper

### cron-graph-re-seed
- **Scheduled:** Cron trigger
- **Invoke:** https://cron-graph-re-seed.q08.workers.dev

### search-worker
- **Vectorize:** (qwav-research-v2)

### audit-worker
- **D1:** QNFO_AUDIT

## R2 Bucket Fleet

| Bucket | Domain | Binding Count |
|:-------|:-------|:------------:|
| qnfo-releases | Publications | 1 (r2-gateway) |
| qnfo-skills | Skills | 1 (r2-gateway) |
| qnfo-audit | Audit trails | 1 (r2-gateway) + 4 legacy |
| qnfo-projects | Projects | 1 (r2-gateway) |
| qnfo-backups | DR | 1 (r2-gateway) + 1 legacy |
| qnfo-assets | Web assets | 1 (r2-gateway) + 1 legacy |

## Status

| Issue | Workers Affected | Action |
|:------|:-----------------|:-------|
| Stale R2 bindings → qnfo | archive-worker, paper-pipeline, qnfo-asset-api, d1-backup-cron | Update wrangler config + redeploy |

**Last Updated:** 2026-07-15 | **Source:** REST API bindings + code inspection
