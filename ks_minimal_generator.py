"""
ks_minimal_generator.py -- Find the smallest generator module for KS sets
=========================================================================

Question: What is the smallest pattern of rays + triads that, when stitched
together in copies, produces KS-uncolorability?

We systematically search modules from 5 rays upward, trying all reasonable
triad arrangements, and test whether copies can be stitched into uncolorable sets.
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

import random
from itertools import combinations
from pysat.solvers import Glucose4

random.seed(42)


def is_ks_uncolorable(n_vertices, triads):
    """Test if a hypergraph is KS-uncolorable via SAT."""
    if not triads:
        return False
    solver = Glucose4()
    for a, b, c in triads:
        va, vb, vc = a + 1, b + 1, c + 1
        solver.add_clause([va, vb, vc])
        solver.add_clause([-va, -vb])
        solver.add_clause([-va, -vc])
        solver.add_clause([-vb, -vc])
    result = solver.solve()
    solver.delete()
    return not result


def stitch_two_modules(module_triads, n_verts, sharing):
    """Stitch two copies of a module with specified vertex sharing.

    sharing: list of (v_in_mod1, v_in_mod2) pairs to identify.
    Returns (total_vertices, merged_triads).
    """
    # Module 2 vertices start at n_verts
    offset = n_verts

    # Union-find
    parent = {}
    def find(x):
        while parent.get(x, x) != x:
            parent[x] = parent.get(parent[x], parent[x])
            x = parent[x]
        return x
    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py

    for v1, v2 in sharing:
        union(v1, v2 + offset)

    # Collect all vertices
    all_verts = set()
    all_triads_raw = []

    # Module 1 triads
    for t in module_triads:
        all_triads_raw.append(tuple(t))
        all_verts.update(t)

    # Module 2 triads (offset)
    for t in module_triads:
        shifted = tuple(v + offset for v in t)
        all_triads_raw.append(shifted)
        all_verts.update(shifted)

    # Remap to canonical
    canonical = {}
    counter = 0
    for v in sorted(all_verts):
        r = find(v)
        if r not in canonical:
            canonical[r] = counter
            counter += 1

    remapped = []
    for t in all_triads_raw:
        rt = tuple(canonical[find(v)] for v in t)
        # Skip degenerate triads (where merging collapsed vertices)
        if len(set(rt)) == 3:
            remapped.append(rt)

    # Deduplicate triads
    unique_triads = list(set(tuple(sorted(t)) for t in remapped))
    # Convert back to unsorted tuples for SAT
    final_triads = [t for t in unique_triads]

    return counter, final_triads


def stitch_n_modules(module_triads, n_verts, n_copies, sharing_fn):
    """Stitch n copies of a module.

    sharing_fn(i, j, n_verts): returns list of (v_mod_i, v_mod_j) pairs to share
    between adjacent modules i and j.
    """
    parent = {}
    def find(x):
        while parent.get(x, x) != x:
            parent[x] = parent.get(parent[x], parent[x])
            x = parent[x]
        return x
    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py

    # Apply sharing between adjacent copies
    for i in range(n_copies - 1):
        pairs = sharing_fn(i, i + 1, n_verts)
        for v1, v2 in pairs:
            union(v1 + i * n_verts, v2 + (i + 1) * n_verts)

    # Collect triads from all copies
    all_verts = set()
    all_triads_raw = []
    for copy in range(n_copies):
        off = copy * n_verts
        for t in module_triads:
            shifted = tuple(v + off for v in t)
            all_triads_raw.append(shifted)
            all_verts.update(shifted)

    # Remap
    canonical = {}
    counter = 0
    for v in sorted(all_verts):
        r = find(v)
        if r not in canonical:
            canonical[r] = counter
            counter += 1

    final_triads = []
    for t in all_triads_raw:
        rt = tuple(canonical[find(v)] for v in t)
        if len(set(rt)) == 3:
            final_triads.append(rt)

    unique = list(set(tuple(sorted(t)) for t in final_triads))
    return counter, unique


# =====================================================================
print("=" * 70)
print("MINIMAL GENERATOR SEARCH")
print("=" * 70)

# =====================================================================
# Part 1: Enumerate small module shapes and test stitchability
# =====================================================================

print("\n--- Part 1: Systematic small modules ---")
print("  For each module size, enumerate triad arrangements and test")
print("  whether stitching 2-6 copies produces uncolorability.\n")

results = []

# Module types to test:
# Each defined by (name, n_vertices, triads, "boundary" vertices available for stitching)

modules = []

# === 3 vertices, 1 triad ===
modules.append(("triangle-3v", 3, [(0, 1, 2)]))

# === 4 vertices, 2 triads (sharing an edge) ===
modules.append(("fan-4v-2t", 4, [(0, 1, 2), (0, 1, 3)]))
modules.append(("chain-4v-2t", 4, [(0, 1, 2), (1, 2, 3)]))

# === 5 vertices, various triad counts ===
modules.append(("5v-2t-disjoint-edge", 5, [(0, 1, 2), (0, 3, 4)]))
modules.append(("5v-2t-chain", 5, [(0, 1, 2), (2, 3, 4)]))
modules.append(("5v-3t-fan", 5, [(0, 1, 2), (0, 1, 3), (0, 1, 4)]))
modules.append(("5v-3t-star", 5, [(0, 1, 2), (0, 3, 4), (1, 3, 4)]))
modules.append(("5v-3t-chain", 5, [(0, 1, 2), (1, 2, 3), (2, 3, 4)]))

# === 6 vertices ===
modules.append(("6v-3t-disjoint", 6, [(0, 1, 2), (0, 3, 4), (1, 4, 5)]))
modules.append(("6v-3t-chain", 6, [(0, 1, 2), (2, 3, 4), (4, 5, 0)]))
modules.append(("6v-4t-dense", 6, [(0, 1, 2), (0, 3, 4), (1, 3, 5), (2, 4, 5)]))
modules.append(("6v-4t-fan", 6, [(0, 1, 2), (0, 1, 3), (0, 4, 5), (1, 4, 5)]))

# === 7 vertices (pentagon + 2 caps) ===
modules.append(("7v-pent+2caps", 7,
    [(5, 0, 2), (6, 1, 3)]))  # 2 triads from non-adj pentagon verts
modules.append(("7v-3t-mixed", 7,
    [(0, 1, 2), (2, 3, 4), (4, 5, 6)]))
modules.append(("7v-4t", 7,
    [(0, 1, 5), (1, 2, 6), (2, 3, 5), (3, 4, 6)]))

# === 8 vertices (pentagon + 3 caps) ===
modules.append(("8v-pent+3caps", 8,
    [(5, 0, 2), (6, 1, 3), (7, 2, 4)]))
modules.append(("8v-4t", 8,
    [(0, 1, 5), (1, 2, 6), (2, 3, 7), (3, 4, 5)]))

# === 9 vertices (pentagon + 4 caps) ===
modules.append(("9v-pent+4caps", 9,
    [(5, 0, 2), (6, 1, 3), (7, 2, 4), (8, 3, 0)]))

# === 10 vertices (full 10-ray module) ===
modules.append(("10v-pent+5caps", 10,
    [(5, 0, 2), (6, 1, 3), (7, 2, 4), (8, 3, 0), (9, 4, 1)]))

# === Also try Fano-plane-like structures ===
# Fano plane: 7 points, 7 lines of 3 points each
modules.append(("7v-fano", 7,
    [(0, 1, 2), (0, 3, 4), (0, 5, 6), (1, 3, 5), (1, 4, 6), (2, 3, 6), (2, 4, 5)]))

# Partial Fano
modules.append(("7v-partial-fano-4t", 7,
    [(0, 1, 2), (0, 3, 4), (1, 3, 5), (2, 4, 6)]))

# Anti-Fano / complementary
modules.append(("6v-steiner", 6,
    [(0, 1, 2), (0, 3, 4), (1, 3, 5), (2, 4, 5)]))


print(f"  Testing {len(modules)} module types\n")

for mod_name, n_verts, triads in modules:
    # First check: is the module itself uncolorable?
    self_ks = is_ks_uncolorable(n_verts, triads)

    if self_ks:
        print(f"  {mod_name} ({n_verts}v, {len(triads)}t): SELF-UNCOLORABLE!")
        results.append((mod_name, n_verts, len(triads), 1, n_verts))
        continue

    # Try stitching with various sharing patterns
    best_total = None
    best_copies = None
    best_sharing_desc = None

    # Generate all possible sharing patterns (share 1 to n_verts-1 vertices)
    for n_shared in range(1, n_verts):
        for n_copies in range(2, 8):
            # Try several random sharing patterns
            found_for_this = False
            for trial in range(200):
                src = random.sample(range(n_verts), min(n_shared, n_verts))
                dst = random.sample(range(n_verts), min(n_shared, n_verts))

                def sharing_fn(i, j, nv, s=src, d=dst):
                    return list(zip(s, d))

                total_v, merged_t = stitch_n_modules(triads, n_verts, n_copies, sharing_fn)

                if merged_t and is_ks_uncolorable(total_v, merged_t):
                    if best_total is None or total_v < best_total:
                        best_total = total_v
                        best_copies = n_copies
                        best_sharing_desc = f"share {n_shared}, {n_copies} copies"
                    found_for_this = True
                    break  # Found one for this config, move on

            if found_for_this and n_copies == 2:
                break  # Already found with 2 copies, no need for more

    if best_total is not None:
        print(f"  {mod_name} ({n_verts}v, {len(triads)}t): "
              f"best = {best_total}v with {best_sharing_desc}")
        results.append((mod_name, n_verts, len(triads), best_copies, best_total))
    else:
        print(f"  {mod_name} ({n_verts}v, {len(triads)}t): no uncolorable stitching found (<7 copies)")


# =====================================================================
# Part 2: Exhaustive search for minimal generators
# =====================================================================
print(f"\n{'='*70}")
print("Part 2: Exhaustive search -- all triad sets on n vertices")
print(f"{'='*70}")

def all_triad_sets(n_verts, min_triads, max_triads):
    """Generate all possible sets of triads on n vertices."""
    all_possible = list(combinations(range(n_verts), 3))
    for n_t in range(min_triads, min(max_triads + 1, len(all_possible) + 1)):
        for triad_combo in combinations(all_possible, n_t):
            yield list(triad_combo)


for n_verts in [4, 5, 6]:
    print(f"\n--- Exhaustive search: {n_verts} vertices ---")
    max_t = min(7, n_verts * (n_verts - 1) // 3)  # reasonable upper bound on triads

    best_for_size = None
    n_tested = 0

    for triads in all_triad_sets(n_verts, 2, max_t):
        n_tested += 1

        # Skip if self-uncolorable (trivial)
        if is_ks_uncolorable(n_verts, triads):
            continue

        # Quick test: stitch 3 copies with heavy sharing
        for n_copies in [3, 4, 5]:
            for trial in range(50):
                n_shared = random.randint(1, n_verts - 1)
                src = random.sample(range(n_verts), n_shared)
                dst = random.sample(range(n_verts), n_shared)

                def sharing_fn(i, j, nv, s=src, d=dst):
                    return list(zip(s, d))

                total_v, merged_t = stitch_n_modules(triads, n_verts, n_copies, sharing_fn)

                if merged_t and total_v < 31 and is_ks_uncolorable(total_v, merged_t):
                    if best_for_size is None or total_v < best_for_size[0]:
                        best_for_size = (total_v, n_verts, triads, n_copies, n_shared)
                        print(f"    NEW BEST: {total_v}v from {n_verts}v module "
                              f"({len(triads)}t) x {n_copies} copies, share {n_shared}")

        if n_tested % 500 == 0:
            print(f"    ...tested {n_tested} modules so far...")

    print(f"  Tested {n_tested} module configurations for {n_verts} vertices")
    if best_for_size:
        print(f"  BEST: {best_for_size[0]}v from {best_for_size[1]}v module "
              f"x {best_for_size[3]} copies")


# =====================================================================
# Summary
# =====================================================================
print(f"\n{'='*70}")
print("SUMMARY: Minimal generators found")
print(f"{'='*70}")

if results:
    results.sort(key=lambda x: (x[1], x[4]))  # Sort by module size, then total
    print(f"\n  {'Module':<30} {'Size':>5} {'Triads':>7} {'Copies':>7} {'Total':>6}")
    print(f"  {'-'*30} {'-'*5} {'-'*7} {'-'*7} {'-'*6}")
    for name, n_v, n_t, copies, total in results:
        print(f"  {name:<30} {n_v:>5} {n_t:>7} {copies:>7} {total:>6}")

print(f"\n  Key insight: The minimum module that generates KS-uncolorability")
print(f"  when stitched is the answer to 'what is the simplest contextuality engine?'")
print(f"\n  Remember: abstract uncolorability != geometric realizability in R^3")

print(f"\n{'='*70}")
print("DONE")
print(f"{'='*70}")
