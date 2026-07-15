# QNFO RED-TEAM KAIZEN REPORT — 2026-07-15

**Auditor:** DeepChat (deepseek-v4-pro) | **Scope:** Entire QNFO infrastructure, operations, research ecosystem
**Methodology:** RED-TEAM → DoD → ITERATE → REFINE cycle per `red-team-dod` v1.3
**Gates Applied:** All 7 assumption challenges, 6 edge cases, negative verification, silent failure detection

---

## EXECUTIVE SUMMARY

**Verdict: 1 BLOCKING, 2 HIGH, 3 MEDIUM, 2 LOW findings. System is operationally healthy but has a structural policy conflict that WILL cause data loss if not addressed.**

| # | Finding | Severity | Status |
|:--|:--------|:---------|:------:|
| F1 | Thin-client mandate deletes in-progress work before R2 save | **BLOCKING** | ⚠️ Policy flaw |
| F2 | R2 Gateway Worker not deployed — 6-bucket fleet has no centralized write path | **HIGH** | ⚠️ Code exists, not deployed |
| F3 | Worker R2 bindings still reference deprecated single `qnfo` bucket (archive-worker, paper-pipeline, qnfo-asset-api, d1-backup-cron, qnfo-lifecycle) | **HIGH** | ⚠️ 5 Workers affected |
| F4 | Archive Worker /health returns 404 — lifecycle pipeline has blind spot | **MEDIUM** | ⚠️ Health check failing |
| F5 | KG/D1 paper node drift: KG=618, D1=616 (2-node gap) | **MEDIUM** | ⚠️ Minor sync gap |
| F6 | Skills with stale `qnfo/` R2 references still present (kaizen-autonomous-update, github-manager, literature-search patterns) | **MEDIUM** | ⚠️ 3+ skill files |
| F7 | No automated Google Drive → R2 migration pipeline | **LOW** | ℹ️ Future need |
| F8 | Working directory contains 18+ non-.git files (thin-client policy not uniformly enforced — protects user work, but policy says otherwise) | **LOW** | ℹ️ Policy vs reality gap |

---

## FINDING F1 — BLOCKING: Thin-Client File-Thrashing Conflict

### Evidence

The working directory at session start contains:
```
shor-phase3/          — Active research project (Phase 3 deliverables)
memory-infra/         — Infrastructure code (lock manager client, etc.)
r2-gateway/           — Worker source code awaiting deployment
HANDOFF.md            — Session handoff document
R2-MULTI-BUCKET-ARCHITECTURE.md  — Canonical architecture doc
UNIFIED-ARCHITECTURE.md          — Canonical architecture doc
r2_archive_upload.ps1 — Active operational script
r2_archive_upload.py  — Active operational script
r2_releases_upload.ps1— Active operational script
setup_r2_env.ps1      — Environment setup script
rclone.exe            — Operational tool
check_papers.py       — Utility script
```

### Policy Analysis

The qnfo-agent §8.5.1 (File Lifecycle Classification) states:
> "Cloudflare R2 is the computer. This machine is the terminal."

And §3.1 (Session-Start Thin-Client Scan) mandates:
> "Delete ALL non-git project files from prior sessions"

**If this policy were STRICTLY enforced at this session start, ALL 18+ files above WOULD BE DELETED BEFORE WORK BEGINS.** This includes:
- The r2-gateway Worker source (would need to be re-written)
- The Shor research project (deliverables lost)
- All operational scripts (would need to be re-pulled from R2)
- Architecture documents (would need to be re-created)

### Root Cause

The thin-client mandate was designed for a scenario where R2 is the sole canonical storage and local disk is purely ephemeral. But in practice:
1. **Projects are actively worked on locally** before R2 upload
2. **Operational scripts need local persistence** for user access
3. **Documents are edited and saved locally** — R2 sync is a separate step
4. **The Google Drive → R2 migration** will add more local-first files

### Red-Team Challenge

**Assumption:** "All important files are already on R2, so local copies are safe to delete."
**Test:** Check if shor-phase3/ exists on R2.
**Result:** Unknown — but the local copy is the user's working copy. Deleting it before verifying R2 sync would destroy work.

### Recommendation

**Add a PROTECTED-FILE CLAUSE to §8.5.1 and §3.1:**
1. Files in project directories (`shor-phase3/`, `memory-infra/`) → NEVER auto-delete. Move to R2 THEN delete.
2. Scripts with intent to persist (`.ps1`, `.py` not `_`-prefixed) → NEVER auto-delete. Upload to R2 then delete.
3. Architecture documents (`.md` not `_`-prefixed) → NEVER auto-delete. Commit to git, then optionally delete.
4. **ONLY `_*`-prefixed files and `__pycache__/` are safe to auto-delete.**

**Proposed policy amendment to §3.1:**
```powershell
# Step 2 (REVISED): Delete ONLY ephemeral files, NEVER project files
# Ephemeral = _* prefix + __pycache__
Get-ChildItem -File -Name | Where-Object { $_ -match '^_' } | ForEach-Object { Remove-Item $_ }
# Project dirs, scripts, and docs are PROTECTED — they survive session boundaries
# They are uploaded to R2 at session closeout, THEN deleted
```

---

## FINDING F2 — HIGH: R2 Gateway Worker Not Deployed

### Evidence

- `r2-gateway/worker.js` exists locally (1,920 bytes of source code)
- No deployed Worker at `r2-gateway.q08.workers.dev`
- No `wrangler.jsonc` or deployment config
- Workers list (27 entries) does not include `r2-gateway`

### Impact

The 6-bucket fleet has NO centralized write path. All R2 writes happen through:
1. Direct Wrangler CLI (`npx wrangler r2 object put`) — bypasses validation
2. Direct Worker bindings (`env.QNFO_BUCKET`) — still references old `qnfo` bucket
3. No key validation, no lock acquisition, no write verification

This means: **the anti-patterns that caused 25% bucket pollution (undefined prefix bug) are NOT prevented.**

### Recommendation

1. Deploy the r2-gateway Worker with wrangler
2. Update Worker R2 bindings (see F3) 
3. Require all future R2 writes to use the gateway

---

## FINDING F3 — HIGH: Workers Still Binding to Deprecated `qnfo` Bucket

### Evidence

| Worker | R2 Binding | Uses Old Paths |
|:-------|:-----------|:--------------|
| archive-worker | `QNFO_BUCKET` | `qnfo/discovery/index.json` |
| paper-pipeline | `QNFO_BUCKET` | `discovery/index.json`, `audit/crons/`, `audit/vectorize-sync/` |
| qnfo-asset-api | `ASSETS_R2` | `discovery/index.json` |
| d1-backup-cron | `BACKUP_BUCKET` | `backups/d1/{name}/{date}/` |
| qnfo-lifecycle | (via Queue) | `qnfo/projects/`, `qnfo/archive/projects/` |

### Impact

These Workers read/write to the deprecated single `qnfo` bucket. When the bucket is deleted (30-day cooldown ends 2026-08-14), all 5 Workers will break.

### Recommendation

**For each Worker:**
1. Update R2 binding to point to correct new bucket:
   - archive-worker → `qnfo-audit` (for audit trails) or `qnfo-releases` (for papers)
   - paper-pipeline → `qnfo-audit` (for audit/crons/) + `qnfo-backups` (for backups)
   - qnfo-asset-api → `qnfo-assets` (already has `ASSETS_R2`, just redirect)
   - d1-backup-cron → `qnfo-backups`
   - qnfo-lifecycle → `qnfo-projects` (for project files), `qnfo-archive-projects` pattern
2. Update Worker source code to remove `qnfo/` path prefix
3. Deploy updated Workers

---

## FINDING F4 — MEDIUM: Archive Worker /health 404

### Evidence

```
GET https://qnfo-archive-worker.q08.workers.dev/health → HTTP 404
```

The Worker is deployed but its /health endpoint returns 404. This means:
- The lifecycle pipeline cannot verify archive Worker health
- The consolidated archive-worker (merged with qnfo-archive-worker) may have lost the /health route

### Impact

The archive Worker's health is unmonitorable through the standard /health endpoint. If it silently fails, archival jobs will be lost without alerting.

### Recommendation

Add a `/health` endpoint to the archive-worker that returns `{status: "ok", worker: "archive-worker-merged"}`.

---

## FINDING F5 — MEDIUM: KG/D1 Paper Node Drift

### Evidence

```
KG: /stats → Paper: 618 nodes
D1: living-paper.papers → 616 papers
Drift: 2 nodes
```

### Impact

Two papers exist in the KG but not in D1, or vice versa. This creates inconsistency in impact analysis and paper discovery.

### Recommendation

Run `cron-graph-re-seed` Worker to reconcile the KG with D1.

---

## FINDING F6 — MEDIUM: Skills with Stale `qnfo/` References

### Evidence

Skills with `qnfo/tools/` references that predate the 6-bucket migration:
- kaizen-autonomous-update — `qnfo/tools/deploy.py`, `qnfo/tools/kaizen_engine.py`, `qnfo/tools/system_audit.py`
- github-manager — `qnfo/tools/deploy.py`, `qnfo/tools/` recovery paths

These were NOT caught in the earlier skill update pass because they use `qnfo/tools/` patterns that differ from the patterns targeted (e.g., `qnfo/audit/`, `qnfo/releases/`).

### Recommendation

Update these skills to reference `qnfo-skills` bucket with correct path convention.

---

## FINDING F7 — LOW: No Google Drive → R2 Migration Pipeline

### Evidence

- rclone.exe present and configured with `archive` and `releases` remotes
- R2 upload scripts exist but only handle one-way sync (local → R2)
- No automated GDrive → R2 migration exists
- User has expressed intent to replace Google Drive with R2

### Impact

When Google Drive → R2 migration begins (planned), the system has no automated pipeline. The rclone mount (A:\, R:\) scripts no longer exist on disk.

### Recommendation

Create a `gdrive-to-r2-migration` skill or add Google Drive sync to `local-to-r2-migration`.

---

## FINDING F8 — LOW: Working Directory Policy vs Reality Gap

### Evidence

18+ files outside `.git/` exist in the working directory, including:
- Active research projects (shor-phase3/)
- Infrastructure code (memory-infra/, r2-gateway/)
- Operational scripts (5+ scripts)
- Architecture documents (3 docs)

The qnfo-agent §3.1 thin-client scan would delete ALL of these. But they survive because:
1. The user is in the middle of active work sessions
2. The agent correctly does NOT enforce the scan during active work
3. The policy says one thing; practice does another

This gap is PROTECTING the user's work. The risk is that a new agent session that STRICTLY follows the policy would destroy everything.

### Recommendation

**Align the policy with practice.** See F1. The thin-client scan should ONLY delete `_*` prefix and `__pycache__/` files. Everything else must be explicitly uploaded to R2 before local deletion.

---

## INFRASTRUCTURE HEALTH SUMMARY

| Component | Status | Detail |
|:----------|:------:|:-------|
| Knowledge Graph | ✅ Healthy | 2071 nodes, 1390 edges, 618 Papers, 92 Projects |
| Lifecycle Worker | ✅ Healthy | 86 projects, 27 ACTIVE, 32 ARCHIVED, 0 STALE |
| Lock Manager | ✅ Healthy | 0 active locks, no concurrent sessions |
| Data API | ✅ Healthy | 616 papers, 191 tasks, 55 handoffs |
| Archive Worker | ⚠️ Degraded | /health returns 404 |
| 27 Workers | Operational | 5 need R2 binding updates |
| R2 6-bucket fleet | Partial | Skills updated, gateway not deployed, bindings stale |

---

## PRIORITY ACTION MATRIX

| Priority | Action | Fix In |
|:---------|:-------|:------:|
| **P0** | Amend thin-client policy: NEVER auto-delete non-`_` files | This session |
| **P0** | Deploy r2-gateway Worker | Next session |
| **P1** | Update 5 Workers' R2 bindings to new bucket fleet | This week |
| **P1** | Add /health endpoint to archive-worker | This week |
| **P2** | Reconcile KG/D1 paper drift (cron-graph-re-seed) | This week |
| **P2** | Update kaizen-autonomous-update and github-manager skills for qnfo-skills bucket | Next session |
| **P3** | Create GDrive → R2 migration pipeline | When needed |
| **P3** | Align working directory policy with practice | Part of P0 |

---

*Red-Team Kaizen Report v1.0 — 2026-07-15 — QNFO Infrastructure Audit*
*Methodology: RED-TEAM → DoD → ITERATE → REFINE per red-team-dod v1.3*
