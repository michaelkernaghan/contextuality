"""v10: complete enumeration of short vanishing sums for the alphabet {0, +-1, +-x}.

A term of an inner product of two words is conj(a) b with a, b letters, so it is
one of +-1, +-x, +-x*, +-N with N = x x* (zero terms are dropped).  A sum of at
most three such terms is  c0 + c1 x + c2 x* + c3 N  with integers c_i and
1 <= |c0|+|c1|+|c2|+|c3| <= 3 (terms that cancel in pairs lower the count, which
is why every smaller L1 norm is included).  This script lists EVERY such
coefficient vector, groups them into orbits of the maps that do not change the
ray pool,

    overall sign,   x -> -x,   x -> x*,   x -> 1/x  [(c0,c1,c2,c3) -> (c3,c2,c1,c0)],

and prints the solution set of each orbit's representative, computed from
x = a + ib:   (c1 - c2) b = 0   and   c0 + (c1 + c2) a + c3 (a^2 + b^2) = 0.
Solutions with x in {0, 1, -1} are discarded (the alphabet degenerates).

v9 printed seven rows found by inspection, justified them with a wrong count,
and omitted the two-term sums.  Run:  python ks_zero_sums_v10.py
Writes paper/figures/zero_sums_table.tex.
"""
import itertools
from fractions import Fraction as Fr
from math import isqrt
from pathlib import Path


def orbit(c):
    seen, todo = set(), [c]
    while todo:
        v = todo.pop()
        if v in seen:
            continue
        seen.add(v)
        c0, c1, c2, c3 = v
        todo += [(-c0, -c1, -c2, -c3), (c0, -c1, -c2, c3), (c0, c2, c1, c3), (c3, c2, c1, c0)]
    return seen


def sqrt_tex(q):
    """TeX for sqrt of a positive rational q."""
    n, d = q.numerator * q.denominator, q.denominator
    r = isqrt(n)
    if r * r == n:
        return str(Fr(r, d))
    return "\\sqrt{%d}/%d" % (n, d) if d != 1 else "\\sqrt{%d}" % n


def real_roots(c0, s, c3):
    """Real x with c0 + s x + c3 x^2 = 0, as (value-or-None, tex)."""
    if c3 == 0:
        return [] if s == 0 else [Fr(-c0, s)]
    disc = s * s - 4 * c3 * c0
    if disc < 0:
        return []
    r = isqrt(disc)
    if r * r == disc:
        return sorted({Fr(-s + r, 2 * c3), Fr(-s - r, 2 * c3)})
    num, den = (-s, 2 * c3) if c3 > 0 else (s, -2 * c3)
    return ["(%d\\pm\\sqrt{%d})/%d" % (num, disc, den)]


def locus(c):
    c0, c1, c2, c3 = c
    if c1 != c2:                                         # forces x real
        if c0 == 0 and c1 + c2 == 0 and c3 == 0:         # e.g. x - x* = 0: every real x
            return "\\mathrm{Im}\\,x=0"
        roots =[r for r in real_roots(c0, c1 + c2, c3) if not (isinstance(r, Fr) and r in (0, 1, -1))]
        if not roots:
            return None
        return "x=" + ",\\ ".join(str(r) if isinstance(r, Fr) else r for r in roots)
    s = 2 * c1                                           # c0 + s a + c3 |x|^2 = 0
    if c3 == 0:
        if s == 0:
            return None
        return "\\mathrm{Re}\\,x=%s" % Fr(-c0, s)
    centre, rad2 = Fr(-s, 2 * c3), Fr(s * s, 4 * c3 * c3) - Fr(c0, c3)
    if rad2 <= 0:
        return None
    if centre == 0:
        return "|x|^2=%s" % rad2
    return "|x%s%s|=%s" % ("-" if centre > 0 else "+", abs(centre), sqrt_tex(rad2))


def poly_tex(c):
    names = ["", "x", "x^{*}", "|x|^2"]
    out = ""
    for k, name in zip(c, names):
        if k == 0:
            continue
        sign = "-" if k < 0 else ("+" if out else "")
        mag = "" if (abs(k) == 1 and name) else str(abs(k))
        out += "%s%s%s" % (sign, mag, name)
    return out + "=0"


def main():
    vectors = [c for c in itertools.product(range(-3, 4), repeat=4) if 1 <= sum(map(abs, c)) <= 3]
    classes, seen = [], set()
    for c in vectors:
        if c in seen:
            continue
        orb = orbit(c)
        seen |= orb
        rep = max(orb)                                   # deterministic representative
        classes.append((rep, len(orb), locus(rep)))
    live = [(r, k, l) for r, k, l in classes if l]
    print("coefficient vectors: %d; orbits: %d; orbits with a solution outside {0,+-1}: %d"
          % (len(vectors), len(classes), len(live)))
    live.sort(key=lambda t: (sum(map(abs, t[0])), [-v for v in t[0]]))
    lines = ["\\begin{tabular}{@{}rlll@{}}", "\\toprule",
             "Terms & Representative relation & Orbit size & Solution set \\\\", "\\midrule"]
    for rep, k, loc in live:
        print("  L1=%d  %-28s orbit %2d   %s" % (sum(map(abs, rep)), poly_tex(rep), k, loc))
        lines.append("%d & $%s$ & %d & $%s$ \\\\" % (sum(map(abs, rep)), poly_tex(rep), k, loc))
    lines += ["\\bottomrule", "\\end{tabular}"]
    out = Path(__file__).resolve().parent / "paper" / "figures" / "zero_sums_table.tex"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("wrote", out)


if __name__ == "__main__":
    main()
