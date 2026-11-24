"""
ks_bpqs_unique.py -- Does CK-31 uniquely enable any Bell scenario?

For each island, find the full range of achievable B-KS partitions (S_A, S_B).
Then check: are there Bell scenarios where CK-31 is the ONLY island that works?

A Bell scenario is specified by (|S_A|, |S_B|). An island "covers" a scenario
if it has a B-KS partition with |S_A'| <= |S_A| and |S_B'| <= |S_B|.

If CK-31 achieves scenarios that no 33-vector island can match, it uniquely
enables those perfect quantum strategies despite having fewer rays.
"""

import sys
sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

import cmath
import math
import random
import time
from itertools import combinations

from pysat.solvers import Glucose4

from ks_complex import hermitian_dot, generate_eisenstein_rays
from ks_new_islands import generate_rays_from_alphabet, hermitian_completion, sat_minimize
from ks_sat import CK31_VECTORS

random.seed(42)


def build_pairs_triads(rays, tol=1e-9):
    n = len(rays)
    pairs = []
    pair_set = set()
    for i in range(n):
        for j in range(i + 1, n):
            dot = hermitian_dot(rays[i], rays[j])
            if abs(dot) < tol:
                pairs.append((i, j))
                pair_set.add((min(i, j), max(i, j)))
    triads = []
    for i in range(n):
        for j in range(i + 1, n):
            if (i, j) not in pair_set:
                continue
            for k in range(j + 1, n):
                if (i, k) in pair_set and (j, k) in pair_set:
                    triads.append((i, j, k))
    return pairs, triads, pair_set


def is_bks(triads, s_a, s_b, pair_set):
    """Check if (S_A, S_B) is B-KS via SAT."""
    active = set(s_a) | set(s_b)
    var_map = {}
    nv = 1
    for b_idx in active:
        for v in triads[b_idx]:
            if (v, b_idx) not in var_map:
                var_map[(v, b_idx)] = nv
                nv += 1
    clauses = []
    for b_idx in active:
        vecs = list(triads[b_idx])
        vs = [var_map[(v, b_idx)] for v in vecs]
        clauses.append(vs[:])
        for i in range(len(vs)):
            for j in range(i + 1, len(vs)):
                clauses.append([-vs[i], -vs[j]])
    for ba in s_a:
        for bb in s_b:
            for v in triads[ba]:
                for w in triads[bb]:
                    if v != w and (min(v, w), max(v, w)) in pair_set:
                        clauses.append([-var_map[(v, ba)], -var_map[(w, bb)]])
    with Glucose4() as solver:
        for c in clauses:
            solver.add_clause(c)
        return not solver.solve()


def find_all_bks_sizes(name, rays, pairs, triads, pair_set, n_greedy=200):
    """Find the range of achievable B-KS (|S_A|, |S_B|) sizes via greedy search."""
    m = len(triads)
    all_bases = list(range(m))

    # Verify full set is B-KS
    if not is_bks(triads, all_bases, all_bases, pair_set):
        print(f"  {name}: full set NOT B-KS!")
        return set()

    achieved = set()
    achieved.add((m, m))

    # Greedy from (all, all): try to minimize various objectives
    for trial in range(n_greedy):
        sa = list(all_bases)
        sb = list(all_bases)

        # Random greedy shrink
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
                    if is_a:
                        if is_bks(triads, candidate, sb, pair_set):
                            sa = candidate
                            improved = True
                            break
                    else:
                        if is_bks(triads, sa, candidate, pair_set):
                            sb = candidate
                            improved = True
                            break

        a, b = min(len(sa), len(sb)), max(len(sa), len(sb))
        achieved.add((a, b))

    return achieved


def get_minimal_ks(rays, pairs, triads, n_trials=300):
    """Get minimal KS set."""
    pair_list = [(a, b) for a, b in pairs]
    triad_list = [(a, b, c) for a, b, c in triads]
    subset, size, _ = sat_minimize(rays, pair_list, triad_list, n_trials=n_trials)
    s = set(subset)
    remap = {old: new for new, old in enumerate(sorted(subset))}
    min_rays = [rays[i] for i in sorted(subset)]
    min_pairs = [(remap[a], remap[b]) for a, b in pair_list if a in s and b in s]
    min_triads = [(remap[a], remap[b], remap[c]) for a, b, c in triad_list
                  if a in s and b in s and c in s]
    min_pair_set = set((min(a, b), max(a, b)) for a, b in min_pairs)
    return min_rays, min_pairs, min_triads, min_pair_set, size


# =================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("CK-31 BPQS UNIQUENESS ANALYSIS")
    print("Does CK-31 uniquely enable any Bell scenario?")
    print("=" * 70)
    print()

    t_start = time.time()

    # Build all islands (minimized)
    islands = {}

    # CK-31: known minimal, use directly
    print("Building CK-31...")
    ck_rays = [tuple(complex(x) for x in v) for v in CK31_VECTORS]
    ck_pairs, ck_triads, ck_ps = build_pairs_triads(ck_rays)
    print(f"  {len(ck_rays)} rays, {len(ck_pairs)} pairs, {len(ck_triads)} bases")
    islands['CK-31'] = (ck_rays, ck_pairs, ck_triads, ck_ps)

    # Eisenstein-33
    print("Building Eisenstein-33...")
    eis_pool = generate_eisenstein_rays(max_coeff=1, dim=3, norm_cutoff=3)
    eis_pp, eis_pt, eis_pps = build_pairs_triads(eis_pool)
    eis_rays, eis_pairs_l, eis_triads_l, eis_ps, eis_n = get_minimal_ks(
        eis_pool, eis_pp, eis_pt, n_trials=300)
    eis_pairs2, eis_triads2, eis_ps2 = build_pairs_triads(eis_rays)
    print(f"  {len(eis_rays)} rays, {len(eis_pairs2)} pairs, {len(eis_triads2)} bases")
    islands['Eisenstein-33'] = (eis_rays, eis_pairs2, eis_triads2, eis_ps2)

    # Peres-33
    print("Building Peres-33...")
    s2 = math.sqrt(2)
    p_alph = [complex(x) for x in [0, 1, -1, s2, -s2]]
    p_pool = generate_rays_from_alphabet(p_alph)
    p_pp, p_pt, p_pps = build_pairs_triads(p_pool)
    p_rays, p_pairs_l, p_triads_l, p_ps, p_n = get_minimal_ks(
        p_pool, p_pp, p_pt, n_trials=300)
    p_pairs2, p_triads2, p_ps2 = build_pairs_triads(p_rays)
    print(f"  {len(p_rays)} rays, {len(p_pairs2)} pairs, {len(p_triads2)} bases")
    islands['Peres-33'] = (p_rays, p_pairs2, p_triads2, p_ps2)

    # Find achievable B-KS sizes for each island
    print(f"\n{'='*70}")
    print("FINDING ACHIEVABLE B-KS SIZES (200 greedy trials each)")
    print(f"{'='*70}\n")

    all_achieved = {}
    for name, (rays, pairs, triads, ps) in islands.items():
        print(f"\n{name}: {len(triads)} bases")
        achieved = find_all_bks_sizes(name, rays, pairs, triads, ps, n_greedy=200)
        all_achieved[name] = achieved

        # Show unique sizes found
        sizes = sorted(achieved)
        products = sorted(set(a * b for a, b in sizes))
        print(f"  Achieved sizes: {len(sizes)} distinct (|S_A|, |S_B|) pairs")
        print(f"  Product range: {min(products)} to {max(products)}")
        print(f"  Best products: {sorted(products)[:8]}")

        # Show smallest few
        by_product = sorted(sizes, key=lambda x: x[0] * x[1])
        for a, b in by_product[:5]:
            print(f"    {a} x {b} = {a*b}")

    # Analysis: which scenarios does CK-31 cover that others don't?
    print(f"\n{'='*70}")
    print("UNIQUENESS ANALYSIS")
    print(f"{'='*70}")

    ck_sizes = all_achieved['CK-31']
    ck_products = sorted(set(a * b for a, b in ck_sizes))

    # For each CK-31 achievable product, check if any 33-island also achieves it
    print("\nCK-31 achievable products vs other islands:")
    for prod in ck_products[:10]:
        ck_configs = [(a, b) for a, b in ck_sizes if a * b == prod]
        covered_by = []
        for name in ['Eisenstein-33', 'Peres-33']:
            other_sizes = all_achieved[name]
            # Check if any config in other island has product <= prod
            other_prods = [a * b for a, b in other_sizes]
            if any(p <= prod for p in other_prods):
                covered_by.append(name)
        unique = " ** UNIQUE TO CK-31 **" if not covered_by else f" (also: {', '.join(covered_by)})"
        print(f"  Product {prod}: CK-31 configs {ck_configs}{unique}")

    # Key question: minimum achievable product per island
    print("\nMinimum B-KS products:")
    for name, achieved in sorted(all_achieved.items()):
        min_prod = min(a * b for a, b in achieved)
        configs = [(a, b) for a, b in achieved if a * b == min_prod]
        print(f"  {name}: {min_prod} ({configs[0][0]} x {configs[0][1]})")

    # Check: does CK-31 achieve any (|S_A|, |S_B|) where |S_A| < 5?
    # (Eisenstein achieves 5x9, so if CK-31 achieves 4xN that's unique)
    print("\nCK-31 configs with |S_A| < 5:")
    small_sa = [(a, b) for a, b in ck_sizes if a < 5]
    if small_sa:
        for a, b in sorted(small_sa):
            print(f"  {a} x {b} = {a*b}")
    else:
        print("  None found")

    # Check: CK-31 configs that require fewer Alice inputs than any 33-island
    ck_min_alice = min(a for a, b in ck_sizes)
    print(f"\nCK-31 minimum Alice inputs: {ck_min_alice}")
    for name in ['Eisenstein-33', 'Peres-33']:
        other_min_alice = min(a for a, b in all_achieved[name])
        print(f"  {name} minimum Alice inputs: {other_min_alice}")

    t_total = time.time() - t_start
    print(f"\nTotal time: {t_total:.1f}s")
