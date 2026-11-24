"""
ks_explore_new2.py -- Continue exploration from crashed session
================================================================

Focus:
1. Complete the runs that didn't finish (Z[phi] extended, Z[1/2], groups)
2. Targeted experiments to probe below 31
3. Irrational/algebraic combinations not yet tried

Key insight from session 1: Z[sqrt2] extended hit MIN 31 (matching CK-31).
Question: Can ANY alphabet produce a KS set with fewer than 31 vectors?
"""

import numpy as np
import itertools
import random
import cmath
from collections import defaultdict

from ks_sat import is_uncolorable as sat_uncolorable, build_graph
from ks_complex import canonicalize_complex_ray, hermitian_dot
from ks_new_islands import (
    generate_rays_from_alphabet,
    hermitian_completion,
    sat_minimize,
)
from ks_new_island_analysis import build_pairs_triads

random.seed(42)
np.random.seed(42)

OMEGA = cmath.exp(2j * cmath.pi / 3)
sqrt2 = np.sqrt(2)
sqrt3 = np.sqrt(3)
sqrt5 = np.sqrt(5)
phi = (1 + sqrt5) / 2


def test_alphabet(name, alphabet, use_completion=True, n_trials=500, max_rays=400):
    """Test an alphabet for KS-uncolorability with a ray count safety limit."""
    rays = generate_rays_from_alphabet(alphabet)

    if len(rays) > max_rays and use_completion:
        # Skip completion for huge pools, just test raw
        pairs, triads = build_pairs_triads(rays)
        print(f"  {name}: {len(rays)}r/{len(triads)}t (skipping completion, too large)")
        if triads:
            uncol = sat_uncolorable(len(rays), pairs, triads)
            if uncol:
                subset, min_size, min_sizes = sat_minimize(rays, pairs, triads, n_trials=n_trials)
                s = set(subset)
                remap = {old: new for new, old in enumerate(sorted(subset))}
                min_triads = [(remap[a], remap[b], remap[c])
                              for a, b, c in triads if a in s and b in s and c in s]
                print(f"    UNCOLORABLE -> MIN {min_size} ({len(min_triads)} bases)")
                top3 = sorted(min_sizes.items())[:3]
                print(f"    Size distribution: {dict(top3)}")
                return {'name': name, 'uncol': True, 'min_size': min_size, 'n_bases': len(min_triads),
                        'rays': len(rays), 'triads': len(triads), 'size_dist': min_sizes}
            else:
                print(f"    Colorable (raw)")
                return {'name': name, 'uncol': False, 'min_size': None, 'rays': len(rays)}
        return {'name': name, 'uncol': False, 'min_size': None, 'rays': len(rays)}

    pairs, triads = build_pairs_triads(rays)
    n_raw = len(rays)
    n_triads_raw = len(triads)

    raw_uncol = False
    if triads:
        raw_uncol = sat_uncolorable(len(rays), pairs, triads)

    comp_uncol = False
    if use_completion and not raw_uncol:
        comp_rays = hermitian_completion(rays, max_iter=5)
        if len(comp_rays) > max_rays:
            print(f"  {name}: {n_raw}r/{n_triads_raw}t -> completion {len(comp_rays)}r (too large, skipping)")
            return {'name': name, 'uncol': False, 'min_size': None, 'rays': n_raw}
        comp_pairs, comp_triads = build_pairs_triads(comp_rays)
        if comp_triads:
            comp_uncol = sat_uncolorable(len(comp_rays), comp_pairs, comp_triads)
        if comp_uncol:
            rays, pairs, triads = comp_rays, comp_pairs, comp_triads

    uncol = raw_uncol or comp_uncol
    min_size = None
    min_sizes = {}
    n_bases = 0

    if uncol:
        subset, min_size, min_sizes = sat_minimize(rays, pairs, triads, n_trials=n_trials)
        s = set(subset)
        remap = {old: new for new, old in enumerate(sorted(subset))}
        min_triads = [(remap[a], remap[b], remap[c])
                      for a, b, c in triads if a in s and b in s and c in s]
        n_bases = len(min_triads)

    status = "UNCOLORABLE" if uncol else "colorable"
    comp_str = ""
    min_str = f" -> MIN {min_size} ({n_bases} bases)" if min_size else ""
    print(f"  {name}: {n_raw}r/{n_triads_raw}t = {status}{min_str}")
    if min_sizes and uncol:
        top3 = sorted(min_sizes.items())[:3]
        print(f"    Size distribution: {dict(top3)}")

    return {'name': name, 'uncol': uncol, 'min_size': min_size, 'n_bases': n_bases,
            'rays': n_raw, 'size_dist': min_sizes}


# =====================================================================
# PART 1: Complete what crashed
# =====================================================================

def complete_remaining():
    """Finish the runs that the previous session didn't complete."""
    print("\n" + "=" * 70)
    print("COMPLETING PREVIOUS SESSION")
    print("=" * 70)

    results = []

    # Z[phi] extended: {0, +/-1, +/-phi, +/-phi^2, +/-(phi-1)}
    phi2 = phi**2
    alph = [0, 1, -1, phi, -phi, phi2, -phi2, phi-1, -(phi-1)]
    r = test_alphabet("Z[phi] extended +{phi^2,phi-1}", alph, n_trials=300)
    results.append(r)

    # Integer with 1/2: {0, +/-1, +/-2, +/-1/2}
    alph = [0, 1, -1, 2, -2, 0.5, -0.5]
    r = test_alphabet("Z[1/2] {0,+/-1,+/-2,+/-1/2}", alph, n_trials=500)
    results.append(r)

    return results


# =====================================================================
# PART 2: Targeted sub-31 search
# =====================================================================

def probe_sub31():
    """Targeted experiments specifically looking for KS sets with < 31 vectors."""
    print("\n" + "=" * 70)
    print("PROBING FOR SUB-31 KS SETS")
    print("=" * 70)

    results = []

    # Idea 1: Dense integer alphabet {0, +/-1, +/-2, +/-3, +/-4}
    # More generators = more orthogonalities = more constraint
    alph = [0, 1, -1, 2, -2, 3, -3, 4, -4]
    r = test_alphabet("Z dense {0..+/-4}", alph, n_trials=500)
    results.append(r)

    # Idea 2: Rational points -- {0, +/-1, +/-2, +/-1/2, +/-3/2}
    alph = [0, 1, -1, 2, -2, 0.5, -0.5, 1.5, -1.5]
    r = test_alphabet("Q dense {1,2,1/2,3/2}", alph, n_trials=500)
    results.append(r)

    # Idea 3: Peres-like with sqrt2+1 (the silver ratio)
    silver = 1 + sqrt2
    alph = [0, 1, -1, sqrt2, -sqrt2, silver, -silver]
    r = test_alphabet("Silver ratio {1,sqrt2,1+sqrt2}", alph, n_trials=500)
    results.append(r)

    # Idea 4: Complex integer (Gaussian) with small generators
    # {0, +/-1, +/-i, +/-(1+i), +/-(1-i)}
    alph = [0, 1, -1, 1j, -1j, 1+1j, -(1+1j), 1-1j, -(1-1j)]
    r = test_alphabet("Gaussian Z[i] {1,i,1+i,1-i}", alph, n_trials=500)
    results.append(r)

    # Idea 5: Roots of unity -- 4th roots
    w4 = cmath.exp(2j * cmath.pi / 4)  # = i
    alph = [0, 1, -1, w4, -w4]  # = {0, +/-1, +/-i}
    r = test_alphabet("4th roots of unity", alph, n_trials=300)
    results.append(r)

    # Idea 6: Roots of unity -- 6th roots
    w6 = cmath.exp(2j * cmath.pi / 6)
    alph = [0, 1, -1, w6, -w6, w6**2, -(w6**2)]
    r = test_alphabet("6th roots of unity", alph, n_trials=300)
    results.append(r)

    # Idea 7: Roots of unity -- 8th roots
    w8 = cmath.exp(2j * cmath.pi / 8)
    alph = [0, 1, -1, w8, -w8, w8**2, -(w8**2), w8**3, -(w8**3)]
    r = test_alphabet("8th roots of unity", alph, n_trials=300)
    results.append(r)

    # Idea 8: Mixed norm-2 generators from DIFFERENT fields
    # Combine the best cancellation identities: 1+1=2, sqrt2^2=2, |omega|=1
    # This mixes integer+Peres+Eisenstein cancellations
    alph = [0, 1, -1, 2, -2, sqrt2, -sqrt2, OMEGA, -OMEGA, OMEGA.conjugate(), -OMEGA.conjugate()]
    r = test_alphabet("Triple norm-2 {2,sqrt2,w,wbar}", alph, n_trials=500)
    results.append(r)

    # Idea 9: sqrt(3) field -- norm 3, should be dead per thesis, but let's confirm
    alph = [0, 1, -1, sqrt3, -sqrt3]
    r = test_alphabet("Q(sqrt3) basic", alph, n_trials=300)
    results.append(r)

    # Idea 10: Algebraic number with norm exactly 2 that we haven't tried
    # 2*cos(pi/5) = phi (already done). Try 2*cos(pi/7)
    cos_pi7 = 2 * np.cos(np.pi / 7)  # ~ 1.802
    alph = [0, 1, -1, cos_pi7, -cos_pi7]
    r = test_alphabet(f"2cos(pi/7)={cos_pi7:.3f}", alph, n_trials=300)
    results.append(r)

    # Idea 11: 2*cos(pi/9) ~ 1.879
    cos_pi9 = 2 * np.cos(np.pi / 9)
    alph = [0, 1, -1, cos_pi9, -cos_pi9]
    r = test_alphabet(f"2cos(pi/9)={cos_pi9:.3f}", alph, n_trials=300)
    results.append(r)

    # Idea 12: sqrt(2) + Gaussian -- combine Peres with complex
    alph = [0, 1, -1, sqrt2, -sqrt2, 1j, -1j, sqrt2*1j, -sqrt2*1j]
    r = test_alphabet("Peres+Gaussian {sqrt2,i,sqrt2*i}", alph, n_trials=300)
    results.append(r)

    return results


# =====================================================================
# PART 3: Group constructions (from crashed session)
# =====================================================================

def explore_groups():
    """Finite group orbits in C^3."""
    print("\n" + "=" * 70)
    print("GROUP CONSTRUCTIONS")
    print("=" * 70)

    results = []

    # Weyl-Heisenberg group on C^3
    X = np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]], dtype=complex)
    Z = np.diag([1, OMEGA, OMEGA**2])

    WH_group = []
    for a in range(3):
        for b in range(3):
            M = np.linalg.matrix_power(X, a) @ np.linalg.matrix_power(Z, b)
            WH_group.append(M)

    seeds = [
        np.array([1, 0, 0], dtype=complex),
        np.array([1, 1, 1], dtype=complex) / np.sqrt(3),
        np.array([1, 1, -1], dtype=complex) / np.sqrt(3),
        np.array([1, OMEGA, OMEGA**2], dtype=complex) / np.sqrt(3),
    ]

    all_rays = set()
    all_rays_list = []
    for seed in seeds:
        for M in WH_group:
            v = M @ seed
            canon = canonicalize_complex_ray(list(v))
            if canon and canon not in all_rays:
                all_rays.add(canon)
                all_rays_list.append(tuple(v))

    print(f"  WH group orbits of 4 seeds: {len(all_rays_list)} rays")
    pairs, triads = build_pairs_triads(all_rays_list)
    print(f"    {len(triads)} triads")
    if triads:
        uncol = sat_uncolorable(len(all_rays_list), pairs, triads)
        if uncol:
            subset, min_size, sizes = sat_minimize(all_rays_list, pairs, triads, n_trials=500)
            s = set(subset)
            remap = {old: new for new, old in enumerate(sorted(subset))}
            mt = [(remap[a], remap[b], remap[c]) for a, b, c in triads if a in s and b in s and c in s]
            print(f"    UNCOLORABLE -> MIN {min_size} ({len(mt)} bases)")
            print(f"    Sizes: {dict(sorted(sizes.items())[:5])}")
            results.append({'name': 'WH group', 'uncol': True, 'min_size': min_size})
        else:
            print(f"    Colorable")
            results.append({'name': 'WH group', 'uncol': False, 'min_size': None})

    # Tetrahedral (A4) - 12 elements
    print(f"\n  Tetrahedral (A4) group:")
    diags = [
        np.array([1, 1, 1]) / np.sqrt(3),
        np.array([1, -1, -1]) / np.sqrt(3),
        np.array([-1, 1, -1]) / np.sqrt(3),
        np.array([-1, -1, 1]) / np.sqrt(3),
    ]

    def rotation_matrix(axis, angle):
        c, s = np.cos(angle), np.sin(angle)
        ax = axis / np.linalg.norm(axis)
        K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
        return np.eye(3) + s * K + (1 - c) * (K @ K)

    A4_group = [np.eye(3)]
    for d in diags:
        A4_group.append(rotation_matrix(d, 2*np.pi/3))
        A4_group.append(rotation_matrix(d, 4*np.pi/3))
    for i in range(3):
        ax = np.zeros(3); ax[i] = 1.0
        A4_group.append(rotation_matrix(ax, np.pi))

    real_seeds = [
        np.array([1, 0, 0], dtype=float),
        np.array([1, 1, 0], dtype=float) / np.sqrt(2),
        np.array([1, 1, 1], dtype=float) / np.sqrt(3),
        np.array([2, 1, 0], dtype=float) / np.sqrt(5),
        np.array([1, 2, 0], dtype=float) / np.sqrt(5),
        np.array([2, 1, 1], dtype=float) / np.sqrt(6),
    ]

    all_rays = set()
    all_rays_list = []
    for seed in real_seeds:
        for M in A4_group:
            v = M @ seed
            canon = canonicalize_complex_ray(list(v))
            if canon and canon not in all_rays:
                all_rays.add(canon)
                all_rays_list.append(tuple(complex(x) for x in v))

    print(f"    A4 orbits of {len(real_seeds)} seeds: {len(all_rays_list)} rays")
    pairs, triads = build_pairs_triads(all_rays_list)
    print(f"    {len(triads)} triads")
    if triads:
        uncol = sat_uncolorable(len(all_rays_list), pairs, triads)
        if uncol:
            subset, min_size, sizes = sat_minimize(all_rays_list, pairs, triads, n_trials=500)
            s = set(subset)
            remap = {old: new for new, old in enumerate(sorted(subset))}
            mt = [(remap[a], remap[b], remap[c]) for a, b, c in triads if a in s and b in s and c in s]
            print(f"    UNCOLORABLE -> MIN {min_size} ({len(mt)} bases)")
            print(f"    Sizes: {dict(sorted(sizes.items())[:5])}")
            results.append({'name': 'A4 group', 'uncol': True, 'min_size': min_size})
        else:
            print(f"    Colorable")
            results.append({'name': 'A4 group', 'uncol': False, 'min_size': None})

    # Octahedral (S4) - 24 elements
    print(f"\n  Octahedral (S4) group:")
    S4_group = []
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product([1, -1], repeat=3):
            M = np.zeros((3, 3))
            for i in range(3):
                M[i, perm[i]] = signs[i]
            if abs(np.linalg.det(M) - 1.0) < 1e-10:
                S4_group.append(M)

    all_rays = set()
    all_rays_list = []
    for seed in real_seeds:
        for M in S4_group:
            v = M @ seed
            canon = canonicalize_complex_ray(list(v))
            if canon and canon not in all_rays:
                all_rays.add(canon)
                all_rays_list.append(tuple(complex(x) for x in v))

    print(f"    S4 orbits of {len(real_seeds)} seeds: {len(all_rays_list)} rays")
    pairs, triads = build_pairs_triads(all_rays_list)
    print(f"    {len(triads)} triads")
    if triads:
        uncol = sat_uncolorable(len(all_rays_list), pairs, triads)
        if uncol:
            subset, min_size, sizes = sat_minimize(all_rays_list, pairs, triads, n_trials=500)
            s = set(subset)
            remap = {old: new for new, old in enumerate(sorted(subset))}
            mt = [(remap[a], remap[b], remap[c]) for a, b, c in triads if a in s and b in s and c in s]
            print(f"    UNCOLORABLE -> MIN {min_size} ({len(mt)} bases)")
            print(f"    Sizes: {dict(sorted(sizes.items())[:5])}")
            results.append({'name': 'S4 group', 'uncol': True, 'min_size': min_size})
        else:
            print(f"    Colorable")
            results.append({'name': 'S4 group', 'uncol': False, 'min_size': None})

    # Icosahedral (A5) - 60 elements
    print(f"\n  Icosahedral (A5) group:")
    # Build from icosahedron vertices
    A5_group = [np.eye(3)]
    # 5-fold axes through opposite vertices of icosahedron
    icos_verts = []
    for s1 in [1, -1]:
        for s2 in [1, -1]:
            icos_verts.append(np.array([0, s1, s2*phi]))
            icos_verts.append(np.array([s1, s2*phi, 0]))
            icos_verts.append(np.array([s2*phi, 0, s1]))
    # Normalize
    icos_verts = [v / np.linalg.norm(v) for v in icos_verts]

    # 5-fold axes (6 pairs of opposite vertices)
    five_fold_axes = []
    used = set()
    for i, v in enumerate(icos_verts):
        if i not in used:
            for j in range(i+1, len(icos_verts)):
                if np.allclose(v, -icos_verts[j]):
                    five_fold_axes.append(v)
                    used.add(i)
                    used.add(j)
                    break

    for ax in five_fold_axes:
        for k in [1, 2, 3, 4]:
            A5_group.append(rotation_matrix(ax, 2*np.pi*k/5))

    # 3-fold axes (10 pairs of opposite face centers)
    # Face centers of icosahedron
    face_axes = [
        np.array([1, 1, 1]) / np.sqrt(3),
        np.array([1, 1, -1]) / np.sqrt(3),
        np.array([1, -1, 1]) / np.sqrt(3),
        np.array([1, -1, -1]) / np.sqrt(3),
        np.array([-1, 1, 1]) / np.sqrt(3),
    ]
    # Additional face centers involving phi
    for s in [1, -1]:
        face_axes.append(np.array([0, 1/phi, phi]) * s / np.sqrt(1 + 1/phi**2 + phi**2))
        face_axes.append(np.array([1/phi, phi, 0]) * s / np.sqrt(1 + 1/phi**2 + phi**2))
        face_axes.append(np.array([phi, 0, 1/phi]) * s / np.sqrt(1 + 1/phi**2 + phi**2))

    for ax in face_axes:
        ax_n = ax / np.linalg.norm(ax)
        for k in [1, 2]:
            A5_group.append(rotation_matrix(ax_n, 2*np.pi*k/3))

    # 2-fold axes (15 edge midpoints)
    edge_axes = []
    for i in range(len(icos_verts)):
        for j in range(i+1, len(icos_verts)):
            d = np.linalg.norm(icos_verts[i] - icos_verts[j])
            if abs(d - 2/np.sqrt(1+phi**2)) < 0.3:  # adjacent vertices
                mid = icos_verts[i] + icos_verts[j]
                if np.linalg.norm(mid) > 0.1:
                    edge_axes.append(mid / np.linalg.norm(mid))

    for ax in edge_axes[:15]:
        A5_group.append(rotation_matrix(ax, np.pi))

    # Deduplicate group elements
    unique_group = []
    for M in A5_group:
        is_dup = False
        for U in unique_group:
            if np.allclose(M, U, atol=1e-10):
                is_dup = True
                break
        if not is_dup:
            unique_group.append(M)

    print(f"    A5 group size: {len(unique_group)} elements")

    all_rays = set()
    all_rays_list = []
    ico_seeds = [
        np.array([1, 0, 0], dtype=float),
        np.array([1, phi, 0], dtype=float) / np.sqrt(1 + phi**2),
        np.array([1, 1, 1], dtype=float) / np.sqrt(3),
    ]

    for seed in ico_seeds:
        for M in unique_group:
            v = M @ seed
            canon = canonicalize_complex_ray(list(v))
            if canon and canon not in all_rays:
                all_rays.add(canon)
                all_rays_list.append(tuple(complex(x) for x in v))

    print(f"    A5 orbits of {len(ico_seeds)} seeds: {len(all_rays_list)} rays")
    pairs, triads = build_pairs_triads(all_rays_list)
    print(f"    {len(triads)} triads")
    if triads:
        uncol = sat_uncolorable(len(all_rays_list), pairs, triads)
        if uncol:
            subset, min_size, sizes = sat_minimize(all_rays_list, pairs, triads, n_trials=500)
            s = set(subset)
            remap = {old: new for new, old in enumerate(sorted(subset))}
            mt = [(remap[a], remap[b], remap[c]) for a, b, c in triads if a in s and b in s and c in s]
            print(f"    UNCOLORABLE -> MIN {min_size} ({len(mt)} bases)")
            print(f"    Sizes: {dict(sorted(sizes.items())[:5])}")
            results.append({'name': 'A5 icosahedral', 'uncol': True, 'min_size': min_size})
        else:
            print(f"    Colorable")
            results.append({'name': 'A5 icosahedral', 'uncol': False, 'min_size': None})
    else:
        print(f"    No triads found")
        results.append({'name': 'A5 icosahedral', 'uncol': False, 'min_size': None})

    return results


# =====================================================================
# MAIN
# =====================================================================

if __name__ == "__main__":
    print("KS Exploration Part 2 -- Continuing from crashed session")
    print("=" * 70)

    all_results = []

    # Part 1: Complete what didn't run
    r1 = complete_remaining()
    all_results.extend(r1)

    # Part 2: Targeted sub-31 probes
    r2 = probe_sub31()
    all_results.extend(r2)

    # Part 3: Group constructions
    r3 = explore_groups()
    all_results.extend(r3)

    # Summary
    print("\n" + "=" * 70)
    print("FULL SUMMARY -- All uncolorable configurations")
    print("=" * 70)

    # Include results from session 1
    print("\n  From session 1:")
    print("    Q(cbrt(2)) extended: MIN 60 (28 bases)")
    print("    Z extended {0,+/-1,+/-2,+/-3}: MIN 31")
    print("    Z[sqrt2] extended +{1+sqrt2,2}: MIN 31 (17 bases)")
    print("    Z[w] extended +{2,2w,2wbar}: MIN 44 (23 bases)")

    print("\n  From session 2:")
    uncol_results = [r for r in all_results if r.get('uncol')]
    for r in uncol_results:
        min_str = f"MIN {r['min_size']}" if r.get('min_size') else "?"
        bases_str = f" ({r.get('n_bases', '?')} bases)" if r.get('n_bases') else ""
        print(f"    {r['name']}: {min_str}{bases_str}")

    if uncol_results:
        best = min(uncol_results, key=lambda x: x.get('min_size', 999))
        print(f"\n  SESSION 2 BEST: {best['name']} with {best.get('min_size')} vectors")
        if best.get('min_size') and best['min_size'] < 31:
            print(f"  *** BREAKTHROUGH: Below CK-31! ***")
        elif best.get('min_size') == 31:
            print(f"  Matches CK-31 minimum")
    else:
        print("\n  No new uncolorable configurations found.")

    print("\n  Open question: Can any algebraic construction beat 31 in dim 3?")
    print("  The 24-31 gap remains the deepest mystery.")
