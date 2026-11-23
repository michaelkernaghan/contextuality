"""Real three-symbol alphabets {0, +-1, +-x, +-y}: which pools are KS-uncolourable?

Reduction.  Signs are in the alphabet and rescaling does not change the pool, so a real
three-symbol alphabet with three distinct nonzero absolute values is {0, +-1, +-x, +-y} with
1 < x < y, the domain D.  (Equal absolute values or a zero letter give a two-symbol
alphabet, classified by Theorem two-symbol.)

Stratification.  Inner products and 2x2 minors of two words are integer combinations
p_c = c0 + c1 x + c2 y + c3 x^2 + c4 xy + c5 y^2 with sum |c_k| <= 3.  Factor every p_c over
Q into irreducibles f_1..f_m.  At a point P, p_c(P) = 0 iff some factor of p_c vanishes at P,
so the pool and its orthogonality graph at P depend only on the set F(P) of irreducibles
vanishing at P.  The realised sets F(P), P in D, are:
  * the empty set (D minus finitely many curves is nonempty);
  * {f} for each f whose zero set meets D in a curve (then all but finitely many of its
    points have F = {f});
  * F(P) at each point P of D lying on two curves, or at a singular point of one curve.
A point lying on one curve only, at an isolated real point of that curve, is singular.

All decisions below are exact: real algebraic numbers are rational isolating intervals and
every sign is decided by exact rational interval arithmetic (class Root).  Floating point is
used only for cross-checks and for the coordinates printed in the output.

Curves in D.  For each f, the x-axis is cut at the real roots of: the discriminant in y,
the leading coefficient in y, f(x, x), and at x = 1.  On each open cell the real roots in y
are continuous, distinct and do not cross y = x, so one rational sample per cell decides
whether f has a branch in D.  Vertical lines x = a are handled directly.

Special points.  For each pair (f, g) whose resultant in y has a real root x >= 1 (Sturm
count), and for each f with its two partial derivatives, the finite variety is split into
prime components {(hx(t), hy(t)) : q(t) = 0}, q irreducible over Q, by a separating linear
form t = x + s y after making the ideal radical (function components).  A factor h vanishes
on a component iff q divides h(hx, hy); membership of D is decided by exact signs at each
real root of q.  Every point is also evaluated to 60 digits; any disagreement stops the
script.

Usage:  python ks_three_symbol_real.py scan | check | certify <budget> <workers> | witness
Writes: results/three_symbol_real_scan.json, results/three_symbol_real_certify.jsonl,
        results/three_symbol_real_witnesses.json
"""
import itertools
import json
import sys
import time
from fractions import Fraction
from pathlib import Path

import mpmath as mp
import sympy as sp
from pysat.solvers import Glucose4

HERE = Path(__file__).resolve().parent
mp.mp.dps = 60
X, Y = sp.symbols("x y")
MON = [sp.Integer(1), X, Y, X ** 2, X * Y, Y ** 2]
LET = [None, (1, 0), (-1, 0), (1, 1), (-1, 1), (1, 2), (-1, 2)]   # (sign, 0=1 / 1=x / 2=y)
PM = {(0, 0): 0, (0, 1): 1, (1, 0): 1, (0, 2): 2, (2, 0): 2, (1, 1): 3, (1, 2): 4,
      (2, 1): 4, (2, 2): 5}
WORDS = [w for w in itertools.product(LET, repeat=3) if any(a is not None for a in w)]
ZERO6 = (0,) * 6


def inner_vec(u, v):
    c = [0] * 6
    for a, b in zip(u, v):
        if a and b:
            c[PM[(a[1], b[1])]] += a[0] * b[0]
    return tuple(c)


def minor_vec(u, v, i, j):
    c = [0] * 6
    for (a, b), s in (((u[i], v[j]), 1), ((u[j], v[i]), -1)):
        if a and b:
            c[PM[(a[1], b[1])]] += s * a[0] * b[0]
    return tuple(c)


def all_vectors():
    vecs = set()
    for u in WORDS:
        for v in WORDS:
            vecs.add(inner_vec(u, v))
            for i, j in ((0, 1), (0, 2), (1, 2)):
                vecs.add(minor_vec(u, v, i, j))
    vecs.discard(ZERO6)
    return sorted(vecs)


def norm_poly(f):
    p = sp.Poly(f, X, Y)
    p = p.primitive()[1]
    return p if p.LC() > 0 else -p


def factorise(vecs):
    """Irreducible factors (as sympy Polys) and, per vector, the indices of its factors."""
    irr, index, fac = [], {}, {}
    for c in vecs:
        p = sum(ci * m for ci, m in zip(c, MON))
        idxs = set()
        if not sp.sympify(p).is_number:
            for f, _ in sp.factor_list(p, X, Y)[1]:
                q = norm_poly(f)
                if q.total_degree() == 0:
                    continue
                key = q.as_expr()
                if key not in index:
                    index[key] = len(irr)
                    irr.append(q)
                idxs.add(index[key])
        fac[c] = frozenset(idxs)
    return irr, fac


# ---------------------------------------------------------------------------------------
# Exact real algebraic numbers.  A real root of a squarefree rational polynomial is kept as
# a rational isolating interval [lo, hi] (lo == hi for a rational root); all decisions about
# signs are made with exact rational interval arithmetic, refining until they are decided.
# No floating-point number enters any decision below.
# ---------------------------------------------------------------------------------------
T = sp.Symbol("t")


def qcoeffs(expr, var):
    """Coefficients (highest first) of a univariate rational polynomial, as Fractions."""
    return [Fraction(int(sp.fraction(c)[0]), int(sp.fraction(c)[1]))
            for c in sp.Poly(expr, var).all_coeffs()]


def ev(cs, t):
    acc = Fraction(0)
    for c in cs:
        acc = acc * t + c
    return acc


def ev_iv(cs, lo, hi):
    """An interval containing {p(t) : lo <= t <= hi} (naive Horner interval arithmetic)."""
    a = b = Fraction(0)
    for c in cs:
        prods = (a * lo, a * hi, b * lo, b * hi)
        a, b = min(prods) + c, max(prods) + c
    return a, b


class Root:
    """The unique root of the squarefree polynomial `cs` in [lo, hi]."""

    def __init__(self, cs, lo, hi):
        self.cs, self.lo, self.hi = cs, Fraction(lo), Fraction(hi)
        if self.lo < self.hi:
            a, b = ev(cs, self.lo), ev(cs, self.hi)
            assert a != 0 and b != 0 and (a > 0) != (b > 0), "not an isolating interval"

    def refine(self, width):
        while self.hi - self.lo > width:
            mid = (self.lo + self.hi) / 2
            v = ev(self.cs, mid)
            if v == 0:
                self.lo = self.hi = mid
            elif (v > 0) == (ev(self.cs, self.lo) > 0):
                self.lo = mid
            else:
                self.hi = mid
        return self

    def sign_of(self, hcs):
        """Sign of h at this root, where h(root) != 0 has been established exactly."""
        while True:
            a, b = ev_iv(hcs, self.lo, self.hi)
            if a > 0:
                return 1
            if b < 0:
                return -1
            if self.lo == self.hi:
                raise AssertionError("h vanishes at a rational root")
            self.refine((self.hi - self.lo) / 4)

    def gt(self, q):
        """root > q for a rational q (exact)."""
        q = Fraction(q)
        if ev(self.cs, q) == 0 and self.lo <= q <= self.hi:
            return False
        while self.lo <= q <= self.hi and self.lo < self.hi:
            self.refine((self.hi - self.lo) / 4)
        return self.lo > q

    def mp(self, digits=60):
        self.refine(Fraction(1, 10 ** (digits + 5)))
        m = (self.lo + self.hi) / 2
        return mp.mpf(m.numerator) / m.denominator


def roots_of(expr, var):
    """Real roots of a nonzero polynomial, sorted, with pairwise disjoint intervals."""
    P = sp.Poly(expr, var)
    if P.degree() <= 0:
        return []
    rs = []
    # Isolate each irreducible factor on its own: sympy's intervals for a product may have
    # an endpoint at a root of another factor, but an irreducible factor of degree >= 2 has
    # no rational root, so its interval endpoints are never roots of it.
    for fct, _ in P.factor_list()[1]:
        cs = qcoeffs(fct.as_expr(), var)
        rs += [Root(cs, Fraction(str(a)), Fraction(str(b))) for (a, b), _ in fct.intervals()]
    while True:                                             # sort and make disjoint
        rs.sort(key=lambda r: r.lo)
        clash = [(r, s) for r, s in zip(rs, rs[1:]) if r.hi >= s.lo]
        if not clash:
            return rs
        for r, s in clash:
            r.refine((r.hi - r.lo) / 4)
            s.refine((s.hi - s.lo) / 4)


def cell_samples(crit_expr):
    """Rational points, one in each open cell of (1, oo) cut by the real roots of crit_expr
    (which must vanish at x = 1), with the cell bounds (hi = None for the last cell)."""
    rs = [r for r in roots_of(crit_expr, X) if r.hi >= 1]
    out = []
    for r, s in zip(rs, rs[1:]):
        out.append((r.hi, s.lo))
    out.append((rs[-1].hi, None))
    return [(a, b) for a, b in out if a >= 1]


def branch_in_D(f):
    """Does the zero set of the irreducible f meet D = {1 < x < y} in a curve?  Returns an
    exact sample {"x": Fraction or Root, "y": Root or Fraction, "gy": poly} or None.

    Non-vertical f: cut x > 1 at the real roots of x - 1, the leading coefficient in y, the
    discriminant in y and f(x, x).  On each open cell the real roots in y are continuous,
    distinct, bounded, and never equal x, so whether some root exceeds x is constant on the
    cell and is decided exactly at one rational point of it."""
    fe = f.as_expr()
    if f.degree(Y) == 0:                                   # vertical line(s) f(x) = 0
        for r in roots_of(fe, X):
            if r.gt(1):
                return {"x": r, "y": None, "vertical": True}
        return None
    diag = sp.expand(fe.subs(Y, X))
    if diag == 0:
        return None                                        # f = y - x: the edge of D
    crit = (X - 1) * sp.Poly(fe, Y).LC()
    if f.degree(Y) == 2:
        crit *= sp.discriminant(fe, Y)
    crit = sp.expand(crit * diag)
    for a, b in cell_samples(crit):
        x0 = (a + b) / 2 if b is not None else a + 1
        assert x0 > 1 and ev(qcoeffs(crit, X), x0) != 0
        g = sp.Poly(fe.subs(X, sp.Rational(x0.numerator, x0.denominator)), Y)
        for gi, _ in g.factor_list()[1]:
            for r in roots_of(gi.as_expr(), Y):
                if r.gt(x0):
                    return {"x": x0, "y": r, "gy": gi.as_expr(), "vertical": False,
                            "cell": (a, b)}
    return None


def poly_in_T(e):
    return not e.has(X) and not e.has(Y)


def components(exprs):
    """Prime components of the finite variety V(exprs) as (q, hx, hy): q irreducible over Q
    in t, and the points of the component are (hx(t), hy(t)) at the roots t of q.

    Method: add the squarefree parts of the eliminants in x, y and t = x + s y.  The ideal is
    then radical (Seidenberg's lemma), so for a separating s its reduced lex basis is
    {x - hx(t), y - hy(t), q(t)} (shape lemma); s = 1, 2, ... until it has that shape."""
    exprs = [sp.expand(e) for e in exprs]
    ex = sp.groebner(exprs, Y, X, order="lex")
    if ex.exprs == [1]:
        return []
    px = [p for p in ex.exprs if not p.has(Y)]
    py = [p for p in sp.groebner(exprs, X, Y, order="lex").exprs if not p.has(X)]
    if not px or not py:
        raise RuntimeError("positive-dimensional variety: %s" % exprs)
    sqf = lambda p, v: sp.Poly(p, v).sqf_part().as_expr()                 # noqa: E731
    for s in range(1, 40):
        lin = T - X - s * Y
        Gt = sp.groebner(exprs + [lin], X, Y, T, order="lex")
        pt = [p for p in Gt.exprs if poly_in_T(p)]
        G = sp.groebner(exprs + [lin, sqf(px[0], X), sqf(py[0], Y), sqf(pt[0], T)],
                        X, Y, T, order="lex")
        es = G.exprs
        if len(es) != 3:
            continue
        hx = hy = q = None
        for e in es:
            if poly_in_T(e):
                q = e
            elif (not e.has(Y) and sp.Poly(e, X).degree() == 1
                  and sp.sympify(sp.Poly(e, X).LC()).is_number):
                lc = sp.Poly(e, X).LC()
                hx = sp.expand(X - e / lc)
            elif (not e.has(X) and sp.Poly(e, Y).degree() == 1
                  and sp.sympify(sp.Poly(e, Y).LC()).is_number):
                lc = sp.Poly(e, Y).LC()
                hy = sp.expand(Y - e / lc)
        if None in (hx, hy, q) or hx.has(X) or hy.has(Y):
            continue
        out = []
        for qi, _ in sp.factor_list(q, T)[1]:
            out.append((qi, sp.rem(hx, qi, T), sp.rem(hy, qi, T)))
        return out
    raise RuntimeError("no separating element found for %s" % exprs)


def special_sets(irr):
    """Realised sets F(P) at points P of D on two curves or singular on one.  Exact: a factor
    h vanishes on a component (q, hx, hy) iff q divides h(hx, hy); membership of D is decided
    by exact signs.  Each point is also evaluated to 60 digits as a cross-check."""
    found = {}
    exprs = [h.as_expr() for h in irr]
    evals = [sp.lambdify((X, Y), e, "mpmath") for e in exprs]

    def record(comp, label):
        q, hx, hy = comp
        dx, dyx = sp.rem(hx - 1, q, T), sp.rem(hy - hx, q, T)
        if dx == 0 or dyx == 0:
            return                                          # on x = 1 or y = x: not in D
        hxs, hys, dxs, dyxs = (qcoeffs(e, T) for e in (hx, hy, dx, dyx))
        F = None
        for r in roots_of(q, T):
            if r.sign_of(dxs) < 0 or r.sign_of(dyxs) < 0:
                continue
            if F is None:
                F = frozenset(k for k, e in enumerate(exprs)
                              if sp.rem(sp.expand(e.subs({X: hx, Y: hy}, simultaneous=True)),
                                        q, T) == 0)
            r.refine(Fraction(1, 10 ** 70))
            lo_x, hi_x = ev_iv(hxs, r.lo, r.hi)
            lo_y, hi_y = ev_iv(hys, r.lo, r.hi)
            px = mp.mpf((lo_x + hi_x).numerator) / (2 * (lo_x + hi_x).denominator)
            py = mp.mpf((lo_y + hi_y).numerator) / (2 * (lo_y + hi_y).denominator)
            num = frozenset(k for k, h in enumerate(evals) if abs(h(px, py)) < mp.mpf(10) ** -40)
            if num != F:
                raise RuntimeError("exact/numeric mismatch at %s from %s: %s vs %s"
                                   % ((px, py), label, sorted(F), sorted(num)))
            found.setdefault(F, (float(px), float(py), label, mp.nstr(px, 55),
                                 mp.nstr(py, 55)))

    for i, j in itertools.combinations(range(len(irr)), 2):
        f, g = exprs[i], exprs[j]
        res = sp.resultant(f, g, Y)
        if sp.sympify(res).is_number:
            if res != 0:
                continue
        elif sp.Poly(res, X).count_roots(1, None) == 0:      # exact (Sturm): no x >= 1
            continue
        for comp in components([f, g]):
            record(comp, "f%d & f%d" % (i, j))
    for i, f in enumerate(exprs):                           # singular points of one curve
        if irr[i].total_degree() < 2:
            continue
        for comp in components([f, sp.diff(f, X), sp.diff(f, Y)]):
            record(comp, "singular point of f%d" % i)
    return found


def pool(F, fac):
    van = lambda c: c == ZERO6 or bool(fac[c] & F)          # noqa: E731
    reps = []
    for w in WORDS:
        if not any(all(van(minor_vec(w, r, i, j)) for i, j in ((0, 1), (0, 2), (1, 2)))
                   for r in reps):
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


def colourable(n, pairs, triads):
    s = Glucose4()
    for i, j in pairs:
        s.add_clause([-(i + 1), -(j + 1)])
    for t in triads:
        s.add_clause([r + 1 for r in t])
    ok = s.solve()
    s.delete()
    return ok


def word_str(w):
    return "(" + ",".join("0" if a is None else ("-" if a[0] < 0 else "") + "1xy"[a[1]]
                          for a in w) + ")"


def scan():
    t0 = time.time()
    vecs = all_vectors()
    irr, fac = factorise(vecs)
    print("%d vectors, %d irreducible factors (%.0fs)" % (len(vecs), len(irr), time.time() - t0),
          flush=True)
    curves = {}
    for k, f in enumerate(irr):
        s = branch_in_D(f)
        if s is not None:
            x0 = float(s["x"].mp(20)) if isinstance(s["x"], Root) else float(s["x"])
            curves[k] = (x0, x0 + 1.0) if s["vertical"] else (x0, float(s["y"].mp(20)))
    print("%d curves meet D (%.0fs)" % (len(curves), time.time() - t0), flush=True)
    special = special_sets(irr)
    print("%d distinct special sets F(P) (%.0fs)" % (len(special), time.time() - t0), flush=True)
    cases = [("generic", frozenset(), None)]
    cases += [("curve", frozenset([k]), curves[k]) for k in sorted(curves)]
    cases += [("point", F, special[F]) for F in sorted(special, key=sorted)]
    out = []
    for kind, F, sample in cases:
        reps, pairs, triads = pool(F, fac)
        col = colourable(len(reps), pairs, triads)
        rec = {"kind": kind, "factors": [str(irr[k].as_expr()) for k in sorted(F)],
               "sample": sample, "rays": len(reps), "pairs": len(pairs),
               "triads": len(triads), "colourable": col}
        out.append(rec)
        if not col:
            print("  UNCOLOURABLE", kind, rec["factors"], sample, len(reps), len(pairs),
                  len(triads), flush=True)
    summary = {"vectors": len(vecs), "irreducible": [str(f.as_expr()) for f in irr],
               "curves_in_D": len(curves), "special_sets": len(special),
               "cases": len(out), "uncolourable": sum(not r["colourable"] for r in out),
               "seconds": round(time.time() - t0, 1)}
    print(json.dumps(summary["cases"]), summary["uncolourable"], "uncolourable", flush=True)
    (HERE / "results" / "three_symbol_real_scan.json").write_text(
        json.dumps({"summary": summary, "cases": out}, indent=1), encoding="utf-8")


def graph_of(prop, orth):
    """Canonical graph: the partition of WORDS into rays (as frozensets of word strings) and
    the set of orthogonal pairs of rays (each ray named by its smallest word string)."""
    reps, members = [], []
    for w in WORDS:
        for k, r in enumerate(reps):
            if prop(w, r):
                members[k].append(w)
                break
        else:
            reps.append(w)
            members.append([w])
    names = [min(word_str(w) for w in m) for m in members]
    edges = frozenset(frozenset((names[i], names[j])) for i in range(len(reps))
                      for j in range(i + 1, len(reps)) if orth(reps[i], reps[j]))
    part = frozenset(frozenset(word_str(w) for w in m) for m in members)
    return part, edges


def exact_graph(F, fac):
    van = lambda c: c == ZERO6 or bool(fac[c] & F)          # noqa: E731
    return graph_of(lambda u, v: all(van(minor_vec(u, v, i, j))
                                     for i, j in ((0, 1), (0, 2), (1, 2))),
                    lambda u, v: van(inner_vec(u, v)))


def numeric_graph(px, py):
    """The same object from coordinates (60 digits), with no use of the factorisation."""
    val = [mp.mpf(1), px, py]
    vec = lambda w: [0 if a is None else a[0] * val[a[1]] for a in w]   # noqa: E731
    tiny = mp.mpf(10) ** -40
    return graph_of(lambda u, v: all(abs(vec(u)[i] * vec(v)[j] - vec(u)[j] * vec(v)[i]) < tiny
                                     for i, j in ((0, 1), (0, 2), (1, 2))),
                    lambda u, v: abs(sum(a * b for a, b in zip(vec(u), vec(v)))) < tiny)


def curve_point(k, irr):
    """An exact point of D on curve k at which no other factor vanishes, as 60-digit
    coordinates, or None.  Tries several rational abscissae in every cell."""
    exprs = [h.as_expr() for h in irr]
    fe = exprs[k]
    s = branch_in_D(irr[k])
    if s is None:
        return None
    if s["vertical"]:
        r = s["x"]
        for m in range(1, 40):
            y0 = r.hi + 1 + Fraction(m, 7)
            ys = sp.Rational(y0.numerator, y0.denominator)
            F = {j for j, e in enumerate(exprs) if sp.rem(sp.expand(e.subs(Y, ys)), fe, X) == 0}
            if F == {k}:
                return r.mp(), mp.mpf(y0.numerator) / y0.denominator
        return None
    crit = (X - 1) * sp.Poly(fe, Y).LC()
    if irr[k].degree(Y) == 2:
        crit *= sp.discriminant(fe, Y)
    crit = sp.expand(crit * sp.expand(fe.subs(Y, X)))
    ccs = qcoeffs(crit, X)
    for a, b in cell_samples(crit):
        for m in range(1, 17):
            x0 = a + (b - a) * Fraction(m, 17) if b is not None else a + m
            if ev(ccs, x0) == 0:
                continue
            xs = sp.Rational(x0.numerator, x0.denominator)
            g = sp.Poly(fe.subs(X, xs), Y)
            for gi, _ in g.factor_list()[1]:
                for r in roots_of(gi.as_expr(), Y):
                    if not r.gt(x0):
                        continue
                    F = {j for j, e in enumerate(exprs)
                         if sp.rem(sp.expand(e.subs(X, xs)), gi.as_expr(), Y) == 0}
                    if F == {k}:
                        return mp.mpf(x0.numerator) / x0.denominator, r.mp()
    return None


def check():
    """Rebuild every case's graph from a sample point's coordinates and compare it, ray
    partition and edge set, with the graph built from the factorisation."""
    vecs = all_vectors()
    irr, fac = factorise(vecs)
    d = json.loads((HERE / "results" / "three_symbol_real_scan.json").read_text(encoding="utf-8"))
    names = {str(f.as_expr()): k for k, f in enumerate(irr)}
    evals = [sp.lambdify((X, Y), h.as_expr(), "mpmath") for h in irr]
    done = bad = 0
    for rec in d["cases"]:
        F = frozenset(names[s] for s in rec["factors"])
        if rec["kind"] == "generic":
            pt = (mp.mpf(13) / 11, mp.sqrt(mp.mpf(5)))
        elif rec["kind"] == "curve":
            (k,) = F
            pt = curve_point(k, irr)
            if pt is None:
                print("NO SAMPLE on curve", rec["factors"], flush=True)
                bad += 1
                continue
        else:
            pt = (mp.mpf(rec["sample"][3]), mp.mpf(rec["sample"][4]))
        Fnum = frozenset(k for k, h in enumerate(evals) if abs(h(*pt)) < mp.mpf(10) ** -40)
        if Fnum != F:
            print("SAMPLE NOT IN STRATUM", rec["kind"], rec["factors"], sorted(Fnum), flush=True)
            bad += 1
            continue
        same = exact_graph(F, fac) == numeric_graph(*pt)
        done += 1
        bad += not same
        if not same:
            print("MISMATCH", rec["kind"], rec["factors"], flush=True)
    print("%d cases, %d graphs compared (ray partition and edge set), %d failures"
          % (len(d["cases"]), done, bad), flush=True)
    return bad


def symmetries(F, fac, reps):
    """Ray permutations from coordinate permutations and sign changes (valid at every point;
    certify4 checks each against the graph)."""
    van = lambda c: c == ZERO6 or bool(fac[c] & F)          # noqa: E731

    def rep_of(w):
        for i, r in enumerate(reps):
            if all(van(minor_vec(w, r, a, b)) for a, b in ((0, 1), (0, 2), (1, 2))):
                return i
        raise AssertionError("word outside the pool")

    perms = set()
    for sigma in itertools.permutations(range(3)):
        for signs in itertools.product((1, -1), repeat=3):
            def act(w):
                return tuple(None if w[sigma[k]] is None
                             else (w[sigma[k]][0] * signs[k], w[sigma[k]][1]) for k in range(3))
            perms.add(tuple(rep_of(act(w)) for w in reps))
    return sorted(perms)


def certify_case(args):
    """Worker: exact minimum within `budget` seconds from a greedy upper bound; if that does
    not terminate, a run that only decides whether a set of fewer than 31 rays exists."""
    import random
    import ks_certify_fast4 as F4
    import ks_recertify_v10 as R
    key, factors, budget = args
    vecs = all_vectors()
    irr, fac = factorise(vecs)
    names = {str(f.as_expr()): k for k, f in enumerate(irr)}
    F = frozenset(names[s] for s in factors)
    reps, pairs, triads = pool(F, fac)
    n = len(reps)
    perms = symmetries(F, fac, reps)
    rec = {"key": key, "factors": factors, "rays": n, "pairs": len(pairs),
           "triads": len(triads)}
    # 1. Is there an uncolourable subset of fewer than 31 rays?  (exact == 31: no.)
    e31, _, b31, info31 = F4.certify4(n, pairs, triads, 31, budget=budget, perms=perms)
    rec["floor31_run"] = info31
    rec["no_set_below_31"] = e31 == 31
    if e31 is not None and e31 < 31:                       # would be a new record: keep it
        assert not R.colourable(b31, pairs, triads)
        rec["witness_below_31"] = [word_str(reps[i]) for i in sorted(b31)]
    # 2. The exact minimum, from a greedy upper bound.
    greedy = R.greedy_min(n, pairs, triads, 200, random.Random(7))
    ub0 = len(greedy)
    exact, ub, best, info = F4.certify4(n, pairs, triads, ub0, budget=budget, perms=perms)
    rec.update(greedy_ub=ub0, certified=exact, upper_bound=ub, exact_run=info)
    if best is None:                       # the certifier never improved on the greedy set
        best = greedy
    assert len(best) == ub and not R.colourable(best, pairs, triads)
    rec["witness"] = [word_str(reps[i]) for i in sorted(best)]
    return rec


def witness():
    """Witnesses for the certified minima, without rerunning the certifier: the greedy set
    of certify_case (same seed, same pool order) for every case where the certifier did not
    improve on it.  Each is checked uncolourable and of the certified size."""
    import random
    import ks_recertify_v10 as R
    vecs = all_vectors()
    irr, fac = factorise(vecs)
    names = {str(f.as_expr()): k for k, f in enumerate(irr)}
    out = []
    for line in (HERE / "results" / "three_symbol_real_certify.jsonl").read_text(
            encoding="utf-8").splitlines():
        rec = json.loads(line)
        reps, pairs, triads = pool(frozenset(names[s] for s in rec["factors"]), fac)
        if "witness" in rec:
            ws = rec["witness"]
            idx = [i for i, w in enumerate(reps) if word_str(w) in set(ws)]
        else:
            assert rec["certified"] == rec["greedy_ub"], rec["factors"]
            idx = R.greedy_min(len(reps), pairs, triads, 200, random.Random(7))
            ws = [word_str(reps[i]) for i in sorted(idx)]
        sub = set(idx)
        sp_ = [p for p in pairs if p[0] in sub and p[1] in sub]
        st = [t for t in triads if set(t) <= sub]
        ok = len(sub) == rec["certified"] and not R.colourable(idx, pairs, triads)
        print(rec["certified"], len(sub), "uncolourable" if ok else "FAILED", rec["factors"],
              flush=True)
        assert ok
        out.append({"factors": rec["factors"], "minimum": rec["certified"], "witness": ws,
                    "pairs": len(sp_), "triads": len(st)})
    (HERE / "results" / "three_symbol_real_witnesses.json").write_text(
        json.dumps(out, indent=1), encoding="utf-8")
    print("%d witnesses written" % len(out), flush=True)


def certify(budget, workers):
    from multiprocessing import Pool
    d = json.loads((HERE / "results" / "three_symbol_real_scan.json").read_text(encoding="utf-8"))
    todo = [(k, r["factors"], budget) for k, r in enumerate(d["cases"]) if not r["colourable"]]
    print("%d uncolourable cases, %d workers, budget %ss each run" % (len(todo), workers, budget),
          flush=True)
    out_path = HERE / "results" / "three_symbol_real_certify.jsonl"
    with Pool(workers) as p:
        for rec in p.imap_unordered(certify_case, todo):
            print(json.dumps({k: v for k, v in rec.items() if "witness" not in k
                              and not k.endswith("_run")}), flush=True)
            with out_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec) + "\n")


if __name__ == "__main__" and sys.argv[1:2] == ["scan"]:
    scan()

if __name__ == "__main__" and sys.argv[1:2] == ["check"]:
    sys.exit(1 if check() else 0)

if __name__ == "__main__" and sys.argv[1:2] == ["certify"]:
    certify(float(sys.argv[2]), int(sys.argv[3]))

if __name__ == "__main__" and sys.argv[1:2] == ["witness"]:
    witness()
