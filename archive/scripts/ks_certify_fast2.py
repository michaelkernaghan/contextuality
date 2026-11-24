"""Certification, second attempt: the bottleneck was the hitting-set solver.

Measured on the first version: of the 1470s spent between iterations 500 and 750
on the Golden pool, roughly 3s was SAT solving and the rest was RC2.  Rebuilding
a MaxSAT instance every iteration, over a constraint set that grows without
bound, dominates everything else.

So stop optimizing and start deciding.  We never actually need the minimum
hitting set; we only need to know whether a hitting set SMALLER than the best
known uncolourable set exists:

  * UNSAT  ->  no uncolourable subset of size < ub exists, so ub is the minimum.
  * SAT    ->  a candidate R with |R| < ub; test it, and either improve ub or
               harvest a new constraint.

That is a single SAT call against one persistent solver.  Hard clauses are added
incrementally and never rebuilt, and the cardinality bound is applied through an
ITotalizer as an ASSUMPTION, so tightening ub costs nothing.
"""
import time

from pysat.card import ITotalizer
from pysat.solvers import Glucose4

from ks_certify_fast import PoolSolver


def certify2(n, pairs, triads, ub_set, budget=1800, verbose=True, log_every=2000):
    """Exact pool minimum via cardinality-decision hitting sets."""
    ps = PoolSolver(n, pairs, triads)
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
            # enforce sum(selected) <= k as an assumption
            sat = hit.solve(assumptions=[-tot.rhs[k]])
            if not sat:
                return ub, ub, ub_set, it, ps.calls, \
                    "optimal: no hitting set smaller than ub"

            model = hit.get_model()
            R = [i for i in range(n) if model[i] > 0]

            if not ps.colourable(R):
                ub_set = set(R)
                ub = len(R)
                if verbose:
                    print("      iter %6d  improved ub -> %d  (%.0fs)"
                          % (it, ub, time.time() - t0), flush=True)
                continue

            M = ps.grow(R)
            clause = [i + 1 for i in range(n) if i not in M]
            if not clause:
                return ub, ub, ub_set, it, ps.calls, "pool itself colourable?"
            hit.add_clause(clause)

            if verbose and it % log_every == 0:
                print("      iter %6d  |R|=%3d  ub=%d  solves=%d  %.0fs"
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
    keys = sys.argv[2:] or ["heegner", "golden", "super", "cubic"]

    for key in keys:
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
        exact, ub, best, it, calls, why = certify2(n, pairs, triads, ub_set,
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
