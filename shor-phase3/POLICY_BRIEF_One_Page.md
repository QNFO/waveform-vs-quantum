# POLICY BRIEF — ONE PAGE
## Shor's Algorithm: What It Actually Proves and What It Doesn't

**July 2026 | QNFO Research**

---

### THE CLAIM

Shor's 1994 algorithm is widely cited as proof that large-scale quantum computers will break RSA encryption, driving a global migration to post-quantum cryptography (PQC).

### THE REALITY

Shor proved **FACTORING ∈ BQP** — that a quantum computer *could* factor integers efficiently. The claim that quantum computers *will* break RSA requires an additional, **unproven** premise: **FACTORING ∉ BPP** — that no polynomial-time classical factoring algorithm exists. After 30 years, this remains an open problem equivalent to separating major complexity classes.

### THE MATH

```
FACTORING ∈ BQP (PROVEN ✓) + FACTORING ∉ BPP (UNPROVEN ✗) = Quantum Advantage (UNCERTAIN)
```

Without FACTORING ∉ BPP, Shor's algorithm demonstrates that factoring is *in* BQP — but not that BQP is *larger than* BPP. A breakthrough classical factoring algorithm would collapse the quantum advantage claim without disproving anything Shor proved.

### THE PHYSICS

RSA-2048 factoring requires:
- **4,099 logical qubits** → **2.1–7.9 million physical qubits** (depending on error rates)
- Gate fidelities of **≥99.99%** at scale
- Under optimistic IBM/Google roadmaps: hardware sufficient **~2040**

### THE ARCHITECTURE

≥80% of known exponential quantum speedups reduce to the **abelian hidden subgroup problem** — the same algebraic trick (period-finding via quantum interference) applied to different problems. Quantum advantage is **narrow**, not general.

### THE NARRATIVES

| Source | What They Say | What's Missing |
|:-------|:-------------|:---------------|
| NIST PQC docs | "Quantum computers will break RSA" | No explicit acknowledgment of FACTORING ∉ BPP uncertainty |
| Expert surveys (Mosca) | RSA-2048 "likely" broken by 2035–2045 | No distinction between BQP membership and practical feasibility |
| Media coverage | "Quantum supremacy achieved" | Conflation of sampling experiments with cryptographic relevance |

### RECOMMENDATIONS

1. **Migration timelines should model uncertainty explicitly** — treat FACTORING ∉ BPP as a Bayesian prior, not a settled fact
2. **Hardware roadmaps should report error bars** on crossover estimates reflecting fidelity sensitivity
3. **The invariant is narrow but genuine:** Shor proves that abelian algebraic periodicity is quantum-detectable — not that quantum computers are generically superior to classical ones
4. **PQC migration is prudent hedging**, not a mathematical necessity — the cost-benefit calculus should treat it as insurance against an uncertain threat, not a response to a proven one

### KEY NUMBERS

| Metric | Value |
|:-------|:------|
| Shor's proven gate complexity | O(n³) |
| Logical qubits for RSA-2048 | 4,099 |
| Physical qubits required (median) | 2.1M |
| Crossover year (optimistic) | ~2040 |
| GNFS complexity constant c | 1.923 (stable since 1993) |
| Fraction of speeds from abelian HSP | ≥80% |
| Years FACTORING ∉ BPP has been open | 30+ |

---

**Bottom line:** Migrate to PQC — it's prudent insurance. But understand that the urgency narrative rests on an unproven premise, not a proven theorem. Shor's algorithm is a brilliant discovery about quantum interference, not a proof that quantum computers will break the internet.
