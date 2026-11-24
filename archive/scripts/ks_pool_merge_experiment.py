"""
ks_pool_merge_experiment.py -- Cross-island pool merge experiment
================================================================

Hypothesis: Combining ray pools from two different algebraic islands
(CK-31 integer pool and Peres sqrt(2) pool) into a single merged pool
might yield a KS-uncolorable subset smaller than 31 vectors.

The idea is that cross-island orthogonalities (integer ray orthogonal to
a sqrt(2) ray) could create new triads that enable tighter KS constraints.

Expectation: unlikely to beat 31, but the structure of the merged pool
and the composition of the minimal subset are interesting either way.

Steps:
  1. Generate integer pool {0, +/-1, +/-2} -> ~31 distinct rays
  2. Generate Peres pool {0, +/-1, +/-sqrt(2)} -> ~62 distinct rays
  3. Merge (union, removing projective duplicates)
  4. Build orthogonality graph (pairs + triads)
  5. Test KS-uncolorability via SAT (Glucose4)
  6. If uncolorable, run greedy SAT-based minimization (multiple trials)
  7. Report: pool sizes, merged size, bases, minimum KS subset,
     and which algebraic types the minimum uses.
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

import math
import random
import time
from itertools import combinations
from math import gcd

from pysat.solvers import Glucose4


# ============================================================
# Ray canonicalization (real-valued, exact for our alphabets)
# ============================================================

S2 = math.sqrt(2)
EPS = 1e-9


def canonicalize_ray(v):
    """
    Canonicalize a real 3D ray: normalize so max |coord| = 1,
    first nonzero component positive. Round to avoid float drift.
    """
    v = list(v)
    if all(abs(x) < EPS for x in v):
        return None
    # Make first nonzero positive
    for x in v:
        if abs(x) > EPS:
            if x < 0:
                v = [-x for x in v]
            break
    # Normalize so max abs = 1
    m = max(abs(x) for x in v)
    v = [x / m for x in v]
    return tuple(round(x, 10) for x in v)


def dot(u, v):
    return sum(a * b for a, b in zip(u, v))


# ============================================================
# Pool generation
# ============================================================

def generate_integer_pool():
    """Generate all distinct rays from alphabet {0, +/-1, +/-2}."""
    alphabet = [-2, -1, 0, 1, 2]
    rays_set = set()
    rays_list = []
    raw_list = []
    for a in alphabet:
        for b in alphabet:
            for c in alphabet:
                if a == 0 and b == 0 and c == 0:
                    continue
                canon = canonicalize_ray((a, b, c))
                if canon is not None and canon not in rays_set:
                    rays_set.add(canon)
                    rays_list.append(canon)
                    raw_list.append((a, b, c))
    return rays_list, raw_list


def generate_peres_pool():
    """Generate all distinct rays from alphabet {0, +/-1, +/-sqrt(2)}."""
    alphabet = [-S2, -1, 0, 1, S2]
    rays_set = set()
    rays_list = []
    raw_list = []
    for a in alphabet:
        for b in alphabet:
            for c in alphabet:
                if abs(a) + abs(b) + abs(c) < EPS:
                    continue
                canon = canonicalize_ray((a, b, c))
                if canon is not None and canon not in rays_set:
                    rays_set.add(canon)
                    rays_list.append(canon)
                    raw_list.append((a, b, c))
    return rays_list, raw_list


def classify_ray(raw):
    """Classify a raw coordinate tuple as 'integer', 'sqrt2', or 'both'."""
    has_irrational = False
    has_integer_gt1 = False
    for x in raw:
        ax = abs(x)
        if ax < EPS:
            continue
        if abs(ax - 1) < EPS:
            continue
        if abs(ax - 2) < EPS:
            has_integer_gt1 = True
        elif abs(ax - S2) < EPS:
            has_irrational = True
        else:
            # Mixed or other
            has_irrational = True
    if has_irrational and has_integer_gt1:
        return 'both'
    if has_irrational:
        return 'sqrt2'
    return 'integer'


# ============================================================
# Graph construction
# ============================================================

def build_orthogonality_graph(rays, tol=1e-9):
    """Build pairs and triads from a list of canonicalized rays."""
    n = len(rays)
    adj = {i: set() for i in range(n)}
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            if abs(dot(rays[i], rays[j])) < tol:
                pairs.append((i, j))
                adj[i].add(j)
                adj[j].add(i)

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

    return pairs, triads, adj


# ============================================================
# SAT-based KS coloring check
# ============================================================

def is_ks_uncolorable(n, pairs, triads):
    """Check if a ray configuration is KS-uncolorable via SAT."""
    if not triads:
        return False
    solver = Glucose4()
    # Triad constraints: exactly one green per triad
    triad_pair_set = set()
    for a, b, c in triads:
        va, vb, vc = a + 1, b + 1, c + 1
        solver.add_clause([va, vb, vc])        # at least one green
        solver.add_clause([-va, -vb])           # pairwise at most one
        solver.add_clause([-va, -vc])
        solver.add_clause([-vb, -vc])
        for x, y in combinations([a, b, c], 2):
            triad_pair_set.add((min(x, y), max(x, y)))

    # Pair constraints: at most one green for non-triad orthogonal pairs
    for i, j in pairs:
        if (min(i, j), max(i, j)) not in triad_pair_set:
            solver.add_clause([-(i + 1), -(j + 1)])

    result = solver.solve()
    solver.delete()
    return not result


# ============================================================
# Greedy SAT-based minimization
# ============================================================

def greedy_minimize(n_rays, pairs, triads, n_trials=1000):
    """
    Greedy deletion with random orderings to find minimal KS subset.
    Returns (best_subset_indices, best_size, size_distribution).
    """
    best = list(range(n_rays))
    best_size = n_rays
    sizes = {}

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
            keep = set(test)
            remap = {old: new for new, old in enumerate(test)}
            sub_triads = [(remap[a], remap[b], remap[c])
                          for a, b, c in triads
                          if a in keep and b in keep and c in keep]
            sub_pairs = [(remap[i], remap[j])
                         for i, j in pairs
                         if i in keep and j in keep]
            if is_ks_uncolorable(len(test), sub_pairs, sub_triads):
                current = test

        size = len(current)
        sizes[size] = sizes.get(size, 0) + 1
        if size < best_size:
            best = current
            best_size = size
            print(f"    Trial {trial+1}: new minimum {best_size}")

    return best, best_size, sizes


# ============================================================
# Main experiment
# ============================================================

def merge_pools(int_rays, int_raw, peres_rays, peres_raw):
    """Merge two ray pools, removing projective duplicates."""
    merged_set = set()
    merged_rays = []
    merged_raw = []
    merged_origin = []  # 'integer', 'peres', or 'shared'

    # Add integer rays first
    for canon, raw in zip(int_rays, int_raw):
        if canon not in merged_set:
            merged_set.add(canon)
            merged_rays.append(canon)
            merged_raw.append(raw)
            merged_origin.append('integer')

    # Add Peres rays, marking shared ones
    n_shared = 0
    for canon, raw in zip(peres_rays, peres_raw):
        if canon in merged_set:
            # Mark as shared
            idx = merged_rays.index(canon)
            if merged_origin[idx] == 'integer':
                merged_origin[idx] = 'shared'
                n_shared += 1
        else:
            merged_set.add(canon)
            merged_rays.append(canon)
            merged_raw.append(raw)
            merged_origin.append('peres')

    return merged_rays, merged_raw, merged_origin, n_shared


if __name__ == "__main__":
    random.seed(42)

    print("=" * 70)
    print("CROSS-ISLAND POOL MERGE EXPERIMENT")
    print("CK-31 (integer) + Peres (sqrt(2)) -> merged pool -> SAT minimize")
    print("=" * 70)
    print()

    # ---- Step 1: Generate pools ----
    t0 = time.time()

    print("Step 1: Generate individual pools")
    print("-" * 40)

    int_rays, int_raw = generate_integer_pool()
    print(f"  Integer pool {'{'}0, +/-1, +/-2{'}'}: {len(int_rays)} rays")

    peres_rays, peres_raw = generate_peres_pool()
    print(f"  Peres pool {'{'}0, +/-1, +/-sqrt(2){'}'}: {len(peres_rays)} rays")

    # ---- Step 2: Verify individual pools ----
    print(f"\nStep 2: Verify individual pools are KS-uncolorable")
    print("-" * 40)

    int_pairs, int_triads, int_adj = build_orthogonality_graph(int_rays)
    print(f"  Integer: {len(int_pairs)} pairs, {len(int_triads)} triads")
    int_unc = is_ks_uncolorable(len(int_rays), int_pairs, int_triads)
    print(f"  Integer KS-uncolorable: {int_unc}")

    per_pairs, per_triads, per_adj = build_orthogonality_graph(peres_rays)
    print(f"  Peres: {len(per_pairs)} pairs, {len(per_triads)} triads")
    per_unc = is_ks_uncolorable(len(peres_rays), per_pairs, per_triads)
    print(f"  Peres KS-uncolorable: {per_unc}")

    # ---- Step 3: Merge pools ----
    print(f"\nStep 3: Merge pools (union, removing projective duplicates)")
    print("-" * 40)

    merged_rays, merged_raw, merged_origin, n_shared = merge_pools(
        int_rays, int_raw, peres_rays, peres_raw)

    n_int_only = merged_origin.count('integer')
    n_peres_only = merged_origin.count('peres')
    n_shared_count = merged_origin.count('shared')

    print(f"  Merged pool: {len(merged_rays)} rays")
    print(f"    Integer-only: {n_int_only}")
    print(f"    Peres-only:   {n_peres_only}")
    print(f"    Shared:       {n_shared_count}")
    print(f"    (Shared rays have coordinates in both alphabets,")
    print(f"     e.g. (1,1,0) uses only {'{'}0, +/-1{'}'}.)")

    # ---- Step 4: Build orthogonality graph ----
    print(f"\nStep 4: Build orthogonality graph for merged pool")
    print("-" * 40)

    m_pairs, m_triads, m_adj = build_orthogonality_graph(merged_rays)
    print(f"  Merged: {len(m_pairs)} pairs, {len(m_triads)} triads")

    # Count cross-island triads (triads with rays from both islands)
    cross_triads = 0
    int_only_triads = 0
    peres_only_triads = 0
    mixed_triads = 0
    for a, b, c in m_triads:
        origins = {merged_origin[a], merged_origin[b], merged_origin[c]}
        # 'shared' counts as accessible from both
        has_int = any(merged_origin[x] in ('integer', 'shared') for x in (a, b, c))
        has_per = any(merged_origin[x] in ('peres', 'shared') for x in (a, b, c))
        has_pure_int = any(merged_origin[x] == 'integer' for x in (a, b, c))
        has_pure_per = any(merged_origin[x] == 'peres' for x in (a, b, c))
        if has_pure_int and has_pure_per:
            cross_triads += 1
        elif has_pure_per and not has_pure_int:
            peres_only_triads += 1
        elif has_pure_int and not has_pure_per:
            int_only_triads += 1
        else:
            mixed_triads += 1  # all shared

    print(f"  Triad breakdown:")
    print(f"    Integer-only triads:     {int_only_triads}")
    print(f"    Peres-only triads:       {peres_only_triads}")
    print(f"    Cross-island triads:     {cross_triads}")
    print(f"    Shared-only triads:      {mixed_triads}")

    # ---- Step 5: Test KS-uncolorability ----
    print(f"\nStep 5: Test merged pool KS-uncolorability")
    print("-" * 40)

    merged_unc = is_ks_uncolorable(len(merged_rays), m_pairs, m_triads)
    print(f"  Merged pool KS-uncolorable: {merged_unc}")

    if not merged_unc:
        print(f"\n  RESULT: Merged pool is COLORABLE -- no KS set possible.")
        print(f"  This would be very surprising. Stopping.")
        sys.exit(0)

    # ---- Step 6: Greedy minimization ----
    print(f"\nStep 6: Greedy SAT-based minimization ({len(merged_rays)} rays)")
    print("-" * 40)
    print(f"  Running 1000 trials...")

    t_min_start = time.time()
    best_subset, best_size, size_dist = greedy_minimize(
        len(merged_rays), m_pairs, m_triads, n_trials=1000)
    t_min_end = time.time()

    print(f"\n  Minimization complete ({t_min_end - t_min_start:.1f}s)")
    print(f"  Minimum KS subset found: {best_size} rays")

    # ---- Step 7: Analyze the minimal subset ----
    print(f"\nStep 7: Analyze minimal subset composition")
    print("-" * 40)

    # Count origins in the minimal subset
    min_int = sum(1 for i in best_subset if merged_origin[i] == 'integer')
    min_per = sum(1 for i in best_subset if merged_origin[i] == 'peres')
    min_shared = sum(1 for i in best_subset if merged_origin[i] == 'shared')

    print(f"  Minimal subset ({best_size} rays):")
    print(f"    Integer-only rays: {min_int}")
    print(f"    Peres-only rays:   {min_per}")
    print(f"    Shared rays:       {min_shared}")

    uses_both = min_int > 0 and min_per > 0
    print(f"  Uses both islands:   {uses_both}")

    # Print the actual rays
    print(f"\n  Rays in minimal subset:")
    for idx, i in enumerate(sorted(best_subset)):
        raw = merged_raw[i]
        origin = merged_origin[i]

        def fmt_coord(x):
            ax = abs(x)
            if ax < EPS:
                return "0"
            if abs(ax - 1) < EPS:
                return "1" if x > 0 else "-1"
            if abs(ax - 2) < EPS:
                return "2" if x > 0 else "-2"
            if abs(ax - S2) < EPS:
                return "s2" if x > 0 else "-s2"
            return f"{x:.4f}"

        coords = f"({fmt_coord(raw[0])}, {fmt_coord(raw[1])}, {fmt_coord(raw[2])})"
        print(f"    {idx+1:2d}. {coords:>20s}  [{origin}]")

    # Size distribution
    print(f"\n  Size distribution across all 1000 trials:")
    for size in sorted(size_dist.keys()):
        count = size_dist[size]
        bar = '#' * (count // 5)
        print(f"    {size:3d}: {count:4d} ({100*count/1000:.1f}%) {bar}")

    # Rebuild triads for minimal subset to count cross-island
    keep = set(best_subset)
    remap = {old: new for new, old in enumerate(best_subset)}
    min_triads = [(remap[a], remap[b], remap[c])
                  for a, b, c in m_triads
                  if a in keep and b in keep and c in keep]
    min_pairs = [(remap[i], remap[j])
                 for i, j in m_pairs
                 if i in keep and j in keep]

    print(f"\n  Minimal subset graph: {len(min_pairs)} pairs, {len(min_triads)} triads")

    # Count cross-island triads in minimal subset
    min_cross = 0
    for a, b, c in m_triads:
        if a in keep and b in keep and c in keep:
            has_pure_int = any(merged_origin[x] == 'integer' for x in (a, b, c))
            has_pure_per = any(merged_origin[x] == 'peres' for x in (a, b, c))
            if has_pure_int and has_pure_per:
                min_cross += 1
    print(f"  Cross-island triads in minimum: {min_cross}")

    # ---- Summary ----
    t_total = time.time() - t0

    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")
    print(f"  Integer pool:  {len(int_rays)} rays")
    print(f"  Peres pool:    {len(peres_rays)} rays")
    print(f"  Merged pool:   {len(merged_rays)} rays ({n_shared_count} shared)")
    print(f"  Merged triads: {len(m_triads)} ({cross_triads} cross-island)")
    print(f"  Minimum KS subset: {best_size} rays")
    print(f"    Integer-only: {min_int}, Peres-only: {min_per}, Shared: {min_shared}")
    print(f"    Uses both islands: {uses_both}")
    if best_size < 31:
        print(f"\n  *** BEATS CK-31! New minimum: {best_size} ***")
    elif best_size == 31:
        print(f"\n  Matches CK-31 minimum (31). Cross-island rays not needed.")
    else:
        print(f"\n  Does NOT beat CK-31 (31). Minimum is {best_size}.")

    if uses_both:
        print(f"  The minimal subset genuinely mixes both algebraic islands.")
        print(f"  This is structurally interesting even if it does not beat 31.")
    else:
        island = "integer" if min_per == 0 else "Peres"
        print(f"  The minimal subset comes entirely from the {island} island.")

    print(f"\n  Total time: {t_total:.1f}s")
    print(f"{'='*70}")
