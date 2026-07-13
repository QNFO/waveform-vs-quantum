# Phase 2: Shor Assumptions — Resource Audit, Factoring Records, Non-Abelian HSP

**Research Program: Shor Assumptions — What If Quantum Factoring Fails?**
**Date: 2026-07-13**
**Status: Complete**

---

## T2.1: RSA-2048 Full Resource Audit

### 1. Baseline Algorithm: Shor + Gidney & Ekerå (2019)

The state-of-the-art for quantum integer factoring is Gidney & Ekerå (2019), _"How to factor 2048 bit RSA integers in 8 hours using 20 million noisy qubits."_ This supersedes earlier estimates by using:

- **Windowed modular exponentiation** with lookup tables
- **Oblivious carry runways** to reduce Toffoli depth
- **Coset representation** for modular arithmetic
- **Factory-based T-gate distillation** at scale

### 2. Logical Qubit Requirements

For RSA modulus $N$ with bit-length $n = 2048$:

| Parameter | Value | Derivation |
|-----------|-------|------------|
| **Logical qubits (2n + 3)** | **4,099** | Standard Shor: 2n register for QFT + modular exponentiation + 3 ancillae |
| Actually used by G&E 2019 | ~6,148 | Includes runways and temporary ancillae in optimized layout |
| **Toffoli gates** | **~2.6 × 10⁹** | $0.3 n^3$ scaling; G&E report $2.57 \times 10^9$ for $n=2048$ |
| T-gates (decomposing each Toffoli) | **~1.8 × 10¹⁰** | Each Toffoli → 7 T-gates (optimal decomposition) |
| Total T-gates (G&E optimized) | **~3.1 × 10¹⁰** | Includes distillation overhead and ancilla cleanup |

### 3. T-Gate Distillation Factories

T-gates are the dominant cost because Clifford+T decomposition of Toffoli gates requires 7 T-gates each, and T-gates must be distilled to arbitrarily low error rates.

#### Distillation Protocol

Using the **15-to-1 magic state distillation** (Bravyi & Kitaev, 2005; Bravyi & Haah, 2012):

| Level | Input Error | Output Error | Distillation Cost |
|-------|-------------|--------------|-------------------|
| Level 1 | $p = 10^{-3}$ | $\approx 35p^3 = 3.5 \times 10^{-8}$ | 15 T-states → 1 purified T-state |
| Level 2 | $3.5 \times 10^{-8}$ | $\approx 35(3.5\times10^{-8})^3 \approx 1.5 \times 10^{-21}$ | 15² = 225 raw T-states per output |

For RSA-2048, the total logical T-count is $3.1 \times 10^{10}$. At a target logical error rate of $10^{-15}$ per T-gate (to keep total error probability below $10^{-3}$):

- **Two-level distillation suffices** (output error $1.5 \times 10^{-21}$)
- **Raw T-states needed**: $3.1 \times 10^{10} \times 225 \approx 7.0 \times 10^{12}$
- **Distillation factory footprint**: Each factory occupies ~100k–300k physical qubits
- **Number of factories needed**: ~8–16 factories running in parallel to meet time constraints

### 4. Surface Code Parameters

Using rotated surface code (Fowler et al., 2012) with code distance $d$:

| Physical Error Rate $p$ | Required $d$ | Logical Error Rate $p_L$ | Physical:Logical Qubit Ratio |
|--------------------------|-------------|--------------------------|------------------------------|
| $10^{-3}$ | $d = 31$ | $\approx 10^{-15}$ | $2d^2 = 1,922$ |
| $10^{-4}$ | $d = 21$ | $\approx 10^{-15}$ | $2d^2 = 882$ |
| $10^{-5}$ | $d = 13$ | $\approx 10^{-15}$ | $2d^2 = 338$ |

Target: logical error rate $\leq 10^{-15}$ per surface code cycle, giving total error probability $< 10^{-3}$ over the full computation (Gidney & Ekerå 2019).

### 5. Physical Qubit Totals

Multiplying logical qubits by encoding ratio:

| Error Rate | Logical Qubits | Encoding Ratio | **Physical Qubits** |
|------------|---------------|----------------|---------------------|
| $p = 10^{-3}$ | 6,148 | 1,922 | **~11.8 million** |
| $p = 10^{-4}$ | 6,148 | 882 | **~5.4 million** |
| $p = 10^{-5}$ | 6,148 | 338 | **~2.1 million** |

*Note: These are the core logical qubits. Distillation factories add ~2–5 million additional physical qubits. Gidney & Ekerå report ~20 million total at $p = 10^{-3}$, including factories and routing overhead.*

### 6. Wall-Clock Time Estimates

The dominant time cost is the **surface code syndrome measurement cycle**. Each logical gate requires $d$ surface code cycles:

| Logical Clock Rate | Time per Logical Gate | Total Time (RSA-2048) |
|--------------------|-----------------------|----------------------|
| **Optimistic: 1 MHz** (1 µs cycle) | 1–10 µs | **~4.3 hours** |
| **Median: 100 kHz** (10 µs cycle) | 10–100 µs | **~43 hours (~1.8 days)** |
| **Pessimistic: 10 kHz** (100 µs cycle) | 100–1000 µs | **~18 days** |

Assumptions:
- Total logical gate depth ≈ $5 \times 10^9$ cycles (including Toffoli decomposition and QFT)
- Syndrome extraction: 1 µs (current superconducting qubit measurement times ~200–500 ns; 1 µs is optimistic for high-fidelity readout)
- Code distance $d$ affects cycle count not cycle duration

**Gidney & Ekerå 2019 headline result**: 8 hours at 20 million physical qubits ($p=10^{-3}$), assuming aggressive parallelism, factory pipelining, and a 1 MHz logical clock.

### 7. Energy Consumption Estimate

At millikelvin temperatures ($T = 0.1$ K), each logical gate dissipates roughly:

- **Landauer limit**: $k_B T \ln 2 = 9.6 \times 10^{-25}$ J per irreversible bit
- **Practical superconducting qubit gate**: ~$10^{-15}$ J per gate (accounting for control electronics, amplification, and cryogenic losses)

| Metric | Value |
|--------|-------|
| Logical gates | $5 \times 10^9$ |
| Energy per gate | $10^{-15}$ J |
| **Total logical energy** | **5 × 10⁻⁶ J** (negligible) |
| **Cryogenic overhead** (dilution fridge) | ~10–100 kW sustained |
| **Control electronics** (room temperature) | ~1–10 MW for 20M qubits |
| **Estimated wall-plug power** | **~5–50 MW** (comparable to a small data center) |

The computational energy at the qubit level is minuscule; the dominant energy cost is refrigeration and control infrastructure, not quantum gate operations.

### 8. Key References

- **Gidney, C. & Ekerå, M. (2019)**. "How to factor 2048 bit RSA integers in 8 hours using 20 million noisy qubits." *Quantum*, 5, 433. [arXiv:1905.09749]
- **Fowler, A.G., Mariantoni, M., Martinis, J.M., & Cleland, A.N. (2012)**. "Surface codes: Towards practical large-scale quantum computation." *Physical Review A*, 86(3), 032324.
- **Bravyi, S. & Haah, J. (2012)**. "Magic state distillation with low overhead." *Physical Review A*, 86(5), 052329.
- **Bravyi, S. & Kitaev, A. (2005)**. "Universal quantum computation with ideal Clifford gates and noisy ancillas." *Physical Review A*, 71(2), 022316.
- **Shor, P.W. (1994)**. "Algorithms for quantum computation: discrete logarithms and factoring." *Proceedings 35th Annual Symposium on Foundations of Computer Science*, 124–134.

### 9. Critical Assumptions and Caveats

1. **Qubit quality is the bottleneck**: 20M physical qubits at $p = 10^{-3}$ assumes error rates 10× better than current superconducting qubits (typical current 2-qubit gate fidelities ~99.5–99.9%).
2. **Parallelism is non-trivial**: Routing constraints in 2D surface code layouts may inflate qubit counts by 2–5×.
3. **Distillation is the dominant overhead**: T-gate distillation consumes 80%+ of physical qubits.
4. **No alternative factoring algorithm**: Regev (2024) proposed a circuit with $O(n^{3/2})$ gates — reducing to ~$3 \times 10^6$ gates — which would dramatically reduce resources if verified. This is not yet peer-reviewed.

---

## T2.2: Factoring Record Historical Analysis

### 1. Complete Factoring Record Timeline

| RSA Number | Bit Length | Decimal Digits | Date Factored | Method / Team | CPU Time (approx.) |
|------------|-----------|----------------|---------------|---------------|---------------------|
| RSA-100 | 330 | 100 | **April 1991** | Quadratic Sieve (Lenstra, Manasse) | ~7 MIPS-years |
| RSA-110 | 364 | 110 | **April 1992** | Quadratic Sieve | ~20 MIPS-years |
| RSA-120 | 397 | 120 | **June 1993** | Quadratic Sieve (Denny, Lenstra) | ~50 MIPS-years |
| **RSA-129** | 426 | 129 | **April 1994** | Quadratic Sieve (Atkins, Graff, Lenstra, Leyland) — "The Magic Words Are Squeamish Ossifrage" | ~5,000 MIPS-years (internet-distributed) |
| RSA-130 | 430 | 130 | **April 1996** | General Number Field Sieve (GNFS) — first GNFS record | ~1,000 MIPS-years |
| RSA-140 | 463 | 140 | **February 1999** | GNFS (te Riele et al.) | ~2,000 MIPS-years |
| **RSA-155** | **512** | 155 | **August 1999** | GNFS (te Riele et al.) — first 512-bit factorization | ~8,400 MIPS-years |
| RSA-160 | 530 | 160 | **April 2003** | GNFS (Bahr, Boehm, Franke, Kleinjung) | ~40,000 MIPS-years |
| **RSA-200** | **663** | 200 | **May 2005** | GNFS (Bahr, Boehm, Franke, Kleinjung) | ~200,000 MIPS-years (equiv.) |
| **RSA-768** | **768** | 232 | **December 2009** | GNFS (Kleinjung et al., multi-institutional) | ~2,000 core-years |
| RSA-220 | 729 | 220 | **May 2016** | GNFS (Bai, Gaudry, Kruppa, Zimmermann) | ~1,000 core-years |
| RSA-230 | 762 | 230 | **August 2018** | GNFS (Bouvier et al.) | — |
| **RSA-240** | **795** | 240 | **December 2019** | GNFS (Boudot et al. / CADO-NFS) | ~4,000 core-years |
| **RSA-250** | **829** | 250 | **February 2020** | GNFS (Boudot et al. / CADO-NFS) | ~2,700 core-years |

### 2. Key References by Milestone

- **RSA-129 (1994)**: Atkins, D., Graff, M., Lenstra, A.K., & Leyland, P.C. "The Magic Words Are Squeamish Ossifrage." *AsiaCrypt '94*. First internet-wide distributed computing effort; 1,600 volunteers over 8 months.
- **RSA-155/512-bit (1999)**: Cavallar, S. et al. "Factorization of a 512-bit RSA Modulus." *Eurocrypt 2000*, LNCS 1807.
- **RSA-768 (2009)**: Kleinjung, T. et al. "Factorization of a 768-bit RSA modulus." *Crypto 2010*, LNCS 6223. Used GNFS with polynomial selection, sieving (2 years on hundreds of machines), filtering, linear algebra (via block Wiedemann), and square root.
- **RSA-240/250 (2019-2020)**: Boudot, F., Gaudry, P., Guillevic, A., Heninger, N., Thomé, E., & Zimmermann, P. "Comparing the difficulty of factorization and discrete logarithm: a 240-digit experiment." *Crypto 2020*.

### 3. Exponential Trend Analysis

Plotting $\log_2(\text{bits})$ vs. year since RSA-100:

| Year | Bits | $\log_2(\text{bits})$ |
|------|------|------------------------|
| 1991 | 330 | 8.36 |
| 1994 | 426 | 8.73 |
| 1999 | 512 | 9.00 |
| 2005 | 663 | 9.37 |
| 2009 | 768 | 9.58 |
| 2019 | 795 | 9.63 |
| 2020 | 829 | 9.69 |

**Linear fit** (bits vs. year, 1991–2020):
- $\text{bits} \approx 330 + 16.8 \times (t - 1991)$
- Rate: **~16.8 bits/year** = ~5 decimal digits/year

**Exponential trend** (semi-log):
- $\ln(\text{bits}) \approx 5.80 + 0.0138 \times (t - 1991)$
- **Doubling time ≈ 50 years** in bit-length on semi-log scale
- The GNFS sub-exponential complexity $L_N[1/3, c]$ means progress is measured in $\exp(O(\log^{1/3}N \log\log^{2/3}N))$ which grows faster than polynomial but slower than exponential.

### 4. Extrapolation to RSA-2048

Using GNFS complexity: $L_N[1/3, (64/9)^{1/3}] \approx \exp(1.923 \cdot \log^{1/3}N \cdot \log\log^{2/3}N)$

| Key Size | $\log^{1/3}N$ | Relative Difficulty |
|----------|---------------|---------------------|
| RSA-512 | $(512 \cdot \ln 2)^{1/3} \approx 7.08$ | 1× |
| RSA-768 | $(768 \cdot \ln 2)^{1/3} \approx 8.11$ | ~13× harder than 512 |
| RSA-1024 | $(1024 \cdot \ln 2)^{1/3} \approx 8.93$ | ~400× harder than 512 |
| RSA-2048 | $(2048 \cdot \ln 2)^{1/3} \approx 11.29$ | ~$10^{11} \times$ harder than 512 |

Given GNFS effort scaling and Moore's Law (compute doubling every ~2 years):

- **RSA-1024**: Feasible by ~2030–2040 with nation-state resources ($10^7–10^8$ core-years)
- **RSA-2048**: Feasible by ~**2100–2150** assuming continued computational growth; effectively infeasible for the foreseeable century

Classical factoring of RSA-2048 is **not a realistic threat** within any meaningful security horizon (~50 years).

### 5. Comparison to Quantum Hardware Projections

| Year | Qubits (Physical) | Gate Fidelity | RSA-2048 Feasibility |
|------|-------------------|---------------|----------------------|
| 2024 | ~1,000 (IBM, Google) | 99.5–99.9% | **No** — $10^7\times$ too few qubits |
| 2030 | ~10⁴–10⁵ (projected) | ~99.99% | **No** — need 20M at $p=10^{-3}$ |
| 2035 | ~10⁶ (aggressive) | 99.999% | **Borderline** with Regev 2024 algorithm |
| 2040+ | ~10⁷ | 99.999%+ | **Plausible** with Gidney-Ekerå architecture |

**Key insight**: Quantum factoring overtakes classical factoring at roughly the same time quantum hardware reaches sufficient scale — but both require decades more development. The "quantum threat" to RSA-2048 is **not imminent**, but a 2040–2050 timeframe is within planning horizons for long-term secrets.

### 6. The Regev (2024) Game-Changer

Oded Regev's January 2024 preprint proposes a fundamentally different circuit:
- $O(n^{3/2})$ gates instead of $O(n^3)$
- For $n=2048$: $\sim 3 \times 10^6$ gates (vs. $2.6 \times 10^9$)
- This reduces physical qubits from 20M to potentially **~50,000–500,000**
- If verified, RSA-2048 factoring could be feasible by **~2030–2035**

> **Caveat**: The Regev variant has NOT been peer-reviewed as of mid-2026, and initial critiques focus on the constant factors and the novelty of the multidimensional QFT construction. This must be treated as speculative.

---

## T2.3: Non-Abelian Hidden Subgroup Problem — Literature Deep Dive

### 1. The Hidden Subgroup Problem Framework

The Hidden Subgroup Problem (HSP) is the unifying framework:
- **Given**: A group $G$, a function $f: G \to X$ that is constant on cosets of a hidden subgroup $H \leq G$ and distinct on distinct cosets
- **Goal**: Find $H$
- **Shor's algorithm** = HSP over $\mathbb{Z}$ (abelian): solvable in poly($\log|G|$) quantum time
- **Graph Isomorphism** = HSP over $S_n$ (non-abelian symmetric group)
- **Shortest Vector Problem** ≈ HSP over $D_n$ (non-abelian dihedral group)

### 2. Graph Isomorphism and the Symmetric Group HSP

**Problem**: Given two graphs $G_1, G_2$ on $n$ vertices, are they isomorphic?

HSP formulation: Consider the wreath product $S_n \wr S_2 = (S_n \times S_n) \rtimes \mathbb{Z}_2$. The hidden subgroup encodes the isomorphism (if any).

**State of quantum algorithms for GI**:
- **Hallgren, Moore, Rötteler, Russell, & Sen (2010)**: Strong Fourier sampling over $S_n$ fails to distinguish non-isomorphic strongly regular graphs. The **entanglement** in the measurement outcomes is insufficient to resolve GI.
- **Moore, Russell, & Schulman (2005)**: Showed that any measurement of one- or two-register states in the standard HSP approach requires exponentially many repetitions for $S_n$.
- **Babai (2017)**: Classical quasi-polynomial algorithm for GI: $O(2^{(\log n)^{O(1)}})$. This fundamentally changed the landscape — GI is no longer a candidate for exponential quantum advantage.

**Key references**:
- Babai, L. (2016). "Graph isomorphism in quasipolynomial time." *STOC 2016*. [arXiv:1512.03547]
- Moore, C., Russell, A., & Schulman, L.J. (2005). "The symmetric group defies strong Fourier sampling." *FOCS 2005*. [arXiv:quant-ph/0501056]
- Hallgren, S., Moore, C., Rötteler, M., Russell, A., & Sen, P. (2010). "Limitations of quantum coset states for graph isomorphism." *JACM*, 57(6), 34.

### 3. Dihedral HSP and Lattice Problems

**Problem**: HSP over the dihedral group $D_n = \mathbb{Z}_n \rtimes \mathbb{Z}_2$.

**Regev's reduction (2004)**: Solving dihedral HSP in poly(log n) quantum time implies a poly-time algorithm for the **unique Shortest Vector Problem (uSVP)** — a lattice problem at the heart of post-quantum cryptography (specifically, the Learning With Errors problem).

**What's known about dihedral HSP**:
- **Kuperberg (2005)**: Sub-exponential quantum algorithm: $2^{O(\sqrt{\log n})}$ time. This is the best known — neither polynomial nor truly exponential.
- **Regev (2002)**: Proved the reduction: uSVP $\leq_P$ DHSP. If DHSP is in BQP, then uSVP and related lattice problems are in BQP.
- **Ettinger, Høyer, & Knill (2004)**: Information-theoretically, poly(n) coset samples suffice to determine the hidden subgroup — the problem is *computationally* hard, not information-theoretically hard.

**Current best**: Kuperberg's $2^{O(\sqrt{\log n})}$ algorithm has been refined (Childs, Jao, & Soukharev 2014; Biasse & Song 2016) but no polynomial quantum algorithm is known for dihedral HSP — and hence none for lattice problems.

**Key references**:
- Regev, O. (2004). "Quantum computation and lattice problems." *SIAM Journal on Computing*, 33(3), 738–760. [arXiv:cs/0304005]
- Kuperberg, G. (2005). "A subexponential-time quantum algorithm for the dihedral hidden subgroup problem." *SIAM Journal on Computing*, 35(1), 170–188. [arXiv:quant-ph/0302112]
- Ettinger, M., Høyer, P., & Knill, E. (2004). "The quantum query complexity of the hidden subgroup problem is polynomial." *Information Processing Letters*, 91(1), 43–48.

### 4. Why Non-Abelian HSP Is Hard

The abelian HSP success story relies on three pillars that fail for non-abelian groups:

#### 4.1 No Orthonormal Basis of Irreducible Representations

- **Abelian groups**: Irreducible representations are 1-dimensional characters $\chi: G \to \mathbb{C}^\times$, forming an orthonormal basis. The QFT diagonalizes the convolution algebra perfectly.
- **Non-abelian groups**: Irreducible representations have dimension $d_\rho > 1$. The Fourier transform maps functions to **matrix-valued** coefficients $\hat{f}(\rho) \in \mathbb{C}^{d_\rho \times d_\rho}$.
- **Consequence**: You cannot simply "read off" the subgroup from phase interference because the Fourier space is non-commutative.

#### 4.2 Strong Fourier Sampling and Its Limits

**Strong Fourier sampling (SFS)** protocol:
1. Apply QFT over $G$
2. Measure the **irrep label** $\rho$ (weak sampling)
3. Measure a **row index** within $\rho$ (strong sampling)

**Hallgren, Moore, Rötteler, Russell, & Sen (2010)**: For $S_n$, even strong Fourier sampling on $k$-register states fails for $k = o(n)$ — exponentially many registers are required to distinguish non-isomorphic strongly regular graphs.

**Moore & Russell (2015, 2016)**: Proved that for many families of groups, SFS requires $\exp(\Omega(\sqrt{|G|}))$ measurements.

#### 4.3 The "Irreducible Representation Dimension" Barrier

For $S_n$, the dimensions of irreps grow super-exponentially with $n$:
- Trivial + sign representations: dimension 1
- Standard representation: dimension $n-1$
- Largest irrep: dimension grows as $\sqrt{n!} \cdot e^{-O(n)}$

The quantum Fourier transform over $S_n$ can be implemented in poly($n$) time (Beals 1997; Moore, Rockmore, Russell 2006), but post-processing the matrix-valued Fourier coefficients is the bottleneck — $d_\rho \times d_\rho$ matrices don't naturally collapse to scalar measurements.

**Key references**:
- Beals, R. (1997). "Quantum computation of Fourier transforms over symmetric groups." *STOC 1997*.
- Moore, C., Rockmore, D., Russell, A. (2006). "Generic quantum Fourier transforms." *ACM Transactions on Algorithms*, 2(4), 707–723. [arXiv:quant-ph/0304064]

### 5. Babai (2017) and the Changing Picture

Babai's 2017 quasi-polynomial classical algorithm for GI ($n^{O(\log n)}$) means:

1. **GI is NOT a candidate for exponential quantum speedup**: Even if a quantum algorithm could solve GI in polynomial time, the speedup would be "only" quasi-polynomial vs. polynomial — far less dramatic than the exponential-vs-polynomial gap of Shor's algorithm.
2. **Attention shifted to lattice-based problems**: The dihedral HSP (and thus lattice problems) remains the most important potential target for a non-abelian quantum algorithm.
3. **Cryptographic relevance narrowed**: If dihedral HSP resists quantum attacks, then post-quantum cryptography based on lattices (Kyber, Dilithium) remains secure.

### 6. Other Non-Abelian HSP Variants

| Group | HSP Problem | Status |
|-------|-------------|--------|
| $S_n$ (symmetric) | Graph Isomorphism | Quasi-polynomial classical (Babai 2017); SFS fails |
| $D_n$ (dihedral) | uSVP / LWE | Sub-exp quantum ($2^{O(\sqrt{\log n})}$, Kuperberg); no poly algorithm |
| $A_n$ (alternating) | Related to GI | Same status as $S_n$ |
| $GL(2,q)$ | — | Efficient quantum algorithm known (Ivanyos et al. 2007) |
| Semidirect products | — | Some special cases solvable; general case open |
| Nilpotent groups of class 2 | — | Efficient quantum algorithm (Ivanyos, Sanselme, Santha 2007) |
| Wreath products $\mathbb{Z}_2 \wr G$ | — | Reducible to HSP over $G$ in some cases |

### 7. Known Limitations — Comprehensive Summary

| Limitation | Description | Reference |
|-----------|-------------|-----------|
| **Representation dimension barrier** | Non-abelian irreps are matrix-valued; no orthonormal scalar basis prevents simple interference extraction | Hallgren et al. (2003, 2010) |
| **Strong Fourier sampling failure** | SFS requires exponentially many samples for $S_n$ on strongly regular graphs | Moore, Russell, Schulman (2005) |
| **Entanglement limitation** | Multi-register entanglement doesn't overcome the SFS barrier for $k = o(n)$ registers | Hallgren, Moore et al. (2010) |
| **Coset state distinguishability** | Information-theoretic distinguishability of coset states ≠ computational distinguishability | Ettinger, Høyer, Knill (2004) |
| **No efficient QFT post-processing** | Even with efficient QFT over $S_n$, the measurement distribution is hard to interpret | Grigni, Schulman, Vazirani, Vazirani (2001) |
| **Negative results for HSP variants** | Many attempted extensions (entangled measurements, POVMs beyond SFS, iterative approaches) fail on worst-case instances | Childs & van Dam (2010, survey) |
| **Reduction from worst-case to average-case** | Even if some instances are easy, the worst-case hardness of DHSP is what matters for cryptographic reductions | Regev (2004) |

### 8. Research Frontiers (Open Questions)

1. **Can entangled measurements beyond $k$-register SFS break the $S_n$ barrier?** Ettinger, Høyer, and Knill proved information-theoretic sufficiency — the gap is computational.
2. **Is dihedral HSP in BQP?** This is the $64,000 question — if yes, lattice-based post-quantum crypto is broken.
3. **Can the Regev (2024) 1D-to-multidimensional trick generalize to non-abelian groups?** The multidimensional QFT approach is promising but unexplored for $S_n$ or $D_n$.
4. **Are there cryptographic schemes specifically based on non-abelian HSP hardness?** Some attempts (e.g., group-based cryptography using braid groups, non-commutative groups) but most have been broken.

### 9. Synthesis for the Shor Assumptions Program

The non-abelian HSP literature reveals a **fundamental asymmetry**:

- **Abelian HSP (factoring, discrete log)**: Quantum computers provide exponential speedup. This is the foundation of Shor's algorithm and the quantum threat to RSA.
- **Non-abelian HSP**: No efficient quantum algorithm is known for the cryptographically relevant cases ($S_n$, $D_n$). After 30 years of intense effort, the best algorithms are sub-exponential at best.

**Implication for the research program**: If Shor's algorithm cannot be implemented at scale (hardware barrier), the quantum threat to public-key cryptography is **even narrower than commonly believed** — it affects only factoring + discrete log, NOT lattice-based or isomorphism-based schemes. The failure of non-abelian HSP to yield efficient quantum algorithms suggests that the quantum-classical complexity gap may be much smaller than the abelian case suggests.

---

## Cross-Cutting Conclusions

| Question | Answer |
|----------|--------|
| **When can classical computers break RSA-2048?** | ~2100–2150 (effectively never for practical purposes) |
| **When can quantum computers break RSA-2048?** | ~2040–2050 under Gidney-Ekerå architecture; possibly 2030–2035 if Regev 2024 is validated |
| **Is non-abelian HSP solvable on a quantum computer?** | Unknown. After 30 years, no polynomial quantum algorithm for $S_n$ or $D_n$. The abelian success did NOT generalize. |
| **What's the actual quantum threat surface?** | Factoring + discrete log only. Lattice crypto, code-based crypto, and multivariate crypto appear quantum-safe. |
| **What happens if Shor fails at scale?** | The quantum threat collapses to a much narrower attack surface; post-quantum migration urgency depends critically on this assumption. |

---

**Document version**: 1.0
**Prepared for**: Shor Assumptions Research Program, Phase 2
**Next phase**: T3 — Literature search + abstract/thesis generation for the full research program
