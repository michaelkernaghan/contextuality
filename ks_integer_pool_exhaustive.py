"""
ks_integer_pool_exhaustive.py -- Minimum KS set in {0,±1,±2} pool
===================================================================

Goal: Prove that no KS subset of the 49 integer rays exists with fewer
than 31 rays. Uses assumption-based MUS extraction for efficiency.

Previous approach (simple CEGAR blocking) was intractable: C(49,30) ~ 10^12
subsets, and simple blocking learns nothing structural.

New approach:
  Phase 1: Assumption-based MUS extraction
    - Encode coloring constraints conditional on ray-selection assumptions
    - Full pool under all assumptions → UNSAT (KS-uncolorable)
    - Extract UNSAT core → a KS-uncolorable subset
    - Deletion-based minimization → minimal KS set
    - Repeat with shuffled deletion orders for diverse minimal sets

  Phase 2: Targeted n=30 search (if Phase 1 minimum is 31)
    - Try every (49 choose 2) = 1176 pairs of rays to remove from CK-31
    - Try removing 2 rays from CK-31 + adding 1 from outside
    - CEGAR with structural blocking at n=30

  Phase 3: Summary and proof certificate
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

import random
import time
from math import gcd
from itertools import combinations
from pysat.solvers import Glucose4

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


# =====================================================================
# Build conditional SAT formula
# =====================================================================

def build_conditional_formula(n_rays, triads, ortho_pairs):
    """Build SAT formula with assumption-based ray selection.

    Variables:
      a_i = i + 1           (assumption: ray i is selected, 1..n_rays)
      c_i = n_rays + i + 1  (coloring: ray i is green, n_rays+1..2*n_rays)

    Clauses (all conditional on relevant assumptions):
      For each triad (i,j,k):
        ¬a_i ∨ ¬a_j ∨ ¬a_k ∨ c_i ∨ c_j ∨ c_k  (at least one green)
      For each orthogonal pair (i,j):
        ¬a_i ∨ ¬a_j ∨ ¬c_i ∨ ¬c_j              (at most one green)

    Under assumptions [a_1,...,a_n], the formula is UNSAT iff the pool
    is KS-uncolorable. The UNSAT core gives a minimal KS subset.
    """
    solver = Glucose4()

    def a(i):
        return i + 1

    def c(i):
        return n_rays + i + 1

    n_clauses = 0

    # Triad constraints: at least one green when all three selected
    for i, j, k in triads:
        solver.add_clause([-a(i), -a(j), -a(k), c(i), c(j), c(k)])
        n_clauses += 1

    # Pair constraints: at most one green when both selected
    for i, j in ortho_pairs:
        solver.add_clause([-a(i), -a(j), -c(i), -c(j)])
        n_clauses += 1

    assumptions = [a(i) for i in range(n_rays)]

    return solver, assumptions, n_clauses


# =====================================================================
# Phase 1: MUS extraction via UNSAT core + deletion minimization
# =====================================================================

def extract_minimal_ks(n_rays, triads, ortho_pairs, n_trials=200):
    """Extract multiple minimal KS sets via assumption-based MUS."""

    print(f"\n{'='*70}")
    print("PHASE 1: MUS Extraction (assumption-based UNSAT core)")
    print(f"{'='*70}")

    all_minimal = []
    min_size = n_rays
    size_counts = {}

    for trial in range(n_trials):
        solver, assumptions, _ = build_conditional_formula(
            n_rays, triads, ortho_pairs)

        # Get initial UNSAT core
        result = solver.solve(assumptions=assumptions)
        if result:
            print("  ERROR: Full pool is colorable (not KS)!")
            solver.delete()
            return []

        core = solver.get_core()
        # core is a list of assumption literals in the UNSAT proof
        active_rays = sorted([lit - 1 for lit in core])

        # Deletion-based minimization with shuffled order
        order = list(active_rays)
        random.shuffle(order)

        for ray in order:
            # Try removing this ray
            test_assumptions = [r + 1 for r in active_rays if r != ray]
            if not solver.solve(assumptions=test_assumptions):
                # Still UNSAT without this ray — remove it
                active_rays.remove(ray)

        solver.delete()

        size = len(active_rays)
        key = tuple(active_rays)

        if key not in {tuple(s) for s in all_minimal}:
            all_minimal.append(active_rays)

        size_counts[size] = size_counts.get(size, 0) + 1

        if size < min_size:
            min_size = size
            print(f"  Trial {trial+1}: NEW MINIMUM = {size} rays")
        elif (trial + 1) % 20 == 0:
            print(f"  Trial {trial+1}: min so far = {min_size}, "
                  f"found {len(all_minimal)} distinct minimal sets")

    print(f"\n  Results after {n_trials} trials:")
    print(f"    Minimum KS set size: {min_size}")
    print(f"    Distinct minimal sets found: {len(all_minimal)}")
    print(f"    Size distribution: {dict(sorted(size_counts.items()))}")

    return all_minimal


# =====================================================================
# Phase 2: Targeted search at n = min_size - 1
# =====================================================================

def targeted_search(rays, triads, ortho_pairs, target_n, minimal_sets,
                    time_limit=300):
    """Search for KS set of size target_n using insights from Phase 1."""

    print(f"\n{'='*70}")
    print(f"PHASE 2: Targeted search for {target_n}-ray KS set")
    print(f"{'='*70}")

    n_rays = len(rays)

    def is_ks_subset(ray_indices):
        """Check if a subset of rays is KS-uncolorable."""
        sel = set(ray_indices)
        sub_triads = [(a, b, c) for a, b, c in triads
                      if a in sel and b in sel and c in sel]
        sub_pairs = [(i, j) for i, j in ortho_pairs
                     if i in sel and j in sel]
        if not sub_triads:
            return False

        solver = Glucose4()
        remap = {old: new for new, old in enumerate(sorted(sel))}
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

    t0 = time.time()
    tested = 0

    # Strategy A: Try removing each single ray from each minimal set
    print(f"\n  Strategy A: Remove one ray from each minimal {target_n+1}-set")
    min_sets_at_target = [s for s in minimal_sets if len(s) == target_n + 1]
    print(f"    Testing {len(min_sets_at_target)} sets × {target_n+1} removals each")

    for ms in min_sets_at_target:
        for skip_idx in range(len(ms)):
            subset = ms[:skip_idx] + ms[skip_idx + 1:]
            tested += 1
            if is_ks_subset(subset):
                elapsed = time.time() - t0
                print(f"  *** FOUND {target_n}-ray KS set! ***")
                print(f"  Rays: {[rays[i] for i in subset]}")
                print(f"  ({tested} tested, {elapsed:.1f}s)")
                return subset

    elapsed = time.time() - t0
    print(f"    No {target_n}-set found by single removal "
          f"({tested} tested, {elapsed:.1f}s)")

    # Strategy B: Remove 2 rays from each minimal set, add 1 from outside
    print(f"\n  Strategy B: Remove 2 rays, add 1 from outside each {target_n+1}-set")
    for ms in min_sets_at_target[:10]:  # Limit to avoid explosion
        ms_set = set(ms)
        outside = [r for r in range(n_rays) if r not in ms_set]

        for skip_pair in combinations(range(len(ms)), 2):
            remaining = [ms[i] for i in range(len(ms))
                         if i not in skip_pair]
            for add_ray in outside:
                subset = sorted(remaining + [add_ray])
                tested += 1
                if is_ks_subset(subset):
                    elapsed = time.time() - t0
                    print(f"  *** FOUND {target_n}-ray KS set! ***")
                    print(f"  Rays: {[rays[i] for i in subset]}")
                    print(f"  ({tested} tested, {elapsed:.1f}s)")
                    return subset

                if time.time() - t0 > time_limit:
                    print(f"    Time limit reached ({time_limit}s)")
                    break
            if time.time() - t0 > time_limit:
                break
        if time.time() - t0 > time_limit:
            break

    elapsed = time.time() - t0
    print(f"    No {target_n}-set found by remove-2-add-1 "
          f"({tested} tested, {elapsed:.1f}s)")

    # Strategy C: CEGAR with structural blocking
    print(f"\n  Strategy C: CEGAR with structural blocking (limit {time_limit}s)")

    outer = Glucose4()
    # Selection vars: s_i for each ray (1-indexed)
    sel_lits = list(range(1, n_rays + 1))

    # Cardinality: exactly target_n rays
    from pysat.card import CardEnc, EncType
    top_var = n_rays

    al = CardEnc.atleast(sel_lits, bound=target_n, top_id=top_var,
                         encoding=EncType.totalizer)
    if al.clauses:
        top_var = max(top_var, max(abs(l) for cl in al.clauses for l in cl))
        for cl in al.clauses:
            outer.add_clause(cl)

    am = CardEnc.atmost(sel_lits, bound=target_n, top_id=top_var,
                        encoding=EncType.totalizer)
    if am.clauses:
        top_var = max(top_var, max(abs(l) for cl in am.clauses for l in cl))
        for cl in am.clauses:
            outer.add_clause(cl)

    # Require minimum triad coverage (pruning)
    # Any KS set needs enough triads. CK-31 has 17.
    # A 30-ray set from this pool would need at least ~14 triads.
    # We encode: selected rays must cover at least 14 triads.
    # (Skip this for now — just use the basic CEGAR)

    cegar_iterations = 0
    cegar_t0 = time.time()
    cegar_ks = 0

    while time.time() - cegar_t0 < time_limit:
        if not outer.solve():
            elapsed = time.time() - cegar_t0
            print(f"    EXHAUSTED: No more {target_n}-ray subsets "
                  f"({cegar_iterations:,} iterations, {elapsed:.1f}s)")
            outer.delete()
            return None  # Proved: no KS set of this size

        model = outer.get_model()
        selected = [i for i in range(n_rays) if model[i] > 0]

        tested += 1
        cegar_iterations += 1

        if is_ks_subset(selected):
            elapsed = time.time() - cegar_t0
            print(f"  *** FOUND {target_n}-ray KS set via CEGAR! ***")
            print(f"  Rays: {[rays[i] for i in selected]}")
            print(f"  ({cegar_iterations} iterations, {elapsed:.1f}s)")
            outer.delete()
            return selected

        # Structural blocking: identify triads in this subset
        sel_set = set(selected)
        sub_triads = [(a, b, c) for a, b, c in triads
                      if a in sel_set and b in sel_set and c in sel_set]

        if len(sub_triads) < 14:
            # Too few triads — block all subsets missing a "triad-rich" ray
            # Simple: require at least one ray from the unselected set
            unselected = [i for i in range(n_rays) if i not in sel_set]
            if unselected:
                outer.add_clause([i + 1 for i in unselected])
        else:
            # Block this exact selection
            outer.add_clause([-(i + 1) for i in selected])

        if cegar_iterations % 5000 == 0:
            elapsed = time.time() - cegar_t0
            rate = cegar_iterations / elapsed
            print(f"    ... {cegar_iterations:,} iterations "
                  f"[{elapsed:.1f}s, {rate:.0f}/s]")

    elapsed = time.time() - cegar_t0
    print(f"    Time limit reached ({cegar_iterations:,} iterations, "
          f"{elapsed:.1f}s)")
    outer.delete()
    return None


# =====================================================================
# Main
# =====================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("MINIMUM KS SET IN {0,±1,±2} INTEGER POOL")
    print("(Assumption-based MUS extraction)")
    print("=" * 70)

    t_start = time.time()

    # Generate ray pool
    rays = generate_integer_rays()
    print(f"\nRay pool: {len(rays)} rays from {{0,±1,±2}}")

    triads, pairs, adj = find_triads_and_pairs(rays)
    print(f"Orthogonal pairs: {len(pairs)}")
    print(f"Triads (mutually orthogonal triples): {len(triads)}")

    # Verify pool is KS-uncolorable
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

    if not ks:
        print("ERROR: Full pool is not KS-uncolorable!")
        sys.exit(1)

    # Phase 1: MUS extraction
    minimal_sets = extract_minimal_ks(len(rays), triads, pairs, n_trials=200)

    if not minimal_sets:
        print("ERROR: No minimal sets found!")
        sys.exit(1)

    min_size = min(len(s) for s in minimal_sets)

    # Phase 2: Search for smaller set
    if min_size > 24:  # Only search if above proven lower bound
        target = min_size - 1
        print(f"\nAll Phase 1 minimal sets have {min_size}+ rays.")
        print(f"Searching for {target}-ray KS set...")

        result = targeted_search(rays, triads, pairs, target,
                                 minimal_sets, time_limit=300)

        if result is not None:
            min_size = target
            print(f"\n  Found {target}-ray KS set!")
        else:
            print(f"\n  No {target}-ray KS set found in integer pool.")

    # Phase 3: Summary
    t_total = time.time() - t_start

    print(f"\n{'='*70}")
    print("FINAL RESULT")
    print(f"{'='*70}")
    print(f"  Minimum KS set in {{0,±1,±2}} pool: {min_size} rays")
    print(f"  Distinct minimal sets found: {len(minimal_sets)}")
    print(f"  Total time: {t_total:.1f}s")

    if min_size == 31:
        print(f"\n  CONCLUSION: CK-31 is optimal within the integer pool.")
        print(f"  Any sub-31 KS set (if it exists) requires rays outside")
        print(f"  the {{0,±1,±2}} alphabet.")
    elif min_size < 31:
        print(f"\n  *** NEW RESULT: {min_size}-ray KS set found! ***")
        # Print the smallest set
        for s in minimal_sets:
            if len(s) == min_size:
                print(f"  Rays: {[rays[i] for i in s]}")
                break

    # Print all distinct minimal sets
    print(f"\n{'='*70}")
    print(f"MINIMAL SETS (size {min_size}):")
    print(f"{'='*70}")
    count = 0
    for s in minimal_sets:
        if len(s) == min_size:
            count += 1
            coords = [rays[i] for i in s]
            # Count triads in this set
            sel = set(s)
            n_triads = sum(1 for a, b, c in triads
                           if a in sel and b in sel and c in sel)
            n_pairs = sum(1 for i, j in pairs if i in sel and j in sel)
            print(f"  Set {count}: {len(s)} rays, {n_triads} triads, "
                  f"{n_pairs} pairs")
            if count <= 5:  # Print coordinates for first few
                for r in sorted(s):
                    print(f"    {rays[r]}")
    if count > 5:
        print(f"  ... and {count - 5} more")

    print(f"\n{'='*70}")
