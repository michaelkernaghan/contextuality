"""
ks_triad_topology.py — Structural analysis of triad overlap topology
=====================================================================

Negative prompting approach: DO NOT use counting arguments.
Instead, analyze the STRUCTURAL relationships between triads.

In R^3:
- Each triad = orthogonal basis = element of O(3)/permutations
- Two triads sharing a vertex: the shared vector constrains
  both bases to have that vector, creating a rotation relationship
- Two triads sharing an edge: two shared vectors forces the third
  to be determined (up to sign)

Key structural invariant: the "triad overlap graph" where
- nodes = triads
- edges = shared vertices (weight = # shared vertices: 1 or 2)
- If edge has weight 2: the third vertex is algebraically determined

This creates a RIGIDITY PROPAGATION: from one triad, all connected
triads (via shared vertices) have their vectors algebraically determined.

Hypothesis: In CK-31, the triad overlap structure has a property
that allows consistent R^3 realization. In sub-31 hypergraphs,
this structure creates contradictions.

Requires: pip install python-sat numpy networkx
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

import random
import numpy as np
from itertools import combinations
from collections import defaultdict

try:
    from pysat.solvers import Glucose4
except ImportError:
    print("ERROR: pip install python-sat")
    sys.exit(1)

import networkx as nx

random.seed(42)
np.random.seed(42)


def is_uncolorable(n, pairs, triads):
    """Test KS-uncolorability via SAT."""
    clauses = []
    triad_pair_set = set()
    for a, b, c in triads:
        A, B, C = a + 1, b + 1, c + 1
        clauses.append([A, B, C])
        clauses.append([-A, -B])
        clauses.append([-A, -C])
        clauses.append([-B, -C])
        for x, y in combinations([a, b, c], 2):
            triad_pair_set.add((min(x, y), max(x, y)))
    for a, b in pairs:
        key = (min(a, b), max(a, b))
        if key not in triad_pair_set:
            clauses.append([-(a + 1), -(b + 1)])
    with Glucose4() as solver:
        for c in clauses:
            solver.add_clause(c)
        return not solver.solve()


def get_ck31():
    """CK-31 vectors and graph."""
    vecs = [
        (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 1, -1), (0, 1, 2), (0, 2, -1),
        (1, 0, 0), (1, 0, 1), (1, 0, -1), (1, 0, 2), (1, 0, -2),
        (1, 1, 0), (1, 1, 1), (1, 1, -1), (1, 1, 2), (1, -1, 0),
        (1, -1, 1), (1, -1, -1), (1, -1, -2), (1, 2, 0), (1, 2, -1),
        (1, -2, 0), (1, -2, 1), (2, 0, 1), (2, 0, -1), (2, 1, 0),
        (2, 1, 1), (2, 1, -1), (2, -1, 0), (2, -1, 1), (2, -1, -1)
    ]
    n = len(vecs)
    pair_set = set()
    for i in range(n):
        for j in range(i + 1, n):
            if sum(a * b for a, b in zip(vecs[i], vecs[j])) == 0:
                pair_set.add((i, j))
    pairs = sorted(pair_set)
    adj = defaultdict(set)
    for i, j in pairs:
        adj[i].add(j)
        adj[j].add(i)
    triads = []
    for i in range(n):
        for j in adj[i]:
            if j > i:
                for k in (adj[i] & adj[j]):
                    if k > j:
                        triads.append((i, j, k))
    return n, pairs, triads, vecs


def triad_overlap_analysis(n, pairs, triads, label=""):
    """
    Analyze the triad overlap structure.

    Returns dict with structural properties.
    """
    print(f"\n  {'='*50}")
    print(f"  {label}: n={n}, pairs={len(pairs)}, triads={len(triads)}")
    print(f"  {'='*50}")

    # 1. Vertex-triad incidence: how many triads is each vertex in?
    vertex_triad_count = defaultdict(int)
    vertex_triads = defaultdict(list)
    for idx, (a, b, c) in enumerate(triads):
        for v in [a, b, c]:
            vertex_triad_count[v] += 1
            vertex_triads[v].append(idx)

    triad_degrees = sorted(vertex_triad_count.values(), reverse=True)
    in_triad = sum(1 for v in range(n) if vertex_triad_count[v] > 0)
    multi_triad = sum(1 for v in range(n) if vertex_triad_count[v] > 1)

    print(f"  Vertices in triads: {in_triad}/{n}")
    print(f"  Vertices in 2+ triads: {multi_triad}")
    print(f"  Triad degree distribution: {dict(sorted(defaultdict(int, {d: sum(1 for x in triad_degrees if x == d) for d in set(triad_degrees)}).items()))}")

    # 2. Triad overlap graph
    T = nx.Graph()
    for i in range(len(triads)):
        T.add_node(i)

    for i in range(len(triads)):
        for j in range(i + 1, len(triads)):
            shared = len(set(triads[i]) & set(triads[j]))
            if shared > 0:
                T.add_edge(i, j, weight=shared)

    print(f"\n  Triad overlap graph: {T.number_of_nodes()} nodes, {T.number_of_edges()} edges")
    n_components = nx.number_connected_components(T)
    print(f"  Connected components: {n_components}")

    # Edge weights: shared vertices
    w1 = sum(1 for _, _, d in T.edges(data=True) if d['weight'] == 1)
    w2 = sum(1 for _, _, d in T.edges(data=True) if d['weight'] == 2)
    print(f"  Edges with 1 shared vertex: {w1}")
    print(f"  Edges with 2 shared vertices: {w2} (determines 3rd vertex)")

    # 3. Rigidity propagation
    # From any triad, how many triads are reachable via weight-2 edges?
    # Weight-2 edges = maximally rigid (shared edge determines everything)
    T_rigid = nx.Graph()
    for i in range(len(triads)):
        T_rigid.add_node(i)
    for i, j, d in T.edges(data=True):
        if d['weight'] >= 2:
            T_rigid.add_edge(i, j)

    rigid_components = list(nx.connected_components(T_rigid))
    max_rigid = max(len(c) for c in rigid_components) if rigid_components else 0
    print(f"  Rigid propagation (weight>=2 edges):")
    print(f"    Components: {len(rigid_components)}, largest: {max_rigid}")

    # Weight-1 edges: shared vertex gives 1 DOF (rotation in perp plane)
    T_flex = nx.Graph()
    for i in range(len(triads)):
        T_flex.add_node(i)
    for i, j, d in T.edges(data=True):
        if d['weight'] == 1:
            T_flex.add_edge(i, j)

    flex_components = list(nx.connected_components(T_flex))
    print(f"  Flexible connections (weight=1 edges):")
    print(f"    Components: {len(flex_components)}, largest: {max(len(c) for c in flex_components) if flex_components else 0}")

    # 4. Full triad overlap connectivity
    if n_components == 1:
        print(f"  Triad overlap graph is CONNECTED")
        diameter = nx.diameter(T)
        print(f"    Diameter: {diameter}")
    else:
        comp_sizes = sorted([len(c) for c in nx.connected_components(T)], reverse=True)
        print(f"  Triad overlap graph is DISCONNECTED: {comp_sizes}")

    # 5. Vertex in plane perpendicular to another vertex
    # In R^3: if v is in triad (v, a, b), then a,b are in v-perp (a 2D subspace)
    # All neighbors of v that are in triads with v must lie in v-perp
    # How many such constraints per vertex?
    for v in range(n):
        if vertex_triad_count[v] >= 2:
            # All triad-partners of v must lie in v-perp
            partners = set()
            for tidx in vertex_triads[v]:
                for u in triads[tidx]:
                    if u != v:
                        partners.add(u)
            # In R^3, v-perp is 2D. These partners must all be orthogonal
            # to v. Each triad through v picks 2 orthogonal vectors in v-perp.
            # If v is in k triads, we need k pairs of orthogonal vectors in R^2.
            k = vertex_triad_count[v]
            # In R^2, max # mutually orthogonal pairs with distinct directions
            # is limited. If pairs share vectors, they overlap.
            # Key constraint: all partners are in R^2 (v-perp), each triad
            # picks an orthogonal pair. With k triads, we need 2k slots
            # but may share vectors.

    # 6. R^3 plane matching constraint
    # For each vertex v, the triads through v define matchings on v-perp.
    # Count: for vertices with triad-degree >= 3, the constraint is tightest.
    high_degree_verts = [(v, vertex_triad_count[v]) for v in range(n)
                         if vertex_triad_count[v] >= 3]
    if high_degree_verts:
        print(f"\n  Vertices with 3+ triads (tight plane constraint):")
        for v, d in sorted(high_degree_verts, key=lambda x: -x[1]):
            partners = set()
            for tidx in vertex_triads[v]:
                for u in triads[tidx]:
                    if u != v:
                        partners.add(u)
            print(f"    v={v}: in {d} triads, {len(partners)} distinct partners in v-perp")
            # In R^2, with d triads, we need d orthogonal pairs.
            # If all pairs are distinct (2d vectors), we need 2d directions in R^2.
            # But R^2 only has 1 DOF for orthogonal pairs (angle theta gives (cos,sin),(-sin,cos)).
            # So d orthogonal pairs in R^2 correspond to d angles, no constraint unless pairs share vertices.

    return {
        'n': n,
        'pairs': len(pairs),
        'triads': len(triads),
        'in_triad': in_triad,
        'multi_triad': multi_triad,
        'triad_overlap_edges': T.number_of_edges(),
        'triad_overlap_components': n_components,
        'rigid_edges_w2': w2,
        'flex_edges_w1': w1,
        'max_rigid_component': max_rigid,
    }


def main():
    print("=" * 60)
    print("TRIAD TOPOLOGY ANALYSIS")
    print("Structural (not counting) analysis of triad overlap")
    print("=" * 60)

    # CK-31
    n_ck, pairs_ck, triads_ck, vecs_ck = get_ck31()
    ck_result = triad_overlap_analysis(n_ck, pairs_ck, triads_ck, "CK-31 (REALIZABLE)")

    # Generate the 8 hard cases (omega<=3, underconstrained, sub-31)
    # Reproduce from the previous script's logic
    print("\n\n" + "=" * 60)
    print("GENERATING HARD CASES (omega<=3, underconstrained, sub-31)")
    print("=" * 60)

    # Generate via merge + random
    adj_ck = defaultdict(set)
    for i, j in pairs_ck:
        adj_ck[i].add(j)
        adj_ck[j].add(i)

    hard_cases = []

    # Random abstract generation with controlled parameters
    for trial in range(100000):
        n = random.randint(28, 30)
        n_triads = random.randint(14, 18)

        triads = set()
        attempts = 0
        while len(triads) < n_triads and attempts < 200:
            t = tuple(sorted(random.sample(range(n), 3)))
            triads.add(t)
            attempts += 1
        triads = sorted(triads)

        pair_set = set()
        for a, b, c in triads:
            pair_set.add((a, b))
            pair_set.add((a, c))
            pair_set.add((b, c))
        # Fewer extra pairs to stay underconstrained
        n_extra = random.randint(5, 15)
        for _ in range(n_extra):
            a, b = sorted(random.sample(range(n), 2))
            pair_set.add((a, b))
        pairs = sorted(pair_set)

        # Quick filters
        m = len(pairs)
        if 2 * n - m - 3 < 0:
            continue  # overconstrained

        # Check clique
        G = nx.Graph()
        G.add_nodes_from(range(n))
        for a, b in pairs:
            G.add_edge(a, b)
        cliques = list(nx.find_cliques(G))
        omega = max(len(c) for c in cliques) if cliques else 0
        if omega > 3:
            continue

        if is_uncolorable(n, pairs, triads):
            hard_cases.append((n, pairs, triads))
            if len(hard_cases) >= 20:
                break

    print(f"  Found {len(hard_cases)} hard cases (omega<=3, underconstrained, uncolorable)")

    # Analyze each
    hard_results = []
    for idx, (n, pairs, triads) in enumerate(hard_cases):
        r = triad_overlap_analysis(n, pairs, triads, f"HARD CASE #{idx+1} (ABSTRACT, NOT REALIZABLE)")
        hard_results.append(r)

    # Comparison
    print("\n\n" + "=" * 60)
    print("STRUCTURAL COMPARISON")
    print("=" * 60)

    print(f"\n  {'Property':<35} {'CK-31':>10} {'Hard avg':>10} {'Hard range':>15}")
    print(f"  {'-'*35} {'-'*10} {'-'*10} {'-'*15}")

    if hard_results:
        props = ['triads', 'in_triad', 'multi_triad', 'triad_overlap_edges',
                 'triad_overlap_components', 'rigid_edges_w2', 'flex_edges_w1',
                 'max_rigid_component']
        for p in props:
            ck_val = ck_result[p]
            vals = [r[p] for r in hard_results]
            avg = np.mean(vals)
            rng = f"{min(vals)}-{max(vals)}"
            print(f"  {p:<35} {ck_val:>10} {avg:>10.1f} {rng:>15}")

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)


if __name__ == '__main__':
    main()
