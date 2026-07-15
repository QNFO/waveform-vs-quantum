# QNFO R2 Multi-Bucket Architecture â€” v1.0

**Date:** 2026-07-15
**Status:** ACTIVE â€” replaces single `qnfo` bucket
**Decision:** ADR-013-REVISED

## Architecture Overview

The QNFO R2 infrastructure has been migrated from a single `qnfo` bucket to a fleet of 6 domain-specific buckets. This eliminates the single point of failure where one corrupted key or accidental delete could affect all data.

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚              THE QNFO R2 BUCKET FLEET                         â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                                â”‚
â”‚  qnfo-releases     qnfo-skills       qnfo-audit               â”‚
â”‚  (publications)    (DeepChat skills)  (audit trails)           â”‚
â”‚                                                                â”‚
â”‚  qnfo-projects     qnfo-backups      qnfo-assets              â”‚
â”‚  (WBS projects)    (disaster recvry) (static web assets)      â”‚
â”‚                                                                â”‚
â”‚  qnfo (DEPRECATED â€” read-only archive)                        â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## Bucket Specification

| Bucket | Domain | Content | Migration Count |
|:-------|:-------|:--------|:---------------:|
| `qnfo-releases` | Publications | papers/{slug}/paper.md, PROVENANCE-BUNDLE.zip, README.md | 20 |
| `qnfo-skills` | DeepChat skills | prompts/skills/{name}/SKILL.md, tools/ | 39 |
| `qnfo-audit` | Audit trails | audit/conversations/, kaizen/ | 1 |
| `qnfo-projects` | WBS projects | projects/{id}/{file} | 3 |
| `qnfo-backups` | Disaster recovery | D1 snapshots, KV dumps | 0 |
| `qnfo-assets` | Static web assets | CSS, JS, fonts, images | 0 |

## Path Convention (CANONICAL)

**The bucket IS the namespace.** Keys MUST NOT include the bucket name as a prefix.

| Correct âœ… | Wrong âŒ |
|:----------|:--------|
| `papers/{slug}/paper.md` (on qnfo-releases) | `qnfo/papers/{slug}/paper.md` |
| `prompts/skills/{name}/SKILL.md` (on qnfo-skills) | `qnfo/prompts/skills/{name}/SKILL.md` |
| `projects/{id}/{file}` (on qnfo-projects) | `qnfo/projects/{id}/{file}` |

## Migration Summary (2026-07-15)

- **63 objects migrated** from `qnfo` â†’ 6 new buckets
- **0 failures** â€” all objects verified with writeâ†’verifyâ†’confirm cycle
- **20 banned `qnfo/` prefix violations** corrected to flat paths
- **Old `qnfo` bucket:** Retained as read-only archive (DEPRECATED.md marker uploaded)
- **30-day cooldown:** Bucket retained until 2026-08-14, then may be deleted

## R2 Gateway Worker (Created - Needs Deploy)

All future R2 writes go through the `r2-gateway` Worker at `POST /write`:
1. Validates keys with `validateR2Key()`
2. Acquires InfraLockManager DO lock
3. Writes to target bucket
4. Verifies with REST API
5. Registers in D1 portfolio-state.resources
6. Releases lock


### Workers Needing R2 Binding Updates

| Worker | Old Binding | New Bucket | Status |
|:-------|:------------|:-----------|:------:|
| archive-worker | QNFO_BUCKET → qnfo | qnfo-audit | Needs deploy |
| paper-pipeline | QNFO_BUCKET → qnfo | qnfo-audit + qnfo-backups | Needs deploy |
| qnfo-asset-api | ASSETS_R2 → qnfo | qnfo-assets | Needs deploy |
| d1-backup-cron | BACKUP_BUCKET → qnfo | qnfo-backups | Needs deploy |
| qnfo-lifecycle | QUEUE → archive-worker | qnfo-projects (path refs) | Needs deploy |

## Skills Requiring Update

| Skill | R2 References | Status |
|:------|:-------------|:-------|
| infrastructure-audit | Bucket inventory, R2 paths | âœ… Updated v2.10 |
| skill-sync | `qnfo/tools/`, skill backup paths | âš ï¸ Needs update |
| publication-publisher | `qnfo/releases/`, R2 archival paths | âš ï¸ Needs update |
| local-to-r2-migration | `qnfo/projects/`, wrangler commands | âš ï¸ Needs update |
| cloudflare-deployer | Bucket name, R2 command examples | âš ï¸ Needs update |

## Lessons Applied (from infrastructure-audit Â§0.12.1)

| Rule | How Architecture Prevents Recurrence |
|:-----|:-------------------------------------|
| R1: Never trust wrangler stdout | R2 Gateway enforces REST API verification |
| R2: Always paginate | D1 registry is SQL-backed (natural pagination) |
| R3: Guard template literals | `validateR2Key()` rejects `undefined` prefixes |
| R4: Bucket IS namespace | Flat keys on domain-specific buckets |
| R5: Writeâ†’verifyâ†’confirm | Gateway enforces: PUT â†’ GET â†’ compare â†’ register |
| R6: DELETEs irreversible | Old bucket archived, not deleted. 30-day cooldown. |
| R7: Centralized paths | ONE place (gateway Worker) constructs all keys |
| R8: DO locks | InfraLockManager integrated into gateway |
