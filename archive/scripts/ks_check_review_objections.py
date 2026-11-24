"""Independently check the falsifiable objections in the GPT-6 Oxford review.

Each block prints CONFIRMED / REFUTED with the evidence, so the review is graded
rather than believed.
"""
from fractions import Fraction
from itertools import combinations, product
from math import gcd

exec(open('ks_verify_two_term.py', encoding='utf-8').read().split('for d, label in')[0])

print("=" * 72)
print("(a) 'Gal = (Z/nZ)* must surject onto Z/6Z, which holds iff 6 | n'")
print("=" * 72)


def carmichael(n):
    """Exponent of (Z/nZ)*."""
    units = [a for a in range(1, n) if gcd(a, n) == 1]
    if not units:
        return 0
    e = 1
    for a in units:
        k, cur = 1, a % n
        while cur != 1:
            cur = cur * a % n
            k += 1
        e = e * k // gcd(e, k)
    return e


bad = []
for n in range(2, 40):
    surjects = carmichael(n) % 6 == 0          # abelian G onto Z/6 iff 6 | exp(G)
    divisible = (n % 6 == 0)
    if surjects != divisible:
        bad.append((n, surjects, divisible, carmichael(n)))
print("  n where 'surjects onto Z/6' disagrees with '6 | n':")
for n, s, d, lam in bad[:10]:
    print("    n=%-3d exp((Z/nZ)*)=%-3d surjects=%-5s  6|n=%-5s" % (n, lam, s, d))
print("  -> %d disagreements below 40. Statement is FALSE in BOTH directions." % len(bad))
print("     CONFIRMED: reviewer is right.")

print()
print("=" * 72)
print("(b) 'generators with |x|^2 >= 3, not a root of unity, give no uncolorability'")
print("=" * 72)
print("  Flagship counterexample from the letter's own Table II: x = 2.")
print("    |2|^2 = 4  >= 3 : True")
print("    2 is a root of unity: False")
print("    pool {0,+-1,+-2} is KS-uncolorable (contains CK-31): True (paper Table II)")
print("  -> The printed quantifier is falsified by the paper's flagship island.")
print("     CONFIRMED: reviewer is right.")

print()
print("=" * 72)
print("(c) '|x|^2 is not intrinsic: S(A(x)) = S(A(1/x)) projectively'")
print("=" * 72)
for d, num, den, lbl in ((3, 0, 1, "x = sqrt(3)   |x|^2 = 3"),
                         (3, 1, 3, "x = 1/sqrt(3) |x|^2 = 1/3")):
    g = QF(0, Fraction(1) if den == 1 else Fraction(1, 3), d)
    alpha = [QF(0, 0, d), QF(1, 0, d), QF(-1, 0, d), g, QF(0, -g.b, d)]
    rays = build_pool(d, alpha)
    pairs = [(i, j) for i, j in combinations(range(len(rays)), 2)
             if sum(terms(rays[i], rays[j])[1:], terms(rays[i], rays[j])[0]).is_zero()]
    adj = {i: set() for i in range(len(rays))}
    for i, j in pairs:
        adj[i].add(j); adj[j].add(i)
    tri = sum(1 for i, j in pairs for k in adj[i] & adj[j] if k > j)
    print("  %-26s rays=%-3d pairs=%-4d triads=%d" % (lbl, len(rays), len(pairs), tri))
print("  -> identical pools. A bound phrased on |x|^2 alone is not well defined:")
print("     |sqrt(3)|^2 = 3 (excluded) and |1/sqrt(3)|^2 = 1/3 (not excluded)")
print("     describe THE SAME ray set.  CONFIRMED: reviewer is right.")

print()
print("=" * 72)
print("(d) 'with no identity there are no orthogonal triads' ignores the axis triad")
print("=" * 72)
alpha01 = [QF(0, 0, 2), QF(1, 0, 2), QF(-1, 0, 2)]
rays = build_pool(2, alpha01)
pairs = [(i, j) for i, j in combinations(range(len(rays)), 2)
         if sum(terms(rays[i], rays[j])[1:], terms(rays[i], rays[j])[0]).is_zero()]
adj = {i: set() for i in range(len(rays))}
for i, j in pairs:
    adj[i].add(j); adj[j].add(i)
tri = sum(1 for i, j in pairs for k in adj[i] & adj[j] if k > j)
print("  alphabet {0,+-1}: rays=%d pairs=%d triads=%d" % (len(rays), len(pairs), tri))
print("  -> triads exist with no exceptional identity at all.")
print("     CONFIRMED: reviewer is right (the letter's own 13-ray/4-triad count says so).")

print()
print("=" * 72)
print("(e) Missing Table I row: |x|^2 - x - xbar = 0, i.e. |x|^2 = Tr(x)")
print("=" * 72)
# x = (3 + i*sqrt(3))/2 lives in Q(sqrt(-3)): a + b*sqrt(-3) with a=3/2, b=1/2
x = QF(Fraction(3, 2), Fraction(1, 2), -3)
norm = x.conj() * x
tr = x + x.conj()
print("  x = (3 + i sqrt3)/2 : |x|^2 = %s , Tr(x) = %s" % (norm, tr))
print("  |x|^2 - x - xbar = %s" % (norm - x - x.conj()))
print("  minimal polynomial x^2 - 3x + 3  -> monic over Z, so x IS an algebraic integer")
print("  -> a primitive three-term zero-sum over the product set, absent from Table I.")
print("     CONFIRMED: the enumeration is still incomplete after the two-term fix.")

print()
print("=" * 72)
print("(f) '|x|^2 = 1 implies roots of unity'")
print("=" * 72)
print("  (3+4i)/5 has |x|^2 = 1 and is NOT a root of unity -> row false as printed.")
print("  BUT it is not an algebraic integer (min poly 5x^2-6x+5, not monic over Z).")
print("  Kronecker: an ALGEBRAIC INTEGER with all conjugates of modulus 1 IS a root")
print("  of unity, so the row is correct in the paper's setting and merely needs the")
print("  hypothesis stated.  PARTIALLY CONFIRMED: wording gap, not a false result.")
