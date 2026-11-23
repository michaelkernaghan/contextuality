"""v10 step 1: re-certify every pool minimum with the sound certifier.

The v9 "OCUS" minima came from ks_ocus_all_pools.py, whose refinement clause is
unsound (it ignores violated triads with two or three omitted rays), so none of
them can be quoted.  This driver rebuilds each NAMED pool in exact arithmetic
(ks_verify_large_minima.Field) and runs ks_certify_fast3.certify3, whose every
hitting clause is the complement of a SAT-verified colourable set.

Each pool is identified by alphabet AND by whether it is the raw word pool or
its closure under orthocomplements ("completed").  A bound for one says nothing
about the other.

Usage:  python ks_recertify_v10.py <budget-seconds> [pool-key ...]
Writes: results/recertify_v10.jsonl (one line per pool, appended).
Exit status is non-zero if any requested pool raised an error.
"""
import json
import random
import sys
import time
import traceback
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
exec((HERE / "ks_verify_large_minima.py").read_text(encoding="utf-8")
     .split('# --------------------------------------------------------------'
            '------------\nQS =')[0])
from ks_certify_fast3 import certify3   # noqa: E402

FQ = Field(2, (5, 0), conj_map=None, name="Q (inside Q(sqrt5))")
F2 = Field(2, (2, 0), conj_map=None, name="Q(sqrt2)")
FM2 = Field(2, (-2, 0), conj_map=lambda c: (c[0], -c[1]), name="Q(sqrt-2)")
FW = Field(2, (-1, -1), conj_map=lambda c: (c[0] - c[1], -c[1]), name="Q(omega)")
F7 = Field(2, (-7, 0), conj_map=lambda c: (c[0], -c[1]), name="Q(sqrt-7)")
F5 = Field(2, (5, 0), conj_map=None, name="Q(sqrt5)")
FC = Field(3, (2, 0, 0), conj_map=None, name="Q(cbrt2)")
FP = Field(3, (1, 0, 1), conj_map=None, name="Q(psi)")


def sym(F, *gens):
    out = [F.el(0), F.el(1), -F.el(1)]
    for g in gens:
        out += [g, -g]
    return out


w = FW.el(0, 1)
a7 = F7.el(Fraction(1, 2), Fraction(1, 2))
phi = F5.el(Fraction(1, 2), Fraction(1, 2))
psi = FP.el(0, 1)

ALPHABETS = {
    "integer":    (FQ, sym(FQ, FQ.el(2)), "{0,+-1,+-2}"),
    "peres":      (F2, sym(F2, F2.el(0, 1)), "{0,+-1,+-sqrt2}"),
    "sqrtm2":     (FM2, sym(FM2, FM2.el(0, 1)), "{0,+-1,+-sqrt(-2)}"),
    "eisenstein": (FW, sym(FW, w, w * w), "{0,+-1,+-w,+-w^2}"),
    "heegner7":   (F7, sym(F7, a7, a7.conj()), "{0,+-1,+-a,+-a*}, a=(1+sqrt-7)/2"),
    "golden":     (F5, sym(F5, phi), "{0,+-1,+-phi}"),
    "supergolden": (FP, sym(FP, psi), "{0,+-1,+-psi}, psi^3=psi^2+1"),
    "supergolden2": (FP, sym(FP, psi, psi * psi), "{0,+-1,+-psi,+-psi^2}"),
    "cubic":      (FC, sym(FC, FC.el(0, 1), FC.el(0, 0, 1)), "{0,+-1,+-cbrt2,+-cbrt4}"),
}
# pool key -> (alphabet key, completed?, greedy trials)
POOLS = {k + "-raw": (k, False, 60) for k in ALPHABETS}
POOLS.update({k + "-completed": (k, True, 40) for k in ALPHABETS})


def run(key, budget, out):
    akey, comp, trials = POOLS[key]
    F, alpha, desc = ALPHABETS[akey]
    rec = {"pool": key, "alphabet": desc, "completed": comp, "date": time.strftime("%Y-%m-%d %H:%M")}
    t0 = time.time()
    rays = build(alpha, F, complete=comp, cap=3000)
    pairs, triads, _ = structure(rays)
    n = len(rays)
    rec.update(rays=n, pairs=len(pairs), triads=len(triads))
    print("%-22s %4d rays %5d pairs %4d triads" % (key, n, len(pairs), len(triads)), flush=True)
    if colourable(range(n), pairs, triads):
        rec.update(status="COLOURABLE")
        print("   pool is colourable", flush=True)
    else:
        ub_set = greedy_min(n, pairs, triads, trials, random.Random(1034))
        print("   greedy upper bound %d (%.0fs)" % (len(ub_set), time.time() - t0), flush=True)
        exact, ub, best, it, calls, why = certify3(n, pairs, triads, ub_set, budget=budget,
                                                   verbose=False)
        assert not colourable(best, pairs, triads), "witness is colourable"
        rec.update(upper_bound=ub, certified_minimum=exact, reason=why, iterations=it,
                   sat_calls=calls, bases_in_witness=len(bases_of(best, triads)),
                   status="CERTIFIED" if exact is not None else "UPPER_BOUND_ONLY",
                   witness=[[[str(c) for c in x] for x in canon(rays[i])] for i in sorted(best)])
        print("   %s: %s  [%s]" % (rec["status"], exact if exact is not None else "<= %d" % ub, why),
              flush=True)
    rec["seconds"] = round(time.time() - t0, 1)
    with out.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")


def main():
    budget = float(sys.argv[1])
    keys = sys.argv[2:] or list(POOLS)
    out = HERE / "results" / "recertify_v10.jsonl"
    out.parent.mkdir(exist_ok=True)
    failed = []
    for key in keys:
        try:
            run(key, budget, out)
        except Exception:
            failed.append(key)
            print("   ERROR in %s" % key, flush=True)
            traceback.print_exc()
    done = [k for k in keys if k not in failed]
    print("finished %d of %d pools; failed: %s" % (len(done), len(keys), failed or "none"))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
