"""
ks_criticality_extended.py -- Extended k-criticality of CK-31
==============================================================

CK-31 is known to be 3-critical: removing any 1, 2, or 3 rays
makes it colorable. This script extends to k=4,5,6,...,~10.

k-criticality means: removing ANY k rays makes the set colorable.
- k=4: C(31,4) = 31,465 subsets  (exhaustive feasible)
- k=5: C(31,5) = 169,911         (exhaustive feasible)
- k=6: C(31,6) = 736,281         (exhaustive feasible)
- k=7: C(31,7) = 2,629,575       (feasible, each SAT call ~microseconds)
- k=8+: C(31,8) = 7,888,725      (may need sampling)

Each SAT call takes microseconds, so even millions of tests are feasible.
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

import time
from itertools import combinations
from pysat.solvers import Glucose4


# =====================================================================
# CK-31 (canonical ordering from ks_sub31_search.py)
# =====================================================================

CK31_INT = [
    (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 1, -1), (0, 1, 2), (0, 2, -1),
    (1, 0, 0), (1, 0, 1), (1, 0, -1), (1, 0, 2), (1, 0, -2),
    (1, 1, 0), (1, 1, 1), (1, 1, -1), (1, 1, 2), (1, -1, 0),
    (1, -1, 1), (1, -1, -1), (1, -1, -2), (1, 2, 0), (1, 2, -1),
    (1, -2, 0), (1, -2, 1), (2, 0, 1), (2, 0, -1), (2, 1, 0),
    (2, 1, 1), (2, 1, -1), (2, -1, 0), (2, -1, 1), (2, -1, -1)
]


def dot_int(a, b):
    return sum(x * y for x, y in zip(a, b))


def find_triads_and_pairs():
    n = len(CK31_INT)
    ortho_pairs = []
    adj = {i: set() for i in range(n)}

    for i in range(n):
        for j in range(i + 1, n):
            if dot_int(CK31_INT[i], CK31_INT[j]) == 0:
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

    return triads, ortho_pairs


def is_ks_uncolorable(n_vertices, triads, ortho_pairs):
    """SAT-based KS-uncolorability check using Glucose4."""
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


# =====================================================================
# Main: Extended criticality test
# =====================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("EXTENDED k-CRITICALITY OF CK-31")
    print("=" * 70)

    ck31_triads, ck31_pairs = find_triads_and_pairs()
    n = len(CK31_INT)
    print(f"\nCK-31: {n} rays, {len(ck31_pairs)} pairs, {len(ck31_triads)} triads")

    # Verify base
    assert is_ks_uncolorable(n, ck31_triads, ck31_pairs), "CK-31 verification failed!"
    print("CK-31 verified KS-uncolorable.")

    # Test k-criticality for increasing k
    MAX_EXHAUSTIVE = 10_000_000  # max combos for exhaustive search
    max_k = 12  # try up to this

    for k in range(1, max_k + 1):
        n_remaining = n - k

        # Compute C(31, k)
        total = 1
        for i in range(k):
            total = total * (n - i) // (i + 1)

        print(f"\n{'='*70}")
        print(f"k = {k}: Remove {k} rays ({n_remaining} remain), "
              f"C(31,{k}) = {total:,} subsets")
        print(f"{'='*70}")

        if total > MAX_EXHAUSTIVE:
            print(f"  Too many combinations for exhaustive search.")
            print(f"  Switching to sampling (1,000,000 random subsets)...")

            import random
            random.seed(42 + k)

            n_tested = 0
            n_still_ks = 0
            sample_size = 1_000_000

            t0 = time.time()
            for trial in range(sample_size):
                remove = set(random.sample(range(n), k))
                keep = [i for i in range(n) if i not in remove]
                keep_set = set(keep)
                remap = {old: new for new, old in enumerate(keep)}

                sub_triads = [(remap[a], remap[b], remap[c])
                              for a, b, c in ck31_triads
                              if a in keep_set and b in keep_set and c in keep_set]
                sub_pairs = [(remap[i], remap[j])
                             for i, j in ck31_pairs
                             if i in keep_set and j in keep_set]

                if is_ks_uncolorable(n_remaining, sub_triads, sub_pairs):
                    n_still_ks += 1
                    removed_coords = [CK31_INT[r] for r in sorted(remove)]
                    print(f"  *** STILL KS with {n_remaining} rays! "
                          f"Removed: {removed_coords}")
                    break

                n_tested += 1
                if n_tested % 200000 == 0:
                    elapsed = time.time() - t0
                    rate = n_tested / elapsed
                    print(f"    ... {n_tested:,}/{sample_size:,} "
                          f"[{elapsed:.1f}s, {rate:.0f}/s]")

            elapsed = time.time() - t0
            if n_still_ks == 0:
                print(f"  {k}-CRITICAL (sampled): All {n_tested:,} tested subsets "
                      f"are colorable [{elapsed:.1f}s]")
            else:
                print(f"  NOT {k}-critical: found subset still KS-uncolorable")
                print(f"  CK-31 is (k-1)={k-1}-critical but not {k}-critical.")
                break
        else:
            # Exhaustive
            n_tested = 0
            n_still_ks = 0

            t0 = time.time()
            for remove in combinations(range(n), k):
                remove_set = set(remove)
                keep = [i for i in range(n) if i not in remove_set]
                keep_set = set(keep)
                remap = {old: new for new, old in enumerate(keep)}

                sub_triads = [(remap[a], remap[b], remap[c])
                              for a, b, c in ck31_triads
                              if a in keep_set and b in keep_set and c in keep_set]
                sub_pairs = [(remap[i], remap[j])
                             for i, j in ck31_pairs
                             if i in keep_set and j in keep_set]

                if is_ks_uncolorable(n_remaining, sub_triads, sub_pairs):
                    n_still_ks += 1
                    removed_coords = [CK31_INT[r] for r in remove]
                    print(f"  *** STILL KS with {n_remaining} rays! "
                          f"Removed: {removed_coords}")
                    break

                n_tested += 1
                if n_tested % 50000 == 0:
                    elapsed = time.time() - t0
                    rate = n_tested / elapsed
                    print(f"    ... {n_tested:,}/{total:,} "
                          f"[{elapsed:.1f}s, {rate:.0f}/s]")

            elapsed = time.time() - t0

            if n_still_ks == 0:
                print(f"  {k}-CRITICAL (exhaustive): All {total:,} subsets "
                      f"are colorable [{elapsed:.1f}s]")
            else:
                print(f"  NOT {k}-critical: found subset still KS-uncolorable")
                print(f"  CK-31 is (k-1)={k-1}-critical but not {k}-critical.")
                break

    # Summary
    print(f"\n{'='*70}")
    print("CRITICALITY SUMMARY")
    print(f"{'='*70}")
    print(f"  CK-31 criticality results will appear above.")
    print(f"  If k-critical for all tested k, CK-31 is 'deeply critical' --")
    print(f"  every ray participates in an essential, non-redundant way")
    print(f"  in the KS-uncolorability proof.")
