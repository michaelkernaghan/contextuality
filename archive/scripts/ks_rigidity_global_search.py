"""
ks_rigidity_global_search.py -- Search for distinct realizations of rigid islands
==================================================================================

For the four infinitesimally rigid islands (CK-31, Eisenstein-33, Heegner-7, Golden-52),
attempt to find distinct geometric realizations by:
1. Random perturbation + optimization back to constraint surface
2. If a valid realization is found at distance > threshold, check if unitarily equivalent

If no distinct realization is found across many trials, this strengthens the case
for global rigidity (though it doesn't prove it).
"""

import sys
sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

import cmath
import math
import random
import time
import numpy as np
from scipy.optimize import minimize as scipy_minimize

from ks_complex import hermitian_dot, generate_eisenstein_rays
from ks_new_islands import generate_rays_from_alphabet, hermitian_completion
from ks_rigidity import (
    build_pairs_triads, normalize_rays, is_ks_uncolorable,
    greedy_minimize, compute_rigidity,
)

random.seed(42)
np.random.seed(42)


def flat_from_rays(rays):
    n = len(rays)
    flat = np.zeros(6 * n)
    for i in range(n):
        for k in range(3):
            flat[6*i + 2*k] = rays[i][k].real
            flat[6*i + 2*k + 1] = rays[i][k].imag
    return flat


def rays_from_flat(flat, n):
    rays = []
    for i in range(n):
        v = tuple(complex(flat[6*i + 2*k], flat[6*i + 2*k + 1]) for k in range(3))
        rays.append(v)
    return rays


def constraint_vector(flat, n, ortho_pairs):
    rays = rays_from_flat(flat, n)
    m = len(ortho_pairs)
    c = np.zeros(n + 2 * m)
    for i in range(n):
        c[i] = sum(abs(rays[i][k])**2 for k in range(3)) - 1.0
    for idx, (i, j) in enumerate(ortho_pairs):
        dot = hermitian_dot(rays[i], rays[j])
        c[n + 2*idx] = dot.real
        c[n + 2*idx + 1] = dot.imag
    return c


def check_rigidity(rays, pairs):
    """Returns (null_dim, sym_dim, is_rigid)."""
    n = len(rays)
    null_dim, sym_dim, rigid, deform, rank, shape = compute_rigidity(
        "test", rays, pairs)
    return null_dim, sym_dim, rigid


def search_distinct_realization(rays, pairs, n_trials=20, perturbation_scale=0.3):
    """Search for a geometrically distinct realization via random perturbation + optimization."""
    n = len(rays)
    flat0 = flat_from_rays(rays)
    distinct_found = 0

    for trial in range(n_trials):
        x0 = flat0 + np.random.randn(len(flat0)) * perturbation_scale

        result = scipy_minimize(
            lambda x: np.sum(constraint_vector(x, n, pairs)**2),
            x0, method='L-BFGS-B',
            options={'maxiter': 5000, 'ftol': 1e-30, 'gtol': 1e-20})

        final_c = constraint_vector(result.x, n, pairs)
        max_violation = np.max(np.abs(final_c))
        dist = np.linalg.norm(result.x - flat0)

        if max_violation < 1e-8 and dist > 0.01:
            new_rays = normalize_rays(rays_from_flat(result.x, n))

            orig_dots = sorted([abs(hermitian_dot(rays[i], rays[j]))
                                for i in range(n) for j in range(i+1, n)
                                if abs(hermitian_dot(rays[i], rays[j])) > 1e-6])
            new_dots = sorted([abs(hermitian_dot(new_rays[i], new_rays[j]))
                               for i in range(n) for j in range(i+1, n)
                               if abs(hermitian_dot(new_rays[i], new_rays[j])) > 1e-6])

            if len(orig_dots) == len(new_dots):
                max_diff = max(abs(a - b) for a, b in zip(orig_dots, new_dots))
                if max_diff > 1e-4:
                    distinct_found += 1
                    print(f"    Trial {trial}: DISTINCT realization! dist={dist:.4f}, "
                          f"spectral_diff={max_diff:.4e}")
            else:
                new_pairs2, _, _ = build_pairs_triads(new_rays, tol=1e-6)
                if len(new_pairs2) != len(pairs):
                    distinct_found += 1
                    print(f"    Trial {trial}: DISTINCT (different graph)! "
                          f"{len(new_pairs2)} pairs vs {len(pairs)}")

    return distinct_found


# =================================================================
# Build the four rigid islands using the same code as ks_rigidity.py
# =================================================================

def build_island(name):
    """Build a minimized island and return (name, rays, pairs, triads).

    Uses the same construction as ks_rigidity.py with high trial counts
    to ensure we hit the correct OCUS-certified minimum.
    """
    if name == "CK-31":
        CK31 = [
            (0,0,1), (0,1,0), (0,1,1), (0,1,-1), (0,1,2), (0,2,-1),
            (1,0,0), (1,0,1), (1,0,-1), (1,0,2), (1,0,-2),
            (1,1,0), (1,1,1), (1,1,-1), (1,1,2), (1,-1,0),
            (1,-1,1), (1,-1,-1), (1,-1,-2), (1,2,0), (1,2,-1),
            (1,-2,0), (1,-2,1), (2,0,1), (2,0,-1), (2,1,0),
            (2,1,1), (2,1,-1), (2,-1,0), (2,-1,1), (2,-1,-1),
        ]
        rays = [tuple(complex(x) for x in v) for v in CK31]
        rays = normalize_rays(rays)
        pairs, triads, _ = build_pairs_triads(rays)
        return name, rays, pairs, triads

    elif name == "Eisenstein-33":
        eis_pool = generate_eisenstein_rays(max_coeff=1, dim=3, norm_cutoff=3)
        pool_pairs, pool_triads, _ = build_pairs_triads(eis_pool)
        min_idx, min_n = greedy_minimize(eis_pool, pool_pairs, pool_triads, n_trials=500)
        rays = normalize_rays([eis_pool[i] for i in min_idx])
        pairs, triads, _ = build_pairs_triads(rays)
        return name, rays, pairs, triads

    elif name == "Heegner-7":
        gen7 = (1 + cmath.sqrt(-7)) / 2
        h7_alph = [0, 1, -1, gen7, -gen7, gen7.conjugate(), -gen7.conjugate()]
        h7_pool = generate_rays_from_alphabet(h7_alph)
        h7_pool_pairs, h7_pool_triads, _ = build_pairs_triads(h7_pool)
        # Use 1000 trials to reliably hit the correct minimum of 43
        min_idx, min_n = greedy_minimize(h7_pool, h7_pool_pairs, h7_pool_triads,
                                          n_trials=1000)
        print(f"    Heegner-7 greedy minimum: {min_n}")
        rays = normalize_rays([h7_pool[i] for i in min_idx])
        pairs, triads, _ = build_pairs_triads(rays)
        return name, rays, pairs, triads

    elif name == "Golden-52":
        phi = (1 + math.sqrt(5)) / 2
        gold_alph = [complex(x) for x in [0, 1, -1, phi, -phi]]
        gold_pool_raw = generate_rays_from_alphabet(gold_alph)
        gold_pool = hermitian_completion(gold_pool_raw)
        gold_pool_pairs, gold_pool_triads, _ = build_pairs_triads(gold_pool)
        print(f"    Golden pool: {len(gold_pool)} rays, {len(gold_pool_triads)} triads")
        min_idx, min_n = greedy_minimize(gold_pool, gold_pool_pairs, gold_pool_triads,
                                          n_trials=500)
        print(f"    Golden greedy minimum: {min_n}")
        rays = normalize_rays([gold_pool[i] for i in min_idx])
        pairs, triads, _ = build_pairs_triads(rays)
        return name, rays, pairs, triads


if __name__ == "__main__":
    print("=" * 70)
    print("GLOBAL RIGIDITY SEARCH: Four infinitesimally rigid islands")
    print("=" * 70)
    print()

    results = {}

    for island_name in ["CK-31", "Eisenstein-33", "Heegner-7", "Golden-52"]:
        print(f"\n{'='*60}")
        print(f"  {island_name}")
        print(f"{'='*60}")

        t0 = time.time()
        name, rays, pairs, triads = build_island(island_name)
        n = len(rays)
        print(f"  Built: {n} rays, {len(pairs)} pairs, {len(triads)} triads")

        # Confirm infinitesimal rigidity
        null_dim, sym_dim, is_rigid = check_rigidity(rays, pairs)
        print(f"  Null space: {null_dim}, Symmetry: {sym_dim}, "
              f"Inf. rigid: {'YES' if is_rigid else 'NO (flex!)'}")

        if not is_rigid:
            print(f"  SKIPPING — not infinitesimally rigid")
            continue

        # Search for distinct realizations
        print(f"  Searching for distinct realizations (20 random trials)...")
        n_distinct = search_distinct_realization(rays, pairs, n_trials=20,
                                                  perturbation_scale=0.3)
        elapsed = time.time() - t0

        if n_distinct == 0:
            print(f"  --> No distinct realization found ({elapsed:.1f}s)")
            print(f"      Consistent with GLOBAL rigidity")
        else:
            print(f"  --> {n_distinct} distinct realizations found ({elapsed:.1f}s)")
            print(f"      NOT globally rigid!")

        results[island_name] = {
            "n": n, "pairs": len(pairs), "triads": len(triads),
            "inf_rigid": is_rigid, "distinct": n_distinct, "time": elapsed
        }

    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"{'Island':<20} {'n':>4} {'Pairs':>6} {'Triads':>6} "
          f"{'Inf.Rigid':>10} {'Distinct':>10} {'Global?':>10}")
    for name, r in results.items():
        global_str = "YES" if r["distinct"] == 0 and r["inf_rigid"] else "NO"
        print(f"{name:<20} {r['n']:>4} {r['pairs']:>6} {r['triads']:>6} "
              f"{'YES' if r['inf_rigid'] else 'NO':>10} "
              f"{r['distinct']:>10} {global_str:>10}")
