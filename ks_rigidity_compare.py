"""
ks_rigidity_compare.py -- Why Z[sqrt(-2)] flexes but Eisenstein doesn't
========================================================================

Both Z[sqrt(-2)]-33 and Eisenstein-33 live in C^3, both have 33 rays,
similar pair/triad counts. Yet Eisenstein is rigid and Z[sqrt(-2)] has
1 infinitesimal deformation.

This script investigates the structural differences:
1. Graph structure comparison (degree sequence, triads, cliques)
2. Coordinate structure (which coordinates are real vs complex)
3. Constraint counting and rank deficiency analysis
4. Identify which specific constraints are "loose" in Z[sqrt(-2)]
5. Compare with Peres-33 (graph-isomorphic to Z[sqrt(-2)], rigid in R^3)
6. Test: does embedding Peres-33 INTO C^3 create the same flex?
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

import cmath
import math
import random
import time
import numpy as np
from collections import Counter

from pysat.solvers import Glucose4

from ks_complex import (
    generate_eisenstein_rays,
    hermitian_dot,
)
from ks_new_islands import (
    generate_rays_from_alphabet,
    hermitian_completion,
)

random.seed(42)


def build_pairs_triads(rays, tol=1e-9):
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
    result = []
    for r in rays:
        norm = math.sqrt(sum(abs(c)**2 for c in r))
        if norm > 0:
            result.append(tuple(c / norm for c in r))
        else:
            result.append(r)
    return result


def is_real_ray(r, tol=1e-10):
    return all(abs(c.imag) < tol for c in r)


def flat_from_rays(rays):
    n = len(rays)
    flat = np.zeros(6 * n)
    for i in range(n):
        for k in range(3):
            flat[6*i + 2*k] = rays[i][k].real
            flat[6*i + 2*k + 1] = rays[i][k].imag
    return flat


def compute_jacobian_complex(rays, ortho_pairs):
    n = len(rays)
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


def compute_jacobian_real(rays, ortho_pairs):
    """Jacobian for real vectors in R^3."""
    n = len(rays)
    m = len(ortho_pairs)
    dim_vars = 3 * n
    n_constraints = n + m
    J = np.zeros((n_constraints, dim_vars))
    for i in range(n):
        v = rays[i]
        J[i, 3*i] = 2 * v[0].real
        J[i, 3*i + 1] = 2 * v[1].real
        J[i, 3*i + 2] = 2 * v[2].real
    for idx, (i, j) in enumerate(ortho_pairs):
        vi = rays[i]
        vj = rays[j]
        row = n + idx
        for k in range(3):
            J[row, 3*i + k] = vj[k].real
            J[row, 3*j + k] = vi[k].real
    return J


def null_space_dim(J, tol_factor=100):
    U, S, Vt = np.linalg.svd(J, full_matrices=True)
    tol = max(J.shape) * np.max(S) * np.finfo(float).eps * tol_factor
    rank = np.sum(S > tol)
    return J.shape[1] - rank, rank


def graph_invariants(n, pairs, triads, adj):
    """Compute graph invariants for comparison."""
    degree_seq = sorted([len(adj[i]) for i in range(n)], reverse=True)

    # Extra pairs (orthogonal but not in any triad)
    triad_pairs = set()
    for a, b, c in triads:
        triad_pairs.add((min(a,b), max(a,b)))
        triad_pairs.add((min(a,c), max(a,c)))
        triad_pairs.add((min(b,c), max(b,c)))
    extra_pairs = [(i,j) for i,j in pairs if (i,j) not in triad_pairs]

    # Rays per triad count
    ray_triad_count = Counter()
    for a, b, c in triads:
        ray_triad_count[a] += 1
        ray_triad_count[b] += 1
        ray_triad_count[c] += 1
    triad_participation = sorted(ray_triad_count.values(), reverse=True)

    return {
        'degree_seq': degree_seq,
        'n_extra_pairs': len(extra_pairs),
        'triad_participation': triad_participation,
        'max_degree': max(degree_seq),
        'min_degree': min(degree_seq),
    }


# =====================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("WHY Z[sqrt(-2)] FLEXES BUT EISENSTEIN DOESN'T")
    print("=" * 70)
    print()

    t_start = time.time()

    # ================================================================
    # Build all three 33-ray sets
    # ================================================================
    print("Building pools and minimizing...")

    # Eisenstein
    eis_pool = generate_eisenstein_rays(max_coeff=1, dim=3, norm_cutoff=3)
    eis_pp, eis_pt, _ = build_pairs_triads(eis_pool)
    eis_idx, eis_n = greedy_minimize(eis_pool, eis_pp, eis_pt, n_trials=500)
    eis_rays = normalize_rays([eis_pool[i] for i in eis_idx])
    eis_pairs, eis_triads, eis_adj = build_pairs_triads(eis_rays)
    print(f"  Eisenstein-33: {eis_n} rays, {len(eis_pairs)} pairs, "
          f"{len(eis_triads)} triads")

    # Z[sqrt(-2)]
    sd2 = cmath.sqrt(-2)
    z2_pool = generate_rays_from_alphabet([0, 1, -1, sd2, -sd2])
    z2_pp, z2_pt, _ = build_pairs_triads(z2_pool)
    z2_idx, z2_n = greedy_minimize(z2_pool, z2_pp, z2_pt, n_trials=500)
    z2_rays = normalize_rays([z2_pool[i] for i in z2_idx])
    z2_pairs, z2_triads, z2_adj = build_pairs_triads(z2_rays)
    print(f"  Z[sqrt(-2)]-33: {z2_n} rays, {len(z2_pairs)} pairs, "
          f"{len(z2_triads)} triads")

    # Peres (real, graph-isomorphic to Z[sqrt(-2)])
    s2 = math.sqrt(2)
    p_pool = generate_rays_from_alphabet([complex(x) for x in [0, 1, -1, s2, -s2]])
    p_pp, p_pt, _ = build_pairs_triads(p_pool)
    p_idx, p_n = greedy_minimize(p_pool, p_pp, p_pt, n_trials=500)
    p_rays = normalize_rays([p_pool[i] for i in p_idx])
    p_pairs, p_triads, p_adj = build_pairs_triads(p_rays)
    print(f"  Peres-33: {p_n} rays, {len(p_pairs)} pairs, "
          f"{len(p_triads)} triads")

    # ================================================================
    # 1. Graph structure comparison
    # ================================================================
    print(f"\n{'='*70}")
    print("1. GRAPH STRUCTURE COMPARISON")
    print(f"{'='*70}")

    eis_inv = graph_invariants(eis_n, eis_pairs, eis_triads, eis_adj)
    z2_inv = graph_invariants(z2_n, z2_pairs, z2_triads, z2_adj)
    p_inv = graph_invariants(p_n, p_pairs, p_triads, p_adj)

    print(f"\n  {'Property':<25} {'Eisenstein':>12} {'Z[sqrt(-2)]':>12} {'Peres':>12}")
    print(f"  {'-'*63}")
    print(f"  {'Rays':<25} {eis_n:>12} {z2_n:>12} {p_n:>12}")
    print(f"  {'Ortho pairs':<25} {len(eis_pairs):>12} {len(z2_pairs):>12} "
          f"{len(p_pairs):>12}")
    print(f"  {'Triads':<25} {len(eis_triads):>12} {len(z2_triads):>12} "
          f"{len(p_triads):>12}")
    print(f"  {'Extra pairs (non-triad)':<25} {eis_inv['n_extra_pairs']:>12} "
          f"{z2_inv['n_extra_pairs']:>12} {p_inv['n_extra_pairs']:>12}")
    print(f"  {'Max degree':<25} {eis_inv['max_degree']:>12} "
          f"{z2_inv['max_degree']:>12} {p_inv['max_degree']:>12}")
    print(f"  {'Min degree':<25} {eis_inv['min_degree']:>12} "
          f"{z2_inv['min_degree']:>12} {p_inv['min_degree']:>12}")

    print(f"\n  Degree sequences:")
    print(f"    Eis: {eis_inv['degree_seq']}")
    print(f"    Z2:  {z2_inv['degree_seq']}")
    print(f"    Per: {p_inv['degree_seq']}")

    # Are Z[sqrt(-2)] and Peres graph-isomorphic?
    if (z2_inv['degree_seq'] == p_inv['degree_seq'] and
        len(z2_pairs) == len(p_pairs) and len(z2_triads) == len(p_triads)):
        print(f"\n  Z[sqrt(-2)] and Peres: SAME degree sequence + counts")
        print(f"  (Previously shown to be graph-isomorphic)")

    if eis_inv['degree_seq'] != z2_inv['degree_seq']:
        print(f"\n  Eisenstein and Z[sqrt(-2)]: DIFFERENT degree sequences")
        print(f"  --> Different orthogonality graphs (not isomorphic)")
    else:
        print(f"\n  Eisenstein and Z[sqrt(-2)]: SAME degree sequence")

    # ================================================================
    # 2. Coordinate structure
    # ================================================================
    print(f"\n{'='*70}")
    print("2. COORDINATE STRUCTURE")
    print(f"{'='*70}")

    for name, rays in [("Eisenstein", eis_rays), ("Z[sqrt(-2)]", z2_rays),
                        ("Peres", p_rays)]:
        n_real = sum(1 for r in rays if is_real_ray(r))
        n_complex = len(rays) - n_real

        # Count zero components
        n_zero_coords = sum(1 for r in rays for c in r if abs(c) < 1e-10)

        # Classify coordinate types
        coord_types = Counter()
        for r in rays:
            for c in r:
                if abs(c) < 1e-10:
                    coord_types['zero'] += 1
                elif abs(c.imag) < 1e-10:
                    coord_types['real'] += 1
                else:
                    coord_types['complex'] += 1

        print(f"\n  {name}:")
        print(f"    Real rays: {n_real}, Complex rays: {n_complex}")
        print(f"    Coordinate types: {dict(coord_types)}")
        print(f"    Zero coordinates: {n_zero_coords} / {len(rays)*3}")

    # ================================================================
    # 3. Constraint counting and Jacobian analysis
    # ================================================================
    print(f"\n{'='*70}")
    print("3. CONSTRAINT COUNTING AND JACOBIAN ANALYSIS")
    print(f"{'='*70}")

    for name, rays, pairs_ in [("Eisenstein", eis_rays, eis_pairs),
                                 ("Z[sqrt(-2)]", z2_rays, z2_pairs),
                                 ("Peres", p_rays, p_pairs)]:
        n = len(rays)
        m = len(pairs_)
        is_real = all(is_real_ray(r) for r in rays)

        if is_real:
            dim_vars = 3 * n
            n_constraints = n + m
            sym_dim = 3  # SO(3)
            J = compute_jacobian_real(rays, pairs_)
        else:
            dim_vars = 6 * n
            n_constraints = n + 2 * m
            sym_dim = n + 8  # U(3) + phases
            J = compute_jacobian_complex(rays, pairs_)

        null_d, rank = null_space_dim(J)
        deform_d = null_d - sym_dim

        print(f"\n  {name} ({'R^3' if is_real else 'C^3'}):")
        print(f"    Variables: {dim_vars}")
        print(f"    Constraints: {n_constraints} "
              f"({n} norms + {'2x' if not is_real else ''}{m} ortho)")
        print(f"    Rank(J): {rank}")
        print(f"    Null(J): {null_d}")
        print(f"    Symmetry dim: {sym_dim}")
        print(f"    Deformation dims: {deform_d}")
        print(f"    Constraint surplus: {n_constraints - dim_vars + sym_dim}")

    # ================================================================
    # 4. KEY TEST: Embed Peres-33 in C^3 — does the flex appear?
    # ================================================================
    print(f"\n{'='*70}")
    print("4. EMBED PERES-33 IN C^3 -- DOES THE FLEX APPEAR?")
    print(f"{'='*70}")
    print("  Peres-33 is rigid in R^3 (null=3, sym=3).")
    print("  If we treat it as complex vectors (with Im=0),")
    print("  does a flex appear in the larger C^3 space?")

    J_peres_complex = compute_jacobian_complex(p_rays, p_pairs)
    null_d_pc, rank_pc = null_space_dim(J_peres_complex)
    sym_dim_pc = p_n + 8
    deform_pc = null_d_pc - sym_dim_pc

    print(f"\n  Peres-33 embedded in C^3:")
    print(f"    Variables: {6 * p_n}")
    print(f"    Constraints: {p_n + 2*len(p_pairs)}")
    print(f"    Rank(J): {rank_pc}")
    print(f"    Null(J): {null_d_pc}")
    print(f"    Symmetry dim: {sym_dim_pc} (U(3) + U(1)^{p_n})")
    print(f"    Deformation dims: {deform_pc}")

    if deform_pc > 0:
        print(f"\n  --> YES! Peres-33 in C^3 has {deform_pc} flex dimensions!")
        print(f"      The flex is a property of the GRAPH in C^3, not the algebra.")
        print(f"      Both Peres and Z[sqrt(-2)] share the same graph,")
        print(f"      and that graph is rigid in R^3 but flexible in C^3.")
    else:
        print(f"\n  --> NO. Peres-33 stays rigid even in C^3.")
        print(f"      The flex is specific to Z[sqrt(-2)] coordinates.")

    # ================================================================
    # 5. Compare Eisenstein graph in R^3 (hypothetical)
    # ================================================================
    print(f"\n{'='*70}")
    print("5. EISENSTEIN GRAPH: RIGID IN C^3 -- WOULD IT FLEX IN R^3?")
    print(f"{'='*70}")
    print("  Eisenstein has genuinely complex coordinates (omega = e^{2pi*i/3}).")
    print("  It can't live in R^3. But we can check constraint counts.")

    n_eis = len(eis_rays)
    m_eis = len(eis_pairs)

    print(f"\n  Eisenstein constraint arithmetic:")
    print(f"    In C^3: {6*n_eis} vars, {n_eis + 2*m_eis} constraints, "
          f"sym={n_eis+8}")
    print(f"    Hypothetical R^3: {3*n_eis} vars, {n_eis + m_eis} constraints, "
          f"sym=3")
    print(f"    C^3 surplus: {n_eis + 2*m_eis - 6*n_eis + n_eis + 8} = "
          f"{2*n_eis + 2*m_eis - 6*n_eis + 8}")
    print(f"    R^3 surplus: {n_eis + m_eis - 3*n_eis + 3} = "
          f"{m_eis - 2*n_eis + 3}")

    # ================================================================
    # 6. The critical difference: imaginary constraint redundancy
    # ================================================================
    print(f"\n{'='*70}")
    print("6. IMAGINARY CONSTRAINT REDUNDANCY ANALYSIS")
    print(f"{'='*70}")
    print("  For real vectors, Im(<v_i,v_j>) = 0 is automatically satisfied.")
    print("  For complex vectors, it's an independent constraint.")
    print("  The flex in Z[sqrt(-2)] may come from redundancy among Im constraints.")

    # For Z[sqrt(-2)], separate Re and Im orthogonality constraints
    n_z = len(z2_rays)
    m_z = len(z2_pairs)

    # Build separate Jacobians for normalization, Re(ortho), Im(ortho)
    J_norm = np.zeros((n_z, 6 * n_z))
    for i in range(n_z):
        v = z2_rays[i]
        for k in range(3):
            J_norm[i, 6*i + 2*k] = 2 * v[k].real
            J_norm[i, 6*i + 2*k + 1] = 2 * v[k].imag

    J_re = np.zeros((m_z, 6 * n_z))
    J_im = np.zeros((m_z, 6 * n_z))
    for idx, (i, j) in enumerate(z2_pairs):
        vi = z2_rays[i]
        vj = z2_rays[j]
        for k in range(3):
            rik, iik = vi[k].real, vi[k].imag
            rjk, ijk = vj[k].real, vj[k].imag
            J_re[idx, 6*i + 2*k] = rjk
            J_re[idx, 6*i + 2*k + 1] = ijk
            J_re[idx, 6*j + 2*k] = rik
            J_re[idx, 6*j + 2*k + 1] = iik
            J_im[idx, 6*i + 2*k] = ijk
            J_im[idx, 6*i + 2*k + 1] = -rjk
            J_im[idx, 6*j + 2*k] = -iik
            J_im[idx, 6*j + 2*k + 1] = rik

    # Check ranks of progressive constraint additions
    J_norm_only = J_norm
    J_norm_re = np.vstack([J_norm, J_re])
    J_norm_re_im = np.vstack([J_norm, J_re, J_im])

    _, rank_norm = null_space_dim(J_norm_only)
    _, rank_norm_re = null_space_dim(J_norm_re)
    _, rank_full = null_space_dim(J_norm_re_im)

    print(f"\n  Z[sqrt(-2)]-33 progressive constraint ranks:")
    print(f"    Norm only:         rank {rank_norm} "
          f"(of {J_norm_only.shape[0]} constraints)")
    print(f"    Norm + Re(ortho):  rank {rank_norm_re} "
          f"(of {J_norm_re.shape[0]} constraints, "
          f"+{rank_norm_re - rank_norm} from Re)")
    print(f"    Norm + Re + Im:    rank {rank_full} "
          f"(of {J_norm_re_im.shape[0]} constraints, "
          f"+{rank_full - rank_norm_re} from Im)")
    print(f"    Im constraints added {rank_full - rank_norm_re} rank "
          f"(of {m_z} Im equations)")
    print(f"    Redundant Im constraints: "
          f"{m_z - (rank_full - rank_norm_re)}")

    # Same analysis for Eisenstein
    n_e = len(eis_rays)
    m_e = len(eis_pairs)

    J_norm_e = np.zeros((n_e, 6 * n_e))
    for i in range(n_e):
        v = eis_rays[i]
        for k in range(3):
            J_norm_e[i, 6*i + 2*k] = 2 * v[k].real
            J_norm_e[i, 6*i + 2*k + 1] = 2 * v[k].imag

    J_re_e = np.zeros((m_e, 6 * n_e))
    J_im_e = np.zeros((m_e, 6 * n_e))
    for idx, (i, j) in enumerate(eis_pairs):
        vi = eis_rays[i]
        vj = eis_rays[j]
        for k in range(3):
            rik, iik = vi[k].real, vi[k].imag
            rjk, ijk = vj[k].real, vj[k].imag
            J_re_e[idx, 6*i + 2*k] = rjk
            J_re_e[idx, 6*i + 2*k + 1] = ijk
            J_re_e[idx, 6*j + 2*k] = rik
            J_re_e[idx, 6*j + 2*k + 1] = iik
            J_im_e[idx, 6*i + 2*k] = ijk
            J_im_e[idx, 6*i + 2*k + 1] = -rjk
            J_im_e[idx, 6*j + 2*k] = -iik
            J_im_e[idx, 6*j + 2*k + 1] = rik

    J_norm_only_e = J_norm_e
    J_norm_re_e = np.vstack([J_norm_e, J_re_e])
    J_norm_re_im_e = np.vstack([J_norm_e, J_re_e, J_im_e])

    _, rank_norm_e = null_space_dim(J_norm_only_e)
    _, rank_norm_re_e = null_space_dim(J_norm_re_e)
    _, rank_full_e = null_space_dim(J_norm_re_im_e)

    print(f"\n  Eisenstein-33 progressive constraint ranks:")
    print(f"    Norm only:         rank {rank_norm_e} "
          f"(of {J_norm_only_e.shape[0]} constraints)")
    print(f"    Norm + Re(ortho):  rank {rank_norm_re_e} "
          f"(of {J_norm_re_e.shape[0]} constraints, "
          f"+{rank_norm_re_e - rank_norm_e} from Re)")
    print(f"    Norm + Re + Im:    rank {rank_full_e} "
          f"(of {J_norm_re_im_e.shape[0]} constraints, "
          f"+{rank_full_e - rank_norm_re_e} from Im)")
    print(f"    Im constraints added {rank_full_e - rank_norm_re_e} rank "
          f"(of {m_e} Im equations)")
    print(f"    Redundant Im constraints: "
          f"{m_e - (rank_full_e - rank_norm_re_e)}")

    # ================================================================
    # 7. Compare: how many real vs complex orthogonal PAIRS
    # ================================================================
    print(f"\n{'='*70}")
    print("7. REAL vs COMPLEX ORTHOGONAL PAIRS")
    print(f"{'='*70}")

    for name, rays, pairs_ in [("Eisenstein", eis_rays, eis_pairs),
                                 ("Z[sqrt(-2)]", z2_rays, z2_pairs)]:
        n_rr = 0  # both real
        n_rc = 0  # one real, one complex
        n_cc = 0  # both complex
        for i, j in pairs_:
            ri = is_real_ray(rays[i])
            rj = is_real_ray(rays[j])
            if ri and rj:
                n_rr += 1
            elif ri or rj:
                n_rc += 1
            else:
                n_cc += 1
        print(f"\n  {name}:")
        print(f"    Real-Real pairs:    {n_rr}")
        print(f"    Real-Complex pairs: {n_rc}")
        print(f"    Complex-Complex:    {n_cc}")
        print(f"    For R-R pairs, Im(<v,v'>) is automatically 0")
        print(f"    For R-C pairs, Im constraint is Im(v_j) . Re(v_i) = 0")
        print(f"    For C-C pairs, Im constraint is independent")

    # ================================================================
    # Summary
    # ================================================================
    t_total = time.time() - t_start

    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"  Total time: {t_total:.1f}s")
