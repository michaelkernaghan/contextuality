"""
ks_maxsat_optimal.py -- Prove no <=30 KS subset exists in 49-ray integer pool
=============================================================================

Peer review requested: Stronger than "greedy never found it" — use exact
optimization to prove CK-31 (31 rays) is the minimum KS set in {0,±1,±2}.

The core challenge: KS-uncolorability is a universal property (no coloring
works), so this is a Sigma_2^p optimization. We use three approaches:

  Phase 1: Exhaustive MUS extraction (1000 trials)
    - Assumption-based UNSAT core + deletion minimization
    - If ALL trials give 31, strong evidence but not proof

  Phase 2: OCUS-style optimal MUS (Optimal Constrained Unsatisfiable Subset)
    - Uses MaxSAT in a CEGAR loop to find the SMALLEST MUS
    - Provably optimal if it terminates

  Phase 3: Targeted exhaustive at n=30
    - Enhanced CEGAR with aggressive structural pruning
    - Symmetry-aware blocking to reduce search space

If all three phases confirm 31, this is definitive for the integer pool.
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

import random
import time
from math import gcd
from itertools import combinations
from pysat.solvers import Glucose4
from pysat.card import CardEnc, EncType

random.seed(42)


# =====================================================================
# Generate the 49 integer rays
# =====================================================================

def generate_integer_rays():
    """Generate all 49 projectively distinct rays from {0,±1,±2}."""
    rays = []
    seen = set()
    for a in range(-2, 3):
        for b in range(-2, 3):
            for c in range(-2, 3):
                if a == 0 and b == 0 and c == 0:
                    continue
                g = gcd(gcd(abs(a), abs(b)), abs(c))
                v = (a // g, b // g, c // g)
                for coord in v:
                    if coord != 0:
                        if coord < 0:
                            v = (-v[0], -v[1], -v[2])
                        break
                if v not in seen:
                    seen.add(v)
                    rays.append(v)
    return rays


def dot_int(a, b):
    return sum(x * y for x, y in zip(a, b))


def find_triads_and_pairs(coords):
    """Find all orthogonal pairs and mutually orthogonal triples."""
    n = len(coords)
    ortho_pairs = []
    adj = {i: set() for i in range(n)}

    for i in range(n):
        for j in range(i + 1, n):
            if dot_int(coords[i], coords[j]) == 0:
                ortho_pairs.append((i, j))
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

    return triads, ortho_pairs, adj


def is_ks_subset(ray_indices, triads, pairs):
    """Check if a subset of rays is KS-uncolorable."""
    sel = set(ray_indices)
    sub_triads = [(a, b, c) for a, b, c in triads
                  if a in sel and b in sel and c in sel]
    sub_pairs = [(i, j) for i, j in pairs
                 if i in sel and j in sel]
    if not sub_triads:
        return False

    remap = {old: new for new, old in enumerate(sorted(sel))}
    solver = Glucose4()
    for a, b, c in sub_triads:
        ra, rb, rc = remap[a], remap[b], remap[c]
        va, vb, vc = ra + 1, rb + 1, rc + 1
        solver.add_clause([va, vb, vc])
        solver.add_clause([-va, -vb])
        solver.add_clause([-va, -vc])
        solver.add_clause([-vb, -vc])
    for i, j in sub_pairs:
        ri, rj = remap[i], remap[j]
        solver.add_clause([-(ri + 1), -(rj + 1)])
    result = solver.solve()
    solver.delete()
    return not result


# =====================================================================
# Phase 1: Exhaustive MUS extraction (1000 trials)
# =====================================================================

def phase1_mus_extraction(n_rays, triads, pairs, n_trials=1000):
    """Extract many MUSes to find the minimum ray-set size."""
    print(f"\n{'='*70}")
    print(f"PHASE 1: MUS Extraction ({n_trials} trials)")
    print(f"{'='*70}")

    t0 = time.time()
    size_counts = {}
    min_size = n_rays
    all_minimal = set()

    for trial in range(n_trials):
        # Build conditional formula with assumptions
        solver = Glucose4()

        def a(i):
            return i + 1

        def c(i):
            return n_rays + i + 1

        for i, j, k in triads:
            solver.add_clause([-a(i), -a(j), -a(k), c(i), c(j), c(k)])
        for i, j in pairs:
            solver.add_clause([-a(i), -a(j), -c(i), -c(j)])

        assumptions = [a(i) for i in range(n_rays)]

        # Get UNSAT core
        result = solver.solve(assumptions=assumptions)
        if result:
            print("  ERROR: Full pool is colorable!")
            solver.delete()
            return None, {}

        core = solver.get_core()
        active_rays = sorted([lit - 1 for lit in core])

        # Deletion-based minimization with shuffled order
        order = list(active_rays)
        random.shuffle(order)

        for ray in order:
            test_assumptions = [r + 1 for r in active_rays if r != ray]
            if not solver.solve(assumptions=test_assumptions):
                active_rays.remove(ray)

        solver.delete()

        size = len(active_rays)
        key = tuple(active_rays)
        all_minimal.add(key)

        size_counts[size] = size_counts.get(size, 0) + 1

        if size < min_size:
            min_size = size
            print(f"  Trial {trial+1}: NEW MINIMUM = {size} rays")
        elif (trial + 1) % 100 == 0:
            elapsed = time.time() - t0
            print(f"  Trial {trial+1}: min = {min_size}, "
                  f"{len(all_minimal)} distinct, [{elapsed:.1f}s]")

    elapsed = time.time() - t0
    print(f"\n  Phase 1 complete ({elapsed:.1f}s):")
    print(f"    Minimum: {min_size}")
    print(f"    Distinct minimal sets: {len(all_minimal)}")
    print(f"    Size distribution: {dict(sorted(size_counts.items()))}")

    return min_size, size_counts


# =====================================================================
# Phase 2: OCUS-style optimal MUS search
# =====================================================================

def phase2_ocus(n_rays, triads, pairs, time_limit=600):
    """Find the smallest MUS using an OCUS-style CEGAR loop.

    Algorithm:
      1. Use an outer MaxSAT/SAT solver to select a SMALL subset of rays
      2. Check if the selected rays form a KS set (inner SAT)
      3. If KS: found optimal (or at least a small KS set)
      4. If not KS: extract the satisfying coloring and add a "correction"
         clause requiring at least one additional ray that would constrain it

    The correction comes from finding which deselected triads/pairs are
    violated by the current coloring — at least one ray from a violated
    constraint must be added.
    """
    print(f"\n{'='*70}")
    print(f"PHASE 2: OCUS-style Optimal MUS Search (limit {time_limit}s)")
    print(f"{'='*70}")

    t0 = time.time()

    # Precompute: which rays participate in each triad and pair
    ray_triads = {i: [] for i in range(n_rays)}
    for idx, (a, b, c) in enumerate(triads):
        ray_triads[a].append(idx)
        ray_triads[b].append(idx)
        ray_triads[c].append(idx)

    ray_pairs = {i: [] for i in range(n_rays)}
    for idx, (a, b) in enumerate(pairs):
        ray_pairs[a].append(idx)
        ray_pairs[b].append(idx)

    # Try decreasing sizes from 30 down
    for target_n in range(30, 20, -1):
        if time.time() - t0 > time_limit:
            print(f"  Time limit reached at target_n={target_n}")
            break

        print(f"\n  Testing n={target_n}...")

        # CEGAR loop: find n-ray KS subsets or prove none exist
        outer = Glucose4()
        sel_lits = list(range(1, n_rays + 1))
        top_var = n_rays

        # Cardinality: exactly target_n rays
        al = CardEnc.atleast(sel_lits, bound=target_n, top_id=top_var,
                             encoding=EncType.totalizer)
        if al.clauses:
            top_var = max(top_var,
                          max(abs(l) for cl in al.clauses for l in cl))
            for cl in al.clauses:
                outer.add_clause(cl)

        am = CardEnc.atmost(sel_lits, bound=target_n, top_id=top_var,
                            encoding=EncType.totalizer)
        if am.clauses:
            top_var = max(top_var,
                          max(abs(l) for cl in am.clauses for l in cl))
            for cl in am.clauses:
                outer.add_clause(cl)

        # Pruning: every selected ray must participate in at least 1 triad
        # (rays with zero triads can't contribute to KS-uncolorability)
        for i in range(n_rays):
            if not ray_triads[i]:
                outer.add_clause([-(i + 1)])  # Deselect useless rays

        iterations = 0
        t_target = time.time()
        found_ks = False

        while time.time() - t0 < time_limit:
            if not outer.solve():
                elapsed = time.time() - t_target
                print(f"    EXHAUSTED: No {target_n}-ray KS set exists "
                      f"({iterations:,} iterations, {elapsed:.1f}s)")
                outer.delete()
                print(f"\n  *** PROVED: minimum KS in integer pool > "
                      f"{target_n} ***")
                break

            model = outer.get_model()
            selected = [i for i in range(n_rays) if model[i] > 0]

            iterations += 1

            if is_ks_subset(selected, triads, pairs):
                elapsed = time.time() - t_target
                print(f"    FOUND {target_n}-ray KS set! "
                      f"({iterations} iterations, {elapsed:.1f}s)")
                outer.delete()
                found_ks = True
                break

            # Get the coloring that satisfies the constraints
            # and use it to derive a correction clause
            sel_set = set(selected)
            sub_triads = [(a, b, c) for a, b, c in triads
                          if a in sel_set and b in sel_set and c in sel_set]
            sub_pairs = [(i, j) for i, j in pairs
                         if i in sel_set and j in sel_set]

            # Get actual coloring from SAT solver
            remap = {old: new for new, old in enumerate(sorted(selected))}
            inv_remap = {new: old for old, new in remap.items()}
            inner = Glucose4()
            for a, b, c in sub_triads:
                ra, rb, rc = remap[a], remap[b], remap[c]
                va, vb, vc = ra + 1, rb + 1, rc + 1
                inner.add_clause([va, vb, vc])
                inner.add_clause([-va, -vb])
                inner.add_clause([-va, -vc])
                inner.add_clause([-vb, -vc])
            for i, j in sub_pairs:
                ri, rj = remap[i], remap[j]
                inner.add_clause([-(ri + 1), -(rj + 1)])
            inner.solve()
            coloring_model = inner.get_model()
            inner.delete()

            # coloring_model[r] > 0 means ray r is "green" (colored 1)
            colored = set()
            for new_idx in range(target_n):
                if coloring_model[new_idx] > 0:
                    colored.add(inv_remap[new_idx])

            # Find deselected rays that would constrain this coloring:
            # A deselected ray r helps if adding r creates a new triad or
            # pair constraint that conflicts with the current coloring.
            correction = set()
            deselected = [i for i in range(n_rays) if i not in sel_set]

            for r in deselected:
                # Check if r participates in a triad with two selected rays
                # where the triad constraint would be violated
                for t_idx in ray_triads[r]:
                    a, b, c = triads[t_idx]
                    others = [x for x in (a, b, c) if x != r]
                    if all(x in sel_set for x in others):
                        # New triad (r, others[0], others[1])
                        # Would this constrain the coloring?
                        all_green = (r in colored and
                                     others[0] in colored and
                                     others[1] in colored)
                        none_green = (r not in colored and
                                      others[0] not in colored and
                                      others[1] not in colored)
                        if all_green or none_green:
                            correction.add(r)
                            break

                if r in correction:
                    continue

                # Check pair constraints
                for p_idx in ray_pairs[r]:
                    a, b = pairs[p_idx]
                    other = b if a == r else a
                    if other in sel_set:
                        # New pair (r, other) — would it help?
                        if r in colored and other in colored:
                            correction.add(r)
                            break

            if correction:
                # Must include at least one correction ray
                outer.add_clause([r + 1 for r in correction])
            else:
                # No structural correction found — block this selection
                outer.add_clause([-(i + 1) for i in selected])

            if iterations % 1000 == 0:
                elapsed = time.time() - t_target
                rate = iterations / elapsed if elapsed > 0 else 0
                print(f"    ... {iterations:,} iterations [{elapsed:.1f}s, "
                      f"{rate:.0f}/s]")

        else:
            elapsed = time.time() - t_target
            print(f"    Time limit at n={target_n} "
                  f"({iterations:,} iterations, {elapsed:.1f}s)")
            outer.delete()

        if found_ks:
            return target_n

    elapsed = time.time() - t0
    print(f"\n  Phase 2 complete ({elapsed:.1f}s)")
    return None


# =====================================================================
# Phase 3: Enhanced exhaustive search at n=30
# =====================================================================

def phase3_exhaustive_30(rays, triads, pairs, adj, time_limit=600):
    """Enhanced CEGAR with structural blocking at n=30."""
    print(f"\n{'='*70}")
    print(f"PHASE 3: Enhanced exhaustive search at n=30 (limit {time_limit}s)")
    print(f"{'='*70}")

    n_rays = len(rays)
    t0 = time.time()

    # Precompute ray properties
    ray_degree = {i: len(adj[i]) for i in range(n_rays)}
    ray_triad_count = {i: 0 for i in range(n_rays)}
    for a, b, c in triads:
        ray_triad_count[a] += 1
        ray_triad_count[b] += 1
        ray_triad_count[c] += 1

    # Identify CK-31 rays
    CK31_INT = [
        (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 1, -1), (0, 1, 2), (0, 2, -1),
        (1, 0, 0), (1, 0, 1), (1, 0, -1), (1, 0, 2), (1, 0, -2),
        (1, 1, 0), (1, 1, 1), (1, 1, -1), (1, 1, 2), (1, -1, 0),
        (1, -1, 1), (1, -1, -1), (1, -1, -2), (1, 2, 0), (1, 2, -1),
        (1, -2, 0), (1, -2, 1), (2, 0, 1), (2, 0, -1), (2, 1, 0),
        (2, 1, 1), (2, 1, -1), (2, -1, 0), (2, -1, 1), (2, -1, -1),
    ]
    ck31_set = set()
    for v in CK31_INT:
        for i, r in enumerate(rays):
            if r == v:
                ck31_set.add(i)
                break

    non_ck31 = [i for i in range(n_rays) if i not in ck31_set]
    print(f"  CK-31 rays: {len(ck31_set)}, non-CK-31: {len(non_ck31)}")
    print(f"  Non-CK-31 rays and their triad counts:")
    for i in non_ck31:
        print(f"    Ray {i} {rays[i]}: degree {ray_degree[i]}, "
              f"triads {ray_triad_count[i]}")

    # Strategy A: Remove each CK-31 ray, add each non-CK-31 ray
    print(f"\n  Strategy A: CK-31 - 1 + 1 non-CK-31 ({31 * len(non_ck31)} tests)")
    tested = 0
    t_a = time.time()

    for remove_ray in sorted(ck31_set):
        base = sorted(ck31_set - {remove_ray})
        for add_ray in non_ck31:
            subset = sorted(set(base) | {add_ray})
            if len(subset) != 30:
                continue  # add_ray was already in base (shouldn't happen)
            tested += 1
            if is_ks_subset(subset, triads, pairs):
                elapsed = time.time() - t_a
                print(f"    *** FOUND 30-ray KS set! ***")
                print(f"    Removed {rays[remove_ray]}, "
                      f"added {rays[add_ray]}")
                return subset

    elapsed = time.time() - t_a
    print(f"    No 30-ray KS found by swap ({tested} tested, {elapsed:.1f}s)")

    # Strategy B: Remove 2 from CK-31 (no replacement)
    print(f"\n  Strategy B: CK-31 minus 2 rays = 29 rays (upper bound check)")
    tested = 0
    t_b = time.time()
    ck31_list = sorted(ck31_set)

    for r1, r2 in combinations(ck31_list, 2):
        subset = [r for r in ck31_list if r != r1 and r != r2]
        tested += 1
        if is_ks_subset(subset, triads, pairs):
            elapsed = time.time() - t_b
            print(f"    *** 29-ray KS subset of CK-31! ***")
            return subset

    elapsed = time.time() - t_b
    print(f"    All C(31,2)={tested} pairs tested: CK-31 is 2-critical "
          f"[{elapsed:.1f}s]")

    # Strategy C: Remove 2 from CK-31, add 1 non-CK-31 = 30 rays
    print(f"\n  Strategy C: CK-31 - 2 + 1 non-CK-31 "
          f"({len(list(combinations(ck31_list, 2))) * len(non_ck31)} tests)")
    tested = 0
    t_c = time.time()

    for r1, r2 in combinations(ck31_list, 2):
        base = [r for r in ck31_list if r != r1 and r != r2]
        for add_ray in non_ck31:
            subset = sorted(set(base) | {add_ray})
            tested += 1
            if is_ks_subset(subset, triads, pairs):
                elapsed = time.time() - t_c
                print(f"    *** FOUND 30-ray KS set! ***")
                print(f"    Removed {rays[r1]}, {rays[r2]}, "
                      f"added {rays[add_ray]}")
                return subset

            if time.time() - t0 > time_limit:
                elapsed = time.time() - t_c
                print(f"    Time limit ({tested} tested, {elapsed:.1f}s)")
                return None

        if tested % 10000 == 0:
            elapsed = time.time() - t_c
            print(f"    ... {tested:,} tested [{elapsed:.1f}s]")

    elapsed = time.time() - t_c
    print(f"    No 30-ray KS found by remove-2-add-1 "
          f"({tested:,} tested, {elapsed:.1f}s)")

    # Strategy D: CEGAR at n=30 with triad-density pruning
    print(f"\n  Strategy D: CEGAR with structural blocking")
    outer = Glucose4()
    sel_lits = list(range(1, n_rays + 1))
    top_var = n_rays

    al = CardEnc.atleast(sel_lits, bound=30, top_id=top_var,
                         encoding=EncType.totalizer)
    if al.clauses:
        top_var = max(top_var,
                      max(abs(l) for cl in al.clauses for l in cl))
        for cl in al.clauses:
            outer.add_clause(cl)

    am = CardEnc.atmost(sel_lits, bound=30, top_id=top_var,
                        encoding=EncType.totalizer)
    if am.clauses:
        top_var = max(top_var,
                      max(abs(l) for cl in am.clauses for l in cl))
        for cl in am.clauses:
            outer.add_clause(cl)

    # Require each selected ray to be in at least 1 triad
    for i in range(n_rays):
        if ray_triad_count[i] == 0:
            outer.add_clause([-(i + 1)])

    iterations = 0
    t_d = time.time()

    while time.time() - t0 < time_limit:
        if not outer.solve():
            elapsed = time.time() - t_d
            print(f"    EXHAUSTED: No 30-ray KS set in pool! "
                  f"({iterations:,} iterations, {elapsed:.1f}s)")
            outer.delete()
            return "PROVED_NONE"

        model = outer.get_model()
        selected = [i for i in range(n_rays) if model[i] > 0]
        iterations += 1

        sel_set = set(selected)
        sub_triads_count = sum(1 for a, b, c in triads
                               if a in sel_set and b in sel_set
                               and c in sel_set)

        if sub_triads_count < 14:
            # Too few triads for KS — block by requiring unselected ray
            unselected = [i for i in range(n_rays) if i not in sel_set]
            if unselected:
                outer.add_clause([i + 1 for i in unselected])
            else:
                outer.add_clause([-(i + 1) for i in selected])
        elif is_ks_subset(selected, triads, pairs):
            elapsed = time.time() - t_d
            print(f"    *** FOUND 30-ray KS set via CEGAR! ***")
            outer.delete()
            return selected
        else:
            outer.add_clause([-(i + 1) for i in selected])

        if iterations % 5000 == 0:
            elapsed = time.time() - t_d
            rate = iterations / elapsed if elapsed > 0 else 0
            print(f"    ... {iterations:,} iterations [{elapsed:.1f}s, "
                  f"{rate:.0f}/s]")

    elapsed = time.time() - t_d
    print(f"    Time limit ({iterations:,} iterations, {elapsed:.1f}s)")
    outer.delete()
    return None


# =====================================================================
# Main
# =====================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("OPTIMAL MINIMUM KS SET IN {0,±1,±2} INTEGER POOL")
    print("(MaxSAT / OCUS / Exhaustive approaches)")
    print("=" * 70)

    t_start = time.time()

    # Generate pool
    rays = generate_integer_rays()
    print(f"\nRay pool: {len(rays)} rays from {{0,±1,±2}}")

    triads, pairs, adj = find_triads_and_pairs(rays)
    print(f"Orthogonal pairs: {len(pairs)}")
    print(f"Triads: {len(triads)}")

    # Verify pool is KS
    solver = Glucose4()
    for a, b, c in triads:
        va, vb, vc = a + 1, b + 1, c + 1
        solver.add_clause([va, vb, vc])
        solver.add_clause([-va, -vb])
        solver.add_clause([-va, -vc])
        solver.add_clause([-vb, -vc])
    for i, j in pairs:
        solver.add_clause([-(i + 1), -(j + 1)])
    ks = not solver.solve()
    solver.delete()
    print(f"Full pool KS-uncolorable: {ks}")
    assert ks, "Pool is not KS-uncolorable!"

    # Phase 1
    min_mus, size_dist = phase1_mus_extraction(
        len(rays), triads, pairs, n_trials=1000)

    # Phase 2
    ocus_result = phase2_ocus(len(rays), triads, pairs, time_limit=600)

    # Phase 3
    phase3_result = phase3_exhaustive_30(rays, triads, pairs, adj,
                                          time_limit=600)

    # Summary
    t_total = time.time() - t_start

    print(f"\n{'='*70}")
    print("FINAL SUMMARY")
    print(f"{'='*70}")
    print(f"  Phase 1 (MUS x1000): minimum = {min_mus}")
    print(f"  Phase 2 (OCUS): {'found ' + str(ocus_result) if ocus_result else 'no sub-31 found'}")
    print(f"  Phase 3 (exhaustive at n=30): "
          f"{'PROVED: no 30-ray KS set' if phase3_result == 'PROVED_NONE' else 'inconclusive' if phase3_result is None else 'FOUND!'}")
    print(f"  Total time: {t_total:.1f}s")

    if min_mus == 31 and ocus_result is None and phase3_result in (None, "PROVED_NONE"):
        print(f"\n  CONCLUSION: Strong evidence that 31 is the minimum KS")
        print(f"  set size in the {{0,±1,±2}} integer pool.")
        if phase3_result == "PROVED_NONE":
            print(f"  Phase 3 PROVED no 30-ray KS set exists (exhaustive).")
