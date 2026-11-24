"""
ks_generator_subgraph.py -- Search for common 10-ray "generator" subgraphs
==========================================================================

The classic KS "generator" (or Gamma graph / basic KS gadget) is a 10-ray
subgraph that appears in every KS construction going back to the original
117-vector Kochen-Specker set. It consists of 10 rays forming interlocking
orthogonal triples that create the "tension" needed for uncolorability.

This script:
1. Constructs the CK-31 orthogonality graph (from integer pool)
2. Constructs the Peres-33 orthogonality graph (exact coordinates)
3. Searches for common 10-ray induced subgraphs with >= 5 triads
4. Uses VF2 subgraph isomorphism to identify shared patterns
5. Reports which patterns appear in both sets and how many copies
"""

import sys
sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

import math
import random
import itertools
from collections import Counter, defaultdict

import networkx as nx
from networkx.algorithms import isomorphism

random.seed(42)

S2 = math.sqrt(2)
EPS = 1e-10


# =====================================================================
# Helper functions (matching project conventions)
# =====================================================================

def dot(u, v):
    return sum(a * b for a, b in zip(u, v))


def is_orthogonal(u, v, tol=1e-9):
    return abs(dot(u, v)) < tol


def ray_key(v):
    """Canonical key for a real ray: normalize, first nonzero > 0."""
    n = math.sqrt(dot(v, v))
    nv = tuple(c / n for c in v)
    for c in nv:
        if abs(c) > EPS:
            if c < 0:
                nv = tuple(-x for x in nv)
            break
    return tuple(round(x, 8) for x in nv)


def fmt_vec(v):
    """Format a vector for display."""
    def c(x):
        if abs(x) < EPS: return "0"
        if abs(x - 1) < EPS: return "1"
        if abs(x + 1) < EPS: return "-1"
        if abs(x - 2) < EPS: return "2"
        if abs(x + 2) < EPS: return "-2"
        if abs(x - S2) < EPS: return "s2"
        if abs(x + S2) < EPS: return "-s2"
        return f"{x:.3f}"
    return f"({c(v[0])}, {c(v[1])}, {c(v[2])})"


# =====================================================================
# Build Peres 33-vector set (exact coordinates from verify_peres33.py)
# =====================================================================

def build_peres33():
    """Return the Peres 33-vector KS set with exact coordinates."""
    vectors = [
        # Type I: Coordinate axes (3 vectors)
        (1, 0, 0), (0, 1, 0), (0, 0, 1),
        # Type II: Face diagonals (6 vectors)
        (1, 1, 0), (1, -1, 0), (1, 0, 1), (1, 0, -1), (0, 1, 1), (0, 1, -1),
        # Type III: Mixed sqrt(2)-1-0 (12 vectors)
        (S2, 1, 0), (S2, -1, 0), (1, S2, 0), (1, -S2, 0),
        (S2, 0, 1), (S2, 0, -1), (1, 0, S2), (1, 0, -S2),
        (0, S2, 1), (0, S2, -1), (0, 1, S2), (0, 1, -S2),
        # Type IV: sqrt(2)-1-1 (12 vectors)
        (1, 1, S2), (1, -1, S2), (1, 1, -S2), (1, -1, -S2),
        (1, S2, 1), (1, S2, -1), (1, -S2, 1), (1, -S2, -1),
        (S2, 1, 1), (S2, 1, -1), (S2, -1, 1), (S2, -1, -1),
    ]
    return vectors


# =====================================================================
# Build CK-31 from integer alphabet
# =====================================================================

def build_ck31():
    """Build the CK-31 set from integer alphabet {0, +/-1, +/-2}.

    Returns the 49-ray integer pool and extracts a minimal 31-ray subset.
    Uses SAT-based minimization matching the project pattern.
    """
    from ks_complex import hermitian_dot, canonicalize_complex_ray
    from ks_new_islands import generate_rays_from_alphabet, sat_minimize

    alph = [complex(x) for x in [0, 1, -1, 2, -2]]
    rays_complex = generate_rays_from_alphabet(alph)

    # Convert to real tuples
    rays_real = [(r[0].real, r[1].real, r[2].real) for r in rays_complex]

    # Build pairs and triads
    n = len(rays_real)
    pairs = []
    pair_set = set()
    for i in range(n):
        for j in range(i + 1, n):
            if is_orthogonal(rays_real[i], rays_real[j]):
                pairs.append((i, j))
                pair_set.add((i, j))

    triads = []
    for i in range(n):
        for j in range(i + 1, n):
            if (i, j) not in pair_set:
                continue
            for k in range(j + 1, n):
                if (i, k) in pair_set and (j, k) in pair_set:
                    triads.append((i, j, k))

    print(f"  Integer pool: {n} rays, {len(pairs)} pairs, {len(triads)} triads")

    # SAT-minimize to get CK-31
    from ks_sat import is_uncolorable as sat_uncolorable

    best_size = n
    best_subset = list(range(n))

    for trial in range(500):
        current = list(range(n))
        random.shuffle(current)
        removed = True
        while removed:
            removed = False
            order = list(current)
            random.shuffle(order)
            for r in order:
                candidate = [x for x in current if x != r]
                if len(candidate) < 3:
                    break
                s = set(candidate)
                remap = {old: new for new, old in enumerate(sorted(candidate))}
                sp = [(remap[a], remap[b]) for a, b in pairs if a in s and b in s]
                st = [(remap[a], remap[b], remap[c]) for a, b, c in triads
                      if a in s and b in s and c in s]
                if st and sat_uncolorable(len(candidate), sp, st):
                    current = candidate
                    removed = True
                    break

        size = len(current)
        if size < best_size:
            best_size = size
            best_subset = current

    # Extract the rays for the minimal subset
    ck31_rays = [rays_real[i] for i in sorted(best_subset)]
    print(f"  CK-31 minimal: {best_size} rays")
    return ck31_rays


# =====================================================================
# Build orthogonality graph and find triads
# =====================================================================

def build_ortho_graph(rays):
    """Build a NetworkX orthogonality graph and find all triads."""
    n = len(rays)
    G = nx.Graph()
    G.add_nodes_from(range(n))

    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            if is_orthogonal(rays[i], rays[j]):
                G.add_edge(i, j)
                pairs.append((i, j))

    # Find all triads (triangles = mutually orthogonal triples)
    triads = []
    for i in range(n):
        nbrs_i = set(G.neighbors(i))
        for j in nbrs_i:
            if j <= i:
                continue
            for k in (nbrs_i & set(G.neighbors(j))):
                if k <= j:
                    continue
                triads.append((i, j, k))

    return G, pairs, triads


# =====================================================================
# Find all 10-ray induced subgraphs with >= k triads
# =====================================================================

def find_triad_rich_subgraphs(G, triads, rays, target_size=10, min_triads=5,
                                max_candidates=50000, sample_size=100000):
    """Find 10-ray induced subgraphs that are 'triad-rich'.

    Strategy: Start from triads and grow by adding connected rays.
    This is much more efficient than brute-force C(n,10).
    """
    n = G.number_of_nodes()

    # Build triad index: for each node, which triads contain it
    node_triads = defaultdict(list)
    for t_idx, (a, b, c) in enumerate(triads):
        node_triads[a].append(t_idx)
        node_triads[b].append(t_idx)
        node_triads[c].append(t_idx)

    # Strategy: grow from pairs of triads that share a ray
    candidates = set()

    # For each pair of triads sharing at least one ray, form their union
    # and try to grow to target_size
    triad_sets = [frozenset(t) for t in triads]

    # Method 1: Union of triad pairs that share an edge/vertex
    seed_sets = set()
    for i in range(len(triads)):
        for j in range(i + 1, len(triads)):
            union = triad_sets[i] | triad_sets[j]
            if len(union) <= target_size:
                seed_sets.add(frozenset(union))

    print(f"    Triad-pair seeds: {len(seed_sets)}")

    # Method 2: Union of triad triples
    triad_triple_seeds = set()
    for i in range(len(triads)):
        for j in range(i + 1, len(triads)):
            if not (triad_sets[i] & triad_sets[j]):
                continue  # Skip disconnected pairs
            for k in range(j + 1, len(triads)):
                union = triad_sets[i] | triad_sets[j] | triad_sets[k]
                if len(union) <= target_size and (triad_sets[j] & triad_sets[k] or
                                                    triad_sets[i] & triad_sets[k]):
                    triad_triple_seeds.add(frozenset(union))

    print(f"    Triad-triple seeds: {len(triad_triple_seeds)}")
    seed_sets |= triad_triple_seeds

    # Grow each seed to exactly target_size by adding neighbors
    results = {}

    for seed in seed_sets:
        if len(seed) == target_size:
            # Check triads
            sub_triads = count_triads_in_subset(seed, triads)
            if sub_triads >= min_triads:
                sg = frozenset(seed)
                if sg not in results:
                    results[sg] = sub_triads
            continue

        if len(seed) > target_size:
            continue

        # Grow by adding neighbors
        need = target_size - len(seed)
        # Find all neighbors of the seed
        nbrs = set()
        for v in seed:
            nbrs |= set(G.neighbors(v))
        nbrs -= seed

        if len(nbrs) < need:
            continue

        # Try random subsets of neighbors
        nbrs_list = sorted(nbrs)
        if len(nbrs_list) <= 15:
            # Enumerate all
            for combo in itertools.combinations(nbrs_list, need):
                full = frozenset(seed | set(combo))
                sub_triads = count_triads_in_subset(full, triads)
                if sub_triads >= min_triads:
                    if full not in results:
                        results[full] = sub_triads
        else:
            # Sample
            for _ in range(min(200, len(nbrs_list) ** 2)):
                combo = random.sample(nbrs_list, need)
                full = frozenset(seed | set(combo))
                sub_triads = count_triads_in_subset(full, triads)
                if sub_triads >= min_triads:
                    if full not in results:
                        results[full] = sub_triads

    return results


def count_triads_in_subset(subset, triads):
    """Count how many triads have all three vertices in the subset."""
    s = set(subset)
    count = 0
    for a, b, c in triads:
        if a in s and b in s and c in s:
            count += 1
    return count


# =====================================================================
# Compute graph isomorphism class of induced subgraphs
# =====================================================================

def subgraph_canonical_form(G, nodes):
    """Get a canonical form for the induced subgraph on given nodes.

    Returns the sorted degree sequence and sorted edge list (relabeled)
    as a hashable key.
    """
    sub = G.subgraph(nodes)
    # Relabel nodes to 0..k-1
    mapping = {v: i for i, v in enumerate(sorted(nodes))}
    relabeled = nx.relabel_nodes(sub, mapping)

    # Use graph6 string as canonical form (fast for small graphs)
    return nx.to_graph6_bytes(relabeled)


def classify_subgraphs(G, subgraph_dict):
    """Group subgraphs by isomorphism class using graph6 encoding + VF2."""
    classes = {}  # canonical_form -> list of subgraph nodesets

    for nodes, n_triads in subgraph_dict.items():
        canon = subgraph_canonical_form(G, nodes)
        if canon not in classes:
            classes[canon] = []
        classes[canon].append((nodes, n_triads))

    return classes


# =====================================================================
# VF2-based common subgraph search
# =====================================================================

def find_common_subgraphs_vf2(G1, G2, subgraphs1, subgraphs2):
    """Find isomorphism classes that appear in both G1 and G2.

    Uses VF2 to compare representative subgraphs from each set.
    """
    classes1 = classify_subgraphs(G1, subgraphs1)
    classes2 = classify_subgraphs(G2, subgraphs2)

    print(f"\n  CK-31 isomorphism classes: {len(classes1)}")
    print(f"  Peres-33 isomorphism classes: {len(classes2)}")

    # Direct match on graph6 canonical form
    common_direct = set(classes1.keys()) & set(classes2.keys())

    # Also check VF2 between representatives of different graph6 forms
    # (graph6 is already canonical for labeled graphs, but we need
    #  unlabeled isomorphism)
    # Actually, graph6 from a consistently-relabeled graph may not be
    # canonical under isomorphism. Use networkx.is_isomorphic instead.

    # Build representative graphs for each class
    reps1 = {}
    for canon, entries in classes1.items():
        nodes = entries[0][0]
        reps1[canon] = G1.subgraph(nodes).copy()

    reps2 = {}
    for canon, entries in classes2.items():
        nodes = entries[0][0]
        reps2[canon] = G2.subgraph(nodes).copy()

    common = []
    for c1, g1 in reps1.items():
        for c2, g2 in reps2.items():
            if nx.is_isomorphic(g1, g2):
                common.append((c1, c2, len(classes1[c1]), len(classes2[c2])))

    return common, classes1, classes2


# =====================================================================
# Build the "classic" KS generator pattern
# =====================================================================

def build_classic_generator():
    """Build the classic 10-ray KS generator (Gamma graph).

    The generator consists of 10 rays forming 5 orthogonal triads
    arranged in a chain where consecutive triads share exactly one ray.
    This creates a "parity argument" that blocks consistent coloring
    when the chain closes.

    The graph structure is: 5 triangles (triads) connected in a line,
    sharing edges/vertices in a specific pattern.

    Pattern (Kochen-Specker 1967, simplified):
      Triad 1: {a, b, c}
      Triad 2: {c, d, e}      (shares c with T1)
      Triad 3: {e, f, g}      (shares e with T2)
      Triad 4: {g, h, i}      (shares g with T3)
      Triad 5: {i, j, a}      (shares i with T4, closes to a from T1)

    This gives 10 rays {a..j} in 5 triads forming a cycle.
    The cycle of length 5 (odd) creates the coloring obstruction.
    """
    G = nx.Graph()
    # 10 nodes: 0-9
    # 5 triads forming a cycle:
    # T1: {0, 1, 2}
    # T2: {2, 3, 4}
    # T3: {4, 5, 6}
    # T4: {6, 7, 8}
    # T5: {8, 9, 0}
    triads = [(0,1,2), (2,3,4), (4,5,6), (6,7,8), (8,9,0)]
    for a, b, c in triads:
        G.add_edge(a, b)
        G.add_edge(a, c)
        G.add_edge(b, c)
    return G, triads


def build_linear_generator():
    """Build a linear (non-cyclic) generator: 5 triads in a chain.

    T1: {0, 1, 2}
    T2: {2, 3, 4}
    T3: {4, 5, 6}
    T4: {6, 7, 8}
    T5: {8, 9, ...}  -- doesn't close

    This is 10 rays in 5 triads, linear chain.
    """
    G = nx.Graph()
    triads = [(0,1,2), (2,3,4), (4,5,6), (6,7,8), (8,9,0)]
    # Actually make a linear version without the cycle closure
    triads_linear = [(0,1,2), (2,3,4), (4,5,6), (6,7,8), (7,8,9)]
    for a, b, c in triads_linear:
        G.add_edge(a, b)
        G.add_edge(a, c)
        G.add_edge(b, c)
    return G, triads_linear


# =====================================================================
# Search for the classic generator as a subgraph
# =====================================================================

def search_for_generator(G_target, generator_G, name=""):
    """Search for the generator pattern as an induced subgraph of G_target."""
    GM = isomorphism.GraphMatcher(G_target, generator_G)

    count = 0
    examples = []
    seen = set()

    for mapping in GM.subgraph_isomorphisms_iter():
        # mapping: target_node -> generator_node
        target_nodes = frozenset(mapping.keys())
        if target_nodes in seen:
            continue
        seen.add(target_nodes)
        count += 1
        if count <= 5:
            examples.append(sorted(target_nodes))

    return count, examples


# =====================================================================
# Main analysis
# =====================================================================

def main():
    print("=" * 70)
    print("KS GENERATOR SUBGRAPH ANALYSIS")
    print("=" * 70)
    print("Searching for common 10-ray 'generator' subgraphs in CK-31 and Peres-33")
    print()

    # -----------------------------------------------------------------
    # Step 1: Build Peres-33
    # -----------------------------------------------------------------
    print("STEP 1: Building Peres-33 orthogonality graph")
    print("-" * 50)
    peres_rays = build_peres33()
    G_peres, peres_pairs, peres_triads = build_ortho_graph(peres_rays)
    print(f"  Peres-33: {len(peres_rays)} rays, {len(peres_pairs)} pairs, "
          f"{len(peres_triads)} triads")

    deg_peres = sorted([G_peres.degree(i) for i in range(len(peres_rays))])
    print(f"  Degree sequence: {deg_peres}")
    print()

    # -----------------------------------------------------------------
    # Step 2: Build CK-31
    # -----------------------------------------------------------------
    print("STEP 2: Building CK-31 from integer pool")
    print("-" * 50)
    ck31_rays = build_ck31()
    G_ck31, ck31_pairs, ck31_triads = build_ortho_graph(ck31_rays)
    print(f"  CK-31: {len(ck31_rays)} rays, {len(ck31_pairs)} pairs, "
          f"{len(ck31_triads)} triads")

    deg_ck31 = sorted([G_ck31.degree(i) for i in range(len(ck31_rays))])
    print(f"  Degree sequence: {deg_ck31}")
    print()

    # -----------------------------------------------------------------
    # Step 3: Search for the classic cyclic 5-triad generator
    # -----------------------------------------------------------------
    print("STEP 3: Searching for classic cyclic 5-triad generator (Gamma graph)")
    print("-" * 50)

    gen_cyclic, gen_cyclic_triads = build_classic_generator()
    print(f"  Generator: {gen_cyclic.number_of_nodes()} nodes, "
          f"{gen_cyclic.number_of_edges()} edges, {len(gen_cyclic_triads)} triads")
    print(f"  Generator degree sequence: {sorted(d for _, d in gen_cyclic.degree())}")

    print("\n  Searching in Peres-33...")
    n_peres_gen, ex_peres = search_for_generator(G_peres, gen_cyclic, "Peres-33")
    print(f"    Found {n_peres_gen} copies of cyclic generator in Peres-33")
    for ex in ex_peres[:3]:
        print(f"      Example nodes: {ex}")
        print(f"        Rays: {[fmt_vec(peres_rays[i]) for i in ex]}")

    print("\n  Searching in CK-31...")
    n_ck31_gen, ex_ck31 = search_for_generator(G_ck31, gen_cyclic, "CK-31")
    print(f"    Found {n_ck31_gen} copies of cyclic generator in CK-31")
    for ex in ex_ck31[:3]:
        print(f"      Example nodes: {ex}")
        print(f"        Rays: {[fmt_vec(ck31_rays[i]) for i in ex]}")

    print()

    # -----------------------------------------------------------------
    # Step 4: Search for triad-rich 10-ray subgraphs
    # -----------------------------------------------------------------
    print("STEP 4: Enumerating triad-rich 10-ray induced subgraphs")
    print("-" * 50)

    for min_t in [5, 4, 3]:
        print(f"\n  --- Min triads = {min_t} ---")

        print(f"  Searching in Peres-33...")
        peres_subs = find_triad_rich_subgraphs(
            G_peres, peres_triads, peres_rays, target_size=10, min_triads=min_t)
        print(f"    Found {len(peres_subs)} subgraphs with >= {min_t} triads")

        if peres_subs:
            triad_counts_p = Counter(peres_subs.values())
            print(f"    Triad count distribution: {dict(sorted(triad_counts_p.items()))}")

        print(f"  Searching in CK-31...")
        ck31_subs = find_triad_rich_subgraphs(
            G_ck31, ck31_triads, ck31_rays, target_size=10, min_triads=min_t)
        print(f"    Found {len(ck31_subs)} subgraphs with >= {min_t} triads")

        if ck31_subs:
            triad_counts_c = Counter(ck31_subs.values())
            print(f"    Triad count distribution: {dict(sorted(triad_counts_c.items()))}")

        if peres_subs and ck31_subs:
            print(f"\n  Finding common isomorphism classes (VF2)...")
            common, classes1, classes2 = find_common_subgraphs_vf2(
                G_ck31, G_peres, ck31_subs, peres_subs)

            print(f"  Common isomorphism classes: {len(common)}")
            for c1, c2, count1, count2 in common[:10]:
                # Get representative from CK-31
                rep_nodes = classes1[c1][0][0]
                rep_triads = classes1[c1][0][1]
                sub = G_ck31.subgraph(rep_nodes)
                deg_seq = sorted(d for _, d in sub.degree())
                print(f"    Class: {count1} copies in CK-31, {count2} copies in Peres-33")
                print(f"      Degree seq: {deg_seq}, triads: {rep_triads}")
                print(f"      Edges: {sub.number_of_edges()}")

                # Show one example from each
                ck_ex = sorted(classes1[c1][0][0])
                pe_ex = sorted(classes2[c2][0][0])
                print(f"      CK-31 example: nodes {ck_ex}")
                print(f"        Rays: {[fmt_vec(ck31_rays[i]) for i in ck_ex]}")
                print(f"      Peres-33 example: nodes {pe_ex}")
                print(f"        Rays: {[fmt_vec(peres_rays[i]) for i in pe_ex]}")

            if min_t >= 4:
                break  # Found enough, no need to go lower

    # -----------------------------------------------------------------
    # Step 5: Direct comparison - specific known generator patterns
    # -----------------------------------------------------------------
    print("\n" + "=" * 70)
    print("STEP 5: Specific generator pattern searches")
    print("=" * 70)

    # The Peres proof uses a chain of triads. Let's extract the proof chain.
    # From verify_peres33.py, the proof uses triads:
    # T1(1,2,3), T4(3,4,5), T3(2,6,7), T2(1,8,9)
    # These share axes 1,2,3. This is a star-like gadget.

    # Build a "star gadget": 3 triads sharing one ray (the hub)
    # Hub: axis ray, spokes: 3 triads emanating from it
    print("\n  Pattern A: Star gadget (3 triads sharing one hub ray)")
    star = nx.Graph()
    # Hub at 0, triads: {0,1,2}, {0,3,4}, {0,5,6}
    star_triads = [(0,1,2), (0,3,4), (0,5,6)]
    for a, b, c in star_triads:
        star.add_edge(a, b)
        star.add_edge(a, c)
        star.add_edge(b, c)

    n_p, ex_p = search_for_generator(G_peres, star, "Peres-33")
    n_c, ex_c = search_for_generator(G_ck31, star, "CK-31")
    print(f"    Peres-33: {n_p} copies")
    print(f"    CK-31: {n_c} copies")

    # 4 triads sharing a hub
    print("\n  Pattern B: Hub-4 gadget (4 triads sharing one hub ray)")
    hub4 = nx.Graph()
    hub4_triads = [(0,1,2), (0,3,4), (0,5,6), (0,7,8)]
    for a, b, c in hub4_triads:
        hub4.add_edge(a, b)
        hub4.add_edge(a, c)
        hub4.add_edge(b, c)
    # 9 nodes

    n_p, ex_p = search_for_generator(G_peres, hub4, "Peres-33")
    n_c, ex_c = search_for_generator(G_ck31, hub4, "CK-31")
    print(f"    Peres-33: {n_p} copies")
    print(f"    CK-31: {n_c} copies")

    # Chain of 3 triads: T1-T2-T3 sharing single rays
    print("\n  Pattern C: Linear chain of 3 triads")
    chain3 = nx.Graph()
    # {0,1,2}, {2,3,4}, {4,5,6}
    chain3_triads = [(0,1,2), (2,3,4), (4,5,6)]
    for a, b, c in chain3_triads:
        chain3.add_edge(a, b)
        chain3.add_edge(a, c)
        chain3.add_edge(b, c)

    n_p, ex_p = search_for_generator(G_peres, chain3, "Peres-33")
    n_c, ex_c = search_for_generator(G_ck31, chain3, "CK-31")
    print(f"    Peres-33: {n_p} copies")
    print(f"    CK-31: {n_c} copies")

    # Chain of 4 triads
    print("\n  Pattern D: Linear chain of 4 triads (10 rays)")
    chain4 = nx.Graph()
    chain4_triads = [(0,1,2), (2,3,4), (4,5,6), (6,7,8)]
    for a, b, c in chain4_triads:
        chain4.add_edge(a, b)
        chain4.add_edge(a, c)
        chain4.add_edge(b, c)
    # 9 nodes, add 10th
    # Actually, let's make it 4 triads on 10 nodes with branching
    # {0,1,2}, {2,3,4}, {4,5,6}, {6,7,8} = 9 nodes
    # Add: {8,9,0} to make it cyclic (same as gen_cyclic with 5 triads on 10)
    # Or: {1,8,9} to create a branch = 10 nodes, 4 triads + 1
    # Let's keep it simple: 4 triads linear on 9 nodes

    n_p, ex_p = search_for_generator(G_peres, chain4, "Peres-33")
    n_c, ex_c = search_for_generator(G_ck31, chain4, "CK-31")
    print(f"    Peres-33: {n_p} copies (9 rays, 4 triads)")
    print(f"    CK-31: {n_c} copies (9 rays, 4 triads)")

    # -----------------------------------------------------------------
    # Step 6: Exhaustive common subgraph comparison at smaller sizes
    # -----------------------------------------------------------------
    print("\n" + "=" * 70)
    print("STEP 6: Common subgraph patterns at various sizes")
    print("=" * 70)

    for size in [7, 8, 9]:
        print(f"\n  --- Size {size}, min triads = 3 ---")

        peres_subs = find_triad_rich_subgraphs(
            G_peres, peres_triads, peres_rays, target_size=size, min_triads=3)
        ck31_subs = find_triad_rich_subgraphs(
            G_ck31, ck31_triads, ck31_rays, target_size=size, min_triads=3)

        print(f"    Peres-33: {len(peres_subs)} subgraphs")
        print(f"    CK-31: {len(ck31_subs)} subgraphs")

        if peres_subs and ck31_subs:
            common, cl1, cl2 = find_common_subgraphs_vf2(
                G_ck31, G_peres, ck31_subs, peres_subs)
            print(f"    Common isomorphism classes: {len(common)}")
            for c1, c2, cnt1, cnt2 in common[:5]:
                rep = G_ck31.subgraph(cl1[c1][0][0])
                deg = sorted(d for _, d in rep.degree())
                print(f"      {cnt1}x in CK-31, {cnt2}x in Peres-33, "
                      f"deg={deg}, triads={cl1[c1][0][1]}")

    # -----------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"CK-31: {len(ck31_rays)} rays, {len(ck31_pairs)} orthogonal pairs, "
          f"{len(ck31_triads)} triads")
    print(f"Peres-33: {len(peres_rays)} rays, {len(peres_pairs)} orthogonal pairs, "
          f"{len(peres_triads)} triads")
    print()

    if n_peres_gen > 0 and n_ck31_gen > 0:
        print("RESULT: The classic cyclic 5-triad generator (Gamma graph) is present")
        print(f"  in BOTH sets: {n_ck31_gen} copies in CK-31, {n_peres_gen} copies in Peres-33.")
    elif n_peres_gen == 0 and n_ck31_gen == 0:
        print("RESULT: The classic cyclic 5-triad generator is NOT present in either set.")
        print("  This is expected -- the 10-ray cyclic generator from the original 117-vector")
        print("  proof may be too large/specific for the minimal 31/33-vector sets.")
        print("  The common substructures found above represent the actual shared 'gadgets'.")
    else:
        print(f"RESULT: Cyclic generator found in {'CK-31' if n_ck31_gen > 0 else 'Peres-33'} "
              f"but not the other.")


if __name__ == "__main__":
    main()
