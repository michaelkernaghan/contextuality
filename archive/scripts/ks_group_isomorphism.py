"""
ks_group_isomorphism.py -- Check if A4/S4 group KS sets are isomorphic to CK-31
================================================================================

The exploration found that tetrahedral (A4) and octahedral (S4) group orbits
both produce MIN 31 KS sets with 17 bases. Are these the same graph as CK-31?
"""

import numpy as np
import cmath
import random
import itertools

from ks_sat import is_uncolorable as sat_uncolorable
from ks_complex import canonicalize_complex_ray, hermitian_dot
from ks_new_islands import generate_rays_from_alphabet, sat_minimize
from ks_new_island_analysis import build_pairs_triads
from ks_graph_analysis import graph_invariants, refined_isomorphism_test

random.seed(42)
np.random.seed(42)

OMEGA = cmath.exp(2j * cmath.pi / 3)


def rotation_matrix(axis, angle):
    c, s = np.cos(angle), np.sin(angle)
    ax = axis / np.linalg.norm(axis)
    K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
    return np.eye(3) + s * K + (1 - c) * (K @ K)


def extract_minimal_set(rays, pairs, triads, n_trials=1000):
    """Extract a minimal KS subset and return its rays, pairs, triads."""
    subset_indices, min_size, sizes = sat_minimize(rays, pairs, triads, n_trials=n_trials)
    s = set(subset_indices)
    sub_rays = [rays[i] for i in sorted(subset_indices)]

    # Rebuild pairs and triads for the subset
    sub_pairs, sub_triads = build_pairs_triads(sub_rays)
    return sub_rays, sub_pairs, sub_triads, min_size, sizes


# =====================================================================
# Build CK-31 (integer alphabet)
# =====================================================================
print("=" * 70)
print("Building CK-31 (integer alphabet)")
print("=" * 70)

alph_int = [0, 1, -1, 2, -2]
rays_int = generate_rays_from_alphabet(alph_int)
pairs_int, triads_int = build_pairs_triads(rays_int)
print(f"  Integer pool: {len(rays_int)} rays, {len(triads_int)} triads")

ck31_rays, ck31_pairs, ck31_triads, ck31_size, ck31_sizes = extract_minimal_set(
    rays_int, pairs_int, triads_int, n_trials=1000)
print(f"  CK-31 minimal: {ck31_size} rays, {len(ck31_triads)} bases")
print(f"  Size distribution (top 5): {dict(sorted(ck31_sizes.items())[:5])}")

ck31_inv = graph_invariants(ck31_size, ck31_pairs)
print(f"  Graph invariants: edges={ck31_inv['edges']}, triangles={ck31_inv['triangles']}")
print(f"  Degree sequence: {ck31_inv['degree_seq']}")


# =====================================================================
# Build A4 group KS set
# =====================================================================
print("\n" + "=" * 70)
print("Building A4 (tetrahedral) group KS set")
print("=" * 70)

diags = [
    np.array([1, 1, 1]) / np.sqrt(3),
    np.array([1, -1, -1]) / np.sqrt(3),
    np.array([-1, 1, -1]) / np.sqrt(3),
    np.array([-1, -1, 1]) / np.sqrt(3),
]

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

all_rays_set = set()
a4_rays = []
for seed in real_seeds:
    for M in A4_group:
        v = M @ seed
        canon = canonicalize_complex_ray(list(v))
        if canon and canon not in all_rays_set:
            all_rays_set.add(canon)
            a4_rays.append(tuple(complex(x) for x in v))

a4_pairs, a4_triads = build_pairs_triads(a4_rays)
print(f"  A4 pool: {len(a4_rays)} rays, {len(a4_triads)} triads")

a4_min_rays, a4_min_pairs, a4_min_triads, a4_size, a4_sizes = extract_minimal_set(
    a4_rays, a4_pairs, a4_triads, n_trials=1000)
print(f"  A4 minimal: {a4_size} rays, {len(a4_min_triads)} bases")
print(f"  Size distribution (top 5): {dict(sorted(a4_sizes.items())[:5])}")

a4_inv = graph_invariants(a4_size, a4_min_pairs)
print(f"  Graph invariants: edges={a4_inv['edges']}, triangles={a4_inv['triangles']}")
print(f"  Degree sequence: {a4_inv['degree_seq']}")


# =====================================================================
# Build S4 group KS set
# =====================================================================
print("\n" + "=" * 70)
print("Building S4 (octahedral) group KS set")
print("=" * 70)

S4_group = []
for perm in itertools.permutations(range(3)):
    for signs in itertools.product([1, -1], repeat=3):
        M = np.zeros((3, 3))
        for i in range(3):
            M[i, perm[i]] = signs[i]
        if abs(np.linalg.det(M) - 1.0) < 1e-10:
            S4_group.append(M)

all_rays_set = set()
s4_rays = []
for seed in real_seeds:
    for M in S4_group:
        v = M @ seed
        canon = canonicalize_complex_ray(list(v))
        if canon and canon not in all_rays_set:
            all_rays_set.add(canon)
            s4_rays.append(tuple(complex(x) for x in v))

s4_pairs, s4_triads = build_pairs_triads(s4_rays)
print(f"  S4 pool: {len(s4_rays)} rays, {len(s4_triads)} triads")

s4_min_rays, s4_min_pairs, s4_min_triads, s4_size, s4_sizes = extract_minimal_set(
    s4_rays, s4_pairs, s4_triads, n_trials=1000)
print(f"  S4 minimal: {s4_size} rays, {len(s4_min_triads)} bases")
print(f"  Size distribution (top 5): {dict(sorted(s4_sizes.items())[:5])}")

s4_inv = graph_invariants(s4_size, s4_min_pairs)
print(f"  Graph invariants: edges={s4_inv['edges']}, triangles={s4_inv['triangles']}")
print(f"  Degree sequence: {s4_inv['degree_seq']}")


# =====================================================================
# Build Z[1/2] KS set (also hit 31)
# =====================================================================
print("\n" + "=" * 70)
print("Building Z[1/2] KS set")
print("=" * 70)

alph_half = [0, 1, -1, 2, -2, 0.5, -0.5]
rays_half = generate_rays_from_alphabet(alph_half)
pairs_half, triads_half = build_pairs_triads(rays_half)
print(f"  Z[1/2] pool: {len(rays_half)} rays, {len(triads_half)} triads")

half_rays, half_pairs, half_triads, half_size, half_sizes = extract_minimal_set(
    rays_half, pairs_half, triads_half, n_trials=1000)
print(f"  Z[1/2] minimal: {half_size} rays, {len(half_triads)} bases")
print(f"  Size distribution (top 5): {dict(sorted(half_sizes.items())[:5])}")

half_inv = graph_invariants(half_size, half_pairs)
print(f"  Graph invariants: edges={half_inv['edges']}, triangles={half_inv['triangles']}")
print(f"  Degree sequence: {half_inv['degree_seq']}")


# =====================================================================
# Build Triple norm-2 KS set (also hit 31)
# =====================================================================
print("\n" + "=" * 70)
print("Building Triple norm-2 {2,sqrt2,w,wbar} KS set")
print("=" * 70)

sqrt2 = np.sqrt(2)
alph_triple = [0, 1, -1, 2, -2, sqrt2, -sqrt2, OMEGA, -OMEGA,
               OMEGA.conjugate(), -OMEGA.conjugate()]
rays_triple = generate_rays_from_alphabet(alph_triple)
pairs_triple, triads_triple = build_pairs_triads(rays_triple)
print(f"  Triple pool: {len(rays_triple)} rays, {len(triads_triple)} triads")

triple_rays, triple_pairs, triple_triads, triple_size, triple_sizes = extract_minimal_set(
    rays_triple, pairs_triple, triads_triple, n_trials=1000)
print(f"  Triple minimal: {triple_size} rays, {len(triple_triads)} bases")
print(f"  Size distribution (top 5): {dict(sorted(triple_sizes.items())[:5])}")

triple_inv = graph_invariants(triple_size, triple_pairs)
print(f"  Graph invariants: edges={triple_inv['edges']}, triangles={triple_inv['triangles']}")
print(f"  Degree sequence: {triple_inv['degree_seq']}")


# =====================================================================
# COMPARISON
# =====================================================================
print("\n" + "=" * 70)
print("GRAPH ISOMORPHISM COMPARISON")
print("=" * 70)

all_sets = [
    ("CK-31 (integer)", ck31_size, ck31_pairs, ck31_inv),
    ("A4 group", a4_size, a4_min_pairs, a4_inv),
    ("S4 group", s4_size, s4_min_pairs, s4_inv),
    ("Z[1/2]", half_size, half_pairs, half_inv),
    ("Triple norm-2", triple_size, triple_pairs, triple_inv),
]

# Quick invariant comparison
print("\nInvariant comparison:")
print(f"  {'Name':<20s} {'n':>4s} {'edges':>6s} {'tri':>5s} {'tr(A4)':>8s} {'degree seq (first 5)':>30s}")
print(f"  {'-'*20} {'-'*4} {'-'*6} {'-'*5} {'-'*8} {'-'*30}")
for name, n, pairs, inv in all_sets:
    deg5 = str(inv['degree_seq'][:5])
    print(f"  {name:<20s} {inv['n']:>4d} {inv['edges']:>6d} {inv['triangles']:>5d} {inv['trace_a4']:>8d} {deg5:>30s}")

# Pairwise refined isomorphism tests
print("\nPairwise Weisfeiler-Leman (WL-1) isomorphism tests:")
for i in range(len(all_sets)):
    for j in range(i+1, len(all_sets)):
        name_i, n_i, pairs_i, inv_i = all_sets[i]
        name_j, n_j, pairs_j, inv_j = all_sets[j]
        if n_i != n_j:
            print(f"  {name_i} vs {name_j}: DIFFERENT (size {n_i} vs {n_j})")
            continue

        # Check invariants first
        if inv_i['edges'] != inv_j['edges']:
            print(f"  {name_i} vs {name_j}: DIFFERENT (edges {inv_i['edges']} vs {inv_j['edges']})")
            continue
        if inv_i['degree_seq'] != inv_j['degree_seq']:
            print(f"  {name_i} vs {name_j}: DIFFERENT (degree sequences differ)")
            continue
        if inv_i['triangles'] != inv_j['triangles']:
            print(f"  {name_i} vs {name_j}: DIFFERENT (triangles {inv_i['triangles']} vs {inv_j['triangles']})")
            continue

        result, detail = refined_isomorphism_test(n_i, pairs_i, n_j, pairs_j)
        status = "LIKELY ISOMORPHIC (WL-1 cannot distinguish)" if result else f"DIFFERENT ({detail})"
        print(f"  {name_i} vs {name_j}: {status}")

# Eigenvalue comparison for the 31-vertex sets
print("\nSpectral comparison (eigenvalues of 31-vertex sets):")
for name, n, pairs, inv in all_sets:
    if n == 31:
        eigs = inv['eigenvalues']
        # Show just the top 5 and bottom 5
        print(f"  {name}: [{eigs[0]:.4f}, {eigs[1]:.4f}, ... {eigs[-2]:.4f}, {eigs[-1]:.4f}]")
        print(f"    Spectral radius: {max(abs(e) for e in eigs):.6f}")

print("\n" + "=" * 70)
print("CONCLUSION")
print("=" * 70)
# Check if all 31-sets share the same invariants
sets_31 = [(name, inv) for name, n, pairs, inv in all_sets if n == 31]
if len(sets_31) > 1:
    ref_inv = sets_31[0][1]
    all_match = all(s[1]['eigenvalues'] == ref_inv['eigenvalues'] and
                    s[1]['degree_seq'] == ref_inv['degree_seq']
                    for s in sets_31)
    if all_match:
        print("All 31-vertex KS sets have IDENTICAL graph invariants.")
        print("Strong evidence that CK-31 emerges as a universal structure")
        print("regardless of algebraic origin (integers, groups, mixed fields).")
    else:
        print("The 31-vertex KS sets have DIFFERENT graph invariants!")
        print("Multiple distinct 31-vertex KS graphs exist.")
