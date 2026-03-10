"""
ks_sub31_search.py -- Search for KS sets with fewer than 31 rays in R^3
=========================================================================

Goal: Either find a KS set in R^3 with n < 31 rays, or build evidence
that 31 is the minimum.

Key insight from CK-31: uncolorability requires BOTH triad constraints
(exactly one ray per basis is "true") AND pairwise exclusion constraints
(two orthogonal rays cannot both be "true"). The 17 triads alone are
NOT sufficient -- 20 additional orthogonal-pair constraints are needed.

Approach:
1. Method 1: Start from verified CK-31 and try removing rays
2. Method 2: Try all algebraic island pools for sub-31 subsets
3. Method 3: Search {0,±1,±2} coordinate space exhaustively
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

import numpy as np
from itertools import combinations
from pysat.solvers import Glucose4
import random
import time

random.seed(42)
np.random.seed(42)

try:
    from ks_spectral_filter import passes_fast_filter
    HAS_SPECTRAL = True
except ImportError:
    HAS_SPECTRAL = False

filtered_count = 0


def is_ks_uncolorable_full(n_vertices, triads, ortho_pairs):
    """Test KS-uncolorability using BOTH triads and pairwise constraints.

    For each triad {a,b,c}: exactly one is true (completeness + exclusion).
    For each orthogonal pair (i,j): at most one is true (exclusion).

    This is critical: CK-31 has 17 triads but 71 orthogonal pairs.
    The 20 pairs not covered by any triad provide essential constraints.
    """
    if not triads and not ortho_pairs:
        return False

    solver = Glucose4()

    # Triad constraints: exactly one true per basis
    for a, b, c in triads:
        va, vb, vc = a + 1, b + 1, c + 1
        solver.add_clause([va, vb, vc])       # at least one
        solver.add_clause([-va, -vb])          # at most one (pairwise)
        solver.add_clause([-va, -vc])
        solver.add_clause([-vb, -vc])

    # Pairwise exclusion for ALL orthogonal pairs (including those not in triads)
    for i, j in ortho_pairs:
        vi, vj = i + 1, j + 1
        solver.add_clause([-vi, -vj])

    result = solver.solve()
    solver.delete()
    return not result


def find_triads_and_pairs(rays, tol=1e-10):
    """Find all orthogonal pairs and mutually orthogonal triples.
    Uses exact integer arithmetic when possible."""
    n = len(rays)

    # Compute dot products
    dots = rays @ rays.T

    # Find orthogonal pairs
    ortho_pairs = []
    adj = {i: set() for i in range(n)}
    for i in range(n):
        for j in range(i + 1, n):
            if abs(dots[i, j]) < tol:
                ortho_pairs.append((i, j))
                adj[i].add(j)
                adj[j].add(i)

    # Find triads
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


def find_triads_and_pairs_exact(int_coords):
    """Find orthogonal pairs/triads using exact integer dot products."""
    n = len(int_coords)
    ortho_pairs = []
    adj = {i: set() for i in range(n)}

    for i in range(n):
        for j in range(i + 1, n):
            dot = sum(int_coords[i][k] * int_coords[j][k] for k in range(3))
            if dot == 0:
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


# =====================================================================
# Verified CK-31 coordinates (from ks_sat.py, matches literature)
# =====================================================================

CK31_INT = [
    (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 1, -1), (0, 1, 2), (0, 2, -1),
    (1, 0, 0), (1, 0, 1), (1, 0, -1), (1, 0, 2), (1, 0, -2),
    (1, 1, 0), (1, 1, 1), (1, 1, -1), (1, 1, 2), (1, -1, 0),
    (1, -1, 1), (1, -1, -1), (1, -1, -2), (1, 2, 0), (1, 2, -1),
    (1, -2, 0), (1, -2, 1), (2, 0, 1), (2, 0, -1), (2, 1, 0),
    (2, 1, 1), (2, 1, -1), (2, -1, 0), (2, -1, 1), (2, -1, -1)
]


# =====================================================================
print("=" * 70)
print("SEARCH FOR KS SETS WITH < 31 RAYS IN R^3")
print("=" * 70)

# =====================================================================
# Verify CK-31 first
# =====================================================================
print("\n--- Verifying CK-31 ---")
ck31_triads, ck31_pairs = find_triads_and_pairs_exact(CK31_INT)
print(f"  Rays: {len(CK31_INT)}")
print(f"  Orthogonal pairs: {len(ck31_pairs)}")
print(f"  Triads (bases): {len(ck31_triads)}")

# Count pairs not in any triad
pairs_in_triads = set()
for a, b, c in ck31_triads:
    pairs_in_triads.add((min(a, b), max(a, b)))
    pairs_in_triads.add((min(a, c), max(a, c)))
    pairs_in_triads.add((min(b, c), max(b, c)))
extra_pairs = len(ck31_pairs) - len(pairs_in_triads)
print(f"  Pairs in triads: {len(pairs_in_triads)}")
print(f"  Extra pairs (not in any triad): {extra_pairs}")

ks_full = is_ks_uncolorable_full(31, ck31_triads, ck31_pairs)
print(f"  KS-uncolorable (full constraints): {ks_full}")

if not ks_full:
    print("  ERROR: CK-31 verification failed!")
    sys.exit(1)

print("  CK-31 verified successfully.")


# =====================================================================
# Method 1: Remove rays from CK-31
# =====================================================================
print(f"\n{'='*70}")
print("--- Method 1: Reduce CK-31 by ray removal ---")
print("  Try removing 1-9 rays, check if remainder is still KS-uncolorable")
print("  (using full triad + pair constraints)")
print("=" * 70)

for n_remove in range(1, 10):
    found_smaller = False
    n_remaining = 31 - n_remove

    # For small removals, try all combinations; for larger, sample
    total_combos = 1
    for i in range(n_remove):
        total_combos = total_combos * (31 - i) // (i + 1)

    if total_combos <= 50000:
        # Exhaustive
        print(f"\n  Remove {n_remove} (exhaustive, {total_combos} combos):")
        tested = 0
        for remove in combinations(range(31), n_remove):
            remove_set = set(remove)
            keep = [i for i in range(31) if i not in remove_set]
            keep_set = set(keep)
            remap = {old: new for new, old in enumerate(keep)}

            sub_triads = [(remap[a], remap[b], remap[c])
                          for a, b, c in ck31_triads
                          if a in keep_set and b in keep_set and c in keep_set]
            sub_pairs = [(remap[i], remap[j])
                         for i, j in ck31_pairs
                         if i in keep_set and j in keep_set]

            if HAS_SPECTRAL and not passes_fast_filter(n_remaining, sub_pairs):
                filtered_count += 1
                tested += 1
                if tested % 5000 == 0:
                    print(f"    ... tested {tested}/{total_combos}")
                continue

            if is_ks_uncolorable_full(n_remaining, sub_triads, sub_pairs):
                found_smaller = True
                removed_coords = [CK31_INT[r] for r in remove]
                print(f"    *** STILL KS with {n_remaining} rays! "
                      f"Removed: {removed_coords}")
                print(f"        {len(sub_triads)} triads, {len(sub_pairs)} pairs")
                break

            tested += 1
            if tested % 5000 == 0:
                print(f"    ... tested {tested}/{total_combos}")
    else:
        # Sample
        n_trials = min(50000, total_combos)
        print(f"\n  Remove {n_remove} (sampling {n_trials} of {total_combos} combos):")
        tested = 0
        for _ in range(n_trials):
            remove = set(random.sample(range(31), n_remove))
            keep = [i for i in range(31) if i not in remove]
            keep_set = set(keep)
            remap = {old: new for new, old in enumerate(keep)}

            sub_triads = [(remap[a], remap[b], remap[c])
                          for a, b, c in ck31_triads
                          if a in keep_set and b in keep_set and c in keep_set]
            sub_pairs = [(remap[i], remap[j])
                         for i, j in ck31_pairs
                         if i in keep_set and j in keep_set]

            if HAS_SPECTRAL and not passes_fast_filter(n_remaining, sub_pairs):
                filtered_count += 1
                tested += 1
                if tested % 5000 == 0:
                    print(f"    ... tested {tested}/{n_trials}")
                continue

            if is_ks_uncolorable_full(n_remaining, sub_triads, sub_pairs):
                found_smaller = True
                removed_coords = [CK31_INT[r] for r in sorted(remove)]
                print(f"    *** STILL KS with {n_remaining} rays! "
                      f"Removed: {removed_coords}")
                print(f"        {len(sub_triads)} triads, {len(sub_pairs)} pairs")
                break

            tested += 1
            if tested % 5000 == 0:
                print(f"    ... tested {tested}/{n_trials}")

    if not found_smaller:
        print(f"    No {n_remaining}-ray KS subset found.")
        if n_remove == 1:
            print(f"    >>> CK-31 is 1-CRITICAL: every single ray is essential!")
        elif n_remove >= 3:
            print(f"    Stopping (if single removal fails, larger removals unlikely).")
            break


# =====================================================================
# Method 2: Search all {0,±1,±2} rays for sub-31 KS sets
# =====================================================================
print(f"\n{'='*70}")
print("--- Method 2: All rays from {0,±1,±2} alphabet ---")
print("  Generate ALL rays, find pairs/triads, search for KS subsets")
print("=" * 70)

# Generate all distinct rays from {0,±1,±2}
all_int_rays = []
seen = set()

for a in range(-2, 3):
    for b in range(-2, 3):
        for c in range(-2, 3):
            if a == 0 and b == 0 and c == 0:
                continue
            # Canonicalize: first nonzero coordinate positive
            v = (a, b, c)
            for coord in v:
                if coord != 0:
                    if coord < 0:
                        v = (-a, -b, -c)
                    break
            if v not in seen:
                seen.add(v)
                all_int_rays.append(v)

print(f"  Total distinct rays from {{0,±1,±2}}: {len(all_int_rays)}")

# Find all orthogonal pairs and triads
all_triads, all_pairs = find_triads_and_pairs_exact(all_int_rays)
print(f"  Orthogonal pairs: {len(all_pairs)}")
print(f"  Triads: {len(all_triads)}")

# Check if the full pool is KS-uncolorable
full_ks = is_ks_uncolorable_full(len(all_int_rays), all_triads, all_pairs)
print(f"  Full pool KS-uncolorable: {full_ks}")

if full_ks:
    # Try greedy minimization
    print(f"\n  Running greedy minimization (200 trials)...")
    best_size = len(all_int_rays)
    best_subset = None

    for trial in range(200):
        # Start with all rays, remove random rays while maintaining KS
        current = list(range(len(all_int_rays)))
        random.shuffle(current)

        for candidate_remove in list(current):
            test = [r for r in current if r != candidate_remove]
            if len(test) < 20:  # Below known lower bound
                break
            test_set = set(test)
            remap = {old: new for new, old in enumerate(test)}

            sub_triads = [(remap[a], remap[b], remap[c])
                          for a, b, c in all_triads
                          if a in test_set and b in test_set and c in test_set]
            sub_pairs = [(remap[i], remap[j])
                         for i, j in all_pairs
                         if i in test_set and j in test_set]

            if is_ks_uncolorable_full(len(test), sub_triads, sub_pairs):
                current = test

        if len(current) < best_size:
            best_size = len(current)
            best_subset = current[:]
            print(f"    Trial {trial+1}: new best = {best_size} rays")

        if trial % 50 == 49:
            print(f"    ... {trial+1} trials done, best = {best_size}")

    print(f"\n  Best minimized set: {best_size} rays")
    if best_size < 31:
        print(f"  *** SUB-31 KS SET FOUND: {best_size} rays! ***")
        coords = [all_int_rays[i] for i in best_subset]
        print(f"  Coordinates: {coords}")
    else:
        print(f"  No sub-31 KS set found from {{0,±1,±2}} alphabet.")


# =====================================================================
# Method 3: Use algebraic island pools
# =====================================================================
print(f"\n{'='*70}")
print("--- Method 3: Check all algebraic island pools ---")
print("  Use our computed island pools and try greedy minimization")
print("=" * 70)

# Import the island generation if available
try:
    from ks_islands import generate_island_pools
    pools = generate_island_pools()
    for name, rays_list in pools.items():
        rays = np.array(rays_list, dtype=float)
        norms = np.linalg.norm(rays, axis=1, keepdims=True)
        rays = rays / norms
        triads, pairs = find_triads_and_pairs(rays, tol=1e-8)
        ks = is_ks_uncolorable_full(len(rays), triads, pairs)
        print(f"  {name}: {len(rays)} rays, {len(triads)} triads, "
              f"{len(pairs)} pairs, KS={ks}")
except ImportError:
    print("  (ks_islands module not available, skipping)")


print(f"\n{'='*70}")
print("SEARCH COMPLETE")
print("=" * 70)
if HAS_SPECTRAL:
    print(f"  Spectral filter rejected: {filtered_count} candidates")
