"""v10: every pool P(x) = S({0, +-1, +-x, +-x*}), x complex, x != 0.

Same method as ks_two_symbol_theorem.py, one letter more.  A product conj(a) b or a b of
two letters is, up to sign, one of the six monomials

    1,  x,  x*,  N = x x*,  x^2,  x*^2,

so every inner product of two words (at most three terms) and every 2x2 minor (two terms)
is  c . (1, x, x*, N, x^2, x*^2)  for an integer vector c with 1 <= |c|_1 <= 3, or is
identically zero.  There are 376 such vectors.  The graph of P(x) is determined by the set
Z(x) of vectors that vanish at x.

Write x = a + ib and B = b^2.  P(x*) = P(x), so only (a, B) with B >= 0 matters.  For a
vector c put  s = c1+c2,  t = c4+c5,  p(a) = c0 + s a + (c3+t) a^2,  k = c3 - t.  Then

    Re = p(a) + k B,        Im = b * [ (c1-c2) + 2 (c4-c5) a ].

So in the (a, B) half-plane the zero set of c is a union of
  * graphs  B = g(a),  g a rational polynomial of degree <= 2 (the real axis is g = 0),
  * vertical lines  a = alpha,  alpha rational or a quadratic irrational,
  * isolated points with a and B in one quadratic field.
Two distinct such curves meet in at most two points, with coordinates in a quadratic field.
Hence: off all curves Z(x) is empty; at a point of exactly one curve that is not special,
Z(x) is the set of vectors whose zero set contains that curve; and the special points
(isolated zeros and pairwise intersections) are finitely many.  Every case is built here in
exact arithmetic over Q(sqrt d), tested for colourability, and, if uncolourable, certified.

Usage:  python ks_conjugate_closed_theorem.py scan            # enumerate + colourability
        python ks_conjugate_closed_theorem.py certify <budget-seconds>
Writes: results/conjugate_closed_scan.json, results/conjugate_closed_theorem.json
"""
import itertools
import json
import random
import sys
import time
from fractions import Fraction as Fr
from pathlib import Path

import ks_recertify_v10 as R

HERE = Path(__file__).resolve().parent


# ---------------------------------------------------------------- Q(sqrt d)
def squarefree(n):
    """Positive integer n = r^2 d with d squarefree; returns (r, d)."""
    r, d, f = 1, n, 2
    while f * f <= d:
        while d % (f * f) == 0:
            d //= f * f
            r *= f
        f += 1
    return r, d


def sqrt_rat(q):
    """sqrt of a rational q > 0 as (r, d) with sqrt(q) = r sqrt(d), d squarefree."""
    r, d = squarefree(q.numerator * q.denominator)
    return Fr(r, q.denominator), d


class Q2:
    """p + q sqrt(d), d squarefree >= 2, or d = 1 with q = 0."""
    __slots__ = ("p", "q", "d")

    def __init__(self, p, q=0, d=1):
        self.p, self.q = Fr(p), Fr(q)
        self.d = d if self.q != 0 else 1
        assert self.d == 1 or squarefree(self.d) == (1, self.d)

    def _co(self, o):
        if not isinstance(o, Q2):
            o = Q2(o)
        d = max(self.d, o.d)
        assert self.d in (1, d) and o.d in (1, d), "mixed quadratic fields"
        return o, d

    def __add__(self, o):
        o, d = self._co(o)
        return Q2(self.p + o.p, self.q + o.q, d)

    __radd__ = __add__

    def __neg__(self):
        return Q2(-self.p, -self.q, self.d)

    def __sub__(self, o):
        o, d = self._co(o)
        return Q2(self.p - o.p, self.q - o.q, d)

    def __mul__(self, o):
        o, d = self._co(o)
        return Q2(self.p * o.p + self.q * o.q * d, self.p * o.q + self.q * o.p, d)

    __rmul__ = __mul__

    def is_zero(self):
        return self.p == 0 and self.q == 0

    def sign(self):
        """Exact sign of p + q sqrt(d)."""
        if self.q == 0:
            return (self.p > 0) - (self.p < 0)
        if self.p == 0:
            return (self.q > 0) - (self.q < 0)
        sp, sq = (self.p > 0) - (self.p < 0), (self.q > 0) - (self.q < 0)
        if sp == sq:
            return sp
        big = self.p * self.p - self.q * self.q * self.d      # |p| vs |q| sqrt d
        return sp if big > 0 else sq

    def key(self):
        return (self.p, self.q, self.d)

    def approx(self):
        return float(self.p) + float(self.q) * self.d ** 0.5

    def __str__(self):
        if self.q == 0:
            return str(self.p)
        s = "%s*sqrt(%d)" % (abs(self.q), self.d)
        if self.p == 0:
            return ("-" if self.q < 0 else "") + s
        return "%s%s%s" % (self.p, "+" if self.q > 0 else "-", s)


def poly_roots(c0, c1, c2):
    """Real roots (as Q2) of c0 + c1 a + c2 a^2, rational coefficients, not identically 0."""
    c0, c1, c2 = Fr(c0), Fr(c1), Fr(c2)
    if c2 == 0:
        return [] if c1 == 0 else [Q2(-c0 / c1)]
    disc = c1 * c1 - 4 * c2 * c0
    if disc < 0:
        return []
    if disc == 0:
        return [Q2(-c1 / (2 * c2))]
    r, d = sqrt_rat(disc)
    if d == 1:
        return [Q2((-c1 + r) / (2 * c2)), Q2((-c1 - r) / (2 * c2))]
    return [Q2(-c1 / (2 * c2), r / (2 * c2), d), Q2(-c1 / (2 * c2), -r / (2 * c2), d)]


def peval(g, a):
    return Q2(g[0]) + a * Q2(g[1]) + a * a * Q2(g[2])


# ---------------------------------------------------------------- points and vectors
VECTORS = [c for c in itertools.product(range(-3, 4), repeat=6) if 1 <= sum(map(abs, c)) <= 3]


class Pt:
    """x = a + i sqrt(B), with a, B in one quadratic field and B >= 0."""

    def __init__(self, a, B):
        self.a = a if isinstance(a, Q2) else Q2(a)
        self.B = B if isinstance(B, Q2) else Q2(B)
        assert self.B.sign() >= 0
        self.a2 = self.a * self.a

    def key(self):
        return self.a.key() + self.B.key()

    def is_origin(self):
        return self.a.is_zero() and self.B.is_zero()

    def vanishes(self, c):
        c0, c1, c2, c3, c4, c5 = c
        if not self.B.is_zero():
            if not (Q2(c1 - c2) + (2 * (c4 - c5)) * self.a).is_zero():
                return False
        t = c4 + c5
        return (Q2(c0) + (c1 + c2) * self.a + (c3 + t) * self.a2 + (c3 - t) * self.B).is_zero()

    def label(self):
        if self.B.is_zero():
            return "%s" % self.a
        return "a = %s, b^2 = %s" % (self.a, self.B)

    def approx(self):
        return (round(self.a.approx(), 6), round(max(self.B.approx(), 0.0) ** 0.5, 6))


def decompose(c):
    """Zero set of c in the (a, B) half-plane: (graphs, vertical lines, isolated points)."""
    c0, c1, c2, c3, c4, c5 = c
    s, t = c1 + c2, c4 + c5
    p, k = (Fr(c0), Fr(s), Fr(c3 + t)), c3 - t
    l0, l1 = c1 - c2, 2 * (c4 - c5)
    graphs, lines, points = [], [], []
    if l0 == 0 and l1 == 0:
        if k != 0:
            graphs.append(tuple(-v / k for v in p))
        else:
            assert any(p), "zero vector"
            lines += poly_roots(*p)
        return graphs, lines, points
    if not any(p):
        graphs.append((Fr(0), Fr(0), Fr(0)))                 # whole real axis
    else:
        points += [Pt(r, 0) for r in poly_roots(*p)]
    if l1 != 0:
        a0 = Q2(Fr(-l0, l1))
        val = peval(p, a0)
        if k != 0:
            Bv = Q2(-val.p / k)
            if Bv.sign() > 0:
                points.append(Pt(a0, Bv))
            elif Bv.sign() == 0 and any(p):
                pass                                         # already a real root of p
        elif val.is_zero():
            lines.append(a0)
    return graphs, lines, points


def arrangement():
    dec = {c: decompose(c) for c in VECTORS}
    graphs = sorted({g for d in dec.values() for g in d[0]})
    lines = {}
    for d in dec.values():
        for a in d[1]:
            lines[a.key()] = a
    special = {}

    def add(pt):
        if not pt.is_origin():
            special[pt.key()] = pt

    for d in dec.values():
        for pt in d[2]:
            add(pt)
    for g1, g2 in itertools.combinations(graphs, 2):
        diff = tuple(u - v for u, v in zip(g1, g2))
        for a in poly_roots(*diff):
            Bv = peval(g1, a)
            if Bv.sign() >= 0:
                add(Pt(a, Bv))
    for g in graphs:
        for a in lines.values():
            Bv = peval(g, a)
            if Bv.sign() >= 0:
                add(Pt(a, Bv))
    return dec, graphs, list(lines.values()), special


def sample_graph(g, dec, special):
    want = {c for c, d in dec.items() if g in d[0]}
    for num in range(-40, 41):
        for den in (7, 11, 13):
            a = Q2(Fr(num, den) + Fr(1, 3))
            Bv = peval(g, a)
            if any(g) and Bv.sign() <= 0:
                continue
            pt = Pt(a, Bv)
            if pt.is_origin() or pt.key() in special:
                continue
            if {c for c in VECTORS if pt.vanishes(c)} == want:
                return pt
    return None


def sample_line(a, dec, special):
    want = {c for c, d in dec.items() if any(l.key() == a.key() for l in d[1])}
    for t in (Fr(1, 3), Fr(2, 7), Fr(3, 11), Fr(5, 13), Fr(7, 3), Fr(11, 5), Fr(13, 7), Fr(17, 3)):
        pt = Pt(a, Q2(t))
        if pt.key() in special:
            continue
        if {c for c in VECTORS if pt.vanishes(c)} == want:
            return pt
    raise RuntimeError("no clean sample on line a = %s" % a)


# ---------------------------------------------------------------- the pool at a point
# letter = None (zero) or (sign, kind), kind 0: 1, 1: x, 2: x*
LETTERS = [None] + [(s, k) for k in (0, 1, 2) for s in (1, -1)]
WORDS = [w for w in itertools.product(LETTERS, repeat=3) if any(w)]
CONJ = {0: 0, 1: 2, 2: 1}
MONO = {(0, 0): 0, (0, 1): 1, (1, 0): 1, (0, 2): 2, (2, 0): 2, (1, 2): 3, (2, 1): 3,
        (1, 1): 4, (2, 2): 5}


def inner_vec(u, v):
    c = [0] * 6
    for a, b in zip(u, v):
        if a is not None and b is not None:
            c[MONO[(CONJ[a[1]], b[1])]] += a[0] * b[0]
    return tuple(c)


def minor_vec(u, v, i, j):
    c = [0] * 6
    for (a, b), sgn in (((u[i], v[j]), 1), ((u[j], v[i]), -1)):
        if a is not None and b is not None:
            c[MONO[(a[1], b[1])]] += sgn * a[0] * b[0]
    return tuple(c)


ZERO6 = (0,) * 6


def pool(pt):
    cache = {ZERO6: True}

    def van(c):
        if c not in cache:
            cache[c] = pt.vanishes(c)
        return cache[c]

    reps = []
    for w in WORDS:
        for r in reps:
            if all(van(minor_vec(w, r, i, j)) for i, j in ((0, 1), (0, 2), (1, 2))):
                break
        else:
            reps.append(w)
    n = len(reps)
    adj = [set() for _ in range(n)]
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            if van(inner_vec(reps[i], reps[j])):
                pairs.append((i, j))
                adj[i].add(j)
                adj[j].add(i)
    triads = [(i, j, k) for (i, j) in pairs for k in adj[i] & adj[j] if k > j]
    return reps, pairs, triads


def word_str(w):
    return "(" + ",".join("0" if a is None else ("-" if a[0] < 0 else "") + ("1", "x", "x*")[a[1]]
                          for a in w) + ")"


def graph_name(g):
    return "b^2 = %s + %s a + %s a^2" % g if any(g) else "b = 0"


def cases():
    dec, graphs, lines, special = arrangement()
    out = []
    gen = None
    for num in range(1, 30):
        pt = Pt(Q2(Fr(num, 17) + Fr(1, 3)), Q2(Fr(1, 5) + Fr(num, 19)))
        if not any(pt.vanishes(c) for c in VECTORS):
            gen = pt
            break
    assert gen is not None
    out.append(("generic", "on no curve", gen))
    skipped = []
    for g in graphs:
        pt = sample_graph(g, dec, special)
        if pt is None:
            skipped.append(graph_name(g))
        else:
            out.append(("curve", graph_name(g), pt))
    for a in sorted(lines, key=lambda q: q.approx()):
        out.append(("curve", "a = %s" % a, sample_line(a, dec, special)))
    for k in sorted(special, key=lambda k: (special[k].approx()[1], special[k].approx()[0])):
        out.append(("point", special[k].label(), special[k]))
    return out, graphs, lines, special, skipped


def has_real_points(g):
    """Does B = g(a) have a point with B > 0?"""
    g0, g1, g2 = g
    if g2 > 0 or (g2 == 0 and g1 != 0):
        return True
    if g2 == 0:
        return g0 > 0
    return g0 - g1 * g1 / (4 * g2) > 0                       # maximum of a downward parabola


CONTROLS = {  # label -> (rays, pairs, triads), from the number-field constructions of the paper
    "2": (49, 138, 26), "1*sqrt(2)": (49, 120, 16), "a = 0, b^2 = 2": (49, 120, 16),
    "a = -1/2, b^2 = 3/4": (57, 174, 22), "a = 1/2, b^2 = 7/4": (145, 522, 42),
    "a = 0, b^2 = 1": (31, 69, 7), "1": (13, 24, 4),
}


def scan():
    t0 = time.time()
    todo, graphs, lines, special, skipped = cases()
    for name in skipped:
        g = [g for g in graphs if graph_name(g) == name][0]
        assert not has_real_points(g), "graph with real points has no clean sample: %s" % name
    print("vectors %d; graphs %d (%d without points b != 0), vertical lines %d, special points %d"
          % (len(VECTORS), len(graphs), len(skipped), len(lines), len(special)), flush=True)
    recs = []
    for kind, name, pt in todo:
        reps, pairs, triads = pool(pt)
        n = len(reps)
        col = R.colourable(range(n), pairs, triads)
        recs.append({"kind": kind, "name": name, "x": pt.label(), "approx": pt.approx(),
                     "rays": n, "pairs": len(pairs), "triads": len(triads), "colourable": col})
        if not col or kind != "point":
            print("%-7s %-44s %3d rays %4d pairs %3d triads  %s" % (
                kind, name[:44], n, len(pairs), len(triads), "colourable" if col else "UNCOLOURABLE"),
                flush=True)
    seen = {r["x"]: (r["rays"], r["pairs"], r["triads"]) for r in recs if r["kind"] == "point"}
    for lab, want in CONTROLS.items():
        assert seen.get(lab) == want, "control %s: got %s, want %s" % (lab, seen.get(lab), want)
    assert (recs[0]["rays"], recs[0]["pairs"], recs[0]["triads"]) == (145, 366, 22), recs[0]
    circ = [r for r in recs if r["name"] == graph_name((Fr(2), Fr(0), Fr(-1)))][0]
    assert (circ["rays"], circ["pairs"], circ["triads"]) == (145, 378, 34), circ
    print("controls agree: %d points, generic, modulus-2 circle" % len(CONTROLS))
    unc = [r for r in recs if not r["colourable"]]
    print("cases %d, uncolourable %d (%.0fs)" % (len(recs), len(unc), time.time() - t0))
    (HERE / "results" / "conjugate_closed_scan.json").write_text(
        json.dumps({"cases": len(recs), "graphs": len(graphs), "graphs_without_points": skipped,
                    "vertical_lines": len(lines), "special_points": len(special), "types": recs},
                   indent=1), encoding="utf-8")
    return todo, recs


def certify(budget):
    todo, recs = scan()
    out = HERE / "results" / "conjugate_closed_theorem.json"
    done = []
    mirror = {}                    # P(-x) = P(x): certify one of each pair x, -x
    for (kind, name, pt), rec in zip(todo, recs):
        if rec["colourable"]:
            continue
        me = (kind == "point", (-pt.a).key() + pt.B.key())
        if kind == "point" and (True, pt.key()) in mirror:
            src = mirror[(True, pt.key())]
            rec.update({k: v for k, v in src.items() if k not in rec}, mirror_of=src["x"])
            done.append(rec)
            continue
        reps, pairs, triads = pool(pt)
        n = len(reps)
        t0 = time.time()
        ub_set = R.greedy_min(n, pairs, triads, 60, random.Random(1034))
        exact, ub, best, it, calls, why = R.certify3(n, pairs, triads, ub_set, budget=budget,
                                                     verbose=False)
        assert not R.colourable(best, pairs, triads), "witness is colourable"
        idx = {r: k for k, r in enumerate(sorted(best))}
        wp = [(idx[i], idx[j]) for (i, j) in pairs if i in idx and j in idx]
        rec.update(status="CERTIFIED" if exact is not None else "UPPER_BOUND_ONLY",
                   certified_minimum=exact, upper_bound=ub, reason=why, iterations=it,
                   bases_in_witness=len(R.bases_of(best, triads)), witness_pairs=len(wp),
                   witness=[word_str(reps[i]) for i in sorted(best)],
                   seconds=round(time.time() - t0, 1))
        done.append(rec)
        mirror[me] = rec
        print("%-7s %-44s %3d rays: %s  (%d pairs, %d bases in witness, %.0fs)" % (
            kind, name[:44], n, ("min %d" % exact) if exact is not None else ("<= %d" % ub),
            len(wp), rec["bases_in_witness"], rec["seconds"]), flush=True)
        out.write_text(json.dumps({"uncolourable": done, "all": recs}, indent=1), encoding="utf-8")
    out.write_text(json.dumps({"uncolourable": done, "all": recs}, indent=1), encoding="utf-8")
    print("certified %d of %d" % (sum(r["status"] == "CERTIFIED" for r in done), len(done)))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "certify":
        certify(float(sys.argv[2]) if len(sys.argv) > 2 else 600.0)
    elif sys.argv[1:2] != ["one"]:
        scan()


def one(label, budget, floor=None):
    """Rerun a single case.  With `floor`, only decide whether an uncolourable subset with
    fewer than `floor` rays exists (certify3 started from a dummy upper bound of that size)."""
    todo, graphs, lines, special, skipped = cases()
    (kind, name, pt), = [t for t in todo if t[2].label() == label]
    reps, pairs, triads = pool(pt)
    n = len(reps)
    t0 = time.time()
    if floor is None:
        ub_set = R.greedy_min(n, pairs, triads, 200, random.Random(7))
    else:
        ub_set = set(range(floor))
    exact, ub, best, it, calls, why = R.certify3(n, pairs, triads, ub_set, budget=budget,
                                                 verbose=False)
    rec = {"x": label, "rays": n, "pairs": len(pairs), "triads": len(triads),
           "reason": why, "iterations": it, "seconds": round(time.time() - t0, 1)}
    if floor is None:
        rec.update(certified=exact, upper_bound=ub)
    else:                       # a floor run proves a lower bound only; it has no witness
        rec.update(threshold=floor, proven_lower_bound=floor if exact is not None else None)
    if floor is None or len(best) < floor:
        assert not R.colourable(best, pairs, triads)
        rec["witness"] = [word_str(reps[i]) for i in sorted(best)]
    print(json.dumps({k: v for k, v in rec.items() if k != "witness"}), flush=True)
    with (HERE / "results" / "conjugate_closed_reruns.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "one":
    one(sys.argv[2], float(sys.argv[3]), int(sys.argv[4]) if len(sys.argv) > 4 else None)
