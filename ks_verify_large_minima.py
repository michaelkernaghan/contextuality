"""Independent verification of the four larger pool minima.

Heegner-7 (43), Golden (52), Cubic Q(cbrt2) (58), Supergolden (<=47).

Deliberately does NOT import the repo's existing machinery: number fields, ray
canonicalisation, cross-product completion, colourability and the minimum-subset
certification are all re-implemented here so that agreement is evidence rather
than a shared bug.

Exact arithmetic throughout (Fraction coefficients over a power basis).

Minimum certification uses implicit hitting-set duality.  Uncolourability is
upward closed: if R is uncolourable and R subset R', a colouring of R' restricts
to one of R, so R' is uncolourable too.  Hence colourable sets are downward
closed, and if M is a MAXIMAL colourable set then any uncolourable R must contain
a ray outside M.  Collecting those complements gives hitting constraints; the
minimum-cardinality set hitting all of them, once it tests uncolourable, is the
pool minimum.
"""
import sys
import time
from fractions import Fraction
from itertools import combinations, product

from pysat.formula import CNF, WCNF
from pysat.solvers import Glucose4
from pysat.examples.rc2 import RC2


# --------------------------------------------------------------------------
# Number fields: Q[t]/(m(t)) on the power basis {1, t, ..., t^(d-1)}
# --------------------------------------------------------------------------
class Field:
    """Monic minimal polynomial given as the tuple of t^d's coordinates."""

    def __init__(self, deg, reduce_top, conj_map=None, name=""):
        self.deg = deg
        self.reduce_top = tuple(Fraction(c) for c in reduce_top)  # t^deg = this
        self.conj_map = conj_map  # None => identity (real field)
        self.name = name

    def el(self, *coeffs):
        c = list(coeffs) + [0] * (self.deg - len(coeffs))
        return El(self, tuple(Fraction(x) for x in c))


class El:
    __slots__ = ("F", "c")

    def __init__(self, F, c):
        self.F = F
        self.c = c

    def __add__(self, o):
        return El(self.F, tuple(a + b for a, b in zip(self.c, o.c)))

    def __sub__(self, o):
        return El(self.F, tuple(a - b for a, b in zip(self.c, o.c)))

    def __neg__(self):
        return El(self.F, tuple(-a for a in self.c))

    def __mul__(self, o):
        d = self.F.deg
        raw = [Fraction(0)] * (2 * d - 1)
        for i, a in enumerate(self.c):
            if a:
                for j, b in enumerate(o.c):
                    if b:
                        raw[i + j] += a * b
        # reduce powers t^d .. t^(2d-2) downward
        for k in range(2 * d - 2, d - 1, -1):
            coef = raw[k]
            if coef:
                raw[k] = Fraction(0)
                for i, r in enumerate(self.F.reduce_top):
                    raw[k - d + i] += coef * r
        return El(self.F, tuple(raw[:d]))

    def conj(self):
        if self.F.conj_map is None:
            return self
        return El(self.F, tuple(self.F.conj_map(self.c)))

    def is_zero(self):
        return all(x == 0 for x in self.c)

    def inv(self):
        """Invert by solving the multiplication matrix over Q."""
        d = self.F.deg
        cols = []
        for k in range(d):
            basis = self.F.el(*[1 if i == k else 0 for i in range(d)])
            cols.append((self * basis).c)
        # solve  M x = e_0   where M[:, k] = cols[k]
        M = [[cols[k][r] for k in range(d)] + [Fraction(1 if r == 0 else 0)]
             for r in range(d)]
        for i in range(d):
            p = next(r for r in range(i, d) if M[r][i] != 0)
            M[i], M[p] = M[p], M[i]
            pv = M[i][i]
            M[i] = [v / pv for v in M[i]]
            for r in range(d):
                if r != i and M[r][i]:
                    f = M[r][i]
                    M[r] = [v - f * w for v, w in zip(M[r], M[i])]
        return El(self.F, tuple(M[r][d] for r in range(d)))

    def __eq__(self, o):
        return self.c == o.c

    def __hash__(self):
        return hash(self.c)


def herm(v, w):
    """Hermitian inner product sum conj(v_k) w_k."""
    s = v[0].conj() * w[0]
    for k in (1, 2):
        s = s + v[k].conj() * w[k]
    return s


def canon(v):
    """Divide by first nonzero coordinate: unique representative of the ray."""
    i = next((k for k in range(3) if not v[k].is_zero()), None)
    if i is None:
        return None
    inv = v[i].inv()
    return tuple((x * inv).c for x in v)


def cross(v, w, F):
    """Cofactor vector spanning the orthocomplement of span{v,w}."""
    a, b = [x.conj() for x in v], [x.conj() for x in w]
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def build(alphabet, F, complete=False, cap=4000):
    """Pool of rays from all 3-letter words, optionally closed under cross products."""
    seen, rays = {}, []
    for w in product(alphabet, repeat=3):
        if all(x.is_zero() for x in w):
            continue
        k = canon(w)
        if k not in seen:
            seen[k] = len(rays)
            rays.append(w)

    if complete:
        while True:
            pairs = orth_pairs(rays)
            added = 0
            for i, j in pairs:
                u = cross(rays[i], rays[j], F)
                if all(x.is_zero() for x in u):
                    continue
                k = canon(u)
                if k not in seen:
                    seen[k] = len(rays)
                    rays.append(u)
                    added += 1
                    if len(rays) > cap:
                        raise RuntimeError("completion exceeded cap %d" % cap)
            if not added:
                break
    return rays


def orth_pairs(rays):
    return [(i, j) for i, j in combinations(range(len(rays)), 2)
            if herm(rays[i], rays[j]).is_zero()]


def structure(rays):
    pairs = orth_pairs(rays)
    adj = {i: set() for i in range(len(rays))}
    for i, j in pairs:
        adj[i].add(j)
        adj[j].add(i)
    triads = [(i, j, k) for i, j in pairs for k in sorted(adj[i] & adj[j]) if k > j]
    return pairs, triads, adj


# --------------------------------------------------------------------------
# Colourability and minimum certification
# --------------------------------------------------------------------------
def colourable(sub, pairs, triads):
    """Is the induced sub-configuration KS-colourable?"""
    S = set(sub)
    if not S:
        return True
    cnf = CNF()
    for i, j in pairs:
        if i in S and j in S:
            cnf.append([-(i + 1), -(j + 1)])        # at most one 1 per orthogonal pair
    for i, j, k in triads:
        if i in S and j in S and k in S:
            cnf.append([i + 1, j + 1, k + 1])       # at least one 1 per triad
    if not cnf.clauses:
        return True
    # Only rays of S appear in any clause, so rays outside S are unconstrained
    # and need no assumptions.
    with Glucose4(bootstrap_with=cnf) as s:
        return s.solve()


def grow_maximal(seed, n, pairs, triads):
    """Extend a colourable seed to a maximal colourable set."""
    cur = list(seed)
    for r in range(n):
        if r in cur:
            continue
        if colourable(cur + [r], pairs, triads):
            cur.append(r)
    return set(cur)


def min_uncolourable(n, pairs, triads, budget):
    """Implicit hitting set: exact pool minimum, or None on timeout."""
    H, it, t0 = [], 0, time.time()
    while True:
        it += 1
        if time.time() - t0 > budget:
            return None, it
        w = WCNF()
        for i in range(n):
            w.append([-(i + 1)], weight=1)          # prefer NOT selecting
        for S in H:
            w.append([i + 1 for i in S])            # must hit
        with RC2(w) as rc2:
            model = rc2.compute()
        if model is None:
            return None, it
        R = [i for i in range(n) if model[i] > 0]
        if not colourable(R, pairs, triads):
            return R, it
        M = grow_maximal(R, n, pairs, triads)
        H.append([i for i in range(n) if i not in M])


def greedy_min(n, pairs, triads, trials, rng):
    """Upper bound: randomised greedy ray deletion."""
    best = None
    order = list(range(n))
    for _ in range(trials):
        rng.shuffle(order)
        cur = set(range(n))
        for r in order:
            cur.discard(r)
            if colourable(cur, pairs, triads):
                cur.add(r)
        if best is None or len(cur) < len(best):
            best = set(cur)
    return best


def bases_of(sub, triads):
    S = set(sub)
    return [t for t in triads if all(x in S for x in t)]


# --------------------------------------------------------------------------
QS = Field(2, (-1, 0), conj_map=lambda c: (c[0], -c[1]), name="Q(sqrt-7)")   # placeholder
# Q(sqrt(-7)): t = sqrt(-7), t^2 = -7
F7 = Field(2, (-7, 0), conj_map=lambda c: (c[0], -c[1]), name="Q(sqrt(-7))")
# Q(sqrt5): t = sqrt5, t^2 = 5, real
F5 = Field(2, (5, 0), conj_map=None, name="Q(sqrt5)")
# Q(cbrt2): t^3 = 2, real
FC = Field(3, (2, 0, 0), conj_map=None, name="Q(cbrt2)")
# Q(psi): psi^3 = psi^2 + 1, real
FP = Field(3, (1, 0, 1), conj_map=None, name="Q(psi)")


def run(label, F, alphabet, complete, claim_min, claim_bases, budget, trials, seed):
    import random
    rng = random.Random(seed)
    print("=" * 70)
    print(label)
    print("=" * 70)
    t0 = time.time()
    rays = build(alphabet, F, complete=complete)
    pairs, triads, _ = structure(rays)
    print("  pool: %d rays, %d pairs, %d triads   (%.1fs)"
          % (len(rays), len(pairs), len(triads), time.time() - t0))

    unc = not colourable(list(range(len(rays))), pairs, triads)
    print("  pool KS-uncolorable: %s" % ("YES" if unc else "NO"))
    if not unc:
        print("  -> pool is colourable; nothing to certify.")
        return

    ub = greedy_min(len(rays), pairs, triads, trials, rng)
    print("  greedy upper bound: %d rays, %d bases  (claimed %s / %s)"
          % (len(ub), len(bases_of(ub, triads)), claim_min, claim_bases))

    t1 = time.time()
    R, iters = min_uncolourable(len(rays), pairs, triads, budget)
    if R is None:
        print("  OCUS-style certification: NOT COMPLETED in %.0fs (%d iterations)"
              % (time.time() - t1, iters))
        print("  -> minimum is at most %d; lower bound UNVERIFIED here." % len(ub))
    else:
        print("  CERTIFIED pool minimum: %d rays, %d bases  [%d iters, %.1fs]"
              % (len(R), len(bases_of(R, triads)), iters, time.time() - t1))
        print("  -> claim %s: %s" % (claim_min,
                                     "CONFIRMED" if len(R) == claim_min else "MISMATCH"))


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    budget = float(sys.argv[2]) if len(sys.argv) > 2 else 600.0

    a = F7.el(Fraction(1, 2), Fraction(1, 2))       # alpha = (1+sqrt-7)/2
    heeg = [F7.el(0), F7.el(1), -F7.el(1), a, -a, a.conj(), -a.conj()]

    phi = F5.el(Fraction(1, 2), Fraction(1, 2))     # (1+sqrt5)/2
    gold = [F5.el(0), F5.el(1), -F5.el(1), phi, -phi]

    c2, c4 = FC.el(0, 1), FC.el(0, 0, 1)
    cub = [FC.el(0), FC.el(1), -FC.el(1), c2, -c2, c4, -c4]

    psi = FP.el(0, 1)
    sup = [FP.el(0), FP.el(1), -FP.el(1), psi, -psi]

    jobs = {
        "heegner": ("Heegner-7  Z[(1+sqrt-7)/2], raw alphabet",
                    F7, heeg, False, 43, 23, 200),
        "golden":  ("Golden  Z[phi], completed", F5, gold, True, 52, 25, 60),
        "cubic":   ("Cubic  Z[cbrt2], completed", FC, cub, True, 58, 26, 30),
        "super":   ("Supergolden  Z[psi], completed", FP, sup, True, 47, None, 60),
    }
    for key, (label, F, alpha, comp, cm, cb, trials) in jobs.items():
        if which in ("all", key):
            try:
                run(label, F, alpha, comp, cm, cb, budget, trials, 42)
            except Exception as e:
                print("  ERROR: %s" % e)
            print()


if __name__ == "__main__":
    main()
