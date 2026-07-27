"""
ks_rigidity_finite.py -- Test if Z[sqrt(-2)] flex is finite or infinitesimal
=============================================================================

The Jacobian analysis found 1 deformation dimension for Z[sqrt(-2)]-33.

Key question: Is this a FINITE flexibility (a continuous family of
realizations) or merely an INFINITESIMAL flex (first-order motion
blocked by higher-order obstructions)?

ANSWER (corrected 2026-07-27): the flex is FINITE.  It integrates to the
one-parameter family of Gould and Aravind, Found. Phys. 40, 1096 (2010),
on which Peres-33 and Z[sqrt(-2)]-33 are antipodal points; exact
certificates in Flores Gordillo, doi:10.5281/zenodo.21488474.

Earlier runs of this script reported the opposite because the
second-order obstruction vector was assembled in a different row order
than the Jacobian -- see the note at the d2_vec assembly below.  The
normalization block of that vector is 2*|dv_i/dt|^2, strictly positive
for any ray that moves, so the "all second derivatives vanish" branch
below can never fire and every run reaches the projection test.

In rigidity theory, this is the distinction between:
  - Flexible: admits a continuous path of distinct realizations
  - Infinitesimally flexible but finitely rigid: first-order flex exists
    but no finite motion (like a "prestressed" framework)

Method: Predictor-corrector path following on the constraint manifold.
If the Newton corrector converges, the flex is finite. If it diverges,
the flex is only infinitesimal.

Also: second-order analysis via the Hessian of constraints.
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

import cmath
import math
import random
import time
import numpy as np
from scipy.optimize import minimize as scipy_minimize

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


def flat_from_rays(rays):
    """Convert rays to flat 6n real array."""
    n = len(rays)
    flat = np.zeros(6 * n)
    for i in range(n):
        for k in range(3):
            flat[6*i + 2*k] = rays[i][k].real
            flat[6*i + 2*k + 1] = rays[i][k].imag
    return flat


def rays_from_flat(flat, n):
    """Convert flat array back to rays."""
    rays = []
    for i in range(n):
        v = tuple(complex(flat[6*i + 2*k], flat[6*i + 2*k + 1]) for k in range(3))
        rays.append(v)
    return rays


def constraint_vector(flat, n, ortho_pairs):
    """Evaluate all constraints. Returns vector of constraint violations."""
    rays = rays_from_flat(flat, n)
    m = len(ortho_pairs)
    c = np.zeros(n + 2 * m)

    # Normalization
    for i in range(n):
        c[i] = sum(abs(rays[i][k])**2 for k in range(3)) - 1.0

    # Orthogonality
    for idx, (i, j) in enumerate(ortho_pairs):
        dot = hermitian_dot(rays[i], rays[j])
        c[n + 2*idx] = dot.real
        c[n + 2*idx + 1] = dot.imag

    return c


def compute_jacobian(flat, n, ortho_pairs):
    """Compute Jacobian of constraints."""
    rays = rays_from_flat(flat, n)
    m = len(ortho_pairs)
    dim_vars = 6 * n
    n_constraints = n + 2 * m

    J = np.zeros((n_constraints, dim_vars))

    for i in range(n):
        v = rays[i]
        for k in range(3):
            J[i, 6*i + 2*k] = 2 * v[k].real
            J[i, 6*i + 2*k + 1] = 2 * v[k].imag

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


def compute_null_space(J, tol_factor=100):
    """Compute null space of J via SVD."""
    U, S, Vt = np.linalg.svd(J, full_matrices=True)
    tol = max(J.shape) * np.max(S) * np.finfo(float).eps * tol_factor
    rank = np.sum(S > tol)
    null_space = Vt[rank:].T
    return null_space, rank


def build_symmetry_generators(rays):
    """Build tangent vectors for U(3) + individual phases."""
    n = len(rays)
    generators = []

    u3_basis = []
    for d in range(3):
        A = np.zeros((3, 3), dtype=complex)
        A[d, d] = 1j
        u3_basis.append(A)
    for j in range(3):
        for k in range(j+1, 3):
            A = np.zeros((3, 3), dtype=complex)
            A[j, k] = 1j
            A[k, j] = 1j
            u3_basis.append(A)
    for j in range(3):
        for k in range(j+1, 3):
            A = np.zeros((3, 3), dtype=complex)
            A[j, k] = 1.0
            A[k, j] = -1.0
            u3_basis.append(A)

    for A in u3_basis:
        tang = np.zeros(6 * n)
        for i in range(n):
            v = np.array([rays[i][0], rays[i][1], rays[i][2]])
            Av = A @ v
            for k in range(3):
                tang[6*i + 2*k] = Av[k].real
                tang[6*i + 2*k + 1] = Av[k].imag
        generators.append(tang)

    for i in range(n):
        tang = np.zeros(6 * n)
        v = rays[i]
        for k in range(3):
            iv_k = 1j * v[k]
            tang[6*i + 2*k] = iv_k.real
            tang[6*i + 2*k + 1] = iv_k.imag
        generators.append(tang)

    return np.array(generators).T


def get_deformation_direction(rays, ortho_pairs):
    """Extract the single deformation direction (orthogonal to symmetries)."""
    n = len(rays)
    flat = flat_from_rays(rays)
    J = compute_jacobian(flat, n, ortho_pairs)
    null_space, rank = compute_null_space(J)

    sym_gens = build_symmetry_generators(rays)

    # Project sym gens into null space
    proj_SG = null_space @ (null_space.T @ sym_gens)
    U_sg, S_sg, _ = np.linalg.svd(proj_SG, full_matrices=False)
    tol = max(proj_SG.shape) * np.max(S_sg) * np.finfo(float).eps * 100
    sym_rank = np.sum(S_sg > tol)
    sym_basis = U_sg[:, :sym_rank]

    deform = null_space - sym_basis @ (sym_basis.T @ null_space)
    U_d, S_d, _ = np.linalg.svd(deform, full_matrices=False)
    tol_d = max(deform.shape) * max(np.max(S_d), 1e-15) * np.finfo(float).eps * 1000
    deform_rank = np.sum(S_d > tol_d)

    return U_d[:, 0], null_space, rank


def predictor_corrector_step(flat, n, ortho_pairs, deform_dir, step_size,
                             max_newton=20, newton_tol=1e-14):
    """
    One predictor-corrector step along the deformation.

    Predictor: move along deform_dir by step_size.
    Corrector: Newton iteration to project back onto constraint surface,
    staying close to the predicted point.

    Returns (new_flat, converged, n_newton_iters, final_residual).
    """
    # Predict
    predicted = flat + step_size * deform_dir

    # Correct: solve c(x) = 0 by Newton, but constrain to move orthogonal
    # to deform_dir (to avoid sliding back along the deformation)
    current = predicted.copy()

    for iteration in range(max_newton):
        c = constraint_vector(current, n, ortho_pairs)
        residual = np.max(np.abs(c))

        if residual < newton_tol:
            return current, True, iteration + 1, residual

        J = compute_jacobian(current, n, ortho_pairs)

        # Least-squares Newton step: dx = -J^+ c
        # But constrain dx to be orthogonal to deform_dir
        # Use augmented system: [J; deform_dir^T] dx = [-c; 0]
        n_c = len(c)
        A = np.vstack([J, deform_dir.reshape(1, -1)])
        b = np.concatenate([-c, [0.0]])

        dx, _, _, _ = np.linalg.lstsq(A, b, rcond=None)

        current = current + dx

    c = constraint_vector(current, n, ortho_pairs)
    residual = np.max(np.abs(c))
    return current, residual < newton_tol, max_newton, residual


def second_order_analysis(rays, ortho_pairs, deform_dir):
    """
    Check if the first-order flex extends to second order.

    For each constraint c_k(x), compute d^2 c_k / dt^2 along the
    deformation direction. If any constraint has nonzero second
    derivative, the flex is obstructed at second order.
    """
    n = len(rays)
    flat = flat_from_rays(rays)
    m = len(ortho_pairs)

    # Second derivatives of constraints along deformation direction
    # For normalization: c_i = |v_i|^2 - 1
    # d^2 c_i / dt^2 = 2 * sum_k (dv_ik/dt)^2 where dv/dt is the deformation
    second_derivs_norm = []
    for i in range(n):
        d2 = 0.0
        for k in range(3):
            d_re = deform_dir[6*i + 2*k]
            d_im = deform_dir[6*i + 2*k + 1]
            d2 += 2 * (d_re**2 + d_im**2)
        second_derivs_norm.append(d2)

    # For orthogonality: c_{ij} = <v_i, v_j>
    # d^2 c_{ij} / dt^2 = 2 * sum_k conj(dv_ik/dt) * dv_jk/dt
    # Split into Re and Im
    second_derivs_ortho_re = []
    second_derivs_ortho_im = []
    for idx, (i, j) in enumerate(ortho_pairs):
        d2_re = 0.0
        d2_im = 0.0
        for k in range(3):
            di_re = deform_dir[6*i + 2*k]
            di_im = deform_dir[6*i + 2*k + 1]
            dj_re = deform_dir[6*j + 2*k]
            dj_im = deform_dir[6*j + 2*k + 1]
            # conj(dv_i) * dv_j = (di_re - i*di_im)(dj_re + i*dj_im)
            # Re: di_re*dj_re + di_im*dj_im
            # Im: di_re*dj_im - di_im*dj_re
            d2_re += 2 * (di_re * dj_re + di_im * dj_im)
            d2_im += 2 * (di_re * dj_im - di_im * dj_re)
        second_derivs_ortho_re.append(d2_re)
        second_derivs_ortho_im.append(d2_im)

    return second_derivs_norm, second_derivs_ortho_re, second_derivs_ortho_im


# =====================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("FINITE vs INFINITESIMAL FLEXIBILITY OF Z[sqrt(-2)]-33")
    print("=" * 70)
    print()

    t_start = time.time()

    # Build Z[sqrt(-2)] minimal set
    print("Building Z[sqrt(-2)] pool and minimizing...")
    sd2 = cmath.sqrt(-2)
    zsqrt2_alph = [0, 1, -1, sd2, -sd2]
    zsqrt2_pool = generate_rays_from_alphabet(zsqrt2_alph)
    pool_pairs, pool_triads, _ = build_pairs_triads(zsqrt2_pool)
    min_idx, min_n = greedy_minimize(
        zsqrt2_pool, pool_pairs, pool_triads, n_trials=500)
    min_rays = normalize_rays([zsqrt2_pool[i] for i in min_idx])
    n = len(min_rays)
    pairs, triads, adj = build_pairs_triads(min_rays)
    print(f"  {n} rays, {len(pairs)} pairs, {len(triads)} triads")

    # Get deformation direction
    deform, null_space, J_rank = get_deformation_direction(min_rays, pairs)
    print(f"  Null space dim: {6*n - J_rank}, Deformation dir found")

    # ================================================================
    # Test 1: Second-order obstruction analysis
    # ================================================================
    print(f"\n{'='*70}")
    print("TEST 1: Second-order obstruction analysis")
    print(f"{'='*70}")
    print("  If d2c/dt2 != 0 along the flex, it's obstructed at 2nd order.")
    print()

    d2_norm, d2_ortho_re, d2_ortho_im = second_order_analysis(
        min_rays, pairs, deform)

    max_d2_norm = max(abs(x) for x in d2_norm)
    max_d2_ortho_re = max(abs(x) for x in d2_ortho_re)
    max_d2_ortho_im = max(abs(x) for x in d2_ortho_im)

    print(f"  Normalization 2nd derivs: max |d²c/dt²| = {max_d2_norm:.6e}")
    print(f"  Orthogonality Re 2nd derivs: max |d²c/dt²| = {max_d2_ortho_re:.6e}")
    print(f"  Orthogonality Im 2nd derivs: max |d²c/dt²| = {max_d2_ortho_im:.6e}")

    # Count non-zero second derivatives
    tol_2nd = 1e-10
    n_nonzero_norm = sum(1 for x in d2_norm if abs(x) > tol_2nd)
    n_nonzero_re = sum(1 for x in d2_ortho_re if abs(x) > tol_2nd)
    n_nonzero_im = sum(1 for x in d2_ortho_im if abs(x) > tol_2nd)

    print(f"\n  Non-zero 2nd derivs:")
    print(f"    Normalization: {n_nonzero_norm}/{n}")
    print(f"    Orthogonality (Re): {n_nonzero_re}/{len(pairs)}")
    print(f"    Orthogonality (Im): {n_nonzero_im}/{len(pairs)}")

    if max_d2_norm < tol_2nd and max_d2_ortho_re < tol_2nd and max_d2_ortho_im < tol_2nd:
        print("\n  --> ALL second derivatives vanish!")
        print("      Flex is unobstructed at 2nd order — likely FINITE.")
    else:
        # Check if obstructions are in the range of J (can be corrected)
        # or in the cokernel (true obstructions)
        J = compute_jacobian(flat_from_rays(min_rays), n, pairs)

        # The obstruction is the vector of second derivatives.
        #
        # It MUST use the same row ordering as constraint_vector() and
        # compute_jacobian(), which interleave the orthogonality parts as
        # [norms, Re_0, Im_0, Re_1, Im_1, ...].  Assembling it in blocked
        # order -- np.concatenate([d2_norm, d2_ortho_re, d2_ortho_im]) -- is
        # a permutation of the correct vector, so the projection below then
        # measures nothing.  That error produced the spurious "nonzero
        # cokernel component" reported in v1-v7 of the paper; the true
        # component is zero and the flex is finite (Gould-Aravind circle).
        d2_vec = np.zeros(n + 2 * len(pairs))
        d2_vec[:n] = d2_norm
        d2_vec[n::2] = d2_ortho_re
        d2_vec[n + 1::2] = d2_ortho_im

        # Check if d2_vec is in the range of J
        # If yes, it can be corrected by a second-order term
        # If no (component in cokernel), it's a true obstruction
        U_j, S_j, Vt_j = np.linalg.svd(J, full_matrices=True)
        tol_sv = max(J.shape) * np.max(S_j) * np.finfo(float).eps * 100
        rank = np.sum(S_j > tol_sv)

        # Project d2_vec onto range of J and cokernel
        range_proj = U_j[:, :rank] @ (U_j[:, :rank].T @ d2_vec)
        cokernel_proj = d2_vec - range_proj

        cokernel_norm = np.linalg.norm(cokernel_proj)
        range_norm = np.linalg.norm(range_proj)
        total_norm = np.linalg.norm(d2_vec)

        print(f"\n  2nd-order obstruction analysis:")
        print(f"    |d²c/dt² total|:    {total_norm:.6e}")
        print(f"    |range component|:  {range_norm:.6e} (correctable)")
        print(f"    |cokernel component|: {cokernel_norm:.6e} (true obstruction)")

        if cokernel_norm < tol_2nd:
            print("\n  --> Obstruction is ENTIRELY in range of J")
            print("      Can be corrected by 2nd-order perturbation — FINITE flex")
        elif cokernel_norm > 1e-6:
            print("\n  --> Obstruction has component in cokernel of J")
            print("      Flex is BLOCKED at 2nd order — INFINITESIMALLY flexible")
            print("      but FINITELY RIGID")
        else:
            print("\n  --> Borderline: cokernel component is small but nonzero")

    # ================================================================
    # Test 2: Predictor-corrector path following
    # ================================================================
    print(f"\n{'='*70}")
    print("TEST 2: Predictor-corrector path following")
    print(f"{'='*70}")
    print("  Attempting to follow the deformation on the constraint surface.")
    print("  If Newton corrector converges, the flex is finite.")
    print()

    flat0 = flat_from_rays(min_rays)
    step_sizes = [1e-6, 1e-5, 1e-4, 1e-3, 5e-3, 1e-2, 5e-2, 0.1]

    print(f"  {'Step':>10} {'Newton its':>12} {'Converged':>10} "
          f"{'Residual':>12} {'Max dot':>12}")
    print(f"  {'-'*58}")

    for step in step_sizes:
        new_flat, converged, n_iters, residual = predictor_corrector_step(
            flat0, n, pairs, deform, step)

        # Check max orthogonality violation
        new_rays = rays_from_flat(new_flat, n)
        new_rays = normalize_rays(new_rays)
        max_dot = max(abs(hermitian_dot(new_rays[i], new_rays[j]))
                      for i, j in pairs)

        conv_str = "YES" if converged else "NO"
        print(f"  {step:>10.1e} {n_iters:>12} {conv_str:>10} "
              f"{residual:>12.2e} {max_dot:>12.2e}")

    # ================================================================
    # Test 3: Nonlinear optimization to find distinct realization
    # ================================================================
    print(f"\n{'='*70}")
    print("TEST 3: Direct search for a distinct realization")
    print(f"{'='*70}")
    print("  Minimizing constraint violations starting from a perturbed point,")
    print("  with a penalty for being too close to the original.")
    print()

    def objective(x, orig_flat, n, ortho_pairs, lam=10.0):
        """Minimize constraint violations with distance penalty."""
        c = constraint_vector(x, n, ortho_pairs)
        constraint_cost = np.sum(c**2)

        # Penalty for being close to original (encourage exploration)
        dist = np.linalg.norm(x - orig_flat)
        distance_bonus = -lam * min(dist, 0.5)  # cap the bonus

        return constraint_cost + distance_bonus

    # Try several starting points along the deformation
    best_distinct = None
    best_dist = 0

    for trial_eps in [0.01, 0.05, 0.1, 0.2, 0.5]:
        x0 = flat0 + trial_eps * deform
        # Add small random perturbation to escape local symmetry
        x0 += np.random.randn(len(x0)) * 0.001

        result = scipy_minimize(
            lambda x: np.sum(constraint_vector(x, n, pairs)**2),
            x0, method='L-BFGS-B', options={'maxiter': 5000, 'ftol': 1e-30})

        final_c = constraint_vector(result.x, n, pairs)
        max_violation = np.max(np.abs(final_c))
        dist = np.linalg.norm(result.x - flat0)

        # Check if we found a valid distinct realization
        if max_violation < 1e-10 and dist > 0.01:
            if dist > best_dist:
                best_distinct = result.x
                best_dist = dist
            print(f"  eps={trial_eps:.2f}: FOUND distinct realization! "
                  f"dist={dist:.6f}, max_viol={max_violation:.2e}")
        else:
            print(f"  eps={trial_eps:.2f}: dist={dist:.6f}, "
                  f"max_viol={max_violation:.2e} "
                  f"{'(converged back)' if dist < 0.01 else '(not on surface)'}")

    if best_distinct is not None:
        print(f"\n  BEST distinct realization at distance {best_dist:.6f}")
        new_rays = normalize_rays(rays_from_flat(best_distinct, n))
        new_pairs, new_triads, _ = build_pairs_triads(new_rays, tol=1e-6)
        ks = is_ks_uncolorable(n, new_triads, new_pairs)
        print(f"  Pairs: {len(new_pairs)}, Triads: {len(new_triads)}, KS: {ks}")

        # Check if unitarily equivalent to original
        # Compare sorted non-zero inner product magnitudes
        orig_dots = sorted([abs(hermitian_dot(min_rays[i], min_rays[j]))
                            for i in range(n) for j in range(i+1, n)
                            if abs(hermitian_dot(min_rays[i], min_rays[j])) > 1e-8])
        new_dots = sorted([abs(hermitian_dot(new_rays[i], new_rays[j]))
                           for i in range(n) for j in range(i+1, n)
                           if abs(hermitian_dot(new_rays[i], new_rays[j])) > 1e-8])

        if len(orig_dots) == len(new_dots):
            max_diff = max(abs(a - b) for a, b in zip(orig_dots, new_dots))
            print(f"  Spectral difference: {max_diff:.6e}")
            if max_diff < 1e-6:
                print("  --> Likely unitarily equivalent (same spectrum)")
            else:
                print("  --> GENUINELY DISTINCT realization (different spectrum)!")
                print("      Z[sqrt(-2)]-33 is FINITELY FLEXIBLE!")
        else:
            print(f"  Different number of non-zero dots: {len(orig_dots)} vs "
                  f"{len(new_dots)}")
    else:
        print("\n  No distinct realization found by optimization.")
        print("  Consistent with infinitesimal-only flexibility.")

    # ================================================================
    # Summary
    # ================================================================
    t_total = time.time() - t_start

    print(f"\n{'='*70}")
    print("CONCLUSION")
    print(f"{'='*70}")
    print(f"  Total time: {t_total:.1f}s")
