# UNIFIED PUBLICATION ARCHITECTURE — v3.0

**QNFO Full-Stack Architecture Document**
**Last Updated:** 2026-07-14
**Compliant With:** ADR-2026-007 (WBS), ADR-2026-008 (D1 Canonical), ADR-2026-011 (Universal Registry), ADR-2026-012 (FK Constraints), ADR-2026-013 (R2 WBS Keys)

---

## 1. Architecture Overview

The QNFO platform is a multi-tier research publication and discovery system built on Cloudflare's edge infrastructure. It follows a **D1-as-canonical-store, R2-as-immutable-storage, Workers-as-compute** architecture.

### 1.1 System Layers

| Layer | Technology | Role |
|:------|:-----------|:-----|
| **Compute** | Cloudflare Workers (26) | API endpoints, processing, lifecycle |
| **Database** | Cloudflare D1 (6 databases) | Canonical source of truth, relational data |
| **Storage** | Cloudflare R2 (`qnfo` bucket) | Immutable artifacts, PDFs, backups |
| **Search** | Vectorize (4 indexes) | Semantic search, paper embeddings |
| **Graph** | graph-api Worker (Neo4j-backed) | Knowledge graph, relationship queries |
| **DNS/Routing** | Cloudflare Pages (10 projects) | Public-facing websites |
| **Queue** | Cloudflare Queues | Event-driven pipeline |
| **KV** | Cloudflare KV (1 namespace) | Ephemeral state, caching |

### 1.2 Data Flow

```text
[Research] -> [Markdown] -> [Pandoc+XeLaTeX] -> [PDF]
    |              |                                  |
    v              v                                  v
[D1 papers]   [D1 papers.body_md]              [R2 qnfo/papers/]
    |              |                                  |
    +--------------+----------------------------------+
                   |
                   v
          [graph-api KG nodes + edges]
                   |
                   v
          [Vectorize embeddings]
                   |
                   v
          [Pages public sites]
```

---

## 2. D1 Database Architecture

### 2.1 Database Inventory

| Database | UUID | Purpose | Key Tables |
|:---------|:-----|:--------|:-----------|
| `living-paper` | `70a58cb3-...` | Paper content, metadata | papers, authors, citations |
| `qnfo-audit` | `35e2e573-...` | Infrastructure audit, tasks | tasks, audit_workers, audit_pages, project_ledger |
| `qnfo-graph` | — | Graph database backing | kg_nodes, kg_edges |
| `qwav-search` | — | Search index metadata | search_index |
| `wbs-state` | — | Work breakdown structure | portfolios, programs, projects, phases, tasks_wbs |
| `discovery-registry` | — | Resource discovery | skills_index, discovery_projects |

### 2.2 WBS Hierarchy (ADR-2026-007)

All work is organized under hierarchical WBS codes:
```text
PORTFOLIO > PROGRAM > PROJECT > PHASE > TASK > SUBTASK
```

Tables enforce referential integrity via foreign keys:
- `portfolios` (root)
- `programs` -> FK `portfolios.portfolio_id`
- `projects` -> FK `programs.program_id`
- `phases` -> FK `projects.project_id`
- `tasks_wbs` -> FK `phases.phase_id`

A single 4-JOIN query traces any task_code to its portfolio unambiguously.

---

## 3. R2 Storage Architecture

### 3.1 Key Structure (ADR-2026-013)

All R2 object keys follow WBS-keyed pattern:
```text
projects/<PORTFOLIO.PROGRAM.PROJECT.PX.TY>/<filename>
```

Protected paths (no deletion without explicit authorization):
- QNFO-RELEASES bucket: `papers/` — Published paper artifacts
- QNFO-RELEASES bucket: `releases/` — Release artifacts
- QNFO-SKILLS bucket: `prompts/skills/` — Skill definitions
- QNFO-SKILLS bucket: `tools/` — Tool scripts

### 3.2 Storage Responsibilities

| Data Type | Primary Store | Backup | Notes |
|:----------|:-------------|:-------|:------|
| Paper metadata | D1 `papers` | R2 `backups/` | D1 is canonical |
| Paper body (markdown) | D1 `papers.body_md` | R2 qnfo-releases bucket: `papers/` | Both must exist before clearing D1 |
| PDFs | R2 qnfo-releases bucket: `papers/` | Zenodo | Immutable |
| Audit trail | D1 `qnfo-audit` | R2 `backups/` | Append-only |
| Skills | R2 qnfo-skills bucket: `prompts/skills/` | GitHub | R2 is canonical deployment |
| Discovery index | D1 `discovery-registry` | R2 | Auto-synced |

---

## 4. Knowledge Graph Architecture

### 4.1 Graph Schema

Node labels: Paper, ZenodoRecord, CloudflareAsset, R2Object, Project, Task, Skill, ResearchQuestion, Concept, Finding, Decision, OpenItem, Phase, Template, Domain, WorkerEndpoint, Handoff, Deployment, Session, WorkerRoute, Organization, Person, Publication, Theorem

Edge types: CITES, AUTHORED_BY, HAS_DOMAIN, BELONGS_TO, HAS_DEPLOYMENT, USES, REFERENCES, IMPLEMENTS

### 4.2 Seeding

The `cron-graph-re-seed` Worker regenerates Paper, ZenodoRecord, and other nodes from D1 data sources on a scheduled basis. Recovery from Paper=0 is handled automatically through this mechanism.

---

## 5. Publication Pipeline

### 5.1 End-to-End Flow

1. **Research** → Markdown manuscript in git
2. **Format** → Pandoc + XeLaTeX → PDF
3. **Publish** → D1 paper record + R2 PDF upload + Zenodo DOI
4. **Seed** → KG Paper node + CITES edges
5. **Embed** → Vectorize embedding (qwav-research-v2)
6. **Deploy** → Cloudflare Pages static site
7. **Disseminate** → Buffer social media posts
8. **Archive** → lifecycle Worker archive trigger

### 5.2 Safety Gates (execution-guard skill)

Before any mutation operation:
1. **D1↔R2 Integrity**: Content must exist in at least one system
2. **Protected R2 Paths**: No deletion of protected paths
3. **D1 Mutation Safety**: R2 backup required before clearing body_md
4. **Vectorize Coverage**: Semantic index health check
5. **KG Sync**: Paper node coverage verification
6. **Architecture Doc**: UNIFIED-ARCHITECTURE.md must be on R2

---

## 6. Worker Inventory (26)

### 6.1 Core Services
- `papers-server` / `papers-server-production`: Paper API
- `graph-api`: Knowledge Graph API
- `search-worker`: Full-text search
- `qnfo-edge-router`: DNS/domain routing
- `qnfo-data-api`: Unified data API

### 6.2 Research & Computation
- `qwav-unified`: QWAV unified service
- `murtagh-engine`: Computation engine
- `braid-matrix`: Matrix computation
- `ultrametric-tree-api`: P-adic/ultrametric search
- `qnfo-ai-worker`: AI/LLM processing
- `paper-pipeline`: Paper processing pipeline

### 6.3 Infrastructure & Operations
- `qnfo-lifecycle`: Project lifecycle management
- `cron-graph-re-seed`: KG paper node regeneration
- `d1-backup-cron`: Daily D1→R2 backups
- `registry-sync`: CF resource→D1 audit sync
- `infra-lock-manager`: Distributed locking
- `archive-worker`: Paper archival automation
- `audit-worker`: Infrastructure auditing

### 6.4 APIs & Gateways
- `api-gateway`: API gateway
- `portfolio-api`: Portfolio management
- `qnfo-asset-api`: Asset management
- `qnfo-agent-session`: Agent session management
- `paper-catalog`: Paper catalog
- `ask-qwav`: Q&A interface
- `ipatent-api`: Patent analysis

---

## 7. Cross-System Integrity Rules

1. **GitHub↔D1**: GitHub issues (QNFO/QWAV) must mirror D1 `qnfo-audit.tasks` (source=`github`)
2. **D1↔R2**: Paper body_md must be backed up to R2 before clearing from D1
3. **D1↔KG**: Every D1 paper must have a KG Paper node
4. **D1↔Vectorize**: Papers with body_md should have Vectorize embeddings
5. **R2↔Pages**: Static sites deployed from R2 content
6. **Skills↔R2**: All 55 skills synced to R2 qnfo-skills bucket: `prompts/skills/`

---

## 8. Page Projects (10)

| Project | Subdomain | Purpose |
|:--------|:----------|:--------|
| qnfo-hub | qnfo.pages.dev | Main QNFO portal |
| qwav-scan | qwav-scan.pages.dev | QWAV scanner |
| ultrametric-playground | ultrametric.pages.dev | P-adic playground |
| papers | papers.qnfo.org | Paper distribution |
| citations | citations.qnfo.org | Citation graph UI |
| registry | registry.qnfo.org | Infrastructure registry |
| archive | archive.qnfo.org | Paper archive |
| skills | skills.qnfo.org | Skill discovery |
| research | research.qnfo.org | Research programs |
| dashboard | dashboard.qnfo.org | Operational dashboard |

---

**Document Status:** Active | **Next Review:** 2026-10-14
**Canonical Location:** R2 `qnfo/UNIFIED-ARCHITECTURE.md`
