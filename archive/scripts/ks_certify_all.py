"""Certify the pool minima for all four larger pools with the fast certifier."""
import random
import sys
import time
from fractions import Fraction

exec(open('ks_verify_large_minima.py', encoding='utf-8').read()
     .split('# ------------------------------------------------------------------'
            '--------\nQS =')[0])
from ks_certify_fast import certify   # noqa: E402

F7 = Field(2, (-7, 0), conj_map=lambda c: (c[0], -c[1]), name="Q(sqrt(-7))")
F5 = Field(2, (5, 0), conj_map=None, name="Q(sqrt5)")
FC = Field(3, (2, 0, 0), conj_map=None, name="Q(cbrt2)")
FP = Field(3, (1, 0, 1), conj_map=None, name="Q(psi)")

a7 = F7.el(Fraction(1, 2), Fraction(1, 2))
phi = F5.el(Fraction(1, 2), Fraction(1, 2))
c2, c4 = FC.el(0, 1), FC.el(0, 0, 1)
psi = FP.el(0, 1)

JOBS = {
    "heegner": ("Heegner-7  Z[(1+sqrt-7)/2]", F7,
                [F7.el(0), F7.el(1), -F7.el(1), a7, -a7, a7.conj(), -a7.conj()],
                False, 43, 120, 60),
    "golden":  ("Golden  Z[phi] completed", F5,
                [F5.el(0), F5.el(1), -F5.el(1), phi, -phi],
                True, 52, 400, 120),
    "super":   ("Supergolden  Z[psi] completed", FP,
                [FP.el(0), FP.el(1), -FP.el(1), psi, -psi],
                True, 47, 400, 120),
    "cubic":   ("Cubic  Z[cbrt2] completed", FC,
                [FC.el(0), FC.el(1), -FC.el(1), c2, -c2, c4, -c4],
                True, 58, 120, 180),
}


def run(key, budget):
    label, F, alpha, comp, claim, trials, _ = JOBS[key]
    print("=" * 72)
    print(label + "   (published claim: %s)" % claim)
    print("=" * 72, flush=True)
    rays = build(alpha, F, complete=comp)
    pairs, triads, _ = structure(rays)
    n = len(rays)
    print("  pool: %d rays, %d pairs, %d triads" % (n, len(pairs), len(triads)),
          flush=True)

    rng = random.Random(1034)
    t0 = time.time()
    ub_set = greedy_min(n, pairs, triads, trials, rng)
    print("  greedy UB after %d trials: %d rays  (%.0fs)"
          % (trials, len(ub_set), time.time() - t0), flush=True)

    t1 = time.time()
    exact, ub, best, it, calls, why = certify(n, pairs, triads, ub_set, budget=budget)
    el = time.time() - t1
    if exact is None:
        print("  NOT CERTIFIED (%s): minimum is <= %d" % (why, ub))
    else:
        verdict = "CONFIRMS" if exact == claim else "CONTRADICTS"
        print("  CERTIFIED MINIMUM = %d   [%s]" % (exact, why))
        print("  -> %s the published %s" % (verdict, claim))
    print("  iters=%d  sat_calls=%d  elapsed=%.0fs" % (it, calls, el), flush=True)
    print(flush=True)
    return exact


if __name__ == "__main__":
    which = sys.argv[1:] or ["heegner", "golden", "super", "cubic"]
    budget = 2700.0
    for k in which:
        try:
            run(k, budget)
        except Exception as e:
            print("  ERROR in %s: %r" % (k, e), flush=True)
