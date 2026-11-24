"""
ks_csw_extended.py -- CSW invariants on full pools + Weyl-Heisenberg reconstruction
====================================================================================

1. Compute CSW invariants on full (non-minimized) ray pools
2. Reconstruct Cabello's Weyl-Heisenberg 33-set and compute its CSW invariants
3. Compare symmetry-optimized vs cardinality-optimized KS sets
"""

import cmath
import math
import random
import time
import numpy as np
from scipy.optimize import linprog

from ks_complex import (
    generate_eisenstein_rays,
    hermitian_dot,
    canonicalize_complex_ray,
)

from ks_new_islands import (
    generate_rays_from_alphabet,
    hermitian_completion,
    sat_minimize,
)

from ks_sat import is_uncolorable as sat_uncolorable


def build_pairs_triads(rays, tol=1e-9):
    n = len(rays)
    pairs = []
    pair_set = set()
    for i in range(n):
        for j in range(i + 1, n):
            dot = hermitian_dot(rays[i], rays[j])
            if abs(dot) < tol:
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


def get_minimal_ks(rays, pairs, triads, n_trials=300):
    subset, size, _ = sat_minimize(rays, pairs, triads, n_trials=n_trials)
    s = set(subset)
    remap = {old: new for new, old in enumerate(sorted(subset))}
    min_rays = [rays[i] for i in sorted(subset)]
    min_pairs = [(remap[a], remap[b]) for a, b in pairs if a in s and b in s]
    min_triads = [(remap[a], remap[b], remap[c]) for a, b, c in triads
                  if a in s and b in s and c in s]
    return min_rays, min_pairs, min_triads, size


def max_independent_set(n, edges, timeout_sec=60):
    """Branch-and-bound MIS with timeout. Falls back to greedy if timeout hit."""
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)

    # For large graphs, use greedy heuristic only
    if n > 80:
        return _greedy_mis(n, adj)

    best = [0]
    start = time.time()
    timed_out = [False]

    def branch(current_set, candidates):
        if time.time() - start > timeout_sec:
            timed_out[0] = True
            return
        if len(current_set) + len(candidates) <= best[0]:
            return
        if not candidates:
            if len(current_set) > best[0]:
                best[0] = len(current_set)
            return
        v = max(candidates, key=lambda x: len(adj[x] & candidates))
        new_candidates = candidates - adj[v] - {v}
        branch(current_set | {v}, new_candidates)
        if not timed_out[0]:
            branch(current_set, candidates - {v})

    branch(set(), set(range(n)))
    if timed_out[0]:
        greedy = _greedy_mis(n, adj)
        return max(best[0], greedy)
    return best[0]


def _greedy_mis(n, adj, n_trials=200):
    """Greedy MIS heuristic: repeated random greedy with min-degree selection."""
    best = 0
    for _ in range(n_trials):
        available = set(range(n))
        chosen = set()
        order = list(range(n))
        random.shuffle(order)
        for v in order:
            if v in available:
                chosen.add(v)
                available -= adj[v]
                available.discard(v)
        best = max(best, len(chosen))
    return best


def fractional_packing(n, edges, triads=None):
    """
    Fractional packing number alpha*(G) via LP with clique constraints.

    In 3D orthogonality graphs, max clique size = 3 (triads).
    Constraints:
      - x_i + x_j + x_k <= 1 for each triad (3-clique)
      - x_i + x_j <= 1 for each edge NOT in any triad (2-clique)

    If triads is None, falls back to edge-only constraints (less tight).
    """
    if triads:
        triad_edges = set()
        for a, b, c_ in triads:
            triad_edges.add((min(a, b), max(a, b)))
            triad_edges.add((min(a, c_), max(a, c_)))
            triad_edges.add((min(b, c_), max(b, c_)))
        standalone = [(a, b) for a, b in edges
                      if (min(a, b), max(a, b)) not in triad_edges]
        n_constraints = len(triads) + len(standalone)
        c = -np.ones(n)
        A_ub = np.zeros((n_constraints, n))
        b_ub = np.ones(n_constraints)
        for idx, (a, b, c_) in enumerate(triads):
            A_ub[idx, a] = 1.0
            A_ub[idx, b] = 1.0
            A_ub[idx, c_] = 1.0
        offset = len(triads)
        for idx, (a, b) in enumerate(standalone):
            A_ub[offset + idx, a] = 1.0
            A_ub[offset + idx, b] = 1.0
    else:
        n_constraints = len(edges)
        c = -np.ones(n)
        A_ub = np.zeros((n_constraints, n))
        b_ub = np.ones(n_constraints)
        for idx, (i, j) in enumerate(edges):
            A_ub[idx, i] = 1.0
            A_ub[idx, j] = 1.0
    bounds = [(0, 1)] * n
    result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
    return -result.fun if result.success else None


def lovasz_theta(n, edges):
    try:
        import cvxpy as cp
        X = cp.Variable((n, n), symmetric=True)
        constraints = [X >> 0, cp.trace(X) == 1]
        for i, j in edges:
            constraints.append(X[i, j] == 0)
        J = np.ones((n, n))
        prob = cp.Problem(cp.Maximize(cp.trace(J @ X)), constraints)
        prob.solve(solver=cp.SCS, verbose=False, max_iters=10000)
        if prob.status in ['optimal', 'optimal_inaccurate']:
            return prob.value
        return None
    except ImportError:
        return None


def csw_quick(name, n, pairs, triads=None):
    """Compute CSW invariants and return as tuple."""
    t0 = time.time()
    alpha = max_independent_set(n, pairs)
    t1 = time.time()
    alpha_star = fractional_packing(n, pairs, triads=triads)
    theta = lovasz_theta(n, pairs)
    t2 = time.time()
    qc = theta / alpha if (theta and alpha > 0) else 0
    print(f"  {name:<35s}: n={n:3d}  alpha={alpha:3d}  "
          f"theta={theta:7.2f}  alpha*={alpha_star:7.2f}  "
          f"Q/C={qc:.4f}  ({t2-t0:.1f}s)")
    return alpha, theta, alpha_star


# ============================================================
# Weyl-Heisenberg construction for dimension 3
# ============================================================

def build_weyl_heisenberg_set():
    """
    Construct the Weyl-Heisenberg KS set in C^3.

    The WH group for d=3 is generated by:
      X (shift): X|j> = |j+1 mod 3>
      Z (clock): Z|j> = omega^j |j>
    where omega = exp(2*pi*i/3).

    The 9 operators X^a Z^b (a,b in {0,1,2}) each have 3 eigenvectors.
    We collect all distinct eigenvectors (as rays) and their orthogonality structure.
    """
    omega = cmath.exp(2j * cmath.pi / 3)
    d = 3

    # Build X and Z as matrices
    X = np.zeros((d, d), dtype=complex)
    for j in range(d):
        X[(j + 1) % d, j] = 1.0

    Z = np.zeros((d, d), dtype=complex)
    for j in range(d):
        Z[j, j] = omega ** j

    # Generate all 9 WH operators X^a Z^b
    operators = []
    op_labels = []
    for a in range(d):
        for b in range(d):
            # Compute X^a
            Xa = np.linalg.matrix_power(X, a)
            # Compute Z^b
            Zb = np.linalg.matrix_power(Z, b)
            # W = X^a Z^b
            W = Xa @ Zb
            operators.append(W)
            op_labels.append(f"X^{a}Z^{b}")

    # Compute eigenvectors of each operator
    all_rays = []
    ray_set = set()
    bases = []  # Each basis is a list of ray indices

    for op_idx, (W, label) in enumerate(zip(operators, op_labels)):
        eigenvalues, eigenvectors = np.linalg.eigh(W)
        # Note: eigh assumes Hermitian, but WH operators are unitary, not Hermitian
        # Use eig instead for unitary operators
        eigenvalues, eigenvectors = np.linalg.eig(W)

        basis_indices = []
        for k in range(d):
            vec = tuple(eigenvectors[:, k])
            # Canonicalize
            canon = canonicalize_complex_ray(list(vec))
            if canon is not None:
                if canon not in ray_set:
                    ray_set.add(canon)
                    all_rays.append(vec)
                # Find index
                idx = None
                for i, r in enumerate(all_rays):
                    c = canonicalize_complex_ray(list(r))
                    if c == canon:
                        idx = i
                        break
                if idx is not None:
                    basis_indices.append(idx)

        if len(basis_indices) == d:
            bases.append(tuple(sorted(basis_indices)))

    # Deduplicate bases
    bases = list(set(bases))

    print(f"  WH construction: {len(all_rays)} distinct rays, {len(bases)} bases")
    print(f"  Operators: {len(operators)}")

    return all_rays, bases


def build_wh_from_eisenstein():
    """
    Build the WH-33 set by finding the 33-vector, 16-base KS set
    within the Eisenstein pool that has the highest symmetry.

    Strategy: among all distinct 33-sets found by SAT minimization,
    pick the one with the most bases (contexts).
    """
    print("\n  Building WH-like set from Eisenstein pool...")
    rays = generate_eisenstein_rays(max_coeff=1, dim=3, norm_cutoff=3)
    pairs, triads = build_pairs_triads(rays)
    print(f"  Pool: {len(rays)} rays, {len(pairs)} pairs, {len(triads)} triads")

    # Run many trials and track distinct 33-sets
    n = len(rays)
    best_size = n
    distinct_sets = {}

    for trial in range(1000):
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
                s = set(candidate)
                remap = {old: new for new, old in enumerate(sorted(candidate))}
                sp = [(remap[a], remap[b]) for a, b in pairs if a in s and b in s]
                st = [(remap[a], remap[b], remap[c]) for a, b, c in triads
                      if a in s and b in s and c in s]
                if st and sat_uncolorable(len(candidate), sp, st):
                    current = candidate
                    removed = True
                    break

        size = len(current)
        if size <= best_size + 2:
            fs = frozenset(current)
            distinct_sets[fs] = distinct_sets.get(fs, 0) + 1
        if size < best_size:
            best_size = size

    # Get all minimal-size sets
    min_sets = [k for k in distinct_sets if len(k) == best_size]
    print(f"  Found {len(min_sets)} distinct {best_size}-sets")

    # For each, count bases and pick the one with most bases
    best_bases = 0
    best_set = None
    for ms in min_sets:
        s = set(ms)
        remap = {old: new for new, old in enumerate(sorted(ms))}
        st = [(remap[a], remap[b], remap[c]) for a, b, c in triads
              if a in s and b in s and c in s]
        if len(st) > best_bases:
            best_bases = len(st)
            best_set = ms

    # Rebuild for the best set
    s = set(best_set)
    remap = {old: new for new, old in enumerate(sorted(best_set))}
    min_rays = [rays[i] for i in sorted(best_set)]
    min_pairs = [(remap[a], remap[b]) for a, b in pairs if a in s and b in s]
    min_triads = [(remap[a], remap[b], remap[c]) for a, b, c in triads
                  if a in s and b in s and c in s]

    print(f"  Best {best_size}-set: {len(min_triads)} bases (max among all {len(min_sets)} sets)")

    # Also find the one with fewest bases for comparison
    min_bases = min(len([(remap2[a], remap2[b], remap2[c])
                         for a, b, c in triads
                         if a in set(ms2) and b in set(ms2) and c in set(ms2)])
                    for ms2 in min_sets
                    for remap2 in [{old: new for new, old in enumerate(sorted(ms2))}])
    print(f"  Range of bases across {len(min_sets)} sets: {min_bases} to {best_bases}")

    return min_rays, min_pairs, min_triads, best_size


def main():
    random.seed(42)

    print("=" * 70)
    print("CSW EXTENDED: Full Pools + Weyl-Heisenberg Reconstruction")
    print("=" * 70)

    all_results = []

    # ================================================================
    # PART 1: CSW on full (non-minimized) pools
    # ================================================================
    print("\n" + "=" * 70)
    print("PART 1: CSW INVARIANTS ON FULL RAY POOLS")
    print("=" * 70)

    # Integer pool
    int_alph = [complex(x) for x in [0, 1, -1, 2, -2]]
    int_rays = generate_rays_from_alphabet(int_alph)
    int_pairs, int_triads = build_pairs_triads(int_rays)
    a, t, astar = csw_quick("Integer pool", len(int_rays), int_pairs, int_triads)
    all_results.append(("Integer pool", len(int_rays), len(int_triads), a, t, astar))

    # Peres pool
    s2 = math.sqrt(2)
    p_alph = [complex(x) for x in [0, 1, -1, s2, -s2]]
    p_rays = generate_rays_from_alphabet(p_alph)
    p_pairs, p_triads = build_pairs_triads(p_rays)
    a, t, astar = csw_quick("Peres pool", len(p_rays), p_pairs, p_triads)
    all_results.append(("Peres pool", len(p_rays), len(p_triads), a, t, astar))

    # Eisenstein pool
    eis_rays = generate_eisenstein_rays(max_coeff=1, dim=3, norm_cutoff=3)
    eis_pairs, eis_triads = build_pairs_triads(eis_rays)
    a, t, astar = csw_quick("Eisenstein pool", len(eis_rays), eis_pairs, eis_triads)
    all_results.append(("Eisenstein pool", len(eis_rays), len(eis_triads), a, t, astar))

    # Z[sqrt(-2)] pool
    sd2 = cmath.sqrt(-2)
    cq_alph = [0, 1, -1, sd2, -sd2]
    cq_rays = generate_rays_from_alphabet(cq_alph)
    cq_pairs, cq_triads = build_pairs_triads(cq_rays)
    a, t, astar = csw_quick("Z[sqrt(-2)] pool", len(cq_rays), cq_pairs, cq_triads)
    all_results.append(("Z[sqrt(-2)] pool", len(cq_rays), len(cq_triads), a, t, astar))

    # Heegner-7 pool
    gen7 = (1 + cmath.sqrt(-7)) / 2
    h7_alph = [0, 1, -1, gen7, -gen7, gen7.conjugate(), -gen7.conjugate()]
    h7_rays = generate_rays_from_alphabet(h7_alph)
    h7_pairs, h7_triads = build_pairs_triads(h7_rays)
    a, t, astar = csw_quick("Heegner-7 pool", len(h7_rays), h7_pairs, h7_triads)
    all_results.append(("Heegner-7 pool", len(h7_rays), len(h7_triads), a, t, astar))

    # ================================================================
    # PART 2: CSW on minimized sets (for comparison)
    # ================================================================
    print("\n" + "=" * 70)
    print("PART 2: CSW INVARIANTS ON MINIMIZED KS SETS (for comparison)")
    print("=" * 70)

    min_rays, min_pairs, min_triads, size = get_minimal_ks(int_rays, int_pairs, int_triads)
    a, t, astar = csw_quick("Integer min-31", size, min_pairs, min_triads)
    all_results.append(("Integer min-31", size, len(min_triads), a, t, astar))

    min_rays, min_pairs, min_triads, size = get_minimal_ks(p_rays, p_pairs, p_triads)
    a, t, astar = csw_quick("Peres min-33", size, min_pairs, min_triads)
    all_results.append(("Peres min-33", size, len(min_triads), a, t, astar))

    min_rays, min_pairs, min_triads, size = get_minimal_ks(eis_rays, eis_pairs, eis_triads)
    a, t, astar = csw_quick("Eisenstein min-33", size, min_pairs, min_triads)
    all_results.append(("Eisenstein min-33", size, len(min_triads), a, t, astar))

    min_rays, min_pairs, min_triads, size = get_minimal_ks(cq_rays, cq_pairs, cq_triads)
    a, t, astar = csw_quick("Z[sqrt(-2)] min-33", size, min_pairs, min_triads)
    all_results.append(("Z[sqrt(-2)] min-33", size, len(min_triads), a, t, astar))

    min_rays, min_pairs, min_triads, size = get_minimal_ks(h7_rays, h7_pairs, h7_triads)
    a, t, astar = csw_quick("Heegner-7 min-43", size, min_pairs, min_triads)
    all_results.append(("Heegner-7 min-43", size, len(min_triads), a, t, astar))

    # ================================================================
    # PART 3: Weyl-Heisenberg reconstruction
    # ================================================================
    print("\n" + "=" * 70)
    print("PART 3: WEYL-HEISENBERG 33-SET (max symmetry from Eisenstein pool)")
    print("=" * 70)

    # Direct WH construction
    print("\n--- Direct WH eigenvector construction ---")
    wh_rays, wh_bases = build_weyl_heisenberg_set()

    # Find max-bases 33-set from Eisenstein pool
    print("\n--- Max-bases 33-set from Eisenstein pool ---")
    wh_min_rays, wh_min_pairs, wh_min_triads, wh_size = build_wh_from_eisenstein()
    a, t, astar = csw_quick(f"Eisenstein max-bases {wh_size}-set", wh_size, wh_min_pairs)
    all_results.append((f"Eis. max-bases {wh_size}", wh_size, len(wh_min_triads), a, t, astar))

    # Also find min-bases 33-set for contrast
    print("\n--- Min-bases 33-set (for contrast) ---")
    # Already have this from Part 2 (Eisenstein min-33)

    # ================================================================
    # Summary
    # ================================================================
    print("\n\n" + "=" * 70)
    print("SUMMARY: CSW INVARIANTS -- FULL POOLS vs MINIMIZED vs MAX-SYMMETRY")
    print("=" * 70)
    print(f"{'Source':<30s} {'n':>4s} {'bases':>6s} {'alpha':>6s} {'theta':>8s} "
          f"{'alpha*':>8s} {'Q/C':>7s}")
    print("-" * 70)
    for name, n, bases, alpha, theta, alpha_star in all_results:
        qc = theta / alpha if (theta and alpha > 0) else 0
        astar_str = f"{alpha_star:.2f}" if alpha_star else "?"
        theta_str = f"{theta:.2f}" if theta else "?"
        print(f"{name:<30s} {n:4d} {bases:6d} {alpha:6d} {theta_str:>8s} "
              f"{astar_str:>8s} {qc:7.4f}")

    print("\nKey question: Does higher symmetry (more bases) produce")
    print("a larger theta/alpha ratio from the same Eisenstein pool?")


if __name__ == "__main__":
    main()
