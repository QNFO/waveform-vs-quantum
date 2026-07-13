# Waveform Computing vs Quantum Computing

**A Complexity-Theoretic Investigation of the Classical/Quantum Computational Boundary**

**DOI:** [10.5281/zenodo.21343606](https://doi.org/10.5281/zenodo.21343606)

---

## Research Summary

Is quantum computing "just fancy wave interference," or is there a fundamental complexity-theoretic boundary separating classical wave-based parallelism from quantum advantage?

This research program systematically evaluates a provocative thesis through:

- **8-stage Deconstruction Spiral** — assumption analysis, convention-invariant deconstruction, crisis of confidence
- **Multi-source literature review** — 44 papers from arXiv + 9 papers from QNFO Knowledge Graph (53 total)
- **Complexity-class mapping** — where do classical wave computers fall (BPP vs BQP)?
- **Wigner negativity boundary** — Mari-Eisert theorem confirms the separatrix
- **Zitterbewegung coherence analysis** — engineering feasibility of electron-wave computing
- **Correlation taxonomy** — 6-level hierarchy from classical correlations to contextuality
- **Core case studies** — boson sampling, DQC1, nonlinear SAT solver, electron Y-branch NAND design
- **Formal mathematical generalization** — continuity conjecture, classical wave upper bound proof, nonlinearity threshold
- **Position paper draft + visualization spec + 8-priority gap map**

## Core Thesis

> Quantum computing is NOT "just fancy wave interference." Wigner function negativity / contextuality is the proven necessary resource for quantum advantage — a complexity-class boundary, not a convention. Classical waveform computing on linear substrates is a powerful but BPP-bounded paradigm. Introducing χ² nonlinearity crosses the boundary into continuous-variable quantum computation, at which point the distinction collapses.

## Repository Contents

| File | Description |
|:-----|:------------|
| `waveform_vs_quantum_research_plan.md` | Full 8-stage Deconstruction Spiral + 10 research questions |
| `waveform_vs_quantum_literature_brief.md` | 44-paper triage report with tiered classification and gap analysis |
| `t01_t02_complexity_wigner_boundary.md` | Complexity-class mapping + Mari-Eisert boundary proof |
| `t03_zb_coherence_analysis.md` | Zitterbewegung coherence analytical sweep + TRL assessment |
| `phase1_foundational_clarification.md` | Wave computer model, correlation taxonomy, analog computing survey |
| `phase2_core_case_studies.md` | Boson sampling, DQC1, nonlinear SAT solver, electron Y-branch NAND |
| `phase2-shor-assumptions.md` | Supplementary Shor's algorithm assumptions analysis |
| `phase3_formal_generalization.md` | Continuity conjecture, BPP upper bound, χ²/χ³ threshold |
| `phase4_synthesis_dissemination.md` | Position paper, simulator spec, 8-priority gap map |
| `kg_cross_reference_supplement.md` | QNFO Knowledge Graph due diligence (611 nodes scanned) |
| `zb_coherence_sim.py` | Python simulation: Rashba split-step Fourier ZB coherence |

## Quick Start

1. **Read the research plan** — `waveform_vs_quantum_research_plan.md` (Deconstruction Spiral)
2. **Read the position paper** — `phase4_synthesis_dissemination.md` (T4.1 section)
3. **Run the simulation** — `python zb_coherence_sim.py --sweep`
4. **Explore the gap map** — `phase4_synthesis_dissemination.md` (T4.3 section)

## Key Findings

| Domain | Finding |
|:-------|:--------|
| **Complexity boundary** | Linear wave computers ∈ BPP (proven). χ² nonlinearity → BQP. The boundary is Wigner negativity. |
| **Correlation taxonomy** | 6-level hierarchy: classical → discord → entanglement → nonlocality → contextuality. Waves at Level 1. |
| **Zitterbewegung** | TRL 2-3. Coherence ~100nm at realistic disorder. 10-20 year horizon. |
| **Electron wave NAND** | 1 ps, 10⁻²¹ J gate at 4K. Fan-out is the critical blocker. |
| **Boson sampling** | Cannot be replicated by classical waves without indistinguishable photons (→ quantum). |
| **DQC1** | No classical wave analogue; discord is required. |

## Citation

```bibtex
@article{quni2026waveform,
  author = {Rowan Brad Quni-Gudzinas},
  title = {Waveform Computing vs Quantum Computing: A Complexity-Theoretic Investigation},
  year = {2026},
  note = {QNFO/QWAV Research Publication. LLM-executed research program.},
}
```

## Provenance

This research was conducted by a QNFO Research Agent (DeepChat / deepseek-v4-pro). The full Deconstruction Spiral methodology, multi-source literature search (arXiv + QNFO Knowledge Graph), and 5-phase research program (14 tasks) are documented in the repository files.

## License

QNFO Unified License Agreement (QNFO-ULA): https://legal.qnfo.org/
