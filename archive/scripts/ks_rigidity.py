"""
ks_rigidity.py -- Rigidity analysis of minimal KS sets
========================================================

Tests whether each of our six algebraic islands' minimal KS sets
is rigid in the sense of Trandafir & Cabello (arXiv:2501.11640):
a KS set is rigid if its orthogonality graph has a unique geometric
realization up to unitary equivalence.

Method: Compute the Jacobian of all constraint equations (normalization
+ orthogonality) at the known solution. The null space of the Jacobian
represents continuous deformations. If the null space dimension equals
the dimension of the symmetry group, there are no deformations beyond
symmetries, and the set is rigid.

For real vectors in R^3:
  - Configuration: 3n real coordinates
  - Constraints: n normalizations (|v|^2=1) + m orthogonalities (<v,v'>=0)
  - Symmetry: SO(3), dim = 3
  - Rigid iff null(J) = 3

For complex vectors in C^3:
  - Configuration: 6n real coordinates (Re/Im of each component)
  - Constraints: n normalizations + 2m orthogonalities (Re/Im parts)
  - Symmetry: U(3) (dim 9) + U(1)^n individual phases - 1 overlap = n+8
  - Rigid iff null(J) = n+8

References:
  Trandafir & Cabello, PRA 111, 052204 (2025), arXiv:2501.11640
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

import cmath
import math
import random
import time
import numpy as np
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


def greedy_minimize(rays, pairs, triads, n_trials=500):
    """Greedy deletion to find minimal KS subset. Returns indices."""
    n_rays = len(rays)
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


def is_real_set(rays, tol=1e-10):
    """Check if all rays have purely real coordinates."""
    for r in rays:
        for c in r:
            if abs(c.imag) > tol:
                return False
    return True


def compute_rigidity(name, rays, ortho_pairs):
    """
    Compute rigidity by Jacobian null space analysis.

    Returns (null_dim, expected_sym_dim, is_rigid, deformation_dims).
    """
    n = len(rays)
    m = len(ortho_pairs)
    real = is_real_set(rays)

    if real:
        # Real case: 3n variables, n + m constraints
        # Variables: (x1, y1, z1, x2, y2, z2, ...)
        dim_vars = 3 * n
        n_constraints = n + m
        expected_sym = 3  # SO(3)

        # Build Jacobian matrix
        J = np.zeros((n_constraints, dim_vars))

        # Normalization constraints: |v_i|^2 - 1 = 0
        for i in range(n):
            v = rays[i]
            # d(|v_i|^2)/d(x_i) = 2*x_i, etc.
            J[i, 3*i] = 2 * v[0].real
            J[i, 3*i + 1] = 2 * v[1].real
            J[i, 3*i + 2] = 2 * v[2].real

        # Orthogonality constraints: <v_i, v_j> = 0
        for idx, (i, j) in enumerate(ortho_pairs):
            vi = rays[i]
            vj = rays[j]
            row = n + idx
            # d(<v_i, v_j>)/d(v_i_k) = v_j_k
            # d(<v_i, v_j>)/d(v_j_k) = v_i_k
            for k in range(3):
                J[row, 3*i + k] = vj[k].real
                J[row, 3*j + k] = vi[k].real

    else:
        # Complex case: 6n real variables, n + 2m constraints
        # Variables: (Re(x1), Im(x1), Re(y1), Im(y1), Re(z1), Im(z1), ...)
        dim_vars = 6 * n
        n_constraints = n + 2 * m
        expected_sym = n + 8  # U(3) dim 9 + n individual phases - 1

        J = np.zeros((n_constraints, dim_vars))

        # Normalization: |v_i|^2 - 1 = sum_k (Re(v_ik)^2 + Im(v_ik)^2) - 1 = 0
        for i in range(n):
            v = rays[i]
            for k in range(3):
                J[i, 6*i + 2*k] = 2 * v[k].real      # d/d(Re(v_ik))
                J[i, 6*i + 2*k + 1] = 2 * v[k].imag   # d/d(Im(v_ik))

        # Orthogonality: <v_i, v_j> = sum_k conj(v_ik) * v_jk = 0
        # Split into Re and Im parts:
        # Re(<v_i, v_j>) = sum_k [Re(v_ik)*Re(v_jk) + Im(v_ik)*Im(v_jk)]
        # Im(<v_i, v_j>) = sum_k [Re(v_ik)*Im(v_jk) - Im(v_ik)*Re(v_jk)]
        for idx, (i, j) in enumerate(ortho_pairs):
            vi = rays[i]
            vj = rays[j]
            re_row = n + 2 * idx
            im_row = n + 2 * idx + 1

            for k in range(3):
                rik = vi[k].real
                iik = vi[k].imag
                rjk = vj[k].real
                ijk = vj[k].imag

                # d Re(<vi,vj>) / d Re(v_ik) = Re(v_jk)
                J[re_row, 6*i + 2*k] = rjk
                # d Re(<vi,vj>) / d Im(v_ik) = Im(v_jk)
                J[re_row, 6*i + 2*k + 1] = ijk
                # d Re(<vi,vj>) / d Re(v_jk) = Re(v_ik)
                J[re_row, 6*j + 2*k] = rik
                # d Re(<vi,vj>) / d Im(v_jk) = Im(v_ik)
                J[re_row, 6*j + 2*k + 1] = iik

                # d Im(<vi,vj>) / d Re(v_ik) = Im(v_jk)
                J[im_row, 6*i + 2*k] = ijk
                # d Im(<vi,vj>) / d Im(v_ik) = -Re(v_jk)
                J[im_row, 6*i + 2*k + 1] = -rjk
                # d Im(<vi,vj>) / d Re(v_jk) = -Im(v_ik)
                J[im_row, 6*j + 2*k] = -iik
                # d Im(<vi,vj>) / d Im(v_jk) = Re(v_ik)
                J[im_row, 6*j + 2*k + 1] = rik

    # Compute SVD to find null space
    U, S, Vt = np.linalg.svd(J, full_matrices=True)

    # Count singular values near zero (tolerance for numerical rank)
    tol = max(J.shape) * np.max(S) * np.finfo(float).eps * 100
    rank = np.sum(S > tol)
    null_dim = dim_vars - rank
    deformation_dims = null_dim - expected_sym

    return null_dim, expected_sym, deformation_dims == 0, deformation_dims, rank, J.shape


def normalize_rays(rays):
    """Normalize rays to unit length."""
    result = []
    for r in rays:
        norm = math.sqrt(sum(abs(c)**2 for c in r))
        if norm > 0:
            result.append(tuple(c / norm for c in r))
        else:
            result.append(r)
    return result


# =====================================================================
# Build all islands and test rigidity
# =====================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("RIGIDITY ANALYSIS OF MINIMAL KS SETS")
    print("Trandafir-Cabello criterion: unique realization up to unitary equiv.")
    print("=" * 70)
    print()
    print("Method: Jacobian null space of orthogonality constraints.")
    print("Rigid iff null(J) = dim(symmetry group).")
    print("  R^3: sym = SO(3), dim = 3")
    print("  C^3: sym = U(3) + U(1)^n / overlap, dim = n + 8")
    print()

    t_start = time.time()
    results_summary = []

    # ================================================================
    # 1. CK-31 (Integer, R^3)
    # ================================================================
    print(f"{'='*70}")
    print("1. CK-31 (Integer, {0,±1,±2}) — REAL")
    print(f"{'='*70}")

    from math import gcd
    CK31_INT = [
        (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 1, -1), (0, 1, 2), (0, 2, -1),
        (1, 0, 0), (1, 0, 1), (1, 0, -1), (1, 0, 2), (1, 0, -2),
        (1, 1, 0), (1, 1, 1), (1, 1, -1), (1, 1, 2), (1, -1, 0),
        (1, -1, 1), (1, -1, -1), (1, -1, -2), (1, 2, 0), (1, 2, -1),
        (1, -2, 0), (1, -2, 1), (2, 0, 1), (2, 0, -1), (2, 1, 0),
        (2, 1, 1), (2, 1, -1), (2, -1, 0), (2, -1, 1), (2, -1, -1),
    ]
    ck31_rays = [tuple(complex(x) for x in v) for v in CK31_INT]
    ck31_rays = normalize_rays(ck31_rays)
    ck31_pairs, ck31_triads, _ = build_pairs_triads(ck31_rays)
    print(f"  Rays: {len(ck31_rays)}, Ortho pairs: {len(ck31_pairs)}, "
          f"Triads: {len(ck31_triads)}")
    assert is_ks_uncolorable(31, ck31_triads, ck31_pairs), "CK-31 should be KS!"

    null_dim, sym_dim, rigid, deform, rank, shape = compute_rigidity(
        "CK-31", ck31_rays, ck31_pairs)
    status = "RIGID" if rigid else f"NOT RIGID ({deform} deformation dims)"
    print(f"  Jacobian: {shape[0]} constraints × {shape[1]} variables")
    print(f"  Rank: {rank}, Null space: {null_dim}")
    print(f"  Expected symmetry dim: {sym_dim} (SO(3))")
    print(f"  --> {status}")
    results_summary.append(("CK-31 (Integer)", 31, "R^3", null_dim, sym_dim,
                            rigid, deform))

    # ================================================================
    # 2. Peres-33 (Z[sqrt(2)], R^3)
    # ================================================================
    print(f"\n{'='*70}")
    print("2. Peres-33 (Z[sqrt(2)]) — REAL")
    print(f"{'='*70}")

    s2 = math.sqrt(2)
    peres_alph = [complex(x) for x in [0, 1, -1, s2, -s2]]
    peres_pool = generate_rays_from_alphabet(peres_alph)
    peres_pool_pairs, peres_pool_triads, _ = build_pairs_triads(peres_pool)
    print(f"  Pool: {len(peres_pool)} rays")

    peres_min_idx, peres_min_n = greedy_minimize(
        peres_pool, peres_pool_pairs, peres_pool_triads, n_trials=500)
    peres_min_rays = normalize_rays([peres_pool[i] for i in peres_min_idx])
    peres_pairs, peres_triads, _ = build_pairs_triads(peres_min_rays)
    print(f"  Minimal: {peres_min_n} rays, {len(peres_pairs)} pairs, "
          f"{len(peres_triads)} triads")
    assert is_ks_uncolorable(peres_min_n, peres_triads, peres_pairs)

    null_dim, sym_dim, rigid, deform, rank, shape = compute_rigidity(
        "Peres-33", peres_min_rays, peres_pairs)
    status = "RIGID" if rigid else f"NOT RIGID ({deform} deformation dims)"
    print(f"  Jacobian: {shape[0]} × {shape[1]}")
    print(f"  Rank: {rank}, Null space: {null_dim}")
    print(f"  Expected symmetry dim: {sym_dim}")
    print(f"  --> {status}")
    results_summary.append(("Peres-33", peres_min_n,
                            "R^3" if is_real_set(peres_min_rays) else "C^3",
                            null_dim, sym_dim, rigid, deform))

    # ================================================================
    # 3. Eisenstein-33 (Z[omega], C^3)
    # ================================================================
    print(f"\n{'='*70}")
    print("3. Eisenstein-33 (Z[omega]) — COMPLEX")
    print(f"{'='*70}")

    eis_pool = generate_eisenstein_rays(max_coeff=1, dim=3, norm_cutoff=3)
    eis_pool_pairs, eis_pool_triads, _ = build_pairs_triads(eis_pool)
    print(f"  Pool: {len(eis_pool)} rays")

    eis_min_idx, eis_min_n = greedy_minimize(
        eis_pool, eis_pool_pairs, eis_pool_triads, n_trials=500)
    eis_min_rays = normalize_rays([eis_pool[i] for i in eis_min_idx])
    eis_pairs, eis_triads, _ = build_pairs_triads(eis_min_rays)
    print(f"  Minimal: {eis_min_n} rays, {len(eis_pairs)} pairs, "
          f"{len(eis_triads)} triads")
    assert is_ks_uncolorable(eis_min_n, eis_triads, eis_pairs)

    null_dim, sym_dim, rigid, deform, rank, shape = compute_rigidity(
        "Eisenstein-33", eis_min_rays, eis_pairs)
    status = "RIGID" if rigid else f"NOT RIGID ({deform} deformation dims)"
    print(f"  Jacobian: {shape[0]} × {shape[1]}")
    print(f"  Rank: {rank}, Null space: {null_dim}")
    print(f"  Expected symmetry dim: {sym_dim} (U(3) + U(1)^{eis_min_n})")
    print(f"  --> {status}")
    results_summary.append(("Eisenstein-33", eis_min_n, "C^3",
                            null_dim, sym_dim, rigid, deform))

    # ================================================================
    # 4. Z[sqrt(-2)]-33 (C^3)
    # ================================================================
    print(f"\n{'='*70}")
    print("4. Z[sqrt(-2)]-33 — COMPLEX")
    print(f"{'='*70}")

    sd2 = cmath.sqrt(-2)
    zsqrt2_alph = [0, 1, -1, sd2, -sd2]
    zsqrt2_pool = generate_rays_from_alphabet(zsqrt2_alph)
    zsqrt2_pool_pairs, zsqrt2_pool_triads, _ = build_pairs_triads(zsqrt2_pool)
    print(f"  Pool: {len(zsqrt2_pool)} rays")

    zsqrt2_min_idx, zsqrt2_min_n = greedy_minimize(
        zsqrt2_pool, zsqrt2_pool_pairs, zsqrt2_pool_triads, n_trials=500)
    zsqrt2_min_rays = normalize_rays([zsqrt2_pool[i] for i in zsqrt2_min_idx])
    zsqrt2_pairs, zsqrt2_triads, _ = build_pairs_triads(zsqrt2_min_rays)
    print(f"  Minimal: {zsqrt2_min_n} rays, {len(zsqrt2_pairs)} pairs, "
          f"{len(zsqrt2_triads)} triads")
    assert is_ks_uncolorable(zsqrt2_min_n, zsqrt2_triads, zsqrt2_pairs)

    null_dim, sym_dim, rigid, deform, rank, shape = compute_rigidity(
        "Z[sqrt(-2)]-33", zsqrt2_min_rays, zsqrt2_pairs)
    status = "RIGID" if rigid else f"NOT RIGID ({deform} deformation dims)"
    print(f"  Jacobian: {shape[0]} × {shape[1]}")
    print(f"  Rank: {rank}, Null space: {null_dim}")
    print(f"  Expected symmetry dim: {sym_dim}")
    print(f"  --> {status}")
    results_summary.append(("Z[sqrt(-2)]-33", zsqrt2_min_n, "C^3",
                            null_dim, sym_dim, rigid, deform))

    # ================================================================
    # 5. Heegner-7 (Z[(1+sqrt(-7))/2], C^3)
    # ================================================================
    print(f"\n{'='*70}")
    print("5. Heegner-7 (Z[(1+sqrt(-7))/2]) — COMPLEX")
    print(f"{'='*70}")

    gen7 = (1 + cmath.sqrt(-7)) / 2
    h7_alph = [0, 1, -1, gen7, -gen7, gen7.conjugate(), -gen7.conjugate()]
    h7_pool = generate_rays_from_alphabet(h7_alph)
    h7_pool_pairs, h7_pool_triads, _ = build_pairs_triads(h7_pool)
    print(f"  Pool: {len(h7_pool)} rays")

    h7_min_idx, h7_min_n = greedy_minimize(
        h7_pool, h7_pool_pairs, h7_pool_triads, n_trials=500)
    h7_min_rays = normalize_rays([h7_pool[i] for i in h7_min_idx])
    h7_pairs, h7_triads, _ = build_pairs_triads(h7_min_rays)
    print(f"  Minimal: {h7_min_n} rays, {len(h7_pairs)} pairs, "
          f"{len(h7_triads)} triads")
    assert is_ks_uncolorable(h7_min_n, h7_triads, h7_pairs)

    null_dim, sym_dim, rigid, deform, rank, shape = compute_rigidity(
        "Heegner-7", h7_min_rays, h7_pairs)
    status = "RIGID" if rigid else f"NOT RIGID ({deform} deformation dims)"
    print(f"  Jacobian: {shape[0]} × {shape[1]}")
    print(f"  Rank: {rank}, Null space: {null_dim}")
    print(f"  Expected symmetry dim: {sym_dim}")
    print(f"  --> {status}")
    results_summary.append(("Heegner-7", h7_min_n, "C^3",
                            null_dim, sym_dim, rigid, deform))

    # ================================================================
    # 6. Golden (Z[phi] + completion, R^3)
    # ================================================================
    print(f"\n{'='*70}")
    print("6. Golden (Z[phi] + cross-product completion) — REAL")
    print(f"{'='*70}")

    phi = (1 + math.sqrt(5)) / 2
    gold_alph = [complex(x) for x in [0, 1, -1, phi, -phi]]
    gold_pool_raw = generate_rays_from_alphabet(gold_alph)
    gold_pool = hermitian_completion(gold_pool_raw)
    gold_pool_pairs, gold_pool_triads, _ = build_pairs_triads(gold_pool)
    print(f"  Pool: {len(gold_pool)} rays")

    gold_min_idx, gold_min_n = greedy_minimize(
        gold_pool, gold_pool_pairs, gold_pool_triads, n_trials=200)
    gold_min_rays = normalize_rays([gold_pool[i] for i in gold_min_idx])
    gold_pairs, gold_triads, _ = build_pairs_triads(gold_min_rays)
    print(f"  Minimal: {gold_min_n} rays, {len(gold_pairs)} pairs, "
          f"{len(gold_triads)} triads")
    assert is_ks_uncolorable(gold_min_n, gold_triads, gold_pairs)

    null_dim, sym_dim, rigid, deform, rank, shape = compute_rigidity(
        "Golden", gold_min_rays, gold_pairs)
    status = "RIGID" if rigid else f"NOT RIGID ({deform} deformation dims)"
    print(f"  Jacobian: {shape[0]} × {shape[1]}")
    print(f"  Rank: {rank}, Null space: {null_dim}")
    print(f"  Expected symmetry dim: {sym_dim}")
    print(f"  --> {status}")
    results_summary.append(("Golden", gold_min_n,
                            "R^3" if is_real_set(gold_min_rays) else "C^3",
                            null_dim, sym_dim, rigid, deform))

    # ================================================================
    # Summary
    # ================================================================
    t_total = time.time() - t_start

    print(f"\n{'='*70}")
    print("RIGIDITY SUMMARY")
    print(f"{'='*70}")
    print(f"{'Island':<20} {'n':>4} {'Space':>5} {'null(J)':>8} "
          f"{'sym dim':>8} {'Deform':>8} {'Status':>12}")
    print("-" * 68)

    for name, n, space, null_d, sym_d, rig, deform_d in results_summary:
        status = "RIGID" if rig else f"FLEX ({deform_d})"
        print(f"{name:<20} {n:>4} {space:>5} {null_d:>8} "
              f"{sym_d:>8} {deform_d:>8} {status:>12}")

    n_rigid = sum(1 for r in results_summary if r[5])
    n_total = len(results_summary)
    print(f"\nRigid: {n_rigid}/{n_total}")
    print(f"Total time: {t_total:.1f}s")

    if n_rigid == n_total:
        print("\n*** ALL six islands produce rigid minimal KS sets ***")
        print("    Every orthogonality graph has a unique realization")
        print("    up to unitary equivalence.")
    elif n_rigid > 0:
        rigid_names = [r[0] for r in results_summary if r[5]]
        flex_names = [r[0] for r in results_summary if not r[5]]
        print(f"\n  Rigid: {', '.join(rigid_names)}")
        print(f"  Flexible: {', '.join(flex_names)}")
        for r in results_summary:
            if not r[5]:
                print(f"    {r[0]}: {r[6]} deformation dimensions "
                      f"(continuous family of realizations)")
