"""Certification v3: grow from the model instead of probing with SAT.

v2 profile on Golden: 290,330 SAT calls, ~6 ms each, ~155 of them per iteration,
almost all inside grow().  Two problems -- the sheer call count, and a persistent
solver whose learned-clause database degrades after ~10^5 assumption solves.

The observation that removes the call count: when a subset R tests colourable,
the solver hands back a full assignment.  That assignment is a colouring, and it
already certifies a colourable superset of R -- no further solving needed.  Take
every ray, find the constraints the assignment violates, and greedily drop rays
until none remain.  The survivors are colourable BY CONSTRUCTION, witnessed by
that assignment.

Soundness is unchanged: the grown set need not be maximal.  Any colourable M
gives the valid constraint "an uncolourable set must contain a ray outside M".
Weaker growth costs iterations, never correctness.

The solver is also rebuilt periodically to shed accumulated learned clauses.
"""
import time
from collections import Counter

from pysat.card import ITotalizer
from pysat.solvers import Glucose4

from ks_certify_fast import PoolSolver


class FastPool(PoolSolver):
    def __init__(self, n, pairs, triads):
        super().__init__(n, pairs, triads)
        self.pair_list = list(pairs)
        self.triad_list = list(triads)
        self._since_rebuild = 0

    def maybe_rebuild(self, every=40000):
        """Shed the learned-clause database.

        Measured degradation: the same solver answered in 0.018 ms on the
        145-ray pool and 6 ms on the 205-ray pool after ~10^5 assumption solves,
        a 330x slowdown with no change in instance size.  The counter must track
        SAT CALLS, not outer iterations -- an earlier version counted iterations
        and so effectively never fired.
        """
        if self.calls - self._since_rebuild >= every:
            self._since_rebuild = self.calls
            carried = self.calls
            self.solver.delete()
            PoolSolver.__init__(self, self.n, self.pair_list, self.triad_list)
            self.calls = carried

    def grow_from_model(self, R):
        """Colourable superset of R, derived from the satisfying assignment."""
        col = self.model_colours()
        Rset = set(R)
        M = set(range(self.n))

        # Violations of the assignment, over the whole pool.
        vp = [(i, j) for (i, j) in self.pair_list if col[i] and col[j]]
        vt = [(i, j, k) for (i, j, k) in self.triad_list
              if not (col[i] or col[j] or col[k])]

        cnt = Counter()
        for (i, j) in vp:
            cnt[i] += 1
            cnt[j] += 1
        for t in vt:
            for r in t:
                cnt[r] += 1

        # Greedily drop the most-implicated rays until the assignment is clean.
        # Rays of R are never dropped: R is colourable under this very
        # assignment, so no violation lies wholly inside R.
        alive_p = set(range(len(vp)))
        alive_t = set(range(len(vt)))
        while alive_p or alive_t:
            cand = [r for r in cnt if r not in Rset and r in M and cnt[r] > 0]
            if not cand:
                break
            worst = max(cand, key=lambda r: cnt[r])
            M.discard(worst)
            for idx in list(alive_p):
                i, j = vp[idx]
                if i == worst or j == worst:
                    alive_p.discard(idx)
                    cnt[i] -= 1
                    cnt[j] -= 1
            for idx in list(alive_t):
                t = vt[idx]
                if worst in t:
                    alive_t.discard(idx)
                    for r in t:
                        cnt[r] -= 1
        return M


def certify3(n, pairs, triads, ub_set, budget=1800, verbose=True, log_every=20000,
             strong_growth=True):
    """strong_growth=True probes with SAT (few iterations, costly each);
    False grows from the model only (many cheap iterations)."""
    ps = FastPool(n, pairs, triads)
    ub_set = set(ub_set)
    ub = len(ub_set)

    hit = Glucose4()
    tot = ITotalizer(lits=list(range(1, n + 1)), ubound=max(ub - 1, 1), top_id=n)
    hit.append_formula(tot.cnf)

    it, t0 = 0, time.time()
    try:
        while True:
            it += 1
            if time.time() - t0 > budget:
                return None, ub, ub_set, it, ps.calls, "budget exhausted"
            k = ub - 1
            if k < 1:
                return ub, ub, ub_set, it, ps.calls, "optimal: ub = 1"
            if not hit.solve(assumptions=[-tot.rhs[k]]):
                return ub, ub, ub_set, it, ps.calls, \
                    "optimal: no hitting set smaller than ub"
            model = hit.get_model()
            R = [i for i in range(n) if model[i] > 0]

            ps.maybe_rebuild()
            if not ps.colourable(R):
                ub_set, ub = set(R), len(R)
                if verbose:
                    print("      iter %7d  improved ub -> %d  (%.0fs)"
                          % (it, ub, time.time() - t0), flush=True)
                continue

            M = ps.grow(R) if strong_growth else ps.grow_from_model(R)
            clause = [i + 1 for i in range(n) if i not in M]
            if not clause:
                return ub, ub, ub_set, it, ps.calls, "pool colourable?"
            hit.add_clause(clause)

            if verbose and it % log_every == 0:
                print("      iter %7d  |R|=%3d  ub=%d  solves=%d  %.0fs"
                      % (it, len(R), ub, ps.calls, time.time() - t0), flush=True)
    finally:
        tot.delete()
        hit.delete()
        ps.delete()


if __name__ == "__main__":
    import random
    import sys
    from fractions import Fraction

    exec(open('ks_verify_large_minima.py', encoding='utf-8').read()
         .split('# --------------------------------------------------------------'
                '------------\nQS =')[0])

    F7 = Field(2, (-7, 0), conj_map=lambda c: (c[0], -c[1]))
    F5 = Field(2, (5, 0), conj_map=None)
    FC = Field(3, (2, 0, 0), conj_map=None)
    FP = Field(3, (1, 0, 1), conj_map=None)
    a7 = F7.el(Fraction(1, 2), Fraction(1, 2))
    phi = F5.el(Fraction(1, 2), Fraction(1, 2))
    c2, c4 = FC.el(0, 1), FC.el(0, 0, 1)
    psi = FP.el(0, 1)

    JOBS = {
        "heegner": ("Heegner-7", F7,
                    [F7.el(0), F7.el(1), -F7.el(1), a7, -a7, a7.conj(), -a7.conj()],
                    False, 43, 120),
        "golden":  ("Golden", F5, [F5.el(0), F5.el(1), -F5.el(1), phi, -phi],
                    True, 52, 400),
        "super":   ("Supergolden", FP, [FP.el(0), FP.el(1), -FP.el(1), psi, -psi],
                    True, 47, 400),
        "cubic":   ("Cubic", FC,
                    [FC.el(0), FC.el(1), -FC.el(1), c2, -c2, c4, -c4],
                    True, 58, 200),
    }

    budget = float(sys.argv[1]) if len(sys.argv) > 1 else 1500.0
    for key in (sys.argv[2:] or ["heegner", "golden", "super", "cubic"]):
        label, F, alpha, comp, claim, trials = JOBS[key]
        print("=" * 72)
        print("%s   (published claim: %s)" % (label, claim))
        print("=" * 72, flush=True)
        rays = build(alpha, F, complete=comp)
        pairs, triads, _ = structure(rays)
        n = len(rays)
        print("  pool: %d rays, %d pairs, %d triads" % (n, len(pairs), len(triads)),
              flush=True)
        rng = random.Random(1034)
        ub_set = greedy_min(n, pairs, triads, trials, rng)
        print("  greedy UB: %d" % len(ub_set), flush=True)
        t1 = time.time()
        exact, ub, best, it, calls, why = certify3(n, pairs, triads, ub_set,
                                                   budget=budget)
        el = time.time() - t1
        if exact is None:
            print("  NOT CERTIFIED (%s): minimum <= %d" % (why, ub))
        else:
            print("  CERTIFIED MINIMUM = %d   [%s]" % (exact, why))
            print("  -> %s the published %s"
                  % ("CONFIRMS" if exact == claim else "CONTRADICTS", claim))
        print("  iters=%d  sat_calls=%d  elapsed=%.0fs  (%.0f iters/s)"
              % (it, calls, el, it / max(el, 1e-9)), flush=True)
        print(flush=True)
