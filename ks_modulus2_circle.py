"""Exact check: one fixed set of coordinate WORDS over {0, +-1, +-x, +-x*} is
KS-uncolorable for EVERY complex x with |x|^2 = 2.

Method. A Hermitian inner product of two words is a polynomial in x and x*
(x* = conj x). Reduce with x x* = 2; what is left is a combination of
1, x, x*, x^2, x*^2, which are linearly independent as functions on the circle
(they are e^{ik theta}, k = 0, +-1, +-2, up to scale). So the product vanishes
for every x on the circle iff every reduced coefficient is zero. Integer
arithmetic only, no floating point.

The graph of identically-orthogonal pairs is then handed to a SAT solver. If it
is uncolorable, the word set is uncolorable at every point of the circle: at a
special phase extra orthogonalities can only add constraints, and two words that
coincide as rays at a special phase must take the same colour, which is a
restriction of the colourings already shown not to exist.

Run:  python ks_modulus2_circle.py
"""
import itertools
import random
from collections import defaultdict

from pysat.solvers import Glucose4

# letter -> (sign, power of x, power of x*)
LETTERS = {"0": None, "1": (1, 0, 0), "-1": (-1, 0, 0),
           "x": (1, 1, 0), "-x": (-1, 1, 0), "x*": (1, 0, 1), "-x*": (-1, 0, 1)}
NAMES = list(LETTERS)


def conj(letter):
    if letter is None:
        return None
    s, a, b = letter
    return (s, b, a)


def inner(u, v):
    """<u|v> = sum conj(u_k) v_k reduced by x x* = 2, as {(a, b): coeff}."""
    poly = defaultdict(int)
    for cu, cv in zip(u, v):
        lu, lv = conj(LETTERS[cu]), LETTERS[cv]
        if lu is None or lv is None:
            continue
        s, a, b = lu[0] * lv[0], lu[1] + lv[1], lu[2] + lv[2]
        m = min(a, b)
        poly[(a - m, b - m)] += s * 2 ** m
    return {k: c for k, c in poly.items() if c}


def identically_orthogonal(u, v):
    return not inner(u, v)


def generic_rays():
    """One word per ray at a generic phase: two words are the same ray for all
    x on the circle iff all 2x2 minors vanish identically after reduction."""
    def mul(p, q):
        if p is None or q is None:
            return None
        return (p[0] * q[0], p[1] + q[1], p[2] + q[2])

    def minor_zero(u, v, i, j):
        poly = defaultdict(int)
        for sgn, t in ((1, mul(LETTERS[u[i]], LETTERS[v[j]])),
                       (-1, mul(LETTERS[u[j]], LETTERS[v[i]]))):
            if t is None:
                continue
            m = min(t[1], t[2])
            poly[(t[1] - m, t[2] - m)] += sgn * t[0] * 2 ** m
        return not any(poly.values())

    reps = []
    for w in itertools.product(NAMES, repeat=3):
        if w == ("0", "0", "0"):
            continue
        if not any(all(minor_zero(w, r, i, j) for i, j in ((0, 1), (0, 2), (1, 2)))
                   for r in reps):
            reps.append(w)
    return reps


def build(words):
    n = len(words)
    adj = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if identically_orthogonal(words[i], words[j]):
                adj[i].add(j)
                adj[j].add(i)
    return adj


def counts(sub, adj):
    sub = set(sub)
    pairs = sum(len(adj[i] & sub) for i in sub) // 2
    triads = sum(1 for i in sub for j in adj[i] & sub if j > i
                 for k in adj[i] & adj[j] & sub if k > j)
    return pairs, triads


def uncolorable(sub, adj):
    sub = set(sub)
    s = Glucose4()
    for i in sub:
        for j in adj[i] & sub:
            if j > i:
                s.add_clause([-(i + 1), -(j + 1)])
                for k in adj[i] & adj[j] & sub:
                    if k > j:
                        s.add_clause([i + 1, j + 1, k + 1])
    sat = s.solve()
    s.delete()
    return not sat


def main():
    words = generic_rays()
    adj = build(words)
    everything = list(range(len(words)))
    p, t = counts(everything, adj)
    print("generic pool: %d rays, %d identically orthogonal pairs, %d triads, %s"
          % (len(words), p, t, "KS-UNCOLORABLE" if uncolorable(everything, adj) else "colorable"))

    rng = random.Random(7)
    best, sizes = None, defaultdict(int)
    for _ in range(200):
        cur, order = everything[:], everything[:]
        rng.shuffle(order)
        for r in order:
            trial = [c for c in cur if c != r]
            if uncolorable(trial, adj):
                cur = trial
        sizes[len(cur)] += 1
        if best is None or len(cur) < len(best):
            best = cur
    print("greedy descents (200 trials), size: count =", dict(sorted(sizes.items())))
    p, t = counts(best, adj)
    print("smallest found: %d words, %d pairs, %d triads, uncolorable=%s"
          % (len(best), p, t, uncolorable(best, adj)))
    critical = all(not uncolorable([c for c in best if c != r], adj) for r in best)
    print("ray-critical (every single deletion colorable):", critical)
    for i in sorted(best):
        print("  (%s)" % ", ".join(words[i]))
    write_tex(sorted(best), words, adj)
    parts_ii_iii(words, adj, sorted(best))


def plane_graph(words):
    """Pairs orthogonal for EVERY complex x: no reduction by x x* = 2."""
    def free_zero(u, v):
        poly = defaultdict(int)
        for cu, cv in zip(u, v):
            lu, lv = conj(LETTERS[cu]), LETTERS[cv]
            if lu is None or lv is None:
                continue
            poly[(lu[1] + lv[1], lu[2] + lv[2])] += lu[0] * lv[0]
        return not any(poly.values())
    n = len(words)
    adj = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if free_zero(words[i], words[j]):
                adj[i].add(j)
                adj[j].add(i)
    return adj


def parts_ii_iii(words, adj, best):
    """Theorem parts (ii) and (iii), with the evidence written to results/modulus2_circle.json."""
    import json
    from pathlib import Path
    from pysat.card import ITotalizer
    from ks_certify_fast3 import FastPool

    n = len(words)
    # (ii) the configuration valid for every complex x, and an explicit colouring of it
    padj = plane_graph(words)
    ppairs = [(i, j) for i in range(n) for j in padj[i] if j > i]
    ptriads = [(i, j, k) for i, j in ppairs for k in padj[i] & padj[j] if k > j]
    s = Glucose4()
    for i, j in ppairs:
        s.add_clause([-(i + 1), -(j + 1)])
    for t in ptriads:
        s.add_clause([x + 1 for x in t])
    assert s.solve(), "plane configuration is not colourable"
    model = s.get_model()
    ones = [i for i in range(n) if model[i] > 0]
    s.delete()
    assert all(not (i in ones and j in ones) for i, j in ppairs)
    assert all(sum(1 for x in t if x in ones) == 1 for t in ptriads)
    print("(ii) every-x configuration: %d pairs, %d triads, COLOURABLE (colouring checked)"
          % (len(ppairs), len(ptriads)))

    # (iii) certified minimum of the circle configuration, keeping the certificate
    cpairs = [(i, j) for i in range(n) for j in adj[i] if j > i]
    ctriads = [(i, j, k) for i, j in cpairs for k in adj[i] & adj[j] if k > j]
    ub = len(best)
    ps = FastPool(n, cpairs, ctriads)
    hit = Glucose4()
    tot = ITotalizer(lits=list(range(1, n + 1)), ubound=ub - 1, top_id=n)
    hit.append_formula(tot.cnf)
    colourable_sets = []
    while hit.solve(assumptions=[-tot.rhs[ub - 1]]):
        m = hit.get_model()
        cand = [i for i in range(n) if m[i] > 0]
        assert ps.colourable(cand), "found an uncolourable set smaller than the upper bound"
        M = ps.grow(cand)
        assert ps.colourable(M)
        colourable_sets.append(sorted(M))
        hit.add_clause([i + 1 for i in range(n) if i not in M])
    print("(iii) minimum of the circle configuration = %d, certified by %d colourable sets"
          % (ub, len(colourable_sets)))
    tot.delete()
    hit.delete()
    ps.delete()

    sub = set(best)
    out = Path(__file__).resolve().parent / "results" / "modulus2_circle.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({
        "words": [list(w) for w in words],
        "circle_pairs": cpairs, "circle_triads": ctriads,
        "every_x_pairs": ppairs, "every_x_triads": ptriads, "every_x_colouring_ones": ones,
        "W": best, "W_pairs": [p for p in cpairs if p[0] in sub and p[1] in sub],
        "W_triads": [t for t in ctriads if all(x in sub for x in t)],
        "minimum": ub,
        "certificate_note": "each listed set is colourable in the circle configuration; no set of "
                            "fewer than `minimum` words meets the complement of every one of them",
        "certificate_colourable_sets": colourable_sets}), encoding="utf-8")
    print("wrote", out)


def write_tex(best, words, adj):
    """Numbered word list and triad list for the paper (paper/figures/modulus2_words.tex)."""
    from pathlib import Path
    tex = {"0": "0", "1": "1", "-1": "\\bar 1", "x": "x", "-x": "\\bar x",
           "x*": "x^{*}", "-x*": "\\bar x^{*}"}
    num = {i: k + 1 for k, i in enumerate(best)}
    cells = ["%d & $%s$" % (num[i], "\\,".join(tex[c] for c in words[i])) for i in best]
    cols = 5
    rows = -(-len(cells) // cols)
    lines = ["\\begin{tabular}{" + "rl@{\\qquad}" * (cols - 1) + "rl}", "\\hline"]
    for r in range(rows):
        row = [cells[r + c * rows] if r + c * rows < len(cells) else " & " for c in range(cols)]
        lines.append(" & ".join(row) + " \\\\")
    lines += ["\\hline", "\\end{tabular}"]
    sub = set(best)
    triads = sorted((num[i], num[j], num[k]) for i in best for j in adj[i] & sub if j > i
                    for k in adj[i] & adj[j] & sub if k > j)
    tri = ", ".join("\\{%d,%d,%d\\}" % t for t in triads)
    out = Path(__file__).resolve().parent / "paper" / "figures"
    out.mkdir(parents=True, exist_ok=True)
    (out / "modulus2_words.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out / "modulus2_triads.tex").write_text("$" + tri.replace(", ", "$, $") + "$\n", encoding="utf-8")
    print("wrote modulus2_words.tex and modulus2_triads.tex (%d triads)" % len(triads))


if __name__ == "__main__":
    main()
