"""Verify Z3 realizability at 600s timeout for CK-31 vertex merges."""
import sys
sys.stdout.reconfigure(line_buffering=True)

import time
from itertools import combinations
from pysat.solvers import Glucose4
import z3

CK31_VECS = [
    (1,0,0), (0,1,0), (0,0,1),
    (1,1,0), (1,-1,0), (1,0,1), (1,0,-1), (0,1,1), (0,1,-1),
    (1,1,1), (1,1,-1), (1,-1,1), (1,-1,-1),
    (2,1,0), (2,-1,0), (2,0,1), (2,0,-1), (0,2,1), (0,2,-1),
    (1,2,0), (1,0,2), (0,1,2),
    (2,1,1), (2,1,-1), (2,-1,1), (1,2,1), (1,2,-1), (1,1,2),
    (1,-2,1), (1,1,-2), (1,-1,2),
]

CK31_NAMES = [
    "(1,0,0)", "(0,1,0)", "(0,0,1)",
    "(1,1,0)", "(1,-1,0)", "(1,0,1)", "(1,0,-1)", "(0,1,1)", "(0,1,-1)",
    "(1,1,1)", "(1,1,-1)", "(1,-1,1)", "(1,-1,-1)",
    "(2,1,0)", "(2,-1,0)", "(2,0,1)", "(2,0,-1)", "(0,2,1)", "(0,2,-1)",
    "(1,2,0)", "(1,0,2)", "(0,1,2)",
    "(2,1,1)", "(2,1,-1)", "(2,-1,1)", "(1,2,1)", "(1,2,-1)", "(1,1,2)",
    "(1,-2,1)", "(1,1,-2)", "(1,-1,2)",
]

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

def check_realizability_z3(n, pairs, timeout_ms=600000):
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

# Build CK-31 graph
adj, pairs, triads = build_ck31_graph()
print(f"CK-31: 31 vectors, {len(pairs)} pairs, {len(triads)} triads")

# Find KS-preserving merges (same logic as ks_z3_focused.py)
n = 31
merge_results = []
print(f"\nFinding KS-preserving merges...")
for v1 in range(n):
    for v2 in range(v1 + 1, n):
        if v2 in adj[v1]:
            continue
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

print(f"Found {len(merge_results)} KS-preserving merges")

# Test first 3 at 600s timeout
print(f"\n{'='*70}")
print("REALIZABILITY CHECK (Z3, 600s timeout)")
print(f"{'='*70}")

for idx, (v1, v2, m_triads, m_pairs) in enumerate(merge_results[:3]):
    print(f"\n  Merge {idx+1}/3: "
          f"ray {v1} {CK31_NAMES[v1]} + ray {v2} {CK31_NAMES[v2]}")
    print(f"    30 vertices, {len(m_pairs)} pairs, {len(m_triads)} triads")
    print(f"    Running Z3 with 600s timeout...")

    t0 = time.time()
    status, model = check_realizability_z3(30, m_pairs, timeout_ms=600000)
    elapsed = time.time() - t0

    if status == "sat":
        print(f"    *** REALIZABLE! *** [{elapsed:.1f}s]")
    elif status == "unsat":
        print(f"    NOT realizable (Z3 proved) [{elapsed:.1f}s]")
    else:
        print(f"    Unknown/timeout [{elapsed:.1f}s]")

print(f"\n{'='*70}")
print("VERIFICATION COMPLETE")
print(f"{'='*70}")
