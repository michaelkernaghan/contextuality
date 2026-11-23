"""Certification v4: certify3 plus two sound reductions.

1. Core.  A ray lying in no triad of a set U can be coloured 0 in any colouring of the
   rest of U (it meets no triad, and a 0 never violates a pair).  So a minimal uncolourable
   set has every ray in a triad of itself, and lies inside the core of the pool: what is
   left after repeatedly deleting rays that lie in no triad of the remaining rays.  The
   minimum over the pool equals the minimum over the core.

2. Orbit clauses.  Colourability depends only on the orthogonality graph (the triads are
   its triangles), so an automorphism g of that graph maps a colourable set M to a
   colourable set g(M).  Whenever certify3 would add the clause "an uncolourable set has a
   ray outside M", we add it for g(M) as well, for every g in a set of automorphisms.
   Any subset of the automorphism group is sound; more elements prune more.

Both only add valid constraints to the hitting-set problem of certify3, whose soundness
argument (Section 2 of the paper) is unchanged.
"""
import time

import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher
from pysat.card import ITotalizer
from pysat.solvers import Glucose4

from ks_certify_fast3 import FastPool


def core(n, triads):
    """Indices of the core: iterate 'keep only rays lying in a triad of the kept rays'."""
    alive = set(range(n))
    while True:
        keep = set()
        for t in triads:
            if all(r in alive for r in t):
                keep.update(t)
        if keep == alive:
            return sorted(alive)
        alive = keep


def restrict(keep, pairs, triads):
    idx = {r: i for i, r in enumerate(keep)}
    p = [(idx[i], idx[j]) for i, j in pairs if i in idx and j in idx]
    t = [tuple(idx[r] for r in tr) for tr in triads if all(r in idx for r in tr)]
    return p, t


def automorphisms(n, pairs, limit):
    """Up to `limit` automorphisms of the orthogonality graph, as tuples g[i]."""
    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from(pairs)
    out = []
    for m in GraphMatcher(G, G).isomorphisms_iter():
        out.append(tuple(m[i] for i in range(n)))
        if len(out) >= limit:
            break
    return out


def check_group(n, pairs, perms):
    """Assert every permutation is an automorphism of the orthogonality graph."""
    E = {frozenset(p) for p in pairs}
    for g in perms:
        assert sorted(g) == list(range(n)), "not a permutation"
        assert all(frozenset((g[i], g[j])) in E for i, j in pairs), "not an automorphism"


def certify4(n, pairs, triads, ub_size, budget=1800, perms=None, verbose=False,
             log_every=5000):
    """Return (exact or None, ub, best set in pool indices or None, info dict).

    `ub_size` is an upper bound to start from (a known uncolourable set's size, or a dummy
    threshold for a lower-bound-only run).  best is None unless an uncolourable set smaller
    than ub_size was found.  `perms`: automorphisms of the pool's orthogonality graph as
    tuples g[i] (checked here); None means the identity only."""
    t0 = time.time()
    keep = core(n, triads)
    cp, ct = restrict(keep, pairs, triads)
    m = len(keep)
    perms = perms or [tuple(range(n))]
    check_group(n, pairs, perms)
    idx = {r: i for i, r in enumerate(keep)}
    group = []
    for g in perms:                      # the core is defined from the graph, so g preserves it
        assert all(g[r] in idx for r in keep)
        group.append(tuple(idx[g[r]] for r in keep))
    group = sorted(set(group))
    info = {"pool": n, "core": m, "core_pairs": len(cp), "core_triads": len(ct),
            "group_elements_used": len(group), "group_seconds": round(time.time() - t0, 1)}
    if verbose:
        print("  core %d of %d rays, %d triads; %d automorphisms (%.1fs)"
              % (m, n, len(ct), len(group), time.time() - t0), flush=True)

    ps = FastPool(m, cp, ct)
    ub, best = ub_size, None
    hit = Glucose4()
    tot = ITotalizer(lits=list(range(1, m + 1)), ubound=max(ub - 1, 1), top_id=m)
    hit.append_formula(tot.cnf)
    seen = set()
    it = 0
    try:
        while True:
            it += 1
            if time.time() - t0 > budget:
                why, exact = "budget exhausted", None
                break
            k = ub - 1
            if k < 1:
                why, exact = "optimal: ub = 1", ub
                break
            if not hit.solve(assumptions=[-tot.rhs[k]]):
                why, exact = "optimal: no hitting set smaller than ub", ub
                break
            model = hit.get_model()
            R = [i for i in range(m) if model[i] > 0]
            ps.maybe_rebuild()
            if not ps.colourable(R):
                ub, best = len(R), [keep[i] for i in R]
                if verbose:
                    print("      iter %7d  improved ub -> %d  (%.0fs)"
                          % (it, ub, time.time() - t0), flush=True)
                continue
            M = ps.grow(R)
            outside = [i for i in range(m) if i not in M]
            if not outside:
                why, exact = "core colourable", None
                break
            for g in group:
                cl = frozenset(g[i] for i in outside)
                if cl not in seen:
                    seen.add(cl)
                    hit.add_clause([i + 1 for i in cl])
            if verbose and it % log_every == 0:
                print("      iter %7d  |R|=%3d  ub=%d  clauses=%d  %.0fs"
                      % (it, len(R), ub, len(seen), time.time() - t0), flush=True)
    finally:
        tot.delete()
        hit.delete()
        ps.delete()
    info.update(iterations=it, clauses=len(seen), seconds=round(time.time() - t0, 1),
                reason=why)
    return exact, ub, best, info
