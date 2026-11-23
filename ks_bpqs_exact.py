"""v10: exact minimum of |S_A| x |S_B| over bipartite-KS (B-KS) pairs of basis sets.

Replaces ks_bpqs_sat.py, which sampled Alice sizes, minimised Bob greedily and
still printed OPTIMAL.

Model (Cabello, PRL 134, 010201, Definition 2, in its Bell-local reading).
Alice holds a set S_A of bases of the KS set, Bob a set S_B.  A local
deterministic assignment picks one vector in each basis of each party
(completeness) such that no vector picked by Alice is orthogonal to a vector
picked by Bob (cross-party exclusion).  (S_A, S_B) is B-KS when no such
assignment exists.  A basis held by both parties is forced to the same pick, so
this agrees with the single-function form of the definition.

Search.  B-KS is monotone: enlarging S_A or S_B only adds constraints.  So if a
pair (M_A, M_B) admits an assignment, every B-KS pair must contain a basis
outside M_A on Alice's side or outside M_B on Bob's.  Each failed candidate is
grown to a maximal assignable pair (checked by SAT) and contributes that clause.
For sizes (p, q), p <= q (the model is symmetric in the parties), in increasing
order of p*q, a SAT solver looks for a pair with |S_A| <= p, |S_B| <= q
satisfying all clauses; the first (p, q) with a genuine B-KS pair is the exact
minimum product, because every smaller product was refuted.

Usage:  python ks_bpqs_exact.py <budget-seconds> [set-key ...]
Writes: results/bpqs_exact_v10.jsonl
"""
import itertools
import json
import sys
import time
from pathlib import Path

from pysat.card import ITotalizer
from pysat.solvers import Glucose4

import ks_recertify_v10 as R

HERE = Path(__file__).resolve().parent
CK31_INT = [
    (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 1, -1), (0, 1, 2), (0, 2, -1),
    (1, 0, 0), (1, 0, 1), (1, 0, -1), (1, 0, 2), (1, 0, -2),
    (1, 1, 0), (1, 1, 1), (1, 1, -1), (1, 1, 2), (1, -1, 0),
    (1, -1, 1), (1, -1, -1), (1, -1, -2), (1, 2, 0), (1, 2, -1),
    (1, -2, 0), (1, -2, 1), (2, 0, 1), (2, 0, -1), (2, 1, 0),
    (2, 1, 1), (2, 1, -1), (2, -1, 0), (2, -1, 1), (2, -1, -1),
]
# set key -> pool whose certified witness (results/recertify_v10.jsonl) is used
SETS = {"ck31": "integer-raw", "peres33": "peres-raw", "sqrtm2-33": "sqrtm2-raw",
        "eisenstein33": "eisenstein-raw", "heegner7-43": "heegner7-raw",
        "supergolden2-47": "supergolden2-raw", "golden": "golden-completed",
        "supergolden": "supergolden-completed", "cubic": "cubic-completed"}


def load_set(key):
    """Return (rays, orthogonal pair set, bases) of the named KS set, exact arithmetic."""
    pool = SETS[key]
    akey, comp, _ = R.POOLS[pool]
    F, alpha, _ = R.ALPHABETS[akey]
    rays = R.build(alpha, F, complete=comp, cap=3000)
    index = {R.canon(v): i for i, v in enumerate(rays)}
    if key == "ck31":
        chosen = [index[R.canon(tuple(F.el(c) for c in v))] for v in CK31_INT]
    else:
        rec = None
        for line in (HERE / "results" / "recertify_v10.jsonl").read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            if r["pool"] == pool and "witness" in r:
                rec = r                                    # last one wins
        if rec is None:
            raise RuntimeError("no certified witness recorded for %s" % pool)
        from fractions import Fraction
        chosen = [index[tuple(tuple(Fraction(c) for c in x) for x in w)] for w in rec["witness"]]
    sub = [rays[i] for i in chosen]
    pairs, triads, _ = R.structure(sub)
    assert not R.colourable(range(len(sub)), pairs, triads), "set is colourable"
    return sub, {frozenset(p) for p in pairs}, [tuple(t) for t in triads]


class Inner:
    """Persistent solver: is the pair (S_A, S_B) assignable?"""

    def __init__(self, bases, orth):
        self.m = len(bases)
        m = self.m
        self.s = Glucose4()
        xa = lambda b, k: 1 + 3 * b + k                    # noqa: E731
        xb = lambda b, k: 1 + 3 * m + 3 * b + k            # noqa: E731
        self.sa = lambda b: 1 + 6 * m + b
        self.sb = lambda b: 1 + 7 * m + b
        for b in range(m):
            for x, sel in ((xa, self.sa), (xb, self.sb)):
                self.s.add_clause([-sel(b)] + [x(b, k) for k in range(3)])
                for k, l in itertools.combinations(range(3), 2):
                    self.s.add_clause([-x(b, k), -x(b, l)])
        for b in range(m):
            for c in range(m):
                for k, v in enumerate(bases[b]):
                    for l, w in enumerate(bases[c]):
                        if frozenset((v, w)) in orth:
                            self.s.add_clause([-xa(b, k), -xb(c, l)])
        self.calls = 0

    def assignable(self, A, B):
        self.calls += 1
        assume = [self.sa(b) if b in A else -self.sa(b) for b in range(self.m)]
        assume += [self.sb(b) if b in B else -self.sb(b) for b in range(self.m)]
        return self.s.solve(assumptions=assume)

    def grow(self, A, B):
        A, B = set(A), set(B)
        for b in range(self.m):
            for side in (A, B):
                if b not in side:
                    side.add(b)
                    if not self.assignable(A, B):
                        side.discard(b)
        return A, B


def minimise(bases, orth, budget):
    m = len(bases)
    inner = Inner(bases, orth)
    full = set(range(m))
    if inner.assignable(full, full):
        return {"status": "NOT_BKS", "bases": m}
    outer = Glucose4()
    ta = ITotalizer(lits=list(range(1, m + 1)), ubound=m, top_id=2 * m)
    tb = ITotalizer(lits=list(range(m + 1, 2 * m + 1)), ubound=m, top_id=ta.top_id)
    outer.append_formula(ta.cnf)
    outer.append_formula(tb.cnf)
    sizes = sorted(((p, q) for p in range(1, m + 1) for q in range(p, m + 1)),
                   key=lambda t: (t[0] * t[1], t[1] - t[0]))
    refuted, t0, iters = [], time.time(), 0
    for p, q in sizes:
        if any(p <= rp and q <= rq for rp, rq in refuted):
            continue
        assume = ([-ta.rhs[p]] if p < m else []) + ([-tb.rhs[q]] if q < m else [])
        while True:
            if time.time() - t0 > budget:
                done = max((rp * rq for rp, rq in refuted), default=0)
                return {"status": "BUDGET", "bases": m, "refuted_all_products_below": p * q,
                        "largest_refuted": done, "iterations": iters, "sat_calls": inner.calls}
            if not outer.solve(assumptions=assume):
                refuted.append((p, q))
                break
            model = outer.get_model()
            A = {b for b in range(m) if model[b] > 0}
            B = {b for b in range(m) if model[m + b] > 0}
            iters += 1
            if not inner.assignable(A, B):
                return {"status": "EXACT", "bases": m, "alice": len(A), "bob": len(B),
                        "product": len(A) * len(B), "S_A": sorted(A), "S_B": sorted(B),
                        "iterations": iters, "sat_calls": inner.calls,
                        "note": "every (p,q), p<=q, with smaller product refuted"}
            MA, MB = inner.grow(A, B)
            outer.add_clause([b + 1 for b in range(m) if b not in MA]
                             + [m + b + 1 for b in range(m) if b not in MB])


def main():
    budget = float(sys.argv[1])
    keys = sys.argv[2:] or list(SETS)
    out = HERE / "results" / "bpqs_exact_v10.jsonl"
    failed = []
    for key in keys:
        t0 = time.time()
        try:
            rays, orth, bases = load_set(key)
            res = minimise(bases, orth, budget)
        except Exception as exc:                            # keep going, fail loudly at the end
            failed.append(key)
            print("%-18s ERROR %s" % (key, exc), flush=True)
            continue
        res.update(set=key, rays=len(rays), seconds=round(time.time() - t0, 1),
                   date=time.strftime("%Y-%m-%d %H:%M"))
        print("%-18s %s" % (key, {k: v for k, v in res.items() if k not in ("S_A", "S_B")}), flush=True)
        with out.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(res) + "\n")
    print("failed: %s" % (failed or "none"))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
