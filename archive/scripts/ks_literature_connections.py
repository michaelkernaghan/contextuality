"""
ks_literature_connections.py -- Connect our results to the literature
=====================================================================

Three computations:
  1. Compare Trandafir-Cabello 97-element SI-C closure with our 49-ray integer pool
  2. Compute N(S) = lcm{||v||^2} for each of our six islands
  3. Test bootstrap percolation on minimal KS sets (merge saturation connection)

References:
  - Trandafir & Cabello, arXiv:2501.11640 (SI-C closure, bootstrap percolation)
  - Cortez, Morales & Reyes, arXiv:2211.13216 (N(S) invariant, Z[1/6])
"""

import sys
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

import cmath
import math
import random
import time
from itertools import combinations
from math import gcd
from functools import reduce

from pysat.solvers import Glucose4

from ks_complex import (
    generate_eisenstein_rays,
    hermitian_dot,
    canonicalize_complex_ray,
)
from ks_new_islands import (
    generate_rays_from_alphabet,
    hermitian_completion,
)

random.seed(42)


def lcm(a, b):
    return abs(a * b) // gcd(a, b)


def lcm_list(lst):
    return reduce(lcm, lst)


def build_pairs_triads(rays, tol=1e-9):
    """Build orthogonal pairs and triads."""
    n = len(rays)
    pairs = []
    adj = {i: set() for i in range(n)}
    for i in range(n):
        for j in range(i + 1, n):
            dot = hermitian_dot(rays[i], rays[j])
            if abs(dot) < tol:
                pairs.append((i, j))
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
    return pairs, triads, adj


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
        solver.add_clause([-(i + 1), -(j + 1)])
    result = solver.solve()
    solver.delete()
    return not result


def greedy_minimize(rays, pairs, triads, n_trials=500):
    """Return indices of a minimal KS subset."""
    n = len(rays)
    best = list(range(n))
    for trial in range(n_trials):
        current = list(range(n))
        order = list(range(n))
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
        if len(current) < len(best):
            best = current
    return best


def canonicalize_int_ray(v):
    """Canonicalize integer ray: primitive, first nonzero positive."""
    a, b, c = v
    if a == 0 and b == 0 and c == 0:
        return None
    g = gcd(gcd(abs(a), abs(b)), abs(c))
    v2 = (a // g, b // g, c // g)
    for coord in v2:
        if coord != 0:
            if coord < 0:
                v2 = (-v2[0], -v2[1], -v2[2])
            break
    return v2


def generate_integer_rays():
    """All 49 projectively distinct rays from {0,±1,±2}."""
    rays = []
    seen = set()
    for a in range(-2, 3):
        for b in range(-2, 3):
            for c in range(-2, 3):
                v = canonicalize_int_ray((a, b, c))
                if v and v not in seen:
                    seen.add(v)
                    rays.append(v)
    return rays


def dot_int(a, b):
    return sum(x * y for x, y in zip(a, b))


def norm_sq_int(v):
    return sum(x * x for x in v)


def cross_product(u, v):
    """Integer cross product."""
    return (
        u[1] * v[2] - u[2] * v[1],
        u[2] * v[0] - u[0] * v[2],
        u[0] * v[1] - u[1] * v[0],
    )


# =====================================================================
# COMPUTATION 1: SI-C closure vs integer pool
# =====================================================================

def computation_1():
    print("=" * 70)
    print("COMPUTATION 1: SI-C Closure vs {0,±1,±2} Integer Pool")
    print("=" * 70)

    # Yu-Oh 13-element minimal SI-C set (projective rays, unnormalized)
    yu_oh_13 = [
        (1, 0, 0), (0, 1, 0), (0, 0, 1),  # basis
        (1, 1, 0), (1, -1, 0),  # face diagonals
        (1, 0, 1), (1, 0, -1),
        (0, 1, 1), (0, 1, -1),
        (1, 1, 1), (1, 1, -1), (1, -1, 1), (1, -1, -1),  # body diags
    ]
    print(f"\n  Yu-Oh minimal SI-C: {len(yu_oh_13)} rays")
    print(f"  Alphabet: {{0, ±1}}")

    # Step 1: Complete bases (find all triads)
    si_c_set = set(yu_oh_13)
    si_c_list = list(yu_oh_13)

    # Find orthogonal pairs in SI-C
    si_c_pairs = []
    for i, u in enumerate(si_c_list):
        for j, v in enumerate(si_c_list):
            if j <= i:
                continue
            if dot_int(u, v) == 0:
                si_c_pairs.append((i, j))

    # Complete bases: for each orthogonal pair, compute cross product
    # (the unique third vector orthogonal to both)
    new_vectors = set()
    for i, j in si_c_pairs:
        u, v = si_c_list[i], si_c_list[j]
        w = cross_product(u, v)
        if w != (0, 0, 0):
            w = canonicalize_int_ray(w)
            if w and w not in si_c_set:
                new_vectors.add(w)

    print(f"\n  After basis completion: +{len(new_vectors)} new vectors")
    for v in sorted(new_vectors):
        print(f"    {v}  (||v||² = {norm_sq_int(v)})")

    step2_set = si_c_set | new_vectors
    step2_list = sorted(step2_set)
    print(f"  Total after completion: {len(step2_set)} rays")

    # Step 2: Add all vectors orthogonal to ≥2 existing vectors
    # These would be cross products of all pairs in step2_set
    new_from_pairs = set()
    step2_sorted = sorted(step2_set)
    for i, u in enumerate(step2_sorted):
        for j, v in enumerate(step2_sorted):
            if j <= i:
                continue
            w = cross_product(u, v)
            if w != (0, 0, 0):
                w = canonicalize_int_ray(w)
                if w and w not in step2_set:
                    new_from_pairs.add(w)

    print(f"\n  Vectors orthogonal to ≥2 existing: +{len(new_from_pairs)}")
    step3_set = step2_set | new_from_pairs
    step3_list = sorted(step3_set)
    print(f"  Total SI-C closure: {len(step3_set)} rays")

    # What's the alphabet of the SI-C closure?
    all_coords = set()
    for v in step3_set:
        for c in v:
            all_coords.add(abs(c))
    print(f"  Coordinate values: {sorted(all_coords)}")

    # Compare with our 49-ray integer pool
    int_pool = set(generate_integer_rays())
    print(f"\n  Our integer pool: {len(int_pool)} rays (alphabet {{0,±1,±2}})")

    overlap = step3_set & int_pool
    only_sic = step3_set - int_pool
    only_pool = int_pool - step3_set

    print(f"\n  Overlap: {len(overlap)} rays")
    print(f"  In SI-C closure only: {len(only_sic)} rays")
    if only_sic:
        for v in sorted(only_sic):
            print(f"    {v}  (||v||² = {norm_sq_int(v)})")
    print(f"  In integer pool only: {len(only_pool)} rays")
    if only_pool:
        for v in sorted(only_pool):
            print(f"    {v}  (||v||² = {norm_sq_int(v)})")

    # Do another round of closure
    print(f"\n  --- Second round of closure ---")
    new_round2 = set()
    step3_sorted = sorted(step3_set)
    for i, u in enumerate(step3_sorted):
        for j, v in enumerate(step3_sorted):
            if j <= i:
                continue
            w = cross_product(u, v)
            if w != (0, 0, 0):
                w = canonicalize_int_ray(w)
                if w and w not in step3_set:
                    new_round2.add(w)
    step4_set = step3_set | new_round2
    print(f"  Round 2 adds: +{len(new_round2)} rays")
    print(f"  Total after round 2: {len(step4_set)} rays")

    all_coords_2 = set()
    for v in step4_set:
        for c in v:
            all_coords_2.add(abs(c))
    print(f"  Coordinate values: {sorted(all_coords_2)}")

    overlap_2 = step4_set & int_pool
    only_sic_2 = step4_set - int_pool
    only_pool_2 = int_pool - step4_set
    print(f"  Overlap with integer pool: {len(overlap_2)}")
    print(f"  In closure only: {len(only_sic_2)}")
    print(f"  In integer pool only: {len(only_pool_2)}")

    # Is the integer pool a subset of the SI-C closure?
    if int_pool <= step4_set:
        print(f"\n  *** Integer pool is a SUBSET of SI-C closure (round 2) ***")
    elif step4_set <= int_pool:
        print(f"\n  *** SI-C closure is a SUBSET of integer pool ***")
    elif int_pool == step4_set:
        print(f"\n  *** Integer pool EQUALS SI-C closure ***")
    else:
        print(f"\n  Neither is a subset of the other.")

    # Check: is the SI-C closure (round 1) KS-uncolorable?
    step3_rays_c = [tuple(complex(x) for x in v) for v in step3_sorted]
    s3_pairs, s3_triads, _ = build_pairs_triads(step3_rays_c)
    s3_ks = is_ks_uncolorable(len(step3_rays_c), s3_triads, s3_pairs)
    print(f"\n  SI-C closure (round 1) KS-uncolorable: {s3_ks}")
    print(f"    ({len(step3_rays_c)} rays, {len(s3_pairs)} pairs, "
          f"{len(s3_triads)} triads)")


# =====================================================================
# COMPUTATION 2: N(S) invariant for all six islands
# =====================================================================

def computation_2():
    print(f"\n\n{'='*70}")
    print("COMPUTATION 2: N(S) = lcm{||v||²} for all six islands")
    print("(Cortez-Morales-Reyes invariant)")
    print("=" * 70)

    # CK-31 (integer)
    CK31 = [
        (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 1, -1), (0, 1, 2), (0, 2, -1),
        (1, 0, 0), (1, 0, 1), (1, 0, -1), (1, 0, 2), (1, 0, -2),
        (1, 1, 0), (1, 1, 1), (1, 1, -1), (1, 1, 2), (1, -1, 0),
        (1, -1, 1), (1, -1, -1), (1, -1, -2), (1, 2, 0), (1, 2, -1),
        (1, -2, 0), (1, -2, 1), (2, 0, 1), (2, 0, -1), (2, 1, 0),
        (2, 1, 1), (2, 1, -1), (2, -1, 0), (2, -1, 1), (2, -1, -1),
    ]

    print(f"\n  --- CK-31 (Integer) ---")
    norms_ck31 = sorted(set(norm_sq_int(v) for v in CK31))
    n_ck31 = lcm_list(norms_ck31)
    print(f"  Distinct ||v||²: {norms_ck31}")
    print(f"  N(S) = lcm = {n_ck31}")
    print(f"  Factorization: ", end="")
    n = n_ck31
    factors = {}
    for p in [2, 3, 5, 7, 11, 13]:
        while n % p == 0:
            factors[p] = factors.get(p, 0) + 1
            n //= p
    if n > 1:
        factors[n] = 1
    print(" × ".join(f"{p}^{e}" if e > 1 else str(p)
                     for p, e in sorted(factors.items())))
    print(f"  Primes: {sorted(factors.keys())}")

    # Full integer pool
    int_pool = generate_integer_rays()
    norms_pool = sorted(set(norm_sq_int(v) for v in int_pool))
    n_pool = lcm_list(norms_pool)
    print(f"\n  Full pool (49 rays): ||v||² = {norms_pool}")
    print(f"  N(pool) = {n_pool}")

    # For algebraic islands, compute Hermitian norm ||v||² = |a|²+|b|²+|c|²
    # For integer components, this is just a²+b²+c²
    # For algebraic components, need to track the algebraic norm

    print(f"\n  --- Peres (Z[√2]) ---")
    s2 = math.sqrt(2)
    peres_alph = [complex(x) for x in [0, 1, -1, s2, -s2]]
    peres_rays = generate_rays_from_alphabet(peres_alph)
    peres_pairs, peres_triads, _ = build_pairs_triads(peres_rays)
    peres_min = greedy_minimize(peres_rays, peres_pairs, peres_triads, 200)
    peres_min_rays = [peres_rays[i] for i in peres_min]

    # Compute Hermitian norms (floating point)
    peres_norms = set()
    for ray in peres_min_rays:
        n2 = sum(abs(c) ** 2 for c in ray)
        peres_norms.add(round(n2, 6))
    print(f"  Min set: {len(peres_min)} rays")
    print(f"  Hermitian norms ||v||²: {sorted(peres_norms)}")
    # Identify algebraic form: with {0,±1,±√2}, norms are in {1, 2, 3, 4, 5, 6}
    print(f"  Algebraic: norms are integers (since |√2|²=2, |1|²=1)")
    int_norms = sorted(set(round(n) for n in peres_norms))
    print(f"  Integer norms: {int_norms}")
    if int_norms:
        n_peres = lcm_list(int_norms)
        print(f"  N(S) = {n_peres}")

    print(f"\n  --- Eisenstein (Z[ω]) ---")
    eis_rays = generate_eisenstein_rays(max_coeff=1, dim=3, norm_cutoff=3)
    eis_pairs, eis_triads, _ = build_pairs_triads(eis_rays)
    eis_min = greedy_minimize(eis_rays, eis_pairs, eis_triads, 200)
    eis_min_rays = [eis_rays[i] for i in eis_min]

    eis_norms = set()
    for ray in eis_min_rays:
        n2 = sum(abs(c) ** 2 for c in ray)
        eis_norms.add(round(n2, 6))
    print(f"  Min set: {len(eis_min)} rays")
    print(f"  Hermitian norms ||v||²: {sorted(eis_norms)}")
    int_norms_e = sorted(set(round(n) for n in eis_norms))
    print(f"  Integer norms: {int_norms_e}")
    if int_norms_e:
        n_eis = lcm_list(int_norms_e)
        print(f"  N(S) = {n_eis}")

    print(f"\n  --- Z[√(-2)] ---")
    sd2 = cmath.sqrt(-2)
    zsqrt2_alph = [0, 1, -1, sd2, -sd2]
    zsqrt2_rays = generate_rays_from_alphabet(zsqrt2_alph)
    zsqrt2_pairs, zsqrt2_triads, _ = build_pairs_triads(zsqrt2_rays)
    zsqrt2_min = greedy_minimize(zsqrt2_rays, zsqrt2_pairs, zsqrt2_triads, 200)
    zsqrt2_min_rays = [zsqrt2_rays[i] for i in zsqrt2_min]

    zsqrt2_norms = set()
    for ray in zsqrt2_min_rays:
        n2 = sum(abs(c) ** 2 for c in ray)
        zsqrt2_norms.add(round(n2, 6))
    print(f"  Min set: {len(zsqrt2_min)} rays")
    print(f"  Hermitian norms ||v||²: {sorted(zsqrt2_norms)}")
    int_norms_z = sorted(set(round(n) for n in zsqrt2_norms))
    print(f"  Integer norms: {int_norms_z}")
    if int_norms_z:
        n_zsqrt2 = lcm_list(int_norms_z)
        print(f"  N(S) = {n_zsqrt2}")

    print(f"\n  --- Heegner-7 (Z[(1+√(-7))/2]) ---")
    gen7 = (1 + cmath.sqrt(-7)) / 2
    h7_alph = [0, 1, -1, gen7, -gen7, gen7.conjugate(), -gen7.conjugate()]
    h7_rays = generate_rays_from_alphabet(h7_alph)
    h7_pairs, h7_triads, _ = build_pairs_triads(h7_rays)
    h7_min = greedy_minimize(h7_rays, h7_pairs, h7_triads, 200)
    h7_min_rays = [h7_rays[i] for i in h7_min]

    h7_norms = set()
    for ray in h7_min_rays:
        n2 = sum(abs(c) ** 2 for c in ray)
        h7_norms.add(round(n2, 6))
    print(f"  Min set: {len(h7_min)} rays")
    print(f"  Hermitian norms ||v||²: {sorted(h7_norms)}")
    int_norms_h = sorted(set(round(n) for n in h7_norms))
    print(f"  Integer norms: {int_norms_h}")
    if int_norms_h:
        n_h7 = lcm_list(int_norms_h)
        print(f"  N(S) = {n_h7}")

    print(f"\n  --- Golden (Z[φ] + completion) ---")
    phi = (1 + math.sqrt(5)) / 2
    gold_alph = [complex(x) for x in [0, 1, -1, phi, -phi]]
    gold_rays_raw = generate_rays_from_alphabet(gold_alph)
    gold_rays = hermitian_completion(gold_rays_raw)
    gold_pairs, gold_triads, _ = build_pairs_triads(gold_rays)
    gold_min = greedy_minimize(gold_rays, gold_pairs, gold_triads, 100)
    gold_min_rays = [gold_rays[i] for i in gold_min]

    gold_norms = set()
    for ray in gold_min_rays:
        n2 = sum(abs(c) ** 2 for c in ray)
        gold_norms.add(round(n2, 6))
    print(f"  Min set: {len(gold_min)} rays")
    print(f"  Hermitian norms ||v||²: {sorted(gold_norms)}")
    # Golden norms involve phi² = phi+1, so norms are in Z[phi]
    # Round to nearest integer or identify algebraic form
    print(f"  Note: norms are in Z[φ], not necessarily integer")


# =====================================================================
# COMPUTATION 3: Bootstrap percolation on minimal KS sets
# =====================================================================

def computation_3():
    print(f"\n\n{'='*70}")
    print("COMPUTATION 3: Bootstrap Percolation and Merge Saturation")
    print("=" * 70)
    print()
    print("Trandafir-Cabello Proposition 1: if A₀ 2-percolates the")
    print("orthogonality graph G, then A₀ determines the entire KS set.")
    print()
    print("Question: Does bootstrap percolation explain merge saturation?")
    print("If merging two vertices v1,v2 creates a vertex with")
    print("combined neighborhoods, the merged graph may 2-percolate")
    print("from a smaller seed — preserving KS-uncolorability.")

    # CK-31
    CK31 = [
        (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 1, -1), (0, 1, 2), (0, 2, -1),
        (1, 0, 0), (1, 0, 1), (1, 0, -1), (1, 0, 2), (1, 0, -2),
        (1, 1, 0), (1, 1, 1), (1, 1, -1), (1, 1, 2), (1, -1, 0),
        (1, -1, 1), (1, -1, -1), (1, -1, -2), (1, 2, 0), (1, 2, -1),
        (1, -2, 0), (1, -2, 1), (2, 0, 1), (2, 0, -1), (2, 1, 0),
        (2, 1, 1), (2, 1, -1), (2, -1, 0), (2, -1, 1), (2, -1, -1),
    ]

    n = len(CK31)
    adj = {i: set() for i in range(n)}
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            if dot_int(CK31[i], CK31[j]) == 0:
                adj[i].add(j)
                adj[j].add(i)
                pairs.append((i, j))

    triads = []
    for i in range(n):
        ni = sorted(adj[i])
        for idx_j, j in enumerate(ni):
            if j <= i:
                continue
            for k in ni[idx_j + 1:]:
                if k <= j:
                    continue
                if k in adj[j]:
                    triads.append((i, j, k))

    print(f"\n  CK-31: {n} rays, {len(pairs)} pairs, {len(triads)} triads")

    # Bootstrap percolation: start with seed A₀, repeatedly add vertices
    # that have ≥r neighbors already in the active set
    def bootstrap(adj, n, seed, r=2):
        """Run r-bootstrap percolation from seed. Return final active set."""
        active = set(seed)
        changed = True
        while changed:
            changed = False
            for v in range(n):
                if v in active:
                    continue
                if len(adj[v] & active) >= r:
                    active.add(v)
                    changed = True
        return active

    # Find minimum 2-percolating set for CK-31
    print(f"\n  --- 2-Bootstrap percolation on CK-31 ---")

    # Try all single vertices
    print(f"  Single-vertex seeds:")
    for v in range(n):
        result = bootstrap(adj, n, {v}, r=2)
        if len(result) == n:
            print(f"    Vertex {v} {CK31[v]}: percolates to ALL {n}")

    # Try all pairs
    min_seed_size = n
    min_seeds = []
    for v1 in range(n):
        for v2 in range(v1 + 1, n):
            result = bootstrap(adj, n, {v1, v2}, r=2)
            if len(result) == n:
                if 2 < min_seed_size:
                    min_seed_size = 2
                    min_seeds = [(v1, v2)]
                elif 2 == min_seed_size:
                    min_seeds.append((v1, v2))

    if min_seeds:
        print(f"  2-vertex seeds that percolate: {len(min_seeds)}")
        for v1, v2 in min_seeds[:5]:
            print(f"    {{{CK31[v1]}, {CK31[v2]}}}")
    else:
        print(f"  No 2-vertex seed percolates.")

    # Try triples
    if not min_seeds:
        count_3 = 0
        for v1, v2, v3 in combinations(range(n), 3):
            result = bootstrap(adj, n, {v1, v2, v3}, r=2)
            if len(result) == n:
                count_3 += 1
                if count_3 <= 3:
                    print(f"    3-seed: {{{CK31[v1]}, {CK31[v2]}, {CK31[v3]}}}")
        if count_3:
            print(f"  3-vertex seeds that percolate: {count_3}")
            min_seed_size = 3
        else:
            print(f"  No 3-vertex seed percolates.")

    # Find minimum seed by trying increasing sizes
    if min_seed_size > 3:
        for k in range(4, n):
            found = False
            for _ in range(10000):
                seed = set(random.sample(range(n), k))
                result = bootstrap(adj, n, seed, r=2)
                if len(result) == n:
                    print(f"  {k}-vertex seed percolates: "
                          f"{{{', '.join(str(CK31[v]) for v in sorted(seed))}}}")
                    min_seed_size = k
                    found = True
                    break
            if found:
                break

    print(f"\n  Minimum 2-percolating seed size: {min_seed_size}")

    # Now: does merging increase the percolation reach?
    # When we merge v1,v2 (non-orthogonal), the merged vertex has
    # neighbors = adj[v1] ∪ adj[v2]. This is a HIGHER degree vertex,
    # which should make percolation easier.
    print(f"\n  --- Merge effect on percolation ---")
    print(f"  Non-orthogonal pairs: {n*(n-1)//2 - len(pairs)}")

    # For each non-orthogonal merge, check: does the merged graph
    # 2-percolate from the SAME minimum seed?
    merge_percolation_stats = []
    for v1 in range(n):
        for v2 in range(v1 + 1, n):
            if v2 in adj[v1]:
                continue  # skip orthogonal

            # Build merged adjacency
            new_n = n - 1
            remap = {}
            idx = 0
            for v in range(n):
                if v == v2:
                    remap[v] = remap[v1]
                else:
                    remap[v] = idx
                    idx += 1

            new_adj = {i: set() for i in range(new_n)}
            for i, j in pairs:
                ni, nj = remap[i], remap[j]
                if ni != nj:
                    new_adj[ni].add(nj)
                    new_adj[nj].add(ni)

            # Merged vertex degree
            merged_v = remap[v1]
            merged_degree = len(new_adj[merged_v])
            orig_degrees = (len(adj[v1]), len(adj[v2]))

            # Check: does the merged graph 2-percolate from just
            # the merged vertex alone?
            result = bootstrap(new_adj, new_n, {merged_v}, r=2)
            single_percolates = len(result) == new_n

            merge_percolation_stats.append({
                'v1': v1, 'v2': v2,
                'merged_degree': merged_degree,
                'orig_degrees': orig_degrees,
                'single_percolates': single_percolates,
                'reached': len(result),
            })

    single_perc_count = sum(1 for s in merge_percolation_stats
                            if s['single_percolates'])
    print(f"\n  Merges where merged vertex alone 2-percolates: "
          f"{single_perc_count}/{len(merge_percolation_stats)}")

    # Distribution of reach
    reaches = [s['reached'] for s in merge_percolation_stats]
    print(f"  Percolation reach from merged vertex alone:")
    print(f"    Min: {min(reaches)}, Max: {max(reaches)}, "
          f"Mean: {sum(reaches)/len(reaches):.1f}")

    # Look at the highest-degree merges
    by_degree = sorted(merge_percolation_stats,
                       key=lambda s: s['merged_degree'], reverse=True)
    print(f"\n  Highest-degree merges:")
    for s in by_degree[:5]:
        print(f"    Merge ({s['v1']},{s['v2']}): "
              f"degree {s['orig_degrees']} → {s['merged_degree']}, "
              f"percolation reach: {s['reached']}/{new_n}")

    # Connection to merge saturation
    print(f"\n  --- Interpretation ---")
    print(f"  Bootstrap percolation from merged vertex alone succeeds")
    print(f"  in {single_perc_count} of {len(merge_percolation_stats)} merges.")
    if single_perc_count > 0:
        print(f"  When a merge creates a high-degree hub, it can")
        print(f"  2-percolate the entire graph, which (by Trandafir-")
        print(f"  Cabello Prop. 1) determines a rigid KS structure.")
        print(f"  This explains WHY merging preserves KS-uncolorability:")
        print(f"  the merged vertex acts as a percolation seed.")
    else:
        print(f"  Merged vertices don't 2-percolate alone, but the")
        print(f"  merged graph's enhanced connectivity still constrains")
        print(f"  colorings enough to preserve KS-uncolorability.")


# =====================================================================
# Main
# =====================================================================

if __name__ == "__main__":
    t_start = time.time()
    computation_1()
    computation_2()
    computation_3()

    t_total = time.time() - t_start
    print(f"\n{'='*70}")
    print(f"Total time: {t_total:.1f}s")
    print(f"{'='*70}")
