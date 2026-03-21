"""
ks_cubic_characterize.py -- Full characterization of the cubic Q(cbrt(2)) island

The paper notes that Q(cbrt(2)) with extended alphabet {0,±1,±cbrt(2),±cbrt(4)}
produces a KS set at minimum 60 after cross-product completion.

This script characterizes:
1. Pool structure (rays, pairs, triads)
2. Minimum KS set (greedy + high trial count)
3. Degree sequence and graph invariants
4. Rigidity analysis (Jacobian null space)
5. BPQS (B-KS partitions)
6. Graph isomorphism check against all known islands
7. Cancellation identity analysis
"""

import sys
sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

import cmath
import math
import random
import time
from collections import Counter

import numpy as np
from pysat.solvers import Glucose4

from ks_complex import hermitian_dot, canonicalize_complex_ray
from ks_new_islands import generate_rays_from_alphabet, hermitian_completion
from ks_rigidity import compute_rigidity, normalize_rays

random.seed(42)


def build_pairs_triads(rays, tol=1e-9):
    n = len(rays)
    pairs = []
    pair_set = set()
    adj = {i: set() for i in range(n)}
    for i in range(n):
        for j in range(i + 1, n):
            dot = hermitian_dot(rays[i], rays[j])
            if abs(dot) < tol:
                pairs.append((i, j))
                pair_set.add((min(i, j), max(i, j)))
                adj[i].add(j)
                adj[j].add(i)
    triads = []
    for i in range(n):
        neighbors_i = sorted(adj[i])
        for idx_j, j in enumerate(neighbors_i):
            if j <= i:
                continue
            for k in neighbors_i[idx_j + 1:]:
                if k <= j:
                    continue
                if k in adj[j]:
                    triads.append((i, j, k))
    return pairs, triads, pair_set, adj


def is_ks_uncolorable(n, triads, pairs):
    if not triads:
        return False
    solver = Glucose4()
    for a, b, c in triads:
        va, vb, vc = a + 1, b + 1, c + 1
        solver.add_clause([va, vb, vc])
        solver.add_clause([-va, -vb])
        solver.add_clause([-va, -vc])
        solver.add_clause([-vb, -vc])
    for i, j in pairs:
        solver.add_clause([-(i+1), -(j+1)])
    result = solver.solve()
    solver.delete()
    return not result


def greedy_minimize(rays, pairs, triads, n_trials=500):
    n_rays = len(rays)
    best = list(range(n_rays))
    best_size = n_rays
    sizes = Counter()
    for trial in range(n_trials):
        current = list(range(n_rays))
        order = list(range(n_rays))
        random.shuffle(order)
        for candidate in order:
            if candidate not in current:
                continue
            test = [r for r in current if r != candidate]
            if len(test) < 20:
                break
            keep_set = set(test)
            remap = {old: new for new, old in enumerate(test)}
            sub_triads = [(remap[a], remap[b], remap[c])
                          for a, b, c in triads
                          if a in keep_set and b in keep_set and c in keep_set]
            sub_pairs = [(remap[i], remap[j])
                         for i, j in pairs
                         if i in keep_set and j in keep_set]
            if is_ks_uncolorable(len(test), sub_triads, sub_pairs):
                current = test
        sizes[len(current)] += 1
        if len(current) < best_size:
            best = current
            best_size = len(current)
            print(f"    Trial {trial+1}: new best = {best_size}")
    return best, best_size, sizes


def degree_sequence(n, pairs):
    deg = [0] * n
    for i, j in pairs:
        deg[i] += 1
        deg[j] += 1
    return tuple(sorted(deg, reverse=True))


def is_bks(triads_list, s_a, s_b, pair_set):
    """Check if (S_A, S_B) is B-KS via SAT."""
    active = set(s_a) | set(s_b)
    var_map = {}
    nv = 1
    for b_idx in active:
        for v in triads_list[b_idx]:
            if (v, b_idx) not in var_map:
                var_map[(v, b_idx)] = nv
                nv += 1
    clauses = []
    for b_idx in active:
        vecs = list(triads_list[b_idx])
        vs = [var_map[(v, b_idx)] for v in vecs]
        clauses.append(vs[:])
        for i in range(len(vs)):
            for j in range(i + 1, len(vs)):
                clauses.append([-vs[i], -vs[j]])
    for ba in s_a:
        for bb in s_b:
            for v in triads_list[ba]:
                for w in triads_list[bb]:
                    if v != w and (min(v, w), max(v, w)) in pair_set:
                        clauses.append([-var_map[(v, ba)], -var_map[(w, bb)]])
    with Glucose4() as solver:
        for c in clauses:
            solver.add_clause(c)
        return not solver.solve()


def find_bpqs(triads_list, pair_set, n_greedy=200):
    """Find optimal BPQS via greedy search."""
    m = len(triads_list)
    all_bases = list(range(m))
    if not is_bks(triads_list, all_bases, all_bases, pair_set):
        return None, None
    best_prod = m * m
    best_a, best_b = m, m
    for trial in range(n_greedy):
        sa, sb = list(all_bases), list(all_bases)
        improved = True
        while improved:
            improved = False
            for is_a in ([True, False] if random.random() < 0.5 else [False, True]):
                primary = sa if is_a else sb
                indices = list(range(len(primary)))
                random.shuffle(indices)
                for i in indices:
                    candidate = primary[:i] + primary[i+1:]
                    if not candidate:
                        continue
                    if is_a and is_bks(triads_list, candidate, sb, pair_set):
                        sa = candidate
                        improved = True
                        break
                    elif not is_a and is_bks(triads_list, sa, candidate, pair_set):
                        sb = candidate
                        improved = True
                        break
        a, b = min(len(sa), len(sb)), max(len(sa), len(sb))
        if a * b < best_prod:
            best_prod = a * b
            best_a, best_b = a, b
    return best_a, best_b


def try_vf2(n1, pairs1, n2, pairs2):
    try:
        import networkx as nx
        from networkx.algorithms.isomorphism import GraphMatcher
        G1 = nx.Graph()
        G1.add_nodes_from(range(n1))
        G1.add_edges_from(pairs1)
        G2 = nx.Graph()
        G2.add_nodes_from(range(n2))
        G2.add_edges_from(pairs2)
        return GraphMatcher(G1, G2).is_isomorphic()
    except ImportError:
        return None


# =================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("CUBIC Q(cbrt(2)) ISLAND CHARACTERIZATION")
    print("=" * 70)
    print()
    t_start = time.time()

    # Build the cubic pool
    cbrt2 = 2 ** (1/3)
    cbrt4 = 2 ** (2/3)

    print(f"Generators: cbrt(2) = {cbrt2:.6f}, cbrt(4) = {cbrt4:.6f}")
    print(f"|cbrt(2)|^2 = {cbrt2**2:.6f}")
    print(f"|cbrt(4)|^2 = {cbrt4**2:.6f}")
    print(f"cbrt(2) * cbrt(4) = {cbrt2 * cbrt4:.6f} (= 2)")
    print()

    # Cancellation identities
    print("Cancellation identities:")
    print(f"  cbrt(2) * cbrt(4) = 2  (modulus-2 via product)")
    print(f"  cbrt(2)^3 = 2")
    print(f"  1 + 1 - cbrt(2)*cbrt(4) = 1 + 1 - 2 = 0")
    print()

    alph = [complex(x) for x in [0, 1, -1, cbrt2, -cbrt2, cbrt4, -cbrt4]]
    print(f"Alphabet: {{0, ±1, ±cbrt(2), ±cbrt(4)}} ({len(alph)} elements)")

    # Raw rays
    print("\n--- RAW POOL ---")
    raw_rays = generate_rays_from_alphabet(alph)
    raw_pairs, raw_triads, raw_ps, raw_adj = build_pairs_triads(raw_rays)
    raw_uncol = is_ks_uncolorable(len(raw_rays), raw_triads, raw_pairs)
    print(f"  Rays: {len(raw_rays)}, Pairs: {len(raw_pairs)}, "
          f"Triads: {len(raw_triads)}, Uncolorable: {raw_uncol}")

    # Completed pool
    print("\n--- COMPLETED POOL ---")
    comp_rays = hermitian_completion(raw_rays, max_iter=5)
    comp_pairs, comp_triads, comp_ps, comp_adj = build_pairs_triads(comp_rays)
    comp_uncol = is_ks_uncolorable(len(comp_rays), comp_triads, comp_pairs)
    print(f"  Rays: {len(comp_rays)}, Pairs: {len(comp_pairs)}, "
          f"Triads: {len(comp_triads)}, Uncolorable: {comp_uncol}")

    if not comp_uncol:
        print("  NOT UNCOLORABLE — cannot characterize")
        sys.exit(1)

    # Minimization (high trial count)
    print("\n--- MINIMIZATION (500 trials) ---")
    t0 = time.time()
    min_idx, min_size, size_dist = greedy_minimize(
        comp_rays, comp_pairs, comp_triads, n_trials=500)
    dt = time.time() - t0
    print(f"  Minimum: {min_size} vectors ({dt:.1f}s)")
    print(f"  Size distribution: {dict(sorted(size_dist.items())[:8])}")

    # Build minimal set
    min_rays_raw = [comp_rays[i] for i in sorted(min_idx)]
    min_rays = normalize_rays(min_rays_raw)
    min_pairs, min_triads, min_ps, min_adj = build_pairs_triads(min_rays)
    n = len(min_rays)
    print(f"  Minimal: {n} rays, {len(min_pairs)} pairs, {len(min_triads)} bases")

    # Degree sequence
    ds = degree_sequence(n, min_pairs)
    deg_count = Counter(ds)
    print(f"\n--- DEGREE SEQUENCE ---")
    print(f"  Distribution: {dict(sorted(deg_count.items()))}")
    print(f"  Degree range: {min(ds)} to {max(ds)}")
    print(f"  Distinct degree types: {len(deg_count)}")

    # Bases per ray
    ray_basis_count = Counter()
    for a, b, c in min_triads:
        ray_basis_count[a] += 1
        ray_basis_count[b] += 1
        ray_basis_count[c] += 1
    basis_dist = Counter(ray_basis_count.values())
    print(f"  Bases-per-ray: {dict(sorted(basis_dist.items()))}")

    # Rigidity
    print(f"\n--- RIGIDITY ANALYSIS ---")
    null_dim, sym_dim, rigid, deform, rank, shape = compute_rigidity(
        "Cubic-cbrt2", min_rays, min_pairs)
    status = "RIGID" if rigid else f"FLEX ({deform} deformation dims)"
    print(f"  Jacobian: {shape[0]} x {shape[1]}")
    print(f"  Null space: {null_dim}, Symmetry dim: {sym_dim}")
    print(f"  Status: {status}")

    # BPQS
    print(f"\n--- BPQS ANALYSIS ---")
    triads_as_list = list(min_triads)  # list of (a,b,c) tuples
    bpqs_a, bpqs_b = find_bpqs(triads_as_list, min_ps, n_greedy=200)
    if bpqs_a:
        print(f"  Best BPQS: {bpqs_a} x {bpqs_b} = {bpqs_a * bpqs_b}")
    else:
        print(f"  BPQS: failed (not B-KS)")

    # Graph isomorphism with known islands
    print(f"\n--- GRAPH ISOMORPHISM ---")

    # Build known islands for comparison
    from ks_sat import CK31_VECTORS
    from ks_complex import generate_eisenstein_rays

    # CK-31
    ck_rays = normalize_rays([tuple(complex(x) for x in v) for v in CK31_VECTORS])
    ck_p, ck_t, _, _ = build_pairs_triads(ck_rays)

    # Eisenstein-33 (need to minimize)
    eis_pool = generate_eisenstein_rays(max_coeff=1, dim=3, norm_cutoff=3)
    eis_pp, eis_pt, _, _ = build_pairs_triads(eis_pool)
    eis_idx, eis_n = greedy_minimize(eis_pool, eis_pp, eis_pt, n_trials=200)[:2]
    eis_rays = normalize_rays([eis_pool[i] for i in eis_idx])
    eis_p, eis_t, _, _ = build_pairs_triads(eis_rays)

    # Peres-33
    s2 = math.sqrt(2)
    p_pool = generate_rays_from_alphabet([complex(x) for x in [0, 1, -1, s2, -s2]])
    p_pp, p_pt, _, _ = build_pairs_triads(p_pool)
    p_idx, p_n = greedy_minimize(p_pool, p_pp, p_pt, n_trials=200)[:2]
    p_rays = normalize_rays([p_pool[i] for i in p_idx])
    p_p, p_t, _, _ = build_pairs_triads(p_rays)

    for ref_name, ref_n, ref_pairs in [
        ("CK-31", len(ck_rays), ck_p),
        ("Eisenstein-33", len(eis_rays), eis_p),
        ("Peres-33", len(p_rays), p_p),
    ]:
        if ref_n != n:
            print(f"  vs {ref_name} ({ref_n} rays): different size, skip")
            continue
        iso = try_vf2(n, min_pairs, ref_n, ref_pairs)
        if iso is None:
            print(f"  vs {ref_name}: networkx not available")
        elif iso:
            print(f"  vs {ref_name}: ISOMORPHIC!")
        else:
            print(f"  vs {ref_name}: NOT isomorphic")

    # Summary
    t_total = time.time() - t_start
    print(f"\n{'='*70}")
    print(f"SUMMARY: Cubic Q(cbrt(2)) Island")
    print(f"{'='*70}")
    print(f"  Alphabet: {{0, ±1, ±cbrt(2), ±cbrt(4)}}")
    print(f"  Cancellation: cbrt(2)*cbrt(4) = 2 (indirect modulus-2)")
    print(f"  Pool: {len(comp_rays)} rays (after completion)")
    print(f"  Minimum KS: {min_size} vectors, {len(min_triads)} bases")
    print(f"  Pairs: {len(min_pairs)}, Degree types: {len(deg_count)}")
    print(f"  Rigidity: {status}")
    if bpqs_a:
        print(f"  BPQS: {bpqs_a} x {bpqs_b} = {bpqs_a * bpqs_b}")
    print(f"  Total time: {t_total:.1f}s")
