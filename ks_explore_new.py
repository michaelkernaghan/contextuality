"""
ks_explore_new.py — Explore unexplored algebraic directions for KS sets
========================================================================

Directions:
1. Cubic fields: Q(∛2), Q(∛3), etc.
2. Mixed-field alphabets: combining elements from different quadratic fields
3. Larger alphabets within known fields
4. Group constructions: finite subgroups of SU(3)

Uses infrastructure from ks_new_islands.py and ks_sat.py.
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


def test_alphabet(name, alphabet, use_completion=True, n_trials=500):
    """Test an alphabet for KS-uncolorability. Returns summary dict."""
    rays = generate_rays_from_alphabet(alphabet)
    pairs, triads = build_pairs_triads(rays)
    n_raw = len(rays)
    n_triads_raw = len(triads)

    # Check raw uncolorability
    raw_uncol = False
    if triads:
        raw_uncol = sat_uncolorable(len(rays), pairs, triads)

    # Try completion
    comp_uncol = False
    comp_rays = rays
    comp_triads = triads
    comp_pairs = pairs
    n_comp = n_raw
    n_triads_comp = n_triads_raw
    min_size = None
    min_sizes = {}

    if use_completion and not raw_uncol:
        comp_rays = hermitian_completion(rays, max_iter=5)
        n_comp = len(comp_rays)
        comp_pairs, comp_triads = build_pairs_triads(comp_rays)
        n_triads_comp = len(comp_triads)
        if comp_triads:
            comp_uncol = sat_uncolorable(len(comp_rays), comp_pairs, comp_triads)

    uncol = raw_uncol or comp_uncol
    source_rays = rays if raw_uncol else comp_rays
    source_pairs = pairs if raw_uncol else comp_pairs
    source_triads = triads if raw_uncol else comp_triads

    if uncol:
        subset, min_size, min_sizes = sat_minimize(
            source_rays, source_pairs, source_triads, n_trials=n_trials
        )
        # Count bases in minimal set
        s = set(subset)
        remap = {old: new for new, old in enumerate(sorted(subset))}
        min_triads = [(remap[a], remap[b], remap[c])
                      for a, b, c in source_triads
                      if a in s and b in s and c in s]
        n_bases = len(min_triads)
    else:
        n_bases = 0

    result = {
        'name': name,
        'alphabet_size': len(alphabet),
        'rays_raw': n_raw,
        'triads_raw': n_triads_raw,
        'rays_comp': n_comp,
        'triads_comp': n_triads_comp,
        'raw_uncol': raw_uncol,
        'comp_uncol': comp_uncol,
        'uncol': uncol,
        'min_size': min_size,
        'n_bases': n_bases,
        'size_dist': min_sizes,
    }

    status = "UNCOLORABLE" if uncol else "colorable"
    comp_str = f" (comp: {n_comp}r/{n_triads_comp}t)" if n_comp != n_raw else ""
    min_str = f" -> MIN {min_size} ({n_bases} bases)" if min_size else ""
    print(f"  {name}: {n_raw}r/{n_triads_raw}t{comp_str} = {status}{min_str}")
    if min_sizes and uncol:
        top3 = sorted(min_sizes.items())[:3]
        print(f"    Size distribution: {dict(top3)}")

    return result


def explore_cubic_fields():
    """Test cubic extensions Q(∛d) for small d."""
    print("\n" + "=" * 70)
    print("CUBIC FIELDS")
    print("=" * 70)

    results = []
    for d in [2, 3, 4, 5, 6, 7]:
        cbrt_d = d ** (1/3)
        norm_sq = cbrt_d ** 2

        # Basic alphabet: {0, ±1, ±∛d}
        alph = [0, 1, -1, cbrt_d, -cbrt_d]
        name = f"Q(cbrt({d})) basic |a|^2={norm_sq:.3f}"
        r = test_alphabet(name, alph, use_completion=True, n_trials=300)
        results.append(r)

        # Extended: add ∛(d²) = (∛d)²
        cbrt_d2 = d ** (2/3)
        alph_ext = [0, 1, -1, cbrt_d, -cbrt_d, cbrt_d2, -cbrt_d2]
        name_ext = f"Q(cbrt({d})) extended +cbrt({d})^2"
        r2 = test_alphabet(name_ext, alph_ext, use_completion=True, n_trials=300)
        results.append(r2)

    return results


def explore_mixed_alphabets():
    """Test alphabets mixing elements from different fields."""
    print("\n" + "=" * 70)
    print("MIXED-FIELD ALPHABETS")
    print("=" * 70)

    sqrt2 = np.sqrt(2)
    sqrt3 = np.sqrt(3)
    phi = (1 + np.sqrt(5)) / 2

    results = []

    # Peres + Eisenstein: {0, ±1, ±sqrt2, ±w, ±wbar}
    alph = [0, 1, -1, sqrt2, -sqrt2, OMEGA, -OMEGA, OMEGA.conjugate(), -OMEGA.conjugate()]
    r = test_alphabet("Peres+Eisenstein {sqrt2,w}", alph, n_trials=300)
    results.append(r)

    # Integer + Eisenstein: {0, ±1, ±2, ±w, ±wbar}
    alph = [0, 1, -1, 2, -2, OMEGA, -OMEGA, OMEGA.conjugate(), -OMEGA.conjugate()]
    r = test_alphabet("Integer+Eisenstein {2,w}", alph, n_trials=300)
    results.append(r)

    # Peres + Golden: {0, ±1, ±sqrt2, ±phi}
    alph = [0, 1, -1, sqrt2, -sqrt2, phi, -phi]
    r = test_alphabet("Peres+Golden {sqrt2,phi}", alph, n_trials=300)
    results.append(r)

    # Integer + Golden: {0, ±1, ±2, ±phi}
    alph = [0, 1, -1, 2, -2, phi, -phi]
    r = test_alphabet("Integer+Golden {2,phi}", alph, n_trials=500)
    results.append(r)

    # Eisenstein + Golden: {0, ±1, ±w, ±wbar, ±phi}
    alph = [0, 1, -1, OMEGA, -OMEGA, OMEGA.conjugate(), -OMEGA.conjugate(), phi, -phi]
    r = test_alphabet("Eisenstein+Golden {w,phi}", alph, n_trials=300)
    results.append(r)

    # Triple mix: {0, ±1, ±sqrt2, ±w, ±wbar, ±phi}
    alph = [0, 1, -1, sqrt2, -sqrt2, OMEGA, -OMEGA,
            OMEGA.conjugate(), -OMEGA.conjugate(), phi, -phi]
    r = test_alphabet("Triple {sqrt2,w,phi}", alph, n_trials=300)
    results.append(r)

    # Integer + sqrt3: {0, ±1, ±2, ±sqrt3}
    alph = [0, 1, -1, 2, -2, sqrt3, -sqrt3]
    r = test_alphabet("Integer+sqrt3 {2,sqrt3}", alph, n_trials=300)
    results.append(r)

    return results


def explore_larger_alphabets():
    """Test larger alphabets within known fields."""
    print("\n" + "=" * 70)
    print("LARGER ALPHABETS IN KNOWN FIELDS")
    print("=" * 70)

    sqrt2 = np.sqrt(2)
    phi = (1 + np.sqrt(5)) / 2

    results = []

    # Extended integer: {0, ±1, ±2, ±3}
    alph = [0, 1, -1, 2, -2, 3, -3]
    r = test_alphabet("Z extended {0,±1,±2,±3}", alph, n_trials=500)
    results.append(r)

    # Z[sqrt2] extended: {0, ±1, ±sqrt2, ±(1+sqrt2), ±2}
    alph = [0, 1, -1, sqrt2, -sqrt2, 1+sqrt2, -(1+sqrt2), 2, -2]
    r = test_alphabet("Z[sqrt2] extended +{1+sqrt2,2}", alph, n_trials=500)
    results.append(r)

    # Eisenstein extended: {0, ±1, ±w, ±wbar, ±2, ±2w, ±2wbar}
    alph = [0, 1, -1, OMEGA, -OMEGA, OMEGA.conjugate(), -OMEGA.conjugate(),
            2, -2, 2*OMEGA, -2*OMEGA, 2*OMEGA.conjugate(), -2*OMEGA.conjugate()]
    r = test_alphabet("Z[w] extended +{2,2w,2wbar}", alph, n_trials=500)
    results.append(r)

    # Z[phi] extended: {0, ±1, ±phi, ±phi², ±(phi-1)}
    phi2 = phi**2  # = phi + 1
    alph = [0, 1, -1, phi, -phi, phi2, -phi2, phi-1, -(phi-1)]
    r = test_alphabet("Z[phi] extended +{phi²,phi-1}", alph, n_trials=300)
    results.append(r)

    # Integer with 1/2: {0, ±1, ±2, ±1/2}
    alph = [0, 1, -1, 2, -2, 0.5, -0.5]
    r = test_alphabet("Z[1/2] {0,±1,±2,±1/2}", alph, n_trials=500)
    results.append(r)

    return results


def explore_group_constructions():
    """Test KS sets from finite group orbits in C³."""
    print("\n" + "=" * 70)
    print("GROUP CONSTRUCTIONS")
    print("=" * 70)

    results = []

    # Weyl-Heisenberg group on C³
    # X = cyclic permutation, Z = phase gate with w
    X = np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]], dtype=complex)
    Z = np.diag([1, OMEGA, OMEGA**2])

    # Generate all group elements X^a Z^b for a,b in {0,1,2}
    WH_group = []
    for a in range(3):
        for b in range(3):
            M = np.linalg.matrix_power(X, a) @ np.linalg.matrix_power(Z, b)
            WH_group.append(M)

    # Seed vectors and generate orbits
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
            subset, min_size, sizes = sat_minimize(
                all_rays_list, pairs, triads, n_trials=500)
            s = set(subset)
            remap = {old: new for new, old in enumerate(sorted(subset))}
            min_triads = [(remap[a], remap[b], remap[c])
                          for a, b, c in triads if a in s and b in s and c in s]
            print(f"    UNCOLORABLE -> MIN {min_size} ({len(min_triads)} bases)")
            print(f"    Sizes: {dict(sorted(sizes.items())[:5])}")
        else:
            print(f"    Colorable")

    # Tetrahedral group (A4) acting on R³
    # 12 elements: identity, 8 rotations by 120°/240° about body diagonals,
    # 3 rotations by 180° about coordinate axes
    print(f"\n  Tetrahedral (A4) group:")
    # Body diagonal axes
    diags = [
        np.array([1, 1, 1]) / np.sqrt(3),
        np.array([1, -1, -1]) / np.sqrt(3),
        np.array([-1, 1, -1]) / np.sqrt(3),
        np.array([-1, -1, 1]) / np.sqrt(3),
    ]

    def rotation_matrix(axis, angle):
        """Rodrigues' rotation formula."""
        c, s = np.cos(angle), np.sin(angle)
        ax = axis / np.linalg.norm(axis)
        K = np.array([[0, -ax[2], ax[1]],
                      [ax[2], 0, -ax[0]],
                      [-ax[1], ax[0], 0]])
        return np.eye(3) + s * K + (1 - c) * (K @ K)

    A4_group = [np.eye(3)]
    for d in diags:
        A4_group.append(rotation_matrix(d, 2*np.pi/3))
        A4_group.append(rotation_matrix(d, 4*np.pi/3))
    # 180° rotations about coordinate axes
    for i in range(3):
        ax = np.zeros(3)
        ax[i] = 1.0
        A4_group.append(rotation_matrix(ax, np.pi))

    # Seeds: try various starting vectors
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
            subset, min_size, sizes = sat_minimize(
                all_rays_list, pairs, triads, n_trials=500)
            s = set(subset)
            remap = {old: new for new, old in enumerate(sorted(subset))}
            min_triads_set = [(remap[a], remap[b], remap[c])
                              for a, b, c in triads if a in s and b in s and c in s]
            print(f"    UNCOLORABLE -> MIN {min_size} ({len(min_triads_set)} bases)")
            print(f"    Sizes: {dict(sorted(sizes.items())[:5])}")
        else:
            print(f"    Colorable")

    # Octahedral group (S4) - 24 elements
    print(f"\n  Octahedral (S4) group:")
    S4_group = []
    # All signed permutations with even number of sign changes
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
            subset, min_size, sizes = sat_minimize(
                all_rays_list, pairs, triads, n_trials=500)
            s = set(subset)
            remap = {old: new for new, old in enumerate(sorted(subset))}
            min_triads_set = [(remap[a], remap[b], remap[c])
                              for a, b, c in triads if a in s and b in s and c in s]
            print(f"    UNCOLORABLE -> MIN {min_size} ({len(min_triads_set)} bases)")
            print(f"    Sizes: {dict(sorted(sizes.items())[:5])}")
        else:
            print(f"    Colorable")

    return results


if __name__ == "__main__":
    print("KS Set Exploration — Unexplored Algebraic Directions")
    print("=" * 70)

    all_results = []

    r1 = explore_cubic_fields()
    all_results.extend(r1)

    r2 = explore_mixed_alphabets()
    all_results.extend(r2)

    r3 = explore_larger_alphabets()
    all_results.extend(r3)

    explore_group_constructions()

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY — Uncolorable configurations found:")
    print("=" * 70)
    for r in all_results:
        if r['uncol']:
            src = "raw" if r['raw_uncol'] else "completion"
            print(f"  {r['name']}: MIN {r['min_size']} ({r['n_bases']} bases) [{src}]")

    uncol_results = [r for r in all_results if r['uncol']]
    if uncol_results:
        best = min(uncol_results, key=lambda x: x['min_size'])
        print(f"\n  BEST: {best['name']} with {best['min_size']} vectors")
        if best['min_size'] < 31:
            print(f"  *** BREAKTHROUGH: Below CK-31! ***")
        elif best['min_size'] == 31:
            print(f"  Matches CK-31 minimum")
        else:
            print(f"  Above CK-31 minimum (31)")
    else:
        print("  No uncolorable configurations found in new directions.")
