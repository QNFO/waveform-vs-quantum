#!/usr/bin/env python3
"""
Compute exact Shor's algorithm success probability given the
prime factorization of N.

Usage:
    python shor_success.py [p1 e1 p2 e2 ...]

Examples:
    python shor_success.py 3 1 7 1       # RSA semiprime N=3*7=21
    python shor_success.py 3 1 7 1 11 1  # Three primes N=3*7*11=231
"""

import sys
from math import gcd, log, ceil
from functools import reduce
from typing import List, Tuple


def v2(x: int) -> int:
    """2-adic valuation: largest e such that 2^e divides x."""
    if x == 0:
        raise ValueError("v2(0) is undefined")
    e = 0
    while x % 2 == 0:
        x //= 2
        e += 1
    return e


def shor_success_probability(factors: List[Tuple[int, int]]) -> float:
    """
    Compute the exact success probability of Shor's algorithm
    per trial, given the prime factorization of N.

    Args:
        factors: List of (p_i, e_i) tuples for N = ∏ p_i^{e_i}.
                 p_i must be odd primes.

    Returns:
        Exact probability that a randomly chosen a in (ℤ/Nℤ)^×
        yields a non-trivial factor via Shor's algorithm.
    """
    odd_primes = [(p, e) for p, e in factors if p > 2]

    if len(odd_primes) == 0:
        return 1.0  # power of 2, factoring is trivial

    if len(odd_primes) == 1:
        # Single prime power: Shor's standard reduction
        # does not apply directly.
        return 0.0

    k = len(odd_primes)
    s_values = [v2(p - 1) for p, _ in odd_primes]
    max_s = max(s_values)

    # P(odd r): all d_i are odd
    prob_odd = 1.0
    for s in s_values:
        prob_odd *= 1.0 / (1 << s)

    # P(symmetric): all v2(d_i) == t for some t >= 1
    prob_symmetric = 0.0
    for t in range(1, max_s + 1):
        prob_t = 1.0
        for s in s_values:
            if t < s:
                prob_t *= 2.0 ** (t - s - 1)
            elif t == s:
                prob_t *= 0.5
            else:
                prob_t = 0.0
                break
        prob_symmetric += prob_t

    return 1.0 - prob_odd - prob_symmetric


def trials_for_confidence(p_success: float, epsilon: float = 1e-3):
    """Number of independent trials needed for confidence >= 1 - epsilon."""
    if p_success >= 1.0:
        return 1
    return ceil(log(epsilon) / log(1 - p_success))


def format_factorization(factors):
    return " · ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in factors)


def main():
    if len(sys.argv) > 1:
        # Parse command-line factors: p1 e1 p2 e2 ...
        args = sys.argv[1:]
        if len(args) % 2 != 0:
            print("Error: factors must be in pairs (p e).", file=sys.stderr)
            sys.exit(1)
        factors = []
        for i in range(0, len(args), 2):
            p = int(args[i])
            e = int(args[i + 1])
            factors.append((p, e))
    else:
        # Default: RSA-2048 typical (demo with small primes)
        factors = [(3, 1), (7, 1)]

    N = 1
    for p, e in factors:
        N *= p ** e

    print(f"N = {format_factorization(factors)}")
    print(f"Number of odd prime factors: k = {sum(1 for p, _ in factors if p > 2)}")

    p_success = shor_success_probability(factors)
    p_failure = 1 - p_success

    print(f"\nP(success per trial) = {p_success:.10f}")
    print(f"P(failure per trial) = {p_failure:.10f}")
    print(f"Expected trials:       {1/p_success:.2f}")

    for eps_label, eps_val in [
        ("50%", 0.5), ("90%", 0.1), ("99%", 0.01), ("99.9%", 0.001)
    ]:
        m = trials_for_confidence(p_success, eps_val)
        print(f"Trials for {eps_label} confidence: {m}")


if __name__ == "__main__":
    main()
