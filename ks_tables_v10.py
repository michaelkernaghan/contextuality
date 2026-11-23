"""v10 step 2: regenerate every table row that can be regenerated in exact arithmetic.

One row per NAMED pool: alphabet, raw or completed, rays / pairs / triads,
colourable or not, and for uncolourable pools the minimum (certified by
ks_certify_fast3 within the budget, else an upper bound).  Coordinates are exact
(Fraction coefficients over Q(t), t^2 = d); nothing is decided by a tolerance.

Rows that need two independent irrationals (for example sqrt2 together with
phi) are NOT produced here; v10 drops them rather than quote unverified counts.

Usage:  python ks_tables_v10.py <budget-seconds> [group ...]
Groups: two real complex ringgen heegner four gaussian completed
Writes: results/tables_v10.jsonl
"""
import json
import random
import sys
import time
from fractions import Fraction as Fr
from pathlib import Path

import ks_recertify_v10 as R

HERE = Path(__file__).resolve().parent
H = Fr(1, 2)


def quad(d):
    conj = (lambda c: (c[0], -c[1])) if d < 0 else None
    return R.Field(2, (d, 0), conj_map=conj, name="Q(sqrt %d)" % d)


def is_square(d):
    return int(abs(d) ** 0.5 + 0.5) ** 2 == abs(d)


def rows():
    out = []                                             # (group, label, field, alphabet, completed)
    Q = quad(5)
    for label, gens in (("{0,+-1}", []), ("{0,+-1,+-2}", [Q.el(2)]), ("{0,+-1,+-1/2}", [Q.el(H)]),
                        ("{0,+-1,+-3}", [Q.el(3)]), ("{0,+-1,+-4}", [Q.el(4)])):
        out.append(("two", label, Q, R.sym(Q, *gens), False))
    for d in range(2, 31):
        if not is_square(d):
            F = quad(d)
            out.append(("real", "{0,+-1,+-sqrt%d}" % d, F, R.sym(F, F.el(0, 1)), False))
    for d in range(1, 16):
        F = quad(-d)
        if d == 1 or not is_square(d):
            out.append(("complex", "{0,+-1,+-sqrt(-%d)}" % d, F, R.sym(F, F.el(0, 1)), False))
    for d in (5, 13, 17, 21, 29):
        F = quad(d)
        out.append(("ringgen", "{0,+-1,+-(1+sqrt%d)/2}" % d, F, R.sym(F, F.el(H, H)), False))
    for d in (1, 2, 3, 7, 11, 19, 43, 67, 163):
        F = quad(-d)
        a = F.el(0, 1) if d in (1, 2) else F.el(H, H)
        out.append(("heegner", "{0,+-1,+-a,+-a*}, d=%d, a=%s" % (d, "sqrt(-d)" if d in (1, 2) else "(1+sqrt(-d))/2"),
                    F, R.sym(F, a, a.conj()), False))
    F5, F2 = quad(5), quad(2)
    phi = F5.el(H, H)
    out += [("four", "{0,+-1,+-2,+-3}", Q, R.sym(Q, Q.el(2), Q.el(3)), False),
            ("four", "{0,+-1,+-sqrt2,+-2}", F2, R.sym(F2, F2.el(0, 1), F2.el(2)), False),
            ("four", "{0,+-1,+-phi,+-2}", F5, R.sym(F5, phi, F5.el(2)), False),
            ("four", "{0,+-1,+-phi,+-phi^2}", F5, R.sym(F5, phi, phi * phi), False)]
    Fi = quad(-1)
    out.append(("gaussian", "{0,+-1,+-i,+-(1+i)}", Fi, R.sym(Fi, Fi.el(0, 1), Fi.el(1, 1)), False))
    for d in (3, 5):
        F = quad(d)
        out.append(("completed", "{0,+-1,+-sqrt%d}" % d, F, R.sym(F, F.el(0, 1)), True))
    out.append(("completed", "{0,+-1,+-i,+-(1+i)}", Fi, R.sym(Fi, Fi.el(0, 1), Fi.el(1, 1)), True))
    return out


def main():
    budget = float(sys.argv[1])
    groups = set(sys.argv[2:])
    out = HERE / "results" / "tables_v10.jsonl"
    failed = 0
    for group, label, F, alpha, comp in rows():
        if groups and group not in groups:
            continue
        t0 = time.time()
        try:
            rays = R.build(alpha, F, complete=comp, cap=3000)
            pairs, triads, _ = R.structure(rays)
            n = len(rays)
            rec = {"group": group, "alphabet": label, "completed": comp, "rays": n,
                   "pairs": len(pairs), "triads": len(triads)}
            if R.colourable(range(n), pairs, triads):
                rec["colourable"] = True
            else:
                ub_set = R.greedy_min(n, pairs, triads, 30, random.Random(1034))
                exact, ub, best, it, calls, why = R.certify3(n, pairs, triads, ub_set,
                                                              budget=budget, verbose=False)
                rec.update(colourable=False, upper_bound=ub, certified_minimum=exact,
                           bases_in_witness=len(R.bases_of(best, triads)))
        except Exception as exc:
            failed += 1
            rec = {"group": group, "alphabet": label, "completed": comp, "error": repr(exc)}
        rec["seconds"] = round(time.time() - t0, 1)
        print(json.dumps(rec), flush=True)
        with out.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + "\n")
    print("errors: %d" % failed)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
