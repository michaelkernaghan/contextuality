"""
ks_graph_analysis.py -- Graph isomorphism, spectral analysis, and exact minimization
=====================================================================================

1. Test whether Peres and Z[sqrt(-2)] orthogonality graphs are isomorphic
2. Compute spectral properties (eigenvalues, Hoffman bound) for all pools
3. Attempt exact minimization: can any 33-island be reduced to 32?
"""

import cmath
import math
import random
import time
import numpy as np
from itertools import permutations

from ks_complex import (
    generate_eisenstein_rays,
    hermitian_dot,
    canonicalize_complex_ray,
)

from ks_new_islands import (
    generate_rays_from_alphabet,
    sat_minimize,
)

from ks_sat import is_uncolorable as sat_uncolorable


def build_pairs_triads(rays, tol=1e-9):
    n = len(rays)
    pairs = []
    pair_set = set()
    for i in range(n):
        for j in range(i + 1, n):
            dot = hermitian_dot(rays[i], rays[j])
            if abs(dot) < tol:
                pairs.append((i, j))
                pair_set.add((i, j))
    triads = []
    for i in range(n):
        for j in range(i + 1, n):
            if (i, j) not in pair_set:
                continue
            for k in range(j + 1, n):
                if (i, k) in pair_set and (j, k) in pair_set:
                    triads.append((i, j, k))
    return pairs, triads


def adjacency_matrix(n, pairs):
    A = np.zeros((n, n))
    for i, j in pairs:
        A[i, j] = 1.0
        A[j, i] = 1.0
    return A


def degree_sequence(n, pairs):
    deg = [0] * n
    for a, b in pairs:
        deg[a] += 1
        deg[b] += 1
    return sorted(deg)


# ============================================================
# PART 1: Graph isomorphism test
# ============================================================

def graph_invariants(n, pairs):
    """Compute a battery of graph invariants for isomorphism testing."""
    A = adjacency_matrix(n, pairs)
    eigenvalues = sorted(np.linalg.eigvalsh(A))

    deg = degree_sequence(n, pairs)

    # Number of triangles
    A2 = A @ A
    A3 = A2 @ A
    triangles = int(round(np.trace(A3) / 6))

    # Number of edges
    edges = len(pairs)

    # Number of 4-cycles (from A^4 trace, corrected)
    A4 = A3 @ A
    # trace(A^4) = 2*edges + 4*triangles_with_pendant + 8*C4 + sum(deg^2)
    # Simpler: just use trace(A^4) as an invariant
    trace_a4 = np.trace(A4)

    return {
        'n': n,
        'edges': edges,
        'degree_seq': tuple(deg),
        'eigenvalues': tuple(np.round(eigenvalues, 8)),
        'triangles': triangles,
        'trace_a4': round(trace_a4),
    }


def refined_isomorphism_test(n1, pairs1, n2, pairs2):
    """
    Test graph isomorphism using vertex refinement (color refinement / WL-1).
    Returns True if the test cannot distinguish the graphs (likely isomorphic),
    False if they are definitely not isomorphic.
    """
    if n1 != n2:
        return False, "different vertex count"

    n = n1

    # Build adjacency
    adj1 = [set() for _ in range(n)]
    for a, b in pairs1:
        adj1[a].add(b)
        adj1[b].add(a)

    adj2 = [set() for _ in range(n)]
    for a, b in pairs2:
        adj2[a].add(b)
        adj2[b].add(a)

    # Initial coloring: degree
    color1 = [len(adj1[i]) for i in range(n)]
    color2 = [len(adj2[i]) for i in range(n)]

    for iteration in range(20):
        # Refine: color = (old_color, sorted tuple of neighbor colors)
        new_color1 = [(color1[i], tuple(sorted(color1[j] for j in adj1[i]))) for i in range(n)]
        new_color2 = [(color2[i], tuple(sorted(color2[j] for j in adj2[i]))) for i in range(n)]

        # Canonicalize colors to integers
        all_colors = sorted(set(new_color1 + new_color2))
        color_map = {c: idx for idx, c in enumerate(all_colors)}

        new_c1 = [color_map[c] for c in new_color1]
        new_c2 = [color_map[c] for c in new_color2]

        # Check if color class distributions match
        from collections import Counter
        dist1 = Counter(new_c1)
        dist2 = Counter(new_c2)

        if dist1 != dist2:
            return False, f"color refinement diverged at iteration {iteration}"

        # Check if stable
        if sorted(new_c1) == sorted(color1) and sorted(new_c2) == sorted(color2):
            break

        color1 = new_c1
        color2 = new_c2

    # If we get here, WL-1 cannot distinguish them
    n_colors = len(set(color1))
    return True, f"WL-1 indistinguishable ({n_colors} color classes after {iteration+1} iterations)"


# ============================================================
# PART 2: Spectral analysis
# ============================================================

def spectral_analysis(name, n, pairs):
    """Compute spectral properties of the orthogonality graph."""
    A = adjacency_matrix(n, pairs)
    eigenvalues = np.linalg.eigvalsh(A)
    eigenvalues = sorted(eigenvalues, reverse=True)

    lambda_max = eigenvalues[0]
    lambda_min = eigenvalues[-1]

    # Hoffman bound: alpha(G) <= n * (-lambda_min) / (lambda_max - lambda_min)
    if lambda_max - lambda_min > 0:
        hoffman = n * (-lambda_min) / (lambda_max - lambda_min)
    else:
        hoffman = n

    # Spectral gap
    if len(eigenvalues) > 1:
        spectral_gap = eigenvalues[0] - eigenvalues[1]
    else:
        spectral_gap = 0

    # Energy (sum of absolute eigenvalues)
    energy = sum(abs(e) for e in eigenvalues)

    print(f"\n  {name} (n={n}, edges={len(pairs)})")
    print(f"    lambda_max = {lambda_max:.4f}")
    print(f"    lambda_min = {lambda_min:.4f}")
    print(f"    Hoffman bound on alpha: {hoffman:.2f}")
    print(f"    Spectral gap: {spectral_gap:.4f}")
    print(f"    Energy: {energy:.2f}")
    print(f"    Top 5 eigenvalues: {', '.join(f'{e:.3f}' for e in eigenvalues[:5])}")
    print(f"    Bottom 5 eigenvalues: {', '.join(f'{e:.3f}' for e in eigenvalues[-5:])}")

    return lambda_max, lambda_min, hoffman, spectral_gap, energy


# ============================================================
# PART 3: Exact minimization for 33-islands
# ============================================================

def test_exact_minimization(name, rays, pairs, triads, known_min=33, n_trials=2000):
    """
    Attempt to find a (known_min - 1)-vector KS subset.

    Strategy:
    1. Find many distinct minimal sets via SAT
    2. For each, test all single-vector removals
    3. Report whether any (known_min - 1)-subset is uncolorable
    """
    print(f"\n  {name}: Testing if {known_min - 1} is achievable...")
    n = len(rays)

    # Collect distinct minimal sets
    distinct_sets = {}
    for trial in range(n_trials):
        current = list(range(n))
        random.shuffle(current)
        removed = True
        while removed:
            removed = False
            order = list(current)
            random.shuffle(order)
            for r in order:
                candidate = [x for x in current if x != r]
                if len(candidate) < 3:
                    break
                s = set(candidate)
                remap = {old: new for new, old in enumerate(sorted(candidate))}
                sp = [(remap[a], remap[b]) for a, b in pairs if a in s and b in s]
                st = [(remap[a], remap[b], remap[c]) for a, b, c in triads
                      if a in s and b in s and c in s]
                if st and sat_uncolorable(len(candidate), sp, st):
                    current = candidate
                    removed = True
                    break
        size = len(current)
        if size == known_min:
            fs = frozenset(current)
            distinct_sets[fs] = distinct_sets.get(fs, 0) + 1

    print(f"    Found {len(distinct_sets)} distinct {known_min}-sets from {n_trials} trials")

    # For each distinct set, try removing each vector
    tested = 0
    for ms in distinct_sets:
        sorted_ms = sorted(ms)
        for remove_idx in range(len(sorted_ms)):
            candidate = [v for i, v in enumerate(sorted_ms) if i != remove_idx]
            s = set(candidate)
            remap = {old: new for new, old in enumerate(sorted(candidate))}
            sp = [(remap[a], remap[b]) for a, b in pairs if a in s and b in s]
            st = [(remap[a], remap[b], remap[c]) for a, b, c in triads
                  if a in s and b in s and c in s]
            tested += 1
            if st and sat_uncolorable(len(candidate), sp, st):
                print(f"    FOUND {known_min - 1}-vector KS set! (removing vector {sorted_ms[remove_idx]})")
                return known_min - 1, candidate

    print(f"    Tested {tested} subsets of size {known_min - 1}: ALL colorable")
    print(f"    {known_min} appears to be optimal for this pool")
    return known_min, None


def main():
    random.seed(42)

    print("=" * 70)
    print("GRAPH ANALYSIS: Isomorphism, Spectra, Exact Minimization")
    print("=" * 70)

    # Build all pools
    # Integer
    int_alph = [complex(x) for x in [0, 1, -1, 2, -2]]
    int_rays = generate_rays_from_alphabet(int_alph)
    int_pairs, int_triads = build_pairs_triads(int_rays)

    # Peres
    s2 = math.sqrt(2)
    p_alph = [complex(x) for x in [0, 1, -1, s2, -s2]]
    p_rays = generate_rays_from_alphabet(p_alph)
    p_pairs, p_triads = build_pairs_triads(p_rays)

    # Eisenstein
    eis_rays = generate_eisenstein_rays(max_coeff=1, dim=3, norm_cutoff=3)
    eis_pairs, eis_triads = build_pairs_triads(eis_rays)

    # Z[sqrt(-2)]
    sd2 = cmath.sqrt(-2)
    cq_alph = [0, 1, -1, sd2, -sd2]
    cq_rays = generate_rays_from_alphabet(cq_alph)
    cq_pairs, cq_triads = build_pairs_triads(cq_rays)

    # Heegner-7
    gen7 = (1 + cmath.sqrt(-7)) / 2
    h7_alph = [0, 1, -1, gen7, -gen7, gen7.conjugate(), -gen7.conjugate()]
    h7_rays = generate_rays_from_alphabet(h7_alph)
    h7_pairs, h7_triads = build_pairs_triads(h7_rays)

    # ================================================================
    # PART 1: Graph Isomorphism -- Peres vs Z[sqrt(-2)]
    # ================================================================
    print("\n" + "=" * 70)
    print("PART 1: GRAPH ISOMORPHISM TEST")
    print("=" * 70)

    # First compare invariants
    print("\n--- Invariant comparison: Peres vs Z[sqrt(-2)] (full pools) ---")
    inv_p = graph_invariants(len(p_rays), p_pairs)
    inv_cq = graph_invariants(len(cq_rays), cq_pairs)

    for key in inv_p:
        match = inv_p[key] == inv_cq[key]
        if key == 'eigenvalues':
            # Compare with tolerance
            match = np.allclose(np.array(inv_p[key]), np.array(inv_cq[key]), atol=1e-6)
        sym = "==" if match else "!="
        if key in ('eigenvalues', 'degree_seq'):
            print(f"  {key}: {'MATCH' if match else 'DIFFER'}")
        else:
            print(f"  {key}: {inv_p[key]} {sym} {inv_cq[key]}")

    # WL-1 refinement test
    print("\n--- WL-1 color refinement test ---")
    iso_result, iso_msg = refined_isomorphism_test(len(p_rays), p_pairs, len(cq_rays), cq_pairs)
    print(f"  Result: {'LIKELY ISOMORPHIC' if iso_result else 'NOT ISOMORPHIC'}")
    print(f"  Detail: {iso_msg}")

    # Also test minimized sets
    print("\n--- Invariant comparison: Peres vs Z[sqrt(-2)] (minimized 33-sets) ---")
    # Get minimized sets
    p_sub, p_size, _ = sat_minimize(p_rays, p_pairs, p_triads, n_trials=300)
    p_s = set(p_sub)
    p_remap = {old: new for new, old in enumerate(sorted(p_sub))}
    p_min_pairs = [(p_remap[a], p_remap[b]) for a, b in p_pairs if a in p_s and b in p_s]

    cq_sub, cq_size, _ = sat_minimize(cq_rays, cq_pairs, cq_triads, n_trials=300)
    cq_s = set(cq_sub)
    cq_remap = {old: new for new, old in enumerate(sorted(cq_sub))}
    cq_min_pairs = [(cq_remap[a], cq_remap[b]) for a, b in cq_pairs if a in cq_s and b in cq_s]

    inv_pm = graph_invariants(p_size, p_min_pairs)
    inv_cqm = graph_invariants(cq_size, cq_min_pairs)

    for key in inv_pm:
        match = inv_pm[key] == inv_cqm[key]
        if key == 'eigenvalues':
            match = np.allclose(np.array(inv_pm[key]), np.array(inv_cqm[key]), atol=1e-6)
        sym = "==" if match else "!="
        if key in ('eigenvalues', 'degree_seq'):
            print(f"  {key}: {'MATCH' if match else 'DIFFER'}")
        else:
            print(f"  {key}: {inv_pm[key]} {sym} {inv_cqm[key]}")

    iso_result2, iso_msg2 = refined_isomorphism_test(p_size, p_min_pairs, cq_size, cq_min_pairs)
    print(f"  WL-1: {'LIKELY ISOMORPHIC' if iso_result2 else 'NOT ISOMORPHIC'} -- {iso_msg2}")

    # ================================================================
    # PART 2: Spectral Analysis
    # ================================================================
    print("\n" + "=" * 70)
    print("PART 2: SPECTRAL ANALYSIS OF ORTHOGONALITY GRAPHS")
    print("=" * 70)

    spectral_results = []

    pools = [
        ("Integer pool", len(int_rays), int_pairs, 17),
        ("Peres pool", len(p_rays), p_pairs, 23),
        ("Eisenstein pool", len(eis_rays), eis_pairs, 18),
        ("Z[sqrt(-2)] pool", len(cq_rays), cq_pairs, 23),
        ("Heegner-7 pool", len(h7_rays), h7_pairs, 44),
    ]

    print("\n--- Full pools ---")
    for name, n, pairs, alpha in pools:
        lmax, lmin, hoffman, gap, energy = spectral_analysis(name, n, pairs)
        spectral_results.append((name, n, alpha, hoffman, lmax, lmin, gap))
        print(f"    Actual alpha = {alpha}, Hoffman bound = {hoffman:.2f}, "
              f"ratio = {alpha/hoffman:.3f}")

    # Summary table
    print("\n\n  SPECTRAL SUMMARY (full pools)")
    print(f"  {'Pool':<20s} {'n':>4s} {'alpha':>6s} {'Hoffman':>8s} {'alpha/H':>8s} "
          f"{'lmax':>7s} {'lmin':>7s} {'gap':>7s}")
    print("  " + "-" * 68)
    for name, n, alpha, hoffman, lmax, lmin, gap in spectral_results:
        print(f"  {name:<20s} {n:4d} {alpha:6d} {hoffman:8.2f} {alpha/hoffman:8.3f} "
              f"{lmax:7.3f} {lmin:7.3f} {gap:7.3f}")

    # ================================================================
    # PART 3: Exact Minimization
    # ================================================================
    print("\n" + "=" * 70)
    print("PART 3: EXACT MINIMIZATION -- Can any 33-island reach 32?")
    print("=" * 70)

    test_exact_minimization("Peres", p_rays, p_pairs, p_triads, known_min=33, n_trials=2000)
    test_exact_minimization("Eisenstein", eis_rays, eis_pairs, eis_triads, known_min=33, n_trials=2000)
    test_exact_minimization("Z[sqrt(-2)]", cq_rays, cq_pairs, cq_triads, known_min=33, n_trials=2000)

    # Also test Heegner-7
    test_exact_minimization("Heegner-7", h7_rays, h7_pairs, h7_triads, known_min=43, n_trials=1000)


if __name__ == "__main__":
    main()
