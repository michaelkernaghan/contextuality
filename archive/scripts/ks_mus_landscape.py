"""
ks_mus_landscape.py -- Map the landscape of minimal 31-sets in the integer pool
=================================================================================

The integer pool has 49 rays and the OCUS-certified minimum KS set is 31 rays.
Previous runs found 162 distinct minimal 31-sets in 1000 MUS trials.

This script:
  1. Extracts 5000 MUS trials to discover as many distinct 31-sets as possible
  2. Analyzes ray frequency: which rays are "core" (in all/most sets) vs "peripheral"
  3. Computes pairwise overlap (Jaccard similarity) between all distinct 31-sets
  4. Identifies cluster structure: do minimal sets form families?
  5. Builds a swap-distance graph: can you walk between any two 31-sets by
     swapping one ray at a time (always staying KS-uncolorable)?
  6. Identifies the "essential core" — rays present in ALL minimal 31-sets
"""

import sys
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

import random
import time
from math import gcd
from itertools import combinations
from collections import Counter

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
    pairs = []
    adj = {i: set() for i in range(n)}
    for i in range(n):
        for j in range(i + 1, n):
            if dot_int(coords[i], coords[j]) == 0:
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
    return triads, pairs, adj


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
# Phase 1: Massive MUS extraction
# =====================================================================

def extract_mus_sets(n_rays, triads, pairs, n_trials=5000):
    """Extract many MUSes, collecting all distinct size-31 sets."""
    print(f"\n{'='*70}")
    print(f"PHASE 1: MUS Extraction ({n_trials} trials)")
    print(f"{'='*70}")

    t0 = time.time()
    all_31 = set()
    size_counts = {}

    for trial in range(n_trials):
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
        result = solver.solve(assumptions=assumptions)
        if result:
            solver.delete()
            continue

        core = solver.get_core()
        active_rays = sorted([lit - 1 for lit in core])

        order = list(active_rays)
        random.shuffle(order)

        for ray in order:
            test_assumptions = [r + 1 for r in active_rays if r != ray]
            if not solver.solve(assumptions=test_assumptions):
                active_rays.remove(ray)

        solver.delete()

        size = len(active_rays)
        size_counts[size] = size_counts.get(size, 0) + 1

        if size == 31:
            key = tuple(sorted(active_rays))
            prev = len(all_31)
            all_31.add(key)
            if len(all_31) > prev and len(all_31) % 50 == 0:
                elapsed = time.time() - t0
                print(f"  Trial {trial+1}: {len(all_31)} distinct 31-sets "
                      f"[{elapsed:.1f}s]")

        if (trial + 1) % 1000 == 0:
            elapsed = time.time() - t0
            print(f"  Trial {trial+1}: {len(all_31)} distinct 31-sets, "
                  f"sizes={dict(sorted(size_counts.items()))} [{elapsed:.1f}s]")

    elapsed = time.time() - t0
    print(f"\n  Extraction complete ({elapsed:.1f}s):")
    print(f"    Distinct 31-sets: {len(all_31)}")
    print(f"    Size distribution: {dict(sorted(size_counts.items()))}")

    return list(all_31), size_counts


# =====================================================================
# Phase 2: Ray frequency analysis
# =====================================================================

def ray_frequency_analysis(rays, sets_31):
    """Which rays appear in how many of the minimal 31-sets?"""
    print(f"\n{'='*70}")
    print("PHASE 2: Ray Frequency Analysis")
    print(f"{'='*70}")

    n_sets = len(sets_31)
    freq = Counter()
    for s in sets_31:
        for r in s:
            freq[r] += 1

    # Sort by frequency
    by_freq = sorted(freq.items(), key=lambda x: -x[1])

    print(f"\n  {'Ray':<15} {'Coord':<15} {'||v||^2':>7} {'Freq':>6} "
          f"{'%':>7}")
    print("  " + "-" * 55)

    core_rays = []  # in ALL sets
    near_core = []  # in > 90% of sets
    peripheral = []  # in < 50% of sets
    absent = []  # in 0 sets

    for idx, count in by_freq:
        v = rays[idx]
        norm_sq = sum(x * x for x in v)
        pct = 100 * count / n_sets
        print(f"  {idx:<15} {str(v):<15} {norm_sq:>7} {count:>6} "
              f"{pct:>6.1f}%")
        if count == n_sets:
            core_rays.append(idx)
        elif count > 0.9 * n_sets:
            near_core.append(idx)
        elif count < 0.5 * n_sets:
            peripheral.append(idx)

    # Check for rays never used
    for i in range(len(rays)):
        if i not in freq:
            absent.append(i)
            v = rays[i]
            norm_sq = sum(x * x for x in v)
            print(f"  {i:<15} {str(v):<15} {norm_sq:>7} {'0':>6} "
                  f"{'0.0':>7}%")

    print(f"\n  Summary:")
    print(f"    Core rays (in ALL {n_sets} sets): {len(core_rays)}")
    print(f"    Near-core (>90%): {len(near_core)}")
    print(f"    Peripheral (<50%): {len(peripheral)}")
    print(f"    Never used: {len(absent)}")
    print(f"    Total rays used: {len(freq)}")
    print(f"    Pool size: {len(rays)}")

    if core_rays:
        print(f"\n  Core rays (invariant across ALL minimal 31-sets):")
        for idx in core_rays:
            print(f"    {rays[idx]}")

    if absent:
        print(f"\n  Never-used rays:")
        for idx in absent:
            v = rays[idx]
            norm_sq = sum(x * x for x in v)
            print(f"    {v}  (||v||^2 = {norm_sq})")

    return freq, core_rays, absent


# =====================================================================
# Phase 3: Pairwise overlap and clustering
# =====================================================================

def overlap_analysis(sets_31):
    """Compute pairwise overlap between all distinct 31-sets."""
    print(f"\n{'='*70}")
    print("PHASE 3: Pairwise Overlap Analysis")
    print(f"{'='*70}")

    n = len(sets_31)
    sets_as_sets = [set(s) for s in sets_31]

    # Compute all pairwise overlaps
    overlaps = []
    for i in range(n):
        for j in range(i + 1, n):
            common = len(sets_as_sets[i] & sets_as_sets[j])
            overlaps.append((i, j, common))

    # Distribution of overlap sizes
    overlap_dist = Counter(o[2] for o in overlaps)

    print(f"\n  Pairwise overlap distribution (out of 31 rays):")
    for size in sorted(overlap_dist.keys()):
        count = overlap_dist[size]
        pct = 100 * count / len(overlaps)
        bar = '#' * max(1, int(pct / 2))
        print(f"    {size:>3} shared: {count:>6} pairs ({pct:>5.1f}%) {bar}")

    min_overlap = min(o[2] for o in overlaps)
    max_overlap = max(o[2] for o in overlaps)
    avg_overlap = sum(o[2] for o in overlaps) / len(overlaps)
    print(f"\n  Min overlap: {min_overlap}/31")
    print(f"  Max overlap: {max_overlap}/31")
    print(f"  Mean overlap: {avg_overlap:.1f}/31")

    # Jaccard similarity
    jaccards = [(i, j, common / (62 - common))
                for i, j, common in overlaps]
    avg_jaccard = sum(j[2] for j in jaccards) / len(jaccards)
    print(f"  Mean Jaccard: {avg_jaccard:.3f}")

    # Find the most distant pair
    min_pair = min(overlaps, key=lambda x: x[2])
    print(f"\n  Most distant pair: sets {min_pair[0]} and {min_pair[1]} "
          f"share {min_pair[2]}/31 rays")

    # Find the most similar pair (not identical)
    max_pair = max(overlaps, key=lambda x: x[2])
    print(f"  Most similar pair: sets {max_pair[0]} and {max_pair[1]} "
          f"share {max_pair[2]}/31 rays")

    return overlaps, overlap_dist


# =====================================================================
# Phase 4: Swap connectivity
# =====================================================================

def swap_connectivity(sets_31, triads, pairs, rays):
    """Can you walk between any two 31-sets by swapping one ray at a time?"""
    print(f"\n{'='*70}")
    print("PHASE 4: Swap Connectivity")
    print(f"{'='*70}")
    print("  Question: Are all minimal 31-sets connected by single-ray swaps")
    print("  (removing one ray, adding another, staying KS-uncolorable)?")

    n = len(sets_31)
    sets_as_sets = [set(s) for s in sets_31]

    # Two sets are "swap-adjacent" if they differ in exactly 1 ray
    # (one has ray A where the other has ray B, all other 30 rays shared)
    swap_edges = []
    for i in range(n):
        for j in range(i + 1, n):
            diff_i = sets_as_sets[i] - sets_as_sets[j]
            diff_j = sets_as_sets[j] - sets_as_sets[i]
            if len(diff_i) == 1 and len(diff_j) == 1:
                swap_edges.append((i, j))

    print(f"\n  Swap-adjacent pairs (differ by exactly 1 ray): "
          f"{len(swap_edges)}")

    if not swap_edges:
        print("  No direct swap neighbors found!")
        # Try 2-swaps
        two_swap = 0
        for i in range(min(n, 100)):
            for j in range(i + 1, min(n, 100)):
                diff = len(sets_as_sets[i] - sets_as_sets[j])
                if diff == 2:
                    two_swap += 1
        print(f"  2-swap pairs (differ by exactly 2 rays): {two_swap} "
              f"(among first {min(n, 100)} sets)")

        # Check k-swap distribution
        print(f"\n  Swap distance distribution (first 100 pairs):")
        dist_counts = Counter()
        for i in range(min(n, 50)):
            for j in range(i + 1, min(n, 50)):
                diff = len(sets_as_sets[i] - sets_as_sets[j])
                dist_counts[diff] += 1

        for k in sorted(dist_counts.keys()):
            print(f"    {k}-swap: {dist_counts[k]} pairs")
    else:
        # Build adjacency and check connectivity via BFS
        adj = {i: set() for i in range(n)}
        for i, j in swap_edges:
            adj[i].add(j)
            adj[j].add(i)

        # BFS from node 0
        visited = {0}
        queue = [0]
        while queue:
            node = queue.pop(0)
            for nb in adj[node]:
                if nb not in visited:
                    visited.add(nb)
                    queue.append(nb)

        components = 1 if len(visited) == n else "multiple"
        print(f"  Connected components: {components}")
        if len(visited) < n:
            print(f"  Largest component: {len(visited)}/{n}")

        # Degree distribution
        degrees = [len(adj[i]) for i in range(n)]
        print(f"\n  Swap-neighbor degree distribution:")
        deg_counts = Counter(degrees)
        for d in sorted(deg_counts.keys()):
            print(f"    Degree {d}: {deg_counts[d]} sets")

    return swap_edges


# =====================================================================
# Phase 5: The CK-31 canonical set in context
# =====================================================================

def ck31_context(rays, sets_31, freq):
    """Where does the canonical CK-31 sit in the landscape?"""
    print(f"\n{'='*70}")
    print("PHASE 5: CK-31 in Context")
    print(f"{'='*70}")

    CK31_INT = [
        (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 1, -1), (0, 1, 2), (0, 2, -1),
        (1, 0, 0), (1, 0, 1), (1, 0, -1), (1, 0, 2), (1, 0, -2),
        (1, 1, 0), (1, 1, 1), (1, 1, -1), (1, 1, 2), (1, -1, 0),
        (1, -1, 1), (1, -1, -1), (1, -1, -2), (1, 2, 0), (1, 2, -1),
        (1, -2, 0), (1, -2, 1), (2, 0, 1), (2, 0, -1), (2, 1, 0),
        (2, 1, 1), (2, 1, -1), (2, -1, 0), (2, -1, 1), (2, -1, -1),
    ]

    ck31_indices = set()
    for v in CK31_INT:
        for i, r in enumerate(rays):
            if r == v:
                ck31_indices.add(i)
                break

    ck31_tuple = tuple(sorted(ck31_indices))

    # Is the canonical CK-31 among our discovered sets?
    found = ck31_tuple in [tuple(sorted(s)) for s in sets_31]
    print(f"\n  Canonical CK-31 in discovered set: {found}")

    # Overlap of CK-31 with each discovered set
    overlaps = []
    for i, s in enumerate(sets_31):
        common = len(ck31_indices & set(s))
        overlaps.append((i, common))

    overlap_dist = Counter(o[1] for o in overlaps)
    print(f"\n  CK-31 overlap with discovered 31-sets:")
    for size in sorted(overlap_dist.keys()):
        count = overlap_dist[size]
        print(f"    {size}/31 shared: {count} sets")

    max_ov = max(overlaps, key=lambda x: x[1])
    min_ov = min(overlaps, key=lambda x: x[1])
    avg_ov = sum(o[1] for o in overlaps) / len(overlaps)
    print(f"\n  Max overlap with CK-31: {max_ov[1]}/31 (set {max_ov[0]})")
    print(f"  Min overlap with CK-31: {min_ov[1]}/31 (set {min_ov[0]})")
    print(f"  Mean overlap with CK-31: {avg_ov:.1f}/31")

    # CK-31 ray frequency scores
    ck31_freq_scores = [freq.get(r, 0) for r in sorted(ck31_indices)]
    n_sets = len(sets_31)
    low_freq = [r for r in ck31_indices if freq.get(r, 0) < 0.5 * n_sets]
    high_freq = [r for r in ck31_indices if freq.get(r, 0) > 0.9 * n_sets]
    print(f"\n  CK-31 rays by landscape frequency:")
    print(f"    High-freq (>90% of all sets): {len(high_freq)}/31")
    print(f"    Low-freq (<50% of all sets): {len(low_freq)}/31")

    if low_freq:
        print(f"    Low-freq CK-31 rays:")
        for r in sorted(low_freq):
            print(f"      {rays[r]}  (in {freq[r]}/{n_sets} = "
                  f"{100*freq[r]/n_sets:.1f}% of sets)")

    return ck31_indices, overlaps


# =====================================================================
# Phase 6: Norm structure
# =====================================================================

def norm_analysis(rays, freq, sets_31):
    """Analyze ray frequency by norm class."""
    print(f"\n{'='*70}")
    print("PHASE 6: Norm Structure")
    print(f"{'='*70}")

    n_sets = len(sets_31)

    # Group rays by norm-squared
    norm_groups = {}
    for i, v in enumerate(rays):
        ns = sum(x * x for x in v)
        if ns not in norm_groups:
            norm_groups[ns] = []
        norm_groups[ns].append(i)

    print(f"\n  {'||v||^2':>7} {'Rays':>5} {'Avg freq':>10} {'Min':>5} "
          f"{'Max':>5} {'In all?':>8}")
    print("  " + "-" * 45)

    for ns in sorted(norm_groups.keys()):
        group = norm_groups[ns]
        freqs = [freq.get(r, 0) for r in group]
        avg_f = sum(freqs) / len(freqs)
        min_f = min(freqs)
        max_f = max(freqs)
        all_present = "Yes" if min_f == n_sets else "No"
        print(f"  {ns:>7} {len(group):>5} {avg_f:>10.1f} {min_f:>5} "
              f"{max_f:>5} {all_present:>8}")

    # Average norm-squared per set
    avg_norms = []
    for s in sets_31:
        norms = [sum(x * x for x in rays[r]) for r in s]
        avg_norms.append(sum(norms) / len(norms))

    print(f"\n  Average ||v||^2 across all 31-sets: "
          f"{sum(avg_norms)/len(avg_norms):.2f}")
    print(f"  Min avg norm: {min(avg_norms):.2f}")
    print(f"  Max avg norm: {max(avg_norms):.2f}")

    # How many norm-1 rays per set?
    norm1_counts = []
    for s in sets_31:
        n1 = sum(1 for r in s if sum(x*x for x in rays[r]) == 1)
        norm1_counts.append(n1)
    print(f"\n  Norm-1 rays per set: min={min(norm1_counts)}, "
          f"max={max(norm1_counts)}, mean={sum(norm1_counts)/len(norm1_counts):.1f}")

    norm2_counts = []
    for s in sets_31:
        n2 = sum(1 for r in s if sum(x*x for x in rays[r]) == 2)
        norm2_counts.append(n2)
    print(f"  Norm-2 rays per set: min={min(norm2_counts)}, "
          f"max={max(norm2_counts)}, mean={sum(norm2_counts)/len(norm2_counts):.1f}")

    return norm_groups


# =====================================================================
# Main
# =====================================================================

def main():
    print("=" * 70)
    print("MUS LANDSCAPE: MINIMAL 31-SETS IN THE INTEGER POOL")
    print("=" * 70)

    t_start = time.time()

    # Build pool
    rays = generate_integer_rays()
    triads, pairs, adj = find_triads_and_pairs(rays)
    print(f"Pool: {len(rays)} rays, {len(pairs)} pairs, {len(triads)} triads")

    # Phase 1: Extract many MUS sets
    sets_31, size_counts = extract_mus_sets(
        len(rays), triads, pairs, n_trials=5000)

    # Filter to size-31 only
    sets_31 = [s for s in sets_31 if len(s) == 31]
    print(f"\n  Total distinct 31-sets: {len(sets_31)}")

    if len(sets_31) < 2:
        print("  Not enough distinct sets for landscape analysis!")
        return

    # Phase 2: Ray frequency
    freq, core_rays, absent = ray_frequency_analysis(rays, sets_31)

    # Phase 3: Pairwise overlap
    overlaps, overlap_dist = overlap_analysis(sets_31)

    # Phase 4: Swap connectivity
    swap_edges = swap_connectivity(sets_31, triads, pairs, rays)

    # Phase 5: CK-31 in context
    ck31_context(rays, sets_31, freq)

    # Phase 6: Norm structure
    norm_analysis(rays, freq, sets_31)

    # Final summary
    t_total = time.time() - t_start
    print(f"\n{'='*70}")
    print("LANDSCAPE SUMMARY")
    print(f"{'='*70}")
    print(f"  Pool: 49 rays, OCUS-certified minimum: 31")
    print(f"  Distinct minimal 31-sets found: {len(sets_31)}")
    print(f"  Core rays (in ALL sets): {len(core_rays)}")
    print(f"  Rays never used: {len(absent)}")
    rays_used = len([r for r in range(len(rays)) if freq.get(r, 0) > 0])
    print(f"  Rays used in at least one set: {rays_used}/49")
    print(f"  Total time: {t_total:.1f}s")


if __name__ == "__main__":
    main()
