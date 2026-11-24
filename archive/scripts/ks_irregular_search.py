"""
ks_irregular_search.py — Search for irregular KS sets with n < 31
====================================================================

Path D: Generate random abstract KS hypergraphs (no algebraic bias),
test uncolorability via SAT, then test R^3 realizability numerically.

The goal: find a KS set that our algebraic alphabet methods would miss.
If one exists, it won't have the symmetry/regularity of known sets.

Strategy:
  Phase 1: Generate random uncolorable 3-uniform hypergraphs
           (purely combinatorial — no geometry yet)
  Phase 2: Test realizability in R^3 via constrained optimization
           (can these orthogonality constraints be satisfied by real vectors?)

Based on: arXiv:2511.18538 survey recommendations for search beyond
algebraic methods.

Requires: pip install python-sat scipy numpy
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

import random
import time
import numpy as np
from itertools import combinations
from math import gcd

try:
    from pysat.solvers import Glucose4
except ImportError:
    print("ERROR: pip install python-sat")
    sys.exit(1)

from scipy.optimize import minimize as scipy_minimize

random.seed(42)
np.random.seed(42)


# =====================================================================
# Phase 1: Abstract KS hypergraph generation + SAT
# =====================================================================

def is_uncolorable(n, pairs, triads):
    """Test KS-uncolorability via SAT. UNSAT = no valid coloring = KS set."""
    clauses = []
    triad_pair_set = set()

    for a, b, c in triads:
        A, B, C = a + 1, b + 1, c + 1
        clauses.append([A, B, C])       # at least one green
        clauses.append([-A, -B])        # pairwise at most one
        clauses.append([-A, -C])
        clauses.append([-B, -C])
        for x, y in combinations([a, b, c], 2):
            triad_pair_set.add((min(x, y), max(x, y)))

    for a, b in pairs:
        key = (min(a, b), max(a, b))
        if key not in triad_pair_set:
            clauses.append([-(a + 1), -(b + 1)])

    with Glucose4() as solver:
        for c in clauses:
            solver.add_clause(c)
        return not solver.solve()


def generate_random_hypergraph(n, target_triads, target_extra_pairs):
    """
    Generate a random 3-uniform hypergraph with controlled density.

    Returns (triads, all_pairs) or None if construction fails.
    Ensures every vertex is in at least one triad.
    """
    vertices = list(range(n))

    # Generate random triads
    triads = []
    triad_set = set()
    covered = set()

    # First, ensure coverage: every vertex in at least one triad
    uncovered = set(vertices)
    attempts = 0
    while uncovered and attempts < 1000:
        # Pick one uncovered vertex + two random others
        v = random.choice(list(uncovered))
        others = [x for x in vertices if x != v]
        if len(others) < 2:
            break
        b, c = sorted(random.sample(others, 2))
        a = v
        triple = tuple(sorted([a, b, c]))
        if triple not in triad_set:
            triad_set.add(triple)
            triads.append(triple)
            covered.update(triple)
            uncovered -= set(triple)
        attempts += 1

    if uncovered:
        return None  # failed to cover all vertices

    # Add more triads up to target
    attempts = 0
    while len(triads) < target_triads and attempts < 5000:
        triple = tuple(sorted(random.sample(vertices, 3)))
        if triple not in triad_set:
            triad_set.add(triple)
            triads.append(triple)
        attempts += 1

    # Extract pairs from triads
    triad_pairs = set()
    for a, b, c in triads:
        triad_pairs.add((a, b))
        triad_pairs.add((a, c))
        triad_pairs.add((b, c))

    all_pairs = list(triad_pairs)

    # Add extra pairs (not already in triads)
    all_possible = [(i, j) for i in range(n) for j in range(i + 1, n)]
    extra_candidates = [p for p in all_possible if p not in triad_pairs]
    random.shuffle(extra_candidates)

    num_extra = min(target_extra_pairs, len(extra_candidates))
    extra_pairs = extra_candidates[:num_extra]
    all_pairs.extend(extra_pairs)

    return triads, all_pairs


def incremental_uncolorable_search(n, max_attempts=100):
    """
    Build an uncolorable hypergraph incrementally.

    Start with triads, add pairs one at a time until UNSAT.
    This is more efficient than random generation because
    we guide toward uncolorability.
    """
    vertices = list(range(n))

    for attempt in range(max_attempts):
        # Random number of triads (scaled to vertex count)
        # CK-31 has 17 triads for 31 vertices (0.55 ratio)
        num_triads = random.randint(n // 2, n)

        result = generate_random_hypergraph(n, num_triads, 0)
        if result is None:
            continue

        triads, triad_pairs = result

        # Check if triads alone make it uncolorable (unlikely but possible)
        if is_uncolorable(n, triad_pairs, triads):
            return triads, triad_pairs, 0  # extra_pairs=0

        # Add extra pairs incrementally until UNSAT or exhausted
        triad_pair_set = set((min(a, b), max(a, b)) for a, b in triad_pairs)
        all_possible = [(i, j) for i in range(n) for j in range(i + 1, n)]
        extra_candidates = [p for p in all_possible if p not in triad_pair_set]
        random.shuffle(extra_candidates)

        current_pairs = list(triad_pairs)
        extra_count = 0

        for pair in extra_candidates:
            current_pairs.append(pair)
            extra_count += 1

            # Check periodically (every 5 pairs to save SAT calls)
            if extra_count % 5 == 0:
                if is_uncolorable(n, current_pairs, triads):
                    return triads, current_pairs, extra_count

            # Don't add too many — we want sparse, irregular sets
            if extra_count > n * 2:
                break

    return None


# =====================================================================
# Phase 2: R^3 Realizability testing
# =====================================================================

def test_realizability(n, pairs, triads, num_starts=20, tol=1e-10):
    """
    Test whether abstract orthogonality constraints can be realized in R^3.

    For each triad (a,b,c): v_a, v_b, v_c must be mutually orthogonal
    For each pair (a,b): v_a, v_b must be orthogonal
    All vectors on S^2 (unit length).

    Returns (success, vectors, residual) where success means all
    orthogonality constraints are satisfied to within tolerance.
    """
    # Objective: minimize sum of squared dot products for all pairs
    all_pair_set = set()
    for a, b, c in triads:
        all_pair_set.add((min(a, b), max(a, b)))
        all_pair_set.add((min(a, c), max(a, c)))
        all_pair_set.add((min(b, c), max(b, c)))
    for a, b in pairs:
        all_pair_set.add((min(a, b), max(a, b)))

    pair_list = list(all_pair_set)
    num_pairs = len(pair_list)

    def objective(x):
        """Sum of squared dot products for all orthogonality constraints."""
        vecs = x.reshape(n, 3)
        # Normalize to unit vectors
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        norms = np.maximum(norms, 1e-12)
        vecs = vecs / norms

        total = 0.0
        for i, j in pair_list:
            dot = np.dot(vecs[i], vecs[j])
            total += dot ** 2

        # Penalty for non-unit vectors (soft constraint)
        for k in range(n):
            norm_k = np.linalg.norm(x[3*k:3*k+3])
            total += 10.0 * (norm_k - 1.0) ** 2

        return total

    def objective_with_grad(x):
        """Objective with analytical gradient for efficiency."""
        vecs = x.reshape(n, 3)
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        norms = np.maximum(norms, 1e-12)
        unit_vecs = vecs / norms

        total = 0.0
        grad = np.zeros_like(vecs)

        for i, j in pair_list:
            dot = np.dot(unit_vecs[i], unit_vecs[j])
            total += dot ** 2
            # Gradient of dot^2 w.r.t. unit vectors
            grad[i] += 2 * dot * unit_vecs[j]
            grad[j] += 2 * dot * unit_vecs[i]

        # Chain rule for normalization: d(v/||v||)/dv = (I - v*v^T/||v||^2)/||v||
        for k in range(n):
            nk = norms[k, 0]
            if nk > 1e-12:
                proj = np.outer(vecs[k], vecs[k]) / (nk ** 2)
                grad[k] = (np.eye(3) - proj) @ grad[k] / nk

        # Unit norm penalty
        for k in range(n):
            nk = np.linalg.norm(x[3*k:3*k+3])
            if nk > 1e-12:
                total += 10.0 * (nk - 1.0) ** 2
                grad[k] += 20.0 * (nk - 1.0) * vecs[k] / nk

        return total, grad.flatten()

    best_residual = float('inf')
    best_vecs = None

    for start in range(num_starts):
        # Random initial unit vectors
        x0 = np.random.randn(n * 3)
        x0 = x0.reshape(n, 3)
        norms = np.linalg.norm(x0, axis=1, keepdims=True)
        x0 = (x0 / norms).flatten()

        result = scipy_minimize(
            objective_with_grad,
            x0,
            jac=True,
            method='L-BFGS-B',
            options={'maxiter': 5000, 'ftol': 1e-15, 'gtol': 1e-12}
        )

        if result.fun < best_residual:
            best_residual = result.fun
            best_vecs = result.x.reshape(n, 3)
            # Normalize
            norms = np.linalg.norm(best_vecs, axis=1, keepdims=True)
            best_vecs = best_vecs / np.maximum(norms, 1e-12)

        # Early exit if perfect
        if result.fun < tol:
            break

    # Verify: check all pairs
    if best_vecs is not None:
        max_dot = 0.0
        for i, j in pair_list:
            dot = abs(np.dot(best_vecs[i], best_vecs[j]))
            max_dot = max(max_dot, dot)

        # Check triads: each should be a complete orthonormal basis
        triad_ok = True
        for a, b, c in triads:
            det = abs(np.linalg.det(best_vecs[[a, b, c]]))
            if det < 0.5:  # should be ~1 for orthonormal basis
                triad_ok = False
                break

        return best_residual < tol and triad_ok, best_vecs, best_residual, max_dot

    return False, None, best_residual, float('inf')


def check_against_known_pools(vectors, tol=0.05):
    """
    Check if a found KS set is actually just a rotation of a known algebraic set.
    Returns True if it matches a known pattern (boring), False if novel.
    """
    if vectors is None:
        return True  # no vectors = not interesting

    n = len(vectors)

    # Check if coordinates are "nearly algebraic" — close to small integers/rationals
    algebraic_count = 0
    total_coords = 0
    for v in vectors:
        for c in v:
            total_coords += 1
            # Check if close to k/d for small k, d
            for d in range(1, 5):
                for k in range(-4, 5):
                    if abs(c - k / d) < tol:
                        algebraic_count += 1
                        break
                else:
                    continue
                break

    algebraic_fraction = algebraic_count / total_coords
    return algebraic_fraction > 0.8  # >80% algebraic = likely known


# =====================================================================
# Main search
# =====================================================================

def main():
    print("=" * 70)
    print("KS IRREGULAR SET SEARCH — Path D (get lucky)")
    print("=" * 70)
    print()
    print("Searching for KS-uncolorable sets with n < 31 vertices")
    print("that don't come from known algebraic pools.")
    print()

    # Statistics
    stats = {
        'trials': 0,
        'abstract_uncolorable': 0,
        'realizable': 0,
        'novel': 0,
    }

    t_start = time.time()
    report_interval = 1000

    # Search parameters
    n_values = [25, 26, 27, 28, 29, 30]
    max_trials = 10_000_000  # adjust based on patience

    # Phase 1: Bulk abstract search
    # CK-31 reference: n=31, t=17, p=71 (51 triad-pairs + 20 extra)
    # We want SPARSE graphs — just barely uncolorable, like CK-31
    print("PHASE 1: Abstract uncolorable hypergraph search")
    print("  Target: sparse, barely-uncolorable graphs (CK-31-like density)")
    print("-" * 50)

    for trial in range(max_trials):
        stats['trials'] += 1
        n = random.choice(n_values)

        # SPARSE parameters tuned to CK-31 density
        # CK-31: triads/n = 0.55, pairs/n = 2.29
        # We want similar density — just enough to be uncolorable
        num_triads = random.randint(max(n // 3, 8), n // 2 + 3)
        num_extra = random.randint(0, n // 2)

        result = generate_random_hypergraph(n, num_triads, num_extra)
        if result is None:
            continue

        triads, all_pairs = result

        if is_uncolorable(n, all_pairs, triads):
            stats['abstract_uncolorable'] += 1

            # Phase 2: Test realizability
            success, vecs, residual, max_dot = test_realizability(
                n, all_pairs, triads, num_starts=10
            )

            elapsed = time.time() - t_start
            print(f"\n  [Trial {trial+1}] UNCOLORABLE n={n}, "
                  f"t={len(triads)}, p={len(all_pairs)}, "
                  f"residual={residual:.2e}, max_dot={max_dot:.2e}")

            if success:
                stats['realizable'] += 1
                is_known = check_against_known_pools(vecs)

                if is_known:
                    print(f"    -> Realizable but coordinates look algebraic (known pattern)")
                else:
                    stats['novel'] += 1
                    print(f"\n{'*' * 70}")
                    print(f"*** NOVEL KS SET FOUND! n={n} ***")
                    print(f"{'*' * 70}")
                    print(f"Triads: {triads}")
                    print(f"Extra pairs: {len(all_pairs) - 3*len(triads)}")
                    print(f"Residual: {residual:.2e}")
                    print(f"Vectors:")
                    for i, v in enumerate(vecs):
                        print(f"  v[{i}] = ({v[0]:.10f}, {v[1]:.10f}, {v[2]:.10f})")

                    # Save to file
                    fname = f"irregular_ks_{n}_{trial}.txt"
                    with open(fname, 'w') as f:
                        f.write(f"n={n}, triads={len(triads)}, pairs={len(all_pairs)}\n")
                        f.write(f"Triads: {triads}\n")
                        f.write(f"Pairs: {list(set((min(a,b),max(a,b)) for a,b in all_pairs))}\n")
                        for i, v in enumerate(vecs):
                            f.write(f"v[{i}] = {v[0]:.15f} {v[1]:.15f} {v[2]:.15f}\n")
                    print(f"Saved to {fname}")

            else:
                if residual < 0.01:
                    print(f"    -> Near-realizable (residual {residual:.6f}) — close miss")

        # Progress report
        if (trial + 1) % report_interval == 0:
            elapsed = time.time() - t_start
            rate = stats['trials'] / elapsed
            print(f"\n  Progress: {stats['trials']:,} trials in {elapsed:.1f}s "
                  f"({rate:.0f}/s)")
            print(f"  Abstract uncolorable: {stats['abstract_uncolorable']}")
            print(f"  Realizable: {stats['realizable']}")
            print(f"  Novel: {stats['novel']}")
            if stats['abstract_uncolorable'] > 0:
                print(f"  Uncolorable rate: "
                      f"{stats['abstract_uncolorable']/stats['trials']*100:.4f}%")
            print()

    # Final report
    elapsed = time.time() - t_start
    print("\n" + "=" * 70)
    print("FINAL REPORT")
    print("=" * 70)
    print(f"Total trials: {stats['trials']:,}")
    print(f"Time: {elapsed:.1f}s ({elapsed/3600:.2f} hours)")
    print(f"Rate: {stats['trials']/elapsed:.0f} trials/s")
    print(f"Abstract uncolorable: {stats['abstract_uncolorable']}")
    print(f"Realizable: {stats['realizable']}")
    print(f"Novel: {stats['novel']}")


def phase1b_incremental():
    """
    Alternative: incremental constraint addition.
    More likely to find uncolorable sets but slower per trial.
    """
    print("=" * 70)
    print("PHASE 1B: Incremental uncolorable search")
    print("=" * 70)

    stats = {'attempts': 0, 'found': 0, 'realizable': 0, 'novel': 0}
    t_start = time.time()

    for n in [25, 26, 27, 28, 29, 30]:
        print(f"\nSearching n={n}...")
        for attempt in range(500):
            stats['attempts'] += 1
            result = incremental_uncolorable_search(n, max_attempts=50)

            if result is not None:
                triads, pairs, extra = result
                stats['found'] += 1
                print(f"  Found uncolorable: n={n}, t={len(triads)}, "
                      f"p={len(pairs)}, extra={extra}")

                # Test realizability
                success, vecs, residual, max_dot = test_realizability(
                    n, pairs, triads, num_starts=15
                )
                print(f"    Realizability: success={success}, "
                      f"residual={residual:.2e}, max_dot={max_dot:.2e}")

                if success:
                    stats['realizable'] += 1
                    is_known = check_against_known_pools(vecs)
                    if not is_known:
                        stats['novel'] += 1
                        print(f"\n*** NOVEL KS SET! n={n} ***")
                        for i, v in enumerate(vecs):
                            print(f"  v[{i}] = ({v[0]:.10f}, "
                                  f"{v[1]:.10f}, {v[2]:.10f})")

        elapsed = time.time() - t_start
        print(f"  [{elapsed:.0f}s] attempts={stats['attempts']}, "
              f"found={stats['found']}, "
              f"realizable={stats['realizable']}, "
              f"novel={stats['novel']}")


# =====================================================================
# Phase 3: Perturbation of known KS sets
# =====================================================================

def generate_integer_pool():
    """Generate all 49 projectively distinct rays from {0,+/-1,+/-2}."""
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


def find_ck31_from_pool():
    """Find CK-31 via SAT minimization from the 49-ray integer pool."""
    pool = generate_integer_pool()
    n = len(pool)

    # Build orthogonality graph
    pairs = []
    adj = {i: set() for i in range(n)}
    for i in range(n):
        for j in range(i + 1, n):
            if sum(a * b for a, b in zip(pool[i], pool[j])) == 0:
                pairs.append((i, j))
                adj[i].add(j)
                adj[j].add(i)

    triads = []
    for i in range(n):
        for j in adj[i]:
            if j > i:
                for k in adj[i] & adj[j]:
                    if k > j:
                        triads.append((i, j, k))

    # Verify pool is uncolorable
    assert is_uncolorable(n, pairs, triads), "Integer pool should be uncolorable!"

    # Greedy minimize: remove rays one at a time
    active = list(range(n))
    random.shuffle(active)

    for ray in list(active):
        candidate = [r for r in active if r != ray]
        # Rebuild for candidate
        c_n = len(candidate)
        remap = {old: new for new, old in enumerate(candidate)}
        c_pairs = [(remap[a], remap[b]) for a, b in pairs
                   if a in remap and b in remap]
        c_triads = [(remap[a], remap[b], remap[c]) for a, b, c in triads
                    if a in remap and b in remap and c in remap]
        if c_triads and is_uncolorable(c_n, c_pairs, c_triads):
            active = candidate

    # Return the minimized set
    ck_vecs = [pool[i] for i in active]
    n_ck = len(ck_vecs)

    # Rebuild graph
    ck_pairs = []
    ck_adj = {i: set() for i in range(n_ck)}
    for i in range(n_ck):
        for j in range(i + 1, n_ck):
            if sum(a * b for a, b in zip(ck_vecs[i], ck_vecs[j])) == 0:
                ck_pairs.append((i, j))
                ck_adj[i].add(j)
                ck_adj[j].add(i)

    ck_triads = []
    for i in range(n_ck):
        for j in ck_adj[i]:
            if j > i:
                for k in ck_adj[i] & ck_adj[j]:
                    if k > j:
                        ck_triads.append((i, j, k))

    return n_ck, ck_pairs, ck_triads, ck_adj, ck_vecs


def get_ck31_graph():
    """Get CK-31 graph via SAT minimization from integer pool."""
    return find_ck31_from_pool()


def perturb_graph(n, pairs, triads, adj, operation):
    """
    Perturb a KS graph. Returns new (n, pairs, triads, adj) or None.

    Operations:
      'remove_vertex': Remove one vertex, reducing n by 1
      'swap_triad': Remove one triad, add a different one
      'add_pair': Add an extra orthogonality pair
      'remove_pair': Remove an extra pair (not in any triad)
      'merge_vertices': Identify two non-adjacent vertices
    """
    if operation == 'remove_vertex':
        # Remove a random vertex
        v = random.randint(0, n - 1)
        # Remap remaining vertices to 0..n-2
        remap = {}
        idx = 0
        for i in range(n):
            if i != v:
                remap[i] = idx
                idx += 1
        new_n = n - 1
        new_pairs = []
        for a, b in pairs:
            if a != v and b != v:
                new_pairs.append((remap[a], remap[b]))
        new_triads = []
        for a, b, c in triads:
            if a != v and b != v and c != v:
                new_triads.append((remap[a], remap[b], remap[c]))
        if not new_triads:
            return None
        new_adj = {i: set() for i in range(new_n)}
        for a, b in new_pairs:
            new_adj[a].add(b)
            new_adj[b].add(a)
        return new_n, new_pairs, new_triads, new_adj

    elif operation == 'swap_triad':
        if not triads:
            return None
        # Remove a random triad
        idx = random.randint(0, len(triads) - 1)
        removed = triads[idx]
        new_triads = [t for i, t in enumerate(triads) if i != idx]
        # Add a random new triad
        attempts = 0
        while attempts < 200:
            t = tuple(sorted(random.sample(range(n), 3)))
            if t not in set(map(tuple, new_triads)):
                new_triads.append(t)
                break
            attempts += 1
        # Recompute pairs from triads + existing extra pairs
        triad_pair_set = set()
        for a, b, c in new_triads:
            triad_pair_set.add((min(a, b), max(a, b)))
            triad_pair_set.add((min(a, c), max(a, c)))
            triad_pair_set.add((min(b, c), max(b, c)))
        # Keep extra pairs that weren't from the removed triad
        removed_pairs = set()
        a, b, c = removed
        removed_pairs.add((min(a, b), max(a, b)))
        removed_pairs.add((min(a, c), max(a, c)))
        removed_pairs.add((min(b, c), max(b, c)))
        extra_pairs = [(a, b) for a, b in pairs
                       if (min(a, b), max(a, b)) not in triad_pair_set
                       and (min(a, b), max(a, b)) not in removed_pairs]
        new_pairs = list(triad_pair_set) + extra_pairs
        new_adj = {i: set() for i in range(n)}
        for a, b in new_pairs:
            new_adj[a].add(b)
            new_adj[b].add(a)
        return n, new_pairs, new_triads, new_adj

    elif operation == 'merge_vertices':
        if n <= 3:
            return None
        # Pick two non-adjacent vertices
        non_adj = [(i, j) for i in range(n) for j in range(i + 1, n)
                   if j not in adj[i]]
        if not non_adj:
            return None
        u, v = random.choice(non_adj)
        # Merge v into u: remap v -> u, shift higher indices down
        remap = {}
        idx = 0
        for i in range(n):
            if i == v:
                remap[i] = remap[u]  # v maps to u's new index
            else:
                remap[i] = idx
                idx += 1
        new_n = n - 1
        new_pair_set = set()
        for a, b in pairs:
            ra, rb = remap[a], remap[b]
            if ra != rb:
                new_pair_set.add((min(ra, rb), max(ra, rb)))
        new_pairs = list(new_pair_set)
        new_triad_set = set()
        for a, b, c in triads:
            ra, rb, rc = remap[a], remap[b], remap[c]
            if ra != rb and ra != rc and rb != rc:
                new_triad_set.add(tuple(sorted([ra, rb, rc])))
        new_triads = list(new_triad_set)
        if not new_triads:
            return None
        new_adj = {i: set() for i in range(new_n)}
        for a, b in new_pairs:
            new_adj[a].add(b)
            new_adj[b].add(a)
        return new_n, new_pairs, new_triads, new_adj

    elif operation == 'add_pair':
        non_adj = [(i, j) for i in range(n) for j in range(i + 1, n)
                   if j not in adj[i]]
        if not non_adj:
            return None
        new_pair = random.choice(non_adj)
        new_pairs = pairs + [new_pair]
        new_adj = {i: set(adj[i]) for i in range(n)}
        new_adj[new_pair[0]].add(new_pair[1])
        new_adj[new_pair[1]].add(new_pair[0])
        return n, new_pairs, triads, new_adj

    elif operation == 'remove_pair':
        triad_pair_set = set()
        for a, b, c in triads:
            triad_pair_set.add((min(a, b), max(a, b)))
            triad_pair_set.add((min(a, c), max(a, c)))
            triad_pair_set.add((min(b, c), max(b, c)))
        extra = [p for p in pairs if (min(p[0], p[1]), max(p[0], p[1]))
                 not in triad_pair_set]
        if not extra:
            return None
        to_remove = random.choice(extra)
        new_pairs = [p for p in pairs if p != to_remove]
        new_adj = {i: set() for i in range(n)}
        for a, b in new_pairs:
            new_adj[a].add(b)
            new_adj[b].add(a)
        return n, new_pairs, triads, new_adj

    return None


def phase3_perturbation():
    """
    Phase 3: Start from CK-31, perturb the graph structure.

    Strategy: Apply random graph operations to CK-31 and test if
    the result is (a) still uncolorable and (b) realizable with
    fewer vertices or different structure.

    This searches NEAR known solutions rather than randomly,
    which is more likely to find something if irregular KS sets
    exist close to algebraic ones.
    """
    print("=" * 70)
    print("PHASE 3: Graph perturbation from CK-31")
    print("=" * 70)
    print()
    print("Starting from CK-31 graph, applying random perturbations,")
    print("testing if perturbed graphs are uncolorable + realizable.")
    print()

    print("Finding CK-31 from integer pool (SAT minimization)...")
    n0, pairs0, triads0, adj0, vecs0 = get_ck31_graph()
    print(f"CK-31 baseline: n={n0}, t={len(triads0)}, p={len(pairs0)}")
    assert is_uncolorable(n0, pairs0, triads0), "CK-31 must be uncolorable!"
    print(f"Verified uncolorable: True")
    print()

    operations = ['remove_vertex', 'swap_triad', 'merge_vertices',
                  'add_pair', 'remove_pair']
    op_weights = [3, 3, 2, 1, 1]  # favor vertex removal and triad swaps

    stats = {
        'trials': 0,
        'valid_perturbations': 0,
        'still_uncolorable': 0,
        'sub31_uncolorable': 0,
        'realizable': 0,
        'near_realizable': 0,
        'best_residual': float('inf'),
        'best_config': None,
    }

    t_start = time.time()
    max_trials = 500_000

    for trial in range(max_trials):
        stats['trials'] += 1

        # Start fresh from CK-31 each time
        n, pairs, triads, adj = n0, list(pairs0), list(triads0), {i: set(adj0[i]) for i in adj0}

        # Apply 1-5 random perturbations
        num_ops = random.randint(1, 5)
        valid = True

        for _ in range(num_ops):
            op = random.choices(operations, weights=op_weights, k=1)[0]
            result = perturb_graph(n, pairs, triads, adj, op)
            if result is None:
                valid = False
                break
            n, pairs, triads, adj = result

        if not valid or not triads:
            continue

        stats['valid_perturbations'] += 1

        # Check uncolorability
        if not is_uncolorable(n, pairs, triads):
            continue

        stats['still_uncolorable'] += 1

        if n < 31:
            stats['sub31_uncolorable'] += 1

            # Test realizability (more starts for promising candidates)
            num_starts = 15 if n <= 28 else 10
            success, vecs, residual, max_dot = test_realizability(
                n, pairs, triads, num_starts=num_starts
            )

            elapsed = time.time() - t_start
            print(f"  [Trial {trial+1}] n={n}, t={len(triads)}, "
                  f"p={len(pairs)}, ops={num_ops}, "
                  f"residual={residual:.2e}, max_dot={max_dot:.2e}")

            if residual < stats['best_residual']:
                stats['best_residual'] = residual
                stats['best_config'] = {
                    'n': n, 'triads': list(triads), 'pairs': list(pairs),
                    'residual': residual, 'max_dot': max_dot
                }

            if residual < 0.1:
                stats['near_realizable'] += 1
                print(f"    *** NEAR-REALIZABLE! residual={residual:.6f}")

            if success:
                stats['realizable'] += 1
                is_known = check_against_known_pools(vecs)
                print(f"\n{'*' * 70}")
                print(f"*** REALIZABLE SUB-31 KS SET! n={n} ***")
                print(f"*** Novel: {not is_known} ***")
                print(f"{'*' * 70}")
                for i, v in enumerate(vecs):
                    print(f"  v[{i}] = ({v[0]:.10f}, {v[1]:.10f}, {v[2]:.10f})")
                fname = f"perturbed_ks_{n}_{trial}.txt"
                with open(fname, 'w') as f:
                    f.write(f"n={n}, triads={len(triads)}, pairs={len(pairs)}\n")
                    f.write(f"Triads: {triads}\n")
                    f.write(f"Pairs: {pairs}\n")
                    if vecs is not None:
                        for i, v in enumerate(vecs):
                            f.write(f"v[{i}] = {v[0]:.15f} {v[1]:.15f} {v[2]:.15f}\n")
                print(f"Saved to {fname}")

        # Progress report
        if (trial + 1) % 5000 == 0:
            elapsed = time.time() - t_start
            rate = stats['trials'] / elapsed
            print(f"\n  Progress: {stats['trials']:,} trials in {elapsed:.1f}s "
                  f"({rate:.0f}/s)")
            print(f"  Valid perturbations: {stats['valid_perturbations']}")
            print(f"  Still uncolorable: {stats['still_uncolorable']}")
            print(f"  Sub-31 uncolorable: {stats['sub31_uncolorable']}")
            print(f"  Near-realizable (res<0.1): {stats['near_realizable']}")
            print(f"  Realizable: {stats['realizable']}")
            print(f"  Best residual: {stats['best_residual']:.4e}")
            if stats['best_config']:
                bc = stats['best_config']
                print(f"  Best config: n={bc['n']}, t={len(bc['triads'])}, "
                      f"p={len(bc['pairs'])}")
            print()

    # Final report
    elapsed = time.time() - t_start
    print("\n" + "=" * 70)
    print("PHASE 3 FINAL REPORT")
    print("=" * 70)
    print(f"Total trials: {stats['trials']:,}")
    print(f"Time: {elapsed:.1f}s ({elapsed/3600:.2f} hours)")
    print(f"Valid perturbations: {stats['valid_perturbations']}")
    print(f"Still uncolorable: {stats['still_uncolorable']}")
    print(f"Sub-31 uncolorable: {stats['sub31_uncolorable']}")
    print(f"Near-realizable: {stats['near_realizable']}")
    print(f"Realizable: {stats['realizable']}")
    print(f"Best residual: {stats['best_residual']:.6e}")
    if stats['best_config']:
        bc = stats['best_config']
        print(f"Best config: n={bc['n']}, t={len(bc['triads'])}, p={len(bc['pairs'])}")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--incremental':
        phase1b_incremental()
    elif len(sys.argv) > 1 and sys.argv[1] == '--perturb':
        phase3_perturbation()
    else:
        main()
