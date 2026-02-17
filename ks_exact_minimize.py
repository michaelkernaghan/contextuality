"""
ks_exact_minimize.py -- Exact minimization of KS sets via MUS + enhanced greedy
================================================================================

Strategy 1: Go beyond greedy deletion to find true minimum KS subsets.

Methods:
  A) MUS (Minimal Unsatisfiable Subset) extraction via PySAT
     - Finds clause-minimal unsatisfiable core, maps back to rays
     - Multiple extractions with different orderings

  B) Enhanced greedy with diverse orderings
     - Sort by degree (ascending = remove high-degree first)
     - Sort by triad participation
     - Sort by betweenness-like centrality
     - 2000 random trials

  C) Swap-based local search
     - Start from greedy minimum, try swapping rays in/out
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

import cmath
import math
import random
import time
from collections import Counter

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
from ks_sat import CK31_VECTORS

random.seed(42)


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


def is_ks_uncolorable(n_vertices, triads, ortho_pairs):
    """Test KS-uncolorability."""
    if not triads and not ortho_pairs:
        return False
    solver = Glucose4()
    for a, b, c in triads:
        va, vb, vc = a + 1, b + 1, c + 1
        solver.add_clause([va, vb, vc])
        solver.add_clause([-va, -vb])
        solver.add_clause([-va, -vc])
        solver.add_clause([-vb, -vc])
    for i, j in ortho_pairs:
        vi, vj = i + 1, j + 1
        solver.add_clause([-vi, -vj])
    result = solver.solve()
    solver.delete()
    return not result


def subset_check(keep_indices, all_pairs, all_triads):
    """Check if a subset of rays is KS-uncolorable."""
    keep_set = set(keep_indices)
    remap = {old: new for new, old in enumerate(keep_indices)}
    sub_triads = [(remap[a], remap[b], remap[c])
                  for a, b, c in all_triads
                  if a in keep_set and b in keep_set and c in keep_set]
    sub_pairs = [(remap[i], remap[j])
                 for i, j in all_pairs
                 if i in keep_set and j in keep_set]
    return is_ks_uncolorable(len(keep_indices), sub_triads, sub_pairs)


def greedy_minimize_ordered(n_rays, all_pairs, all_triads, order, floor=20):
    """Greedy deletion in a specific order."""
    current = list(range(n_rays))
    for candidate in order:
        if candidate not in current:
            continue
        test = [r for r in current if r != candidate]
        if len(test) < floor:
            break
        if subset_check(test, all_pairs, all_triads):
            current = test
    return current


def mus_extraction(n_rays, all_pairs, all_triads):
    """Extract MUS and map back to rays.
    Uses assumption-based approach: one assumption per ray."""
    # Build clauses with tracking
    # For each ray i, assumption variable: n_rays + i + 1
    clauses = []
    clause_rays = []  # which rays each clause involves

    for a, b, c in all_triads:
        involved = {a, b, c}
        va, vb, vc = a + 1, b + 1, c + 1
        clauses.append([va, vb, vc])
        clause_rays.append(involved)
        clauses.append([-va, -vb])
        clause_rays.append(involved)
        clauses.append([-va, -vc])
        clause_rays.append(involved)
        clauses.append([-vb, -vc])
        clause_rays.append(involved)

    for i, j in all_pairs:
        involved = {i, j}
        vi, vj = i + 1, j + 1
        clauses.append([-vi, -vj])
        clause_rays.append(involved)

    # Use assumption-based MUS: for each ray, if we "deactivate" it,
    # all clauses involving it become satisfied trivially.
    # We use selector variables: for ray i, selector s_i.
    # Clause C involving rays R gets augmented: C ∨ ¬s_{r1} ∨ ¬s_{r2} ...
    # (clause is trivially satisfied if any of its rays is deactivated)

    base = n_rays + 1  # selector variables start here
    augmented_clauses = []
    for idx, clause in enumerate(clauses):
        rays_involved = clause_rays[idx]
        # Add negative selectors for involved rays
        aug = clause + [-(base + r) for r in rays_involved]
        augmented_clauses.append(aug)

    # Assumptions: all selectors true (all rays active)
    assumptions = [base + r for r in range(n_rays)]

    solver = Glucose4()
    for cl in augmented_clauses:
        solver.add_clause(cl)

    # Verify UNSAT with all assumptions
    result = solver.solve(assumptions=assumptions)
    if result:
        solver.delete()
        return None  # not uncolorable

    # Get UNSAT core (subset of assumptions that suffice for UNSAT)
    core = solver.get_core()
    solver.delete()

    if core is None:
        return None

    # Map back to ray indices
    core_rays = sorted([lit - base for lit in core if lit >= base])
    return core_rays


def swap_search(initial_set, n_rays, all_pairs, all_triads, max_swaps=5000):
    """Try swapping rays in/out to find smaller sets."""
    current = set(initial_set)
    best = set(initial_set)
    outside = set(range(n_rays)) - current

    improvements = 0
    for _ in range(max_swaps):
        if not outside:
            break
        # Try removing a ray
        ray_out = random.choice(list(current))
        test = sorted(current - {ray_out})
        if len(test) >= 20 and subset_check(test, all_pairs, all_triads):
            current = set(test)
            outside.add(ray_out)
            if len(current) < len(best):
                best = set(current)
                improvements += 1
            continue

        # Try swapping: remove one, add one from outside
        ray_in = random.choice(list(outside))
        test = sorted((current - {ray_out}) | {ray_in})
        if subset_check(test, all_pairs, all_triads):
            current = set(test)
            outside = set(range(n_rays)) - current

    return sorted(best), improvements


def analyze_pool(name, rays, n_greedy_trials=2000):
    """Full analysis of one pool."""
    print(f"\n{'='*70}")
    print(f"POOL: {name} ({len(rays)} rays)")
    print(f"{'='*70}")

    pairs, triads, adj = build_pairs_triads(rays)
    n = len(rays)
    print(f"  Pairs: {len(pairs)}, Triads: {len(triads)}")

    if not is_ks_uncolorable(n, triads, pairs):
        print(f"  NOT KS-uncolorable, skipping.")
        return None

    # Ray statistics
    degree = [len(adj[i]) for i in range(n)]
    triad_count = Counter()
    for a, b, c in triads:
        triad_count[a] += 1
        triad_count[b] += 1
        triad_count[c] += 1

    # --- Method A: MUS extraction ---
    print(f"\n  --- Method A: MUS (UNSAT core) extraction ---")
    t0 = time.time()
    core_rays = mus_extraction(n, pairs, triads)
    t1 = time.time()
    if core_rays is not None:
        # Verify the core is actually KS-uncolorable
        ks = subset_check(core_rays, pairs, triads)
        print(f"  UNSAT core: {len(core_rays)} rays (KS={ks}) [{t1-t0:.2f}s]")

        # Now greedy-minimize the core
        core_pairs_local = [(i, j) for i, j in pairs
                           if i in set(core_rays) and j in set(core_rays)]
        core_triads_local = [(a, b, c) for a, b, c in triads
                            if a in set(core_rays) and b in set(core_rays) and c in set(core_rays)]

        if ks:
            # Further minimize the core via greedy
            best_from_core = len(core_rays)
            for trial in range(200):
                order = list(core_rays)
                random.shuffle(order)
                result = greedy_minimize_ordered(n, pairs, triads,
                    [r for r in order] + [r for r in range(n) if r not in core_rays],
                    floor=20)
                if len(result) < best_from_core:
                    best_from_core = len(result)
            print(f"  Core minimized to: {best_from_core} rays")
    else:
        print(f"  MUS extraction failed")

    # --- Method B: Enhanced greedy ---
    print(f"\n  --- Method B: Enhanced greedy ({n_greedy_trials} trials) ---")
    best_size = n
    best_subset = list(range(n))
    t0 = time.time()

    # Ordering strategies
    strategies = {
        'degree_asc': sorted(range(n), key=lambda i: degree[i]),
        'degree_desc': sorted(range(n), key=lambda i: -degree[i]),
        'triad_asc': sorted(range(n), key=lambda i: triad_count.get(i, 0)),
        'triad_desc': sorted(range(n), key=lambda i: -triad_count.get(i, 0)),
        'combined_asc': sorted(range(n), key=lambda i: degree[i] + 3*triad_count.get(i, 0)),
    }

    for sname, order in strategies.items():
        result = greedy_minimize_ordered(n, pairs, triads, order)
        if len(result) < best_size:
            best_size = len(result)
            best_subset = result
        print(f"    {sname}: {len(result)} rays")

    # Random trials
    for trial in range(n_greedy_trials):
        order = list(range(n))
        random.shuffle(order)
        result = greedy_minimize_ordered(n, pairs, triads, order)
        if len(result) < best_size:
            best_size = len(result)
            best_subset = result
            print(f"    Random trial {trial+1}: new best = {best_size}")
        if (trial + 1) % 500 == 0:
            print(f"    ... {trial+1}/{n_greedy_trials} random trials, best = {best_size}")

    t1 = time.time()
    print(f"  Best from greedy: {best_size} rays [{t1-t0:.1f}s]")

    # --- Method C: Swap search ---
    print(f"\n  --- Method C: Swap-based local search ---")
    t0 = time.time()
    best_swap_size = best_size
    for trial in range(10):
        # Start from a random greedy minimum
        order = list(range(n))
        random.shuffle(order)
        start = greedy_minimize_ordered(n, pairs, triads, order)
        swapped, impr = swap_search(start, n, pairs, triads, max_swaps=2000)
        if len(swapped) < best_swap_size:
            best_swap_size = len(swapped)
            print(f"    Swap trial {trial+1}: {len(swapped)} rays ({impr} improvements)")
    t1 = time.time()
    print(f"  Best from swaps: {best_swap_size} rays [{t1-t0:.1f}s]")

    final_best = min(best_size, best_swap_size)
    if core_rays is not None and subset_check(core_rays, pairs, triads):
        final_best = min(final_best, len(core_rays))

    print(f"\n  >>> FINAL MINIMUM for {name}: {final_best} rays")
    if final_best < 31:
        print(f"  *** SUB-31 KS SET FOUND! ***")
    return final_best


# =====================================================================
# Build pools
# =====================================================================

def build_all_pools():
    pools = {}

    print("Building pools...")
    int_alph = [complex(x) for x in [0, 1, -1, 2, -2]]
    pools['Integer'] = generate_rays_from_alphabet(int_alph)

    eis_rays = generate_eisenstein_rays(max_coeff=1, dim=3, norm_cutoff=3)
    pools['Eisenstein'] = eis_rays

    s2 = math.sqrt(2)
    pools['Peres'] = generate_rays_from_alphabet([complex(x) for x in [0, 1, -1, s2, -s2]])

    sd2 = cmath.sqrt(-2)
    pools['Z[sqrt(-2)]'] = generate_rays_from_alphabet([0, 1, -1, sd2, -sd2])

    gen7 = (1 + cmath.sqrt(-7)) / 2
    pools['Heegner-7'] = generate_rays_from_alphabet(
        [0, 1, -1, gen7, -gen7, gen7.conjugate(), -gen7.conjugate()])

    phi = (1 + math.sqrt(5)) / 2
    golden_raw = generate_rays_from_alphabet([complex(x) for x in [0, 1, -1, phi, -phi]])
    pools['Golden ratio'] = hermitian_completion(golden_raw)

    for name, rays in pools.items():
        print(f"  {name}: {len(rays)} rays")

    return pools


if __name__ == "__main__":
    print("=" * 70)
    print("STRATEGY 1: EXACT MINIMIZATION OF KS SETS")
    print("MUS extraction + enhanced greedy + swap search")
    print("=" * 70)

    pools = build_all_pools()

    summary = {}
    for name, rays in pools.items():
        result = analyze_pool(name, rays, n_greedy_trials=2000)
        if result is not None:
            summary[name] = result

    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    for name, min_size in summary.items():
        marker = " *** SUB-31! ***" if min_size < 31 else ""
        print(f"  {name:<16}: minimum = {min_size}{marker}")
    print(f"{'='*70}")
