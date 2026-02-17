"""
ks_sub31_all_pools.py -- Search for sub-31 KS sets across ALL algebraic constructions
=====================================================================================

Runs greedy minimization on each of the six known algebraic KS ray pools
to check whether any can produce a KS subset with fewer than 31 vectors.

Pools tested:
  1. Integer (CK-31): 49 rays from {0, ±1, ±2}
  2. Eisenstein: 57 rays from Z[omega]
  3. Peres: 49 rays from Z[sqrt(2)]
  4. Z[sqrt(-2)]: 49 rays
  5. Heegner-7: 145 rays from Z[(1+sqrt(-7))/2]
  6. Golden ratio: ~205 rays from Z[phi] with completion
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

import cmath
import math
import random
import time

from pysat.solvers import Glucose4

from ks_complex import (
    generate_eisenstein_rays,
    hermitian_dot,
    canonicalize_complex_ray,
)
from ks_new_islands import (
    generate_rays_from_alphabet,
    hermitian_completion,
    sat_minimize,
)
from ks_sat import CK31_VECTORS

random.seed(42)


def build_pairs_triads(rays, tol=1e-9):
    """Build orthogonal pairs and triads using Hermitian dot product."""
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
    """Test KS-uncolorability using BOTH triads and pairwise constraints."""
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
    """Greedy minimization: repeatedly try removing random rays."""
    best_size = n_rays
    best_subset = list(range(n_rays))

    for trial in range(n_trials):
        current = list(range(n_rays))
        random.shuffle(current)

        for candidate_remove in list(current):
            test = [r for r in current if r != candidate_remove]
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
            print(f"    Trial {trial+1}: new best = {best_size}")

        if (trial + 1) % 100 == 0:
            print(f"    ... {trial+1}/{n_trials} done, best = {best_size}")

    return best_size, best_subset


# =====================================================================
# Build all six pools
# =====================================================================

def build_all_pools():
    pools = {}

    # 1. Integer (full {0,±1,±2} pool, not just CK-31)
    print("  Building Integer pool...")
    int_alph = [complex(x) for x in [0, 1, -1, 2, -2]]
    int_rays = generate_rays_from_alphabet(int_alph)
    pools['Integer'] = int_rays

    # 2. Eisenstein
    print("  Building Eisenstein pool...")
    eis_rays = generate_eisenstein_rays(max_coeff=1, dim=3, norm_cutoff=3)
    pools['Eisenstein'] = eis_rays

    # 3. Peres (Z[sqrt(2)])
    print("  Building Peres pool...")
    s2 = math.sqrt(2)
    peres_alph = [complex(x) for x in [0, 1, -1, s2, -s2]]
    peres_rays = generate_rays_from_alphabet(peres_alph)
    pools['Peres'] = peres_rays

    # 4. Z[sqrt(-2)]
    print("  Building Z[sqrt(-2)] pool...")
    sd2 = cmath.sqrt(-2)
    zsqrt2_alph = [0, 1, -1, sd2, -sd2]
    zsqrt2_rays = generate_rays_from_alphabet(zsqrt2_alph)
    pools['Z[sqrt(-2)]'] = zsqrt2_rays

    # 5. Heegner-7
    print("  Building Heegner-7 pool...")
    gen7 = (1 + cmath.sqrt(-7)) / 2
    h7_alph = [0, 1, -1, gen7, -gen7, gen7.conjugate(), -gen7.conjugate()]
    h7_rays = generate_rays_from_alphabet(h7_alph)
    pools['Heegner-7'] = h7_rays

    # 6. Golden ratio (needs completion)
    print("  Building Golden ratio pool...")
    phi = (1 + math.sqrt(5)) / 2
    golden_alph = [complex(x) for x in [0, 1, -1, phi, -phi]]
    golden_raw = generate_rays_from_alphabet(golden_alph)
    golden_rays = hermitian_completion(golden_raw)
    pools['Golden ratio'] = golden_rays

    return pools


# =====================================================================
# Main
# =====================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("SUB-31 KS SEARCH ACROSS ALL ALGEBRAIC CONSTRUCTIONS")
    print("=" * 70)

    pools = build_all_pools()

    print(f"\n{'='*70}")
    print(f"{'Construction':<16} {'Pool':>5} {'Pairs':>6} {'Triads':>7} {'KS?':>5}")
    print(f"{'-'*70}")

    results = {}
    for name, rays in pools.items():
        pairs, triads = build_pairs_triads(rays)
        ks = is_ks_uncolorable(len(rays), triads, pairs)
        print(f"{name:<16} {len(rays):>5} {len(pairs):>6} {len(triads):>7} {'YES' if ks else 'no':>5}")
        results[name] = (rays, pairs, triads, ks)

    print(f"\n{'='*70}")
    print("GREEDY MINIMIZATION (500 trials each)")
    print("Goal: find any KS subset with < 31 vectors")
    print("=" * 70)

    for name, (rays, pairs, triads, ks) in results.items():
        if not ks:
            print(f"\n--- {name}: SKIPPED (not KS-uncolorable) ---")
            continue

        print(f"\n--- {name}: {len(rays)} rays, {len(triads)} triads ---")
        t0 = time.time()
        best_size, best_subset = greedy_minimize(
            len(rays), pairs, triads, n_trials=500, floor=20)
        elapsed = time.time() - t0

        if best_size < 31:
            print(f"  *** SUB-31 KS SET FOUND: {best_size} vectors! ***")
        else:
            print(f"  Minimum found: {best_size} vectors ({elapsed:.1f}s)")

    print(f"\n{'='*70}")
    print("SEARCH COMPLETE")
    print("=" * 70)
