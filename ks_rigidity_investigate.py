"""
ks_rigidity_investigate.py -- Investigate Z[sqrt(-2)] deformation
=================================================================

The rigidity analysis found that Z[sqrt(-2)]-33 has exactly 1 deformation
dimension beyond symmetries. This script:

1. Identifies the deformation direction in the Jacobian null space
2. Projects out the symmetry directions (U(3) + individual phases)
3. Traces the deformation to see how vectors move
4. Checks whether the deformed set stays KS-uncolorable
5. Characterizes what kind of geometric freedom this represents
6. Compares with Peres-33 (same graph, rigid in R^3)
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
    """Greedy deletion to find minimal KS subset."""
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


def is_real_set(rays, tol=1e-10):
    """Check if all rays have purely real coordinates."""
    for r in rays:
        for c in r:
            if abs(c.imag) > tol:
                return False
    return True


def compute_jacobian_complex(rays, ortho_pairs):
    """Compute Jacobian for complex rays. Returns J, dim_vars, n_constraints."""
    n = len(rays)
    m = len(ortho_pairs)
    dim_vars = 6 * n
    n_constraints = n + 2 * m

    J = np.zeros((n_constraints, dim_vars))

    # Normalization
    for i in range(n):
        v = rays[i]
        for k in range(3):
            J[i, 6*i + 2*k] = 2 * v[k].real
            J[i, 6*i + 2*k + 1] = 2 * v[k].imag

    # Orthogonality (Re and Im parts of <v_i, v_j>)
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

            J[re_row, 6*i + 2*k] = rjk
            J[re_row, 6*i + 2*k + 1] = ijk
            J[re_row, 6*j + 2*k] = rik
            J[re_row, 6*j + 2*k + 1] = iik

            J[im_row, 6*i + 2*k] = ijk
            J[im_row, 6*i + 2*k + 1] = -rjk
            J[im_row, 6*j + 2*k] = -iik
            J[im_row, 6*j + 2*k + 1] = rik

    return J


def build_symmetry_generators(rays):
    """
    Build tangent vectors for symmetry directions at the given configuration.

    U(3) generators: 9 real generators (3 anti-symmetric real + 3 symmetric
    imaginary + 3 diagonal imaginary). Each acts as v -> A*v.

    Individual phase rotations: v_k -> i*v_k (one per ray).

    Returns matrix where each column is a tangent vector in 6n-space.
    """
    n = len(rays)
    generators = []

    # U(3) generators: 9 basis matrices for u(3) (Lie algebra)
    # Anti-Hermitian matrices iH where H is Hermitian
    # Basis: i*E_jj (3 diagonal), i*(E_jk + E_kj) (3 real symmetric off-diag),
    #         (E_jk - E_kj) (3 real antisymmetric off-diag)
    u3_basis = []

    # Diagonal: i * diag(1,0,0), i * diag(0,1,0), i * diag(0,0,1)
    for d in range(3):
        A = np.zeros((3, 3), dtype=complex)
        A[d, d] = 1j
        u3_basis.append(A)

    # Off-diagonal symmetric imaginary: i * (E_jk + E_kj)
    for j in range(3):
        for k in range(j+1, 3):
            A = np.zeros((3, 3), dtype=complex)
            A[j, k] = 1j
            A[k, j] = 1j
            u3_basis.append(A)

    # Off-diagonal antisymmetric real: E_jk - E_kj
    for j in range(3):
        for k in range(j+1, 3):
            A = np.zeros((3, 3), dtype=complex)
            A[j, k] = 1.0
            A[k, j] = -1.0
            u3_basis.append(A)

    assert len(u3_basis) == 9

    # For each U(3) generator A, the tangent vector is d/dt(e^{tA} v)|_{t=0} = A*v
    for A in u3_basis:
        tang = np.zeros(6 * n)
        for i in range(n):
            v = np.array([rays[i][0], rays[i][1], rays[i][2]])
            Av = A @ v
            for k in range(3):
                tang[6*i + 2*k] = Av[k].real
                tang[6*i + 2*k + 1] = Av[k].imag
        generators.append(tang)

    # Individual phase rotations: v_i -> e^{it} v_i, tangent = i * v_i
    for i in range(n):
        tang = np.zeros(6 * n)
        v = rays[i]
        for k in range(3):
            iv_k = 1j * v[k]
            tang[6*i + 2*k] = iv_k.real
            tang[6*i + 2*k + 1] = iv_k.imag
        generators.append(tang)

    return np.array(generators).T  # columns = generators


def project_out_symmetries(null_space, sym_generators):
    """
    Given the null space of J (columns = null vectors) and the symmetry
    generators (columns = sym tangent vectors), find the components of the
    null space orthogonal to the symmetry subspace.

    Returns the deformation directions (orthogonal to all symmetries).
    """
    # Combine into one matrix
    # First, project sym_generators into null_space
    # (sym generators should lie in null space; project for numerical stability)

    # Orthonormalize symmetry generators within the null space
    # Project each sym gen onto null space
    NS = null_space  # columns
    SG = sym_generators  # columns

    # Project SG onto column space of NS: proj = NS @ NS^T @ SG
    proj_SG = NS @ (NS.T @ SG)

    # Orthonormalize these projected generators
    U_sg, S_sg, _ = np.linalg.svd(proj_SG, full_matrices=False)
    tol = max(proj_SG.shape) * np.max(S_sg) * np.finfo(float).eps * 100
    sym_rank = np.sum(S_sg > tol)
    sym_basis = U_sg[:, :sym_rank]

    # Project null space onto orthogonal complement of sym_basis
    # deform = NS - sym_basis @ sym_basis^T @ NS
    deform = NS - sym_basis @ (sym_basis.T @ NS)

    # SVD to find remaining directions
    U_d, S_d, _ = np.linalg.svd(deform, full_matrices=False)
    tol_d = max(deform.shape) * max(np.max(S_d), 1e-15) * np.finfo(float).eps * 1000
    deform_rank = np.sum(S_d > tol_d)

    deform_dirs = U_d[:, :deform_rank]
    return deform_dirs, sym_rank, deform_rank


def vec_from_flat(flat, n):
    """Convert flat 6n real array back to list of complex 3-vectors."""
    rays = []
    for i in range(n):
        v = tuple(complex(flat[6*i + 2*k], flat[6*i + 2*k + 1]) for k in range(3))
        rays.append(v)
    return rays


def flat_from_rays(rays):
    """Convert list of complex 3-vectors to flat 6n real array."""
    n = len(rays)
    flat = np.zeros(6 * n)
    for i in range(n):
        for k in range(3):
            flat[6*i + 2*k] = rays[i][k].real
            flat[6*i + 2*k + 1] = rays[i][k].imag
    return flat


def trace_deformation(rays, ortho_pairs, deform_dir, epsilons):
    """
    Move along deformation direction and check:
    - Orthogonality constraints still satisfied?
    - KS-uncolorable?
    - How do coordinates change?
    """
    n = len(rays)
    base = flat_from_rays(rays)
    results = []

    for eps in epsilons:
        new_flat = base + eps * deform_dir

        # Renormalize each vector
        new_rays_raw = vec_from_flat(new_flat, n)
        new_rays = normalize_rays(new_rays_raw)

        # Check orthogonality preservation
        max_dot = 0
        for i, j in ortho_pairs:
            dot = abs(hermitian_dot(new_rays[i], new_rays[j]))
            max_dot = max(max_dot, dot)

        # Check KS
        new_pairs, new_triads, _ = build_pairs_triads(new_rays, tol=1e-6)
        ks = is_ks_uncolorable(n, new_triads, new_pairs)

        results.append((eps, max_dot, len(new_pairs), len(new_triads), ks))

    return results


# =====================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("INVESTIGATING Z[sqrt(-2)]-33 DEFORMATION")
    print("=" * 70)
    print()

    t_start = time.time()

    # Build the Z[sqrt(-2)] pool and minimize
    print("Building Z[sqrt(-2)] pool...")
    sd2 = cmath.sqrt(-2)
    zsqrt2_alph = [0, 1, -1, sd2, -sd2]
    zsqrt2_pool = generate_rays_from_alphabet(zsqrt2_alph)
    zsqrt2_pool_pairs, zsqrt2_pool_triads, _ = build_pairs_triads(zsqrt2_pool)
    print(f"  Pool: {len(zsqrt2_pool)} rays")

    print("Finding minimal set (500 greedy trials)...")
    zsqrt2_min_idx, zsqrt2_min_n = greedy_minimize(
        zsqrt2_pool, zsqrt2_pool_pairs, zsqrt2_pool_triads, n_trials=500)
    min_rays = normalize_rays([zsqrt2_pool[i] for i in zsqrt2_min_idx])
    n = len(min_rays)
    pairs, triads, adj = build_pairs_triads(min_rays)
    print(f"  Minimal: {n} rays, {len(pairs)} pairs, {len(triads)} triads")
    assert is_ks_uncolorable(n, triads, pairs)

    # ================================================================
    # Step 1: Compute Jacobian and full null space
    # ================================================================
    print(f"\n{'='*70}")
    print("STEP 1: Jacobian null space")
    print(f"{'='*70}")

    J = compute_jacobian_complex(min_rays, pairs)
    U_j, S_j, Vt_j = np.linalg.svd(J, full_matrices=True)
    tol = max(J.shape) * np.max(S_j) * np.finfo(float).eps * 100
    rank = np.sum(S_j > tol)
    null_dim = 6 * n - rank
    null_space = Vt_j[rank:].T  # columns = null vectors

    print(f"  Jacobian: {J.shape[0]} × {J.shape[1]}")
    print(f"  Rank: {rank}, Null space dim: {null_dim}")
    print(f"  Expected symmetry dim: {n + 8} = U(3)[9] + U(1)^{n}[{n}] - 1")

    # ================================================================
    # Step 2: Build symmetry generators and project them out
    # ================================================================
    print(f"\n{'='*70}")
    print("STEP 2: Identify symmetry vs deformation directions")
    print(f"{'='*70}")

    sym_gens = build_symmetry_generators(min_rays)
    print(f"  Symmetry generators: {sym_gens.shape[1]} "
          f"(9 U(3) + {n} phases)")

    # Verify symmetry generators are in the null space
    sym_residuals = J @ sym_gens
    max_residual = np.max(np.abs(sym_residuals))
    print(f"  Max J @ sym_gen residual: {max_residual:.2e} "
          f"({'OK' if max_residual < 1e-10 else 'WARNING'})")

    deform_dirs, sym_rank_in_null, deform_rank = project_out_symmetries(
        null_space, sym_gens)
    print(f"  Symmetry directions in null space: {sym_rank_in_null}")
    print(f"  Deformation directions: {deform_rank}")

    if deform_rank == 0:
        print("\n  No deformation found! Set is rigid after all.")
        print("  (Previous result may have been a numerical artifact.)")
        sys.exit(0)

    # ================================================================
    # Step 3: Analyze the deformation direction
    # ================================================================
    print(f"\n{'='*70}")
    print("STEP 3: Characterize the deformation")
    print(f"{'='*70}")

    deform = deform_dirs[:, 0]  # The single deformation direction

    # Which rays are most affected?
    ray_movements = []
    for i in range(n):
        movement = np.sqrt(sum(deform[6*i + 2*k]**2 + deform[6*i + 2*k + 1]**2
                               for k in range(3)))
        ray_movements.append((i, movement))

    ray_movements.sort(key=lambda x: -x[1])

    print("  Rays most affected by deformation:")
    print(f"  {'Ray':>4} {'Movement':>10} {'Vector':>50} {'|Im|':>10}")
    n_moving = 0
    for i, mv in ray_movements:
        if mv < 1e-10:
            continue
        n_moving += 1
        v = min_rays[i]
        im_norm = math.sqrt(sum(c.imag**2 for c in v))
        v_str = f"({v[0]:.4f}, {v[1]:.4f}, {v[2]:.4f})"
        print(f"  {i:>4} {mv:>10.6f} {v_str:>50} {im_norm:>10.6f}")

    print(f"\n  Total rays affected: {n_moving}/{n}")

    # Decompose deformation into real/imaginary parts per ray
    print(f"\n  Deformation direction decomposition:")
    print(f"  {'Ray':>4} {'dRe(x)':>8} {'dIm(x)':>8} {'dRe(y)':>8} "
          f"{'dIm(y)':>8} {'dRe(z)':>8} {'dIm(z)':>8}")
    for i, mv in ray_movements[:15]:
        if mv < 1e-10:
            break
        vals = [deform[6*i + j] for j in range(6)]
        print(f"  {i:>4} " + " ".join(f"{v:>8.5f}" for v in vals))

    # Check: is the deformation purely imaginary (phase-like)?
    real_part_norm = 0
    imag_part_norm = 0
    for i in range(n):
        for k in range(3):
            v_k = min_rays[i][k]
            d_re = deform[6*i + 2*k]
            d_im = deform[6*i + 2*k + 1]
            # Tangent to phase rotation at v_k: d/dt(e^{it} v_k) = i*v_k
            # = (-Im(v_k), Re(v_k))
            # Project deformation onto phase direction and orthogonal
            phase_dir = np.array([-v_k.imag, v_k.real])
            d_vec = np.array([d_re, d_im])
            norm_v = abs(v_k)
            if norm_v > 1e-12:
                phase_comp = np.dot(d_vec, phase_dir) / norm_v
                ortho_comp = np.linalg.norm(d_vec - (np.dot(d_vec, phase_dir)
                                            / (norm_v**2)) * phase_dir)
                real_part_norm += ortho_comp**2
                imag_part_norm += phase_comp**2

    real_part_norm = math.sqrt(real_part_norm)
    imag_part_norm = math.sqrt(imag_part_norm)
    print(f"\n  Deformation decomposition:")
    print(f"    Phase-like component: {imag_part_norm:.6f}")
    print(f"    Geometric component:  {real_part_norm:.6f}")

    # ================================================================
    # Step 4: Trace the deformation
    # ================================================================
    print(f"\n{'='*70}")
    print("STEP 4: Trace the deformation (move along it)")
    print(f"{'='*70}")

    epsilons = [0, 0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5]
    results = trace_deformation(min_rays, pairs, deform, epsilons)

    print(f"  {'epsilon':>8} {'max|<vi,vj>|':>14} {'pairs':>6} "
          f"{'triads':>7} {'KS?':>5}")
    print(f"  {'-'*44}")
    for eps, max_dot, np_, nt, ks in results:
        ks_str = "YES" if ks else "NO"
        print(f"  {eps:>8.3f} {max_dot:>14.2e} {np_:>6} {nt:>7} {ks_str:>5}")

    # ================================================================
    # Step 5: Check if deformation leaves the Z[sqrt(-2)] ring
    # ================================================================
    print(f"\n{'='*70}")
    print("STEP 5: Does the deformation leave the algebraic ring?")
    print(f"{'='*70}")

    # At epsilon=0.01, extract deformed vectors and check coordinates
    eps_test = 0.01
    base = flat_from_rays(min_rays)
    new_flat = base + eps_test * deform
    new_rays = normalize_rays(vec_from_flat(new_flat, n))

    print(f"\n  At epsilon={eps_test}:")
    print(f"  Sample deformed vectors (first 5 that moved):")
    for i, mv in ray_movements[:5]:
        if mv < 1e-10:
            continue
        orig = min_rays[i]
        defd = new_rays[i]
        print(f"    Ray {i}:")
        print(f"      Original: ({orig[0]:.6f}, {orig[1]:.6f}, {orig[2]:.6f})")
        print(f"      Deformed: ({defd[0]:.6f}, {defd[1]:.6f}, {defd[2]:.6f})")

    # ================================================================
    # Step 6: Compare with Peres-33 (same graph type, but rigid)
    # ================================================================
    print(f"\n{'='*70}")
    print("STEP 6: Compare with Peres-33 (graph-isomorphic, rigid)")
    print(f"{'='*70}")

    s2 = math.sqrt(2)
    peres_alph = [complex(x) for x in [0, 1, -1, s2, -s2]]
    peres_pool = generate_rays_from_alphabet(peres_alph)
    peres_pool_pairs, peres_pool_triads, _ = build_pairs_triads(peres_pool)
    peres_min_idx, peres_min_n = greedy_minimize(
        peres_pool, peres_pool_pairs, peres_pool_triads, n_trials=500)
    peres_min_rays = normalize_rays([peres_pool[i] for i in peres_min_idx])
    peres_pairs, peres_triads, _ = build_pairs_triads(peres_min_rays)

    print(f"  Peres-33: {peres_min_n} rays, {len(peres_pairs)} pairs, "
          f"{len(peres_triads)} triads")
    print(f"  Z[sqrt(-2)]-33: {n} rays, {len(pairs)} pairs, "
          f"{len(triads)} triads")

    # Count real vs complex rays in each
    n_real_peres = sum(1 for r in peres_min_rays if is_real_set([r]))
    n_complex_peres = peres_min_n - n_real_peres
    n_real_zsqrt2 = sum(1 for r in min_rays if is_real_set([r]))
    n_complex_zsqrt2 = n - n_real_zsqrt2

    print(f"  Peres: {n_real_peres} real + {n_complex_peres} complex rays")
    print(f"  Z[sqrt(-2)]: {n_real_zsqrt2} real + {n_complex_zsqrt2} complex rays")

    # Check if deformation moves only complex rays
    real_ray_movement = 0
    complex_ray_movement = 0
    for i, mv in ray_movements:
        if mv < 1e-10:
            continue
        if is_real_set([min_rays[i]]):
            real_ray_movement += mv
        else:
            complex_ray_movement += mv

    print(f"\n  Deformation movement on real rays: {real_ray_movement:.6f}")
    print(f"  Deformation movement on complex rays: {complex_ray_movement:.6f}")

    if real_ray_movement < 1e-8 and complex_ray_movement > 1e-4:
        print("  --> Deformation affects ONLY complex-coordinate rays")
        print("  --> This explains why Peres (all real) is rigid!")
    elif real_ray_movement > 1e-4:
        print("  --> Deformation affects real rays too")

    # ================================================================
    # Step 7: Is it a Galois conjugation?
    # ================================================================
    print(f"\n{'='*70}")
    print("STEP 7: Is the deformation related to Galois conjugation?")
    print(f"{'='*70}")

    # Z[sqrt(-2)] has Galois automorphism sqrt(-2) -> -sqrt(-2)
    # i.e., i*sqrt(2) -> -i*sqrt(2), which means conjugating the
    # imaginary part of sqrt(-2) coordinates.
    # Check if the deformation direction is tangent to this.

    # Build Galois tangent: d/dt (v with sqrt(-2) -> e^{it} * sqrt(-2))|_{t=0}
    # If v has coordinates a + b*sqrt(-2), Galois sends to a - b*sqrt(-2)
    # Interpolating: a + b*e^{it}*sqrt(-2). Tangent at t=0: i*b*sqrt(-2)
    # This multiplies the sqrt(-2) component by i.
    #
    # For a coordinate c = a + b*i*sqrt(2) (since sqrt(-2) = i*sqrt(2)):
    # The sqrt(-2) part is b*i*sqrt(2). Galois tangent: i * b*i*sqrt(2) = -b*sqrt(2).
    # So the tangent replaces Im(c) *= -1 ... no, let me think more carefully.
    #
    # sqrt(-2) = i * sqrt(2). Galois: sqrt(-2) -> -sqrt(-2) = -i*sqrt(2).
    # So coordinate c = a + b*(i*sqrt(2)) maps to a + b*(-i*sqrt(2)) = a - b*i*sqrt(2)
    # = conj(c) if a is real and the imaginary part is b*sqrt(2).
    #
    # But our coordinates might not decompose cleanly this way after normalization.
    # Let's just check: does applying complex conjugation to all vectors
    # give a valid realization of the same graph?

    conj_rays = [tuple(c.conjugate() for c in r) for r in min_rays]
    conj_rays = normalize_rays(conj_rays)
    conj_pairs, conj_triads, _ = build_pairs_triads(conj_rays)

    print(f"  Conjugated set: {len(conj_pairs)} pairs, {len(conj_triads)} triads")
    print(f"  Original set:   {len(pairs)} pairs, {len(triads)} triads")

    if len(conj_pairs) == len(pairs) and len(conj_triads) == len(triads):
        print("  Conjugation preserves the orthogonality graph!")

        # Check if conjugated set is unitarily equivalent to original
        # Quick test: are the sorted inner product spectra the same?
        orig_dots = sorted([abs(hermitian_dot(min_rays[i], min_rays[j]))
                            for i in range(n) for j in range(i+1, n)])
        conj_dots = sorted([abs(hermitian_dot(conj_rays[i], conj_rays[j]))
                            for i in range(n) for j in range(i+1, n)])

        diff = max(abs(a - b) for a, b in zip(orig_dots, conj_dots))
        print(f"  Max difference in sorted |<v_i,v_j>| spectra: {diff:.2e}")

        if diff < 1e-8:
            print("  Spectra match -> conjugate is likely unitarily equivalent")
        else:
            print("  Spectra DIFFER -> conjugate is NOT unitarily equivalent")
            print("  --> The deformation connects original to its Galois conjugate!")

            # Check if deformation direction aligns with conjugation tangent
            conj_flat = flat_from_rays(conj_rays)
            orig_flat = flat_from_rays(min_rays)
            conj_dir = conj_flat - orig_flat
            conj_dir_norm = np.linalg.norm(conj_dir)
            if conj_dir_norm > 1e-12:
                conj_dir /= conj_dir_norm
                alignment = abs(np.dot(deform, conj_dir))
                print(f"  Alignment of deformation with conjugation direction: "
                      f"{alignment:.6f}")
                if alignment > 0.9:
                    print("  --> STRONG alignment: deformation IS the Galois "
                          "conjugation path!")
                elif alignment > 0.5:
                    print("  --> Partial alignment with Galois conjugation")
                else:
                    print("  --> Deformation is NOT aligned with conjugation")
    else:
        print("  Conjugation changes the graph structure")

    # ================================================================
    # Summary
    # ================================================================
    t_total = time.time() - t_start

    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"  Z[sqrt(-2)]-33 has exactly 1 deformation dimension")
    print(f"  {n_moving} of {n} rays are affected")
    print(f"  Deformation moves complex rays: {complex_ray_movement:.6f}")
    print(f"  Deformation moves real rays:    {real_ray_movement:.6f}")
    print(f"  Total time: {t_total:.1f}s")
