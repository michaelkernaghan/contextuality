"""
ks_vf2_verification.py -- Definitive VF2 isomorphism check for CK-31 universality
===================================================================================

Uses the same construction pipeline as ks_explore_new2.py (which is known to work)
but adds VF2 graph isomorphism and hypergraph verification.
Also adds negative controls for norm > 2 fields.
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

import numpy as np
import cmath
import random
import networkx as nx

from ks_complex import canonicalize_complex_ray, hermitian_dot
from ks_new_islands import generate_rays_from_alphabet, hermitian_completion, sat_minimize
from ks_new_island_analysis import build_pairs_triads
from ks_sat import is_uncolorable as sat_uncolorable

random.seed(42)
np.random.seed(42)

OMEGA = cmath.exp(2j * cmath.pi / 3)
sqrt2 = np.sqrt(2)


def test_and_minimize(name, alphabet, use_completion=True, max_rays=400):
    """Test alphabet, minimize, return (rays, pairs, triads, size) or None."""
    rays = generate_rays_from_alphabet(alphabet)
    n_raw = len(rays)

    if use_completion:
        rays = hermitian_completion(rays, max_iter=5)
        if len(rays) > max_rays:
            print(f"  {name}: {n_raw} -> {len(rays)} after completion (too large, skipping completion)")
            rays = generate_rays_from_alphabet(alphabet)

    pairs, triads = build_pairs_triads(rays)

    if not triads or not sat_uncolorable(len(rays), pairs, triads):
        print(f"  {name}: {len(rays)} rays, {len(triads)} bases -- COLORABLE")
        return None

    subset, min_size, sizes = sat_minimize(rays, pairs, triads, n_trials=500)
    s = set(subset)
    remap = {old: new for new, old in enumerate(sorted(subset))}
    min_rays = [rays[i] for i in sorted(subset)]
    min_pairs = [(remap[a], remap[b]) for a, b in pairs if a in s and b in s]
    min_triads = [(remap[a], remap[b], remap[c]) for a, b, c in triads
                  if a in s and b in s and c in s]

    print(f"  {name}: {len(rays)} rays -> MIN {min_size} rays, {len(min_triads)} bases")
    return (min_rays, min_pairs, min_triads, min_size)


def build_nx_graph(n, pairs):
    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from(pairs)
    return G


def check_hypergraph_iso(triads1, triads2, mapping):
    """Check if triads1 maps to triads2 under mapping dict."""
    mapped = set()
    for a, b, c in triads1:
        t = tuple(sorted([mapping[a], mapping[b], mapping[c]]))
        mapped.add(t)
    original = set(tuple(sorted(t)) for t in triads2)
    return mapped == original


# =====================================================================
print("=" * 70)
print("VF2 ISOMORPHISM VERIFICATION FOR CK-31 UNIVERSALITY")
print("=" * 70)

# These are the constructions known to produce min-31 from ks_explore_new2.py
constructions = {}

# 1. Integer {0, +/-1, +/-2}
print("\n--- 1. Integer ---")
r = test_and_minimize("Integer", [0, 1, -1, 2, -2])
if r and r[3] == 31: constructions["Integer"] = r

# 2. Z[1/2] rationals {0, +/-1, +/-2, +/-1/2}
print("\n--- 2. Z[1/2] ---")
r = test_and_minimize("Z[1/2]", [0, 1, -1, 2, -2, 0.5, -0.5], use_completion=False)
if r and r[3] == 31: constructions["Z[1/2]"] = r

# 3. Triple norm-2 {0, +/-1, +/-2, +/-sqrt(2), +/-omega, +/-omega_bar}
print("\n--- 3. Triple norm-2 ---")
r = test_and_minimize("Triple norm-2",
    [0, 1, -1, 2, -2, sqrt2, -sqrt2, OMEGA, -OMEGA,
     OMEGA.conjugate(), -OMEGA.conjugate()],
    use_completion=False, max_rays=300)
if r and r[3] == 31: constructions["Triple norm-2"] = r

# 4-5. Group constructions (A4, S4) -- build manually
print("\n--- 4-5. Group orbits (A4, S4) ---")

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

# Generate group elements
R3 = rotation_matrix([1, 1, 1], 2*np.pi/3)
R2 = rotation_matrix([1, 0, 0], np.pi)
R4 = rotation_matrix([0, 0, 1], np.pi/2)

def generate_group(generators, max_size=100):
    elements = [np.eye(3)]
    queue = [np.eye(3)]
    for _ in range(30):
        new = []
        for g in queue:
            for gen in generators:
                h = g @ gen
                is_new = all(not np.allclose(h, e, atol=1e-10) for e in elements)
                if is_new:
                    elements.append(h)
                    new.append(h)
                    if len(elements) >= max_size:
                        return elements
        queue = new
        if not queue:
            break
    return elements

a4_elems = generate_group([R3, R3 @ R3, R2])
s4_elems = generate_group([R3, R3 @ R3, R2, R4, R4 @ R4 @ R4])
print(f"  A4: {len(a4_elems)} elements, S4: {len(s4_elems)} elements")

seeds = [np.array([1, 0, 0], dtype=float),
         np.array([1, 1, 0], dtype=float),
         np.array([1, 1, 1], dtype=float),
         np.array([2, 1, 0], dtype=float),
         np.array([2, 1, 1], dtype=float)]

for group_name, group_elems in [("A4", a4_elems), ("S4", s4_elems)]:
    rays_raw = []
    for seed in seeds:
        for g in group_elems:
            v = g @ seed
            r = canonicalize_complex_ray(v)
            if r is not None:
                is_dup = any(abs(hermitian_dot(r, e)) > 0.999 for e in rays_raw)
                if not is_dup:
                    rays_raw.append(r)

    rays_tuples = [tuple(complex(x) for x in r) for r in rays_raw]
    rays_comp = hermitian_completion(rays_tuples, max_iter=5)
    pairs, triads = build_pairs_triads(rays_comp)
    n = len(rays_comp)

    if triads and sat_uncolorable(n, pairs, triads):
        subset, min_size, sizes = sat_minimize(rays_comp, pairs, triads, n_trials=500)
        s = set(subset)
        remap = {old: new for new, old in enumerate(sorted(subset))}
        min_rays = [rays_comp[i] for i in sorted(subset)]
        min_pairs = [(remap[a], remap[b]) for a, b in pairs if a in s and b in s]
        min_triads = [(remap[a], remap[b], remap[c]) for a, b, c in triads
                      if a in s and b in s and c in s]
        print(f"  {group_name}: {n} rays -> MIN {min_size} rays, {len(min_triads)} bases")
        if min_size == 31:
            constructions[group_name] = (min_rays, min_pairs, min_triads, min_size)
    else:
        print(f"  {group_name}: {n} rays -- COLORABLE")


# =====================================================================
print("\n" + "=" * 70)
print("VF2 GRAPH ISOMORPHISM (definitive)")
print("=" * 70)

names = list(constructions.keys())
graphs = {}
for name in names:
    mr, mp, mt, sz = constructions[name]
    G = build_nx_graph(sz, mp)
    graphs[name] = (G, mt)
    print(f"  {name}: {G.number_of_nodes()}v, {G.number_of_edges()}e, {len(mt)} bases")

all_graph_iso = True
all_hyp_iso = True
ref = names[0]
G_ref, t_ref = graphs[ref]

for name in names[1:]:
    G_test, t_test = graphs[name]
    GM = nx.isomorphism.GraphMatcher(G_ref, G_test)
    g_iso = GM.is_isomorphic()
    print(f"  {ref} <-> {name}: graph {'ISO' if g_iso else 'NOT ISO'}", end="")
    if not g_iso:
        all_graph_iso = False
        print()
        continue

    # Check hypergraph under the found mapping
    mapping = GM.mapping
    h_iso = check_hypergraph_iso(t_ref, t_test, mapping)
    if not h_iso:
        # Try other isomorphisms
        for m in GM.isomorphisms_iter():
            if check_hypergraph_iso(t_ref, t_test, m):
                h_iso = True
                break
    print(f", hypergraph {'ISO' if h_iso else 'NOT ISO'}")
    if not h_iso:
        all_hyp_iso = False

print(f"\n  RESULT: {len(names)} constructions, "
      f"graph iso: {'ALL' if all_graph_iso else 'SOME FAILED'}, "
      f"hypergraph iso: {'ALL' if all_hyp_iso else 'SOME FAILED'}")


# =====================================================================
print("\n" + "=" * 70)
print("NEGATIVE CONTROLS (norm > 2 fields)")
print("=" * 70)

for field_name, alph in [
    ("Z[sqrt(3)]  |a|^2=3", [0, 1, -1, np.sqrt(3), -np.sqrt(3)]),
    ("Z[sqrt(5)]  |a|^2=5", [0, 1, -1, np.sqrt(5), -np.sqrt(5)]),
    ("Z[sqrt(-5)] |a|^2=5", [0, 1, -1, 1j*np.sqrt(5), -1j*np.sqrt(5)]),
]:
    rays = generate_rays_from_alphabet(alph)
    rays_c = hermitian_completion(rays, max_iter=5)
    pairs, triads = build_pairs_triads(rays_c)
    n = len(rays_c)
    ks = sat_uncolorable(n, pairs, triads) if triads else False
    print(f"  {field_name}: {n} rays, {len(pairs)} pairs, {len(triads)} bases, KS: {ks}")

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)
