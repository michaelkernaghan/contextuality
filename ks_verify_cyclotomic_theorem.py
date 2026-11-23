"""Verify the cyclotomic theorem and the structural lemmas its proof rests on.

Theorem: the pool S_n generated in C^3 by the alphabet {0} u mu_n is
KS-uncolorable iff 6 | n.

Exact and fast: every alphabet letter is a root of unity, so a coordinate is
either 0 or an exponent mod n.  A dot product is a sum of at most three n-th
roots of unity, and vanishing is decidable in closed form:

  1 term  : never zero
  2 terms : zeta^a + zeta^b = 0  iff  b - a = n/2   (needs 2 | n)
  3 terms : zeta^a + zeta^b + zeta^c = 0 iff the pairwise offsets from a are
            {n/3, 2n/3}   (needs 3 | n), since three unit vectors summing to
            zero form an equilateral triple.

No floating point anywhere.
"""
import sys
from itertools import combinations, product

from pysat.formula import CNF
from pysat.solvers import Glucose4


def vanishes(terms, n):
    """terms: list of exponents mod n (each a root of unity). Does the sum vanish?"""
    t = sorted(terms)
    if len(t) == 0:
        return True
    if len(t) == 1:
        return False
    if len(t) == 2:
        return n % 2 == 0 and (t[1] - t[0]) % n == n // 2
    if len(t) == 3:
        if n % 3:
            return False
        offs = sorted(((x - t[0]) % n) for x in t)
        return offs == [0, n // 3, 2 * n // 3]
    raise ValueError


def build(n):
    """Rays of S_n, canonicalised by dividing through by the first nonzero entry."""
    letters = [None] + list(range(n))          # None = 0
    seen, rays = set(), []
    for w in product(letters, repeat=3):
        if all(x is None for x in w):
            continue
        i = next(k for k in range(3) if w[k] is not None)
        shift = w[i]
        key = tuple(None if x is None else (x - shift) % n for x in w)
        if key not in seen:
            seen.add(key)
            rays.append(key)
    return rays


def orthogonal(v, w, n):
    """Hermitian product sum conj(v_k) w_k: surviving terms are w_k - v_k."""
    terms = [(w[k] - v[k]) % n for k in range(3)
             if v[k] is not None and w[k] is not None]
    return vanishes(terms, n)


def structure(rays, n):
    idx = range(len(rays))
    pairs = [(i, j) for i, j in combinations(idx, 2)
             if orthogonal(rays[i], rays[j], n)]
    adj = {i: set() for i in idx}
    for i, j in pairs:
        adj[i].add(j)
        adj[j].add(i)
    triads = [(i, j, k) for i, j in pairs for k in sorted(adj[i] & adj[j]) if k > j]
    return pairs, triads, adj


def colourable(nrays, pairs, triads):
    cnf = CNF()
    for i, j in pairs:
        cnf.append([-(i + 1), -(j + 1)])
    for i, j, k in triads:
        cnf.append([i + 1, j + 1, k + 1])
    if not cnf.clauses:
        return True
    with Glucose4(bootstrap_with=cnf) as s:
        return s.solve()


def allnz(r):
    return all(x is not None for x in r)


def main():
    hi = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    print("%3s %7s %7s %7s  %-11s %-9s %s"
          % ("n", "rays", "pairs", "triads", "colourable?", "6|n", "agree"))
    print("-" * 64)
    bad = 0
    lemma_fail = []
    for n in range(2, hi + 1):
        rays = build(n)
        pairs, triads, adj = structure(rays, n)
        col = colourable(len(rays), pairs, triads)
        pred_uncol = (n % 6 == 0)
        agree = (not col) == pred_uncol
        if not agree:
            bad += 1
        print("%3d %7d %7d %7d  %-11s %-9s %s"
              % (n, len(rays), len(pairs), len(triads),
                 "yes" if col else "NO", "yes" if pred_uncol else "no",
                 "ok" if agree else "MISMATCH"))

        # ---- structural lemmas used in the necessity proof ----
        if n % 6 != 0:
            if n % 2 and n % 3:                      # Case A
                if len(triads) != 1:
                    lemma_fail.append((n, "A: expected exactly 1 triad, got %d"
                                       % len(triads)))
            elif n % 2 == 0 and n % 3:               # Case B
                anz = [(i, j) for i, j in pairs if allnz(rays[i]) and allnz(rays[j])]
                if anz:
                    lemma_fail.append((n, "B: %d all-nonzero orthogonal pairs"
                                       % len(anz)))
            elif n % 3 == 0 and n % 2:               # Case C
                cnt = {}
                for t in triads:
                    for r in t:
                        if allnz(rays[r]):
                            cnt[r] = cnt.get(r, 0) + 1
                offenders = [r for r, c in cnt.items() if c != 1]
                if offenders:
                    lemma_fail.append((n, "C: %d all-nonzero rays in != 1 triad"
                                       % len(offenders)))
                missing = [i for i in range(len(rays))
                           if allnz(rays[i]) and i not in cnt]
                if missing:
                    lemma_fail.append((n, "C: %d all-nonzero rays in NO triad"
                                       % len(missing)))

    print()
    print("theorem mismatches over n=2..%d : %d" % (hi, bad))
    print("structural lemma failures        : %d" % len(lemma_fail))
    for n, msg in lemma_fail:
        print("   n=%d  %s" % (n, msg))


if __name__ == "__main__":
    main()
