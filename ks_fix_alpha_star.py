"""
ks_fix_alpha_star.py -- Fix fractional packing number computation
=================================================================

The original alpha* computation used only edge constraints:
    x_i + x_j <= 1 for each edge

The correct CSW fractional packing number uses CLIQUE constraints:
    sum(x_i for i in C) <= 1 for each maximal clique C

In 3D, max clique size is 3 (triads = orthogonal triples), so:
    x_i + x_j + x_k <= 1 for each triad
    x_i + x_j <= 1 for edges NOT in any triad

This script recomputes alpha* for all islands (minimized and full pools)
and compares old (wrong) vs new (correct) values.
"""

import cmath
import math
import random
import time
import numpy as np
from scipy.optimize import linprog

from ks_complex import (
    generate_eisenstein_rays,
    hermitian_dot,
)

from ks_new_islands import (
    generate_rays_from_alphabet,
    sat_minimize,
)

from ks_sat import (
    is_uncolorable as sat_uncolorable,
    CK31_VECTORS,
    build_graph,
)

from ks_csw_extended import (
    build_pairs_triads,
    max_independent_set,
    lovasz_theta,
)


def fractional_packing_edge_only(n, edges):
    """OLD (incorrect) implementation -- edge constraints only."""
    c = -np.ones(n)
    A_ub = np.zeros((len(edges), n))
    b_ub = np.ones(len(edges))
    for idx, (i, j) in enumerate(edges):
        A_ub[idx, i] = 1.0
        A_ub[idx, j] = 1.0
    bounds = [(0, 1)] * n
    result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
    return -result.fun if result.success else None


def fractional_packing_clique(n, pairs, triads):
    """
    CORRECT implementation -- clique constraints.

    In 3D orthogonality graphs, max clique size = 3 (triads).
    Constraints:
      - x_i + x_j + x_k <= 1 for each triad (3-clique)
      - x_i + x_j <= 1 for each edge NOT contained in any triad (2-clique)
    """
    # Find edges that are covered by at least one triad
    triad_edges = set()
    for a, b, c in triads:
        triad_edges.add((min(a, b), max(a, b)))
        triad_edges.add((min(a, c), max(a, c)))
        triad_edges.add((min(b, c), max(b, c)))

    # Standalone edges (not in any triad)
    standalone_edges = [(a, b) for a, b in pairs
                        if (min(a, b), max(a, b)) not in triad_edges]

    n_constraints = len(triads) + len(standalone_edges)
    c = -np.ones(n)
    A_ub = np.zeros((n_constraints, n))
    b_ub = np.ones(n_constraints)

    # Triad constraints
    for idx, (a, b, c_) in enumerate(triads):
        A_ub[idx, a] = 1.0
        A_ub[idx, b] = 1.0
        A_ub[idx, c_] = 1.0

    # Standalone edge constraints
    offset = len(triads)
    for idx, (a, b) in enumerate(standalone_edges):
        A_ub[offset + idx, a] = 1.0
        A_ub[offset + idx, b] = 1.0

    bounds = [(0, 1)] * n
    result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
    return -result.fun if result.success else None


def get_minimal_ks(rays, pairs, triads):
    subset, size, _ = sat_minimize(rays, pairs, triads, n_trials=300)
    s = set(subset)
    remap = {old: new for new, old in enumerate(sorted(subset))}
    min_rays = [rays[i] for i in sorted(subset)]
    min_pairs = [(remap[a], remap[b]) for a, b in pairs if a in s and b in s]
    min_triads = [(remap[a], remap[b], remap[c]) for a, b, c in triads
                  if a in s and b in s and c in s]
    return min_rays, min_pairs, min_triads, size


def compute_all(name, n, pairs, triads):
    """Compute alpha, theta, old alpha*, new alpha* for one configuration."""
    t0 = time.time()
    alpha = max_independent_set(n, pairs)
    theta = lovasz_theta(n, pairs)
    old_astar = fractional_packing_edge_only(n, pairs)
    new_astar = fractional_packing_clique(n, pairs, triads)
    dt = time.time() - t0

    # Standalone edges count
    triad_edges = set()
    for a, b, c in triads:
        triad_edges.add((min(a, b), max(a, b)))
        triad_edges.add((min(a, c), max(a, c)))
        triad_edges.add((min(b, c), max(b, c)))
    standalone = sum(1 for a, b in pairs if (min(a, b), max(a, b)) not in triad_edges)

    qc_old = theta / alpha if (theta and alpha > 0) else 0
    qc_new = theta / alpha if (theta and alpha > 0) else 0

    print(f"  {name:<35s} n={n:3d}  bases={len(triads):3d}  "
          f"standalone_edges={standalone:3d}")
    print(f"    alpha={alpha:3d}  theta={theta:7.2f}  "
          f"old_a*={old_astar:7.2f}  new_a*={new_astar:7.2f}  "
          f"Q/C={qc_new:.4f}  ({dt:.1f}s)")

    if abs(old_astar - new_astar) > 0.01:
        print(f"    *** CHANGED: a* went from {old_astar:.2f} to {new_astar:.2f} "
              f"(delta = {new_astar - old_astar:+.2f}) ***")
    else:
        print(f"    (no change)")

    return {
        'name': name, 'n': n, 'bases': len(triads),
        'alpha': alpha, 'theta': theta,
        'old_astar': old_astar, 'new_astar': new_astar,
        'standalone': standalone,
    }


def main():
    random.seed(42)

    print("=" * 70)
    print("ALPHA* FIX: Edge-only LP vs Clique LP")
    print("=" * 70)
    print("\nThe CSW fractional packing number alpha*(G) should use clique")
    print("constraints, not just edge constraints. In 3D, cliques = triads.")
    print("This recomputes all values.\n")

    all_results = []

    # Build all pools
    # Integer (CK-31)
    int_pairs, int_triads = build_graph(CK31_VECTORS)
    int_rays = [tuple(complex(x) for x in v) for v in CK31_VECTORS]
    r = compute_all("Integer (CK-31)", len(CK31_VECTORS), int_pairs, int_triads)
    all_results.append(r)

    # Peres pool
    s2 = math.sqrt(2)
    p_alph = [complex(x) for x in [0, 1, -1, s2, -s2]]
    p_rays = generate_rays_from_alphabet(p_alph)
    p_pairs, p_triads = build_pairs_triads(p_rays)
    r = compute_all("Peres pool", len(p_rays), p_pairs, p_triads)
    all_results.append(r)

    # Peres minimized
    p_min_rays, p_min_pairs, p_min_triads, p_size = get_minimal_ks(p_rays, p_pairs, p_triads)
    r = compute_all(f"Peres min-{p_size}", p_size, p_min_pairs, p_min_triads)
    all_results.append(r)

    # Eisenstein pool
    eis_rays = generate_eisenstein_rays(max_coeff=1, dim=3, norm_cutoff=3)
    eis_pairs, eis_triads = build_pairs_triads(eis_rays)
    r = compute_all("Eisenstein pool", len(eis_rays), eis_pairs, eis_triads)
    all_results.append(r)

    # Eisenstein minimized
    e_min_rays, e_min_pairs, e_min_triads, e_size = get_minimal_ks(eis_rays, eis_pairs, eis_triads)
    r = compute_all(f"Eisenstein min-{e_size}", e_size, e_min_pairs, e_min_triads)
    all_results.append(r)

    # Z[sqrt(-2)] pool
    sd2 = cmath.sqrt(-2)
    cq_alph = [0, 1, -1, sd2, -sd2]
    cq_rays = generate_rays_from_alphabet(cq_alph)
    cq_pairs, cq_triads = build_pairs_triads(cq_rays)
    r = compute_all("Z[sqrt(-2)] pool", len(cq_rays), cq_pairs, cq_triads)
    all_results.append(r)

    # Z[sqrt(-2)] minimized
    cq_min_rays, cq_min_pairs, cq_min_triads, cq_size = get_minimal_ks(cq_rays, cq_pairs, cq_triads)
    r = compute_all(f"Z[sqrt(-2)] min-{cq_size}", cq_size, cq_min_pairs, cq_min_triads)
    all_results.append(r)

    # Heegner-7 pool
    gen7 = (1 + cmath.sqrt(-7)) / 2
    h7_alph = [0, 1, -1, gen7, -gen7, gen7.conjugate(), -gen7.conjugate()]
    h7_rays = generate_rays_from_alphabet(h7_alph)
    h7_pairs, h7_triads = build_pairs_triads(h7_rays)
    r = compute_all("Heegner-7 pool", len(h7_rays), h7_pairs, h7_triads)
    all_results.append(r)

    # Heegner-7 minimized
    h7_min_rays, h7_min_pairs, h7_min_triads, h7_size = get_minimal_ks(h7_rays, h7_pairs, h7_triads)
    r = compute_all(f"Heegner-7 min-{h7_size}", h7_size, h7_min_pairs, h7_min_triads)
    all_results.append(r)

    # Summary comparison table
    print("\n\n" + "=" * 70)
    print("COMPARISON: OLD (edge-only) vs NEW (clique) alpha*")
    print("=" * 70)
    print(f"\n{'Set':<28s} {'n':>4s} {'alpha':>6s} {'theta':>7s} "
          f"{'old a*':>7s} {'new a*':>7s} {'delta':>7s} {'n/2':>5s}")
    print("-" * 70)

    any_changed = False
    for r in all_results:
        delta = r['new_astar'] - r['old_astar']
        changed = abs(delta) > 0.01
        if changed:
            any_changed = True
        marker = " ***" if changed else ""
        print(f"{r['name']:<28s} {r['n']:4d} {r['alpha']:6d} {r['theta']:7.2f} "
              f"{r['old_astar']:7.2f} {r['new_astar']:7.2f} {delta:+7.2f} "
              f"{r['n']/2:5.1f}{marker}")

    if any_changed:
        print("\n*** = value changed. Tables in paper need updating.")
        print("\nThe 'alpha* = n/2' universality claim was WRONG.")
        print("It held only because the LP used edge constraints (x_i+x_j<=1)")
        print("where x_i=1/2 is always feasible. With triad constraints")
        print("(x_i+x_j+x_k<=1), the LP is tighter.")
    else:
        print("\nNo values changed. The original computation was correct after all.")

    # Also check: does theta still satisfy alpha <= theta <= alpha*_new?
    print("\n\nSANITY CHECK: alpha <= theta <= alpha*")
    print("-" * 50)
    for r in all_results:
        ok_lower = r['alpha'] <= r['theta'] + 0.01
        ok_upper = r['theta'] <= r['new_astar'] + 0.01
        status = "OK" if (ok_lower and ok_upper) else "VIOLATION"
        print(f"  {r['name']:<28s}: {r['alpha']} <= {r['theta']:.2f} <= {r['new_astar']:.2f}  [{status}]")


if __name__ == "__main__":
    main()
