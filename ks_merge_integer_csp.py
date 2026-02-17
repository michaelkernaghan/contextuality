"""
ks_merge_integer_csp.py -- Integer-pool CSP for CK-31 vertex merging
=====================================================================

The 15 abstract 30-vertex KS graphs from CK-31 vertex merging hit a Z3
timeout wall (nonlinear real arithmetic over ~90 variables). But CK-31
uses integer rays {0,±1,±2} (49 rays total), so we can test realizability
as a FINITE constraint satisfaction problem:

For each merged graph (30 vertices, ~67 orthogonality edges):
  - Each vertex can be assigned one of the 49 integer rays
  - Orthogonality: edge (i,j) => dot(ray_i, ray_j) = 0
  - Non-collinearity: distinct vertices => distinct rays
  - Encode as SAT: 30×49 = 1470 boolean variables

If any is realizable => 30-ray KS set found (breakthrough).
If none => CK-31 cannot be compressed by merging within the integer pool.
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

import time
from itertools import combinations
from pysat.solvers import Glucose4
from pysat.card import CardEnc, EncType

# =====================================================================
# CK-31 vectors (same ordering as ks_z3_focused.py)
# =====================================================================

CK31_VECS = [
    (1, 0, 0), (0, 1, 0), (0, 0, 1),
    (1, 1, 0), (1, -1, 0), (1, 0, 1), (1, 0, -1), (0, 1, 1), (0, 1, -1),
    (1, 1, 1), (1, 1, -1), (1, -1, 1), (1, -1, -1),
    (2, 1, 0), (2, -1, 0), (2, 0, 1), (2, 0, -1), (0, 2, 1), (0, 2, -1),
    (1, 2, 0), (1, 0, 2), (0, 1, 2),
    (2, 1, 1), (2, 1, -1), (2, -1, 1), (1, 2, 1), (1, 2, -1), (1, 1, 2),
    (1, -2, 1), (1, 1, -2), (1, -1, 2),
]

CK31_NAMES = [str(v) for v in CK31_VECS]


def dot_int(a, b):
    return sum(x * y for x, y in zip(a, b))


# =====================================================================
# Generate the 49 integer rays from {0,±1,±2}
# =====================================================================

def generate_integer_rays():
    rays = []
    seen = set()
    for a in range(-2, 3):
        for b in range(-2, 3):
            for c in range(-2, 3):
                if a == 0 and b == 0 and c == 0:
                    continue
                v = (a, b, c)
                for coord in v:
                    if coord != 0:
                        if coord < 0:
                            v = (-a, -b, -c)
                        break
                if v not in seen:
                    seen.add(v)
                    rays.append(v)
    return rays


# =====================================================================
# Precompute orthogonality between all 49 rays
# =====================================================================

def precompute_orthogonality(rays):
    """Returns set of (i,j) pairs where rays[i] ⊥ rays[j], i < j."""
    n = len(rays)
    ortho = set()
    for i in range(n):
        for j in range(i + 1, n):
            if dot_int(rays[i], rays[j]) == 0:
                ortho.add((i, j))
    return ortho


# =====================================================================
# Build CK-31 graph and find merges (reused from ks_z3_focused.py)
# =====================================================================

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


def find_ks_preserving_merges():
    """Find all 15 KS-preserving merges of CK-31."""
    adj, pairs, triads = build_ck31_graph()
    n = 31
    merge_results = []

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
                # Also store which CK-31 vertices map to which merged vertex
                merge_results.append({
                    'v1': v1,
                    'v2': v2,
                    'triads': new_triads,
                    'pairs': new_pairs,
                    'remap': remap,
                    'n': new_n,
                })

    return merge_results


# =====================================================================
# Integer-pool CSP via SAT encoding
# =====================================================================

def check_integer_realizability(n_vertices, abstract_pairs, abstract_non_pairs,
                                rays, ray_ortho_set):
    """
    Check if an abstract graph can be realized using rays from the pool.

    Variables: x_{v,r} = "vertex v is assigned ray r"  (v=0..n-1, r=0..R-1)

    Constraints:
    1. Each vertex assigned exactly one ray: sum_r x_{v,r} = 1
    2. Orthogonality: edge (i,j) => ray_i ⊥ ray_j
       For each non-orthogonal ray pair (r1,r2): ¬(x_{i,r1} ∧ x_{j,r2})
    3. Distinct vertices => distinct rays: ¬(x_{i,r} ∧ x_{j,r}) for all i≠j
       (Actually, collinear rays represent the same direction, so we need
        distinct DIRECTIONS. Two rays are collinear if one is a scalar multiple.)
    """
    R = len(rays)

    # Variable mapping: x_{v,r} -> SAT variable (1-indexed)
    def var(v, r):
        return v * R + r + 1

    top_var = n_vertices * R

    solver = Glucose4()

    # Constraint 1: Each vertex gets exactly one ray
    for v in range(n_vertices):
        lits = [var(v, r) for r in range(R)]
        # At least one
        solver.add_clause(lits)
        # At most one (pairwise encoding for R=49 is 49*48/2 = 1176 clauses per vertex)
        # Use cardinality encoding instead
        am1 = CardEnc.atmost(lits, bound=1, top_id=top_var, encoding=EncType.pairwise)
        top_var = max(top_var, max(abs(l) for cl in am1.clauses for l in cl))
        for cl in am1.clauses:
            solver.add_clause(cl)

    # Constraint 2: Orthogonality edges
    # If (i,j) is an edge, then for every non-orthogonal ray pair (r1,r2),
    # we add ¬x_{i,r1} ∨ ¬x_{j,r2}
    for i, j in abstract_pairs:
        for r1 in range(R):
            for r2 in range(R):
                pair = (min(r1, r2), max(r1, r2))
                if r1 != r2 and pair not in ray_ortho_set:
                    solver.add_clause([-var(i, r1), -var(j, r2)])
                elif r1 == r2:
                    # Same ray can be orthogonal to itself only if zero vector (impossible)
                    solver.add_clause([-var(i, r1), -var(j, r2)])

    # Constraint 3: Non-orthogonality for merged vertices
    # If (i,j) is NOT an edge (they were merged from non-orthogonal CK-31 rays),
    # then assigned rays must NOT be orthogonal
    for i, j in abstract_non_pairs:
        for r1 in range(R):
            for r2 in range(R):
                pair = (min(r1, r2), max(r1, r2))
                if r1 != r2 and pair in ray_ortho_set:
                    solver.add_clause([-var(i, r1), -var(j, r2)])
                elif r1 == r2:
                    # Same ray assigned to both is fine for non-orthogonality
                    # (but violates distinctness unless they ARE the merged vertex)
                    pass

    # Constraint 4: Distinct rays for distinct vertices
    for i in range(n_vertices):
        for j in range(i + 1, n_vertices):
            for r in range(R):
                solver.add_clause([-var(i, r), -var(j, r)])

    # Solve
    result = solver.solve()

    if result:
        model = solver.get_model()
        assignment = {}
        for v in range(n_vertices):
            for r in range(R):
                if model[var(v, r) - 1] > 0:
                    assignment[v] = rays[r]
                    break
        solver.delete()
        return True, assignment
    else:
        solver.delete()
        return False, None


# =====================================================================
# Main
# =====================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("INTEGER-POOL CSP FOR CK-31 VERTEX MERGING")
    print("=" * 70)

    # Generate integer rays
    rays = generate_integer_rays()
    print(f"\nInteger ray pool: {len(rays)} rays from {{0,±1,±2}}")

    # Precompute orthogonality
    ray_ortho = precompute_orthogonality(rays)
    print(f"Orthogonal ray pairs: {len(ray_ortho)}")

    # Find the 15 KS-preserving merges
    print("\nFinding KS-preserving merges of CK-31...")
    t0 = time.time()
    merges = find_ks_preserving_merges()
    print(f"Found {len(merges)} KS-preserving merges [{time.time()-t0:.1f}s]")

    # Test each merge for integer realizability
    print(f"\n{'='*70}")
    print("TESTING REALIZABILITY VIA INTEGER-POOL CSP")
    print(f"{'='*70}")

    n_realizable = 0
    n_unsat = 0

    for idx, merge in enumerate(merges):
        v1, v2 = merge['v1'], merge['v2']
        n = merge['n']
        m_pairs = merge['pairs']
        m_triads = merge['triads']

        # Compute non-edges (all vertex pairs that are NOT orthogonal)
        edge_set = set((min(i, j), max(i, j)) for i, j in m_pairs)
        non_pairs = []
        for i in range(n):
            for j in range(i + 1, n):
                if (i, j) not in edge_set:
                    non_pairs.append((i, j))

        print(f"\n  Merge {idx+1}/{len(merges)}: "
              f"ray {v1} {CK31_NAMES[v1]} + ray {v2} {CK31_NAMES[v2]}")
        print(f"    {n} vertices, {len(m_pairs)} edges, {len(m_triads)} triads, "
              f"{len(non_pairs)} non-edges")

        t0 = time.time()
        realizable, assignment = check_integer_realizability(
            n, m_pairs, non_pairs, rays, ray_ortho
        )
        elapsed = time.time() - t0

        if realizable:
            n_realizable += 1
            print(f"    *** REALIZABLE! *** [{elapsed:.1f}s]")
            print(f"    Assignment:")
            for v in range(n):
                print(f"      vertex {v} -> {assignment[v]}")

            # Verify the assignment
            print("    Verification:")
            ok = True
            for i, j in m_pairs:
                d = dot_int(assignment[i], assignment[j])
                if d != 0:
                    print(f"      FAIL: edge ({i},{j}): dot = {d}")
                    ok = False
            if ok:
                print("      All orthogonality constraints satisfied.")
            # Check KS-uncolorability of the realized set
            real_coords = [assignment[v] for v in range(n)]
            from ks_sub31_search import find_triads_and_pairs_exact, is_ks_uncolorable_full
            real_triads, real_pairs = find_triads_and_pairs_exact(real_coords)
            ks = is_ks_uncolorable_full(n, real_triads, real_pairs)
            print(f"      KS-uncolorable with real coordinates: {ks}")
            if ks:
                print(f"      *** 30-RAY KS SET FOUND! ***")
        else:
            n_unsat += 1
            print(f"    Not realizable in integer pool [{elapsed:.1f}s]")

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"  Tested: {len(merges)} KS-preserving merges")
    print(f"  Realizable: {n_realizable}")
    print(f"  Not realizable: {n_unsat}")

    if n_realizable > 0:
        print(f"\n  *** BREAKTHROUGH: {n_realizable} merge(s) realizable "
              f"in integer pool! ***")
    else:
        print(f"\n  Conclusion: CK-31 cannot be compressed by vertex merging")
        print(f"  within the {{0,±1,±2}} integer construction.")
        print(f"  The 24-31 gap remains a realizability problem.")
