"""Verify CSW sandwich theorem for ALL pools.
Bug: ks_csw_extended.py didn't pass triads to fractional_packing,
and paper Table 7 has wrong alpha* values."""

import cmath
import math
import numpy as np
from scipy.optimize import linprog

from ks_new_islands import generate_rays_from_alphabet, hermitian_completion
from ks_csw_extended import build_pairs_triads, max_independent_set, lovasz_theta
from ks_complex import generate_eisenstein_rays


def fractional_packing(n, edges, triads=None):
    """Fractional packing with proper clique constraints."""
    if triads:
        triad_edges = set()
        for a, b, c_ in triads:
            triad_edges.add((min(a, b), max(a, b)))
            triad_edges.add((min(a, c_), max(a, c_)))
            triad_edges.add((min(b, c_), max(b, c_)))
        standalone = [(a, b) for a, b in edges
                      if (min(a, b), max(a, b)) not in triad_edges]
        n_constraints = len(triads) + len(standalone)
        c = -np.ones(n)
        A_ub = np.zeros((n_constraints, n))
        b_ub = np.ones(n_constraints)
        for idx, (a, b, c_) in enumerate(triads):
            A_ub[idx, a] = 1.0
            A_ub[idx, b] = 1.0
            A_ub[idx, c_] = 1.0
        offset = len(triads)
        for idx, (a, b) in enumerate(standalone):
            A_ub[offset + idx, a] = 1.0
            A_ub[offset + idx, b] = 1.0
    else:
        n_constraints = len(edges)
        c = -np.ones(n)
        A_ub = np.zeros((n_constraints, n))
        b_ub = np.ones(n_constraints)
        for idx, (i, j) in enumerate(edges):
            A_ub[idx, i] = 1.0
            A_ub[idx, j] = 1.0
    bounds = [(0, 1)] * n
    result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
    return -result.fun if result.success else None


def check_pool(name, rays):
    pairs, triads = build_pairs_triads(rays)
    n = len(rays)
    print(f"\n{'='*60}")
    print(f"  {name}: {n} rays, {len(pairs)} pairs, {len(triads)} triads")

    alpha = max_independent_set(n, pairs)
    theta = lovasz_theta(n, pairs)
    astar = fractional_packing(n, pairs, triads=triads)

    ok = "OK" if alpha <= theta + 0.01 and theta <= astar + 0.01 else "VIOLATED!"
    print(f"  alpha={alpha}  theta={theta:.2f}  alpha*={astar:.2f}  theta/alpha={theta/alpha:.3f}  [{ok}]")
    return name, n, len(triads), alpha, theta, astar


results = []

# Integer pool
int_alph = [complex(x) for x in [0, 1, -1, 2, -2]]
int_rays = generate_rays_from_alphabet(int_alph)
results.append(check_pool("Integer", int_rays))

# Peres pool
s2 = math.sqrt(2)
p_alph = [complex(x) for x in [0, 1, -1, s2, -s2]]
p_rays = generate_rays_from_alphabet(p_alph)
results.append(check_pool("Peres", p_rays))

# Z[sqrt(-2)] pool
s2i = complex(0, math.sqrt(2))
z2_alph = [complex(0), complex(1), complex(-1), s2i, -s2i]
z2_rays = generate_rays_from_alphabet(z2_alph)
results.append(check_pool("Z[sqrt(-2)]", z2_rays))

# Eisenstein pool
eis_rays = generate_eisenstein_rays(max_coeff=1, dim=3, norm_cutoff=3)
results.append(check_pool("Eisenstein", eis_rays))

# Heegner-7 pool
a7 = (1 + cmath.sqrt(-7)) / 2
h7_alph = [complex(0), complex(1), complex(-1), a7, -a7, a7.conjugate(), -a7.conjugate()]
h7_rays_raw = generate_rays_from_alphabet(h7_alph)
h7_rays = hermitian_completion(h7_rays_raw)
results.append(check_pool("Heegner-7", h7_rays))

# Summary table
print(f"\n\n{'='*80}")
print(f"CORRECTED TABLE FOR PAPER (full pools)")
print(f"{'='*80}")
print(f"{'Island':<15s} {'n':>4s} {'triads':>7s} {'alpha':>6s} {'theta':>8s} {'alpha*':>8s} {'th/al':>7s}")
print("-" * 60)
for name, n, t, alpha, theta, astar in results:
    print(f"{name:<15s} {n:4d} {t:7d} {alpha:6d} {theta:8.2f} {astar:8.2f} {theta/alpha:7.3f}")
