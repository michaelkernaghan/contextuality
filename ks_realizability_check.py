"""
ks_realizability_check.py -- Check geometric realizability of small abstract KS sets
====================================================================================

For each small abstract KS-uncolorable hypergraph found by ks_minimal_generator.py,
try to find an embedding as actual rays in R^3 (or C^3) with exact orthogonalities.

Method: numerical optimization. Variables are ray coordinates in R^3.
Constraints: orthogonality for each edge, normalization for each ray.
We minimize the total violation of orthogonality constraints.

If the minimum is 0 (or very close), the abstract set is realizable.
If not, it's a purely combinatorial object with no geometric embedding.
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
    result = solver.solve()
    solver.delete()
    return not result


def stitch_n_modules(module_triads, n_verts, n_copies, sharing_pairs_list):
    """Stitch n copies. sharing_pairs_list[i] = [(v_mod_i, v_mod_{i+1}), ...] for adjacent pairs."""
    parent = {}
    def find(x):
        while parent.get(x, x) != x:
            parent[x] = parent.get(parent[x], parent[x])
            x = parent[x]
        return x
    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py

    for i, pairs in enumerate(sharing_pairs_list):
        for v1, v2 in pairs:
            union(v1 + i * n_verts, v2 + (i + 1) * n_verts)

    all_triads_raw = []
    all_verts = set()
    for copy in range(n_copies):
        off = copy * n_verts
        for t in module_triads:
            shifted = tuple(v + off for v in t)
            all_triads_raw.append(shifted)
            all_verts.update(shifted)

    canonical = {}
    counter = 0
    for v in sorted(all_verts):
        r = find(v)
        if r not in canonical:
            canonical[r] = counter
            counter += 1

    final_triads = []
    for t in all_triads_raw:
        rt = tuple(canonical[find(v)] for v in t)
        if len(set(rt)) == 3:
            final_triads.append(rt)

    unique = list(set(tuple(sorted(t)) for t in final_triads))
    return counter, unique


def get_edges_from_triads(triads):
    """Extract all orthogonality edges implied by triads."""
    edges = set()
    for a, b, c in triads:
        edges.add((min(a,b), max(a,b)))
        edges.add((min(a,c), max(a,c)))
        edges.add((min(b,c), max(b,c)))
    return list(edges)


def check_realizability_R3(n_verts, triads, n_restarts=50):
    """Try to realize an abstract KS set in R^3.

    Each vertex is a unit ray in R^3 (3 coordinates).
    Triads must be mutually orthogonal triples.

    Returns (best_violation, best_rays) where violation ~ 0 means realizable.
    """
    edges = get_edges_from_triads(triads)
    n_edges = len(edges)

    def objective(x):
        """Total squared violation of orthogonality + normalization."""
        rays = x.reshape(n_verts, 3)
        cost = 0.0

        # Orthogonality: dot(ray_i, ray_j) = 0 for each edge
        for i, j in edges:
            dot = np.dot(rays[i], rays[j])
            cost += dot ** 2

        # Normalization: |ray_i| = 1
        for i in range(n_verts):
            norm_sq = np.dot(rays[i], rays[i])
            cost += (norm_sq - 1.0) ** 2

        return cost

    def jacobian(x):
        """Gradient of objective."""
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
    best_x = None

    for restart in range(n_restarts):
        x0 = np.random.randn(n_verts * 3)
        # Normalize initial rays
        for i in range(n_verts):
            norm = np.linalg.norm(x0[i*3:(i+1)*3])
            if norm > 0:
                x0[i*3:(i+1)*3] /= norm

        result = minimize(objective, x0, jac=jacobian, method='L-BFGS-B',
                         options={'maxiter': 5000, 'ftol': 1e-15, 'gtol': 1e-12})

        if result.fun < best_cost:
            best_cost = result.fun
            best_x = result.x

        if best_cost < 1e-20:
            break  # Perfect realization found

    best_rays = best_x.reshape(n_verts, 3) if best_x is not None else None
    return best_cost, best_rays


def check_realizability_C3(n_verts, triads, n_restarts=50):
    """Try to realize in C^3 (6 real params per ray: re + im for each coordinate)."""
    edges = get_edges_from_triads(triads)

    def objective(x):
        # x has 6 values per vertex: (re0, im0, re1, im1, re2, im2)
        cost = 0.0
        for i, j in edges:
            # Hermitian inner product: sum_k conj(ray_i[k]) * ray_j[k]
            dot_re = 0.0
            dot_im = 0.0
            for k in range(3):
                ri_re = x[i*6 + 2*k]
                ri_im = x[i*6 + 2*k + 1]
                rj_re = x[j*6 + 2*k]
                rj_im = x[j*6 + 2*k + 1]
                # conj(ri) * rj = (ri_re - i*ri_im)(rj_re + i*rj_im)
                dot_re += ri_re * rj_re + ri_im * rj_im
                dot_im += ri_re * rj_im - ri_im * rj_re
            cost += dot_re**2 + dot_im**2

        for i in range(n_verts):
            norm_sq = sum(x[i*6 + 2*k]**2 + x[i*6 + 2*k + 1]**2 for k in range(3))
            cost += (norm_sq - 1.0) ** 2

        return cost

    best_cost = float('inf')
    best_x = None

    for restart in range(n_restarts):
        x0 = np.random.randn(n_verts * 6)
        for i in range(n_verts):
            norm = np.sqrt(sum(x0[i*6+j]**2 for j in range(6)))
            if norm > 0:
                x0[i*6:(i+1)*6] /= norm

        result = minimize(objective, x0, method='L-BFGS-B',
                         options={'maxiter': 5000, 'ftol': 1e-15})

        if result.fun < best_cost:
            best_cost = result.fun
            best_x = result.x

        if best_cost < 1e-20:
            break

    return best_cost, best_x


def verify_ks_with_rays(n_verts, triads, rays):
    """Verify that the found rays actually satisfy orthogonality."""
    edges = get_edges_from_triads(triads)
    max_dot = 0
    for i, j in edges:
        dot = abs(np.dot(rays[i], rays[j]))
        max_dot = max(max_dot, dot)

    max_norm_err = 0
    for i in range(n_verts):
        err = abs(np.linalg.norm(rays[i]) - 1.0)
        max_norm_err = max(max_norm_err, err)

    return max_dot, max_norm_err


# =====================================================================
print("=" * 70)
print("GEOMETRIC REALIZABILITY CHECK")
print("=" * 70)

# Define the abstract KS sets to test
# From ks_minimal_generator.py results

test_cases = []

# 1. Fano plane (7v, 7t) -- self-uncolorable
fano_triads = [(0,1,2), (0,3,4), (0,5,6), (1,3,5), (1,4,6), (2,3,6), (2,4,5)]
test_cases.append(("Fano plane (7v, 7t)", 7, fano_triads))

# 2. Build some stitched small generators
# fan-4v-2t x 3 copies, share 3
# Module: triads (0,1,2) and (0,1,3)
mod_4v = [(0,1,2), (0,1,3)]
# Try many sharings to find one that gives 6v uncolorable
random.seed(42)
for trial in range(500):
    s1 = random.sample(range(4), 3)
    d1 = random.sample(range(4), 3)
    s2 = random.sample(range(4), 3)
    d2 = random.sample(range(4), 3)
    sharing = [list(zip(s1, d1)), list(zip(s2, d2))]
    nv, nt = stitch_n_modules(mod_4v, 4, 3, sharing)
    if nv == 6 and nt and is_ks_uncolorable(nv, nt):
        test_cases.append((f"4v-fan x3 (6v, {len(nt)}t)", nv, nt))
        break

# 5v-3t-chain x 2 copies, share 4
mod_5v = [(0,1,2), (1,2,3), (2,3,4)]
for trial in range(500):
    s = random.sample(range(5), 4)
    d = random.sample(range(5), 4)
    sharing = [list(zip(s, d))]
    nv, nt = stitch_n_modules(mod_5v, 5, 2, sharing)
    if nv == 6 and nt and is_ks_uncolorable(nv, nt):
        test_cases.append((f"5v-chain x2 (6v, {len(nt)}t)", nv, nt))
        break

# 6v-4t-dense x 2 copies, share 5
mod_6v = [(0,1,2), (0,3,4), (1,3,5), (2,4,5)]
for trial in range(500):
    s = random.sample(range(6), 5)
    d = random.sample(range(6), 5)
    sharing = [list(zip(s, d))]
    nv, nt = stitch_n_modules(mod_6v, 6, 2, sharing)
    if nv == 7 and nt and is_ks_uncolorable(nv, nt):
        test_cases.append((f"6v-dense x2 (7v, {len(nt)}t)", nv, nt))
        break

# Also build some intermediate sizes (15-25 range)
# 3 modules of 10-ray, share 5 -> 20v (from stitching search)
mod_10v = [(5,0,2), (6,1,3), (7,2,4), (8,3,0), (9,4,1)]
for trial in range(500):
    s1 = random.sample(range(10), 5)
    d1 = random.sample(range(10), 5)
    s2 = random.sample(range(10), 5)
    d2 = random.sample(range(10), 5)
    sharing = [list(zip(s1, d1)), list(zip(s2, d2))]
    nv, nt = stitch_n_modules(mod_10v, 10, 3, sharing)
    if 18 <= nv <= 25 and nt and is_ks_uncolorable(nv, nt):
        test_cases.append((f"10v-module x3 ({nv}v, {len(nt)}t)", nv, nt))
        break

print(f"\n  Testing {len(test_cases)} abstract KS sets for geometric realizability\n")

# =====================================================================
# Test each case
# =====================================================================

for name, n_verts, triads in test_cases:
    edges = get_edges_from_triads(triads)
    print(f"\n--- {name} ---")
    print(f"  Vertices: {n_verts}, Triads: {len(triads)}, Edges: {len(edges)}")
    print(f"  Triads: {triads}")

    # Verify it's actually uncolorable
    ks = is_ks_uncolorable(n_verts, triads)
    print(f"  KS-uncolorable: {ks}")
    if not ks:
        print(f"  SKIP: not uncolorable")
        continue

    # Check edge density
    max_edges = n_verts * (n_verts - 1) // 2
    print(f"  Edge density: {len(edges)}/{max_edges} = {len(edges)/max_edges:.2f}")

    # Check: is this even possible? In R^3, max orthogonal rays = 3.
    # Each vertex can be orthogonal to at most 2 others (they span the ortho-complement).
    # Actually in R^3, each ray has a 2D orthogonal complement, so it can be orthogonal
    # to infinitely many rays -- but an orthogonal BASIS is 3 rays.
    # The constraint is: each triad must be an orthonormal basis (3 mutually orthogonal rays).

    # Degree check: max degree in orthogonality graph
    deg = {}
    for i, j in edges:
        deg[i] = deg.get(i, 0) + 1
        deg[j] = deg.get(j, 0) + 1
    max_deg = max(deg.values()) if deg else 0
    print(f"  Max degree in orthogonality graph: {max_deg}")

    # In R^3, each ray's orthogonal complement is 2D, so it can be orthogonal
    # to rays spanning that plane. No fundamental degree limit from dimension alone.

    # Try R^3 realization
    print(f"  Trying R^3 realization (100 restarts)...")
    cost_r3, rays_r3 = check_realizability_R3(n_verts, triads, n_restarts=100)
    print(f"    Best violation (R^3): {cost_r3:.2e}")

    if cost_r3 < 1e-10:
        print(f"    REALIZABLE IN R^3!")
        max_dot, max_norm = verify_ks_with_rays(n_verts, triads, rays_r3)
        print(f"    Max |dot product|: {max_dot:.2e}, Max norm error: {max_norm:.2e}")
        print(f"    Rays:")
        for i in range(n_verts):
            print(f"      ray {i}: ({rays_r3[i,0]:.6f}, {rays_r3[i,1]:.6f}, {rays_r3[i,2]:.6f})")
    else:
        # Try C^3
        print(f"  Trying C^3 realization (100 restarts)...")
        cost_c3, _ = check_realizability_C3(n_verts, triads, n_restarts=100)
        print(f"    Best violation (C^3): {cost_c3:.2e}")

        if cost_c3 < 1e-10:
            print(f"    REALIZABLE IN C^3 (but not R^3)")
        else:
            print(f"    NOT REALIZABLE in R^3 or C^3")
            print(f"    This is a purely combinatorial KS obstruction")


# =====================================================================
# Additional: systematic scan of ALL 6-7 vertex uncolorable hypergraphs
# =====================================================================
print(f"\n{'='*70}")
print("SYSTEMATIC: All uncolorable hypergraphs on 6-9 vertices")
print(f"{'='*70}")

for n_v in [6, 7, 8, 9]:
    print(f"\n--- {n_v} vertices ---")
    all_possible_triads = list(combinations(range(n_v), 3))
    realizable_count = 0
    uncolorable_count = 0

    # For n_v=6: C(6,3)=20 possible triads, test subsets of size 3-10
    max_triads = min(12, len(all_possible_triads))
    min_triads = 3

    for n_t in range(min_triads, max_triads + 1):
        # Sample triad sets (exhaustive for small, sampled for large)
        n_combos = 1
        for i in range(n_t):
            n_combos = n_combos * (len(all_possible_triads) - i) // (i + 1)

        if n_combos <= 5000:
            triad_sets = list(combinations(all_possible_triads, n_t))
        else:
            # Random sample
            triad_sets = []
            for _ in range(2000):
                ts = tuple(sorted(random.sample(all_possible_triads, n_t)))
                triad_sets.append(ts)
            triad_sets = list(set(triad_sets))

        for ts in triad_sets:
            triads = list(ts)
            if is_ks_uncolorable(n_v, triads):
                uncolorable_count += 1

                # Quick realizability check (fewer restarts for speed)
                cost, rays = check_realizability_R3(n_v, triads, n_restarts=30)
                if cost < 1e-10:
                    realizable_count += 1
                    edges = get_edges_from_triads(triads)
                    print(f"  REALIZABLE: {n_v}v, {n_t}t, {len(edges)}e, cost={cost:.2e}")
                    print(f"    Triads: {triads}")

                    # Verify and show rays
                    max_dot, max_norm = verify_ks_with_rays(n_v, triads, rays)
                    print(f"    Max |dot|: {max_dot:.2e}")
                    for i in range(n_v):
                        print(f"    ray {i}: ({rays[i,0]:.4f}, {rays[i,1]:.4f}, {rays[i,2]:.4f})")
                else:
                    # Also try C^3 for the smallest cases
                    if n_v <= 7:
                        cost_c3, _ = check_realizability_C3(n_v, triads, n_restarts=20)
                        if cost_c3 < 1e-10:
                            realizable_count += 1
                            print(f"  REALIZABLE (C^3 only): {n_v}v, {n_t}t, cost={cost_c3:.2e}")
                            print(f"    Triads: {triads}")

    print(f"  Total uncolorable: {uncolorable_count}, realizable: {realizable_count}")


print(f"\n{'='*70}")
print("DONE")
print(f"{'='*70}")
