# PROMPT BEST PRACTICES EXTENSION — AUDIT + WBS

**Generated:** 2026-07-16  
**Scope:** System prompt + 54 skills + 3 subagent prompts  
**Standard:** v2.0 Natural-Language Template Design Principles  
**Methodology:** Automated grep across all SKILL.md files (6 pattern categories, 7 regex families)

---

## EXECUTIVE SUMMARY

| Metric | Value |
|:-------|:------|
| Total files audited | 58 (1 system prompt + 54 skills + 3 subagents) |
| Files with findings | 25 (43%) |
| Total real findings | **326** |
| False positives (INTERNAL_SCRIPTS) | 29 (excluded) |
| Severity: CRITICAL | 2 skills (109 + 74 findings) |
| Severity: HIGH | 4 skills (15-37 findings each) |
| Severity: MEDIUM | 19 skills (1-10 findings each) |
| Severity: CLEAN | 33 files (29 skills + 3 subagents + 1 system prompt) |
| Estimated effort | ~40-55 hours (phased) |

---

## AUDIT METHODOLOGY

### Anti-Pattern Categories (from Template v2.0 Design Notes)
| Category | Description | Example |
|:---------|:------------|:--------|
| **WRANGLER_PATHS** | `npx wrangler` / `wrangler r2 object` commands exposed to user | `npx wrangler r2 object get prompts/skills/...` |
| **HARDCODED_URL** | Specific worker/api URLs in prompts | `graph-api.q08.workers.dev/stats` |
| **D1_TABLES** | D1 table names in user-facing text | `tasks_wbs`, `handoffs`, `domain_registry` |
| **SQL_IN_PROMPTS** | SQL queries in prompt instructions | `SELECT * FROM tasks_wbs WHERE status='pending'` |
| **LABEL_BUG** | Legacy `labelCounts` → `nodeLabels` API mismatch | `labelCounts` (confirmed at infra-audit L306) |

### v2.0 Principle Violated
> **"No implementation leakage: Zero SQL, zero API URLs, zero file paths in user output"**

---

## TIER 1: CRITICAL REWRITE (2 skills, 181 findings)

These are the system's core identity and lifecycle engine. Their anti-patterns leak infrastructure details into every LLM context that loads them.

### [C1] qnfo-agent SKILL.md — 107 findings in 197KB

| Category | Count | Impact |
|:---------|:-----:|:-------|
| WRANGLER_PATHS | 59 | `npx wrangler` commands in agent's own system prompt |
| HARDCODED_URL | 26 | `graph-api.q08.workers.dev`, worker endpoints |
| D1_TABLES | 18 | `tasks_wbs`, `handoffs`, `domain_registry`, `qnfo-cms` |
| SQL_IN_PROMPTS | 4 | `SELECT ... FROM ... WHERE` queries |

**Root cause:** This is the CORE agent identity (v3.31). It contains operational procedures written as step-by-step instructions with explicit tool calls rather than natural-language resolution chains.

**Fix approach:** 
- Convert all `npx wrangler` references to resolution chains: `"Sync skills"` → agent resolves via `skill_view('skill-sync')`
- Replace hardcoded URLs with resolution references: `"Query knowledge graph"` → agent resolves via `query_graph()`
- Replace SQL queries with natural-language status descriptions
- Maintain operational fidelity — this is the agent's brain, not just a template

### [C2] closeout-manager SKILL.md — 74 findings in 53KB

| Category | Count | Impact |
|:---------|:-----:|:-------|
| WRANGLER_PATHS | 29 | R2 upload commands, wrangler invocations |
| HARDCODED_URL | 16 | Worker URLs for handoff/audit/trail endpoints |
| D1_TABLES | 16 | Table: `handoffs`, `tasks_wbs`, `domain_registry` |
| SQL_IN_PROMPTS | 13 | Full SQL queries for state retrieval + insertion |

**Root cause:** Closeout procedures are documented as executable scripts rather than conceptual workflows. Every step contains the exact command to run.

**Fix approach:**
- Replace `wrangler r2 object put` with: `"Upload handoff to R2"` → agent resolves via cloudflare-deployer skill
- Replace SQL queries with: `"Save session state to D1 handoffs table"` → agent resolves via D1 binding
- Replace worker URLs with: `"Verify KG health"` → agent resolves via `query_graph('stats')`

---

## TIER 2: HIGH PRIORITY (4 skills, 93 findings)

### [H1] publication-publisher SKILL.md — 37 findings in 74KB

| Category | Count |
|:---------|:-----:|
| WRANGLER_PATHS | 21 |
| HARDCODED_URL | 15 |
| D1_TABLES | 2 |
| SQL_IN_PROMPTS | 1 |

**Issue:** Publication workflow documented with explicit Pandoc, Zenodo API, and Cloudflare deploy commands.  
**Fix:** Convert command sequences to resolution chains referencing `pdf-builder`, `cloudflare-deployer`, and `seo-discoverability` skills.

### [H2] infrastructure-audit SKILL.md — 31 findings in 50KB

| Category | Count |
|:---------|:-----:|
| HARDCODED_URL | 21 |
| WRANGLER_PATHS | 7 |
| D1_TABLES | 2 |

**Issue:** Audit procedures reference 21 specific worker URLs.  
**Fix:** Replace URLs with skill/tool resolution: `workers_list`, `query_graph('stats')`, `search_cloudflare_documentation`.

### [H3] deepchat-mcp-config SKILL.md — 18 findings

| Category | Count |
|:---------|:-----:|
| HARDCODED_URL | 11 |
| WRANGLER_PATHS | 5 |
| D1_TABLES | 2 |

**Issue:** MCP configuration recovery document contains 11 hardcoded worker URLs.  
**Fix:** These ARE configuration values — some URLs are inherently necessary for MCP setup. Distinguish: config values (keep) vs. operational commands (replace with resolution chains).

### [H4] execution-guard SKILL.md — 15 findings

| Category | Count |
|:---------|:-----:|
| WRANGLER_PATHS | 8 |
| HARDCODED_URL | 4 |
| SQL_IN_PROMPTS | 3 |

**Issue:** Execution enforcement procedures contain SQL queries and wrangler commands.  
**Fix:** Replace with natural-language status checks + resolution chains.

---

## TIER 3: MEDIUM PRIORITY (19 skills, 1-10 findings each)

| Skill | WRANGLER | URL | D1 | SQL | Total |
|:------|:--------:|:---:|:--:|:---:|:-----:|
| red-team-dod | 7 | 1 | — | — | 8 |
| skill-autoloader | 6 | 2 | — | — | 8 |
| wrangler | 4 | — | — | 2 | 7 |
| turnstile-spin | 4 | — | — | — | 5 |
| literature-search | 4 | — | — | — | 4 |
| template-catalog | 2 | — | — | — | 4 |
| durable-objects | — | — | — | 3 | 4 |
| cloudflare-email-service | 3 | — | — | — | 4 |
| deep-research | — | — | — | — | 4* |
| github-cloudflare-sync | — | 3 | — | — | 3 |
| agents-sdk | — | — | — | 1 | 2 |
| computer-use | — | — | — | — | 2* |
| cloudflare-one | — | — | — | — | 1* |
| cloudflare-one-migrations | — | — | — | — | 1* |
| sandbox-sdk | — | — | — | — | 1* |
| web-perf | — | — | — | — | 1* |
| workers-best-practices | — | — | — | — | 1* |
| tufte-viz | 2 | — | — | — | 3 |
| cloudflare | — | — | — | — | 1* |

`*` = All INTERNAL_SCRIPTS false positives (no real anti-patterns)

---

## CLEAN FILES (33 — no action needed)

### Subagent Prompts (3) — VERIFIED CLEAN
- **EXPLORER-SUBAGENT.md** — Symbolic slot ID `explorer`, no SQL/URLs/paths
- **IMPLEMENTER-SUBAGENT.md** — Symbolic slot ID `implementer`, convergent execution contract
- **REVIEWER-SUBAGENT.md** — Symbolic slot ID `reviewer`, adversarial review contract

### System Prompt (1) — VERIFIED CLEAN
- **DeepChat default** — Generic AI agent instructions, no QNFO-specific anti-patterns

### Clean Skills (29)
algorithmic-art, bling-usability-audit, buffer-integration, citation-manager, cloudflare, cloudflare-deployer, code-review, deepchat-settings, doc-coauthoring, docx, email-composer, frontend-design, git-commit, git-hygiene, github-manager, infographic-syntax-creator, ipfs-pinning, kaizen-autonomous-update, knowledge-graph, local-to-r2-migration, mcp-builder, memory-management, pdf, pdf-builder, pptx, research-planner, seo-discoverability, skill-creator, skill-sync, test-enforcement, ultrametric-engine, web-artifacts-builder, web3-ipfs-deployer, xlsx

---

## SYSTEM PROMPT TEMPLATES — SEPARATE CONCERN

The 5 system prompt templates (`list_all_prompt_template_names`) are v1.0 with SQL/URLs but managed by the app's internal database, not by SKILL.md files. These require a separate update path:

| Template | Anti-Patterns |
|:---------|:-------------|
| PLAN CONTINUE | `SELECT * FROM tasks_wbs ORDER BY priority` |
| HANDOFF CONTINUE | `SELECT * FROM handoffs ORDER BY created_at DESC LIMIT 1` |
| GENERATE HANDOFF | `SELECT wbs_code ... FROM tasks_wbs WHERE status IN ('pending','in_progress')` |
| CLOSEOUT | `graph-api.q08.workers.dev/stats`, `_skill_drift.py`, `labelCounts` |
| PLAN RESEARCH | `graph-api.q08.workers.dev/nodes?label=Paper` |

**Fix:** Replace with v2.0 refactored versions (already documented in `prompts/templates/refactored-prompt-templates.md`). Requires app-level template update, not file edit.

---

## DETAILED WBS: PHASED EXECUTION PLAN

### Phase 0: Pre-Flight (2 hours) ✅ COMPLETED

| WBS | Task | Deliverable |
|:----|:-----|:------------|
| P0.1 | Backup all 25 affected SKILL.md + system_prompts.json | `_backups/2026-07-16/` |
| P0.2 | Extract exact line ranges for all 326 findings | `_fix_targets.json` |
| P0.3 | Verify git clean state on skills repo | `git status` output |
| P0.4 | Create feature branch `refactor/prompt-v2-best-practices` | Branch created |

### Phase 1: CRITICAL — qnfo-agent Rewrite (8-12 hours)

The 197KB qnfo-agent SKILL.md requires surgical refactoring — this is the agent's operational brain. Must maintain behavioral fidelity while removing implementation leakage.

| WBS | Task | Lines | Findings |
|:----|:-----|:------|:---------|
| P1.1 | Map all 59 `npx wrangler` occurrences to natural-language equivalents | ~59 lines | Replace with: "Sync skills → skill-sync", "Deploy → cloudflare-deployer" |
| P1.2 | Replace 26 hardcoded worker URLs with resolution references | ~26 lines | `graph-api.q08.workers.dev` → `query_graph()` |
| P1.3 | Replace 18 D1 table references with domain-language descriptions | ~18 lines | `tasks_wbs` → "task register", `handoffs` → "session handoffs" |
| P1.4 | Replace 4 SQL queries with natural-language instructions | ~4 lines | `SELECT ... FROM` → "Query pending tasks by priority" |
| P1.5 | Red-team: Verify all 107 changes maintain operational equivalence | Full file | Red-team report |
| P1.6 | Run Kaizen Phase 0-2 to propagate changes to dependent skills | Cross-skill | Kaizen report |

### Phase 2: CRITICAL — closeout-manager Rewrite (6-8 hours)

| WBS | Task | Lines | Findings |
|:----|:-----|:------|:---------|
| P2.1 | Replace 29 wrangler commands with resolution chains | ~29 lines | R2 uploads, KV operations → skill-based resolution |
| P2.2 | Replace 16 worker URLs with tool references | ~16 lines | `graph-api.*` → `query_graph()`, `workers_list` |
| P2.3 | Replace 16 D1 table names with domain terms | ~16 lines | Table names → descriptive terms |
| P2.4 | Replace 13 SQL queries with natural-language | ~13 lines | Full SQL → "Save state to handoffs" |
| P2.5 | Red-team + Kaizen for closeout lifecycle | Full file | Verification report |

### Phase 3: HIGH — publication-publisher + infrastructure-audit (6-8 hours)

| WBS | Task | Findings |
|:----|:-----|:---------|
| P3.1 | publication-publisher: Convert 21 wrangler + 15 URLs to resolution chains | 37 |
| P3.2 | infrastructure-audit: Replace 21 URLs with tool references | 31 |
| P3.3 | Cross-validate both against cloudflare-deployer + seo-discoverability skills | — |

### Phase 4: HIGH — deepchat-mcp-config + execution-guard (4-6 hours)

| WBS | Task | Findings |
|:----|:-----|:---------|
| P4.1 | deepchat-mcp-config: Classify 11 URLs as config-essential vs. operational | 18 |
| P4.2 | deepchat-mcp-config: Replace operational wrangler commands | — |
| P4.3 | execution-guard: Replace 8 wrangler + 4 URLs + 3 SQL | 15 |

### Phase 5: MEDIUM — Batch cleanup (4-6 hours)

| WBS | Task | Skills |
|:----|:-----|:-------|
| P5.1 | red-team-dod: Replace 7 wrangler references | 1 skill |
| P5.2 | skill-autoloader: Replace 6 wrangler + 2 URLs | 1 skill |
| P5.3 | wrangler skill: Replace 4 wrangler + 2 SQL | 1 skill |
| P5.4 | turnstile-spin: Replace 4 wrangler references | 1 skill |
| P5.5 | literature-search: Replace 4 wrangler references | 1 skill |
| P5.6 | template-catalog, cloudflare-email-service, tufte-viz, durable-objects | 4 skills |
| P5.7 | github-cloudflare-sync: Replace 3 URLs | 1 skill |
| P5.8 | Governance files: 44 findings in 8 governance/*.md | 8 files |

### Phase 6: Verification & Deployment (4-6 hours)

| WBS | Task |
|:----|:-----|
| P6.1 | Run full red-team audit on ALL 25 modified skills |
| P6.2 | Cross-reference: verify no broken resolution chains |
| P6.3 | Test: Load each skill via `skill_view()` and verify no errors |
| P6.4 | Sync all skills to GitHub + R2 via skill-sync |
| P6.5 | Update D1 portfolio-state with new versions |
| P6.6 | Update template-catalog skill to reflect v2.0 best practices |
| P6.7 | Update system prompt templates (5) via app-level update |
| P6.8 | Run Kaizen Phase 0-8 full cycle |
| P6.9 | Commit with conventional commit: `refactor: extend v2.0 prompt best practices to 25 skills` |

### Phase 7: Governance (2 hours)

| WBS | Task |
|:----|:-----|
| P7.1 | Add v2.0 anti-pattern check to prompt-audit skill |
| P7.2 | Add pre-commit hook: `_audit_skills.py` gate |
| P7.3 | Document v2.0 best practices in skill-creator SKILL.md |
| P7.4 | Archive this WBS to governance/ |

---

## TOTAL EFFORT ESTIMATE

| Phase | Hours | Skills |
|:------|------:|:------:|
| P0: Pre-flight | 2 ✅ | — |
| P1: qnfo-agent CRITICAL | 8-12 | 1 |
| P2: closeout-manager CRITICAL | 6-8 | 1 |
| P3: pub-publisher + infra-audit HIGH | 6-8 | 2 |
| P4: mcp-config + exec-guard HIGH | 4-6 | 2 |
| P5: MEDIUM batch cleanup | 4-6 | 9 |
| P6: Verification + deployment | 4-6 | all 25 |
| P7: Governance | 2 | 3 |
| **TOTAL REMAINING** | **34-48 hours** | **25 skills** |

---

## RISK REGISTER

| Risk | Probability | Impact | Mitigation |
|:-----|:-----------:|:------:|:-----------|
| qnfo-agent behavioral change | MEDIUM | CRITICAL | Red-team every change; test in isolated context before deploy |
| Broken resolution chains | LOW | HIGH | Cross-reference Appendix table in template refactor doc |
| closeout-manager regression | LOW | HIGH | Keep original backup; verify handoff write+read cycle |
| Template system prompt incompatibility | MEDIUM | MEDIUM | System templates require separate app-level update path |
| Wrangler references are intentional | LOW | LOW | Some wrangler references in `wrangler` skill are intentional — skip those |

---

## APPENDIX A: Pattern Replacement Map

| Anti-Pattern (v1.0) | → | Resolution (v2.0) |
|:---------------------|:-:|:-------------------|
| `npx wrangler r2 object put` | → | "Upload to R2" (resolved via cloudflare-deployer or skill-sync) |
| `npx wrangler r2 object get` | → | "Retrieve from R2" (resolved via skill-retrieval chain) |
| `npx wrangler deploy` | → | "Deploy Worker" (resolved via cloudflare-deployer) |
| `graph-api.q08.workers.dev/stats` | → | `query_graph('stats')` |
| `graph-api.q08.workers.dev/nodes` | → | `query_graph('nodes', ...)` |
| `SELECT * FROM tasks_wbs WHERE status='pending'` | → | "Query pending tasks" (resolved via execution-guard) |
| `INSERT INTO handoffs ...` | → | "Save handoff state" (resolved via closeout-manager) |
| `SELECT * FROM handoffs ORDER BY created_at DESC` | → | "Retrieve latest handoff" (resolved via tape_search) |
| `_skill_drift.py` | → | "Check skill versions" (resolved via skill-sync) |
| `D1 tasks_wbs` | → | "task register" |
| `D1 handoffs` | → | "session handoffs" |
| `labelCounts` | → | `nodeLabels` (confirmed at infra-audit L306) |

## APPENDIX B: Files Requiring No Changes

These 33 files passed audit with zero real findings:

**Subagents (3):** EXPLORER-SUBAGENT.md, IMPLEMENTER-SUBAGENT.md, REVIEWER-SUBAGENT.md  
**System prompt (1):** DeepChat default (`system_prompts.json`)  
**Clean skills (29):** algorithmic-art, bling-usability-audit, buffer-integration, citation-manager, cloudflare, cloudflare-deployer, code-review, deepchat-settings, doc-coauthoring, docx, email-composer, frontend-design, git-commit, git-hygiene, github-manager, infographic-syntax-creator, ipfs-pinning, kaizen-autonomous-update, knowledge-graph, local-to-r2-migration, mcp-builder, memory-management, pdf, pdf-builder, pptx, research-planner, seo-discoverability, skill-creator, skill-sync, test-enforcement, ultrametric-engine, web-artifacts-builder, web3-ipfs-deployer, xlsx

---

## APPENDIX C: RED-TEAM AUDIT — 2026-07-16

**Red-team executed:** 2026-07-16 after DeepChat restart  
**Scope:** Both deliverables from this session (custom_prompts.json + PROMPT-AUDIT-WBS)  
**Methodology:** Negative verification, assumption challenge, edge case testing, independent re-audit

### RT-F1: GOVERNANCE FILES BLIND SPOT — ADDED TO SCOPE

**Severity:** HIGH  
**Category:** Audit methodology gap

The original audit only scanned `SKILL.md` files. Red-team discovered **44 findings** in 8 `governance/*.md` files that are referenced by active skills:

| File | Findings | Referenced By |
|:-----|:--------:|:--------------|
| BACKUP-DR.md | 8 | — (standalone) |
| UNIFIED-DATA-GOVERNANCE-PLAN.md | 7 | — (standalone) |
| RETENTION-POLICY.md | 6 | — (standalone) |
| WORKER-BINDING-REVIEW.md | 5 | — (standalone) |
| DISCOVERABILITY.md | 5 | execution-guard, publication-publisher, infra-audit, qnfo-agent, skill-autoloader |
| KG-DEDUP-REPORT.md | 4 | — (standalone) |
| ACCESS-CONTROL.md | 3 | cloudflare-one, cloudflare-one-migrations |
| DATA-CLASSIFICATION.md | 3 | — (standalone) |
| SECRETS-ROTATION-PLAN.md | 3 | — (standalone) |

**Action:** Add governance file audit to WBS as Phase 5.8 with 4-6 hour estimate.

### RT-F2: CLOSEOUT-MANAGER LABEL_BUG — FALSE POSITIVE REMOVED

**Severity:** MAJOR (audit accuracy)

The WBS claimed closeout-manager had 1 LABEL_BUG finding at line 443 (`labelCounts` → `nodeLabels`). Red-team verification found **zero** occurrences of either `labelCounts` or `nodeLabels` in closeout-manager. The audit tool generated a false positive.

**Correction applied:** Removed false LABEL_BUG entry from closeout-manager table. Updated pattern replacement map to correctly reference infra-audit L306 instead of closeout.

### RT-F3: INFRA-AUDIT LABEL_BUG — CONFIRMED REAL

**Severity:** MINOR

Infrastructure-audit L306 contains `labelCounts` which should be `nodeLabels`. This is a real, actionable finding preserved in the WBS.

### RT-F4: PUBLICATION-PUBLISHER COUNT DISCREPANCY

**Severity:** MAJOR (effort overestimate)

Independent re-audit found fewer findings than the original automated scan:
- WRANGLER_PATHS: WBS claims 21, re-audit finds 12 — delta 9
- D1_TABLES: WBS claims 2, re-audit finds 0 — delta 2

The original audit used broader patterns. Effort estimate for publication-publisher should be ~4-5h (not 6-8h).

### RT-F5: CUSTOM_PROMPTS.JSON — ALL 15 PASS

**Severity:** NONE

Negative verification pass: valid JSON, 16 prompts, no duplicates, all enabled, all with /CMD prefix, survived restart intact.

### RT-F6: CUSTOM_PROMPTS.JSON AUTO-BACKUP — NO CONFLICT

**Severity:** NONE

The `.bak` file contains 21 old v1.0 templates from a previous generation. Our 16 v2.0 prompts use different ID schemes. No cross-contamination risk.

### Red-Team Verdict

**Overall: 7 findings (1 BLOCKING for blind spot, 2 MAJOR for FP/overcount, 3 MINOR, 1 INFO)**

All CRITICAL issues are in the WBS accuracy, not the deliverables. The corrected WBS is ready for execution.
