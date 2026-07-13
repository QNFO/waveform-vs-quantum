# Phase 1: Foundational Clarification (T1.1–T1.4)

> **Research Program:** Waveform Computing vs Quantum Computing  
> **Tasks:** T1.1 Formal wave computer model · T1.2 Correlation taxonomy · T1.3 Analog computing survey · T1.4 Electron wave constraints  
> **Date:** 2026-07-13  
> **Status:** ✅ ALL EXECUTED  

---

## T1.1: Formal Definition of the "Wave Computer" Computational Model

### 1.1.1 Model Definition

A **Wave Computer** `W(N, L, M, f)` is a 4-tuple:

| Component | Symbol | Definition |
|:----------|:-------|:-----------|
| **Channels** | N ∈ ℕ | Number of frequency/spectral channels (modes) available for parallel encoding |
| **Linearity** | L ∈ {0, 1} | 0 = linear system (passive optical elements only); 1 = nonlinear (allows χ²/χ³ mixing) |
| **Measurement** | M ∈ {S, H, A} | S = Spectral (frequency-domain readout); H = Homodyne (quadrature measurement); A = Adaptive (measurement-dependent feedforward) |
| **Functor space** | f: ℂ^N → ℂ^N | The transfer function mapping input spectral amplitudes to output spectral amplitudes |

### 1.1.2 Computational Model

**Input encoding:** An N-bit classical input `x ∈ {0, 1}^N` is encoded as a complex waveform:
```
ψ_in(t) = Σⱼ aⱼ · exp(i·2π·fⱼ·t + i·φⱼ)
```
where `aⱼ = xⱼ` (amplitude modulation) or `φⱼ = π·xⱼ` (phase modulation).

**Allowed operations:**

| Operation | Mathematical Form | Physical Realization | Complexity Cost |
|:----------|:------------------|:---------------------|:----------------|
| Frequency filtering | H(f) = rect((f-f_c)/B) | Band-pass filter, grating | O(1) [passive] |
| Fourier transform | F[ψ](f) = ∫ψ(t)·e^{-i2πft}dt | Lens, grating, prism | O(1) [passive, speed of light] |
| Phase shift | ψ → ψ·e^{iΔφ} | Optical delay line, phase plate | O(1) [passive] |
| Beam splitting | [ψ₁,ψ₂] → [(ψ₁+ψ₂)/√2, (ψ₁-ψ₂)/√2] | Beam splitter, directional coupler | O(1) [passive] |
| Amplification | ψ → G·ψ (G > 1) | Optical amplifier, EDFA | O(N) [active, noise-limited] |
| Nonlinear mixing (χ²) | ψ_out(f) ∝ ∫ψ_in(f')·ψ_in(f-f')df' | SHG crystal, PPLN | O(N²) [active] |
| Nonlinear mixing (χ³) | ψ_out ∝ ∭ψ_in·ψ_in·ψ_in | Kerr medium, HNLF | O(N³) [active] |
| Spectral measurement | p(fⱼ) = |aⱼ|²/Σₖ|aₖ|² | Spectrometer, WDM | O(N) [readout] |
| Homodyne detection | x̂ = ∫ψ(t)·cos(ωt)dt | Balanced homodyne detector | O(1) [readout] |
| Adaptive measurement | Depends on prior outcome | FPGA + optical switch | O(log N) [readout] |

**Computational cost:** A Wave Computer `W(N, 0, S, f)` (linear, spectral readout) can compute any operation expressible as:
```
y = |F·H·A·x|²
```
where F is the Fourier matrix, H is a diagonal filter matrix, and A is the amplitude encoding. The wall-clock time is O(1) (the time for light to traverse the optical path).

### 1.1.3 Complexity Class Assignment

| Wave Computer Configuration | Operations Allowed | Complexity Class | Justification |
|:----------------------------|:-------------------|:-----------------|:--------------|
| **W(N, 0, S)** — Linear, spectral readout | Filtering, FFT, splitting, measurement | **BPP** (contained in) | Maps onto positive-Wigner sector (Mari-Eisert) |
| **W(N, 0, H)** — Linear, homodyne | Above + quadrature measurement | **BPP** | Gaussian operations preserve positivity |
| **W(N, 1, H)** — Nonlinear (χ²), homodyne | Above + squeezing, parametric amplification | **BQP** (for CV encoding) | Squeezed states have negative Wigner in one quadrature → escapes Mari-Eisert |
| **W(N, 1, A)** — Nonlinear (χ³), adaptive | Above + Kerr, cubic phase, feedforward | **BQP** (universal CV-QC) | Lloyd & Braunstein (1999): Gaussian + cubic phase = universal |

### 1.1.4 Comparison to Standard Computational Models

| Property | Turing Machine | Circuit Model | Quantum Circuit | Wave Computer W(N, 0, S) |
|:---------|:--------------|:--------------|:----------------|:-------------------------|
| State representation | Tape string | Bit vector | Hilbert space ray | Complex amplitude vector |
| State space size | Unbounded | 2^n | 2^n (exponential) | N (frequency channels) |
| Elementary operation | Symbol write | Boolean gate | Unitary gate | Transfer function |
| Parallelism | Sequential | Gate-level | Quantum superposition | Frequency multiplexing |
| Readout | Deterministic | Deterministic | Probabilistic | Deterministic (spectral) |
| Universality | Yes (Church-Turing) | Yes | Yes (conjectured) | No (restricted to linear transformations) |
| Complexity | P | P/poly | BQP | BPP (subset) |

---

## T1.2: Taxonomy of Correlation Types in Computing

### 2.1 The Correlation Hierarchy

Computational resources can be classified by the type of correlation they exploit:

```
LEVEL 0:  No correlation (independent bits)
          └─ Classical deterministic computation
          └─ Example: Boolean logic gates on independent inputs

LEVEL 1:  Classical correlation (separable joint probability)
          └─ P(a,b) = Σ_λ p(λ) P(a|λ) P(b|λ)
          └─ Example: Shared random bits, frequency-division multiplexing
          └─ Computational power: BPP (identical to Level 0)

LEVEL 2:  Quantum discord (non-classical correlation without entanglement)
          └─ States separable (ρ = Σ p_i ρ_i^A ⊗ ρ_i^B) but with quantum correlations
          └─ Measured by: D(A|B) = I(A:B) - J(A|B) where J is classical correlation
          └─ Example: DQC1 model (Knill & Laflamme, 1998)
          └─ Computational power: DQC1-complete (strictly > BPP, < BQP?)

LEVEL 3:  Entanglement (non-separable states, Bell-local)
          └─ Cannot be written as ρ = Σ p_i ρ_i^A ⊗ ρ_i^B
          └─ BUT can be described by local hidden-variable model (satisfies all Bell inequalities)
          └─ Example: Werner states for p ≤ 1/√2, some bound entangled states
          └─ Computational power: Some entangled states are classically simulable (Gottesman-Knill)
                             Some provide quantum advantage (when combined with magic)

LEVEL 4:  Bell nonlocality (violates CHSH inequality)
          └─ Correlations satisfy: |⟨A₀B₀⟩ + ⟨A₀B₁⟩ + ⟨A₁B₀⟩ - ⟨A₁B₁⟩| > 2
          └─ Example: Maximally entangled Bell state |Φ⁺⟩
          └─ Computational power: Subset of BQP; necessary for device-independent QKD
                                   Not sufficient for universality without magic

LEVEL 5:  Contextuality / Magic (violates noncontextuality inequality)
          └─ Measurement outcomes depend on compatible measurements performed simultaneously
          └─ Measured by: Wigner function negativity, stabilizer rank, robustness of magic
          └─ Example: T gate, π/8 gate, magic states
          └─ Computational power: Necessary + sufficient (with Clifford) for universal QC (BQP)
```

### 2.2 Formal Distinctions

| Correlation Type | Mathematical Criterion | Physical Test | Computational Resource? |
|:-----------------|:----------------------|:--------------|:------------------------|
| **Classical** | Existence of joint probability distribution over local hidden variables | Bell inequality satisfied | No — all BPP |
| **Discord** | ρ separable AND I(A:B) > J(A:B) | State tomography + optimization | Yes — DQC1 advantage |
| **Entanglement (local)** | ρ non-separable AND Bell inequality satisfied | Bell test + state tomography | Partial — extends C but not to BQP |
| **Nonlocality** | CHSH > 2 | Bell test (CHSH experiment) | Yes for device-independent protocols |
| **Contextuality** | Violates NC inequality OR Wigner negativity | Sequential compatible measurements | Yes — necessary for BQP |

### 2.3 The "ENTANGLEMENT = CORRELATION" Claim Revisited

The user's claim that "entanglement = correlation" can now be precisely mapped:

**TRUE in this sense:** Entanglement is a type of correlation — specifically, a correlation between measurement outcomes that cannot be explained by any separable state. It lives at Level 3 in the hierarchy above.

**FALSE in this sense:** Not all correlations are entanglement. Classical correlations (Level 1) and quantum discord (Level 2) are distinct from entanglement but still "correlations."

**WHY THE DISTINCTION MATTERS for computing:** Classical wave correlations (Level 1) enable parallel frequency-domain processing but cannot access the resources at Levels 2-5. The wave computer's "correlations" are between different frequency components of the same signal — these are fully separable correlations (each frequency component is an independent degree of freedom). No Bell inequality is violated. No contextuality is present.

**The boundary between "wave computing" and "quantum computing" is the boundary between Level 1 and Level 2+ correlations.** A wave computer cannot generate discord, entanglement, nonlocality, or contextuality without nonlinearity — and once it has sufficient nonlinearity, it IS a quantum computer (continuous-variable).

### 2.4 Taxonomy Table for Computing Paradigms

| Paradigm | Correlation Level | Substrate | Universal? | Complexity Class | Status |
|:---------|:-----------------:|:----------|:----------:|:-----------------|:-------|
| Digital (CMOS) | 0 | Transistor switches | Yes (Turing) | P | Mature |
| Analog (op-amp) | 0 | Continuous voltages | No | P (BSS model) | Mature |
| Waveform (linear optical) | 1 | Frequency channels | No | BPP | Emerging (photonic AI) |
| Waveform (nonlinear optical) | 2-3 (χ²) | Squeezed light modes | Yes (CV-QC) | BQP | Research |
| Quantum (gate model) | 3-5 | Qubits (superconducting, ion trap) | Yes | BQP | Prototype |
| Quantum (CV model) | 2-5 | Optical modes | Yes | BQP | Research |
| Quantum (measurement-based) | 4-5 | Cluster states | Yes | BQP | Research |
| Neuromorphic (spiking) | 0-1 | Analog neurons | Probably not | P | Emerging |
| Reservoir computing | 1 | Nonlinear dynamical system | No | P (conjectured) | Emerging |

---

## T1.3: Survey of Analog Computing History & Complexity

### 3.1 Historical Timeline

| Era | Milestone | Relevance to Waveform Computing |
|:----|:----------|:-------------------------------|
| **1876** | Kelvin's tide predictor (mechanical analog) | First harmonic analyzer — used Fourier synthesis with mechanical gears. Direct ancestor of wave-based computation. |
| **1930s** | Vannevar Bush's Differential Analyzer | Mechanical analog computer solving ODEs via wheel-and-disc integrators. Demonstrated that continuous physical quantities can encode computation. |
| **1940s** | Electronic analog computers (REAC, EAI) | Op-amp integrators, summers, multipliers. Problem: noise accumulates linearly with operations → limited precision (~10⁻³). |
| **1960s** | Optical Fourier processors (Goodman, VanderLugt) | Coherent optical processing: lens performs Fourier transform at speed of light. Matched filtering, correlation, SAR processing. Still in use. |
| **1970s** | SAW (Surface Acoustic Wave) devices | Acoustic wave filters/computers for radar pulse compression. Demonstrated wave-based multiplexing at MHz frequencies. |
| **1989** | Blum-Shub-Smale (BSS) model | First formal complexity theory for analog computation over real numbers. Proved P_R ≠ NP_R over reals. Established that analog ≠ automatically faster. |
| **1990s** | Optical neural networks (Psaltis, Farhat) | Holographic correlators for pattern recognition. Limited by dynamic range of photorefractive crystals. |
| **1999** | Siegelmann's "Neural Networks and Analog Computation" | Proved that analog recurrent neural networks (ARNN) with real weights are super-Turing — can compute non-recursive functions. BUT: requires infinite precision, physically impossible. |
| **2017** | Photonic tensor cores (Shen et al., Nature Photonics) | Integrated silicon photonic circuits for matrix-vector multiplication. Demonstrated O(1)-time MVM with low energy. |
| **2020** | Optical Ising machines (NTT, Stanford) | Coherent optical networks solving combinatorial optimization via gain-dissipative dynamics. Comparable to quantum annealers on specific problems. |
| **2025** | Meta-surface DFT devices (Tanuwijaya et al.) | Single-layer metasurface performing complex-valued DFT at optical speeds. Brings Fourier-optical computing to chip scale. |

### 3.2 Key Theoretical Results

**BSS Model (Blum, Shub, Smale, 1989):**
- Defines computation over ℝ (real numbers) rather than finite fields.
- Complexity classes: P_R (polynomial time over ℝ), NP_R (nondeterministic polynomial over ℝ).
- **Key result:** P_R ≠ NP_R is an open problem (analogous to P ≠ NP). Existence of one-way functions over ℝ is unknown.
- **Implication:** Analogness alone does not guarantee computational advantage. The BSS model shows that continuous variables ≠ exponential speedup.

**Siegelmann's ARNN (1999):**
- Analog recurrent neural networks with real-valued weights are **super-Turing**: they can compute the halting problem for Turing machines.
- **Catch:** Requires infinite-precision real numbers. Physical noise (thermal, quantum) makes this impossible to realize. The result is a "complexity mirage" — mathematically true but physically inaccessible.

**Optical Computing Complexity (Reck et al., 1994):**
- Any N×N unitary matrix can be implemented with N(N-1)/2 beam splitters and phase shifters.
- Linear optical networks implement arbitrary unitary transformations on mode space.
- **Limitation:** Without nonlinearity or adaptive measurement, linear optical networks are classically simulable (BPP).

**Continuous-Variable Quantum Computing (Lloyd & Braunstein, 1999):**
- Gaussian operations (squeezing, displacement, beam splitter, homodyne) + any single non-Gaussian operation (e.g., cubic phase gate) = universality for CV-QC.
- **Implication:** A wave computer with χ² nonlinearity + homodyne detection IS a quantum computer.

### 3.3 Lessons for Waveform Computing

1. **Infinite precision is a mirage.** Siegelmann's super-Turing result is physically unrealizable. Any claim that analog/wave computers can exceed Turing machines must account for finite precision and noise.

2. **Linearity bounds you to BPP.** The BSS model and optical computing results both show that linear systems are computationally equivalent to probabilistic Turing machines.

3. **Nonlinearity is the escape hatch.** Lloyd & Braunstein's result shows that the minimum additional resource needed for universality is a single non-Gaussian operation — which in optical terms means χ² (squeezing + nonlinear mixing) or χ³ (cubic phase via Kerr effect).

4. **The history of analog computing teaches humility.** Analog computers were dominant in the 1940s-60s and lost to digital for a reason: noise accumulation, limited precision, and lack of programmability. Waveform computing must solve these same problems.

---

## T1.4: Electron Wave Optics Engineering Constraints

### 4.1 Physical Constraints

| Constraint | Value | Impact | Mitigation |
|:-----------|:------|:-------|:-----------|
| **Electron wavelength** | λ_dB = h/√(2m*E) | For E=10 meV in GaAs (m*=0.067mₑ): λ ≈ 40 nm | Determines minimum feature size for interference |
| **Phase coherence length (L_φ)** | ~1-100 μm at T < 1K | Sets maximum interferometer size | Ultra-low temperature, clean materials |
| **Momentum relaxation length (L_m)** | ~0.1-10 μm | Sets maximum ballistic transport distance | Modulation doping, remote impurities |
| **Spin-orbit coupling** | α_R ~ 1-10 × 10⁻¹¹ eV·m | Controls ZB; also causes spin dephasing | Gate-tunable Rashba in 2DEG |
| **Electron-electron interactions** | τ_ee ~ 1-100 ps | Causes decoherence at high density | Low carrier density (n_s < 10¹¹ cm⁻²) |
| **Disorder potential** | σ_V ~ 1-10 meV | Anderson localization; limits coherence | Delta-doping, clean interfaces |
| **Thermal broadening** | k_B T | At T=4K: 0.34 meV; at T=300K: 26 meV | Cryogenic operation essential |

### 4.2 Device Design Space

| Device | Operating T | L_φ (typ) | Frequency | Function | TRL |
|:-------|:-----------:|:---------:|:---------:|:---------|:---:|
| Aharonov-Bohm ring | 20 mK | 10 μm | DC | Phase-sensitive interference | 5 |
| Quantum point contact | 4 K | 1 μm | DC | Conductance quantization | 7 |
| Y-branch switch | 4 K | 1 μm | ~1 GHz | Electron beam steering | 4 |
| Electron Mach-Zehnder | 20 mK | 5 μm | DC-100 MHz | Coherent interference | 3 |
| Ballistic rectifier | 4 K | 0.5 μm | ~1 THz | Nonlinear transport | 3 |
| ZB oscillator | 4 K | 0.1 μm | ~1 THz | THz emission (speculative) | 2 |
| Electron prism | 4 K | 1 μm | DC | Energy/momentum filtering | 2 |

### 4.3 Fabrication Feasibility

**Achievable today (2026):**
- Electron beam lithography: feature size ~5-10 nm
- Modulation-doped GaAs/AlGaAs heterostructures: mobility 10⁷ cm²/V·s at 0.3K
- Gate-defined quantum point contacts: reproducible, tunable
- Single-electron transistors (SET): charge sensitivity 10⁻⁶ e/√Hz

**Not yet achievable (10+ years):**
- Multi-gate electron wave interferometer arrays (>10 gates) with uniform coherence
- Room-temperature electron wave coherence (in topological insulators? quantum spin Hall edge states?)
- ZB-synchronized clock distribution across a chip
- Integration with conventional CMOS at scale

### 4.4 Energy Efficiency Comparison

| Technology | Operations/Joule | Operations/Second | Joules/Operation |
|:-----------|:----------------:|:-----------------:|:----------------:|
| CMOS (7nm, 2026) | 10¹² | 10¹¹ | 10⁻¹⁵ |
| Optical Fourier processor | 10¹⁵ (MVM) | 10¹² | 10⁻¹⁵ |
| Superconducting qubit | 10³ | 10⁶ | 10⁻⁹ |
| Trapped ion qubit | 10¹ | 10³ | 10⁻⁷ |
| Hypothetical ZB computer | 10¹⁴ (est.) | 10¹² (est.) | 10⁻¹⁴ (est.) |
| Human brain (for reference) | 10¹³ | 10¹⁵ | 10⁻¹³ |

**Analysis:** Optical Fourier processors already match CMOS in energy efficiency for specific workloads (convolution, MVM). A ZB-based computer, operating at ~1 THz with single-electron transport, could theoretically achieve comparable efficiency — but the cryogenic cooling overhead (10⁴-10⁵ × power penalty) negates any advantage unless room-temperature ZB coherence is achieved.

---

## Phase 1 Summary

| Task | Key Finding | Verdict |
|:-----|:------------|:--------|
| T1.1 — Wave computer model | Linear wave computers map onto **BPP**; nonlinear (χ²) onto **BQP** (CV-QC). Formal 4-tuple model: W(N, L, M, f). | ✅ Model defined |
| T1.2 — Correlation taxonomy | 6-level hierarchy from classical to contextuality. Wave computers at Level 1; quantum at Levels 2-5. Boundary = discord/entanglement. | ✅ Taxonomy complete |
| T1.3 — Analog computing survey | History teaches: linear analog = BPP at best; super-Turing requires infinite precision (unphysical). Nonlinearity is the escape hatch to BQP. | ✅ Survey complete |
| T1.4 — Electron wave constraints | L_φ ~ 1-10 μm at cryogenic T. TRL 2-5 depending on device. Room-temp ZB impossible with current materials; 10-20 year horizon. | ✅ Constraints mapped |

---

> **Status:** ✅ Phase 1 (T1.1-T1.4) ALL EXECUTED | **Next:** Phase 2 (T2.1-T2.4) → Core Case Studies
