"""
ks_cross_pool.py -- Search for sub-31 KS sets by mixing rays from different pools
==================================================================================

Strategy 2: Combine rays from different algebraic number fields.
Orthogonalities that don't exist within any single pool might emerge
when rays from different fields are combined.

Approach:
  1. Build all six pools
  2. For each pair of pools, combine and check for new orthogonalities
  3. For each combined pool that is KS-uncolorable, run greedy minimization
  4. Also try the union of ALL pools
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
from ks_sat import CK31_VECTORS

random.seed(42)


def build_pairs_triads(rays, tol=1e-9):
    """Build orthogonal pairs and triads."""
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
    return pairs, triads


def is_ks_uncolorable(n_vertices, triads, ortho_pairs):
    """Test KS-uncolorability."""
    if not triads and not ortho_pairs:
        return False
    solver = Glucose4()
    for a, b, c in triads:
        va, vb, vc = a + 1, b + 1, c + 1
        solver.add_clause([va, vb, vc])
        solver.add_clause([-va, -vb])
        solver.add_clause([-va, -vc])
        solver.add_clause([-vb, -vc])
    for i, j in ortho_pairs:
        vi, vj = i + 1, j + 1
        solver.add_clause([-vi, -vj])
    result = solver.solve()
    solver.delete()
    return not result


def greedy_minimize(n_rays, all_pairs, all_triads, n_trials=500, floor=20):
    """Greedy minimization with random orderings."""
    best_size = n_rays
    best_subset = list(range(n_rays))

    for trial in range(n_trials):
        current = list(range(n_rays))
        random.shuffle(current)

        for candidate in list(current):
            test = [r for r in current if r != candidate]
            if len(test) < floor:
                break
            test_set = set(test)
            remap = {old: new for new, old in enumerate(test)}
            sub_triads = [(remap[a], remap[b], remap[c])
                          for a, b, c in all_triads
                          if a in test_set and b in test_set and c in test_set]
            sub_pairs = [(remap[i], remap[j])
                         for i, j in all_pairs
                         if i in test_set and j in test_set]
            if is_ks_uncolorable(len(test), sub_triads, sub_pairs):
                current = test

        if len(current) < best_size:
            best_size = len(current)
            best_subset = current[:]
            print(f"      Trial {trial+1}: new best = {best_size}")

        if (trial + 1) % 100 == 0:
            print(f"      ... {trial+1}/{n_trials}, best = {best_size}")

    return best_size, best_subset


def merge_pools(pool_a, pool_b, tol=1e-9):
    """Merge two ray pools, deduplicating by canonical form."""
    merged = list(pool_a)
    existing = set()
    for r in pool_a:
        c = canonicalize_complex_ray(r)
        if c:
            existing.add(c)

    added = 0
    for r in pool_b:
        c = canonicalize_complex_ray(r)
        if c and c not in existing:
            existing.add(c)
            merged.append(r)
            added += 1

    return merged, added


def count_cross_pairs(pool_a, pool_b, merged_pairs, n_a):
    """Count orthogonal pairs that cross between the two pools."""
    cross = 0
    for i, j in merged_pairs:
        if (i < n_a and j >= n_a) or (i >= n_a and j < n_a):
            cross += 1
    return cross


def count_cross_triads(pool_a, pool_b, merged_triads, n_a):
    """Count triads that use rays from both pools."""
    cross = 0
    for a, b, c in merged_triads:
        sources = set()
        for r in (a, b, c):
            sources.add('A' if r < n_a else 'B')
        if len(sources) > 1:
            cross += 1
    return cross


# =====================================================================
# Build pools
# =====================================================================

def build_all_pools():
    pools = {}

    print("Building pools...")
    int_alph = [complex(x) for x in [0, 1, -1, 2, -2]]
    pools['Integer'] = generate_rays_from_alphabet(int_alph)

    eis_rays = generate_eisenstein_rays(max_coeff=1, dim=3, norm_cutoff=3)
    pools['Eisenstein'] = eis_rays

    s2 = math.sqrt(2)
    pools['Peres'] = generate_rays_from_alphabet([complex(x) for x in [0, 1, -1, s2, -s2]])

    sd2 = cmath.sqrt(-2)
    pools['Z[sqrt(-2)]'] = generate_rays_from_alphabet([0, 1, -1, sd2, -sd2])

    gen7 = (1 + cmath.sqrt(-7)) / 2
    pools['Heegner-7'] = generate_rays_from_alphabet(
        [0, 1, -1, gen7, -gen7, gen7.conjugate(), -gen7.conjugate()])

    phi = (1 + math.sqrt(5)) / 2
    golden_raw = generate_rays_from_alphabet([complex(x) for x in [0, 1, -1, phi, -phi]])
    pools['Golden'] = hermitian_completion(golden_raw)

    for name, rays in pools.items():
        print(f"  {name}: {len(rays)} rays")

    return pools


if __name__ == "__main__":
    print("=" * 70)
    print("STRATEGY 2: CROSS-POOL MIXING")
    print("Combine rays from different algebraic constructions")
    print("=" * 70)

    pools = build_all_pools()
    pool_names = list(pools.keys())

    # =====================================================================
    # Pairwise combinations
    # =====================================================================
    print(f"\n{'='*70}")
    print("PAIRWISE POOL COMBINATIONS")
    print(f"{'='*70}")

    interesting = []

    for i, name_a in enumerate(pool_names):
        for name_b in pool_names[i+1:]:
            pool_a = pools[name_a]
            pool_b = pools[name_b]
            n_a = len(pool_a)

            merged, added = merge_pools(pool_a, pool_b)
            pairs, triads = build_pairs_triads(merged)

            cross_p = count_cross_pairs(pool_a, pool_b, pairs, n_a)
            cross_t = count_cross_triads(pool_a, pool_b, triads, n_a)

            ks = is_ks_uncolorable(len(merged), triads, pairs)

            print(f"\n  {name_a} + {name_b}:")
            print(f"    Merged: {len(merged)} rays ({n_a} + {added} new)")
            print(f"    Pairs: {len(pairs)} ({cross_p} cross-pool)")
            print(f"    Triads: {len(triads)} ({cross_t} cross-pool)")
            print(f"    KS-uncolorable: {'YES' if ks else 'no'}")

            if ks and cross_t > 0:
                interesting.append((name_a, name_b, merged, pairs, triads, cross_t))

    # =====================================================================
    # Minimize interesting combinations
    # =====================================================================
    if interesting:
        print(f"\n{'='*70}")
        print(f"MINIMIZING {len(interesting)} INTERESTING COMBINATIONS")
        print(f"{'='*70}")

        for name_a, name_b, merged, pairs, triads, cross_t in interesting:
            print(f"\n  --- {name_a} + {name_b} ({len(merged)} rays, {cross_t} cross-triads) ---")
            t0 = time.time()
            best_size, best_subset = greedy_minimize(
                len(merged), pairs, triads, n_trials=500, floor=20)
            elapsed = time.time() - t0

            if best_size < 31:
                print(f"  *** SUB-31 KS SET FOUND: {best_size} vectors! ***")
            else:
                print(f"  Minimum: {best_size} vectors ({elapsed:.1f}s)")

            # Check which pools contributed to the minimum
            n_a = len(pools[name_a])
            from_a = sum(1 for r in best_subset if r < n_a)
            from_b = len(best_subset) - from_a
            print(f"  Composition: {from_a} from {name_a}, {from_b} from {name_b}")

    # =====================================================================
    # Union of ALL pools
    # =====================================================================
    print(f"\n{'='*70}")
    print("UNION OF ALL SIX POOLS")
    print(f"{'='*70}")

    all_merged = list(pools[pool_names[0]])
    existing = set()
    for r in all_merged:
        c = canonicalize_complex_ray(r)
        if c:
            existing.add(c)

    pool_boundaries = {pool_names[0]: (0, len(all_merged))}
    for name in pool_names[1:]:
        start = len(all_merged)
        for r in pools[name]:
            c = canonicalize_complex_ray(r)
            if c and c not in existing:
                existing.add(c)
                all_merged.append(r)
        pool_boundaries[name] = (start, len(all_merged))

    print(f"  Total unique rays: {len(all_merged)}")
    for name, (s, e) in pool_boundaries.items():
        print(f"    {name}: rays [{s}:{e}) ({e-s} unique)")

    pairs, triads = build_pairs_triads(all_merged)
    print(f"  Total pairs: {len(pairs)}, triads: {len(triads)}")

    ks = is_ks_uncolorable(len(all_merged), triads, pairs)
    print(f"  KS-uncolorable: {'YES' if ks else 'no'}")

    if ks:
        print(f"\n  Running greedy minimization (500 trials)...")
        t0 = time.time()
        best_size, best_subset = greedy_minimize(
            len(all_merged), pairs, triads, n_trials=500, floor=20)
        elapsed = time.time() - t0

        if best_size < 31:
            print(f"  *** SUB-31 KS SET FOUND: {best_size} vectors! ***")
        else:
            print(f"  Minimum: {best_size} vectors ({elapsed:.1f}s)")

        # Which pools contributed?
        composition = {}
        for name, (s, e) in pool_boundaries.items():
            count = sum(1 for r in best_subset if s <= r < e)
            if count > 0:
                composition[name] = count
        print(f"  Composition: {composition}")

    print(f"\n{'='*70}")
    print("CROSS-POOL SEARCH COMPLETE")
    print(f"{'='*70}")
