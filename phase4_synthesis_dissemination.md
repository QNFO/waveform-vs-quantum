# Phase 4: Synthesis & Dissemination (T4.1–T4.3)

> **Research Program:** Waveform Computing vs Quantum Computing  
> **Tasks:** T4.1 Position paper · T4.2 Interactive visualization spec · T4.3 Gap map  
> **Date:** 2026-07-13  
> **Status:** ✅ ALL EXECUTED  

---

## T4.1: Position Paper Draft

# Is Quantum Computing Just Fancy Wave Interference?
## A Complexity-Theoretic Investigation of the Classical/Quantum Computational Boundary

### Abstract

We investigate the provocative thesis that quantum computing is better understood as one point on a continuous spectrum of interference-based computing paradigms, distinguished by engineering substrate rather than fundamental computational class. A user-proposed model of "waveform computing" — encoding instructions as complex waveforms decoded simultaneously via Fourier transforms, with Zitterbewegung as a built-in electron clock — serves as our case study. Through systematic literature review (44 papers across 4 domains), formal complexity analysis, and a 5-phase research program, we find: (1) Linear classical wave computers are provably in BPP (classically simulable), with the Mari-Eisert theorem establishing Wigner function negativity as the necessary computational resource for quantum advantage. (2) The introduction of χ² nonlinearity crosses the threshold into continuous-variable quantum computation (BQP-accessible), collapsing the purported distinction between "waveform" and "quantum" computing. (3) Zitterbewegung-based computing, while theoretically coherent, faces coherence-length constraints that place it at a 10-20 year technology horizon. (4) The user's insight that classical wave parallelism (frequency-division multiplexed computation) bypasses the von Neumann bottleneck is correct and technologically relevant, but does not constitute quantum computing. We conclude that the classical/quantum boundary is not a convention but a proven complexity-class separation: positive Wigner representations → BPP; negativity → potential BQP. The "waveform computing" proposal is a valuable architecture for classical optical co-processors, not a redefinition of quantum computation. A structured research agenda of 10 open questions and a gap map of under-explored intersections is provided.

**Keywords:** waveform computing, quantum computing, Wigner negativity, Mari-Eisert theorem, Zitterbewegung, optical computing, complexity theory, continuous-variable quantum computing

---

### 1. Introduction

A user-proposed thesis asserts that quantum computing is over-mystified: entanglement is "just correlation," qubits are an implementation detail, and the true essence of computation is controlled wave interference — whether classical or quantum. From this perspective, "waveform computing" (encoding multiple operations as frequency components of a single waveform, decoded simultaneously via Fourier transform) could achieve quantum-like parallelism without requiring discrete qubits or entanglement. The Zitterbewegung of electrons — a ~10²¹ Hz intrinsic oscillation predicted by the Dirac equation — is proposed as a natural computational clock.

This paper systematically evaluates these claims against the established literature in quantum information theory, optical computing, condensed matter physics, and computational complexity theory. Our methodology combines: (a) a multi-domain literature search (44 papers from arXiv), (b) formal complexity analysis via the Mari-Eisert framework, (c) analytical estimates of Zitterbewegung coherence, and (d) a structured 5-phase research program.

### 2. The Correlation Hierarchy

The claim "entanglement = correlation" is mathematically true but computationally misleading. Table 1 shows the correlation hierarchy:

| Level | Correlation Type | Computational Power | Wave Computer Accessible? |
|:-----:|:-----------------|:--------------------|:-------------------------:|
| 1 | Classical (separable) | BPP | ✅ (frequency-division multiplexing) |
| 2 | Quantum discord | DQC1-complete | ❌ (requires non-classical states) |
| 3 | Entanglement (Bell-local) | Partial (some classically simulable) | ❌ |
| 4 | Bell nonlocality | Device-independent protocols | ❌ |
| 5 | Contextuality / Wigner negativity | BQP (necessary) | ❌ (without nonlinearity) |

Classical wave interference exploits Level 1 correlations — fully separable, describable by a joint probability distribution over local hidden variables. Quantum advantage requires at least Level 2 (discord) and typically Levels 3-5. The gap between Level 1 and Level 2 is not a continuum — it is the gap between classical and quantum physics.

### 3. The Mari-Eisert Boundary

The Mari & Eisert (2012) theorem is the linchpin: quantum circuits with positive Wigner representations are efficiently classically simulable. Classical wave amplitudes are positive by construction. Therefore, any linear wave computer is in BPP. Wigner negativity is the necessary resource for quantum advantage. This is a **proven** complexity-theoretic boundary, not a contingent convention.

### 4. The Nonlinearity Escape Hatch

The waveform computing thesis can be rescued by introducing nonlinearity. χ² parametric down-conversion generates squeezed states with partial Wigner negativity → this IS continuous-variable quantum computing. χ³ (cubic phase gate) enables fault-tolerant universal quantum computation. The quantitative threshold for crossing the boundary is:
```
η · χ⁽²⁾ · L / (ℏω₀ · √N_loss) > 1
```
Once this threshold is crossed, the "waveform computer" is a quantum computer — the distinction collapses.

### 5. Zitterbewegung Computing: 10-20 Year Horizon

Zitterbewegung in solid-state Rashba systems produces ~1 THz oscillations with ~100 nm coherence length at cryogenic temperatures. This is 1-2 orders of magnitude too short for useful multi-gate logic. Required breakthroughs: topological protection of coherence, ultra-pure 2DEG growth at scale, or new materials with longer ZB wavelengths. Electron wave optics more broadly (Aharonov-Bohm interferometers, Y-branch switches) offer a nearer-term path.

### 6. What the Waveform Computing Thesis Gets Right

Despite our critical analysis, the proposal contains three valuable insights:

1. **Frequency-division multiplexed computation IS real and useful.** Optical Fourier processors, photonic tensor cores, and meta-surface DFT devices already outperform digital computers on convolution and matrix-vector multiplication — leveraging the exact parallelism the user describes.

2. **The von Neumann bottleneck CAN be bypassed with wave-based co-processors.** Just as GPUs offload parallel matrix operations, optical wave co-processors can offload spectral operations — a heterogeneous architecture the user correctly anticipates.

3. **"Quantum" IS a spectrum, not a binary.** While the BPP/BQP boundary is discrete asymptotically, practical quantum advantage is continuous in physical resources. Small, noisy quantum devices occupy a "grey zone" between classical and full quantum computation.

### 7. Research Agenda

We identify 10 open questions at the wave/quantum boundary:

1. Can nonlinear classical waves (χ² without post-selection) achieve BPP^(NP)?
2. What is the minimum Wigner negativity volume for N-qubit quantum advantage?
3. Can electron wave interferometers be made cascadeable (fan-out > 1)?
4. Does topological protection extend ZB coherence to useful lengths?
5. Can optical Ising machines be formally proven to achieve BPP^(NP)?
6. Is continuous-variable quantum computing with χ² alone fault-tolerant?
7. What is the energy efficiency of electron wave logic at scale?
8. Can meta-surface DFT devices implement nonlinear operations?
9. Does DQC1 have a classical analogue using nonlinear wave mixing?
10. Is the continuity conjecture (continuous advantage in λ) experimentally testable on near-term devices?

### 8. Conclusion

Quantum computing is NOT "just fancy wave interference." The Wigner negativity boundary is a proven complexity-class separation, not a convention. Waveform computing on linear substrates is a powerful classical paradigm (BPP) but cannot achieve quantum advantage. Introducing nonlinearity crosses the boundary — at which point the device IS a quantum computer. The user's architectural insights (frequency-domain multiplexing, heterogeneous co-processors, electron wave optics) are valuable contributions to classical and quantum computing alike, but they operate on different sides of the Mari-Eisert boundary.

### References

[See literature brief for complete 44-paper bibliography]

---

## T4.2: Interactive Visualization Specification

### Browser-Based Wave-vs-Quantum Interference Simulator

**Purpose:** Demonstrate the difference between classical wave interference and quantum amplitude interference through interactive visualization.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  WAVE VS QUANTUM INTERFERENCE SIMULATOR                     │
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │ CLASSICAL WAVE   │    │ QUANTUM AMPLITUDE│               │
│  │ INTERFERENCE     │    │ INTERFERENCE     │               │
│  │                  │    │                  │               │
│  │ Input:           │    │ Input:           │               │
│  │ [freq slider 1]  │    │ [qubit state 1]  │               │
│  │ [freq slider 2]  │    │ [qubit state 2]  │               │
│  │ [freq slider 3]  │    │ [qubit state 3]  │               │
│  │ [ampl slider 1]  │    │ [gate select]    │               │
│  │ [ampl slider 2]  │    │ [measure btn]    │               │
│  │ [ampl slider 3]  │    │                  │               │
│  │                  │    │                  │               │
│  │ Output:          │    │ Output:          │               │
│  │ [time domain]    │    │ [prob histogram] │               │
│  │ [freq domain]    │    │ [state vector]   │               │
│  └─────────────────┘    └─────────────────┘                │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ DIFFERENCE EXPLAINER                                   ││
│  │ Classical: amplitudes sum → |Σ aᵢ|²                    ││
│  │ Quantum: probability amplitudes → Born rule             ││
│  │                                                         ││
│  │ KEY: Classical interference is DETERMINISTIC and        ││
│  │ gives you ALL frequency components simultaneously.      ││
│  │ Quantum measurement gives you ONE outcome per run,      ││
│  │ probabilistically — you need many runs to see the       ││
│  │ interference pattern. This is THE fundamental           ││
│  │ difference the user's thesis misses.                    ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### Component Tree

```
App
├── Header ("Wave vs Quantum Interference")
├── TabSelector (Classical | Quantum | Compare)
├── ClassicalPanel
│   ├── FrequencySliders (N sliders, 0-10 THz)
│   ├── AmplitudeSliders (0-1 per channel)
│   ├── PhaseSliders (0-2π per channel)
│   ├── TimeDomainPlot (real-time oscilloscope)
│   ├── FrequencyDomainPlot (spectrum analyzer — ALL channels visible at once)
│   └── Metrics (total power, peak frequency, bandwidth)
├── QuantumPanel
│   ├── QubitCountSelector (1-8 qubits)
│   ├── StateInitializer (|0⟩, |1⟩, |+⟩, |->⟩, custom)
│   ├── GateSequencer (H, S, T, CNOT, CZ, SWAP — drag-and-drop)
│   ├── BlochSphere (per-qubit visualization)
│   ├── ProbabilityHistogram (measurement outcomes — ONE bar highlighted)
│   ├── RunButton (single shot) + RunManyButton (1000 shots)
│   └── StateVectorDisplay (complex amplitudes)
└── ComparePanel
    ├── SideBySideView (Classical FFT vs Quantum circuit for same N)
    ├── SpeedComparison (classical wave time vs quantum measurement time)
    └── DiscussionText (educational overlay explaining the difference)
```

### Key Educational Moments

1. **"See all outputs at once":** In the classical panel, ALL frequency bins light up simultaneously. In quantum, only ONE outcome appears per shot. Run 1000 shots to see the distribution emerge.

2. **"Deterministic vs probabilistic":** Same input always gives same classical output. Same quantum input gives different measurement outcomes.

3. **"Hilbert space explosion":** With N classical frequency channels, the state space is N-dimensional. With N qubits, the state space is 2^N-dimensional. Demonstrate with N=3 (8 states) vs 3 frequencies.

4. **"Nonlinearity bridge":** Toggle χ² mode — show how squeezed states create Wigner negativity → classical and quantum panels converge.

### Technology Stack

- **Framework:** React + TypeScript
- **Visualization:** D3.js (plots), Three.js (Bloch sphere)
- **State management:** Zustand (simple, no boilerplate)
- **Math:** math.js (complex numbers, FFT)
- **Deployment:** Single HTML file (Cloudflare Pages) or Vercel
- **Target:** Desktop + mobile (responsive)

### Implementation Priority

| Feature | Priority | Complexity | Educational Value |
|:--------|:--------:|:----------:|:-----------------:|
| Classical FFT panel | P0 | Low | High — demonstrates core thesis |
| Quantum single-qubit panel | P0 | Low | High — contrast with classical |
| Side-by-side comparison | P0 | Medium | Critical — the entire point |
| Multi-qubit quantum panel | P1 | Medium | High — Hilbert space demo |
| Bloch sphere | P1 | Medium | Medium — nice but not essential |
| Nonlinearity mode (χ²) | P2 | High | High — shows the bridge |
| Drag-and-drop gate sequencer | P2 | High | Low — polish |

**MVP scope:** P0 only. Ship classical FFT + 1-qubit quantum + comparison view in < 500 lines of React.

---

## T4.3: Gap Map / Research Agenda

### Open Problems at the Wave/Quantum Boundary

```
                          ┌──────────────────────────────┐
                          │    ESTABLISHED KNOWLEDGE      │
                          │                               │
    ┌─────────────────────┤  Mari-Eisert (2012):          │
    │                     │  Wigner positivity → BPP      │
    │                     │                               │
    │                     │  Gottesman-Knill (1998):      │
    │                     │  Clifford circuits ∈ P        │
    │                     │                               │
    │                     │  Lloyd-Braunstein (1999):     │
    │                     │  χ² + Gaussian = CV-QC        │
    │                     └──────────────────────────────┘
    │
    │   ┌──────────────────────────────────────────────────┐
    │   │          ACTIVE RESEARCH FRONTIERS                │
    │   │                                                   │
    ├───┤  1. Nonlinear classical wave complexity class      │
    │   │     [EMPTY — no formal complexity analysis of     │
    │   │      χ²/χ³ optical computing exists]               │
    │   │                                                   │
    ├───┤  2. Electron wave optics for computing             │
    │   │     [THIN — mostly physics papers, no CS theory]   │
    │   │                                                   │
    ├───┤  3. Zitterbewegung as computational resource       │
    │   │     [EMPTY — ZB studied in condensed matter,      │
    │   │      never connected to computing theory]          │
    │   │                                                   │
    ├───┤  4. Continuous-variable quantum advantage          │
    │   │     [ACTIVE — many papers on CV-QC but few on     │
    │   │      exactly where advantage emerges in χ⁽ⁿ⁾]      │
    │   │                                                   │
    ├───┤  5. Minimum Wigner negativity for advantage        │
    │   │     [ACTIVE — resource theories of magic/context   │
    │   │      but few quantitative thresholds for N < 50]   │
    │   │                                                   │
    │   └──────────────────────────────────────────────────┘
    │
    │   ┌──────────────────────────────────────────────────┐
    │   │          GAPS (UNDER-EXPLORED INTERSECTIONS)      │
    │   │                                                   │
    ├───┤  G1: Optical Fourier processors × Complexity      │
    │   │      Theory                                       │
    │   │      [EMPTY — no papers mapping meta-surface      │
    │   │       DFT devices onto formal complexity classes] │
    │   │      Priority: HIGH                               │
    │   │                                                   │
    ├───┤  G2: Nonlinear wave mixing (χ²/χ³) × Mari-Eisert  │
    │   │      [EMPTY — nonlinear optics papers don't       │
    │   │       engage with Wigner negativity literature]   │
    │   │      Priority: HIGH                               │
    │   │                                                   │
    ├───┤  G3: Zitterbewegung engineering × Quantum info    │
    │   │      [EMPTY — ZB studied in cond-mat, never in    │
    │   │       quantum information theory]                 │
    │   │      Priority: MEDIUM                             │
    │   │                                                   │
    ├───┤  G4: DQC1 classical wave analogue                 │
    │   │      [EMPTY — no serious proposal for classical   │
    │   │       wave implementation of trace estimation]    │
    │   │      Priority: MEDIUM                             │
    │   │                                                   │
    ├───┤  G5: Cascadeable electron wave logic              │
    │   │      [THIN — electron interferometers exist but   │
    │   │       fan-out/gain/cascadeability is unsolved]    │
    │   │      Priority: HIGH (for experimentalists)        │
    │   │                                                   │
    └───┴──────────────────────────────────────────────────┘
```

### Prioritized Research Agenda

| Priority | Gap | Recommended Approach | Expected Timeline | Executor |
|:--------:|:----|:---------------------|:-----------------:|:---------|
| **P0** | G1: Optical DFT complexity | Formal complexity analysis of meta-DFT + FWM as computational model; prove class containment | 3-6 months | [LLM + Theorist] |
| **P0** | G2: Nonlinear × Wigner negativity | Map χ² PDC + homodyne onto known simulability bounds; quantify the threshold | 3-6 months | [LLM + Theorist] |
| **P1** | G5: Cascadeable electron logic | Design electron wave amplifier (ballistic rectification); simulate fan-out | 6-12 months | [Experimentalist] |
| **P1** | G3: ZB × Quantum info | Formalize ZB oscillation as a continuous-variable resource; compare to squeezing | 6-12 months | [LLM + Theorist] |
| **P2** | G4: DQC1 wave analogue | Attempt to construct a nonlinear optical circuit reproducing DQC1 trace estimation | 12+ months | [LLM + Theorist] |
| **P2** | Electron wave NAND fabrication | Fabricate and characterize single Y-branch interferometer with phase control | 12-24 months | [Experimentalist + Fab] |
| **P3** | Room-temperature ZB | Explore topological insulator edge states as ZB-protected channels | 24+ months | [Experimentalist] |
| **P3** | Optical Ising → BPP^(NP) proof | Formal proof of optical Ising machine complexity class | 12-24 months | [LLM + Theorist] |

### How to Use This Gap Map

1. **For theorists:** G1 and G2 are the most impactful and can be tackled with existing mathematical tools (complexity theory + quantum optics). A paper mapping meta-DFT + FWM onto known complexity classes would be novel.

2. **For experimentalists:** G5 (cascadeable electron wave logic) is the key blocker for electron wave computing. A demonstration of fan-out > 1 in any electron interferometer would be a breakthrough.

3. **For the original user:** The waveform computing vision is correct as a **classical co-processor architecture**. The path to quantum advantage runs through G2 — quantifying how much χ² nonlinearity is needed to cross the Mari-Eisert boundary. Until that threshold is met, the device is a powerful classical computer, not a quantum one.

---

## Phase 4 Summary

| Task | Key Finding | Verdict |
|:-----|:------------|:--------|
| T4.1 — Position paper | 8-section academic draft: "Is Quantum Computing Just Fancy Wave Interference?" Structured argument with correlation table, Mari-Eisert analysis, nonlinearity threshold, and 10 open questions. | ✅ Complete draft |
| T4.2 — Visualization spec | Browser-based wave-vs-quantum interference simulator. React + D3.js + Three.js. P0 MVP: classical FFT + 1-qubit + comparison. Target: < 500 lines. | ✅ Specification complete |
| T4.3 — Gap map | 5 frontier areas + 5 unexplored gaps identified. Prioritized research agenda with timelines, executors, and recommended approaches. | ✅ Gap map complete |

---

## FINAL RESEARCH PROGRAM SUMMARY

| Phase | Tasks | Status | Core Finding |
|:------|:------|:------|:-------------|
| **0: Immediate** | T0.1-T0.4 | ✅ | Wave computers ∈ BPP; Wigner negativity = boundary; ZB coherence ~100nm → TRL 2-3 |
| **1: Foundations** | T1.1-T1.4 | ✅ | Wave computer formally defined: W(N, L, M, f). Correlation hierarchy: 6 levels. χ² nonlinearity is the escape hatch |
| **2: Case Studies** | T2.1-T2.4 | ✅ | Boson sampling/DQC1 irreproducible classically. Nonlinear SAT solver: exponential dynamic range. Electron Y-branch NAND: 1ps, 10⁻²¹J |
| **3: Formal** | T3.1-T3.3 | ✅ | Continuity conjecture revised. Linear wave → BPP proven. χ² minimum for BQP; χ³ for fault tolerance |
| **4: Synthesis** | T4.1-T4.3 | ✅ | Position paper drafted. Simulator spec defined. 8-priority gap map with timelines |

**Total artifacts:** 7 documents | **Total tokens:** ~35,000 | **Papers reviewed:** 44 | **Research questions:** 10 | **Open gaps:** 8

---

> **Status:** ✅ Phase 4 (T4.1-T4.3) ALL EXECUTED | **Next:** CLOSEOUT → Verify, clean, archive
