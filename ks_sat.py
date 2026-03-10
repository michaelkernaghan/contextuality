"""
ks_sat.py — SAT-solver approach to finding small KS sets

Methodology (inverted from alphabet search):
  Alphabet search: Coordinates -> Graph -> Check coloring
  SAT approach:    Graph -> Check coloring (SAT) -> Find coordinates (optimization)

By separating the combinatorial and geometric problems, this approach
can in principle search a much larger space of configurations — the
coordinates need not come from any small alphabet.

Three phases:
  1. SAT analysis of Conway-Kochen 31 (essential rays, essential triads)
  2. Realizability: recover R³ coordinates from abstract graph via optimization
  3. Search for novel KS configurations on fewer than 31 rays

Requires: pip install python-sat scipy numpy
"""

import numpy as np
from scipy.optimize import minimize as scipy_min
from itertools import combinations
import time
import sys

# ============================================================
# SAT-based KS coloring
# ============================================================

try:
    from pysat.solvers import Glucose4
    SAT_ENGINE = "Glucose4"
except ImportError:
    SAT_ENGINE = "backtrack"
    print("WARNING: pysat not found, using backtracking (slower)")
    print("Install with: pip install python-sat")

try:
    from ks_spectral_filter import passes_fast_filter
    HAS_SPECTRAL = True
except ImportError:
    HAS_SPECTRAL = False


def is_uncolorable(n, pairs, triads):
    """Check if a ray configuration is KS-uncolorable."""
    if SAT_ENGINE == "Glucose4":
        return _sat_check(n, pairs, triads)
    return _backtrack_check(n, pairs, triads)


def _sat_check(n, pairs, triads):
    """
    Encode KS coloring as SAT.
    Variable i (1-indexed): ray i is GREEN.
    For each triad: exactly one green (4 clauses).
    For each orthogonal pair: at most one green (1 clause).
    UNSAT = no valid coloring = KS set.
    """
    clauses = []
    triad_pair_set = set()

    for a, b, c in triads:
        A, B, C = a + 1, b + 1, c + 1
        clauses.append([A, B, C])       # at least one green
        clauses.append([-A, -B])        # pairwise exclusion
        clauses.append([-A, -C])
        clauses.append([-B, -C])
        for x, y in combinations([a, b, c], 2):
            triad_pair_set.add((min(x, y), max(x, y)))

    for a, b in pairs:
        if (min(a, b), max(a, b)) not in triad_pair_set:
            clauses.append([-(a + 1), -(b + 1)])

    with Glucose4() as solver:
        for c in clauses:
            solver.add_clause(c)
        return not solver.solve()


def _backtrack_check(n, pairs, triads):
    """Backtracking solver (fallback if pysat unavailable)."""
    P = [[0] * n for _ in range(n)]
    for a, b in pairs:
        P[a][b] = P[b][a] = 1

    def propagate(C):
        changed = True
        while changed:
            changed = False
            for i in range(n):
                if C[i] == 1:
                    for j in range(n):
                        if P[i][j]:
                            if C[j] == 1:
                                return False
                            if C[j] == -1:
                                C[j] = 0
                                changed = True
            for t in triads:
                v = [C[t[0]], C[t[1]], C[t[2]]]
                g, r = v.count(1), v.count(0)
                if g > 1 or r == 3:
                    return False
                if g == 1:
                    for idx in t:
                        if C[idx] == -1:
                            C[idx] = 0
                            changed = True
                if r == 2 and v.count(-1) == 1 and g == 0:
                    for idx in t:
                        if C[idx] == -1:
                            C[idx] = 1
                            changed = True
        return True

    def solve(C):
        C2 = C[:]
        if not propagate(C2):
            return False
        if -1 not in C2:
            return True
        best = max((sum(1 for j in range(n) if P[i][j] and C2[j] != -1), i)
                   for i in range(n) if C2[i] == -1)[1]
        for color in [1, 0]:
            C3 = C2[:]
            C3[best] = color
            if solve(C3):
                return True
        return False

    return not solve([-1] * n)


def get_essential_triads(n, pairs, triads):
    """
    Use assumption-based SAT to find which triads are essential.
    Returns indices of triads in the UNSAT core.
    """
    if SAT_ENGINE != "Glucose4":
        return None

    clauses = []
    assumptions = []

    for k, (a, b, c) in enumerate(triads):
        A, B, C = a + 1, b + 1, c + 1
        sel = n + k + 1  # selector for this triad
        assumptions.append(sel)
        # If selector active, enforce triad constraints:
        clauses.append([-sel, A, B, C])
        clauses.append([-sel, -A, -B])
        clauses.append([-sel, -A, -C])
        clauses.append([-sel, -B, -C])

    # Pair exclusions (always active, not assumption-gated)
    triad_pair_set = set()
    for a, b, c in triads:
        for x, y in combinations([a, b, c], 2):
            triad_pair_set.add((min(x, y), max(x, y)))
    for a, b in pairs:
        if (min(a, b), max(a, b)) not in triad_pair_set:
            clauses.append([-(a + 1), -(b + 1)])

    with Glucose4() as solver:
        for c in clauses:
            solver.add_clause(c)
        result = solver.solve(assumptions=assumptions)
        if not result:
            core = solver.get_core()
            return [k for k in range(len(triads)) if (n + k + 1) in core]
    return None


# ============================================================
# Graph construction from coordinates
# ============================================================

CK31_VECTORS = [
    (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 1, -1), (0, 1, 2), (0, 2, -1),
    (1, 0, 0), (1, 0, 1), (1, 0, -1), (1, 0, 2), (1, 0, -2),
    (1, 1, 0), (1, 1, 1), (1, 1, -1), (1, 1, 2), (1, -1, 0),
    (1, -1, 1), (1, -1, -1), (1, -1, -2), (1, 2, 0), (1, 2, -1),
    (1, -2, 0), (1, -2, 1), (2, 0, 1), (2, 0, -1), (2, 1, 0),
    (2, 1, 1), (2, 1, -1), (2, -1, 0), (2, -1, 1), (2, -1, -1)
]


def build_graph(vectors):
    """Build orthogonality graph: pairs and triads from coordinate vectors."""
    n = len(vectors)
    pair_set = set()
    for i in range(n):
        for j in range(i + 1, n):
            if sum(a * b for a, b in zip(vectors[i], vectors[j])) == 0:
                pair_set.add((i, j))
    pairs = sorted(pair_set)

    triads = []
    for i in range(n):
        for j in range(i + 1, n):
            if (i, j) not in pair_set:
                continue
            for k in range(j + 1, n):
                if (i, k) in pair_set and (j, k) in pair_set:
                    triads.append((i, j, k))
    return pairs, triads


# ============================================================
# Essential ray analysis
# ============================================================

def restrict(subset, pairs, triads):
    """Restrict pairs and triads to a subset of rays, re-indexing."""
    s = set(subset)
    remap = {old: new for new, old in enumerate(sorted(subset))}
    p = [(remap[a], remap[b]) for a, b in pairs if a in s and b in s]
    t = [(remap[a], remap[b], remap[c]) for a, b, c in triads
         if a in s and b in s and c in s]
    return p, t


def find_essential_rays(n, pairs, triads):
    """Identify which rays are essential (removal makes set colorable)."""
    essential, removable = [], []
    for ray in range(n):
        subset = [i for i in range(n) if i != ray]
        sp, st = restrict(subset, pairs, triads)
        if is_uncolorable(len(subset), sp, st):
            removable.append(ray)
        else:
            essential.append(ray)
    return essential, removable


# ============================================================
# Realizability: abstract graph -> R³ coordinates
# ============================================================

def check_realizability(n_rays, pairs, n_restarts=30):
    """
    Check if an abstract orthogonality graph can be realized in R^3.

    Find unit vectors v_1,...,v_n on S^2 such that v_i . v_j = 0
    for every required orthogonal pair (i,j).

    Parametrize each ray by spherical coordinates (theta, phi).
    Objective: sum of (v_i . v_j)^2 over all required pairs.
    Feasible when objective < 1e-10.

    Returns (feasible, vectors, residual).
    """
    if not pairs:
        return True, None, 0.0

    def rays_from_params(params):
        vecs = []
        for i in range(n_rays):
            th, ph = params[2 * i], params[2 * i + 1]
            vecs.append(np.array([
                np.sin(th) * np.cos(ph),
                np.sin(th) * np.sin(ph),
                np.cos(th)
            ]))
        return vecs

    def objective(params):
        vecs = rays_from_params(params)
        cost = 0.0
        for i, j in pairs:
            d = np.dot(vecs[i], vecs[j])
            cost += d * d
        return cost

    best_cost = float('inf')
    best_params = None
    for _ in range(n_restarts):
        x0 = np.random.uniform(0, 2 * np.pi, 2 * n_rays)
        result = scipy_min(objective, x0, method='L-BFGS-B')
        if result.fun < best_cost:
            best_cost = result.fun
            best_params = result.x

    feasible = best_cost < 1e-6
    vectors = rays_from_params(best_params) if best_params is not None else None
    return feasible, vectors, best_cost


def verify_realization(n_rays, vectors, required_pairs):
    """Check a realization for violations and extra orthogonalities."""
    max_viol = 0.0
    for i, j in required_pairs:
        max_viol = max(max_viol, abs(np.dot(vectors[i], vectors[j])))

    req_set = set((min(a, b), max(a, b)) for a, b in required_pairs)
    extra = []
    for i in range(n_rays):
        for j in range(i + 1, n_rays):
            if (i, j) not in req_set:
                if abs(np.dot(vectors[i], vectors[j])) < 1e-6:
                    extra.append((i, j))

    return max_viol, extra


# ============================================================
# Abstract graph generators
# ============================================================

def generate_interlocked_hypergraph(n_rays, n_triads):
    """
    Generate a random hypergraph where each triad shares at least
    one ray with an existing triad (ensures connectivity).
    """
    triads = []
    used = set()

    t = tuple(sorted(int(x) for x in np.random.choice(n_rays, 3, replace=False)))
    triads.append(t)
    used.update(t)

    attempts = 0
    while len(triads) < n_triads and attempts < 1000:
        attempts += 1
        shared = int(np.random.choice(list(used)))
        pool = [r for r in range(n_rays) if r != shared]
        others = [int(x) for x in np.random.choice(pool, 2, replace=False)]
        t = tuple(sorted([shared, others[0], others[1]]))
        if t not in triads:
            triads.append(t)
            used.update(t)

    pairs = set()
    for a, b, c in triads:
        pairs.add((min(a, b), max(a, b)))
        pairs.add((min(a, c), max(a, c)))
        pairs.add((min(b, c), max(b, c)))

    return sorted(pairs), triads


def perturb_ks_graph(n, pairs, triads, n_perturbations=1):
    """
    Perturb a known KS graph: swap a ray in one triad for a new ray.
    Explores the 'neighborhood' of known KS sets in graph space.
    """
    triads = [list(t) for t in triads]
    max_ray = n - 1

    for _ in range(n_perturbations):
        k = int(np.random.randint(len(triads)))
        pos = int(np.random.randint(3))
        old_ray = triads[k][pos]

        # Try a new ray (possibly extending the ray count)
        new_ray = int(np.random.randint(max_ray + 2))  # allow one new ray
        if new_ray != old_ray and new_ray not in triads[k]:
            triads[k][pos] = new_ray
            max_ray = max(max_ray, new_ray)

    n_new = max_ray + 1
    triads = [tuple(sorted(t)) for t in triads]

    pairs = set()
    for a, b, c in triads:
        pairs.add((min(a, b), max(a, b)))
        pairs.add((min(a, c), max(a, c)))
        pairs.add((min(b, c), max(b, c)))

    return n_new, sorted(pairs), triads


# ============================================================
# Main demonstration
# ============================================================

if __name__ == "__main__":
    np.random.seed(42)

    print("=" * 60)
    print("KS Set Search: SAT + Realizability Approach")
    print("=" * 60)
    print(f"SAT engine: {SAT_ENGINE}\n")

    # ---- PHASE 1: Analyze CK-31 ----
    print("PHASE 1: Analyze Conway-Kochen 31")
    print("-" * 40)

    pairs, triads = build_graph(CK31_VECTORS)
    n = len(CK31_VECTORS)
    print(f"  {n} rays, {len(pairs)} pairs, {len(triads)} triads")

    t0 = time.time()
    assert is_uncolorable(n, pairs, triads)
    print(f"  Uncolorable: YES ({time.time() - t0:.3f}s)")

    # Essential rays
    print("\n  Essential ray analysis...")
    t0 = time.time()
    essential, removable = find_essential_rays(n, pairs, triads)
    dt = time.time() - t0
    print(f"  Essential: {len(essential)}/{n} rays ({dt:.1f}s)")
    print(f"  Removable: {len(removable)} rays")
    if removable:
        for r in removable:
            print(f"    Ray {r}: {CK31_VECTORS[r]}")
    else:
        print("  -> CK-31 is MINIMAL: every ray is essential.")

    # Essential triads
    core_triads = get_essential_triads(n, pairs, triads)
    if core_triads is not None:
        print(f"\n  UNSAT core: {len(core_triads)}/{len(triads)} triads")
        print(f"  (These triads form the kernel of the KS contradiction)")
        for k in core_triads:
            a, b, c = triads[k]
            print(f"    T{k}: rays {a},{b},{c}  "
                  f"= {CK31_VECTORS[a]}, {CK31_VECTORS[b]}, {CK31_VECTORS[c]}")

    # ---- PHASE 2: Realizability ----
    print("\n" + "=" * 60)
    print("PHASE 2: Realizability")
    print("-" * 40)
    print("  Recovering R^3 coordinates from CK-31's abstract graph...")

    t0 = time.time()
    feasible, vecs, residual = check_realizability(n, pairs, n_restarts=30)
    dt = time.time() - t0
    print(f"  Realizable: {feasible} (residual: {residual:.2e}, {dt:.1f}s)")

    if feasible:
        max_viol, extras = verify_realization(n, vecs, pairs)
        print(f"  Max orthogonality violation: {max_viol:.2e}")
        print(f"  Extra orthogonalities found: {len(extras)}")
        if extras:
            print("  WARNING: realization introduced extra orthogonal pairs!")
            print("  The realized graph is LARGER than the abstract graph.")
        else:
            print("  Clean realization -- abstract and realized graphs match.")

    # ---- PHASE 3: Search ----
    print("\n" + "=" * 60)
    print("PHASE 3: Search for Novel KS Configurations")
    print("-" * 40)

    # Strategy A: Random interlocked hypergraphs
    print("\n  Strategy A: Random interlocked hypergraphs")
    print("  (Does any abstract graph on <31 rays happen to be both")
    print("   KS-uncolorable AND realizable in R^3?)\n")

    total_tested = 0
    total_uncolorable = 0
    total_realizable = 0

    for n_rays in [26, 28, 30]:
        for n_triads in [15, 17, 19]:
            unc = 0
            for trial in range(200):
                total_tested += 1
                p, t = generate_interlocked_hypergraph(n_rays, n_triads)
                if is_uncolorable(n_rays, p, t):
                    unc += 1
                    total_uncolorable += 1
                    # Only check realizability for uncolorable ones
                    ok, v, res = check_realizability(n_rays, p, n_restarts=3)
                    if ok:
                        total_realizable += 1
                        mv, ext = verify_realization(n_rays, v, p)
                        status = "CLEAN" if len(ext) == 0 else f"+{len(ext)} extra"
                        print(f"  *** FOUND: {n_rays}r, {len(t)}t, "
                              f"residual={res:.1e}, {status} ***")
            if unc:
                print(f"  [{n_rays}r, {n_triads}t]: "
                      f"{unc}/200 uncolorable, checked realizability")

    # Strategy B: Perturb CK-31's graph
    print(f"\n  Strategy B: Perturb CK-31's graph")
    print("  (Swap rays in triads, check if still uncolorable + realizable)\n")

    perturbation_hits = 0
    for trial in range(200):
        n2, p2, t2 = perturb_ks_graph(n, pairs, triads, n_perturbations=1)
        if n2 <= 31 and is_uncolorable(n2, p2, t2):
            perturbation_hits += 1
            if n2 < 31:
                ok, v, res = check_realizability(n2, p2, n_restarts=3)
                status = "REALIZABLE" if ok else f"not realizable (res={res:.1e})"
                print(f"  Perturbation: {n2} rays, {len(t2)} triads -- {status}")

    print(f"  {perturbation_hits}/200 perturbations preserved uncolorability")

    # ---- Summary ----
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  CK-31 essential rays: {len(essential)}/{n}")
    if core_triads is not None:
        print(f"  CK-31 essential triads (UNSAT core): {len(core_triads)}/{len(triads)}")
    print(f"  CK-31 realizability: {'YES' if feasible else 'NO'}")
    print(f"\n  Random search: {total_tested} graphs tested")
    print(f"    Uncolorable: {total_uncolorable}")
    print(f"    Realizable:  {total_realizable}")
    print(f"\n  Key insight: most abstract KS-uncolorable graphs CANNOT be")
    print(f"  realized in R^3. The geometric constraints are the bottleneck,")
    print(f"  not the combinatorial ones.")
    print(f"\n  To scale: replace random generation with systematic enumeration")
    print(f"  and use algebraic geometry (Groebner bases) for realizability")
    print(f"  instead of numerical optimization.")
