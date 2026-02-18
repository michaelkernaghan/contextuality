"""
ks_z3_focused.py -- Focused Z3 search: CK-31 merging + small realizability
==========================================================================

Key results (corrected CK-31 vectors):
- CK-31 vertex merging: 394 KS-preserving merges (all non-orthogonal pairs)
- Z3 returns "unknown" for all at 60s timeout
- Integer-pool CSP (ks_merge_integer_csp.py) proves all 394 unrealizable

This script focuses on the most informative approach (C: vertex merging)
and adds detailed analysis of WHY the merges aren't realizable.
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

import time
import numpy as np
from itertools import combinations

from pysat.solvers import Glucose4
import z3

# =====================================================================
# CK-31
# =====================================================================

CK31_VECS = [
    (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 1, -1), (0, 1, 2), (0, 2, -1),
    (1, 0, 0), (1, 0, 1), (1, 0, -1), (1, 0, 2), (1, 0, -2),
    (1, 1, 0), (1, 1, 1), (1, 1, -1), (1, 1, 2), (1, -1, 0),
    (1, -1, 1), (1, -1, -1), (1, -1, -2), (1, 2, 0), (1, 2, -1),
    (1, -2, 0), (1, -2, 1), (2, 0, 1), (2, 0, -1), (2, 1, 0),
    (2, 1, 1), (2, 1, -1), (2, -1, 0), (2, -1, 1), (2, -1, -1),
]

CK31_NAMES = [str(v) for v in CK31_VECS]


def dot_int(a, b):
    return sum(x * y for x, y in zip(a, b))


def build_ck31_graph():
    n = 31
    adj = {i: set() for i in range(n)}
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            if dot_int(CK31_VECS[i], CK31_VECS[j]) == 0:
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
    return adj, pairs, triads


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
        vi, vj = i + 1, j + 1
        solver.add_clause([-vi, -vj])
    result = solver.solve()
    solver.delete()
    return not result


def check_realizability_z3(n, pairs, timeout_ms=60000):
    """Check realizability in R^3 using Z3."""
    solver = z3.Solver()
    solver.set("timeout", timeout_ms)

    vecs = []
    for i in range(n):
        x = z3.Real(f"x_{i}")
        y = z3.Real(f"y_{i}")
        zz = z3.Real(f"z_{i}")
        vecs.append((x, y, zz))
        solver.add(x * x + y * y + zz * zz == 1)

    for i, j in pairs:
        xi, yi, zi = vecs[i]
        xj, yj, zj = vecs[j]
        solver.add(xi * xj + yi * yj + zi * zj == 0)

    result = solver.check()
    if result == z3.sat:
        return "sat", solver.model()
    elif result == z3.unsat:
        return "unsat", None
    else:
        return "unknown", None


# =====================================================================
# Approach C: Detailed CK-31 vertex merging analysis
# =====================================================================

print("=" * 70)
print("Z3 SEARCH: CK-31 VERTEX MERGING ANALYSIS")
print("=" * 70)

adj, pairs, triads = build_ck31_graph()
print(f"\nCK-31: 31 vectors, {len(pairs)} orthogonal pairs, {len(triads)} triads")

n = 31
merge_results = []

print(f"\nTesting all {n*(n-1)//2 - len(pairs)} non-orthogonal pair merges...")
t0 = time.time()

for v1 in range(n):
    for v2 in range(v1 + 1, n):
        if v2 in adj[v1]:
            continue

        # Merge v2 into v1
        remap = {}
        idx = 0
        for v in range(n):
            if v == v2:
                remap[v] = remap[v1]
            else:
                remap[v] = idx
                idx += 1

        new_n = 30
        new_pairs_set = set()
        for i, j in pairs:
            ni, nj = remap[i], remap[j]
            if ni != nj:
                new_pairs_set.add((min(ni, nj), max(ni, nj)))
        new_pairs = list(new_pairs_set)

        new_adj = {i: set() for i in range(new_n)}
        for i, j in new_pairs:
            new_adj[i].add(j)
            new_adj[j].add(i)

        new_triads = []
        for i in range(new_n):
            ni_list = sorted(new_adj[i])
            for idx_j, j in enumerate(ni_list):
                if j <= i:
                    continue
                for k in ni_list[idx_j + 1:]:
                    if k <= j:
                        continue
                    if k in new_adj[j]:
                        new_triads.append((i, j, k))

        if not new_triads:
            continue

        if is_ks_uncolorable(new_n, new_triads, new_pairs):
            merge_results.append((v1, v2, new_triads, new_pairs))

elapsed = time.time() - t0
print(f"\nFound {len(merge_results)} KS-preserving merges [{elapsed:.1f}s]")

# Now check realizability of each with detailed output
print(f"\n{'='*70}")
print("REALIZABILITY CHECK (Z3, 60s timeout each)")
print(f"{'='*70}")

for idx, (v1, v2, m_triads, m_pairs) in enumerate(merge_results):
    print(f"\n  Merge {idx+1}/{len(merge_results)}: "
          f"ray {v1} {CK31_NAMES[v1]} + ray {v2} {CK31_NAMES[v2]}")
    print(f"    Result: 30 vertices, {len(m_pairs)} pairs, {len(m_triads)} triads")

    t0 = time.time()
    status, model = check_realizability_z3(30, m_pairs, timeout_ms=60000)
    elapsed = time.time() - t0

    if status == "sat":
        print(f"    *** REALIZABLE! *** [{elapsed:.1f}s]")
    elif status == "unsat":
        print(f"    NOT realizable (Z3 proved) [{elapsed:.1f}s]")
    else:
        print(f"    Unknown/timeout [{elapsed:.1f}s]")


# =====================================================================
# Also try: remove one ray, add constraints for remaining 30
# =====================================================================

print(f"\n{'='*70}")
print("CK-31 SINGLE RAY REMOVAL: REALIZABILITY OF 30-RAY SUBSETS")
print("(checking if CK-31 minus one ray is realizable with EXTRA")
print(" orthogonalities that might restore KS-uncolorability)")
print(f"{'='*70}")

# We know CK-31 minus any single ray is colorable.
# But what if we add new orthogonality constraints between remaining rays?
# Can we find a 30-ray subset that becomes KS with added constraints?

# For each removal, check how many additional pairs would be needed
for removed in range(31):
    remaining = [i for i in range(31) if i != removed]
    remap = {old: new for new, old in enumerate(remaining)}

    sub_pairs = [(remap[i], remap[j]) for i, j in pairs
                 if i in remap and j in remap]
    sub_triads = [(remap[a], remap[b], remap[c])
                  for a, b, c in triads
                  if a in remap and b in remap and c in remap]

    n_triads_lost = len(triads) - len(sub_triads)
    n_pairs_lost = len(pairs) - len(sub_pairs)

    if removed < 5 or n_triads_lost >= 3:
        print(f"  Remove ray {removed} {CK31_NAMES[removed]}: "
              f"lose {n_triads_lost} triads, {n_pairs_lost} pairs, "
              f"remain {len(sub_triads)}t/{len(sub_pairs)}p")


# =====================================================================
# Approach: Can we find ANY 30-vertex KS graph realizable in R^3?
# Use known KS-uncolorable abstract graphs and check realizability.
# =====================================================================

print(f"\n{'='*70}")
print("ABSTRACT 30-VERTEX KS HYPERGRAPHS FROM CK-31 STRUCTURE")
print("(Modify CK-31's triad structure, check realizability)")
print(f"{'='*70}")

# Take CK-31's triads, try swapping one triad for another
import random
random.seed(42)

all_possible_triads_30 = list(combinations(range(30), 3))
n_tested = 0
n_ks = 0
n_realizable = 0

# Use the first merge (which we know is KS-uncolorable) as base
if merge_results:
    base_v1, base_v2, base_triads, base_pairs = merge_results[0]

    print(f"\nBase: merge of rays {base_v1}+{base_v2}, "
          f"{len(base_triads)} triads, {len(base_pairs)} pairs")

    # Try adding/removing triads
    print("\nTrying triad modifications (add one, remove one)...")

    for trial in range(100):
        modified_triads = list(base_triads)

        # Remove a random triad
        if modified_triads:
            idx_remove = random.randint(0, len(modified_triads) - 1)
            removed = modified_triads.pop(idx_remove)

        # Add a random new triad
        new_triad = random.choice(all_possible_triads_30)
        while new_triad in modified_triads:
            new_triad = random.choice(all_possible_triads_30)
        modified_triads.append(new_triad)

        # Build pairs
        pair_set = set()
        for a, b, c in modified_triads:
            pair_set.add((min(a, b), max(a, b)))
            pair_set.add((min(a, c), max(a, c)))
            pair_set.add((min(b, c), max(b, c)))
        mod_pairs = list(pair_set)

        n_tested += 1
        if is_ks_uncolorable(30, modified_triads, mod_pairs):
            n_ks += 1
            status, _ = check_realizability_z3(30, mod_pairs, timeout_ms=30000)
            if status == "sat":
                n_realizable += 1
                print(f"  *** REALIZABLE modified 30-vertex KS set "
                      f"(trial {trial+1})! ***")
                break
            elif status == "unsat":
                pass  # not realizable
        if (trial + 1) % 25 == 0:
            print(f"    Trial {trial+1}/100: "
                  f"{n_ks} KS, {n_realizable} realizable")

    print(f"\n  Summary: {n_tested} tested, {n_ks} KS-uncolorable, "
          f"{n_realizable} realizable")


print(f"\n{'='*70}")
print("Z3 FOCUSED SEARCH COMPLETE")
print("=" * 70)
