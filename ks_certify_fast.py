"""Fast exact certification of pool minima.

The slow version rebuilt a CNF from scratch for every colourability test, and
tested maximal growth one ray at a time -- O(n) full solver constructions per
hitting-set iteration.  Three changes:

1. ONE persistent incremental solver.  Every ray r gets a selector s_r, and the
   pool's constraints are written once, guarded by selectors:
       pair  (i,j)   : -s_i or -s_j or -x_i or -x_j
       triad (i,j,k) : -s_i or -s_j or -s_k or x_i or x_j or x_k
   Testing a subset R is then a single solve under assumptions, reusing all
   learned clauses instead of discarding them.

2. Model-guided growth.  After a satisfying assignment for R is found, rays
   consistent with that very assignment are added in bulk before falling back to
   one-at-a-time probing, which collapses most of the O(n) probes.

3. An upper bound that terminates the search.  If the minimum hitting set has
   size >= the best known uncolourable set, that set is optimal and we stop:
   every uncolourable subset must hit every constraint, so no smaller one exists.
   Symmetrically, if a minimum hitting set is itself uncolourable it is optimal.

Soundness note: a grown set M need not be strictly maximal for the algorithm to
stay correct.  Any colourable M yields the valid constraint "an uncolourable set
must contain a ray outside M", since every subset of M is colourable.  Weaker
growth costs iterations, never correctness.
"""
import sys
import time

from pysat.formula import CNF, WCNF
from pysat.solvers import Glucose4
from pysat.examples.rc2 import RC2


class PoolSolver:
    """Persistent selector-guarded solver for one ray pool."""

    def __init__(self, n, pairs, triads):
        self.n = n
        self.pairs = pairs
        self.triads = triads
        cnf = CNF()
        for i, j in pairs:
            cnf.append([-self.s(i), -self.s(j), -self.x(i), -self.x(j)])
        for i, j, k in triads:
            cnf.append([-self.s(i), -self.s(j), -self.s(k),
                        self.x(i), self.x(j), self.x(k)])
        self.solver = Glucose4(bootstrap_with=cnf)
        self.calls = 0

    def x(self, i):
        return i + 1

    def s(self, i):
        return self.n + i + 1

    def assume(self, R):
        sel = set(R)
        return [self.s(i) if i in sel else -self.s(i) for i in range(self.n)]

    def colourable(self, R):
        self.calls += 1
        return self.solver.solve(assumptions=self.assume(R))

    def model_colours(self):
        m = self.solver.get_model()
        return {i: (m[self.x(i) - 1] > 0) for i in range(self.n)}

    def grow(self, R):
        """Extend colourable R towards a maximal colourable set."""
        M = set(R)
        if not self.colourable(M):
            return M
        col = self.model_colours()

        # Bulk pass: keep the current assignment and admit every ray whose own
        # constraints it already satisfies.
        inM = M
        for r in range(self.n):
            if r in inM:
                continue
            ok = True
            if col[r]:
                for (i, j) in self.adj_pairs(r):
                    other = j if i == r else i
                    if other in inM and col[other]:
                        ok = False
                        break
            if ok:
                inM.add(r)
        if not self.colourable(inM):
            inM = set(R)  # bulk pass overshot; fall back

        # Probe the remainder one at a time.
        for r in range(self.n):
            if r in inM:
                continue
            inM.add(r)
            if not self.colourable(inM):
                inM.discard(r)
        return inM

    def adj_pairs(self, r):
        if not hasattr(self, "_adj"):
            self._adj = {i: [] for i in range(self.n)}
            for (i, j) in self.pairs:
                self._adj[i].append((i, j))
                self._adj[j].append((i, j))
        return self._adj[r]

    def delete(self):
        self.solver.delete()


def min_hitting_set(H, n):
    w = WCNF()
    for i in range(n):
        w.append([-(i + 1)], weight=1)
    for S in H:
        if not S:
            return None
        w.append([i + 1 for i in S])
    with RC2(w) as rc2:
        model = rc2.compute()
    if model is None:
        return None
    return [i for i in range(n) if model[i] > 0]


def certify(n, pairs, triads, ub_set, budget=1800, verbose=True):
    """Exact pool minimum, or the best bounds reached inside the budget."""
    ps = PoolSolver(n, pairs, triads)
    ub_set = set(ub_set)
    ub = len(ub_set)
    H, it, t0 = [], 0, time.time()
    try:
        while True:
            it += 1
            if time.time() - t0 > budget:
                return None, ub, ub_set, it, ps.calls, "budget exhausted"
            R = min_hitting_set(H, n)
            if R is None:
                return None, ub, ub_set, it, ps.calls, "hitting set infeasible"
            if len(R) >= ub:
                return ub, ub, ub_set, it, ps.calls, "optimal: lower bound met UB"
            if not ps.colourable(R):
                return len(R), len(R), set(R), it, ps.calls, "optimal: min hitting set is uncolourable"
            M = ps.grow(R)
            H.append([i for i in range(n) if i not in M])
            if verbose and it % 250 == 0:
                print("      iter %5d  |hit|=%3d  ub=%d  solves=%d  %.0fs"
                      % (it, len(R), ub, ps.calls, time.time() - t0), flush=True)
    finally:
        ps.delete()


if __name__ == "__main__":
    # Benchmark against the known-good Heegner-7 answer (43, certified in 24.5s
    # by the slow version).
    from fractions import Fraction
    src = open('ks_verify_large_minima.py', encoding='utf-8').read()
    exec(src.split('# ----------------------------------------------------------'
                   '----------------\nQS =')[0])

    F7 = Field(2, (-7, 0), conj_map=lambda c: (c[0], -c[1]), name="Q(sqrt(-7))")
    a = F7.el(Fraction(1, 2), Fraction(1, 2))
    alpha = [F7.el(0), F7.el(1), -F7.el(1), a, -a, a.conj(), -a.conj()]

    rays = build(alpha, F7)
    pairs, triads, _ = structure(rays)
    print("Heegner-7 pool: %d rays, %d pairs, %d triads"
          % (len(rays), len(pairs), len(triads)))

    import random
    rng = random.Random(42)
    ub_set = greedy_min(len(rays), pairs, triads, 60, rng)
    print("greedy UB: %d" % len(ub_set))

    t = time.time()
    exact, ub, best, it, calls, why = certify(len(rays), pairs, triads, ub_set)
    print("certified minimum: %s  [%s]" % (exact, why))
    print("iterations=%d  sat_calls=%d  elapsed=%.1fs" % (it, calls, time.time() - t))
    print("expected 43 -> %s" % ("MATCH" if exact == 43 else "MISMATCH"))
