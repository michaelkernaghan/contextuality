"""The 33-word family on |x|^2 = 1/2: a genuine deformation of Peres's set?

Theorem (conjugate-closed alphabets): on the circle |x|^2 = 1/2 the pool of
{0, +-1, +-x, +-x*} has a minimum uncolourable set of 33 rays with Peres's graph, given by
one fixed list of 33 words (results/conjugate_closed_theorem.json).  At x = 1/sqrt 2 the
words are Peres's set.  Questions answered here, numerically (double precision):

1. Is the orthogonality graph the same along the circle, and is it Peres's graph?
2. Are the members unitarily inequivalent to one another?  Test: the sorted list of squared
   overlaps |<u,v>|^2 of the normalised rays is invariant under unitary and antiunitary maps
   and under relabelling; if it changes with x, the members are inequivalent.
3. Infinitesimal flexes of each member (same Jacobian as ks_rigidity_v10.py).

Usage:  python ks_half_circle_family.py      Writes results/half_circle_family.json
"""
import cmath
import json
import math
from pathlib import Path

import networkx as nx
import numpy as np
from networkx.algorithms.isomorphism import GraphMatcher

import ks_extras_v10 as E
from ks_rigidity_v10 import flexes

HERE = Path(__file__).resolve().parent
CURVE = "b^2 = 1/2 + 0 a + -1 a^2"
TOL = 1e-9


def words():
    d = json.loads((HERE / "results" / "conjugate_closed_theorem.json").read_text(encoding="utf-8"))
    (rec,) = [r for r in d["uncolourable"] if r["kind"] == "curve" and r["name"] == CURVE]
    return rec["witness"]


def vector(word, x):
    out = []
    for tok in word.strip("()").split(","):
        sign = -1 if tok.startswith("-") else 1
        tok = tok.lstrip("-")
        val = {"0": 0, "1": 1, "x": x, "x*": x.conjugate()}[tok]
        out.append(sign * val)
    v = np.array(out, dtype=complex)
    return v / np.linalg.norm(v)


def member(theta, ws):
    x = cmath.exp(1j * theta) / math.sqrt(2)
    vecs = [vector(w, x) for w in ws]
    n = len(vecs)
    gram = np.array([[np.vdot(vecs[i], vecs[j]) for j in range(n)] for i in range(n)])
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n) if abs(gram[i, j]) < TOL]
    q = sorted(abs(gram[i, j]) ** 2 for i in range(n) for j in range(i + 1, n))
    return vecs, pairs, np.array(q)


def realify(vecs):
    return np.concatenate([np.concatenate([v.real, v.imag]) for v in vecs])


def trivial_motions(vecs):
    """Tangent vectors of U(3) acting on all rays and of a phase on each ray (n + 9 real
    generators spanning n + 8 dimensions)."""
    n = len(vecs)
    gens = []
    E3 = np.eye(3)
    herm = []
    for k in range(3):
        herm.append(np.outer(E3[k], E3[k]).astype(complex))
        for m in range(k + 1, 3):
            herm.append((np.outer(E3[k], E3[m]) + np.outer(E3[m], E3[k])).astype(complex))
            herm.append(1j * (np.outer(E3[k], E3[m]) - np.outer(E3[m], E3[k])))
    for H in herm:
        gens.append(realify([1j * H @ v for v in vecs]))
    for i in range(n):
        gens.append(realify([1j * vecs[j] if j == i else 0 * vecs[j] for j in range(n)]))
    return np.array(gens).T


def velocity(word, x):
    """d/dtheta of the normalised vector of `word` at x = e^{i theta}/sqrt 2: x' = i x and
    (x*)' = -i x*; the norm is constant on the circle."""
    out, norm = [], []
    for tok in word.strip("()").split(","):
        sign = -1 if tok.startswith("-") else 1
        tok = tok.lstrip("-")
        out.append(sign * {"0": 0, "1": 0, "x": 1j * x, "x*": -1j * x.conjugate()}[tok])
        norm.append(sign * {"0": 0, "1": 1, "x": x, "x*": x.conjugate()}[tok])
    return np.array(out, dtype=complex) / np.linalg.norm(np.array(norm, dtype=complex))


def velocity_at(theta, ws):
    """Is d/dtheta of the family a non-trivial flex?  Returns (rank of trivial motions, rank
    with the velocity added, relative distance of the velocity from the trivial motions,
    largest residual of the velocity in the linearised orthogonality constraints
    <w_i, v_j> + <v_i, w_j> = 0 over the orthogonal pairs)."""
    x = cmath.exp(1j * theta) / math.sqrt(2)
    v0, pairs, _ = member(theta, ws)
    wv = [velocity(w, x) for w in ws]
    w = realify(wv)
    resid = max(abs(np.vdot(wv[i], v0[j]) + np.vdot(v0[i], wv[j])) for i, j in pairs)
    T = trivial_motions(v0)
    sv = lambda A: np.linalg.svd(A, compute_uv=False)              # noqa: E731
    rT = int((sv(T) > 1e-8 * sv(T)[0]).sum())
    rTw = int((sv(np.column_stack([T, w])) > 1e-8 * sv(T)[0]).sum())
    coeff, *_ = np.linalg.lstsq(T, w, rcond=None)
    dist = float(np.linalg.norm(w - T @ coeff) / np.linalg.norm(w))
    return rT, rTw, dist, float(resid)


# Gould and Aravind, Found. Phys. 40 (2010) 1096, Table 3: the 33 rays, in terms of a, b, c
# with |a| = |b| = 1, |c|^2 = 2 and k = -a b* c / c*.  Entries are functions of
# (a, a*, b, b*, c, c*, k, k*).
GA_TABLE3 = [
    lambda a, as_, b, bs, c, cs, k, ks: (1, 0, 0),
    lambda a, as_, b, bs, c, cs, k, ks: (0, 1, 0),
    lambda a, as_, b, bs, c, cs, k, ks: (0, 0, 1),
    lambda a, as_, b, bs, c, cs, k, ks: (0, 1, a),
    lambda a, as_, b, bs, c, cs, k, ks: (0, as_, -1),
    lambda a, as_, b, bs, c, cs, k, ks: (1, 0, b),
    lambda a, as_, b, bs, c, cs, k, ks: (bs, 0, -1),
    lambda a, as_, b, bs, c, cs, k, ks: (1, k, 0),
    lambda a, as_, b, bs, c, cs, k, ks: (ks, -1, 0),
    lambda a, as_, b, bs, c, cs, k, ks: (as_ * cs, -as_, 1),
    lambda a, as_, b, bs, c, cs, k, ks: (cs, 1, a),
    lambda a, as_, b, bs, c, cs, k, ks: (-cs, 1, a),
    lambda a, as_, b, bs, c, cs, k, ks: (as_ * cs, as_, -1),
    lambda a, as_, b, bs, c, cs, k, ks: (-bs, bs * c, 1),
    lambda a, as_, b, bs, c, cs, k, ks: (1, c, b),
    lambda a, as_, b, bs, c, cs, k, ks: (1, -c, b),
    lambda a, as_, b, bs, c, cs, k, ks: (bs, bs * c, -1),
    lambda a, as_, b, bs, c, cs, k, ks: (-ks, 1, b * cs),
    lambda a, as_, b, bs, c, cs, k, ks: (1, k, -a * c),
    lambda a, as_, b, bs, c, cs, k, ks: (1, k, a * c),
    lambda a, as_, b, bs, c, cs, k, ks: (ks, -1, b * cs),
    lambda a, as_, b, bs, c, cs, k, ks: (1, 0, a * c),
    lambda a, as_, b, bs, c, cs, k, ks: (1, -c, 0),
    lambda a, as_, b, bs, c, cs, k, ks: (1, c, 0),
    lambda a, as_, b, bs, c, cs, k, ks: (1, 0, -a * c),
    lambda a, as_, b, bs, c, cs, k, ks: (0, 1, b * cs),
    lambda a, as_, b, bs, c, cs, k, ks: (-cs, 1, 0),
    lambda a, as_, b, bs, c, cs, k, ks: (cs, 1, 0),
    lambda a, as_, b, bs, c, cs, k, ks: (0, 1, -b * cs),
    lambda a, as_, b, bs, c, cs, k, ks: (0, bs * c, 1),
    lambda a, as_, b, bs, c, cs, k, ks: (as_ * cs, 0, 1),
    lambda a, as_, b, bs, c, cs, k, ks: (-as_ * cs, 0, 1),
    lambda a, as_, b, bs, c, cs, k, ks: (0, -bs * c, 1),
]


def exact():
    """Exact (symbolic) statements about the family.  Points of the circle are x = u with
    x* = 1/(2u), u a nonzero complex number with |u|^2 = 1/2; theta = arg u.

    1. Constant graph: exactly 72 inner products vanish identically in u; every other one has
       no zero on the circle; no two words are proportional anywhere on the circle.
    2. Gould-Aravind: with a = b = 1, c = 1/x*, Table 3 is our list of 33 words, ray by ray;
       for general a, b the diagonal unitary diag(b, a, 1) carries Table 3 at (a, b, c) to
       Table 3 at (1, 1, a b* c).
    3. Symmetries: x -> -x and x -> x* (with coordinates 1 and 2 swapped) map the list of
       rays to itself; so theta, theta + pi and -theta give unitarily equivalent members.
    4. Invariant: sum over pairs of |<v_i, v_j>|^4 (unit vectors) equals
       37493/432 + (17/2) cos 2 theta, strictly decreasing on [0, pi/2]."""
    import sympy as sp
    u = sp.symbols("u", nonzero=True)
    X, XS = u, 1 / (2 * u)
    conj = lambda e: sp.sympify(e).subs(u, 1 / (2 * u))      # noqa: E731  (real coefficients)
    ws = words()

    def vec(w):
        out = []
        for tok in w.strip("()").split(","):
            sign = -1 if tok.startswith("-") else 1
            out.append(sign * {"0": 0, "1": 1, "x": X, "x*": XS}[tok.lstrip("-")])
        return out

    V = [vec(w) for w in ws]
    n = len(V)
    num = lambda e: sp.Poly(sp.numer(sp.together(sp.expand(e))), u)     # noqa: E731

    def zero_on_circle(p):
        """Does the polynomial p(u) (real coefficients) vanish somewhere on |u|^2 = 1/2?
        Such a zero is a common zero of p(u) and u^d p(1/(2u)); test the gcd's roots."""
        d = p.degree()
        rec = sp.Poly(sp.expand(u ** d * p.as_expr().subs(u, 1 / (2 * u))), u)
        g = sp.gcd(p, rec)
        if g.degree() <= 0:
            return False                                   # exact: no candidate zero
        fallback.append(g.as_expr())
        return any(abs(sp.Abs(r.evalf(60)) ** 2 - sp.Rational(1, 2)) < sp.Float(10) ** -40
                   for r in sp.Poly(g, u).all_roots())

    inner = lambda p, q: sum(conj(a) * b for a, b in zip(p, q))         # noqa: E731
    fallback = []
    for control in (2 * u ** 2 + 1, 4 * u ** 4 + 1):      # positive controls: zeros on circle
        assert zero_on_circle(sp.Poly(control, u)), control
    assert not zero_on_circle(sp.Poly(u ** 2 + 1, u))       # negative control
    fallback.clear()
    vanish, bad = 0, 0
    for i in range(n):
        for j in range(i + 1, n):
            e = sp.simplify(inner(V[i], V[j]))
            if e == 0:
                vanish += 1
            elif zero_on_circle(num(e)):
                bad += 1
            minors = [sp.expand(V[i][a] * V[j][b] - V[i][b] * V[j][a])
                      for a, b in ((0, 1), (0, 2), (1, 2))]
            if all(m == 0 for m in minors) or not any(
                    m != 0 and not zero_on_circle(num(m)) for m in minors):
                bad += 1
    graph = {"pairs_vanishing_identically": vanish, "other_pairs_or_rays_failing": bad,
             "polynomials_needing_numerical_root_test": sorted(set(map(str, fallback)))}
    print("1.", graph, flush=True)

    def prop(p, q):
        return all(sp.simplify(p[a] * q[b] - p[b] * q[a]) == 0
                   for a, b in ((0, 1), (0, 2), (1, 2)))

    c, cs = 1 / XS, 1 / X
    ga = [f(1, 1, 1, 1, c, cs, -c / cs, -cs / c) for f in GA_TABLE3]
    match = [[k for k, v in enumerate(V) if prop(g, v)] for g in ga]
    bij = all(len(m) == 1 for m in match) and len({m[0] for m in match}) == n
    A, B, C = sp.symbols("A B C", nonzero=True)           # |A| = |B| = 1, |C|^2 = 2
    gen = lambda a, b, cc: [f(a, 1 / a, b, 1 / b, cc, 2 / cc, -a * cc / (b * (2 / cc)),   # noqa
                                 -(1 / a) * b * (2 / cc) / cc) for f in GA_TABLE3]
    red = all(prop([B * p[0], A * p[1], p[2]], q)
              for p, q in zip(gen(A, B, C), gen(1, 1, A * C / B)))
    ga_rec = {"table3_at_a_b_1_c_1_over_xstar_is_our_list": bij,
              "match_table3_row_to_word": {k + 1: ws[m[0]] for k, m in enumerate(match) if m},
              "diag_b_a_1_reduces_to_a_b_1": red}
    print("2.", bij, red, flush=True)

    def same_set(V1, V2):
        return all(any(prop(p, q) for q in V2) for p in V1)
    neg = [[sp.sympify(e).subs(u, -u) for e in v] for v in V]
    swap = [[conj(v[1]), conj(v[0]), conj(v[2])] for v in V]   # x -> x*, coordinates 1 <-> 2
    sym = {"x_to_minus_x": same_set(neg, V),
           "conjugate_and_swap_coordinates_1_2": same_set(swap, V)}
    print("3.", sym, flush=True)

    norms = [sp.simplify(inner(v, v)) for v in V]
    S = 0
    for i in range(n):
        for j in range(i + 1, n):
            e = inner(V[i], V[j])
            S += (e * conj(e)) ** 2 / (norms[i] * norms[j]) ** 2
    target = sp.Rational(37493, 432) + sp.Rational(17, 4) * (2 * u ** 2 + 1 / (2 * u ** 2))
    inv = {"quartic_sum_equals_37493/432_+_17/2_cos_2theta": sp.simplify(S - target) == 0}
    print("4.", inv, flush=True)
    out = {"graph": graph, "gould_aravind": ga_rec, "symmetries": sym, "invariant": inv}
    (HERE / "results" / "half_circle_family_exact.json").write_text(json.dumps(out, indent=1),
                                                                   encoding="utf-8")
    return out


def main():
    ws = words()
    peres = E.graph("peres33")
    thetas = [0.0, 0.05, 0.2, 0.5, 0.8, 1.0, math.pi / 4, math.pi / 3, math.pi / 2]
    _, _, q0 = member(0.0, ws)
    rows = []
    for th in thetas:
        vecs, pairs, q = member(th, ws)
        g = nx.Graph()
        g.add_nodes_from(range(len(vecs)))
        g.add_edges_from(pairs)
        null, flex, kept, dropped = flexes(vecs, pairs)
        row = {"theta": round(th, 6), "pairs": len(pairs),
               "peres_graph": GraphMatcher(g, peres).is_isomorphic(),
               "max_overlap_change_vs_theta0": float(np.max(np.abs(q - q0))),
               "flexes": flex, "sv_kept": kept, "sv_dropped": dropped}
        rows.append(row)
        print(row, flush=True)
    vel = []
    for th in (0.0, 0.5, math.pi / 2):
        rT, rTw, dist, resid = velocity_at(th, ws)
        rec = {"theta": round(th, 6), "rank_trivial": rT, "rank_with_velocity": rTw,
               "relative_distance_of_velocity_from_trivial": dist,
               "max_linearised_constraint_residual": resid}
        vel.append(rec)
        print(rec, flush=True)
    out = {"curve": CURVE, "words": ws, "members": rows, "velocity": vel}
    (HERE / "results" / "half_circle_family.json").write_text(json.dumps(out, indent=1),
                                                             encoding="utf-8")


if __name__ == "__main__":
    import sys
    if sys.argv[1:2] == ["exact"]:
        exact()
    else:
        main()
