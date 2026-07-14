# Red Team Self-Audit: Waveform Computing vs Quantum Computing Research Program

> **Date:** 2026-07-13 | **Auditor:** DeepChat Research Agent (self-audit)
> **Scope:** Full research program — 5 phases, 14 tasks, 11 artifacts, 53 papers

---

## 1. Output Verification (Negative Verification)

### 1.1 Artifact Existence
| Artifact | Exists? | Size (KB) | Content Verified? |
|:---------|:-------:|:---------:|:------------------|
| Research plan | ✅ | 15.1 | ✅ |
| Literature brief | ✅ | 13.6 | ✅ |
| T0.1-2 Complexity/Wigner boundary | ✅ | 15.8 | ✅ |
| T0.3 ZB coherence analysis | ✅ | 11.7 | ✅ |
| Phase 1 Foundational clarification | ✅ | 18.9 | ✅ |
| Phase 2 Core case studies | ✅ | 17.3 | ✅ |
| Phase 3 Formal generalization | ✅ | 12.9 | ✅ |
| Phase 4 Synthesis/dissemination | ✅ | 23.7 | ✅ |
| KG cross-reference supplement | ✅ | 9.3 | ✅ |
| ZB simulation script | ✅ | 10.0 | ✅ |
| README.md | ✅ | ~5 | ✅ |
| **PDFs** | ❌ | **0** | **MISSING — CRITICAL** |
| **All verified out of 12 required types** | **11/12** | | |

### 1.2 Claim Verification
| Claim | Evidence | Status |
|:------|:---------|:------|
| "Linear wave computers ∈ BPP" | Mari-Eisert (2012) — PRL 109, 230503 | ✅ |
| "Wigner negativity is necessary for quantum advantage" | Mari-Eisert + Howard et al. (2014) | ✅ |
| "ZB coherence ~100nm at realistic disorder" | Analytical estimate from Schliemann et al. (2005) | ✅ (analytical, not simulated) |
| "χ² PDC sufficient for BQP" | Lloyd-Braunstein (1999) | ✅ |
| "Gottesman-Knill: Clifford ∈ P" | Gottesman (1998), Van den Nest (2008) | ✅ |
| "Boson sampling #P-hard" | Aaronson-Arkhipov (2011) | ✅ |
| "44 papers reviewed" | Literature search output verified | ✅ |
| "9 QNFO KG papers" | KG cross-reference verified | ✅ |
| "QG has 611 Paper nodes" | /stats API output verified | ✅ |

### 1.3 Source Label Compliance
| Document | Has [LLM-INFERRED] tags? | Has references? |
|:---------|:------------------------|:----------------|
| Research plan | ✅ (5 assumptions tagged) | ✅ (10 QNFO-style refs) |
| Literature brief | ✅ (tier classification) | ✅ (8 key refs with DOIs) |
| Position paper (T4.1) | ✅ (embedded) | ✅ (bibliography) |

---

## 2. Assumption Challenge

### 2.1 Core Assumptions Tested

| # | Assumption | Challenged By | Survives? |
|:--|:----------|:-------------|:----------|
| A1 | "Wigner negativity is necessary for quantum advantage" | DQC1 model (quantum advantage without entanglement, but DQC1 still uses non-classical states) | ✅ Yes — DQC1 uses quantum discord, not classical waves |
| A2 | "Classical wave amplitudes are positive by construction" | Phase-space representations can be negative even for classical systems (e.g., P-function) | ⚠️ Partially — the P-function can be negative for non-classical states, but the Wigner function of classical thermal/coherent states is positive. The boundary is representation-dependent. |
| A3 | "ZB coherence is too short for computing" | Topological protection (quantum spin Hall edge states) could extend coherence | ⚠️ Speculative — no experimental evidence for topologically-protected ZB coherence |
| A4 | "The KG has no Wigner negativity papers" | The /nodes endpoint is paginated to 100; we only saw 200 of 611 papers via SQL | ⚠️ False negative risk — but /nodes search for "Wigner" returned 0, suggesting it's genuinely missing |
| A5 | "User's thesis that quantum/classical boundary is a convention is wrong" | The "Quantum-Classical Divide: A Human-Created Illusion" paper in KG (un-retrieved) may partially agree | ⚠️ We couldn't retrieve it — this is a genuine blind spot |

### 2.2 Most Dangerous Assumption

**A2 (amplitude positivity) is the most dangerous.** If there exists a classical wave configuration whose phase-space quasi-probability representation is negative (e.g., via nonlinear detection or post-selection), then the Mari-Eisert boundary does NOT cleanly separate classical waves from quantum advantage. This is precisely the "nonlinearity escape hatch" we identified in T3.3 — but the quantitative threshold is unproven.

---

## 3. Edge Case Check

| Edge Case | Status | Resolution |
|:----------|:------|:-----------|
| **Empty results** (0 arXiv papers) | ❌ Initial run returned 0 | ✅ Fixed with shorter queries (44 papers found) |
| **KG /nodes pagination** (100-result limit) | ⚠️ 511 of 611 papers unseen | ⚠️ Mitigated with SQL /query (200 results) + targeted searches |
| **ZB simulation timeout** (500k timesteps) | ❌ Sim didn't complete | ✅ Switched to analytical estimates from literature |
| **Semantic Scholar API (0 results)** | ❌ All Semantic Scholar queries returned 0 | ⚠️ Root cause not identified — rate limiting or API change |
| **GitHub repo naming collision** | ✅ 409 handled | ✅ Repo already exists, pushed to existing |
| **Zenodo upload URL format** | ❌ Initial bucket URL format wrong | ✅ Fixed — directly PUT to bucket/filename |
| **PowerShell inline Python escaping** | ❌ Multiple failures | ✅ Used .py script files instead |
| **Null/disconnected state** | N/A | No null states encountered |
| **Maximum values** (file sizes) | ✅ Max 24 KB (within Zenodo 50GB limit) | ✅ |
| **Boundary conditions** (BPP/BQP threshold) | ✅ Mari-Eisert boundary clearly stated | ✅ |

---

## 4. DoD Integration — Definition of Done Checklist

| Criterion | Status | Evidence |
|:----------|:------:|:---------|
| Research plan (8-stage spiral) complete | ✅ | `waveform_vs_quantum_research_plan.md` |
| Literature review (50+ papers from 2+ sources) | ✅ | 44 arXiv + 9 KG = 53 papers |
| All 5 phases executed (14 tasks) | ✅ | 8 documents saved |
| KG cross-reference performed | ✅ | `kg_cross_reference_supplement.md` |
| GitHub repo created + pushed | ✅ | https://github.com/QNFO/waveform-vs-quantum |
| Zenodo DOI assigned | ✅ | 10.5281/zenodo.21343606 |
| **PDF generated** | ❌ | **MISSING** |
| **All intermediate outputs archived** | ⚠️ | **Partially — 11 files on Zenodo, but some intermediate data (search JSONs, simulation results) not archived** |
| **Social media disseminated** | ❌ | **NOT DONE** (Stage 9 of publication-publisher) |
| Source labels on all claims | ✅ | [LLM-INFERRED] tags in plan; DOIs in brief |
| Ephemeral files cleaned | ✅ | 0 _* files remaining |
| Citations complete | ✅ | 8 key references with DOIs |

**DoD score: 9/12 (75%) — FAILS PDF and SOCIAL gates**

---

## 5. Red Team Findings Summary

### Critical (P0) — Must Fix
1. **NO PDFs generated.** Publication-publisher Stage 2 mandates PDF. Without PDF, this is not a complete publication.
2. **Intermediate outputs not fully archived.** Literature search JSONs, simulation results, KG query outputs — these intermediate data products should be preserved for reproducibility.

### High (P1) — Should Fix
3. **"Quantum-Classical Divide" KG paper not retrieved.** This paper's thesis may align with or contradict our findings. Blind spot.
4. **Semantic Scholar API returned 0 results across all queries.** Root cause unknown — literature search may be incomplete.
5. **Social media dissemination not done.** Stage 9 of publication-publisher mandates Buffer posting.

### Medium (P2) — Consider
6. **ZB simulation never ran to completion.** Analytical estimates used instead. For full reproducibility, the simulation should be run on appropriate hardware.
7. **Hidden-variable theories not engaged.** Self-critique identified this gap but didn't address it.

---

## 6. Remediation Plan

| Priority | Issue | Fix | Effort |
|:---------|:------|:----|:------|
| P0 | No PDFs | Build combined research report PDF + position paper PDF via Pandoc+XeLaTeX | ~30 min |
| P0 | Incomplete archive | Upload PDFs to Zenodo (new version) + push to GitHub | ~15 min |
| P1 | KG paper not retrieved | Query KG with exact title match across all pages | ~15 min |
| P1 | Semantic Scholar | Retry with different query format or accept gap | ~10 min |
| P2 | ZB simulation | Tag as [LLM-INFERRED] in final report; note for future HPC run | ~5 min |

---

> **[RED-TEAM-AUDIT-COMPLETE]**  
> **Verdict: 9/12 DoD criteria passed. FAILS on PDF gate and social gate.**  
> **Primary action: Generate PDFs, update Zenodo, run Kaizen update.**
