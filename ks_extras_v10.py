"""v10: structural facts about the named KS sets, each decided exactly.

  profile   pairs, bases, degree sequence, ray-criticality (every single-ray
            deletion colourable) of each certified witness and of CK-31, CK-33.
  bases     how many bases are individually indispensable (dropping that basis's
            "exactly one" rule, keeping every pair exclusion, gives a colouring),
            and whether two bases suffice when none is.
  iso       graph isomorphism tests (networkx VF2) between named sets and pools.
  census    ALL minimum-size uncolourable subsets of a raw pool, by exhaustive
            implicit-hitting-set enumeration, and their orbits under the 48
            signed coordinate permutations.

Usage:  python ks_extras_v10.py [profile|bases|iso|census ...]
Writes: results/extras_v10.jsonl
"""
import itertools
import json
import sys
import time
from collections import Counter
from pathlib import Path

import networkx as nx
from pysat.card import ITotalizer
from pysat.solvers import Glucose4

import ks_bpqs_exact as B
import ks_recertify_v10 as R
from ks_certify_fast3 import FastPool

HERE = Path(__file__).resolve().parent
OUT = HERE / "results" / "extras_v10.jsonl"
CK33 = [(0, 0, 1), (0, 1, -1), (0, 1, 0), (0, 1, 1), (1, -2, -1), (1, -2, 0), (1, -2, 1),
        (1, -1, -2), (1, -1, -1), (1, -1, 0), (1, -1, 1), (1, -1, 2), (1, 0, -2), (1, 0, -1),
        (1, 0, 0), (1, 0, 1), (1, 0, 2), (1, 1, -2), (1, 1, -1), (1, 1, 0), (1, 1, 1), (1, 1, 2),
        (1, 2, -1), (1, 2, 0), (1, 2, 1), (2, -1, -1), (2, -1, 0), (2, -1, 1), (2, 0, -1),
        (2, 0, 1), (2, 1, -1), (2, 1, 0), (2, 1, 1)]


def emit(rec):
    rec["date"] = time.strftime("%Y-%m-%d %H:%M")
    print(json.dumps(rec), flush=True)
    with OUT.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")


def named(key):
    """(rays, pairs, triads) with pairs/triads as sorted tuples."""
    if key == "ck33":
        F = R.FQ
        rays = [tuple(F.el(c) for c in v) for v in CK33]
        pairs, triads, _ = R.structure(rays)
        return rays, pairs, triads
    if key.endswith("-raw") or key.endswith("-completed"):
        akey, comp, _ = R.POOLS[key]
        F, alpha, _ = R.ALPHABETS[akey]
        rays = R.build(alpha, F, complete=comp, cap=3000)
        pairs, triads, _ = R.structure(rays)
        return rays, pairs, triads
    rays, orth, bases = B.load_set(key)
    return rays, sorted(tuple(sorted(p)) for p in orth), bases


def available_sets():
    keys = ["ck33"]
    for k in B.SETS:
        try:
            B.load_set(k)
            keys.append(k)
        except Exception:
            pass
    return keys


def profile():
    for key in available_sets():
        rays, pairs, triads = named(key)
        n = len(rays)
        deg = Counter()
        for i, j in pairs:
            deg[i] += 1
            deg[j] += 1
        seq = dict(sorted(Counter(deg[i] for i in range(n)).items()))
        unc = not R.colourable(range(n), pairs, triads)
        crit = unc and all(R.colourable([i for i in range(n) if i != r], pairs, triads) for r in range(n))
        emit({"what": "profile", "set": key, "rays": n, "pairs": len(pairs), "bases": len(triads),
              "degree_sequence": seq, "uncolourable": unc, "ray_critical": crit})


def colourable_without(n, pairs, triads, dropped):
    s = Glucose4()
    for i, j in pairs:
        s.add_clause([-(i + 1), -(j + 1)])
    for k, t in enumerate(triads):
        if k not in dropped:
            s.add_clause([x + 1 for x in t])
    ok = s.solve()
    s.delete()
    return ok


def bases():
    for key in available_sets():
        rays, pairs, triads = named(key)
        n, m = len(rays), len(triads)
        single = [k for k in range(m) if colourable_without(n, pairs, triads, {k})]
        rec = {"what": "bases", "set": key, "bases": m, "individually_indispensable": len(single)}
        if not single:
            two = sum(1 for a, b in itertools.combinations(range(m), 2)
                      if colourable_without(n, pairs, triads, {a, b}))
            rec["pairs_of_bases_whose_removal_colours"] = two
        emit(rec)


def graph(key):
    rays, pairs, triads = named(key)
    g = nx.Graph()
    g.add_nodes_from(range(len(rays)))
    g.add_edges_from(pairs)
    return g


def iso():
    tests = [("peres33", "sqrtm2-33"), ("peres-raw", "sqrtm2-raw"), ("peres-completed", "sqrtm2-completed"),
             ("peres33", "eisenstein33"), ("peres33", "ck33"), ("eisenstein33", "ck33")]
    for a, b in tests:
        emit({"what": "iso", "a": a, "b": b, "isomorphic": nx.is_isomorphic(graph(a), graph(b))})


def signed_perms(rays):
    index = {R.canon(v): i for i, v in enumerate(rays)}
    maps = []
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product((1, -1), repeat=3):
            img = []
            for v in rays:
                w = tuple(v[perm[k]] if signs[k] == 1 else -v[perm[k]] for k in range(3))
                img.append(index[R.canon(w)])
            maps.append(img)
    return maps


def census(pool_keys=("integer-raw", "peres-raw", "sqrtm2-raw", "eisenstein-raw", "heegner7-raw")):
    for key in pool_keys:
        t0 = time.time()
        rays, pairs, triads = named(key)
        n = len(rays)
        rec0 = None
        for line in (HERE / "results" / "recertify_v10.jsonl").read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            if r["pool"] == key and r.get("certified_minimum"):
                rec0 = r
        m = rec0["certified_minimum"]
        ps = FastPool(n, pairs, triads)
        hit = Glucose4()
        tot = ITotalizer(lits=list(range(1, n + 1)), ubound=m, top_id=n)
        hit.append_formula(tot.cnf)
        found = []
        while hit.solve(assumptions=[-tot.rhs[m]]):
            model = hit.get_model()
            S = [i for i in range(n) if model[i] > 0]
            ps.maybe_rebuild()
            if ps.colourable(S):
                M = ps.grow(S)
                hit.add_clause([i + 1 for i in range(n) if i not in M])
            else:
                assert len(S) == m, "found a set below the certified minimum"
                found.append(frozenset(S))
                hit.add_clause([i + 1 for i in range(n) if i not in S])
        maps = signed_perms(rays)
        orbits, seen = 0, set()
        for S in found:
            if S in seen:
                continue
            orbits += 1
            for g in maps:
                seen.add(frozenset(g[i] for i in S))
        assert seen == set(found), "orbit closure differs from enumeration"
        union = set().union(*found)
        core = set(found[0]).intersection(*found)
        nb = sorted(Counter(len(R.bases_of(S, triads)) for S in found).items())
        emit({"what": "census", "pool": key, "minimum": m, "minimum_sets": len(found),
              "orbits_under_signed_permutations": orbits, "rays_used": len(union),
              "rays_in_every_set": len(core), "basis_counts": nb, "seconds": round(time.time() - t0, 1)})
        tot.delete()
        hit.delete()
        ps.delete()


if __name__ == "__main__":
    jobs = sys.argv[1:] or ["profile", "bases", "iso", "census"]
    for job in jobs:
        {"profile": profile, "bases": bases, "iso": iso, "census": census}[job]()
