"""
ks_realizability_scan.py -- Systematic realizability scan for 6-9 vertex hypergraphs
====================================================================================

Optimized version: R^3 only, fewer restarts, faster convergence checks.
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

import numpy as np
import random
from itertools import combinations
from pysat.solvers import Glucose4
from scipy.optimize import minimize

random.seed(42)
np.random.seed(42)


def is_ks_uncolorable(n_vertices, triads):
    if not triads:
        return False
    solver = Glucose4()
    for a, b, c in triads:
        va, vb, vc = a + 1, b + 1, c + 1
        solver.add_clause([va, vb, vc])
        solver.add_clause([-va, -vb])
        solver.add_clause([-va, -vc])
        solver.add_clause([-vb, -vc])
    result = solver.solve()
    solver.delete()
    return not result


def get_edges_from_triads(triads):
    edges = set()
    for a, b, c in triads:
        edges.add((min(a,b), max(a,b)))
        edges.add((min(a,c), max(a,c)))
        edges.add((min(b,c), max(b,c)))
    return list(edges)


def check_realizability_R3(n_verts, triads, n_restarts=20):
    edges = get_edges_from_triads(triads)

    def objective(x):
        rays = x.reshape(n_verts, 3)
        cost = 0.0
        for i, j in edges:
            dot = np.dot(rays[i], rays[j])
            cost += dot ** 2
        for i in range(n_verts):
            norm_sq = np.dot(rays[i], rays[i])
            cost += (norm_sq - 1.0) ** 2
        return cost

    def jacobian(x):
        rays = x.reshape(n_verts, 3)
        grad = np.zeros_like(rays)
        for i, j in edges:
            dot = np.dot(rays[i], rays[j])
            grad[i] += 2 * dot * rays[j]
            grad[j] += 2 * dot * rays[i]
        for i in range(n_verts):
            norm_sq = np.dot(rays[i], rays[i])
            grad[i] += 4 * (norm_sq - 1.0) * rays[i]
        return grad.flatten()

    best_cost = float('inf')

    for restart in range(n_restarts):
        x0 = np.random.randn(n_verts * 3)
        for i in range(n_verts):
            norm = np.linalg.norm(x0[i*3:(i+1)*3])
            if norm > 0:
                x0[i*3:(i+1)*3] /= norm

        result = minimize(objective, x0, jac=jacobian, method='L-BFGS-B',
                         options={'maxiter': 3000, 'ftol': 1e-15, 'gtol': 1e-12})

        if result.fun < best_cost:
            best_cost = result.fun

        # Early exit if clearly unrealizable
        if restart >= 5 and best_cost > 0.1:
            break
        if best_cost < 1e-20:
            break

    return best_cost


# =====================================================================
print("=" * 70)
print("SYSTEMATIC REALIZABILITY SCAN: 6-9 vertex hypergraphs")
print("=" * 70)

for n_v in [6, 7, 8, 9]:
    print(f"\n{'='*70}")
    print(f"--- {n_v} vertices ---")
    print(f"{'='*70}")

    all_possible_triads = list(combinations(range(n_v), 3))
    n_possible = len(all_possible_triads)
    print(f"  Possible triads: {n_possible}")

    realizable_count = 0
    uncolorable_count = 0
    tested_count = 0

    max_triads = min(n_possible, 15)
    min_triads = 3

    for n_t in range(min_triads, max_triads + 1):
        # Count combinations
        from math import comb
        n_combos = comb(n_possible, n_t)

        if n_combos <= 3000:
            triad_sets = list(combinations(all_possible_triads, n_t))
            sampled = False
        else:
            # Random sample
            seen = set()
            triad_sets = []
            for _ in range(2000):
                ts = tuple(sorted(random.sample(all_possible_triads, n_t)))
                if ts not in seen:
                    seen.add(ts)
                    triad_sets.append(ts)
            sampled = True

        ks_found = 0
        real_found = 0

        for ts in triad_sets:
            triads = list(ts)
            tested_count += 1

            if is_ks_uncolorable(n_v, triads):
                ks_found += 1
                uncolorable_count += 1

                cost = check_realizability_R3(n_v, triads, n_restarts=20)
                if cost < 1e-10:
                    realizable_count += 1
                    real_found += 1
                    edges = get_edges_from_triads(triads)
                    print(f"  *** REALIZABLE: {n_v}v, {n_t}t, {len(edges)}e, cost={cost:.2e}")
                    print(f"      Triads: {triads}")

        sampling_note = f" (sampled {len(triad_sets)}/{n_combos})" if sampled else f" (exhaustive, {n_combos})"
        if ks_found > 0:
            print(f"  {n_t} triads: {ks_found} uncolorable, {real_found} realizable{sampling_note}")
        else:
            print(f"  {n_t} triads: 0 uncolorable{sampling_note}")

    print(f"\n  TOTALS for {n_v} vertices:")
    print(f"    Tested: {tested_count}")
    print(f"    Uncolorable: {uncolorable_count}")
    print(f"    Realizable: {realizable_count}")

print(f"\n{'='*70}")
print("SCAN COMPLETE")
print(f"{'='*70}")
