"""
ks_islands_d4.py -- Algebraic islands survey in dimension 4 (sketch)
====================================================================

A d=4 analogue of ks_islands.py. Same pipeline:

    alphabet  ->  pool of canonicalized rays in C^4
              ->  orthogonality graph + tetrads (4-element bases)
              ->  SAT uncolorability  ->  greedy minimization

Reference points:
  - CEG-18  (Cabello-Estebaranz-Garcia-Alcaine 1996): lives in {0, +/-1}^4
  - Peres-24 (Peres 1991): lives in {0, +/-1, +/-sqrt(2)}^4 unsigned-coord-perm orbit
  - Mermin-Peres "magic square" needs operator-level structure; not in scope here.

Goal of this run: confirm the integer alphabet is KS-uncolorable in d=4,
recover a small KS set (target ~18-24), then test Eisenstein and Gaussian
analogues to see whether the d=3 norm-<=2 thesis still controls things
once a real Hadamard exists at the seed.

Random seed 42 for reproducibility (matches contextuality convention).
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

import cmath
import math
import random
import time
from itertools import combinations, product
from collections import Counter

random.seed(42)

try:
    from pysat.solvers import Glucose4
    HAS_SAT = True
except ImportError:
    HAS_SAT = False
    print("WARNING: python-sat not available - install with: pip install python-sat")

EPS = 1e-9
DIM = 4


# ----------------------------------------------------------------------
# Canonicalization & inner product (complex)
# ----------------------------------------------------------------------
def canonicalize(v):
    """Canonical form of a complex ray.
    Divide by the first nonzero component, then by its modulus, then
    round to a hashable tuple. Rays related by any nonzero complex scalar
    collapse to one key."""
    v = list(v)
    if all(abs(x) < EPS for x in v):
        return None
    # Find first nonzero, scale so it becomes 1
    for x in v:
        if abs(x) > EPS:
            v = [c / x for c in v]
            break
    # Already first-nonzero=1, just round
    return tuple((round(c.real, 8), round(c.imag, 8)) for c in v)


def hdot(u, v):
    """Hermitian inner product <u|v> = sum conj(u_i) * v_i."""
    return sum((a.conjugate() if isinstance(a, complex) else a) * b for a, b in zip(u, v))


def is_orthogonal(u, v):
    return abs(hdot(u, v)) < EPS


# ----------------------------------------------------------------------
# Pool generation
# ----------------------------------------------------------------------
def make_pool(alphabet, label, max_rays=None):
    """Generate canonicalized nonzero vectors in alphabet^4."""
    pool_set = {}
    for tup in product(alphabet, repeat=DIM):
        v = tuple(complex(x) for x in tup)
        key = canonicalize(v)
        if key is None:
            continue
        if key not in pool_set:
            pool_set[key] = v
        if max_rays is not None and len(pool_set) >= max_rays:
            break
    keys = list(pool_set.keys())
    vecs = [pool_set[k] for k in keys]
    print(f"[{label}] alphabet size {len(alphabet)} -> pool size {len(vecs)}")
    return keys, vecs


# ----------------------------------------------------------------------
# Orthogonality graph + tetrads
# ----------------------------------------------------------------------
def build_graph(vecs):
    n = len(vecs)
    pairs = []
    for i, j in combinations(range(n), 2):
        if is_orthogonal(vecs[i], vecs[j]):
            pairs.append((i, j))
    print(f"  orthogonal pairs: {len(pairs)}")
    return pairs


def find_tetrads(vecs, pairs, cap=200000):
    """Enumerate mutually orthogonal 4-tuples (bases of C^4).
    Builds adjacency, then extends 3-cliques by a common neighbour.
    `cap` short-circuits pathological pools."""
    n = len(vecs)
    adj = [set() for _ in range(n)]
    for i, j in pairs:
        adj[i].add(j)
        adj[j].add(i)
    tetrads = []
    for i, j in pairs:
        if len(tetrads) > cap:
            break
        common_ij = adj[i] & adj[j]
        common_ij = {k for k in common_ij if k > j}
        for k in common_ij:
            common_ijk = common_ij & adj[k]
            for l in common_ijk:
                if l > k:
                    tetrads.append((i, j, k, l))
                    if len(tetrads) > cap:
                        break
    print(f"  tetrads (4-bases): {len(tetrads)}")
    return tetrads


# ----------------------------------------------------------------------
# SAT KS-uncolorability test
# ----------------------------------------------------------------------
def sat_uncolorable(n, pairs, tetrads):
    """A KS-uncolorable set in d=4 admits no assignment of {0,1} to rays
    such that each tetrad has exactly one '1' and each orthogonal pair
    has at most one '1'. Returns True iff UNSAT."""
    if not HAS_SAT:
        return None
    g = Glucose4()
    # Variable i+1 (1-indexed) means "ray i is green (=1)".
    for tet in tetrads:
        a, b, c, d = (i + 1 for i in tet)
        # at-least-one
        g.add_clause([a, b, c, d])
        # at-most-one (pairwise mutex within the tetrad)
        for u, v in combinations((a, b, c, d), 2):
            g.add_clause([-u, -v])
    for i, j in pairs:
        # at-most-one across orthogonal pairs (subsumed by tetrad mutex
        # for pairs already in some tetrad, but cheap to add)
        g.add_clause([-(i + 1), -(j + 1)])
    sat = g.solve()
    g.delete()
    return not sat


# ----------------------------------------------------------------------
# Greedy minimization
# ----------------------------------------------------------------------
def greedy_minimize(n, pairs, tetrads, trials=20):
    """Try to shrink the ray set by removing rays that keep KS-uncolorability."""
    best = None
    for t in range(trials):
        keep = list(range(n))
        random.shuffle(keep)
        active = set(range(n))
        for r in keep:
            cand = active - {r}
            sub_pairs = [(i, j) for (i, j) in pairs if i in cand and j in cand]
            sub_tets = [tet for tet in tetrads if all(x in cand for x in tet)]
            if not sub_tets:
                continue
            # Renumber for SAT
            idx = {old: new for new, old in enumerate(sorted(cand))}
            rp = [(idx[i], idx[j]) for (i, j) in sub_pairs]
            rt = [tuple(idx[x] for x in tet) for tet in sub_tets]
            if sat_uncolorable(len(cand), rp, rt):
                active = cand
        size = len(active)
        if best is None or size < best:
            best = size
            print(f"  trial {t+1}: minimized to {size} rays")
    return best


# ----------------------------------------------------------------------
# Survey
# ----------------------------------------------------------------------
def run_island(label, alphabet):
    print(f"\n{'='*60}\n{label}\n{'='*60}")
    keys, vecs = make_pool(alphabet, label)
    pairs = build_graph(vecs)
    tetrads = find_tetrads(vecs, pairs)
    if not tetrads:
        print("  no tetrads -> not a KS candidate")
        return
    t0 = time.time()
    unc = sat_uncolorable(len(vecs), pairs, tetrads)
    print(f"  full pool KS-uncolorable: {unc}  ({time.time()-t0:.2f}s)")
    if unc:
        m = greedy_minimize(len(vecs), pairs, tetrads, trials=10)
        print(f"  best minimized size: {m}")


def main():
    print(f"d=4 algebraic-islands survey  (SAT engine: {'Glucose4' if HAS_SAT else 'none'})")

    # 1. Real integer alphabet -- expected to host CEG-18 / Peres-24
    run_island("Integer  {0, +/-1}", [0, 1, -1])

    # 2. Real with sqrt(2) -- d=3 Peres analogue
    s2 = math.sqrt(2)
    run_island("Real-sqrt2  {0, +/-1, +/-sqrt(2)}", [0, 1, -1, s2, -s2])

    # 3. Gaussian integers -- {0, +/-1, +/-i}
    run_island("Gaussian  {0, +/-1, +/-i}", [0, 1, -1, 1j, -1j])

    # 4. Eisenstein -- cube roots of unity
    om = cmath.exp(2j * math.pi / 3)
    run_island("Eisenstein  {0, +/-1, +/-omega, +/-omega^2}",
               [0, 1, -1, om, -om, om*om, -om*om])

    # 5. Mixed integer + Gaussian -- {0, +/-1, +/-i, +/-(1+i)}
    run_island("Z[i] extended  {0, +/-1, +/-i, +/-(1+i)}",
               [0, 1, -1, 1j, -1j, 1+1j, -(1+1j)])


if __name__ == "__main__":
    main()
