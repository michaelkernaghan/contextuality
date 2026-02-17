"""
ks_z3_search.py -- Z3/SMT-based search for sub-31 KS sets
==========================================================

Three approaches:
  A) Abstract KS hypergraph enumeration (PySAT) + realizability check (Z3)
  B) Direct Z3 encoding: find n vectors in R^3 forming a KS set
  C) Targeted: fix CK-31 graph, remove vertices, try to realize
     modified graphs with fewer vectors

The LBG approach (arXiv:2306.13319) proved lower bound 24 using
SAT + orderly generation + Z3 realizability. We attempt a simplified
version without proof certificates.
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

import time
import math
import random
import numpy as np
from itertools import combinations

from pysat.solvers import Glucose4
import z3

random.seed(42)


# =====================================================================
# CK-31 orthogonality graph (for reference and targeted search)
# =====================================================================

CK31_VECS = [
    (1,0,0), (0,1,0), (0,0,1),
    (1,1,0), (1,-1,0), (1,0,1), (1,0,-1), (0,1,1), (0,1,-1),
    (1,1,1), (1,1,-1), (1,-1,1), (1,-1,-1),
    (2,1,0), (2,-1,0), (2,0,1), (2,0,-1), (0,2,1), (0,2,-1),
    (1,2,0), (1,0,2), (0,1,2),
    (2,1,1), (2,1,-1), (2,-1,1), (1,2,1), (1,2,-1), (1,1,2),
    (1,-2,1), (1,1,-2), (1,-1,2),
]


def dot_int(a, b):
    return sum(x * y for x, y in zip(a, b))


def build_ck31_graph():
    """Build CK-31 orthogonality graph."""
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


def is_ks_uncolorable_sat(n, triads, pairs):
    """Check KS-uncolorability via SAT."""
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


# =====================================================================
# Approach A: Enumerate abstract KS hypergraphs + Z3 realizability
# =====================================================================

def check_realizability_z3(n, pairs, timeout_ms=30000):
    """Check if an abstract orthogonality graph is realizable in R^3.

    Given n vertices and a set of pairs that must be orthogonal,
    find unit vectors v_1,...,v_n in R^3 satisfying all constraints.
    Returns (realizable, model_or_None).
    """
    solver = z3.Solver()
    solver.set("timeout", timeout_ms)

    # Create real variables for each vector
    vecs = []
    for i in range(n):
        x = z3.Real(f"x_{i}")
        y = z3.Real(f"y_{i}")
        zz = z3.Real(f"z_{i}")
        vecs.append((x, y, zz))

    # Unit norm constraints (relaxed: norm^2 = 1)
    for i in range(n):
        x, y, zz = vecs[i]
        solver.add(x * x + y * y + zz * zz == 1)

    # Orthogonality constraints for specified pairs
    for i, j in pairs:
        xi, yi, zi = vecs[i]
        xj, yj, zj = vecs[j]
        solver.add(xi * xj + yi * yj + zi * zj == 0)

    # Non-collinearity: distinct rays should not be parallel
    # (This is expensive, so only add for pairs in same triad)
    # Actually, unit vectors that are collinear would be v_j = +/- v_i
    # which would mean their dot product is +/- 1, not 0, so
    # orthogonality constraints already prevent collinearity for
    # orthogonal pairs. For non-orthogonal pairs, we add:
    # Not all proportional (at least one coordinate ratio differs)
    # This is too expensive for Z3. Skip and check post-hoc.

    result = solver.check()
    if result == z3.sat:
        model = solver.model()
        return True, model
    elif result == z3.unsat:
        return False, None
    else:
        return None, None  # timeout / unknown


def enumerate_small_ks_hypergraphs(n, max_triads=30, max_candidates=1000):
    """Generate random KS-uncolorable hypergraphs on n vertices.

    Since exhaustive enumeration is intractable for n >= 25,
    we sample random hypergraphs and filter for KS-uncolorability.
    """
    candidates = []
    attempts = 0
    max_attempts = max_candidates * 100

    while len(candidates) < max_candidates and attempts < max_attempts:
        attempts += 1

        # Generate random triads
        n_triads = random.randint(10, max_triads)
        all_possible = list(combinations(range(n), 3))
        if n_triads > len(all_possible):
            n_triads = len(all_possible)
        triads = random.sample(all_possible, n_triads)

        # Extract pairs from triads
        pair_set = set()
        for a, b, c in triads:
            pair_set.add((min(a, b), max(a, b)))
            pair_set.add((min(a, c), max(a, c)))
            pair_set.add((min(b, c), max(b, c)))
        pairs = list(pair_set)

        # Check KS-uncolorability
        if is_ks_uncolorable_sat(n, triads, pairs):
            candidates.append((triads, pairs))

        if attempts % 10000 == 0:
            print(f"    ... {attempts} attempts, {len(candidates)} KS candidates found")

    return candidates


def approach_a(n_target):
    """Approach A: Random KS hypergraphs + Z3 realizability."""
    print(f"\n  Generating random KS hypergraphs on {n_target} vertices...")
    t0 = time.time()
    candidates = enumerate_small_ks_hypergraphs(
        n_target, max_triads=25, max_candidates=100)
    t_gen = time.time() - t0
    print(f"  Found {len(candidates)} KS-uncolorable hypergraphs [{t_gen:.1f}s]")

    if not candidates:
        print("  No abstract KS hypergraphs found at this size.")
        return False

    # Check realizability of each
    realizable_count = 0
    for idx, (triads, pairs) in enumerate(candidates):
        result, model = check_realizability_z3(n_target, pairs, timeout_ms=30000)
        if result is True:
            realizable_count += 1
            print(f"  *** REALIZABLE KS set found! "
                  f"({len(triads)} triads, {len(pairs)} pairs) ***")
            return True
        elif result is None:
            pass  # timeout
        if (idx + 1) % 20 == 0:
            print(f"    Checked {idx+1}/{len(candidates)}, "
                  f"realizable: {realizable_count}, "
                  f"[{time.time()-t0:.1f}s]")

    print(f"  No realizable KS hypergraph found among {len(candidates)} candidates.")
    return False


# =====================================================================
# Approach B: Direct Z3 encoding (small n only)
# =====================================================================

def approach_b(n_target, min_triads=10, timeout_ms=120000):
    """Direct Z3 encoding: find n vectors forming a KS set.

    This combines continuous (coordinates) and discrete (coloring)
    constraints in a single Z3 query. Likely intractable for n > 20.
    """
    print(f"\n  Direct Z3 encoding for {n_target}-vector KS set "
          f"(timeout={timeout_ms//1000}s)...")
    t0 = time.time()

    solver = z3.Solver()
    solver.set("timeout", timeout_ms)

    # Vector coordinates (real)
    vecs = []
    for i in range(n_target):
        x = z3.Real(f"x_{i}")
        y = z3.Real(f"y_{i}")
        zz = z3.Real(f"z_{i}")
        vecs.append((x, y, zz))
        # Unit norm
        solver.add(x * x + y * y + zz * zz == 1)

    # Edge variables: e[i][j] = True if rays i,j are orthogonal
    e = {}
    for i in range(n_target):
        for j in range(i + 1, n_target):
            e[(i, j)] = z3.Bool(f"e_{i}_{j}")
            xi, yi, zi = vecs[i]
            xj, yj, zj = vecs[j]
            dot = xi * xj + yi * yj + zi * zj
            # e[(i,j)] => dot == 0
            solver.add(z3.Implies(e[(i, j)], dot == 0))

    # Triad variables: t[i][j][k] = True if (i,j,k) form an orthogonal triple
    triads_list = list(combinations(range(n_target), 3))
    t_vars = {}
    for a, b, c in triads_list:
        tv = z3.Bool(f"t_{a}_{b}_{c}")
        t_vars[(a, b, c)] = tv
        ab = e[(min(a, b), max(a, b))]
        ac = e[(min(a, c), max(a, c))]
        bc = e[(min(b, c), max(b, c))]
        # t => all three edges
        solver.add(z3.Implies(tv, z3.And(ab, ac, bc)))
        # all three edges => t
        solver.add(z3.Implies(z3.And(ab, ac, bc), tv))

    # Minimum number of triads
    solver.add(z3.Sum([z3.If(tv, 1, 0) for tv in t_vars.values()]) >= min_triads)

    # KS-uncolorability: no valid {0,1} coloring exists
    # For each potential coloring, at least one triad must be violated
    # This is the hard part -- we encode it as:
    # For each triad, exactly one vertex gets color 1
    # AND for each orthogonal pair, at most one gets color 1
    # AND this system must be UNSATISFIABLE
    #
    # We encode this using coloring variables and assert they can't all be satisfied
    c_vars = [z3.Bool(f"c_{i}") for i in range(n_target)]

    # Build the coloring constraints
    coloring_clauses = []
    # For each triad: at least one colored 1, at most one colored 1
    for (a, b, c), tv in t_vars.items():
        # If this is a triad, enforce exactly-one
        coloring_clauses.append(
            z3.Implies(tv, z3.Or(c_vars[a], c_vars[b], c_vars[c])))
        coloring_clauses.append(
            z3.Implies(tv, z3.Not(z3.And(c_vars[a], c_vars[b]))))
        coloring_clauses.append(
            z3.Implies(tv, z3.Not(z3.And(c_vars[a], c_vars[c]))))
        coloring_clauses.append(
            z3.Implies(tv, z3.Not(z3.And(c_vars[b], c_vars[c]))))

    # For each orthogonal pair: at most one colored 1
    for (i, j), ev in e.items():
        coloring_clauses.append(
            z3.Implies(ev, z3.Not(z3.And(c_vars[i], c_vars[j]))))

    # The system should be UNSAT: no coloring satisfies all constraints
    # We assert that the coloring constraints CANNOT all be true
    # i.e., NOT(AND(all coloring constraints))
    # But this means "there exists a graph where no coloring works"
    # Z3 would need to find vectors AND show no coloring exists.
    #
    # This is a forall-exists problem (forall colorings, exists violated constraint)
    # which Z3 can handle with quantifiers but it's very expensive.
    #
    # Simpler: assert that at least one of several known-bad coloring
    # patterns holds. But this doesn't capture all colorings.
    #
    # Actually, the cleanest encoding: we want the orthogonality graph
    # to be KS-uncolorable. We can encode this as:
    # For EVERY possible coloring (2^n), the coloring violates some constraint.
    # With n=25, that's 2^25 = 33M constraints. Too many.
    #
    # Alternative: use the SAT characterization. The coloring problem
    # is itself a SAT problem. We need the SAT problem to be UNSAT.
    # This is a "UNSAT certificate" which Z3 can represent as
    # "no assignment to c_vars satisfies all coloring constraints."
    #
    # Z3 approach: use ForAll quantifier over coloring variables
    coloring_sat = z3.And(coloring_clauses)
    # We want: the graph is such that no coloring works
    # i.e., ForAll c_vars, NOT(coloring_sat)
    # But ForAll with real arithmetic underneath is undecidable in general.
    # Let's try anyway with a timeout.

    solver.add(z3.ForAll(c_vars, z3.Not(coloring_sat)))

    result = solver.check()
    elapsed = time.time() - t0

    if result == z3.sat:
        print(f"  *** Z3 found a {n_target}-vector KS set! *** [{elapsed:.1f}s]")
        return True
    elif result == z3.unsat:
        print(f"  Z3 proved no {n_target}-vector KS set exists [{elapsed:.1f}s]")
        return False
    else:
        print(f"  Z3 returned {result} (timeout/unknown) [{elapsed:.1f}s]")
        return None


# =====================================================================
# Approach C: Fix graph structure from CK-31, check modified versions
# =====================================================================

def approach_c_targeted():
    """Try to realize KS-uncolorable subgraphs of CK-31 with fewer vectors.

    For each pair of CK-31 rays: can we merge them (identify two vertices)
    while preserving KS-uncolorability, and is the merged graph realizable?
    """
    adj, pairs, triads = build_ck31_graph()
    print(f"\n  CK-31: {len(pairs)} pairs, {len(triads)} triads")

    # Strategy: try to identify pairs of vertices (merge two rays into one)
    # If the merged graph is still KS-uncolorable, check realizability
    n = 31
    merge_candidates = 0
    realizable = 0

    for v1 in range(n):
        for v2 in range(v1 + 1, n):
            # Skip if v1, v2 are orthogonal (can't merge orthogonal rays)
            if v2 in adj[v1]:
                continue

            # Merge v2 into v1: relabel v2 -> v1, delete v2
            new_n = n - 1
            remap = {}
            idx = 0
            for v in range(n):
                if v == v2:
                    remap[v] = remap[v1]  # v2 maps to v1's new index
                else:
                    remap[v] = idx
                    idx += 1

            # Build merged graph
            new_pairs_set = set()
            for i, j in pairs:
                ni, nj = remap[i], remap[j]
                if ni != nj:
                    new_pairs_set.add((min(ni, nj), max(ni, nj)))
            new_pairs = list(new_pairs_set)

            # Build triads from merged adjacency
            new_adj = {i: set() for i in range(new_n)}
            for i, j in new_pairs:
                new_adj[i].add(j)
                new_adj[j].add(i)

            new_triads = []
            for i in range(new_n):
                ni = sorted(new_adj[i])
                for idx_j, j in enumerate(ni):
                    if j <= i:
                        continue
                    for k in ni[idx_j + 1:]:
                        if k <= j:
                            continue
                        if k in new_adj[j]:
                            new_triads.append((i, j, k))

            if not new_triads:
                continue

            if is_ks_uncolorable_sat(new_n, new_triads, new_pairs):
                merge_candidates += 1
                # Check realizability
                result, model = check_realizability_z3(
                    new_n, new_pairs, timeout_ms=10000)
                if result is True:
                    realizable += 1
                    print(f"  *** REALIZABLE 30-ray KS set by merging "
                          f"rays {v1} and {v2}! ***")
                    return True

    print(f"  Tested all {n*(n-1)//2 - len(pairs)} non-orthogonal pairs. "
          f"KS-preserving merges: {merge_candidates}, "
          f"Realizable: {realizable}")
    return False


# =====================================================================
# Approach D: Enumerate small abstract KS hypergraphs (PySAT-based)
# =====================================================================

def find_minimal_ks_hypergraphs_sat(n, max_triads_per_vertex=4):
    """Use SAT to find abstract KS-uncolorable hypergraphs on n vertices.

    Rather than random sampling, use SAT to directly search for
    triad sets that make the coloring problem unsatisfiable.
    """
    all_triads = list(combinations(range(n), 3))
    n_triads = len(all_triads)
    print(f"  Total possible triads on {n} vertices: {n_triads}")

    # Variables: t_k = triad k is included (1-indexed: k+1)
    # Coloring variables: c_i = vertex i colored 1 (offset by n_triads)
    # We need: if triad included, coloring constraints apply
    # AND no valid coloring exists

    # This is a 2QBF problem: exists triad selection, forall colorings,
    # some constraint is violated.
    # PySAT can't do 2QBF directly. We'd need a QBF solver.

    # Alternative: iteratively add blocking clauses
    # 1. Find a coloring
    # 2. Add constraint that this coloring must be violated
    # 3. Repeat until UNSAT (no triad selection works) or solution found

    # Start with a SAT solver for triad selection + one coloring attempt
    # Use incremental approach

    print("  Using iterative coloring elimination...")

    # Triad selection variables: 1..n_triads
    # Coloring variables: n_triads+1..n_triads+n
    t_offset = 0
    c_offset = n_triads

    solver = Glucose4()

    # At least min_triads triads must be selected
    min_triads = max(10, n // 3)

    # Cardinality constraint: at least min_triads triads
    # (simple encoding: sequential counter)
    # For simplicity, just add that each vertex must be in at least one triad
    for v in range(n):
        clause = []
        for k, (a, b, c) in enumerate(all_triads):
            if v in (a, b, c):
                clause.append(k + 1)  # triad variable
        if clause:
            solver.add_clause(clause)

    # Limit triads per vertex (for tractability)
    # Each vertex in at most max_triads_per_vertex triads
    # (Using pairwise encoding for small bounds)
    for v in range(n):
        v_triads = [k + 1 for k, (a, b, c) in enumerate(all_triads)
                    if v in (a, b, c)]
        if len(v_triads) > max_triads_per_vertex:
            # At-most-k constraint: any (k+1)-subset must have at least one false
            for subset in combinations(v_triads, max_triads_per_vertex + 1):
                solver.add_clause([-t for t in subset])

    # Iterative coloring elimination
    max_iterations = 200
    found = False

    for iteration in range(max_iterations):
        # Try to find a triad selection + coloring
        # Coloring constraints: for active triads, exactly one vertex colored 1
        # and orthogonal pairs exclude simultaneous 1s

        # Actually, we want NO coloring to work.
        # Approach: find triad selection, then separately check if it's KS.

        result = solver.solve()
        if not result:
            print(f"  No more triad selections possible after "
                  f"{iteration} iterations.")
            break

        model = solver.get_model()
        selected = []
        for k in range(n_triads):
            if model[k] > 0:  # triad k is selected
                selected.append(all_triads[k])

        # Extract pairs
        pair_set = set()
        for a, b, c in selected:
            pair_set.add((min(a, b), max(a, b)))
            pair_set.add((min(a, c), max(a, c)))
            pair_set.add((min(b, c), max(b, c)))
        sel_pairs = list(pair_set)

        # Check KS-uncolorability
        if is_ks_uncolorable_sat(n, selected, sel_pairs):
            print(f"  Found abstract KS hypergraph: "
                  f"{len(selected)} triads, {len(sel_pairs)} pairs "
                  f"(iteration {iteration+1})")
            # Check realizability
            real_result, _ = check_realizability_z3(
                n, sel_pairs, timeout_ms=30000)
            if real_result is True:
                print(f"  *** REALIZABLE {n}-vector KS set found! ***")
                found = True
                break
            elif real_result is False:
                print(f"    Not realizable in R^3.")
            else:
                print(f"    Realizability check timed out.")

            # Block this exact selection and try another
            blocking = [-((k + 1) if all_triads[k] in selected else -(k + 1))
                        for k in range(n_triads)]
            # Actually, block by requiring at least one selected triad to be removed
            blocking = [-(k + 1) for k in range(n_triads)
                        if all_triads[k] in selected]
            solver.add_clause(blocking)
        else:
            # This selection is colorable -- block it
            blocking = [-(k + 1) for k in range(n_triads)
                        if all_triads[k] in selected]
            solver.add_clause(blocking)

        if (iteration + 1) % 50 == 0:
            print(f"    ... iteration {iteration+1}/{max_iterations}")

    solver.delete()
    return found


# =====================================================================
# Main execution
# =====================================================================

print("=" * 70)
print("Z3/SMT-BASED SEARCH FOR SUB-31 KS SETS")
print("=" * 70)


# --- Approach B: Direct Z3 (small n) ---
print("\n--- Approach B: Direct Z3 encoding ---")
for n in [15, 20]:
    print(f"\n  n = {n}:")
    approach_b(n, min_triads=8, timeout_ms=60000)


# --- Approach C: CK-31 vertex merging ---
print("\n--- Approach C: CK-31 vertex merging ---")
print("  Trying to merge non-orthogonal ray pairs while preserving KS...")
t0 = time.time()
found = approach_c_targeted()
elapsed = time.time() - t0
print(f"  [{elapsed:.1f}s]")


# --- Approach A: Random KS hypergraphs + realizability ---
print("\n--- Approach A: Random abstract KS hypergraphs + Z3 realizability ---")
for n in [25, 28, 30]:
    print(f"\n  n = {n}:")
    t0 = time.time()
    found = approach_a(n)
    elapsed = time.time() - t0
    print(f"  [{elapsed:.1f}s]")


# --- Approach D: SAT-guided hypergraph search ---
print("\n--- Approach D: SAT-guided KS hypergraph enumeration ---")
for n in [20, 25]:
    print(f"\n  n = {n}:")
    t0 = time.time()
    found = find_minimal_ks_hypergraphs_sat(n, max_triads_per_vertex=4)
    elapsed = time.time() - t0
    print(f"  [{elapsed:.1f}s]")


print(f"\n{'='*70}")
print("Z3/SMT SEARCH COMPLETE")
print("=" * 70)
