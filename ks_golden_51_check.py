"""Settle the Golden minimum: is there a 51-ray KS set, contra the published 52?

Does not rely on the greedy search being correct.  It extracts a candidate,
writes its exact coordinates out, and then re-verifies from scratch with a
freshly built encoding:

  1. the subset is KS-uncolorable  (SAT says UNSAT)
  2. the subset is ray-critical    (deleting ANY single ray makes it colorable)

Ray-criticality is the real content: a critical uncolorable set of size 51 means
no 51-ray set can be padding around a smaller one, and it directly contradicts a
claimed pool minimum of 52.
"""
import random
import sys
import time
from fractions import Fraction

from pysat.formula import CNF
from pysat.solvers import Glucose4

exec(open('ks_verify_large_minima.py', encoding='utf-8').read()
     .split('# ------------------------------------------------------------------'
            '--------\nQS =')[0])

F5 = Field(2, (5, 0), conj_map=None, name="Q(sqrt5)")
phi = F5.el(Fraction(1, 2), Fraction(1, 2))
ALPHA = [F5.el(0), F5.el(1), -F5.el(1), phi, -phi]


def fresh_uncolorable(sub, rays):
    """Rebuild the encoding from the RAY COORDINATES, not from cached indices."""
    sub = sorted(sub)
    pos = {r: i for i, r in enumerate(sub)}
    cnf = CNF()
    npair = ntriad = 0
    adj = {i: set() for i in range(len(sub))}
    for a in range(len(sub)):
        for b in range(a + 1, len(sub)):
            if herm(rays[sub[a]], rays[sub[b]]).is_zero():
                cnf.append([-(a + 1), -(b + 1)])
                adj[a].add(b)
                adj[b].add(a)
                npair += 1
    for a in range(len(sub)):
        for b in sorted(x for x in adj[a] if x > a):
            for c in sorted(x for x in (adj[a] & adj[b]) if x > b):
                cnf.append([a + 1, b + 1, c + 1])
                ntriad += 1
    with Glucose4(bootstrap_with=cnf) as s:
        sat = s.solve()
    return (not sat), npair, ntriad


def main():
    t0 = time.time()
    rays = build(ALPHA, F5, complete=True)
    pairs, triads, _ = structure(rays)
    print("Golden pool: %d rays, %d pairs, %d triads  (%.1fs)"
          % (len(rays), len(pairs), len(triads), time.time() - t0))

    rng = random.Random(7)
    best = None
    for trial in range(40):
        order = list(range(len(rays)))
        rng.shuffle(order)
        cur = set(range(len(rays)))
        for r in order:
            cur.discard(r)
            if colourable(cur, pairs, triads):
                cur.add(r)
        if best is None or len(cur) < len(best):
            best = set(cur)
            print("  trial %2d: new best %d rays" % (trial, len(best)))
    sub = sorted(best)
    print("\nsmallest found: %d rays" % len(sub))

    unc, np_, nt_ = fresh_uncolorable(sub, rays)
    print("re-verified from coordinates: %d pairs, %d triads, uncolorable=%s"
          % (np_, nt_, unc))

    print("ray-criticality: deleting each of the %d rays in turn..." % len(sub))
    non_critical = []
    for r in sub:
        rest = [x for x in sub if x != r]
        still, _, _ = fresh_uncolorable(rest, rays)
        if still:
            non_critical.append(r)
    if non_critical:
        print("  NOT critical: %d rays are removable -> smaller set exists"
              % len(non_critical))
    else:
        print("  CRITICAL: every single-ray deletion restores colorability.")

    out = 'golden_%d_rays.txt' % len(sub)
    with open(out, 'w', encoding='utf-8') as f:
        f.write("Golden pool KS set, %d rays, coordinates over Q(sqrt5) "
                "as a+b*sqrt5\n" % len(sub))
        f.write("uncolorable=%s ray_critical=%s pairs=%d triads=%d\n\n"
                % (unc, not non_critical, np_, nt_))
        for r in sub:
            f.write("  (%s)\n" % ", ".join(
                "%s%+s*sqrt5" % (x.c[0], x.c[1]) for x in rays[r]))
    print("coordinates written to %s" % out)

    print("\nVERDICT: published Golden minimum is 52; this run exhibits a %s "
          "%d-ray KS set." % ("ray-critical" if not non_critical else "non-critical",
                              len(sub)))


if __name__ == "__main__":
    main()
