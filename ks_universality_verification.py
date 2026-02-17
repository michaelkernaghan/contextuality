"""
ks_universality_verification.py -- Rigorous verification for universality_letter.tex
==================================================================================

Addresses peer review items:
  #4: Definitive graph isomorphism via VF2 (networkx)
  #5: Hypergraph (basis) isomorphism verification
  #9: Negative control -- norm > 2 field with orthogonal triples but KS-colorable
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

import numpy as np
import cmath
import random
import networkx as nx
from itertools import combinations

from ks_complex import canonicalize_complex_ray, hermitian_dot
from ks_new_islands import generate_rays_from_alphabet, hermitian_completion
from ks_new_island_analysis import build_pairs_triads
from ks_sat import is_uncolorable as sat_uncolorable
from ks_new_islands import sat_minimize as _sat_minimize

random.seed(42)
np.random.seed(42)

OMEGA = cmath.exp(2j * cmath.pi / 3)
SQRT2 = np.sqrt(2)


def build_nx_graph(n, pairs):
    """Build networkx graph from pairs."""
    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from(pairs)
    return G


def hypergraph_isomorphic(triads1, triads2, iso_map):
    """Check if triads1 maps to triads2 under iso_map (dict: node->node)."""
    mapped = set()
    for a, b, c in triads1:
        t = tuple(sorted([iso_map[a], iso_map[b], iso_map[c]]))
        mapped.add(t)
    original = set(tuple(sorted(t)) for t in triads2)
    return mapped == original


def get_minimal_ks(rays, pairs, triads, label=""):
    """Get minimal KS set via greedy deletion. Returns (rays, pairs, triads, size)."""
    n = len(rays)
    if not triads or not sat_uncolorable(n, pairs, triads):
        print(f"  {label}: NOT KS-uncolorable ({n} rays, {len(triads)} bases)")
        return None, None, None, None

    best_subset, best_size, sizes = _sat_minimize(rays, pairs, triads, n_trials=500)

    # Rebuild rays/pairs/triads for the minimal subset
    s = set(best_subset)
    remap = {old: new for new, old in enumerate(sorted(best_subset))}
    min_rays = [rays[i] for i in sorted(best_subset)]
    min_pairs = [(remap[a], remap[b]) for a, b in pairs if a in s and b in s]
    min_triads = [(remap[a], remap[b], remap[c]) for a, b, c in triads
                  if a in s and b in s and c in s]

    print(f"  {label}: {n} rays -> min {len(min_rays)} rays, {len(min_triads)} bases")
    return min_rays, min_pairs, min_triads, len(min_rays)


# =====================================================================
# PART 1: Build 31-vertex KS sets from different constructions
# =====================================================================
print("=" * 70)
print("UNIVERSALITY VERIFICATION")
print("=" * 70)

constructions = {}

# 1. Integer alphabet {0, +/-1, +/-2}
print("\n--- Construction 1: Integer alphabet ---")
alph_int = [0, 1, -1, 2, -2]
rays = generate_rays_from_alphabet(alph_int)
rays = hermitian_completion(rays, max_iter=5)
pairs, triads = build_pairs_triads(rays)
mr, mp, mt, sz = get_minimal_ks(rays, pairs, triads, "Integer")
if sz == 31:
    constructions["Integer"] = (mr, mp, mt)

# 2. Rational alphabet {0, +/-1, +/-2, +/-1/2}
print("\n--- Construction 2: Rational alphabet ---")
alph_rat = [0, 1, -1, 2, -2, 0.5, -0.5]
rays = generate_rays_from_alphabet(alph_rat)
print(f"  Raw: {len(rays)} rays")
# Skip completion for large pools -- raw is already large enough
pairs, triads = build_pairs_triads(rays)
mr, mp, mt, sz = get_minimal_ks(rays, pairs, triads, "Rational")
if sz == 31:
    constructions["Rational"] = (mr, mp, mt)

# 3. Extended Peres {0, +/-1, +/-sqrt(2), +/-(1+sqrt(2)), +/-2}
print("\n--- Construction 3: Extended Peres ---")
alph_peres = [0, 1, -1, SQRT2, -SQRT2, 1+SQRT2, -(1+SQRT2), 2, -2]
rays = generate_rays_from_alphabet(alph_peres)
rays = hermitian_completion(rays, max_iter=5)
pairs, triads = build_pairs_triads(rays)
mr, mp, mt, sz = get_minimal_ks(rays, pairs, triads, "Ext. Peres")
if sz == 31:
    constructions["Ext. Peres"] = (mr, mp, mt)

# 4. Mixed norm-2: {0, +/-1, +/-2, +/-sqrt(2), +/-omega, +/-omega_bar}
print("\n--- Construction 4: Mixed norm-2 ---")
alph_mixed = [0, 1, -1, 2, -2, SQRT2, -SQRT2, OMEGA, -OMEGA,
              OMEGA.conjugate(), -OMEGA.conjugate()]
rays = generate_rays_from_alphabet(alph_mixed)
rays = hermitian_completion(rays, max_iter=5)
pairs, triads = build_pairs_triads(rays)
mr, mp, mt, sz = get_minimal_ks(rays, pairs, triads, "Mixed norm-2")
if sz == 31:
    constructions["Mixed norm-2"] = (mr, mp, mt)

# 5. A4 group orbits
print("\n--- Construction 5: A4 group ---")
# A4 = even permutations of 4 elements, acting as 3D rotation group
# Generators: 3-fold rotation about (1,1,1) and 2-fold rotation about (1,0,0)
def rotation_matrix(axis, angle):
    axis = np.array(axis, dtype=float)
    axis = axis / np.linalg.norm(axis)
    c, s = np.cos(angle), np.sin(angle)
    x, y, z = axis
    return np.array([
        [c + x*x*(1-c), x*y*(1-c) - z*s, x*z*(1-c) + y*s],
        [y*x*(1-c) + z*s, c + y*y*(1-c), y*z*(1-c) - x*s],
        [z*x*(1-c) - y*s, z*y*(1-c) + x*s, c + z*z*(1-c)]
    ])

# Generate A4 group elements
R3 = rotation_matrix([1, 1, 1], 2*np.pi/3)
R2 = rotation_matrix([1, 0, 0], np.pi)
a4_elements = set()
queue = [np.eye(3)]
seen = []
for _ in range(20):
    new_queue = []
    for g in queue:
        for gen in [R3, R2, R3 @ R3]:
            h = g @ gen
            is_new = True
            for s in seen:
                if np.allclose(h, s, atol=1e-10):
                    is_new = False
                    break
            if is_new:
                seen.append(h)
                new_queue.append(h)
    queue = new_queue
    if not queue:
        break
print(f"  A4 has {len(seen)} elements")

# Generate rays from seeds under A4
seeds = [np.array([1, 0, 0], dtype=float),
         np.array([1, 1, 0], dtype=float),
         np.array([1, 1, 1], dtype=float),
         np.array([2, 1, 0], dtype=float),
         np.array([2, 1, 1], dtype=float)]

a4_rays_raw = []
for seed in seeds:
    for g in seen:
        v = g @ seed
        r = canonicalize_complex_ray(v)
        if r is not None:
            is_dup = False
            for existing in a4_rays_raw:
                if hermitian_dot(r, existing) > 0.999:
                    is_dup = True
                    break
            if not is_dup:
                a4_rays_raw.append(r)

a4_rays = hermitian_completion(a4_rays_raw, max_iter=5)
pairs, triads = build_pairs_triads(a4_rays)
mr, mp, mt, sz = get_minimal_ks(a4_rays, pairs, triads, "A4")
if sz == 31:
    constructions["A4"] = (mr, mp, mt)

# 6. S4 group orbits
print("\n--- Construction 6: S4 group ---")
R4 = rotation_matrix([0, 0, 1], np.pi/2)
s4_elements = list(seen)  # start with A4
queue = list(seen)
for _ in range(20):
    new_queue = []
    for g in queue:
        for gen in [R4, R4 @ R4 @ R4]:
            h = g @ gen
            is_new = True
            for s in s4_elements:
                if np.allclose(h, s, atol=1e-10):
                    is_new = False
                    break
            if is_new:
                s4_elements.append(h)
                new_queue.append(h)
    queue = new_queue
    if not queue:
        break
print(f"  S4 has {len(s4_elements)} elements")

s4_rays_raw = []
for seed in seeds:
    for g in s4_elements:
        v = g @ seed
        r = canonicalize_complex_ray(v)
        if r is not None:
            is_dup = False
            for existing in s4_rays_raw:
                if hermitian_dot(r, existing) > 0.999:
                    is_dup = True
                    break
            if not is_dup:
                s4_rays_raw.append(r)

s4_rays = hermitian_completion(s4_rays_raw, max_iter=5)
pairs, triads = build_pairs_triads(s4_rays)
mr, mp, mt, sz = get_minimal_ks(s4_rays, pairs, triads, "S4")
if sz == 31:
    constructions["S4"] = (mr, mp, mt)


# =====================================================================
# PART 2: Definitive pairwise graph isomorphism (VF2)
# =====================================================================
print("\n" + "=" * 70)
print("GRAPH ISOMORPHISM (VF2 -- definitive)")
print("=" * 70)

names = list(constructions.keys())
graphs = {}
for name in names:
    mr, mp, mt = constructions[name]
    G = build_nx_graph(len(mr), mp)
    graphs[name] = (G, mt)
    print(f"  {name}: {G.number_of_nodes()} vertices, {G.number_of_edges()} edges, {len(mt)} bases")

all_iso = True
for i, n1 in enumerate(names):
    for n2 in names[i+1:]:
        G1 = graphs[n1][0]
        G2 = graphs[n2][0]
        iso = nx.is_isomorphic(G1, G2)
        print(f"  {n1} <-> {n2}: {'ISOMORPHIC' if iso else 'NOT ISOMORPHIC'}")
        if not iso:
            all_iso = False

if all_iso:
    print(f"\n  ALL {len(names)} constructions produce graph-isomorphic 31-vertex sets.")
else:
    print(f"\n  WARNING: Some pairs are NOT isomorphic!")


# =====================================================================
# PART 3: Hypergraph (basis) isomorphism
# =====================================================================
print("\n" + "=" * 70)
print("HYPERGRAPH (BASIS) ISOMORPHISM")
print("=" * 70)

ref_name = names[0]
G_ref, triads_ref = graphs[ref_name]

for name in names[1:]:
    G_test, triads_test = graphs[name]
    GM = nx.isomorphism.GraphMatcher(G_ref, G_test)
    if GM.is_isomorphic():
        mapping = GM.mapping  # dict: ref_node -> test_node
        hyp_iso = hypergraph_isomorphic(triads_ref, triads_test, mapping)
        print(f"  {ref_name} <-> {name}: graph iso YES, hypergraph iso {'YES' if hyp_iso else 'NO'}")
        if not hyp_iso:
            # Try other isomorphisms
            found = False
            for m in GM.isomorphisms_iter():
                if hypergraph_isomorphic(triads_ref, triads_test, m):
                    found = True
                    break
            print(f"    (searched alternative mappings: {'FOUND hypergraph iso' if found else 'NO hypergraph iso found'})")
    else:
        print(f"  {ref_name} <-> {name}: NOT graph isomorphic")


# =====================================================================
# PART 4: Negative control -- norm > 2, orthogonal triples exist, but KS-colorable
# =====================================================================
print("\n" + "=" * 70)
print("NEGATIVE CONTROL: norm > 2 fields")
print("=" * 70)

for field_name, alph in [
    ("Z[sqrt(3)]", [0, 1, -1, np.sqrt(3), -np.sqrt(3)]),
    ("Z[sqrt(5)]", [0, 1, -1, np.sqrt(5), -np.sqrt(5)]),
    ("Z[sqrt(-3)] (not Eisenstein)", [0, 1, -1, 1j*np.sqrt(3), -1j*np.sqrt(3)]),
]:
    rays = generate_rays_from_alphabet(alph)
    rays = hermitian_completion(rays, max_iter=5)
    pairs, triads = build_pairs_triads(rays)
    n = len(rays)
    ks = sat_uncolorable(n, pairs, triads) if triads else False
    print(f"  {field_name}: {n} rays, {len(pairs)} pairs, {len(triads)} bases, KS-uncolorable: {ks}")

print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
