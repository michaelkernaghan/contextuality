"""Settle 51 vs 52 for the Golden pool.

An earlier run (seed 42) reported a 51-ray subset; a later run (seed 7) reported
52.  Same algorithm, so one of them is luck and the other is the truth about the
search, not about the pool.  Run many independent greedy descents, record the
distribution of sizes reached, and RE-VERIFY any subset below 52 from its raw
coordinates before believing it.
"""
import random
import time
from collections import Counter
from fractions import Fraction

from pysat.formula import CNF
from pysat.solvers import Glucose4

exec(open('ks_verify_large_minima.py', encoding='utf-8').read()
     .split('# ------------------------------------------------------------------'
            '--------\nQS =')[0])

F5 = Field(2, (5, 0), conj_map=None, name="Q(sqrt5)")
phi = F5.el(Fraction(1, 2), Fraction(1, 2))
ALPHA = [F5.el(0), F5.el(1), -F5.el(1), phi, -phi]


def independent_check(sub, rays):
    """Rebuild encoding from coordinates; return (uncolorable, critical)."""
    sub = sorted(sub)
    m = len(sub)
    adj = {a: set() for a in range(m)}
    for a in range(m):
        for b in range(a + 1, m):
            if herm(rays[sub[a]], rays[sub[b]]).is_zero():
                adj[a].add(b)
                adj[b].add(a)

    def unsat(keep):
        idx = {r: i for i, r in enumerate(keep)}
        cnf = CNF()
        for a in keep:
            for b in adj[a]:
                if b > a and b in idx:
                    cnf.append([-(idx[a] + 1), -(idx[b] + 1)])
        for a in keep:
            for b in sorted(x for x in adj[a] if x > a and x in idx):
                for c in sorted(x for x in (adj[a] & adj[b]) if x > b and x in idx):
                    cnf.append([idx[a] + 1, idx[b] + 1, idx[c] + 1])
        if not cnf.clauses:
            return False
        with Glucose4(bootstrap_with=cnf) as s:
            return not s.solve()

    whole = list(range(m))
    if not unsat(whole):
        return False, False
    crit = all(not unsat([x for x in whole if x != r]) for r in whole)
    return True, crit


def main():
    rays = build(ALPHA, F5, complete=True)
    pairs, triads, _ = structure(rays)
    n = len(rays)
    print("Golden pool: %d rays, %d pairs, %d triads" % (n, len(pairs), len(triads)))

    sizes = Counter()
    champion = None
    t0 = time.time()
    trial = 0
    while time.time() - t0 < 420:
        rng = random.Random(1000 + trial)
        order = list(range(n))
        rng.shuffle(order)
        cur = set(range(n))
        for r in order:
            cur.discard(r)
            if colourable(cur, pairs, triads):
                cur.add(r)
        sizes[len(cur)] += 1
        if champion is None or len(cur) < len(champion):
            champion = set(cur)
            print("  trial %3d: new best %d  (%.0fs)" % (trial, len(cur), time.time() - t0))
        trial += 1

    print("\n%d trials in %.0fs" % (trial, time.time() - t0))
    print("size distribution: %s" % dict(sorted(sizes.items())))
    print("best found: %d" % len(champion))

    unc, crit = independent_check(champion, rays)
    print("independent re-verification of the best subset:")
    print("   uncolorable  : %s" % unc)
    print("   ray-critical : %s" % crit)

    if len(champion) < 52 and unc:
        print("\n==> published minimum 52 is REFUTED: a %d-ray KS set exists."
              % len(champion))
    elif len(champion) == 52 and unc:
        print("\n==> no sub-52 subset found in %d trials; the earlier 51 is not"
              " reproducible and should be treated as a search artifact until"
              " exhibited with coordinates." % trial)


if __name__ == "__main__":
    main()
