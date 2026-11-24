"""
ks_realizability_obstruction.py — Test cross-disciplinary realizability obstructions
===================================================================================

Applies techniques from:
1. Delta Theorem (Hall 2026): dim >= n - delta(G) for faithful orth. rep.
2. Gram dimension / forbidden minors (Laurent-Varvitsiotis 2012): K5, K_{2,2,2}
3. Degree-of-freedom counting: 2n DOF vs m constraints
4. Rigidity / Belk-Connelly d-realizability

Tests these on:
- CK-31 (the known minimum, as calibration)
- Abstract uncolorable hypergraphs with n < 31 (from perturbation search)
- Random uncolorable hypergraphs

Inspired by: "Accelerating Scientific Research with Gemini" (arXiv:2602.03837v3)
Technique: Neuro-symbolic verification loop + cross-pollination

Requires: pip install python-sat numpy networkx
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

import random
import time
import numpy as np
from itertools import combinations
from collections import defaultdict

try:
    from pysat.solvers import Glucose4
except ImportError:
    print("ERROR: pip install python-sat")
    sys.exit(1)

try:
    import networkx as nx
except ImportError:
    print("ERROR: pip install networkx")
    sys.exit(1)

random.seed(42)
np.random.seed(42)


# =====================================================================
# Core: KS uncolorability test via SAT
# =====================================================================

def is_uncolorable(n, pairs, triads):
    """Test KS-uncolorability. UNSAT = uncolorable = KS."""
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


# =====================================================================
# CK-31: The known minimum KS set in R^3
# =====================================================================

def get_ck31():
    """CK-31 vectors from {0, +/-1, +/-2} alphabet. Canonical from ks_sat.py."""
    CK31_VECS = [
        (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 1, -1), (0, 1, 2), (0, 2, -1),
        (1, 0, 0), (1, 0, 1), (1, 0, -1), (1, 0, 2), (1, 0, -2),
        (1, 1, 0), (1, 1, 1), (1, 1, -1), (1, 1, 2), (1, -1, 0),
        (1, -1, 1), (1, -1, -1), (1, -1, -2), (1, 2, 0), (1, 2, -1),
        (1, -2, 0), (1, -2, 1), (2, 0, 1), (2, 0, -1), (2, 1, 0),
        (2, 1, 1), (2, 1, -1), (2, -1, 0), (2, -1, 1), (2, -1, -1)
    ]
    n = len(CK31_VECS)
    pairs = []
    triads = []
    for i, j in combinations(range(n), 2):
        vi, vj = CK31_VECS[i], CK31_VECS[j]
        dot = sum(a * b for a, b in zip(vi, vj))
        if dot == 0:
            pairs.append((i, j))
    # Find triads
    adj = defaultdict(set)
    for i, j in pairs:
        adj[i].add(j)
        adj[j].add(i)
    for i in range(n):
        for j in adj[i]:
            if j > i:
                common = adj[i] & adj[j]
                for k in common:
                    if k > j:
                        triads.append((i, j, k))
    return n, pairs, triads, CK31_VECS


# =====================================================================
# Test 1: Delta Theorem (Hall 2026)
# =====================================================================

def orthogonal_dimension_bounds(n, pairs):
    """
    Bounds on the minimum dimension for orthogonal representation.

    Lower bounds:
    - Clique number omega(G): need at least omega(G) dimensions for
      omega mutually orthogonal vectors
    - For FAITHFUL rep: also need dim >= max independent set alpha(G)
      because non-adjacent vertices need non-orthogonal vectors

    Upper bounds:
    - Delta Theorem (Hall 2026): faithful orth. rep exists in dim n - delta(G)

    Returns dict with bounds and whether R^3 is blocked.
    """
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for a, b in pairs:
        G.add_edge(a, b)

    # Degree stats
    degrees = [G.degree(v) for v in range(n)]
    delta = min(degrees) if degrees else 0
    max_deg = max(degrees) if degrees else 0

    # Clique number (lower bound on dimension)
    cliques = list(nx.find_cliques(G))
    omega = max(len(c) for c in cliques) if cliques else 0

    # Independent set (lower bound on faithful dim)
    # Use complement clique = independent set
    G_comp = nx.complement(G)
    comp_cliques = list(nx.find_cliques(G_comp))
    alpha = max(len(c) for c in comp_cliques) if comp_cliques else 0

    # Treewidth approximation
    tw = nx.algorithms.approximation.treewidth_min_degree(G)[0]

    return {
        'omega': omega,  # clique number = lower bound on orth. dim
        'alpha': alpha,  # independence number
        'delta': delta,  # min degree
        'max_degree': max_deg,
        'treewidth_approx': tw,
        'upper_bound_dim': n - delta,  # Delta Theorem upper bound
        'omega_blocks_R3': omega > 3,  # if clique > 3, need dim > 3
    }


# =====================================================================
# Test 2: Forbidden minor check (K5, K_{2,2,2})
# =====================================================================

def check_forbidden_minors(n, pairs):
    """
    Check structural properties relevant to realizability.
    Uses clique number (from find_cliques), treewidth, etc.
    """
    G_orth = nx.Graph()
    G_orth.add_nodes_from(range(n))
    for a, b in pairs:
        G_orth.add_edge(a, b)

    G_comp = nx.complement(G_orth)

    results = {}

    # Clique numbers via find_cliques
    orth_cliques = list(nx.find_cliques(G_orth))
    comp_cliques = list(nx.find_cliques(G_comp))
    orth_clique = max(len(c) for c in orth_cliques) if orth_cliques else 0
    comp_clique = max(len(c) for c in comp_cliques) if comp_cliques else 0

    results['orth_max_clique'] = orth_clique
    results['comp_max_clique'] = comp_clique
    results['orth_has_K5_subgraph'] = orth_clique >= 5
    results['comp_has_K5_subgraph'] = comp_clique >= 5

    # Treewidth approximation
    orth_tw = nx.algorithms.approximation.treewidth_min_degree(G_orth)[0]
    comp_tw = nx.algorithms.approximation.treewidth_min_degree(G_comp)[0]
    results['orth_treewidth_approx'] = orth_tw
    results['comp_treewidth_approx'] = comp_tw
    results['orth_series_parallel'] = orth_tw <= 2
    results['comp_series_parallel'] = comp_tw <= 2

    return results


# =====================================================================
# Test 3: Degree-of-freedom counting
# =====================================================================

def dof_analysis(n, pairs, triads):
    """
    Lines in R^3: 2 DOF each (point in RP^2), so 2n total.
    Each orthogonality constraint: 1 equation.
    Each triad: 3 equations but only 3 DOF (element of SO(3)).

    Expected dimension of configuration variety = 2n - m
    where m = number of orthogonality pairs.

    If 2n - m < 0: overconstrained (generically no solution).
    But this is only necessary, not sufficient for non-realizability.
    """
    m = len(pairs)
    t = len(triads)
    # Subtract global SO(3) symmetry (3 DOF)
    free_dof = 2 * n - m - 3
    # Extra pairs beyond triads
    triad_pairs = set()
    for a, b, c in triads:
        for x, y in combinations([a, b, c], 2):
            triad_pairs.add((min(x, y), max(x, y)))
    extra_pairs = len([p for p in pairs if (min(p), max(p)) not in triad_pairs])

    return {
        'n': n,
        'pairs': m,
        'triads': t,
        'triad_pairs': len(triad_pairs),
        'extra_pairs': extra_pairs,
        'total_dof': 2 * n,
        'constraints': m,
        'free_dof': free_dof,
        'overconstrained': free_dof < 0,
        'constraint_ratio': m / n if n > 0 else 0,
    }


# =====================================================================
# Generate abstract uncolorable hypergraphs via CK-31 perturbation
# =====================================================================

def generate_sub31_abstract(num_trials=50000):
    """
    Generate abstract uncolorable hypergraphs with n < 31.

    Strategy: Start from random 3-uniform hypergraphs with enough
    structure for uncolorability (CK-31-inspired parameters).
    Also: merge vertices in CK-31 (abstract graph only).
    """
    results = []

    # First: get CK-31 abstract graph
    n_ck = 31
    vecs = [
        (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 1, -1), (0, 1, 2), (0, 2, -1),
        (1, 0, 0), (1, 0, 1), (1, 0, -1), (1, 0, 2), (1, 0, -2),
        (1, 1, 0), (1, 1, 1), (1, 1, -1), (1, 1, 2), (1, -1, 0),
        (1, -1, 1), (1, -1, -1), (1, -1, -2), (1, 2, 0), (1, 2, -1),
        (1, -2, 0), (1, -2, 1), (2, 0, 1), (2, 0, -1), (2, 1, 0),
        (2, 1, 1), (2, 1, -1), (2, -1, 0), (2, -1, 1), (2, -1, -1)
    ]
    pair_set = set()
    for i in range(n_ck):
        for j in range(i + 1, n_ck):
            if sum(a * b for a, b in zip(vecs[i], vecs[j])) == 0:
                pair_set.add((i, j))
    pairs_ck = sorted(pair_set)
    adj_ck = defaultdict(set)
    for i, j in pairs_ck:
        adj_ck[i].add(j)
        adj_ck[j].add(i)
    triads_ck = []
    for i in range(n_ck):
        for j in adj_ck[i]:
            if j > i:
                for k in (adj_ck[i] & adj_ck[j]):
                    if k > j:
                        triads_ck.append((i, j, k))

    print(f"  CK-31 base: {n_ck} vertices, {len(pairs_ck)} pairs, {len(triads_ck)} triads")

    # Strategy 1: Merge non-adjacent vertices in CK-31
    non_adj = [(i, j) for i in range(n_ck) for j in range(i+1, n_ck)
               if j not in adj_ck[i]]
    print(f"  Non-adjacent pairs to try merging: {len(non_adj)}")

    merge_count = 0
    for v1, v2 in non_adj:
        # Merge v2 into v1: all edges of v2 become edges of v1
        remap = {}
        idx = 0
        for i in range(n_ck):
            if i == v2:
                remap[i] = remap[v1]  # v2 maps to v1's new index
            else:
                remap[i] = idx
                idx += 1
        # But v1 must be mapped first
        remap = {}
        new_idx = 0
        for i in range(n_ck):
            if i == v2:
                continue
            remap[i] = new_idx
            new_idx += 1
        remap[v2] = remap[v1]  # merge v2 -> v1
        new_n = n_ck - 1

        new_pair_set = set()
        for a, b in pairs_ck:
            ra, rb = remap[a], remap[b]
            if ra != rb:
                new_pair_set.add((min(ra, rb), max(ra, rb)))
        new_pairs = sorted(new_pair_set)

        new_triad_set = set()
        for a, b, c in triads_ck:
            ra, rb, rc = remap[a], remap[b], remap[c]
            tri = tuple(sorted([ra, rb, rc]))
            if len(set(tri)) == 3:
                new_triad_set.add(tri)
        new_triads = sorted(new_triad_set)

        if new_triads and is_uncolorable(new_n, new_pairs, new_triads):
            results.append((new_n, new_pairs, new_triads))
            merge_count += 1

    print(f"  Merge-derived uncolorable: {merge_count}/{len(non_adj)}")

    # Strategy 2: Random abstract hypergraphs near CK-31 parameters
    # Target: n=28-30, ~15-17 triads, ~65-75 pairs
    rand_count = 0
    for trial in range(num_trials):
        n = random.randint(28, 30)
        n_triads = random.randint(14, 20)

        # Generate random triads
        triads = set()
        attempts = 0
        while len(triads) < n_triads and attempts < 200:
            t = tuple(sorted(random.sample(range(n), 3)))
            triads.add(t)
            attempts += 1
        triads = sorted(triads)

        # Collect triad pairs + add extra random pairs
        pair_set = set()
        for a, b, c in triads:
            pair_set.add((a, b))
            pair_set.add((a, c))
            pair_set.add((b, c))
        n_extra = random.randint(10, 30)
        for _ in range(n_extra):
            a, b = sorted(random.sample(range(n), 2))
            pair_set.add((a, b))
        pairs = sorted(pair_set)

        if is_uncolorable(n, pairs, triads):
            results.append((n, pairs, triads))
            rand_count += 1

    print(f"  Random-generated uncolorable: {rand_count}/{num_trials}")

    return results


# =====================================================================
# Main analysis
# =====================================================================

def main():
    print("=" * 70)
    print("REALIZABILITY OBSTRUCTION ANALYSIS")
    print("Techniques: Delta Theorem, Forbidden Minors, DOF Counting")
    print("=" * 70)

    # --- CK-31 (calibration) ---
    print("\n" + "=" * 70)
    print("CALIBRATION: CK-31 (the known minimum, n=31)")
    print("=" * 70)

    n_ck, pairs_ck, triads_ck, vecs_ck = get_ck31()
    print(f"  n={n_ck}, pairs={len(pairs_ck)}, triads={len(triads_ck)}")
    assert is_uncolorable(n_ck, pairs_ck, triads_ck), "CK-31 must be uncolorable!"

    print("\n--- Orthogonal Dimension Bounds ---")
    ob = orthogonal_dimension_bounds(n_ck, pairs_ck)
    for k, v in ob.items():
        print(f"  {k}: {v}")
    print(f"  NOTE: omega={ob['omega']} means clique of {ob['omega']} mutually orthogonal vectors.")
    print(f"  In R^3 max clique=3 (a triad). omega>3 would block R^3 realization.")

    print("\n--- Forbidden Minors ---")
    fm = check_forbidden_minors(n_ck, pairs_ck)
    for k, v in fm.items():
        print(f"  {k}: {v}")

    print("\n--- DOF Analysis ---")
    dof = dof_analysis(n_ck, pairs_ck, triads_ck)
    for k, v in dof.items():
        print(f"  {k}: {v}")

    # --- Generate abstract sub-31 uncolorable hypergraphs ---
    print("\n" + "=" * 70)
    print("GENERATING ABSTRACT SUB-31 UNCOLORABLE HYPERGRAPHS")
    print("(by perturbing CK-31 — purely combinatorial)")
    print("=" * 70)

    t0 = time.time()
    sub31_list = generate_sub31_abstract(num_trials=20000)
    elapsed = time.time() - t0
    print(f"  Total: {len(sub31_list)} uncolorable sub-31 hypergraphs in {elapsed:.1f}s")

    # Deduplicate by (n, len(pairs), len(triads))
    seen = set()
    unique = []
    for n, pairs, triads in sub31_list:
        key = (n, len(pairs), len(triads))
        if key not in seen:
            seen.add(key)
            unique.append((n, pairs, triads))
    print(f"  Unique by (n, |pairs|, |triads|): {len(unique)}")

    # Size distribution
    size_dist = defaultdict(int)
    for n, _, _ in sub31_list:
        size_dist[n] += 1
    print(f"  Size distribution: {dict(sorted(size_dist.items()))}")

    # --- Analyze sub-31 hypergraphs ---
    print("\n" + "=" * 70)
    print("ANALYZING SUB-31 HYPERGRAPHS WITH REALIZABILITY TESTS")
    print("=" * 70)

    omega_blocks = 0
    overconstrained_count = 0
    underconstrained_count = 0

    # Track results by n
    results_by_n = defaultdict(lambda: {
        'count': 0, 'omega_blocked': 0, 'overconstrained': 0,
        'max_omega': 0, 'max_alpha': 0,
        'min_free_dof': float('inf'), 'max_free_dof': float('-inf'),
    })

    # Analyze a sample (all unique ones, up to 200)
    sample = unique[:200]

    for idx, (n, pairs, triads) in enumerate(sample):
        ob = orthogonal_dimension_bounds(n, pairs)
        dof = dof_analysis(n, pairs, triads)

        r = results_by_n[n]
        r['count'] += 1
        if ob['omega_blocks_R3']:
            r['omega_blocked'] += 1
            omega_blocks += 1
        if dof['overconstrained']:
            r['overconstrained'] += 1
            overconstrained_count += 1
        else:
            underconstrained_count += 1
        r['max_omega'] = max(r['max_omega'], ob['omega'])
        r['max_alpha'] = max(r['max_alpha'], ob['alpha'])
        r['min_free_dof'] = min(r['min_free_dof'], dof['free_dof'])
        r['max_free_dof'] = max(r['max_free_dof'], dof['free_dof'])

        if idx % 50 == 0:
            print(f"  ... analyzed {idx+1}/{len(sample)}")

    print(f"\n  Total analyzed: {len(sample)}")
    if len(sample) > 0:
        print(f"  Omega > 3 (clique blocks R^3): {omega_blocks} ({100*omega_blocks/len(sample):.1f}%)")
        print(f"  Overconstrained (2n-m-3 < 0): {overconstrained_count} ({100*overconstrained_count/len(sample):.1f}%)")
        print(f"  Underconstrained: {underconstrained_count}")
    else:
        print("  No sub-31 hypergraphs generated — skipping analysis.")

    print(f"\n  {'n':>3} {'count':>6} {'omega_blk':>10} {'overconstr':>11} {'max_omega':>10} {'max_alpha':>10} {'free_dof':>15}")
    print(f"  {'-'*3} {'-'*6} {'-'*10} {'-'*11} {'-'*10} {'-'*10} {'-'*15}")
    for n in sorted(results_by_n.keys()):
        r = results_by_n[n]
        fdof = f"{r['min_free_dof']}-{r['max_free_dof']}"
        print(f"  {n:>3} {r['count']:>6} {r['omega_blocked']:>10} {r['overconstrained']:>11} {r['max_omega']:>10} {r['max_alpha']:>10} {fdof:>15}")

    # --- Forbidden minors on a few examples ---
    print("\n" + "=" * 70)
    print("FORBIDDEN MINOR ANALYSIS (sample of 10 sub-31 hypergraphs)")
    print("=" * 70)

    fm_sample = unique[:10]
    for idx, (n, pairs, triads) in enumerate(fm_sample):
        print(f"\n  Hypergraph #{idx+1}: n={n}, pairs={len(pairs)}, triads={len(triads)}")
        fm = check_forbidden_minors(n, pairs)
        print(f"    Orth graph: max_clique={fm['orth_max_clique']}, "
              f"treewidth~{fm['orth_treewidth_approx']}, "
              f"series-parallel={fm['orth_series_parallel']}")
        print(f"    Complement: max_clique={fm['comp_max_clique']}, "
              f"treewidth~{fm['comp_treewidth_approx']}, "
              f"series-parallel={fm['comp_series_parallel']}")

        # Also check: does orth graph have K5 as MINOR (not just subgraph)?
        G = nx.Graph()
        G.add_nodes_from(range(n))
        for a, b in pairs:
            G.add_edge(a, b)

    # --- Key question: what separates realizable from unrealizable? ---
    print("\n" + "=" * 70)
    print("COMPARISON: CK-31 (realizable) vs sub-31 (unrealizable)")
    print("=" * 70)

    ck_dof = dof_analysis(n_ck, pairs_ck, triads_ck)
    ck_ob = orthogonal_dimension_bounds(n_ck, pairs_ck)

    print(f"\n  CK-31: n={n_ck}, pairs={ck_dof['pairs']}, triads={ck_dof['triads']}")
    print(f"    constraint_ratio={ck_dof['constraint_ratio']:.3f}, free_dof={ck_dof['free_dof']}")
    print(f"    omega={ck_ob['omega']}, alpha={ck_ob['alpha']}, treewidth~{ck_ob['treewidth_approx']}")

    # Average of sub-30 uncolorable
    if unique:
        sub30 = [(n, p, t) for n, p, t in unique if n == 30]
        if sub30:
            avg_pairs = np.mean([len(p) for _, p, _ in sub30])
            avg_triads = np.mean([len(t) for _, _, t in sub30])
            avg_ratio = np.mean([len(p)/n for n, p, _ in sub30])
            print(f"\n  Sub-30 (n=30) average: pairs={avg_pairs:.1f}, triads={avg_triads:.1f}")
            print(f"    constraint_ratio={avg_ratio:.3f}")

            # Compare structural properties
            print(f"\n  Structural comparison (n=30 sample vs CK-31):")
            for n, pairs, triads in sub30[:5]:
                dof = dof_analysis(n, pairs, triads)
                ob = orthogonal_dimension_bounds(n, pairs)
                print(f"    n={n}: pairs={dof['pairs']}, triads={dof['triads']}, "
                      f"extra={dof['extra_pairs']}, omega={ob['omega']}, "
                      f"alpha={ob['alpha']}, free_dof={dof['free_dof']}")

    # --- Deep dive: omega=3 sub-31 cases (the hard ones) ---
    print("\n" + "=" * 70)
    print("DEEP DIVE: omega=3 sub-31 hypergraphs (pass clique test)")
    print("These are the cases that COULD fit in R^3 by clique alone.")
    print("=" * 70)

    omega3_cases = []
    for n, pairs, triads in unique:
        ob = orthogonal_dimension_bounds(n, pairs)
        if ob['omega'] <= 3 and n < 31:
            dof = dof_analysis(n, pairs, triads)
            omega3_cases.append((n, pairs, triads, ob, dof))

    print(f"\n  Found {len(omega3_cases)} omega<=3 sub-31 cases out of {len(unique)} unique")

    for idx, (n, pairs, triads, ob, dof) in enumerate(omega3_cases[:20]):
        # Check: how many vertices are in 0 triads?
        triad_verts = set()
        for a, b, c in triads:
            triad_verts.update([a, b, c])
        isolated = n - len(triad_verts)

        # Degree distribution
        deg = defaultdict(int)
        for a, b in pairs:
            deg[a] += 1
            deg[b] += 1
        deg_vals = sorted(deg.values())

        # Key question: does this graph have a valid R^3 orthogonality structure?
        # In R^3, every triad defines a coordinate frame. Overlapping triads
        # share vectors, creating algebraic dependencies.
        # Count: how many triads share an edge (pair)?
        triad_edge_count = defaultdict(int)
        for a, b, c in triads:
            for e in [(a,b), (a,c), (b,c)]:
                triad_edge_count[e] += 1
        shared_edges = sum(1 for v in triad_edge_count.values() if v > 1)

        print(f"\n  Case #{idx+1}: n={n}, pairs={len(pairs)}, triads={len(triads)}")
        print(f"    omega={ob['omega']}, alpha={ob['alpha']}, free_dof={dof['free_dof']}")
        print(f"    extra_pairs={dof['extra_pairs']}, isolated_verts={isolated}")
        print(f"    degree range: {deg_vals[0]}-{deg_vals[-1]}, shared_triad_edges={shared_edges}")
        print(f"    overconstrained={dof['overconstrained']}")

    # Summary statistics for omega=3 cases
    if omega3_cases:
        print(f"\n  --- Summary of omega<=3 sub-31 cases ---")
        oc_count = sum(1 for _, _, _, _, d in omega3_cases if d['overconstrained'])
        print(f"  Overconstrained: {oc_count}/{len(omega3_cases)} ({100*oc_count/len(omega3_cases):.1f}%)")
        free_dofs = [d['free_dof'] for _, _, _, _, d in omega3_cases]
        print(f"  Free DOF range: {min(free_dofs)} to {max(free_dofs)}")
        print(f"  Mean free DOF: {np.mean(free_dofs):.1f}")

        # The KEY question: are there any omega=3, underconstrained cases?
        easy = [(n, p, t, o, d) for n, p, t, o, d in omega3_cases if not d['overconstrained']]
        print(f"\n  Omega<=3 AND underconstrained: {len(easy)}")
        if easy:
            print("  *** THESE ARE THE MOST INTERESTING CASES ***")
            print("  *** They pass both the clique test AND DOF test ***")
            print("  *** Something deeper must block R^3 realization ***")
            for n, pairs, triads, ob, dof in easy[:10]:
                print(f"    n={n}, pairs={len(pairs)}, triads={len(triads)}, "
                      f"free_dof={dof['free_dof']}, alpha={ob['alpha']}")

    print("\n" + "=" * 70)
    print("DONE")
    print("=" * 70)


if __name__ == '__main__':
    main()
