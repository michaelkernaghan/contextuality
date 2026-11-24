"""Emit the 51-ray Golden KS set as a checkable witness.

Regenerates deterministically from the seed that produced it (trial 34 of the
settle run used random.Random(1034)), re-verifies from raw coordinates, and
writes the ray list so the refutation of the published 52 can be checked by
anyone without rerunning the search.
"""
import random
from fractions import Fraction

from pysat.formula import CNF
from pysat.solvers import Glucose4

exec(open('ks_verify_large_minima.py', encoding='utf-8').read()
     .split('# ------------------------------------------------------------------'
            '--------\nQS =')[0])

F5 = Field(2, (5, 0), conj_map=None, name="Q(sqrt5)")
phi = F5.el(Fraction(1, 2), Fraction(1, 2))
ALPHA = [F5.el(0), F5.el(1), -F5.el(1), phi, -phi]


def encode(sub, rays, drop=None):
    keep = [r for r in sub if r != drop]
    idx = {r: i for i, r in enumerate(keep)}
    adj = {i: set() for i in range(len(keep))}
    for a in range(len(keep)):
        for b in range(a + 1, len(keep)):
            if herm(rays[keep[a]], rays[keep[b]]).is_zero():
                adj[a].add(b)
                adj[b].add(a)
    cnf = CNF()
    npair = ntri = 0
    for a in range(len(keep)):
        for b in sorted(x for x in adj[a] if x > a):
            cnf.append([-(a + 1), -(b + 1)])
            npair += 1
            for c in sorted(x for x in (adj[a] & adj[b]) if x > b):
                cnf.append([a + 1, b + 1, c + 1])
                ntri += 1
    if not cnf.clauses:
        return False, npair, ntri
    with Glucose4(bootstrap_with=cnf) as s:
        return (not s.solve()), npair, ntri


def fmt(e):
    a, b = e.c
    if b == 0:
        return str(a)
    if a == 0:
        return "%s*r5" % b
    # NB: %+s does not sign a string, so build the sign explicitly.
    return "%s %s %s*r5" % (a, "+" if b > 0 else "-", abs(b))


rays = build(ALPHA, F5, complete=True)
pairs, triads, _ = structure(rays)
print("pool: %d rays, %d pairs, %d triads" % (len(rays), len(pairs), len(triads)))

rng = random.Random(1034)
order = list(range(len(rays)))
rng.shuffle(order)
cur = set(range(len(rays)))
for r in order:
    cur.discard(r)
    if colourable(cur, pairs, triads):
        cur.add(r)
sub = sorted(cur)
print("reproduced subset size: %d" % len(sub))

unc, np_, nt_ = encode(sub, rays)
crit = all(not encode(sub, rays, drop=r)[0] for r in sub)
print("uncolorable=%s  ray-critical=%s  pairs=%d  triads=%d" % (unc, crit, np_, nt_))

with open("golden_51_rays.txt", "w", encoding="utf-8") as f:
    f.write("51-ray Kochen-Specker set in the completed Q(phi) pool (205 rays).\n")
    f.write("Refutes the pool minimum of 52 reported in earlier work.\n")
    f.write("Coordinates over Q(sqrt5), written a+b*r5 with r5 = sqrt(5).\n")
    f.write("uncolorable=%s  ray_critical=%s  pairs=%d  triads=%d\n"
            % (unc, crit, np_, nt_))
    f.write("Reproduce: random.Random(1034), greedy deletion over the 205-ray pool.\n\n")
    for i, r in enumerate(sub, 1):
        f.write("%2d  (%s)\n" % (i, ",  ".join(fmt(x) for x in rays[r])))
print("witness written to golden_51_rays.txt")
