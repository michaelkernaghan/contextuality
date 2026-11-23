"""Export minimality certificates to lean/Minimality.lean.

For a pool P with certified minimum u this writes, between GENERATED markers:
  rays    exact coordinates (integer tuples in the pool's coefficient ring);
  pairs, triads   the orthogonality graph, recomputed with the ring arithmetic Lean uses;
  fam     colourable sets as a binary tree of (C, T) bit masks: C the complement of the set,
          T the rays coloured true.  Every uncolourable subset of P meets every C;
  tree    a branching proof that no set of fewer than u rays meets every C.  A leaf lists
          complements that miss the included rays and are pairwise disjoint after removing
          the excluded rays;
  sel, cert   a u-ray uncolourable subset and its case-split refutation.

Lean checks all of it (KSMin.minimum_eq); nothing here is trusted.  Each piece is also
checked below with a Python mirror of the Lean checker, so a bad certificate is reported
here first.

Usage:  python ks_lean_minimality.py [intpool ...]
"""
import sys
from fractions import Fraction
from math import gcd
from pathlib import Path

from pysat.solvers import Glucose4

import ks_bpqs_exact as B
import ks_recertify_v10 as R
from ks_certify_fast3 import FastPool
from ks_lean_export import graph, refute

HERE = Path(__file__).resolve().parent
sys.setrecursionlimit(100000)


def int_dot(u, v):
    return (sum(a * b for a, b in zip(u, v)),)


def primitive(ray):
    """Integer multiple of a rational ray with coprime entries."""
    fr = [Fraction(x.c[0]) for x in ray]
    assert all(all(c == 0 for c in x.c[1:]) for x in ray), "not a rational ray"
    den = 1
    for f in fr:
        den = den * f.denominator // gcd(den, f.denominator)
    iv = [int(f * den) for f in fr]
    g = 0
    for v in iv:
        g = gcd(g, abs(v))
    return tuple(v // g for v in iv)


def intpool():
    akey, comp, _ = R.POOLS["integer-raw"]
    F, alpha, _ = R.ALPHABETS[akey]
    rays = R.build(alpha, F, complete=comp, cap=3000)
    coords = [primitive(r) for r in rays]
    index = {R.canon(r): i for i, r in enumerate(rays)}
    assert len(index) == len(rays), "two listed vectors are proportional"
    wit, _, _ = B.load_set("ck31")
    sel = sorted(index[R.canon(r)] for r in wit)
    return coords, int_dot, 31, sel, lambda c: "(%d, %d, %d)" % c


def e_dot(u, v):            # Z[omega], omega^2 = -1 - omega; mirrors Eis.edot
    s = (0, 0)
    for a, b in zip(u, v):
        x = (a[0] - a[1], -a[1])
        p = (x[0] * b[0] - x[1] * b[1], x[0] * b[1] + x[1] * b[0] - x[1] * b[1])
        s = (s[0] + p[0], s[1] + p[1])
    return s


def s2_dot(u, v):           # Z[sqrt 2], real; mirrors PeresPool.dot
    s = (0, 0)
    for a, b in zip(u, v):
        s = (s[0] + a[0] * b[0] + 2 * a[1] * b[1], s[1] + a[0] * b[1] + a[1] * b[0])
    return s


def scaled(ray, conv):
    """The canonical ray times the least s in {1, 2} making conv(coordinate) integral."""
    for s in (1, 2):
        row = [conv(tuple(Fraction(c) * s for c in x.c)) for x in ray]
        if all(v.denominator == 1 for c in row for v in c):
            return tuple(tuple(int(v) for v in c) for c in row)
    raise AssertionError("ray not integral after scaling by 2")


def field_pool(pool_key, set_key, conv, dot, u):
    akey, comp, _ = R.POOLS[pool_key]
    F, alpha, _ = R.ALPHABETS[akey]
    rays = R.build(alpha, F, complete=comp, cap=3000)
    coords = [scaled(r, conv) for r in rays]
    index = {R.canon(r): i for i, r in enumerate(rays)}
    # one vector per ray: canon divides by the first nonzero coordinate in the exact field,
    # so distinct canonical forms are pairwise non-proportional vectors
    assert len(index) == len(rays), "two listed vectors are proportional"
    wit, _, _ = B.load_set(set_key)
    sel = sorted(index[R.canon(r)] for r in wit)
    return coords, dot, u, sel, lambda r: "(" + ", ".join(
        "(" + ", ".join(map(str, c)) + ")" for c in r) + ")"


def heegnerpool():          # F7 stores a + b sqrt(-7); sqrt(-7) = 2 alpha - 1
    from ks_lean_export import h_dot
    return field_pool("heegner7-raw", "heegner7-43", lambda c: (c[0] - c[1], 2 * c[1]),
                      h_dot, 43)


def eispool():              # FW stores a + b omega
    return field_pool("eisenstein-raw", "eisenstein33", lambda c: c, e_dot, 33)


def perespool():            # F2 stores a + b sqrt 2
    return field_pool("peres-raw", "peres33", lambda c: c, s2_dot, 33)


def m2_dot(u, v):           # Z[sqrt -2], Hermitian; mirrors Sqrtm2Pool.dot
    s = (0, 0)
    for a, b in zip(u, v):
        x = (a[0], -a[1])
        s = (s[0] + x[0] * b[0] - 2 * x[1] * b[1], s[1] + x[0] * b[1] + x[1] * b[0])
    return s


def sqrtm2pool():           # FM2 stores a + b sqrt(-2)
    return field_pool("sqrtm2-raw", "sqrtm2-33", lambda c: c, m2_dot, 33)


def supergoldenpool():      # FP stores a + b psi + c psi^2
    from ks_lean_export import p_dot
    return field_pool("supergolden2-raw", "supergolden2-47", lambda c: c, p_dot, 47)


POOLS = {"intpool": intpool, "heegnerpool": heegnerpool, "eispool": eispool,
         "perespool": perespool, "sqrtm2pool": sqrtm2pool,
         "supergoldenpool": supergoldenpool}


def colouring(n, pairs, triads, M):
    """A valid colouring of the set M, as the set of rays coloured true."""
    s = Glucose4()
    inM = [False] * n
    for i in M:
        inM[i] = True
    for i, j in pairs:
        if inM[i] and inM[j]:
            s.add_clause([-(i + 1), -(j + 1)])
    for t in triads:
        if all(inM[x] for x in t):
            s.add_clause([x + 1 for x in t])
    for i in range(n):
        if not inM[i]:
            s.add_clause([-(i + 1)])
    assert s.solve(), "set from the certifier is not colourable"
    model = s.get_model()
    return {i for i in M if model[i] > 0}


def family(n, pairs, triads, u):
    """Colourable sets (complement C, true rays T) such that no set of fewer than u rays
    meets every C.  Terminates only if u really is the minimum."""
    from pysat.card import CardEnc, EncType
    ps = FastPool(n, pairs, triads)
    hit = Glucose4()
    card = CardEnc.atmost(lits=list(range(1, n + 1)), bound=u - 1, top_id=n,
                          encoding=EncType.seqcounter)
    for c in card.clauses:
        hit.add_clause(c)
    fam = []
    while hit.solve():
        model = hit.get_model()
        Rset = [i for i in range(n) if model[i] > 0]
        assert ps.colourable(Rset), "an uncolourable set of fewer than %d rays exists" % u
        M = set(ps.grow(Rset))
        C = frozenset(i for i in range(n) if i not in M)
        assert C, "the whole pool is colourable"
        fam.append((C, frozenset(colouring(n, pairs, triads, M))))
        hit.add_clause([i + 1 for i in C])
    return fam


def col_ok(pairs, triads, C, T):
    """Mirror of KSMin.colOK."""
    return (all(not (i in T and j in T) for i, j in pairs) and
            all(any(x in C for x in t) or any(x in T for x in t) for t in triads))


def lower_bound_tree(fam, u):
    """Branch and bound; returns the tree as nested tuples and its node count."""
    nodes = [0]

    def packing(inc, live):
        used, out = set(), []
        for j, d in sorted(live, key=lambda p: len(p[1])):
            if not (d & used):
                used |= d
                out.append(j)
                if inc + len(out) >= u:
                    return out
        return None

    def go(inc, live):
        nodes[0] += 1
        for j, d in live:
            if not d:                               # every ray of this complement excluded
                return ("dead", j)
        pk = packing(inc, live) if inc < u else []
        if pk is not None:
            return ("pack", pk)
        cnt = {}
        for _, d in live:
            for v in d:
                cnt[v] = cnt.get(v, 0) + 1
        _, c = min(live, key=lambda p: len(p[1]))
        v = max(c, key=lambda x: (cnt[x], -x))
        a = go(inc + 1, [(j, d) for j, d in live if v not in d])
        b = go(inc, [(j, d - {v}) for j, d in live])
        return ("split", v, a, b)

    return go(0, [(j, C) for j, (C, _) in enumerate(fam)]), nodes[0]


def mask(s):
    m = 0
    for i in s:
        m |= 1 << i
    return m


def check_lb(fam, u, t, I=0, E=0, k=0):
    """Mirror of KSMin.checkLB (clause lookup by index)."""
    if t[0] == "pack":
        if not u <= k + len(t[1]):
            return False
        acc = 0
        for j in t[1]:
            c = fam[j]
            d = c ^ (c & E)
            if c & I or d & acc:
                return False
            acc |= d
        return True
    if t[0] == "dead":
        c = fam[t[1]]
        return c ^ (c & E) == 0
    _, v, a, b = t
    return (not (I >> v) & 1 and check_lb(fam, u, a, I | 1 << v, E, k + 1)
            and check_lb(fam, u, b, I, E | 1 << v, k))


def bt_term(items, depth=0):
    """Binary tree read by KSMin.BT.get: bit `depth` of the index picks the branch."""
    if len(items) == 1:
        _, (C, T) = items[0]
        return "(.leaf %d %d)" % (mask(C), mask(T))
    lo = [it for it in items if not (it[0] >> depth) & 1]
    hi = [it for it in items if (it[0] >> depth) & 1]
    lo, hi = lo or hi[:1], hi or lo[:1]            # an empty side repeats a valid leaf
    return "(.node %s %s)" % (bt_term(lo, depth + 1), bt_term(hi, depth + 1))


def lb_term(t):
    if t[0] == "pack":
        return "(.pack [%s])" % ", ".join(map(str, t[1]))
    if t[0] == "dead":
        return "(.dead %d)" % t[1]
    return "(.split %d %s %s)" % (t[1], lb_term(t[2]), lb_term(t[3]))


CHUNK = 300     # a large tree is cut into definitions of at most this many nodes, because
                # Lean cannot elaborate a single term with tens of thousands of nodes


def lb_defs(tree):
    """Lean source defining `tree`, with big subtrees as separate definitions tree_0, ..."""
    size = {}

    def sz(t):
        s = 1 if t[0] != "split" else 1 + sz(t[2]) + sz(t[3])
        size[id(t)] = s
        return s

    sz(tree)
    defs = []

    def ref(t):
        if t[0] != "split":
            return lb_term(t)
        if size[id(t)] <= CHUNK:
            name = "tree_%d" % len(defs)
            defs.append("set_option maxRecDepth 100000 in\ndef %s : LB :=\n  %s\n"
                        % (name, lb_term(t)))
            return name
        return "(.split %d %s %s)" % (t[1], ref(t[2]), ref(t[3]))

    if size[id(tree)] <= CHUNK:
        top = lb_term(tree)
    else:
        top = "(.split %d %s %s)" % (tree[1], ref(tree[2]), ref(tree[3]))
    defs.append("set_option maxRecDepth 100000 in\ndef tree : LB :=\n  %s" % top)
    return "\n".join(defs)


def emit(key):
    coords, dot, u, sel, fmt = POOLS[key]()
    n = len(coords)
    assert len(set(coords)) == n, "a ray is listed twice"
    pairs, triads = graph(coords, dot)
    fam = family(n, pairs, triads, u)
    assert all(col_ok(pairs, triads, C, T) for C, T in fam), "a colouring fails"
    tree, nodes = lower_bound_tree(fam, u)
    assert check_lb([mask(C) for C, _ in fam], u, tree), "lower-bound tree fails"
    assert len(sel) == u
    pos = {s: i for i, s in enumerate(sel)}
    sp = [(pos[i], pos[j]) for i, j in pairs if i in pos and j in pos]
    st = [tuple(pos[x] for x in t) for t in triads if all(x in pos for x in t)]
    cert, cnodes = refute(u, sp, st)
    begin, end = "-- BEGIN GENERATED (%s)" % key, "-- END GENERATED (%s)" % key
    block = """%s
/-- Generated by ks_lean_minimality.py: %d rays, %d orthogonal pairs, %d triads;
    %d colourable sets; lower-bound tree with %d nodes; %d-ray witness, certificate with
    %d nodes. -/
def rays : List R := [
  %s]

def pairs : List (Nat × Nat) := [%s]

def triads : List (Nat × Nat × Nat) := [%s]

def fam : BT :=
  %s

%s

def sel : List Nat := [%s]

def cert : Cert :=
  %s
%s""" % (begin, n, len(pairs), len(triads), len(fam), nodes, u, cnodes,
         ",\n  ".join(fmt(c) for c in coords),
         ", ".join("(%d, %d)" % p for p in pairs),
         ", ".join("(%d, %d, %d)" % t for t in triads),
         bt_term(list(enumerate(fam))), lb_defs(tree),
         ", ".join(map(str, sel)), cert, end)
    path = HERE / "lean" / "Minimality.lean"
    text = path.read_text(encoding="utf-8")
    assert text.count(begin) == 1 and text.count(end) == 1
    i, j = text.index(begin), text.index(end)
    path.write_text(text[:i] + block + text[j + len(end):], encoding="utf-8", newline="\n")
    print("%s: %d rays, %d pairs, %d triads, minimum %d; %d colourable sets, tree %d nodes, "
          "witness certificate %d nodes" % (key, n, len(pairs), len(triads), u, len(fam),
                                            nodes, cnodes), flush=True)


if __name__ == "__main__":
    for k in sys.argv[1:] or list(POOLS):
        emit(k)
