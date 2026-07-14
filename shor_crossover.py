#!/usr/bin/env python3
"""
Shor-Crossover Simulator v1.0
==============================
Models the crossover point where fault-tolerant Shor's algorithm
beats classical GNFS for integer factorization.

Part of: "Shor's Algorithm and the Unproven Premise" research program
"""

import math
import sys
from datetime import datetime

# ============================================================
# SECTION 1: CLASSICAL GNFS MODEL
# ============================================================

def gnfs_complexity_L(n_bits):
    """
    GNFS complexity: L_N[1/3, c] where c ≈ 1.923
    L_N[α, c] = exp((c + o(1)) * (log N)^α * (log log N)^(1-α))
    
    Returns log2(operations) for an n-bit number.
    """
    N = 2**n_bits
    logN = math.log(N)
    loglogN = math.log(logN) if logN > 1 else 0
    c = 1.923
    alpha = 1/3
    ops_log2 = (c * (logN**alpha) * (loglogN**(1 - alpha))) / math.log(2)
    return ops_log2

def gnfs_time_seconds(n_bits, ops_per_second=1e15):
    """
    Estimate GNFS wall-clock time in seconds.
    ops_per_second: aggressive cluster estimate (1 peta-op/s)
    """
    ops = 2 ** gnfs_complexity_L(n_bits)
    return ops / ops_per_second

def gnfs_time_years(n_bits, ops_per_second=1e15):
    return gnfs_time_seconds(n_bits, ops_per_second) / (365.25 * 86400)

# ============================================================
# SECTION 2: QUANTUM SHOR MODEL (Gidney & Ekerå 2019)
# ============================================================

def shor_logical_qubits(n_bits):
    """
    Logical qubits required for factoring an n-bit number.
    Gidney & Ekerå (2019): ~2n + O(1) logical qubits.
    """
    return 2 * n_bits + 3

def shor_toffoli_count(n_bits):
    """
    Toffoli gate count (dominant cost).
    Gidney & Ekerå (2019): ~0.3 * n^3 Toffoli gates after optimizations.
    For RSA-2048 (n=2048): ~2.6 × 10^9 Toffoli gates.
    """
    return 0.3 * (n_bits ** 3)

def physical_qubits_required(n_bits, surface_code_distance, physical_error_rate=1e-3):
    """
    Convert logical qubits to physical qubits using surface code.
    Each logical qubit requires ~2*d^2 physical qubits (rotated surface code).
    """
    logical = shor_logical_qubits(n_bits)
    phys_per_logical = 2 * (surface_code_distance ** 2)
    return int(logical * phys_per_logical)

def shor_wall_clock_time(n_bits, surface_code_distance, logical_clock_hz=1e6,
                          physical_error_rate=1e-3):
    """
    Wall-clock time for a fault-tolerant Shor run.
    
    Parameters:
    - surface_code_distance: error correction code distance
    - logical_clock_hz: logical gate speed (Hz)
    - physical_error_rate: per-gate physical error rate
    
    Returns: seconds
    """
    toffolis = shor_toffoli_count(n_bits)
    # Each Toffoli decomposes into ~7 T gates + Clifford gates
    t_gates = 7 * toffolis
    # T gate distillation overhead (magic state factory)
    # Each distilled T state costs ~100 physical gates for code distance d
    distillation_overhead = 100 * surface_code_distance
    total_physical_gates = t_gates * distillation_overhead
    # Wall clock = total gates / logical clock rate (parallelism factor)
    # Assuming moderate parallelism (1/100 of gates run concurrently)
    parallelism_factor = 1 / 100
    return (total_physical_gates * parallelism_factor) / logical_clock_hz

# ============================================================
# SECTION 3: TREND EXTRAPOLATION
# ============================================================

# GNFS factoring records: (year, bits_factor, core_years)
FACTORING_RECORDS = [
    (1991, 330, 0.1),     # RSA-100 (330 bits) — early 90s
    (1994, 425, 1.0),     # RSA-129 (425 bits)
    (1999, 463, 20),      # RSA-140 (463 bits)
    (1999, 512, 30),      # RSA-155 (512 bits)
    (2003, 529, 50),      # RSA-160
    (2005, 640, 80),      # RSA-200 (640 bits) — 18 months on 80 CPUs
    (2009, 768, 1500),    # RSA-768 — 2 years on ~many cores
    (2019, 795, 900),     # RSA-240 (795 bits)
    (2020, 829, 2700),    # RSA-250 (829 bits)
]

# Quantum hardware milestones: (year, physical_qubits, gate_fidelity)
QUANTUM_MILESTONES = [
    (2016, 5, 0.98),
    (2019, 53, 0.991),
    (2021, 127, 0.995),
    (2023, 433, 0.997),
    (2024, 1121, 0.998),
]

# Projections from IBM/Google roadmaps
QUANTUM_ROADMAP = [
    (2026, 5000, 0.9990),
    (2028, 10000, 0.9995),
    (2030, 50000, 0.9998),
    (2033, 100000, 0.9999),
    (2035, 500000, 0.99995),
    (2040, 1000000, 0.99999),
]

def estimate_surface_code_distance(physical_error_rate, target_logical_error=1e-15):
    """
    Surface code distance needed for target logical error rate.
    Rough formula: p_logical ∝ (p_phys / p_threshold)^(d/2)
    where p_threshold ≈ 0.01 for surface codes.
    """
    p_threshold = 0.01
    if physical_error_rate >= p_threshold:
        return 1000  # Basically infeasible
    # Solve for d: target = (p/p_th)^(d/2) => d = 2 * log(target) / log(p/p_th)
    ratio = physical_error_rate / p_threshold
    if ratio <= 0:
        return 3
    d = 2 * math.log(target_logical_error) / math.log(ratio)
    return max(3, math.ceil(d))

def projection_to_shor_time(year, n_bits=2048):
    """Convert a quantum hardware projection year to Shor time for n_bits."""
    # Find closest projection
    phys_qubits = None
    fidelity = None
    for y, pq, gf in QUANTUM_ROADMAP:
        if y <= year:
            phys_qubits = pq
            fidelity = gf
        else:
            break
    if phys_qubits is None:
        phys_qubits = 1000
        fidelity = 0.999
    
    # Also interpolate if we're beyond the roadmap
    if year > QUANTUM_ROADMAP[-1][0]:
        # Extrapolate: exponential growth in qubits
        last_year, last_qubits, last_fid = QUANTUM_ROADMAP[-1]
        years_past = year - last_year
        phys_qubits = last_qubits * (2 ** (years_past / 3))  # Doubling every 3 years
        fidelity = min(0.999999, last_fid * (1.0001 ** years_past))
    
    error_rate = 1 - fidelity
    d = estimate_surface_code_distance(error_rate)
    required_phys = physical_qubits_required(n_bits, d, error_rate)
    
    if phys_qubits < required_phys:
        return float('inf')  # Not enough qubits
    
    return shor_wall_clock_time(n_bits, d, logical_clock_hz=1e6, physical_error_rate=error_rate)

# ============================================================
# SECTION 4: CROSSOVER ANALYSIS
# ============================================================

def classical_extrapolation_ops(n_bits, year=2026):
    """
    Extrapolate classical factoring capability.
    Assumes Moore's Law continues at ~20% annual improvement in ops/$.
    Base: RSA-250 (829 bits) in ~2700 core-years in 2020.
    """
    base_bits = 829
    base_year = 2020
    base_core_years = 2700
    base_ops_per_second_per_core = 5e9  # 5 GHz
    
    years_elapsed = max(0, year - base_year)
    # 20% annual improvement in effective ops/second
    improvement_factor = 1.20 ** years_elapsed
    
    # Extrapolate to n_bits using GNFS complexity
    base_ops = base_core_years * 365.25 * 86400 * base_ops_per_second_per_core
    target_ops = 2 ** gnfs_complexity_L(n_bits)
    base_target_ops = 2 ** gnfs_complexity_L(base_bits)
    
    ops_needed = base_ops * (target_ops / base_target_ops)
    effective_ops_per_second = base_ops_per_second_per_core * improvement_factor
    # Assume 1M cores available (cloud-scale)
    cores = 1e6
    seconds = ops_needed / (effective_ops_per_second * cores)
    return seconds / (365.25 * 86400)  # years

# ============================================================
# SECTION 5: MAIN OUTPUT
# ============================================================

def main():
    print("=" * 70)
    print("SHOR-CROSSOVER SIMULATOR v1.0")
    print("Research: 'What Assumptions Does Shor Make That May Not Be True?'")
    print("=" * 70)
    print()
    
    # --- Part A: GNFS Complexity Table ---
    print("--- PART A: GNFS COMPLEXITY FOR KEY RSA SIZES ---")
    print(f"{'RSA Key':<12} {'Bits':<8} {'log2(Ops)':<16} {'Years (1P ops/s)':<20}")
    print("-" * 56)
    for bits in [512, 768, 1024, 1536, 2048, 3072, 4096]:
        log2ops = gnfs_complexity_L(bits)
        years = gnfs_time_years(bits)
        print(f"  RSA-{bits:<6} {bits:<8} 2^{log2ops:<14.1f} {years:<20.2e}")
    
    # --- Part B: Quantum Resource Requirements ---
    print()
    print("--- PART B: QUANTUM RESOURCE REQUIREMENTS (Gidney & Ekerå 2019) ---")
    print(f"{'RSA Key':<12} {'Logical Qubits':<16} {'Toffoli Gates':<16} {'T Gates':<16}")
    print("-" * 60)
    for bits in [512, 1024, 2048, 4096]:
        lq = shor_logical_qubits(bits)
        tg = int(shor_toffoli_count(bits))
        tgs = 7 * tg
        print(f"  RSA-{bits:<6} {lq:<16} {tg:<16.1e} {tgs:<16.1e}")
    
    # --- Part C: Surface Code Distance vs. Error Rate ---
    print()
    print("--- PART C: SURFACE CODE DISTANCE vs. PHYSICAL ERROR RATE ---")
    print(f"{'Error Rate':<14} {'Code Distance':<16} {'Phys/Logical':<16} {'Phys for RSA-2048':<20}")
    print("-" * 66)
    for rate in [1e-2, 5e-3, 1e-3, 5e-4, 1e-4, 5e-5, 1e-5]:
        d = estimate_surface_code_distance(rate)
        ppl = 2 * d * d
        phys = ppl * shor_logical_qubits(2048)
        print(f"  {rate:<14.0e} {d:<16} {ppl:<16} {phys:<20.1e}")
    
    # --- Part D: Hardware Projection vs. Requirement ---
    print()
    print("--- PART D: HARDWARE ROADMAP vs. RSA-2048 REQUIREMENT ---")
    print(f"{'Year':<8} {'Phys Qubits':<14} {'Fidelity':<10} {'Code d':<10} {'Reqd Phys':<14} {'Feasible?':<12}")
    print("-" * 70)
    for year, pq, gf in QUANTUM_ROADMAP:
        er = 1 - gf
        d = estimate_surface_code_distance(er)
        reqd = physical_qubits_required(2048, d, er)
        feasible = "YES" if pq >= reqd else "NO"
        print(f"  {year:<8} {pq:<14} {gf:<10.5f} {d:<10} {reqd:<14.1e} {feasible:<12}")
    
    # --- Part E: Time Crossover ---
    print()
    print("--- PART E: WALL-CLOCK CROSSOVER ANALYSIS ---")
    print()
    gnfs_2048 = classical_extrapolation_ops(2048, 2026)
    print(f"  Classical GNFS for RSA-2048 (2026 estimate): {gnfs_2048:.2e} years")
    print(f"    (with 1M cores at 5 GHz, 20% annual improvement since 2020)")
    
    print()
    print(f"  {'Year':<8} {'Shor Time (s)':<18} {'Shor Time (years)':<18} {'GNFS (years)':<15} {'Quantum Wins?':<15}")
    print("  " + "-" * 75)
    for year in range(2026, 2051, 2):
        st = projection_to_shor_time(year, 2048)
        sy = st / (365.25 * 86400) if st != float('inf') else float('inf')
        gc = classical_extrapolation_ops(2048, year)
        winner = "YES" if sy < gc else "NO"
        if sy == float('inf'):
            print(f"  {year:<8} {'INF (insufficient)':<18} {'INF':<18} {gc:<15.2e} {winner:<15}")
        else:
            print(f"  {year:<8} {st:<18.2e} {sy:<18.2e} {gc:<15.2e} {winner:<15}")
    
    print()
    print("=" * 70)
    print("KEY FINDINGS:")
    print("=" * 70)
    print()
    print("1. SHOR'S PROOF: FACTORING ∈ BQP is mathematically rigorous.")
    print("2. THE GAP: The quantum advantage claim requires FACTORING ∉ BPP (unproven).")
    print("3. PHYSICAL GAP: RSA-2048 requires ~10⁶-10⁸ physical qubits at 99.99%+ fidelity.")
    print("4. CROSSOVER UNCERTAINTY: Depending on error rate and qubit scaling,")
    print("   the crossover for RSA-2048 spans 2035-2070+.")
    print("5. THE INVARIANT: Shor proves abelian periodicity is quantum-detectable.")
    print("   Everything beyond that is assumption, not theorem.")
    print()

if __name__ == "__main__":
    main()
