"""
ks_stitching_search.py -- Search for tighter stitchings of 10-ray modules
=========================================================================

Strategy:
1. Extract the exact 10-ray module structure from CK-31
2. Build abstract stitchings by overlapping modules at shared vertices
3. Test each for KS-uncolorability via SAT
4. Look for uncolorable stitchings with < 31 total vertices
5. Check geometric realizability of any found

Two approaches:
  A) Top-down: try removing rays from CK-31 while preserving uncolorability
  B) Bottom-up: stitch 10-ray modules together, test uncolorability
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

import numpy as np
import cmath
import random
import networkx as nx
from itertools import combinations
from pysat.solvers import Glucose4

from ks_complex import canonicalize_complex_ray, hermitian_dot
from ks_new_islands import generate_rays_from_alphabet, hermitian_completion, sat_minimize
from ks_new_island_analysis import build_pairs_triads
from ks_sat import is_uncolorable as sat_uncolorable

random.seed(42)
np.random.seed(42)


def is_ks_uncolorable(n_vertices, triads):
    """Test if an abstract hypergraph is KS-uncolorable via SAT.

    KS coloring: assign 0 or 1 to each vertex such that each triad
    has exactly one vertex colored 1.

    Returns True if NO valid coloring exists (= KS-uncolorable).
    """
    solver = Glucose4()

    # Variables: vertex i -> variable (i+1)
    # For each triad (a,b,c): exactly one of a,b,c is 1
    for a, b, c in triads:
        va, vb, vc = a + 1, b + 1, c + 1
        # At least one is true
        solver.add_clause([va, vb, vc])
        # At most one is true (pairwise negation)
        solver.add_clause([-va, -vb])
        solver.add_clause([-va, -vc])
        solver.add_clause([-vb, -vc])

    result = solver.solve()
    solver.delete()
    return not result


def build_ck31():
    """Build CK-31 and return full data."""
    alphabet = [0, 1, -1, 2, -2]
    rays = generate_rays_from_alphabet(alphabet)
    rays = hermitian_completion(rays, max_iter=5)
    pairs, triads = build_pairs_triads(rays)

    subset, min_size, _ = sat_minimize(rays, pairs, triads, n_trials=500)
    s = set(subset)
    remap = {old: new for new, old in enumerate(sorted(subset))}
    min_rays = [rays[i] for i in sorted(subset)]
    min_pairs = [(remap[a], remap[b]) for a, b in pairs if a in s and b in s]
    min_triads = [(remap[a], remap[b], remap[c]) for a, b, c in triads
                  if a in s and b in s and c in s]

    return min_rays, min_pairs, min_triads, min_size


# =====================================================================
print("=" * 70)
print("STITCHING SEARCH FOR TIGHTER KS SETS")
print("=" * 70)

# Build CK-31
print("\n--- Building CK-31 ---")
rays_31, pairs_31, triads_31, size_31 = build_ck31()
print(f"  CK-31: {size_31} rays, {len(triads_31)} bases")

G31 = nx.Graph()
G31.add_nodes_from(range(size_31))
G31.add_edges_from(pairs_31)


# =====================================================================
# APPROACH A: Top-down -- systematic ray removal from CK-31
# =====================================================================
print(f"\n{'='*70}")
print("APPROACH A: Top-down ray removal from CK-31")
print(f"{'='*70}")

print("\n--- Testing: can any single ray be removed? ---")
for v in range(31):
    remaining = [i for i in range(31) if i != v]
    remap = {old: new for new, old in enumerate(remaining)}
    new_triads = []
    for a, b, c in triads_31:
        if a != v and b != v and c != v:
            new_triads.append((remap[a], remap[b], remap[c]))

    if new_triads and is_ks_uncolorable(30, new_triads):
        deg = G31.degree(v)
        n_triads = sum(1 for a, b, c in triads_31 if v in (a, b, c))
        print(f"  REMOVING vertex {v} (deg {deg}, {n_triads} triads): "
              f"STILL UNCOLORABLE with 30 vertices, {len(new_triads)} bases!")

print("\n--- Testing: can any pair of rays be removed? ---")
pair_removals = 0
for v1, v2 in combinations(range(31), 2):
    remaining = [i for i in range(31) if i != v1 and i != v2]
    remap = {old: new for new, old in enumerate(remaining)}
    removed = {v1, v2}
    new_triads = []
    for a, b, c in triads_31:
        if a not in removed and b not in removed and c not in removed:
            new_triads.append((remap[a], remap[b], remap[c]))

    if new_triads and is_ks_uncolorable(29, new_triads):
        d1, d2 = G31.degree(v1), G31.degree(v2)
        print(f"  REMOVING vertices {v1} (deg {d1}) and {v2} (deg {d2}): "
              f"STILL UNCOLORABLE with 29 vertices, {len(new_triads)} bases!")
        pair_removals += 1

if pair_removals == 0:
    print("  No pair removal preserves uncolorability.")


# =====================================================================
# APPROACH B: Bottom-up -- abstract stitching of pentagon+triad modules
# =====================================================================
print(f"\n{'='*70}")
print("APPROACH B: Bottom-up abstract stitching")
print(f"{'='*70}")

# Define abstract 10-ray module
# Pentagon: vertices 0-4 in a 5-cycle
# Caps: vertices 5-9
# Triads: each cap vertex forms a triad with two non-adjacent pentagon vertices
# (non-adjacent because adjacent pentagon vertices are already connected by edge)

def make_module(offset=0):
    """Create one abstract 10-ray module.

    Pentagon: offset+0 through offset+4 (5-cycle)
    Caps: offset+5 through offset+9

    Triads connect caps to non-adjacent pentagon vertex pairs:
      cap5 with (pent0, pent2)  -- non-adjacent in pentagon
      cap6 with (pent1, pent3)  -- non-adjacent
      cap7 with (pent2, pent4)  -- non-adjacent
      cap8 with (pent3, pent0)  -- non-adjacent
      cap9 with (pent4, pent1)  -- non-adjacent
    """
    p = [offset + i for i in range(5)]
    c = [offset + i for i in range(5, 10)]

    triads = [
        (c[0], p[0], p[2]),
        (c[1], p[1], p[3]),
        (c[2], p[2], p[4]),
        (c[3], p[3], p[0]),
        (c[4], p[4], p[1]),
    ]

    edges = [
        (p[0], p[1]), (p[1], p[2]), (p[2], p[3]), (p[3], p[4]), (p[4], p[0]),
    ]
    # Add triad edges
    for a, b, cc in triads:
        edges.extend([(a, b), (a, cc), (b, cc)])

    return p, c, triads, edges


def stitch_modules(n_modules, shared_vertices_map):
    """Stitch n modules together with specified vertex sharing.

    shared_vertices_map: list of (mod_i, vert_i, mod_j, vert_j) tuples
    meaning module i's vertex vert_i is identified with module j's vertex vert_j.
    """
    # Assign vertices: first module gets 0-9, second 10-19, etc.
    # Then merge shared vertices
    raw_vertices = {}
    for m in range(n_modules):
        for v in range(10):
            raw_vertices[(m, v)] = m * 10 + v

    # Union-find for merging
    parent = {}
    def find(x):
        while parent.get(x, x) != x:
            parent[x] = parent.get(parent[x], parent[x])
            x = parent[x]
        return x
    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py

    for mi, vi, mj, vj in shared_vertices_map:
        union(raw_vertices[(mi, vi)], raw_vertices[(mj, vj)])

    # Collect all triads and remap
    all_triads = []
    for m in range(n_modules):
        _, _, triads, _ = make_module(m * 10)
        all_triads.extend(triads)

    # Remap to canonical representatives
    canonical = {}
    counter = 0
    remapped_triads = []
    for a, b, c in all_triads:
        ra, rb, rc = find(a), find(b), find(c)
        for r in [ra, rb, rc]:
            if r not in canonical:
                canonical[r] = counter
                counter += 1
        remapped_triads.append((canonical[ra], canonical[rb], canonical[rc]))

    return counter, remapped_triads


# Test single module
print("\n--- Single 10-ray module ---")
p, c, triads, edges = make_module()
ks = is_ks_uncolorable(10, triads)
print(f"  10 rays, 5 triads: KS-uncolorable = {ks}")

# Test two modules with varying overlap
print("\n--- Two modules with varying shared vertices ---")

# Try systematic stitchings of 2 modules
# Share between 1 and 5 vertices
best_uncolorable = None

# Strategy: share cap vertices of module 1 with pentagon vertices of module 2
# This mimics how KS sets are built -- one module's auxiliary rays become
# another module's structural rays
stitching_configs = [
    # (description, [(mod_i, vert_i, mod_j, vert_j), ...])
    ("1 shared (cap0=pent0)", [(0, 5, 1, 0)]),
    ("2 shared (cap0=pent0, cap1=pent1)", [(0, 5, 1, 0), (0, 6, 1, 1)]),
    ("3 shared (cap0-2 = pent0-2)", [(0, 5, 1, 0), (0, 6, 1, 1), (0, 7, 1, 2)]),
    ("3 shared (cap0,2,4 = pent0,2,4)", [(0, 5, 1, 0), (0, 7, 1, 2), (0, 9, 1, 4)]),
    ("4 shared", [(0, 5, 1, 0), (0, 6, 1, 1), (0, 7, 1, 2), (0, 8, 1, 3)]),
    ("5 shared (all caps=pents)", [(0, 5, 1, 0), (0, 6, 1, 1), (0, 7, 1, 2), (0, 8, 1, 3), (0, 9, 1, 4)]),
    # Cross-stitching: share pentagon vertices too
    ("2 shared pent-pent", [(0, 0, 1, 0), (0, 1, 1, 1)]),
    ("3 shared pent-pent", [(0, 0, 1, 0), (0, 1, 1, 1), (0, 2, 1, 2)]),
    # Mixed: share one cap and one pentagon
    ("2 mixed (pent0=pent0, cap0=pent2)", [(0, 0, 1, 0), (0, 5, 1, 2)]),
    ("3 mixed", [(0, 0, 1, 0), (0, 5, 1, 2), (0, 7, 1, 4)]),
]

for desc, sharing in stitching_configs:
    n_verts, triads = stitch_modules(2, sharing)
    ks = is_ks_uncolorable(n_verts, triads)
    print(f"  {desc}: {n_verts} vertices, {len(triads)} triads, KS = {ks}")
    if ks and (best_uncolorable is None or n_verts < best_uncolorable):
        best_uncolorable = n_verts

# Try 3 modules
print("\n--- Three modules ---")
configs_3 = [
    ("chain: 1-2 share 3, 2-3 share 3",
     [(0, 5, 1, 0), (0, 6, 1, 1), (0, 7, 1, 2),
      (1, 5, 2, 0), (1, 6, 2, 1), (1, 7, 2, 2)]),
    ("chain: 1-2 share 5, 2-3 share 5",
     [(0, 5, 1, 0), (0, 6, 1, 1), (0, 7, 1, 2), (0, 8, 1, 3), (0, 9, 1, 4),
      (1, 5, 2, 0), (1, 6, 2, 1), (1, 7, 2, 2), (1, 8, 2, 3), (1, 9, 2, 4)]),
    ("triangle: each pair shares 2",
     [(0, 5, 1, 0), (0, 6, 1, 1),
      (1, 5, 2, 0), (1, 6, 2, 1),
      (2, 5, 0, 0), (2, 6, 0, 1)]),
    ("triangle: each pair shares 3",
     [(0, 5, 1, 0), (0, 6, 1, 1), (0, 7, 1, 2),
      (1, 5, 2, 0), (1, 6, 2, 1), (1, 7, 2, 2),
      (2, 5, 0, 0), (2, 6, 0, 1), (2, 7, 0, 2)]),
    ("hub: mod0 caps shared with mod1 and mod2 pentagons",
     [(0, 5, 1, 0), (0, 6, 1, 1), (0, 7, 1, 2),
      (0, 8, 2, 0), (0, 9, 2, 1)]),
]

for desc, sharing in configs_3:
    n_verts, triads = stitch_modules(3, sharing)
    ks = is_ks_uncolorable(n_verts, triads)
    print(f"  {desc}: {n_verts}v, {len(triads)}t, KS = {ks}")
    if ks and (best_uncolorable is None or n_verts < best_uncolorable):
        best_uncolorable = n_verts

# Try 4 modules
print("\n--- Four modules ---")
configs_4 = [
    ("chain: each pair shares 3",
     [(0, 5, 1, 0), (0, 6, 1, 1), (0, 7, 1, 2),
      (1, 5, 2, 0), (1, 6, 2, 1), (1, 7, 2, 2),
      (2, 5, 3, 0), (2, 6, 3, 1), (2, 7, 3, 2)]),
    ("chain: each pair shares 5",
     [(0, 5, 1, 0), (0, 6, 1, 1), (0, 7, 1, 2), (0, 8, 1, 3), (0, 9, 1, 4),
      (1, 5, 2, 0), (1, 6, 2, 1), (1, 7, 2, 2), (1, 8, 2, 3), (1, 9, 2, 4),
      (2, 5, 3, 0), (2, 6, 3, 1), (2, 7, 3, 2), (2, 8, 3, 3), (2, 9, 3, 4)]),
    ("ring: 4 modules in a cycle, each shares 3",
     [(0, 5, 1, 0), (0, 6, 1, 1), (0, 7, 1, 2),
      (1, 5, 2, 0), (1, 6, 2, 1), (1, 7, 2, 2),
      (2, 5, 3, 0), (2, 6, 3, 1), (2, 7, 3, 2),
      (3, 5, 0, 0), (3, 6, 0, 1), (3, 7, 0, 2)]),
    ("star: mod0 is hub, shares 3 with each of 1,2,3",
     [(0, 5, 1, 0), (0, 6, 1, 1), (0, 7, 1, 2),
      (0, 8, 2, 0), (0, 9, 2, 1), (0, 0, 2, 2),
      (0, 1, 3, 0), (0, 2, 3, 1), (0, 3, 3, 2)]),
]

for desc, sharing in configs_4:
    n_verts, triads = stitch_modules(4, sharing)
    ks = is_ks_uncolorable(n_verts, triads)
    print(f"  {desc}: {n_verts}v, {len(triads)}t, KS = {ks}")
    if ks and (best_uncolorable is None or n_verts < best_uncolorable):
        best_uncolorable = n_verts

# Try 5 and 6 modules with heavy sharing
print("\n--- Five and six modules (heavy sharing) ---")
def make_chain_sharing(n_modules, n_shared):
    sharing = []
    for i in range(n_modules - 1):
        for j in range(n_shared):
            sharing.append((i, 5 + j, i + 1, j))
    return sharing

def make_ring_sharing(n_modules, n_shared):
    sharing = []
    for i in range(n_modules):
        for j in range(n_shared):
            sharing.append((i, 5 + j, (i + 1) % n_modules, j))
    return sharing

configs_56 = [
    (5, "chain-5: each shares 5", make_chain_sharing(5, 5)),
    (5, "ring-5: each shares 3", make_ring_sharing(5, 3)),
    (6, "chain-6: each shares 5", make_chain_sharing(6, 5)),
    (6, "ring-6: each shares 3", make_ring_sharing(6, 3)),
]

for n_mod, desc, sharing in configs_56:
    n_verts, triads = stitch_modules(n_mod, sharing)
    ks = is_ks_uncolorable(n_verts, triads)
    print(f"  {desc}: {n_verts}v, {len(triads)}t, KS = {ks}")
    if ks and (best_uncolorable is None or n_verts < best_uncolorable):
        best_uncolorable = n_verts


# =====================================================================
# APPROACH C: Random stitching search
# =====================================================================
print(f"\n{'='*70}")
print("APPROACH C: Randomized stitching search")
print(f"{'='*70}")

def random_stitching(n_modules, min_shared=2, max_shared=5, n_trials=1000):
    """Try random stitchings and report smallest uncolorable."""
    best = None
    best_config = None

    for trial in range(n_trials):
        sharing = []
        for i in range(n_modules - 1):
            n_shared = random.randint(min_shared, max_shared)
            # Pick random vertices to share
            src_verts = random.sample(range(10), n_shared)
            dst_verts = random.sample(range(10), n_shared)
            for sv, dv in zip(src_verts, dst_verts):
                sharing.append((i, sv, i+1, dv))

        # Also sometimes add cross-links (ring closure)
        if n_modules >= 3 and random.random() < 0.3:
            n_cross = random.randint(1, 3)
            src_verts = random.sample(range(10), n_cross)
            dst_verts = random.sample(range(10), n_cross)
            for sv, dv in zip(src_verts, dst_verts):
                sharing.append((n_modules-1, sv, 0, dv))

        n_verts, triads = stitch_modules(n_modules, sharing)

        if n_verts < 31 and triads and is_ks_uncolorable(n_verts, triads):
            if best is None or n_verts < best:
                best = n_verts
                best_config = (n_modules, sharing, n_verts, len(triads))
                print(f"  Trial {trial}: FOUND {n_verts}v, {len(triads)}t "
                      f"({n_modules} modules) -- NEW BEST!")

    return best, best_config

for n_mod in [3, 4, 5, 6, 7]:
    print(f"\n  Searching with {n_mod} modules (2000 random trials)...")
    best, config = random_stitching(n_mod, min_shared=2, max_shared=6, n_trials=2000)
    if best:
        print(f"  Best with {n_mod} modules: {best} vertices")
    else:
        print(f"  No uncolorable stitching found < 31 vertices")


# =====================================================================
# Summary
# =====================================================================
print(f"\n{'='*70}")
print("SUMMARY")
print(f"{'='*70}")

if best_uncolorable:
    print(f"\n  Smallest abstract KS-uncolorable stitching found: {best_uncolorable} vertices")
    print(f"  (CK-31 has 31 vertices)")
    print(f"  NOTE: Abstract uncolorability does NOT guarantee geometric realizability in R^3")
else:
    print(f"\n  No stitching found that beats CK-31's 31 vertices")
    print(f"  The 10-ray module stitching approach may not be the right decomposition,")
    print(f"  or 31 may truly be minimal.")

print(f"\n{'='*70}")
print("DONE")
print(f"{'='*70}")
