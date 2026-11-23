"""v10 Theorem (two-symbol alphabets): every pool S({0, +-1, +-x}), x complex, x != 0.

The orthogonality graph of the pool depends on x only through

  (a) which inner products  c0 + c1 x + c2 x* + c3 |x|^2  vanish, where c runs over the
      128 nonzero integer vectors with |c0|+|c1|+|c2|+|c3| <= 3, and
  (b) which words are proportional (2x2 minors, polynomials m0 + m1 x + m2 x^2).

With x = a + ib the vanishing set of one vector c is  (c1-c2) b = 0  and
c0 + (c1+c2) a + c3 (a^2+b^2) = 0:  the real axis, a vertical line, a circle centred on
the real axis, finitely many real points, or nothing.  So the plane is cut into

  * the complement of all curves                (one type: no relation holds),
  * each curve minus finitely many points       (one type per curve),
  * finitely many special points                (real roots, and intersections of curves).

Off the special points, the vectors that vanish at a point of a curve C are exactly the
vectors whose locus is C; this is asserted below at an exact sample point of each curve.
The script lists every curve and every special point, builds the pool at each in exact
arithmetic, decides colourability, and certifies the minimum uncolourable subset with
ks_certify_fast3.certify3.

Exact arithmetic: a point is (a, B) with a in Q(sqrt d) and B = b^2 rational (B > 0 only
when a is rational).  The sign of b is not recorded: conjugating every coordinate maps the
pool of x to the pool of x* and preserves orthogonality, so the two graphs are equal.

Usage:  python ks_two_symbol_theorem.py [budget-seconds]
Writes: results/two_symbol_theorem.json; prints one line per symmetry class (paper Table 3).
"""
import itertools
import json
import random
import sys
import time
from fractions import Fraction as Fr
from math import isqrt
from pathlib import Path

import ks_recertify_v10 as R

HERE = Path(__file__).resolve().parent


# ---------------------------------------------------------------- Q(sqrt d) helpers
def squarefree_sqrt(q):
    """sqrt of a rational q >= 0 as (r, d): sqrt(q) = r * sqrt(d), d squarefree, d >= 1."""
    n, m = q.numerator * q.denominator, q.denominator      # sqrt(q) = sqrt(n) / m
    r, d = 1, n
    f = 2
    while f * f <= d:
        while d % (f * f) == 0:
            d //= f * f
            r *= f
        f += 1
    if n == 0:
        return Fr(0), 1
    return Fr(r, m), d


class Pt:
    """x = a + i sqrt(B), a = p + q sqrt(d)."""

    def __init__(self, p, q=0, d=1, B=0):
        self.p, self.q, self.d, self.B = Fr(p), Fr(q), d, Fr(B)
        if self.q == 0:
            self.d = 1
        assert self.B >= 0 and (self.B == 0 or self.q == 0)

    def key(self):
        return (self.p, self.q, self.d, self.B)

    def a2(self):                                          # a^2 as (rational, sqrt-part)
        return (self.p * self.p + self.q * self.q * self.d, 2 * self.p * self.q)

    def is_zero(self):
        return self.p == 0 and self.q == 0 and self.B == 0

    def vanishes(self, c):
        """c0 + c1 x + c2 x* + c3 |x|^2 == 0, exactly."""
        c0, c1, c2, c3 = c
        if c1 != c2 and self.B != 0:
            return False
        s = c1 + c2
        r, t = self.a2()
        return c0 + s * self.p + c3 * (r + self.B) == 0 and s * self.q + c3 * t == 0

    def poly_vanishes(self, m):
        """m0 + m1 x + m2 x^2 == 0, exactly."""
        m0, m1, m2 = m
        r, t = self.a2()
        real = (m0 + m1 * self.p + m2 * (r - self.B), m1 * self.q + m2 * t)
        if real != (0, 0):
            return False
        if self.B == 0:
            return True
        return m1 + 2 * m2 * self.p == 0 and 2 * m2 * self.q == 0

    def approx(self):
        return complex(float(self.p) + float(self.q) * self.d ** 0.5, float(self.B) ** 0.5)

    def label(self):
        def rat(v):
            return str(v)
        a = rat(self.p) if self.q == 0 else (
            ("%s%s%s*sqrt(%d)" % (rat(self.p), "+" if self.q > 0 else "-", rat(abs(self.q)), self.d))
            if self.p != 0
            else "%s*sqrt(%d)" % (rat(self.q), self.d))
        if self.B == 0:
            return a
        r, d = squarefree_sqrt(self.B)
        b = "%s*i" % r if d == 1 else "%s*i*sqrt(%d)" % (r, d)
        return b if (self.p == 0 and self.q == 0) else "%s + %s" % (a, b)

    def neg(self):
        return Pt(-self.p, -self.q, self.d, self.B)

    def inv(self):
        """1/x = x* / |x|^2; returned up to conjugation."""
        if self.B != 0:                                    # a rational
            n = self.p * self.p + self.B
            return Pt(self.p / n, 0, 1, self.B / (n * n))
        n = self.p * self.p - self.q * self.q * self.d     # 1/(p+q sqrt d)
        return Pt(self.p / n, -self.q / n, self.d, 0)

    def orbit_key(self):
        """Exact key of the orbit under x -> -x, x -> 1/x (conjugation is built in)."""
        pts = [self, self.neg(), self.inv(), self.inv().neg()]
        return min(tuple(str(v) for v in z.key()) for z in pts)


# ---------------------------------------------------------------- loci of the 128 vectors
VECTORS = [c for c in itertools.product(range(-3, 4), repeat=4) if 1 <= sum(map(abs, c)) <= 3]


def locus(c):
    """('all',) | ('none',) | ('R',) | ('line', a0) | ('circle', h, r2) | ('points', [Pt..])"""
    c0, c1, c2, c3 = c
    if c1 != c2:                                           # x real, c0 + s a + c3 a^2 = 0
        s = c1 + c2
        if c3 == 0:
            if s == 0:
                return ("R",) if c0 == 0 else ("none",)
            return ("points", [Pt(Fr(-c0, s))])
        disc = Fr(s * s - 4 * c3 * c0)
        if disc < 0:
            return ("none",)
        r, d = squarefree_sqrt(disc)
        if d == 1:
            return ("points", [Pt((-s + r) / (2 * c3)), Pt((-s - r) / (2 * c3))])
        return ("points", [Pt(Fr(-s, 2 * c3), r / (2 * c3), d), Pt(Fr(-s, 2 * c3), -r / (2 * c3), d)])
    s = 2 * c1                                             # c0 + s a + c3 |x|^2 = 0
    if c3 == 0:
        if s == 0:
            return ("none",)                               # c0 != 0 here
        return ("line", Fr(-c0, s))
    h, r2 = Fr(-s, 2 * c3), Fr(s * s, 4 * c3 * c3) - Fr(c0, c3)
    if r2 < 0:
        return ("none",)
    if r2 == 0:
        return ("points", [Pt(h)])
    return ("circle", h, r2)


def real_pt(v):
    """Real point v = rational + rational*sqrt(d) given as (p, (r, d))."""
    p, (r, d) = v
    return Pt(p, r if d != 1 else 0, d) if d != 1 else Pt(p + r)


def intersect(A, B):
    ka, kb = A[0], B[0]
    if ka > kb:
        A, B, ka, kb = B, A, kb, ka
    out = []
    if (ka, kb) == ("R", "line"):
        out.append(Pt(B[1]))
    elif ka == "R" and kb == "circle":
        h, r2 = B[1], B[2]
        r, d = squarefree_sqrt(r2)
        out += [real_pt((h, (r, d))), real_pt((h, (-r, d)))]
    elif ka == "circle" and kb == "line":
        h, r2, a0 = A[1], A[2], B[1]
        Bv = r2 - (a0 - h) ** 2
        if Bv >= 0:
            out.append(Pt(a0, 0, 1, Bv))
    elif ka == "circle" and kb == "circle":
        (h1, r1), (h2, rr2) = A[1:], B[1:]
        if h1 != h2:
            a = (r1 - rr2 - h1 * h1 + h2 * h2) / (2 * (h2 - h1))
            Bv = r1 - (a - h1) ** 2
            if Bv >= 0:
                out.append(Pt(a, 0, 1, Bv))
    return out


def arrangement():
    loci = {c: locus(c) for c in VECTORS}
    curves = sorted({l for l in loci.values() if l[0] in ("R", "line", "circle")})
    special = {}
    for l in loci.values():
        if l[0] == "points":
            for p in l[1]:
                special[p.key()] = p
    for A, B in itertools.combinations(curves, 2):
        for p in intersect(A, B):
            special[p.key()] = p
    # the two points where words coincide beyond the generic pattern: x = +-1, +-i
    for p in (Pt(1), Pt(-1), Pt(0, 0, 1, 1)):
        special[p.key()] = p
    special = {k: p for k, p in special.items() if not p.is_zero()}
    return loci, curves, special


def on_curve(p, curve):
    if curve[0] == "R":
        return p.B == 0
    if curve[0] == "line":
        return p.q == 0 and p.p == curve[1]
    h, r2 = curve[1], curve[2]
    r, t = p.a2()
    return (r - 2 * h * p.p + h * h + p.B - r2 == 0) and (t - 2 * h * p.q == 0)


def sample(curve, loci, special):
    """Exact point of the curve at which exactly the vectors with this locus vanish."""
    cands = []
    for t in (Fr(1, 3), Fr(2, 7), Fr(3, 11), Fr(5, 13), Fr(7, 3), Fr(11, 5)):
        if curve[0] == "R":
            cands.append(Pt(t + 3))
        elif curve[0] == "line":
            cands.append(Pt(curve[1], 0, 1, t + 3))
        else:
            h, r2 = curve[1], curve[2]
            if r2 - t * t > 0:
                cands.append(Pt(h + t, 0, 1, r2 - t * t))
    want = {c for c, l in loci.items() if l == curve}
    for p in cands:
        if p.key() in special:
            continue
        if {c for c in VECTORS if p.vanishes(c)} == want:
            return p
    raise RuntimeError("no clean sample point on %r" % (curve,))


# ---------------------------------------------------------------- the pool at a point
LETTERS = [None, (1, 0), (-1, 0), (1, 1), (-1, 1)]         # (sign, power of x); None = 0
WORDS = [w for w in itertools.product(LETTERS, repeat=3) if any(w)]


def inner_vec(u, v):
    """conj(u).v as coefficients on (1, x, x*, |x|^2)."""
    c = [0, 0, 0, 0]
    for a, b in zip(u, v):
        if a is None or b is None:
            continue
        idx = {(0, 0): 0, (0, 1): 1, (1, 0): 2, (1, 1): 3}[(a[1], b[1])]
        c[idx] += a[0] * b[0]
    return tuple(c)


def minor_vec(u, v, i, j):
    """u_i v_j - u_j v_i as coefficients on (1, x, x^2)."""
    m = [0, 0, 0]
    for (a, b), sgn in (((u[i], v[j]), 1), ((u[j], v[i]), -1)):
        if a is None or b is None:
            continue
        m[a[1] + b[1]] += sgn * a[0] * b[0]
    return tuple(m)


def pool(p):
    zero_c, zero_m = {(0, 0, 0, 0): True}, {(0, 0, 0): True}

    def vc(c):
        if c not in zero_c:
            zero_c[c] = p.vanishes(c)
        return zero_c[c]

    def vm(m):
        if m not in zero_m:
            zero_m[m] = p.poly_vanishes(m)
        return zero_m[m]

    def same_ray(u, v):
        return all(vm(minor_vec(u, v, i, j)) for i, j in ((0, 1), (0, 2), (1, 2)))

    reps = []
    for w in WORDS:
        if not any(same_ray(w, r) for r in reps):
            reps.append(w)
    n = len(reps)
    adj = [set() for _ in range(n)]
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            if vc(inner_vec(reps[i], reps[j])):
                pairs.append((i, j))
                adj[i].add(j)
                adj[j].add(i)
    triads = [(i, j, k) for (i, j) in pairs for k in adj[i] & adj[j] if k > j]
    relations = sorted(c for c in VECTORS if p.vanishes(c))
    return reps, pairs, triads, relations


def word_str(w):
    return "(" + ",".join("0" if a is None else ("-" if a[0] < 0 else "") + ("x" if a[1] else "1")
                          for a in w) + ")"


def analyse(name, kind, p, budget):
    reps, pairs, triads, relations = pool(p)
    n = len(reps)
    rec = {"type": name, "kind": kind, "x": p.label(), "x_approx": [round(p.approx().real, 6),
                                                                   round(p.approx().imag, 6)],
           "relations_holding": len(relations), "rays": n, "pairs": len(pairs),
           "triads": len(triads), "orbit": list(p.orbit_key())}
    if R.colourable(range(n), pairs, triads):
        rec["status"] = "COLOURABLE"
    else:
        ub_set = R.greedy_min(n, pairs, triads, 60, random.Random(1034))
        exact, ub, best, it, calls, why = R.certify3(n, pairs, triads, ub_set, budget=budget,
                                                     verbose=False)
        assert not R.colourable(best, pairs, triads), "witness is colourable"
        rec.update(status="CERTIFIED" if exact is not None else "UPPER_BOUND_ONLY",
                   certified_minimum=exact, upper_bound=ub, reason=why, iterations=it,
                   bases_in_witness=len(R.bases_of(best, triads)),
                   witness=[word_str(reps[i]) for i in sorted(best)])
        idx = {r: k for k, r in enumerate(sorted(best))}
        rec["_witness_pairs"] = [(idx[i], idx[j]) for (i, j) in pairs if i in idx and j in idx]
    print("%-34s %-9s %3d rays %4d pairs %3d triads  %s" % (
        p.label(), kind, n, len(pairs), len(triads),
        rec["status"] if rec["status"] == "COLOURABLE" else
        ("min %s" % rec["certified_minimum"] if rec["certified_minimum"] else "<= %d" % rec["upper_bound"])),
        flush=True)
    return rec


def curve_name(c):
    if c[0] == "R":
        return "Im x = 0"
    if c[0] == "line":
        return "Re x = %s" % c[1]
    return "|x%s|^2 = %s" % ("" if c[1] == 0 else (" - %s" % c[1] if c[1] > 0 else " + %s" % -c[1]), c[2])


CONTROLS = {            # (rays, pairs, triads) from the independent number-field build
    "2": (49, 138, 26), "1*sqrt(2)": (49, 120, 16), "1*i*sqrt(2)": (49, 120, 16),
    "1/2+1/2*sqrt(5)": (49, 138, 10), "1*i": (31, 69, 7), "1": (13, 24, 4),
}


def main():
    budget = float(sys.argv[1]) if len(sys.argv) > 1 else 600.0
    t0 = time.time()
    loci, curves, special = arrangement()
    kinds = {}
    for l in loci.values():
        kinds[l[0]] = kinds.get(l[0], 0) + 1
    print("vectors %d: %s" % (len(VECTORS), kinds))
    print("curves %d, special points %d" % (len(curves), len(special)))

    recs = []
    generic = Pt(Fr(1, 3), 0, 1, Fr(1, 5))
    assert not any(generic.vanishes(c) for c in VECTORS)
    recs.append(analyse("generic", "generic", generic, budget))
    for c in curves:
        p = sample(c, loci, special)
        rec = analyse(curve_name(c), "curve", p, budget)
        rec["curve"] = curve_name(c)
        recs.append(rec)
    for k in sorted(special, key=lambda k: (special[k].approx().imag, special[k].approx().real)):
        p = special[k]
        rec = analyse(p.label(), "point", p, budget)
        rec["curves_through"] = [curve_name(c) for c in curves if on_curve(p, c)]
        recs.append(rec)

    # positive controls: counts must agree with the number-field construction of the paper
    seen = {r["x"]: (r["rays"], r["pairs"], r["triads"]) for r in recs if r["kind"] == "point"}
    for lab, want in CONTROLS.items():
        assert seen.get(lab) == want, "control %s: got %s, want %s" % (lab, seen.get(lab), want)
    assert (recs[1 + curves.index(("R",))]["rays"], recs[1 + curves.index(("R",))]["pairs"],
            recs[1 + curves.index(("R",))]["triads"]) == (49, 114, 10)
    print("controls agree (%d points, generic real line)" % len(CONTROLS))

    unc = [r for r in recs if r["status"] != "COLOURABLE"]
    assert all(r["status"] == "CERTIFIED" for r in unc), "an uncolourable pool was not certified"

    # identify the minimum set found in each uncolourable pool with the named sets (VF2)
    import networkx as nx
    import ks_extras_v10 as E
    named = {k: E.graph(k) for k in ("ck31", "peres33", "sqrtm2-33", "eisenstein33", "ck33")}
    for r in unc:
        g = nx.Graph()
        g.add_nodes_from(range(len(r["witness"])))
        g.add_edges_from(r.pop("_witness_pairs"))
        r["witness_pairs"] = g.number_of_edges()
        r["witness_isomorphic_to"] = [k for k, h in named.items()
                                      if h.number_of_nodes() == g.number_of_nodes()
                                      and nx.is_isomorphic(g, h)]
        print("  %-22s min %d: %d pairs, %d bases, isomorphic to %s" % (
            r["x"], r["certified_minimum"], r["witness_pairs"], r["bases_in_witness"],
            r["witness_isomorphic_to"]))
    mins = sorted({r["certified_minimum"] for r in unc})
    summary = {"types": len(recs), "curves": len(curves), "special_points": len(special),
               "uncolourable_types": len(unc), "minima": mins,
               "attaining_minimum": [r["x"] for r in unc if r["certified_minimum"] == mins[0]],
               "seconds": round(time.time() - t0, 1)}
    print(json.dumps(summary))
    out = HERE / "results" / "two_symbol_theorem.json"
    out.write_text(json.dumps({"summary": summary, "types": recs}, indent=1), encoding="utf-8")
    print("wrote", out)

    # table: one row per orbit under x -> -x, x -> x*, x -> 1/x
    groups = {}
    for r in recs:
        key = (r["kind"],) + ((tuple(r["orbit"]),) if r["kind"] == "point" else
                              (r["rays"], r["pairs"], r["triads"], r["relations_holding"]))
        groups.setdefault(key, []).append(r)
    for key, g in groups.items():
        sig = {(r["rays"], r["pairs"], r["triads"], r["status"], r.get("certified_minimum")) for r in g}
        assert len(sig) == 1, "orbit members disagree: %s" % sorted(r["x"] for r in g)
    rows = []
    for key, g in groups.items():
        r = g[0]
        rows.append((r["kind"] != "generic", r["kind"] != "curve", -r["pairs"],
                     " ; ".join(sorted({x.get("curve", x["x"]) for x in g})), r))
    rows.sort(key=lambda t: t[:4])
    lines = ["% classes (kind | members | rays pairs triads | result):"]
    for *_, names, r in rows:
        lines.append("%% %s | %s | %d %d %d | %s" % (
            r["kind"], names, r["rays"], r["pairs"], r["triads"],
            "colourable" if r["status"] == "COLOURABLE" else "min %s" % r["certified_minimum"]))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
