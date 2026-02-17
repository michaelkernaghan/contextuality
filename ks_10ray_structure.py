"""
ks_10ray_structure.py -- Decompose KS sets into 10-ray basic structures
=======================================================================

Analyzes the pentagon + triad stitching pattern in CK-31 and Peres-33.

The 10-ray basic structure contains:
  - A pentagon (5-cycle) of orthogonal rays
  - Additional rays forming triads (orthogonal triples) with pentagon vertices

KS sets are built by stitching overlapping copies of this structure.
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

import numpy as np
import cmath
import random
import networkx as nx
from itertools import combinations

from ks_complex import canonicalize_complex_ray, hermitian_dot
from ks_new_islands import generate_rays_from_alphabet, hermitian_completion, sat_minimize
from ks_new_island_analysis import build_pairs_triads
from ks_sat import is_uncolorable as sat_uncolorable

random.seed(42)
np.random.seed(42)


def build_ks_set(name, alphabet, use_completion=True):
    """Build a minimized KS set and return (rays, pairs, triads, size)."""
    rays = generate_rays_from_alphabet(alphabet)
    if use_completion:
        rays = hermitian_completion(rays, max_iter=5)
    pairs, triads = build_pairs_triads(rays)

    if not triads or not sat_uncolorable(len(rays), pairs, triads):
        print(f"  {name}: NOT KS-uncolorable")
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


def find_pentagons(G):
    """Find all 5-cycles (pentagons) in graph G."""
    pentagons = []
    nodes = list(G.nodes())
    n = len(nodes)

    # Enumerate all 5-subsets and check if they form a cycle
    # For small graphs (31-52 vertices) this is feasible
    for combo in combinations(nodes, 5):
        sub = G.subgraph(combo)
        if sub.number_of_edges() == 5:
            # Check if it's actually a cycle (all degrees = 2)
            degs = [sub.degree(v) for v in combo]
            if all(d == 2 for d in degs):
                pentagons.append(set(combo))

    # Remove duplicates (same set found multiple times)
    unique = []
    for p in pentagons:
        if p not in unique:
            unique.append(p)

    return unique


def find_triads_for_vertex(v, triads):
    """Find all triads containing vertex v."""
    return [(a, b, c) for a, b, c in triads if v in (a, b, c)]


def analyze_ks_structure(name, rays, pairs, triads, size):
    """Full structural analysis of a KS set."""
    print(f"\n{'='*70}")
    print(f"STRUCTURAL ANALYSIS: {name} ({size} rays, {len(triads)} bases)")
    print(f"{'='*70}")

    # Build graph
    G = nx.Graph()
    G.add_nodes_from(range(size))
    G.add_edges_from(pairs)

    print(f"\n  Vertices: {G.number_of_nodes()}")
    print(f"  Edges (orthogonal pairs): {G.number_of_edges()}")
    print(f"  Bases (triads): {len(triads)}")

    # Degree analysis
    degrees = sorted([G.degree(v) for v in G.nodes()])
    deg_seq = {}
    for d in degrees:
        deg_seq[d] = deg_seq.get(d, 0) + 1
    print(f"  Degree sequence: {dict(sorted(deg_seq.items()))}")

    # Hub analysis (high-degree vertices)
    print(f"\n--- Hub vertices (degree >= 5) ---")
    hubs = [(v, G.degree(v)) for v in G.nodes() if G.degree(v) >= 5]
    hubs.sort(key=lambda x: -x[1])
    for v, d in hubs:
        n_triads = len(find_triads_for_vertex(v, triads))
        print(f"  Vertex {v}: degree {d}, in {n_triads} triads")

    # Find all triangles (triads in the graph)
    print(f"\n--- Triangles (orthogonal triples = bases) ---")
    triangles = []
    for a, b, c in triads:
        if G.has_edge(a, b) and G.has_edge(b, c) and G.has_edge(a, c):
            triangles.append((a, b, c))
    print(f"  Triangles that are bases: {len(triangles)} / {len(triads)}")

    # Find pentagons
    print(f"\n--- Pentagons (5-cycles) ---")
    print(f"  Searching for 5-cycles in the orthogonality graph...")
    pentagons = find_pentagons(G)
    print(f"  Found {len(pentagons)} pentagons")

    if pentagons:
        # Analyze pentagon overlaps
        print(f"\n--- Pentagon overlap analysis ---")

        # Which vertices appear in pentagons?
        pent_vertices = set()
        vertex_pent_count = {}
        for p in pentagons:
            pent_vertices.update(p)
            for v in p:
                vertex_pent_count[v] = vertex_pent_count.get(v, 0) + 1

        print(f"  Vertices in at least one pentagon: {len(pent_vertices)} / {size}")
        non_pent = set(range(size)) - pent_vertices
        if non_pent:
            print(f"  Vertices NOT in any pentagon: {sorted(non_pent)}")

        # Pentagon membership distribution
        membership = {}
        for v, c in vertex_pent_count.items():
            membership[c] = membership.get(c, 0) + 1
        print(f"  Pentagon membership distribution: {dict(sorted(membership.items()))}")
        print(f"    (e.g., '3: 5' means 5 vertices each appear in 3 pentagons)")

        # Most shared vertices
        top_shared = sorted(vertex_pent_count.items(), key=lambda x: -x[1])[:10]
        print(f"\n  Most shared vertices (appear in most pentagons):")
        for v, c in top_shared:
            print(f"    Vertex {v}: in {c} pentagons, degree {G.degree(v)}, "
                  f"in {len(find_triads_for_vertex(v, triads))} triads")

        # Pairwise pentagon overlaps
        overlap_sizes = {}
        for i, p1 in enumerate(pentagons):
            for j, p2 in enumerate(pentagons):
                if j > i:
                    ov = len(p1 & p2)
                    overlap_sizes[ov] = overlap_sizes.get(ov, 0) + 1
        print(f"\n  Pairwise pentagon overlaps:")
        for ov_size, count in sorted(overlap_sizes.items()):
            print(f"    {ov_size} shared vertices: {count} pairs")

    # 10-ray structure search
    print(f"\n--- 10-ray basic structure search ---")
    print(f"  Looking for pentagons with triad caps...")

    structures_found = []
    for pi, pent in enumerate(pentagons):
        pent_list = sorted(pent)

        # For each pentagon, find triads that include pentagon vertices
        # and identify the "cap" rays (non-pentagon rays in those triads)
        cap_rays = set()
        connecting_triads = []
        for t in triads:
            a, b, c = t
            in_pent = sum(1 for x in (a, b, c) if x in pent)
            if in_pent >= 1:  # At least one vertex in pentagon
                connecting_triads.append(t)
                for x in (a, b, c):
                    if x not in pent:
                        cap_rays.add(x)

        total_rays = pent | cap_rays
        if len(total_rays) <= 12:  # Reasonable size for a basic structure
            structures_found.append({
                'pentagon': pent_list,
                'cap_rays': sorted(cap_rays),
                'total_rays': len(total_rays),
                'triads': len(connecting_triads),
            })

    print(f"  Found {len(structures_found)} pentagon+cap structures (<=12 rays)")

    # Show distribution of structure sizes
    size_dist = {}
    for s in structures_found:
        sz = s['total_rays']
        size_dist[sz] = size_dist.get(sz, 0) + 1
    print(f"  Size distribution: {dict(sorted(size_dist.items()))}")

    # Show some examples
    if structures_found:
        # Sort by total size
        structures_found.sort(key=lambda x: x['total_rays'])

        print(f"\n  Smallest structures:")
        for s in structures_found[:5]:
            print(f"    Pentagon {s['pentagon']} + caps {s['cap_rays']} "
                  f"= {s['total_rays']} rays, {s['triads']} triads")

        # Find the 10-ray structures specifically
        ten_ray = [s for s in structures_found if s['total_rays'] == 10]
        if ten_ray:
            print(f"\n  Exact 10-ray structures: {len(ten_ray)}")
            for s in ten_ray[:10]:
                print(f"    Pentagon {s['pentagon']} + caps {s['cap_rays']} "
                      f"({s['triads']} triads)")

    # Coverage analysis: how many copies needed to cover all vertices?
    print(f"\n--- Coverage analysis ---")
    if pentagons:
        # Greedy set cover: pick pentagons that cover the most uncovered vertices
        uncovered = set(range(size))
        cover = []
        remaining_pents = list(range(len(pentagons)))

        while uncovered and remaining_pents:
            best_i = max(remaining_pents,
                        key=lambda i: len(pentagons[i] & uncovered))
            best_pent = pentagons[best_i]
            newly_covered = best_pent & uncovered
            if not newly_covered:
                break
            cover.append((best_i, best_pent, len(newly_covered)))
            uncovered -= newly_covered
            remaining_pents.remove(best_i)

        print(f"  Greedy pentagon cover: {len(cover)} pentagons needed")
        total_in_cover = sum(5 for _ in cover)
        shared = total_in_cover - size + len(uncovered)
        print(f"  Total ray slots: {total_in_cover}, unique rays covered: {size - len(uncovered)}, "
              f"uncovered: {len(uncovered)}")
        for i, (pi, pent, new) in enumerate(cover):
            print(f"    Pentagon {i+1}: {sorted(pent)} (covered {new} new vertices)")
        if uncovered:
            print(f"    Uncovered vertices: {sorted(uncovered)}")

    # Chromatic analysis of the pentagon subgraph
    print(f"\n--- Odd cycle analysis ---")
    # Count odd cycles of all lengths
    print(f"  3-cycles (triangles/bases): {len(triangles)}")
    print(f"  5-cycles (pentagons): {len(pentagons)}")

    # Count 7-cycles
    seven_cycles = 0
    for combo in combinations(range(size), 7):
        sub = G.subgraph(combo)
        if sub.number_of_edges() == 7:
            degs = [sub.degree(v) for v in combo]
            if all(d == 2 for d in degs):
                seven_cycles += 1
    print(f"  7-cycles (heptagons): {seven_cycles}")

    return pentagons, structures_found


# =====================================================================
# Build KS sets
# =====================================================================
print("=" * 70)
print("10-RAY BASIC STRUCTURE ANALYSIS")
print("=" * 70)

OMEGA = cmath.exp(2j * cmath.pi / 3)
sqrt2 = np.sqrt(2)

# 1. CK-31 (Integer)
print("\n--- Building CK-31 (Integer) ---")
ck31 = build_ks_set("CK-31", [0, 1, -1, 2, -2])

# 2. Peres-33 (sqrt(2))
print("\n--- Building Peres-33 ---")
peres33 = build_ks_set("Peres-33", [0, 1, -1, sqrt2, -sqrt2])

# 3. Eisenstein-33
print("\n--- Building Eisenstein-33 ---")
eis33 = build_ks_set("Eisenstein-33", [0, 1, -1, OMEGA, -OMEGA,
                                        OMEGA.conjugate(), -OMEGA.conjugate()])

# =====================================================================
# Analyze each
# =====================================================================
results = {}

if ck31:
    rays, pairs, triads, size = ck31
    p, s = analyze_ks_structure("CK-31", rays, pairs, triads, size)
    results["CK-31"] = (p, s)

if peres33:
    rays, pairs, triads, size = peres33
    p, s = analyze_ks_structure("Peres-33", rays, pairs, triads, size)
    results["Peres-33"] = (p, s)

if eis33:
    rays, pairs, triads, size = eis33
    p, s = analyze_ks_structure("Eisenstein-33", rays, pairs, triads, size)
    results["Eisenstein-33"] = (p, s)

# =====================================================================
# Comparative summary
# =====================================================================
print(f"\n{'='*70}")
print("COMPARATIVE SUMMARY")
print(f"{'='*70}")

for name in ["CK-31", "Peres-33", "Eisenstein-33"]:
    if name in results:
        pentagons, structures = results[name]
        ten_ray = [s for s in structures if s['total_rays'] == 10]
        print(f"\n  {name}:")
        print(f"    Pentagons: {len(pentagons)}")
        print(f"    10-ray structures: {len(ten_ray)}")
        print(f"    Pentagon+cap structures (<=12 rays): {len(structures)}")

print(f"\n{'='*70}")
print("DONE")
print(f"{'='*70}")
