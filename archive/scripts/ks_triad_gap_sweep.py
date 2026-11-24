"""Is there a presentation-invariant discriminator to replace the |x|^2 bound?

The generator-norm bound fails twice over: x = 2 has |x|^2 = 4 yet its pool holds
CK-31, and S(A(x)) = S(A(1/x)) projectively, so |x|^2 is not even an invariant of
the pool.  Triad count IS an invariant of the pool.  Sweep the two-letter
alphabets and see whether uncolorable and colorable pools separate on it.

Colorability is decided by SAT over the pool's triads and orthogonal pairs.
"""
from fractions import Fraction
from itertools import combinations

from pysat.formula import CNF
from pysat.solvers import Glucose4

exec(open('ks_verify_two_term.py', encoding='utf-8').read().split('for d, label in')[0])


def pool_stats(d, alpha=None):
    rays = build_pool(d, alpha)
    n = len(rays)
    pairs = []
    for i, j in combinations(range(n), 2):
        t = terms(rays[i], rays[j])
        if (t[0] + t[1] + t[2]).is_zero():
            pairs.append((i, j))
    adj = {i: set() for i in range(n)}
    for i, j in pairs:
        adj[i].add(j)
        adj[j].add(i)
    triads = [(i, j, k) for i, j in pairs for k in sorted(adj[i] & adj[j]) if k > j]
    return rays, pairs, triads


def ks_uncolorable(n, pairs, triads):
    """UNSAT  <=>  no valid KS colouring exists."""
    cnf = CNF()
    for i, j in pairs:                       # at most one 1 per orthogonal pair
        cnf.append([-(i + 1), -(j + 1)])
    for i, j, k in triads:                   # exactly one 1 per triad
        cnf.append([i + 1, j + 1, k + 1])
    with Glucose4(bootstrap_with=cnf) as s:
        return not s.solve()


print("%-22s %6s %7s %7s  %s" % ("alphabet", "rays", "pairs", "triads", "KS?"))
print("-" * 60)

rows = []

# minimal alphabet
r, p, t = pool_stats(2, [QF(0, 0, 2), QF(1, 0, 2), QF(-1, 0, 2)])
rows.append(("{0,+-1}", len(r), len(p), len(t), ks_uncolorable(len(r), p, t)))

# integer alphabet {0,+-1,+-2} lives in Q(sqrt(2)) with b = 0
intalpha = [QF(0, 0, 2), QF(1, 0, 2), QF(-1, 0, 2), QF(2, 0, 2), QF(-2, 0, 2)]
r, p, t = pool_stats(2, intalpha)
rows.append(("{0,+-1,+-2}", len(r), len(p), len(t), ks_uncolorable(len(r), p, t)))

# reciprocal presentation of the same pool
halfalpha = [QF(0, 0, 2), QF(1, 0, 2), QF(-1, 0, 2),
             QF(Fraction(1, 2), 0, 2), QF(Fraction(-1, 2), 0, 2)]
r, p, t = pool_stats(2, halfalpha)
rows.append(("{0,+-1,+-1/2}", len(r), len(p), len(t), ks_uncolorable(len(r), p, t)))

# real and imaginary quadratic two-letter alphabets
squares = {1, 4, 9, 16, 25}
for d in [x for x in range(2, 31) if x not in squares]:
    r, p, t = pool_stats(d)
    rows.append(("{0,+-1,+-sqrt%d}" % d, len(r), len(p), len(t),
                 ks_uncolorable(len(r), p, t)))
for d in (1, 2, 3, 5, 6, 7, 10, 11, 13, 14, 15):
    r, p, t = pool_stats(-d)
    rows.append(("{0,+-1,+-sqrt-%d}" % d, len(r), len(p), len(t),
                 ks_uncolorable(len(r), p, t)))

for name, nr, npair, ntri, ks in rows:
    print("%-22s %6d %7d %7d  %s" % (name, nr, npair, ntri, "YES" if ks else "no"))

unc = [r for r in rows if r[4]]
col = [r for r in rows if not r[4]]
print()
print("uncolorable pools : triad counts %s" % sorted({r[3] for r in unc}))
print("colorable pools   : triad counts %s" % sorted({r[3] for r in col}))
if unc and col:
    print("GAP: min(uncolorable) = %d   max(colorable) = %d"
          % (min(r[3] for r in unc), max(r[3] for r in col)))
