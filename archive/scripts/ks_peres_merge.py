"""
ks_peres_merge.py -- Peres-33 merge comparison with CK-31
==========================================================

Peer review question: Do all non-orthogonal pair merges preserve KS
for Peres-33, like they do for CK-31? If not, CK-31 is structurally
special — its merge resilience is unique among known minimum KS sets.

For CK-31: all 394 non-orthogonal pair merges preserve KS-uncolorability.
We test the same for:
  - Peres-33 (Z[sqrt(2)], 33 rays, 16 triads)
  - Eisenstein-33 (Z[omega], 33 rays, 14 triads)
  - Z[sqrt(-2)]-33 (33 rays, 16 triads — graph-isomorphic to Peres)

If Peres-33 has some merges that BREAK KS, this shows CK-31 has a
uniquely rigid constraint topology.
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

import cmath
import math
import random
import time
from itertools import combinations

from pysat.solvers import Glucose4

from ks_complex import (
    generate_eisenstein_rays,
    hermitian_dot,
    canonicalize_complex_ray,
)
from ks_new_islands import (
    generate_rays_from_alphabet,
    hermitian_completion,
)

random.seed(42)


def build_pairs_triads(rays, tol=1e-9):
    """Build orthogonal pairs and triads from ray list."""
    n = len(rays)
    pairs = []
    adj = {i: set() for i in range(n)}
    for i in range(n):
        for j in range(i + 1, n):
            dot = hermitian_dot(rays[i], rays[j])
            if abs(dot) < tol:
                pairs.append((i, j))
                adj[i].add(j)
                adj[j].add(i)
    triads = []
    for i in range(n):
        neighbors_i = sorted(adj[i])
        for idx_j, j in enumerate(neighbors_i):
            if j <= i:
                continue
            for k in neighbors_i[idx_j + 1:]:
                if k <= j:
                    continue
                if k in adj[j]:
                    triads.append((i, j, k))
    return pairs, triads, adj


def is_ks_uncolorable(n, triads, pairs):
    """Test KS-uncolorability via SAT."""
    if not triads:
        return False
    solver = Glucose4()
    for a, b, c in triads:
        va, vb, vc = a + 1, b + 1, c + 1
        solver.add_clause([va, vb, vc])
        solver.add_clause([-va, -vb])
        solver.add_clause([-va, -vc])
        solver.add_clause([-vb, -vc])
    for i, j in pairs:
        vi, vj = i + 1, j + 1
        solver.add_clause([-vi, -vj])
    result = solver.solve()
    solver.delete()
    return not result


def greedy_minimize(n_rays, pairs, triads, n_trials=500):
    """Greedy deletion with random orderings to find minimal KS subset."""
    best = list(range(n_rays))
    best_size = n_rays

    for trial in range(n_trials):
        current = list(range(n_rays))
        order = list(range(n_rays))
        random.shuffle(order)

        for candidate in order:
            if candidate not in current:
                continue
            test = [r for r in current if r != candidate]
            if len(test) < 20:
                break
            keep_set = set(test)
            remap = {old: new for new, old in enumerate(test)}
            sub_triads = [(remap[a], remap[b], remap[c])
                          for a, b, c in triads
                          if a in keep_set and b in keep_set and c in keep_set]
            sub_pairs = [(remap[i], remap[j])
                         for i, j in pairs
                         if i in keep_set and j in keep_set]
            if is_ks_uncolorable(len(test), sub_triads, sub_pairs):
                current = test

        if len(current) < best_size:
            best = current
            best_size = len(current)

    return best, best_size


def analyze_merges(name, rays, pairs, triads, adj, min_subset, min_n):
    """Analyze all non-orthogonal pair merges for a minimal KS set."""
    print(f"\n{'='*70}")
    print(f"MERGE ANALYSIS: {name} (min={min_n} rays)")
    print(f"{'='*70}")

    # Rebuild pairs/triads/adj for minimal set
    min_set = set(min_subset)
    remap = {old: new for new, old in enumerate(sorted(min_subset))}
    m_pairs = [(remap[a], remap[b]) for a, b in pairs
               if a in min_set and b in min_set]
    m_adj = {i: set() for i in range(min_n)}
    for i, j in m_pairs:
        m_adj[i].add(j)
        m_adj[j].add(i)
    m_triads = [(remap[a], remap[b], remap[c]) for a, b, c in triads
                if a in min_set and b in min_set and c in min_set]

    n_ortho = len(m_pairs)
    n_total = min_n * (min_n - 1) // 2
    n_non_ortho = n_total - n_ortho

    print(f"  Rays: {min_n}")
    print(f"  Orthogonal pairs: {n_ortho}")
    print(f"  Non-orthogonal pairs: {n_non_ortho}")
    print(f"  Triads: {len(m_triads)}")

    # Verify KS-uncolorable
    assert is_ks_uncolorable(min_n, m_triads, m_pairs), \
        f"{name} minimal set is NOT KS-uncolorable!"

    # Test all non-orthogonal pair merges
    n_ks = 0
    n_not_ks = 0
    broken_merges = []
    preserved_merges = []

    t0 = time.time()
    for v1 in range(min_n):
        for v2 in range(v1 + 1, min_n):
            if v2 in m_adj[v1]:
                continue  # Skip orthogonal pairs

            # Merge v2 into v1
            merge_remap = {}
            idx = 0
            for v in range(min_n):
                if v == v2:
                    merge_remap[v] = merge_remap[v1]
                else:
                    merge_remap[v] = idx
                    idx += 1

            new_n = min_n - 1
            new_pairs_set = set()
            for i, j in m_pairs:
                ni, nj = merge_remap[i], merge_remap[j]
                if ni != nj:
                    new_pairs_set.add((min(ni, nj), max(ni, nj)))
            new_pairs = list(new_pairs_set)

            new_adj = {i: set() for i in range(new_n)}
            for i, j in new_pairs:
                new_adj[i].add(j)
                new_adj[j].add(i)

            new_triads = []
            for i in range(new_n):
                ni_list = sorted(new_adj[i])
                for idx_j, j in enumerate(ni_list):
                    if j <= i:
                        continue
                    for k in ni_list[idx_j + 1:]:
                        if k <= j:
                            continue
                        if k in new_adj[j]:
                            new_triads.append((i, j, k))

            if not new_triads:
                n_not_ks += 1
                broken_merges.append((v1, v2, 0, len(new_pairs)))
                continue

            if is_ks_uncolorable(new_n, new_triads, new_pairs):
                n_ks += 1
                preserved_merges.append((v1, v2, len(new_triads),
                                         len(new_pairs)))
            else:
                n_not_ks += 1
                broken_merges.append((v1, v2, len(new_triads),
                                      len(new_pairs)))

    elapsed = time.time() - t0

    print(f"\n  Results ({elapsed:.1f}s):")
    print(f"    Non-orthogonal pairs tested: {n_ks + n_not_ks}")
    print(f"    KS preserved: {n_ks} ({100*n_ks/(n_ks+n_not_ks):.1f}%)")
    print(f"    KS broken: {n_not_ks} ({100*n_not_ks/(n_ks+n_not_ks):.1f}%)")

    if broken_merges:
        print(f"\n  Broken merges (first 10):")
        for v1, v2, nt, np_ in broken_merges[:10]:
            print(f"    Merge ({v1},{v2}): {nt} triads, {np_} pairs → colorable")

    if preserved_merges:
        triad_counts = [nt for _, _, nt, _ in preserved_merges]
        pair_counts = [np_ for _, _, _, np_ in preserved_merges]
        print(f"\n  Preserved merges: triads {min(triad_counts)}-"
              f"{max(triad_counts)}, pairs {min(pair_counts)}-"
              f"{max(pair_counts)}")

    return n_ks, n_not_ks, broken_merges, preserved_merges


# =====================================================================
# Build all islands and run merge analysis
# =====================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("MERGE RESILIENCE COMPARISON ACROSS ALL ISLANDS")
    print("=" * 70)
    print()
    print("Question: Is CK-31's 100% merge preservation unique,")
    print("or do other minimal KS sets also preserve KS under all merges?")

    t_start = time.time()
    results = {}

    # ---- CK-31 (Integer) ----
    print(f"\n{'='*70}")
    print("BUILDING: CK-31 (Integer, {0,±1,±2})")
    print(f"{'='*70}")

    from math import gcd
    int_rays = []
    seen = set()
    for a in range(-2, 3):
        for b in range(-2, 3):
            for c in range(-2, 3):
                if a == 0 and b == 0 and c == 0:
                    continue
                g = gcd(gcd(abs(a), abs(b)), abs(c))
                v = (a // g, b // g, c // g)
                for coord in v:
                    if coord != 0:
                        if coord < 0:
                            v = (-v[0], -v[1], -v[2])
                        break
                if v not in seen:
                    seen.add(v)
                    int_rays.append(v)

    # Convert to complex for hermitian_dot compatibility
    int_rays_c = [tuple(complex(x) for x in r) for r in int_rays]
    int_pairs, int_triads, int_adj = build_pairs_triads(int_rays_c)
    print(f"  Pool: {len(int_rays)} rays, {len(int_pairs)} pairs, "
          f"{len(int_triads)} triads")

    # CK-31 is the known minimum
    CK31_INT = [
        (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 1, -1), (0, 1, 2), (0, 2, -1),
        (1, 0, 0), (1, 0, 1), (1, 0, -1), (1, 0, 2), (1, 0, -2),
        (1, 1, 0), (1, 1, 1), (1, 1, -1), (1, 1, 2), (1, -1, 0),
        (1, -1, 1), (1, -1, -1), (1, -1, -2), (1, 2, 0), (1, 2, -1),
        (1, -2, 0), (1, -2, 1), (2, 0, 1), (2, 0, -1), (2, 1, 0),
        (2, 1, 1), (2, 1, -1), (2, -1, 0), (2, -1, 1), (2, -1, -1),
    ]
    # Map CK31 to indices in int_rays
    ck31_indices = []
    for v in CK31_INT:
        idx = int_rays.index(v)
        ck31_indices.append(idx)

    ck31_ks, ck31_not, ck31_broken, ck31_preserved = analyze_merges(
        "CK-31 (Integer)", int_rays_c, int_pairs, int_triads, int_adj,
        sorted(ck31_indices), 31)

    # ---- Peres (Z[sqrt(2)]) ----
    print(f"\n{'='*70}")
    print("BUILDING: Peres (Z[sqrt(2)])")
    print(f"{'='*70}")

    s2 = math.sqrt(2)
    peres_alph = [complex(x) for x in [0, 1, -1, s2, -s2]]
    peres_rays = generate_rays_from_alphabet(peres_alph)
    peres_pairs, peres_triads, peres_adj = build_pairs_triads(peres_rays)
    print(f"  Pool: {len(peres_rays)} rays, {len(peres_pairs)} pairs, "
          f"{len(peres_triads)} triads")

    peres_min, peres_min_n = greedy_minimize(
        len(peres_rays), peres_pairs, peres_triads, n_trials=500)
    print(f"  Minimum found: {peres_min_n}")

    peres_ks, peres_not, peres_broken, peres_preserved = analyze_merges(
        "Peres-33", peres_rays, peres_pairs, peres_triads, peres_adj,
        peres_min, peres_min_n)

    # ---- Eisenstein (Z[omega]) ----
    print(f"\n{'='*70}")
    print("BUILDING: Eisenstein (Z[omega])")
    print(f"{'='*70}")

    eis_rays = generate_eisenstein_rays(max_coeff=1, dim=3, norm_cutoff=3)
    eis_pairs, eis_triads, eis_adj = build_pairs_triads(eis_rays)
    print(f"  Pool: {len(eis_rays)} rays, {len(eis_pairs)} pairs, "
          f"{len(eis_triads)} triads")

    eis_min, eis_min_n = greedy_minimize(
        len(eis_rays), eis_pairs, eis_triads, n_trials=500)
    print(f"  Minimum found: {eis_min_n}")

    eis_ks, eis_not, eis_broken, eis_preserved = analyze_merges(
        "Eisenstein-33", eis_rays, eis_pairs, eis_triads, eis_adj,
        eis_min, eis_min_n)

    # ---- Z[sqrt(-2)] ----
    print(f"\n{'='*70}")
    print("BUILDING: Z[sqrt(-2)]")
    print(f"{'='*70}")

    sd2 = cmath.sqrt(-2)
    zsqrt2_alph = [0, 1, -1, sd2, -sd2]
    zsqrt2_rays = generate_rays_from_alphabet(zsqrt2_alph)
    zsqrt2_pairs, zsqrt2_triads, zsqrt2_adj = build_pairs_triads(zsqrt2_rays)
    print(f"  Pool: {len(zsqrt2_rays)} rays, {len(zsqrt2_pairs)} pairs, "
          f"{len(zsqrt2_triads)} triads")

    zsqrt2_min, zsqrt2_min_n = greedy_minimize(
        len(zsqrt2_rays), zsqrt2_pairs, zsqrt2_triads, n_trials=500)
    print(f"  Minimum found: {zsqrt2_min_n}")

    zsqrt2_ks, zsqrt2_not, zsqrt2_broken, zsqrt2_preserved = analyze_merges(
        "Z[sqrt(-2)]-33", zsqrt2_rays, zsqrt2_pairs, zsqrt2_triads,
        zsqrt2_adj, zsqrt2_min, zsqrt2_min_n)

    # ---- Heegner-7 ----
    print(f"\n{'='*70}")
    print("BUILDING: Heegner-7 (Z[(1+sqrt(-7))/2])")
    print(f"{'='*70}")

    gen7 = (1 + cmath.sqrt(-7)) / 2
    h7_alph = [0, 1, -1, gen7, -gen7, gen7.conjugate(), -gen7.conjugate()]
    h7_rays = generate_rays_from_alphabet(h7_alph)
    h7_pairs, h7_triads, h7_adj = build_pairs_triads(h7_rays)
    print(f"  Pool: {len(h7_rays)} rays, {len(h7_pairs)} pairs, "
          f"{len(h7_triads)} triads")

    h7_min, h7_min_n = greedy_minimize(
        len(h7_rays), h7_pairs, h7_triads, n_trials=500)
    print(f"  Minimum found: {h7_min_n}")

    h7_ks, h7_not, h7_broken, h7_preserved = analyze_merges(
        "Heegner-7", h7_rays, h7_pairs, h7_triads, h7_adj,
        h7_min, h7_min_n)

    # ---- Golden (Z[phi] + completion) ----
    print(f"\n{'='*70}")
    print("BUILDING: Golden (Z[phi] + cross-product completion)")
    print(f"{'='*70}")

    phi = (1 + math.sqrt(5)) / 2
    gold_alph = [complex(x) for x in [0, 1, -1, phi, -phi]]
    gold_rays_raw = generate_rays_from_alphabet(gold_alph)
    gold_rays = hermitian_completion(gold_rays_raw)
    gold_pairs, gold_triads, gold_adj = build_pairs_triads(gold_rays)
    print(f"  Pool: {len(gold_rays)} rays, {len(gold_pairs)} pairs, "
          f"{len(gold_triads)} triads")

    gold_min, gold_min_n = greedy_minimize(
        len(gold_rays), gold_pairs, gold_triads, n_trials=200)
    print(f"  Minimum found: {gold_min_n}")

    gold_ks, gold_not, gold_broken, gold_preserved = analyze_merges(
        "Golden", gold_rays, gold_pairs, gold_triads, gold_adj,
        gold_min, gold_min_n)

    # ---- Summary ----
    t_total = time.time() - t_start

    print(f"\n{'='*70}")
    print("SUMMARY: MERGE RESILIENCE COMPARISON")
    print(f"{'='*70}")
    print(f"{'Island':<20} {'Min':>4} {'Non-orth':>10} {'Preserved':>10} "
          f"{'Broken':>8} {'Rate':>8}")
    print("-" * 62)

    all_results = [
        ("CK-31", 31, ck31_ks, ck31_not),
        ("Peres-33", 33, peres_ks, peres_not),
        ("Eisenstein-33", 33, eis_ks, eis_not),
        ("Z[sqrt(-2)]-33", 33, zsqrt2_ks, zsqrt2_not),
        ("Heegner-7", h7_min_n, h7_ks, h7_not),
        ("Golden", gold_min_n, gold_ks, gold_not),
    ]

    all_preserved = True
    for name, min_n, n_ks, n_not in all_results:
        total = n_ks + n_not
        rate = 100 * n_ks / total if total > 0 else 0
        print(f"{name:<20} {min_n:>4} {total:>10} {n_ks:>10} "
              f"{n_not:>8} {rate:>7.1f}%")
        if n_not > 0:
            all_preserved = False

    print(f"\nTotal time: {t_total:.1f}s")

    if all_preserved:
        print(f"\n*** ALL six islands show 100% merge preservation ***")
        print(f"    Merge resilience is a UNIVERSAL property of minimal KS")
        print(f"    sets across all known algebraic islands in dimension 3.")
        print(f"    Conjecture: Every minimal KS set in R^3/C^3 is")
        print(f"    merge-saturated (no vertex identification reduces size).")
    elif ck31_not == 0 and any(r[3] > 0 for r in all_results[1:]):
        print(f"\n*** CK-31 uniquely preserves KS under all merges ***")
    else:
        print(f"\n    Mixed results — see individual analyses above.")
