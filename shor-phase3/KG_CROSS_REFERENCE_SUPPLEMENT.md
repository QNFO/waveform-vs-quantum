# KG Cross-Reference Supplement: Shor's Assumptions Research

**Generated:** 2026-07-14 | **KG Version:** v2.5 (3,242 nodes, 4,697 edges)

---

## 1. KNOWNLEDGE GRAPH GAP ANALYSIS

### What the KG Contains That Was Not Cross-Referenced

The QNFO Knowledge Graph contains **611 Paper nodes, 48 ResearchQuestions, and 41 Findings** spanning the QWAV Physics domain. My Shor assumptions research plan (18 tasks across 6 phases) was executed purely from training knowledge without cross-referencing any of these internal resources.

### Direct Hit: Papers on Shor and Quantum Advantage

| KG Paper ID | Title | Relevance |
|:------------|:------|:----------|
| `paper-feynman-shor-quantum-bifurcation` | **Feynman-Shor Quantum Bifurcation** | **DIRECT** — explicitly addresses Shor's algorithm. Authors: QNFO Research. Published. Stored in living-paper D1. |
| `paper-geometric-quantum-advantage` | **GEOMETRIC QUANTUM ADVANTAGE** | **DIRECT** — explicitly addresses quantum advantage. Authors: QNFO Research. Published. Stored in living-paper D1. |

Both papers are QNFO publications in the living-paper D1 database. Either (or both) may already contain analysis that overlaps with or extends beyond the Shor assumptions research conducted here.

### Adjacent: Quantum Error Correction & Physical Feasibility

| KG Paper ID | Title | Relevance to Shor Assumptions |
|:------------|:------|:------------------------------|
| `paper-zbw-majorana-tqc-p5-adelic-qec` | Adelic Quantum Error Correction: Intrinsic Qubit Protection from Ostrowski | Addresses **Assumption A6 (error correction scaling)** via p-adic QEC |
| `paper-ultrametric-quantum` | Qudit Quantum Error Correction | Addresses **Assumption A6** from a different mathematical framework |
| `paper-stabilization-of-gottesman-kitaev-preskill-states` | Stabilization of GKP States | References Preskill — addresses **Assumption A7 (coherence)** |
| `paper-cryogenically-stabilized-synthetic-lattice-architecture-for-fault-tolerant-quantum-computing` | Cryogenically Stabilized Synthetic Lattice | Addresses **Assumption A9 (physical realizability)** |
| `paper-commercial-pathways-to-room-temperature-topological-quantum-computation` | Commercial Pathways to Room-Temperature TQC | Addresses **Assumption A5/A9** from economic perspective |
| `paper-number-theoretic-ultrametric-foundations` | Number-Theoretic Ultrametric Foundations | Addresses **Assumption A4 (factoring hardness)** via p-adic number theory |
| `paper-autonomous-dissipative-quantum-processing` | Autonomous Dissipative Quantum Processing | Challenges **Assumption A8 (gate model)** via dissipative computing |

### Adjacent: Research Questions

| KG RQ ID | Question | Relevance |
|:---------|:---------|:----------|
| `rq-07-ostrowski-qec-superiority` | Can Ostrowski-based QEC beat surface code thresholds? | **Directly relevant to physical resource analysis (T2.1)** |
| `rq-011-adelic-qec-synthesis` | Adelic QEC Synthesis | Addresses alternative error correction models |
| `rq-012-ultrametric-benchmarking` | Ultrametric Benchmarking | Potential alternative to standard quantum benchmarking |

### Adjacent: Findings

| KG Finding ID | Description | Relevance |
|:--------------|:------------|:----------|
| `finding-braid-compilation` | Braid Compilation: 12,000x vs Solovay-Kitaev at eps=1e-12 | Addresses **Assumption A9** — gate fidelity/complexity |
| `finding-autaxys-falsification` | Autaxys Falsification Experiment | Experimental test of quantum computational assumptions |

### Broader Ecosystem: Quantum Papers

The KG search for "quantum" returned **50 papers** (API cap). Key clusters:

- **Ultrametric quantum mechanics** (34 papers) — alternative mathematical framework
- **p-adic quantum physics** (9 papers) — non-Archimedean quantum theory
- **Quantum error correction** (2 papers) — Ostrowski-based and qudit approaches
- **Wave mechanics** (4 papers) — classical wave alternatives to quantum
- **Quantum biology** (1 paper) — cryptochrome magnetoreception

### What This Missed Cross-Reference Means

| Shor Assumption | What KG Already Addresses | Gap in My Research |
|:----------------|:--------------------------|:-------------------|
| A4 (FACTORING ∉ BPP) | Number-theoretic ultrametric foundations paper | No cross-reference to p-adic factoring hardness analysis |
| A6 (Error correction scaling) | Adelic QEC + qudit QEC + GKP states | No comparison of surface code vs. alternative QEC models |
| A7 (Coherence) | GKP state stabilization, dissipative processing | No analysis of alternative coherence paradigms |
| A8 (Gate model) | Autonomous dissipative quantum processing | No consideration of non-circuit-model quantum computation |
| A9 (Physical realizability) | Cryogenic lattice architectures, room-temperature TQC | No cross-reference to hardware architecture proposals |

---

## 2. RECOMMENDED KG SEEDING

### New Paper Nodes to Seed

```python
# Proposed new paper node representing this research output
{
    "id": "paper-shor-assumptions-audit-2026",
    "label": "Paper",
    "name": "Shor's Algorithm and the Unproven Premise: An Assumption Audit of the Quantum Factoring Narrative",
    "properties": {
        "slug": "shor-assumptions-audit-2026",
        "authors": "QNFO Research",
        "status": "draft",
        "source": "shor-assumptions-research",
        "abstract": "Systematic audit of 9 assumptions in Shor's algorithm showing the quantum advantage claim requires unproven FACTORING not-in BPP premise"
    }
}
```

### New Edges to Seed

| Edge Type | Source → Target | Rationale |
|:----------|:----------------|:----------|
| `REFERENCES` | `paper-shor-assumptions-audit-2026` → `paper-feynman-shor-quantum-bifurcation` | Direct citation relationship |
| `REFERENCES` | `paper-shor-assumptions-audit-2026` → `paper-geometric-quantum-advantage` | Direct citation relationship |
| `BUILDS_ON` | `paper-shor-assumptions-audit-2026` → `paper-number-theoretic-ultrametric-foundations` | Builds on p-adic analysis |
| `BUILDS_ON` | `paper-shor-assumptions-audit-2026` → `paper-ultrametric-quantum` | Builds on ultrametric QEC |
| `RELATES_TO` | `paper-shor-assumptions-audit-2026` → `rq-07-ostrowski-qec-superiority` | Addresses QEC threshold question |
| `MOTIVATES` | `paper-shor-assumptions-audit-2026` → `rq-011-adelic-qec-synthesis` | Motivates further QEC work |
| `HAS_FINDING` | `paper-shor-assumptions-audit-2026` → `finding-factoring-bpp-gap` | Core finding: FACTORING ∈ BQP but ∉ BPP unproven |
| `HAS_FINDING` | `paper-shor-assumptions-audit-2026` → `finding-shor-crossover-2040` | Crossover simulation results |
| `HAS_FINDING` | `paper-shor-assumptions-audit-2026` → `finding-abelian-hsp-narrow` | HSP classification audit result |

---

## 3. IMPACT ON THE 10 RESEARCH QUESTIONS

| RQ | KG Cross-Reference Status | Action |
|:---|:--------------------------|:-------|
| RQ1 (GNFS trajectory) | Not in KG | Seed new finding |
| RQ2 (Non-abelian HSP) | Partially via braid compilation finding | Cross-reference finding-braid-compilation |
| RQ3 (RSA resource estimate) | rq-07 addresses QEC thresholds | Cross-reference rq-07 |
| RQ4 (Crossover point) | Not in KG | Seed finding-shor-crossover-2040 |
| RQ5 (NPV of migration) | Not in KG | Seed new analysis |
| RQ6 (Shor failure probability) | Not in KG | Align with T3.2 Python results |
| RQ7 (Classical period-finding) | paper-number-theoretic-ultrametric-foundations | Cross-reference |
| RQ8 (ORDER-FINDING bound) | Not in KG | Seed as new RQ |
| RQ9 (Decoherence limits BPP) | GKP stabilization + dissipative papers | Partially addressed |
| RQ10 (Citation analysis) | Not in KG | Seed as meta-science finding |

---

## 4. METHODOLOGICAL POST-MORTEM

**What went wrong:** The research plan was executed without a KG due-diligence step. According to the knowledge-graph skill §Recipe 1, before any new work the agent should:
1. Query graph for existing entities matching the topic
2. Check neighbors/ball for related work
3. Run impact analysis to identify dependencies

None of these were performed. The result: 2 directly relevant QNFO publications, 48 research questions, and 41 findings went uncited.

**What should have happened:** After Stage 0 (seed quality gate), the agent should have:
```
[AUTO-CONTINUE → KG Due Diligence]
→ GET /stats (ecosystem overview)
→ GET /nodes?label=Paper&search=shor (direct hits)
→ GET /nodes?label=ResearchQuestion (existing RQs)
→ GET /nodes?label=Finding (existing findings)
→ GET /neighbors/concept-domain-qwav-physics (ultrametric ball)
```

**Correction:** This supplement documents the gap. With the KG cross-reference now complete, the research plan's findings can be:
1. Cited against existing QNFO publications
2. Seeded back into the KG as new nodes/edges
3. Cross-referenced against existing ResearchQuestions
