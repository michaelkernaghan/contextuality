"""
ks_csw.py -- Cabello-Severini-Winter graph invariants for algebraic islands
=============================================================================

Computes the three CSW invariants for the orthogonality graph of each island's
minimal KS set:

  alpha(G)  = independence number (classical bound)
  theta(G)  = Lovasz theta number (quantum bound, via SDP)
  alpha*(G) = fractional packing number (nonsignaling bound, via LP)

The contextual advantage is theta(G)/alpha(G).
The Bell inequality violation ratio is theta(G)/alpha(G).

Reference: Cabello, Severini, Winter, PRL 112, 040401 (2014)
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


# ============================================================
# Independence number alpha(G) -- exact via branch and bound
# ============================================================

def max_independent_set(n, edges):
    """
    Exact maximum independent set via branch-and-bound.
    For graphs with n <= 55, this is feasible with good pruning.
    """
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)

    best = [0]
    best_set = [[]]

    def bound(candidates):
        """Upper bound: greedy coloring of candidates gives independence bound."""
        return len(candidates)

    def branch(current_set, candidates):
        if len(current_set) + len(candidates) <= best[0]:
            return  # Prune: can't beat best even with all candidates

        if not candidates:
            if len(current_set) > best[0]:
                best[0] = len(current_set)
                best_set[0] = list(current_set)
            return

        # Pick vertex with max degree in subgraph (most constrained first)
        v = max(candidates, key=lambda x: len(adj[x] & candidates))

        # Branch 1: include v
        new_candidates = candidates - adj[v] - {v}
        branch(current_set | {v}, new_candidates)

        # Branch 2: exclude v
        branch(current_set, candidates - {v})

    branch(set(), set(range(n)))
    return best[0], best_set[0]


# ============================================================
# Fractional packing number alpha*(G) -- via LP
# ============================================================

def fractional_packing(n, edges, triads=None):
    """
    alpha*(G) = fractional packing number with clique constraints.

    In 3D orthogonality graphs, max clique size = 3 (triads).
    Constraints:
      - x_i + x_j + x_k <= 1 for each triad (3-clique)
      - x_i + x_j <= 1 for each edge NOT in any triad (2-clique)
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

    if result.success:
        return -result.fun, result.x
    else:
        return None, None


# ============================================================
# Lovasz theta number theta(G) -- via SDP
# ============================================================

def lovasz_theta_sdp(n, edges):
    """
    Compute Lovasz theta via SDP using cvxpy:
    theta(G) = max Tr(J * X) subject to:
        Tr(X) = 1
        X_ij = 0 for all (i,j) in E(G)
        X >= 0 (PSD)
    where J is the all-ones matrix.
    """
    try:
        import cvxpy as cp

        X = cp.Variable((n, n), symmetric=True)
        constraints = [
            X >> 0,  # PSD
            cp.trace(X) == 1,
        ]
        for i, j in edges:
            constraints.append(X[i, j] == 0)

        J = np.ones((n, n))
        objective = cp.Maximize(cp.trace(J @ X))
        prob = cp.Problem(objective, constraints)
        prob.solve(solver=cp.SCS, verbose=False, max_iters=10000)

        if prob.status in ['optimal', 'optimal_inaccurate']:
            return prob.value
        else:
            print(f"    SDP status: {prob.status}")
            return None

    except ImportError:
        return None


def lovasz_theta_approximate(n, edges, rays=None):
    """
    Approximate Lovasz theta using the Schrijver bound or eigenvalue method.

    For the orthogonality graph with known ray vectors, we can compute
    theta directly: theta(G) = max (sum_i (d·v_i)^2) over unit d,
    where v_i are unit vectors assigned to vertices with v_i·v_j = 0 when (i,j) in E.

    For KS orthogonality graphs, the rays themselves provide a valid assignment.
    """
    if rays is not None:
        # Use the actual rays as the orthogonal representation
        # theta >= n * max eigenvalue of the Gram matrix restricted to...
        # Actually, for the orthogonality graph of rays in C^d,
        # the quantum value is simply n/d (for vertex-transitive graphs).
        # More precisely, theta(G) = n/d when the graph is the orthogonality
        # graph of n rays in C^d and the graph is vertex-transitive.
        # For non-vertex-transitive graphs, it's harder.
        pass

    # Eigenvalue bound: theta(G) >= 1 - lambda_max(A) / lambda_min(A)
    # where A is the adjacency matrix
    adj_matrix = np.zeros((n, n))
    for i, j in edges:
        adj_matrix[i, j] = 1
        adj_matrix[j, i] = 1

    eigenvalues = np.linalg.eigvalsh(adj_matrix)
    lambda_max = eigenvalues[-1]
    lambda_min = eigenvalues[0]

    if lambda_min < -1e-10:
        theta_lb = 1 - lambda_max / lambda_min
    else:
        theta_lb = n  # Trivial bound

    return theta_lb


# ============================================================
# Full CSW analysis for an island
# ============================================================

def csw_analysis(name, n, pairs, triads, rays=None):
    """Compute all CSW invariants for an orthogonality graph."""
    print(f"\n{'='*60}")
    print(f"  CSW Analysis: {name}")
    print(f"{'='*60}")
    print(f"  Vertices (rays): {n}")
    print(f"  Edges (orthogonal pairs): {len(pairs)}")
    print(f"  Triads (bases): {len(triads)}")

    # Degree statistics
    deg = [0] * n
    for a, b in pairs:
        deg[a] += 1
        deg[b] += 1
    print(f"  Avg degree: {sum(deg)/n:.1f}")

    # 1. Independence number (classical bound)
    t0 = time.time()
    alpha, alpha_set = max_independent_set(n, pairs)
    t1 = time.time()
    print(f"\n  alpha(G) = {alpha}  (independence number, classical bound)")
    print(f"    Computed in {t1-t0:.2f}s")

    # 2. Fractional packing (nonsignaling bound)
    t0 = time.time()
    alpha_star, x_star = fractional_packing(n, pairs)
    t1 = time.time()
    if alpha_star is not None:
        print(f"  alpha*(G) = {alpha_star:.4f}  (fractional packing, nonsignaling bound)")
        print(f"    Computed in {t1-t0:.2f}s")
        # Show how fractional the solution is
        n_frac = sum(1 for x in x_star if 0.01 < x < 0.99)
        n_int = sum(1 for x in x_star if x > 0.99 or x < 0.01)
        print(f"    Fractional variables: {n_frac}, Integer: {n_int}")
    else:
        print(f"  alpha*(G) = FAILED")
        alpha_star = None

    # 3. Lovasz theta (quantum bound)
    t0 = time.time()
    theta = lovasz_theta_sdp(n, pairs)
    t1 = time.time()
    if theta is not None:
        print(f"  theta(G) = {theta:.4f}  (Lovasz theta, quantum bound)")
        print(f"    Computed in {t1-t0:.2f}s (SDP)")
    else:
        print(f"  theta(G): cvxpy not available, using eigenvalue bound")
        theta_lb = lovasz_theta_approximate(n, pairs, rays)
        print(f"  theta(G) >= {theta_lb:.4f}  (eigenvalue lower bound)")
        theta = theta_lb

    # 4. Summary and ratios
    print(f"\n  CSW Invariant Chain:")
    print(f"    alpha(G) <= theta(G) <= alpha*(G)")
    print(f"    {alpha}      <= {theta:.4f}  <= {alpha_star:.4f}" if alpha_star else
          f"    {alpha}      <= {theta:.4f}")

    if alpha > 0:
        q_advantage = theta / alpha
        print(f"\n  Quantum/Classical ratio: theta/alpha = {q_advantage:.4f}")
        print(f"  Bell inequality violation: {q_advantage:.4f}x classical bound")

    if alpha_star and alpha > 0:
        ns_advantage = alpha_star / alpha
        print(f"  Nonsignaling/Classical ratio: alpha*/alpha = {ns_advantage:.4f}")

    # 5. Verify KS property connection
    # For a KS set, the graph has no valid {0,1} coloring respecting triads.
    # The CSW framework connects this to: quantum value > classical value
    # Specifically, KS-uncolorability implies theta(G) > alpha(G)
    if theta > alpha + 0.01:
        print(f"\n  CSW confirms contextuality: theta > alpha ({theta:.4f} > {alpha})")
    else:
        print(f"\n  NOTE: theta ~ alpha ({theta:.4f} ~ {alpha}), CSW inequality not violated")

    return alpha, theta, alpha_star


def main():
    random.seed(42)

    print("=" * 60)
    print("CABELLO-SEVERINI-WINTER GRAPH INVARIANTS")
    print("FOR ALL ALGEBRAIC ISLANDS")
    print("=" * 60)
    print("\nThe CSW framework maps orthogonality graphs to Bell inequalities:")
    print("  alpha(G)  = classical bound (independence number)")
    print("  theta(G)  = quantum bound (Lovasz theta, SDP)")
    print("  alpha*(G) = nonsignaling bound (fractional packing, LP)")
    print("  Contextual advantage = theta(G) / alpha(G)")

    results = []

    # ---- Island 1: Integer (CK-31) ----
    print("\n\nGenerating Integer island (CK-31)...")
    int_alph = [complex(x) for x in [0, 1, -1, 2, -2]]
    int_rays = generate_rays_from_alphabet(int_alph)
    int_pairs, int_triads = build_pairs_triads(int_rays)
    min_rays, min_pairs, min_triads, size = get_minimal_ks(
        int_rays, int_pairs, int_triads)
    print(f"  Minimal set: {size} vectors, {len(min_triads)} bases")
    a, t, astar = csw_analysis("Integer (CK-31)", size, min_pairs, min_triads, min_rays)
    results.append(("Integer (CK-31)", size, len(min_triads), a, t, astar))

    # ---- Island 2: Peres (sqrt(2)) ----
    print("\n\nGenerating Peres island...")
    s2 = math.sqrt(2)
    p_alph = [complex(x) for x in [0, 1, -1, s2, -s2]]
    p_rays = generate_rays_from_alphabet(p_alph)
    p_pairs, p_triads = build_pairs_triads(p_rays)
    min_rays, min_pairs, min_triads, size = get_minimal_ks(
        p_rays, p_pairs, p_triads)
    print(f"  Minimal set: {size} vectors, {len(min_triads)} bases")
    a, t, astar = csw_analysis("Peres (sqrt(2))", size, min_pairs, min_triads, min_rays)
    results.append(("Peres (sqrt(2))", size, len(min_triads), a, t, astar))

    # ---- Island 3: Eisenstein ----
    print("\n\nGenerating Eisenstein island...")
    eis_rays = generate_eisenstein_rays(max_coeff=1, dim=3, norm_cutoff=3)
    eis_pairs, eis_triads = build_pairs_triads(eis_rays)
    min_rays, min_pairs, min_triads, size = get_minimal_ks(
        eis_rays, eis_pairs, eis_triads)
    print(f"  Minimal set: {size} vectors, {len(min_triads)} bases")
    a, t, astar = csw_analysis("Eisenstein", size, min_pairs, min_triads, min_rays)
    results.append(("Eisenstein", size, len(min_triads), a, t, astar))

    # ---- Island 4: Z[sqrt(-2)] ----
    print("\n\nGenerating Z[sqrt(-2)] island...")
    sd2 = cmath.sqrt(-2)
    cq_alph = [0, 1, -1, sd2, -sd2]
    cq_rays = generate_rays_from_alphabet(cq_alph)
    cq_pairs, cq_triads = build_pairs_triads(cq_rays)
    min_rays, min_pairs, min_triads, size = get_minimal_ks(
        cq_rays, cq_pairs, cq_triads)
    print(f"  Minimal set: {size} vectors, {len(min_triads)} bases")
    a, t, astar = csw_analysis("Z[sqrt(-2)]", size, min_pairs, min_triads, min_rays)
    results.append(("Z[sqrt(-2)]", size, len(min_triads), a, t, astar))

    # ---- Island 5: Heegner-7 ----
    print("\n\nGenerating Heegner-7 island...")
    gen7 = (1 + cmath.sqrt(-7)) / 2
    h7_alph = [0, 1, -1, gen7, -gen7, gen7.conjugate(), -gen7.conjugate()]
    h7_rays = generate_rays_from_alphabet(h7_alph)
    h7_pairs, h7_triads = build_pairs_triads(h7_rays)
    min_rays, min_pairs, min_triads, size = get_minimal_ks(
        h7_rays, h7_pairs, h7_triads)
    print(f"  Minimal set: {size} vectors, {len(min_triads)} bases")
    a, t, astar = csw_analysis("Heegner-7", size, min_pairs, min_triads, min_rays)
    results.append(("Heegner-7", size, len(min_triads), a, t, astar))

    # ---- Island 6: Golden ----
    print("\n\nGenerating Golden island...")
    phi = (1 + math.sqrt(5)) / 2
    g_alph = [complex(x) for x in [0, 1, -1, phi, -phi]]
    g_rays_raw = generate_rays_from_alphabet(g_alph)
    g_rays = hermitian_completion(g_rays_raw)
    g_pairs, g_triads = build_pairs_triads(g_rays)
    if g_triads and sat_uncolorable(len(g_rays), g_pairs, g_triads):
        min_rays, min_pairs, min_triads, size = get_minimal_ks(
            g_rays, g_pairs, g_triads, n_trials=100)
        print(f"  Minimal set: {size} vectors, {len(min_triads)} bases")
        a, t, astar = csw_analysis("Golden", size, min_pairs, min_triads, min_rays)
        results.append(("Golden", size, len(min_triads), a, t, astar))

    # ================================================================
    # Summary Table
    # ================================================================
    print("\n\n" + "=" * 70)
    print("SUMMARY: CSW INVARIANTS ACROSS ALL ISLANDS")
    print("=" * 70)
    print(f"{'Island':<20s} {'n':>4s} {'bases':>6s} {'alpha':>6s} {'theta':>8s} "
          f"{'alpha*':>8s} {'Q/C':>6s}")
    print("-" * 70)
    for name, n, bases, alpha, theta, alpha_star in results:
        qc = theta / alpha if alpha > 0 else 0
        astar_str = f"{alpha_star:.2f}" if alpha_star else "?"
        print(f"{name:<20s} {n:4d} {bases:6d} {alpha:6d} {theta:8.2f} "
              f"{astar_str:>8s} {qc:6.3f}")

    print("\nInterpretation:")
    print("  alpha(G) = max rays assignable 'yes' classically")
    print("  theta(G) = max quantum expectation value")
    print("  alpha*(G) = max nonsignaling expectation")
    print("  Q/C = theta/alpha = quantum advantage ratio")
    print("  Q/C > 1 implies quantum contextuality / Bell violation")


if __name__ == "__main__":
    main()
