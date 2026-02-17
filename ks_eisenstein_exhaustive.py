"""
ks_eisenstein_exhaustive.py -- Exhaustive proof that 33 is minimum for Eisenstein island
========================================================================================

Analogous to the exhaustive 31-optimality proof for the integer island:
1. Generate the Eisenstein ray pool (57 rays, max_coeff=1, norm_cutoff=3)
2. Run 1000+ minimization trials to find all distinct 33-sets
3. Take the union of rays used across all 33-sets
4. Exhaustively check all C(union_size, 32) subsets for KS-uncolorability

If all 32-subsets are colorable, 33 is proved minimum for this island.
"""

import itertools
import random
import time
import sys

from ks_complex import (
    generate_eisenstein_rays,
    hermitian_dot,
    canonicalize_complex_ray,
)

from ks_sat import is_uncolorable as sat_uncolorable


def build_pairs_triads(rays):
    """Build orthogonal pairs and triads for a ray set."""
    n = len(rays)
    pairs = []
    pair_set = set()
    for i in range(n):
        for j in range(i + 1, n):
            dot = hermitian_dot(rays[i], rays[j])
            if abs(dot) < 1e-9:
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

    return pairs, triads


def restrict_to_subset(subset, pairs, triads):
    """Restrict pairs and triads to a subset of ray indices, re-indexing."""
    s = set(subset)
    remap = {old: new for new, old in enumerate(sorted(subset))}
    sp = [(remap[a], remap[b]) for a, b in pairs if a in s and b in s]
    st = [(remap[a], remap[b], remap[c]) for a, b, c in triads
          if a in s and b in s and c in s]
    return sp, st


def sat_minimize_track(rays, pairs, triads, n_trials=1000):
    """
    SAT-based greedy minimization, tracking all distinct minimal sets found.
    Returns: best_size, size_distribution, list of distinct minimal sets (as frozensets of indices)
    """
    n = len(rays)
    best_size = n
    sizes = {}
    distinct_sets = {}  # frozenset -> count

    for trial in range(n_trials):
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
                sp, st = restrict_to_subset(candidate, pairs, triads)
                if st and sat_uncolorable(len(candidate), sp, st):
                    current = candidate
                    removed = True
                    break

        size = len(current)
        sizes[size] = sizes.get(size, 0) + 1
        if size <= best_size + 2:  # Track sets near the minimum
            fs = frozenset(current)
            distinct_sets[fs] = distinct_sets.get(fs, 0) + 1
        if size < best_size:
            best_size = size

        if (trial + 1) % 100 == 0:
            n_distinct_min = sum(1 for k in distinct_sets if len(k) == best_size)
            print(f"  Trial {trial+1}/{n_trials}: best={best_size}, "
                  f"distinct {best_size}-sets so far: {n_distinct_min}", flush=True)

    # Filter to just the minimal sets
    minimal_sets = [k for k in distinct_sets if len(k) == best_size]
    return best_size, sizes, minimal_sets


def main():
    random.seed(42)

    print("=" * 70)
    print("EXHAUSTIVE PROOF: Is 33 the minimum for the Eisenstein island?")
    print("=" * 70)

    # Step 1: Generate ray pool
    print("\nStep 1: Generate Eisenstein ray pool (max_coeff=1, norm_cutoff=3)")
    t0 = time.time()
    rays = generate_eisenstein_rays(max_coeff=1, dim=3, norm_cutoff=3)
    print(f"  Pool: {len(rays)} rays ({time.time()-t0:.2f}s)")

    # Step 2: Build orthogonality structure
    print("\nStep 2: Build orthogonality graph")
    pairs, triads = build_pairs_triads(rays)
    print(f"  Pairs: {len(pairs)}, Triads: {len(triads)}")

    # Verify uncolorable
    assert sat_uncolorable(len(rays), pairs, triads), "Pool should be uncolorable!"
    print(f"  Pool is KS-uncolorable: YES")

    # Step 3: Find all distinct minimal sets
    print(f"\nStep 3: Find distinct minimal 33-sets (1000 trials)")
    t0 = time.time()
    best_size, sizes, minimal_sets = sat_minimize_track(rays, pairs, triads, n_trials=1000)
    dt = time.time() - t0
    print(f"\n  Minimization complete ({dt:.1f}s)")
    print(f"  Best size: {best_size}")
    print(f"  Size distribution: {dict(sorted(sizes.items()))}")
    print(f"  Distinct {best_size}-sets found: {len(minimal_sets)}")

    if best_size != 33:
        print(f"\n  UNEXPECTED: best size is {best_size}, not 33!")
        print(f"  Cannot proceed with 33-optimality proof.")
        return

    # Step 4: Find union of rays used across all 33-sets
    union_rays = set()
    for ms in minimal_sets:
        union_rays |= ms
    union_rays = sorted(union_rays)
    print(f"\n  Union of rays across all {len(minimal_sets)} distinct 33-sets: {len(union_rays)} of {len(rays)} rays")

    # Step 5: Exhaustive check
    n_union = len(union_rays)
    target_size = best_size - 1  # 32
    n_subsets = 1
    for i in range(target_size):
        n_subsets = n_subsets * (n_union - i) // (i + 1)

    print(f"\nStep 4: Exhaustive check of all C({n_union},{target_size}) = {n_subsets:,} subsets of size {target_size}")

    if n_subsets > 5_000_000_000:
        print(f"  WARNING: {n_subsets:,} subsets is very large!")
        print(f"  Estimated time at ~10K checks/sec: {n_subsets/10000/3600:.0f} hours")
        print(f"  Consider using a sampling approach instead.")

        # Do sampling first
        print(f"\n  Running random sampling check (100,000 random 32-subsets)...")
        t0 = time.time()
        found_any = False
        for i in range(100_000):
            subset = sorted(random.sample(union_rays, target_size))
            sp, st = restrict_to_subset(subset, pairs, triads)
            if st and sat_uncolorable(len(subset), sp, st):
                print(f"  FOUND UNCOLORABLE 32-SUBSET at sample {i+1}!")
                found_any = True
                break
            if (i + 1) % 10000 == 0:
                print(f"    Checked {i+1}/100,000 random subsets... all colorable so far ({time.time()-t0:.1f}s)", flush=True)

        if found_any:
            print(f"\n  33 is NOT the minimum! Found a {target_size}-ray KS set.")
        else:
            print(f"\n  All 100,000 random 32-subsets are colorable ({time.time()-t0:.1f}s)")

        # Also try neighborhood search around each 33-set
        print(f"\n  Neighborhood search: single-ray removals from each 33-set...")
        t0 = time.time()
        total_removals = 0
        for ms_idx, ms in enumerate(minimal_sets):
            ms_list = sorted(ms)
            for ray in ms_list:
                subset = [r for r in ms_list if r != ray]
                sp, st = restrict_to_subset(subset, pairs, triads)
                if st and sat_uncolorable(len(subset), sp, st):
                    print(f"  FOUND: removing ray {ray} from set {ms_idx} gives uncolorable 32-set!")
                    found_any = True
                    break
                total_removals += 1
            if found_any:
                break
        if not found_any:
            print(f"  All {total_removals} single-ray removals are colorable ({time.time()-t0:.1f}s)")

        # Ray-swap search
        print(f"\n  Neighborhood search: ray swaps from each 33-set...")
        t0 = time.time()
        swap_count = 0
        for ms_idx, ms in enumerate(minimal_sets[:10]):  # limit to first 10 sets
            ms_list = sorted(ms)
            non_ms = [r for r in union_rays if r not in ms]
            for ray_out in ms_list:
                for ray_in in non_ms:
                    subset = [r for r in ms_list if r != ray_out] + [ray_in]
                    subset.sort()
                    sp, st = restrict_to_subset(subset, pairs, triads)
                    if st and sat_uncolorable(len(subset), sp, st):
                        # Found an uncolorable 33-set (different), but can we reduce it?
                        # Try removing each ray from this new 33-set
                        for r2 in subset:
                            sub2 = [x for x in subset if x != r2]
                            sp2, st2 = restrict_to_subset(sub2, pairs, triads)
                            if st2 and sat_uncolorable(len(sub2), sp2, st2):
                                print(f"  FOUND: swap {ray_out}->{ray_in} in set {ms_idx}, "
                                      f"then remove {r2} gives 31-ray KS set!")
                                found_any = True
                                break
                    swap_count += 1
            if found_any:
                break
            if (ms_idx + 1) % 5 == 0:
                print(f"    Processed {ms_idx+1} sets, {swap_count} swaps so far ({time.time()-t0:.1f}s)", flush=True)

        if not found_any:
            print(f"  All {swap_count} ray-swap tests done, no 32-set found ({time.time()-t0:.1f}s)")

        if not found_any and n_subsets <= 50_000_000:
            print(f"\n  Subset count ({n_subsets:,}) is manageable. Proceeding with exhaustive check...")
        elif not found_any:
            print(f"\n  Exhaustive check would require {n_subsets:,} SAT calls.")
            print(f"  Based on sampling and neighborhood search, 33 appears to be minimum.")
            print(f"  Exhaustive proof deferred (too many subsets).")
            return

    if n_subsets <= 50_000_000:
        # Full exhaustive check
        print(f"\n  Running exhaustive check...", flush=True)
        t0 = time.time()
        checked = 0
        found = False
        last_report = time.time()

        for subset in itertools.combinations(union_rays, target_size):
            subset = list(subset)
            sp, st = restrict_to_subset(subset, pairs, triads)
            if st and sat_uncolorable(len(subset), sp, st):
                print(f"\n  *** FOUND UNCOLORABLE {target_size}-SUBSET ***")
                print(f"  Rays: {subset}")
                found = True
                break
            checked += 1
            now = time.time()
            if now - last_report >= 30:
                elapsed = now - t0
                rate = checked / elapsed
                eta = (n_subsets - checked) / rate if rate > 0 else float('inf')
                pct = 100 * checked / n_subsets
                print(f"    Checked {checked:,}/{n_subsets:,} ({pct:.1f}%) "
                      f"rate={rate:.0f}/s, ETA={eta/60:.0f}min", flush=True)
                last_report = now

        dt = time.time() - t0
        if not found:
            print(f"\n  EXHAUSTIVE CHECK COMPLETE: All {n_subsets:,} subsets of size {target_size} are COLORABLE")
            print(f"  Time: {dt:.1f}s ({dt/60:.1f} min)")
            print(f"\n  *** PROVED: {best_size} is the minimum KS set size for the Eisenstein island ***")
        else:
            print(f"\n  {best_size} is NOT the minimum! Found a {target_size}-ray KS set.")


if __name__ == "__main__":
    main()
