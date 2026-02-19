"""
ks_ocus_all_pools.py -- OCUS proof of minimum KS size for all 6 algebraic pools
==================================================================================

For the integer pool, OCUS already proved 31 is optimal (ks_maxsat_optimal.py).
This script runs the same OCUS procedure on ALL six pools to certify every
entry in Table I of the sub31 letter.

Expected results:
  Integer:    31 (already proved)
  Peres:      33 (to certify)
  Eisenstein: 33 (to certify)
  Z[sqrt(-2)]:33 (to certify)
  Heegner-7:  43 (to certify)
  Golden:     52 (to certify, may be slow due to 205 rays)
"""

import sys
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

import cmath
import math
import random
import time
from itertools import combinations
from math import gcd

from pysat.solvers import Glucose4
from pysat.card import CardEnc, EncType

from ks_complex import (
    generate_eisenstein_rays,
    hermitian_dot,
    canonicalize_complex_ray,
)
from ks_new_islands import (
    generate_rays_from_alphabet,
    hermitian_completion,
)

random.seed(42)


# =====================================================================
# Common functions
# =====================================================================

def build_pairs_triads(rays, tol=1e-9):
    """Build orthogonal pairs and triads from ray list."""
    n = len(rays)
    pairs = []
    adj = {i: set() for i in range(n)}
    for i in range(n):
        for j in range(i + 1, n):
            dot = hermitian_dot(rays[i], rays[j])
            if abs(dot) < tol:
                pairs.append((i, j))
                adj[i].add(j)
                adj[j].add(i)
    triads = []
    for i in range(n):
        neighbors_i = sorted(adj[i])
        for idx_j, j in enumerate(neighbors_i):
            if j <= i:
                continue
            for k in neighbors_i[idx_j + 1:]:
                if k <= j:
                    continue
                if k in adj[j]:
                    triads.append((i, j, k))
    return pairs, triads, adj


def build_int_pairs_triads(coords):
    """Build orthogonal pairs and triads for integer rays (exact dot product)."""
    n = len(coords)
    pairs = []
    adj = {i: set() for i in range(n)}
    for i in range(n):
        for j in range(i + 1, n):
            if sum(x * y for x, y in zip(coords[i], coords[j])) == 0:
                pairs.append((i, j))
                adj[i].add(j)
                adj[j].add(i)
    triads = []
    for i in range(n):
        neighbors_i = sorted(adj[i])
        for idx_j, j in enumerate(neighbors_i):
            if j <= i:
                continue
            for k in neighbors_i[idx_j + 1:]:
                if k <= j:
                    continue
                if k in adj[j]:
                    triads.append((i, j, k))
    return pairs, triads, adj


def is_ks_subset(ray_indices, triads, pairs):
    """Check if a subset of rays is KS-uncolorable."""
    sel = set(ray_indices)
    sub_triads = [(a, b, c) for a, b, c in triads
                  if a in sel and b in sel and c in sel]
    sub_pairs = [(i, j) for i, j in pairs
                 if i in sel and j in sel]
    if not sub_triads:
        return False

    remap = {old: new for new, old in enumerate(sorted(sel))}
    solver = Glucose4()
    for a, b, c in sub_triads:
        ra, rb, rc = remap[a], remap[b], remap[c]
        va, vb, vc = ra + 1, rb + 1, rc + 1
        solver.add_clause([va, vb, vc])
        solver.add_clause([-va, -vb])
        solver.add_clause([-va, -vc])
        solver.add_clause([-vb, -vc])
    for i, j in sub_pairs:
        ri, rj = remap[i], remap[j]
        solver.add_clause([-(ri + 1), -(rj + 1)])
    result = solver.solve()
    solver.delete()
    return not result


def greedy_minimize(n_rays, pairs, triads, n_trials=500):
    """Find a minimal KS subset via greedy deletion."""
    best = None
    best_n = n_rays

    for trial in range(n_trials):
        active = list(range(n_rays))
        random.shuffle(active)

        for ray in list(active):
            test = [r for r in active if r != ray]
            if is_ks_subset(test, triads, pairs):
                active = test

        if len(active) < best_n:
            best_n = len(active)
            best = sorted(active)

    return best, best_n


def ocus_proof(name, n_rays, triads, pairs, known_min, time_limit=600):
    """Run OCUS to prove the known minimum is optimal within the pool.

    Tests from (known_min - 1) down until exhaustion or time limit.
    """
    print(f"\n  OCUS proof for {name} (pool={n_rays}, known min={known_min})")

    t0 = time.time()

    # Precompute: which rays participate in each triad and pair
    ray_triads = {i: [] for i in range(n_rays)}
    for idx, (a, b, c) in enumerate(triads):
        ray_triads[a].append(idx)
        ray_triads[b].append(idx)
        ray_triads[c].append(idx)

    ray_pairs = {i: [] for i in range(n_rays)}
    for idx, (a, b) in enumerate(pairs):
        ray_pairs[a].append(idx)
        ray_pairs[b].append(idx)

    proved_down_to = known_min  # We'll track how far down we prove

    for target_n in range(known_min - 1, max(known_min - 15, 14), -1):
        if time.time() - t0 > time_limit:
            print(f"    Time limit at n={target_n}")
            break

        # CEGAR loop: find n-ray KS subsets or prove none exist
        outer = Glucose4()
        sel_lits = list(range(1, n_rays + 1))
        top_var = n_rays

        # Cardinality: exactly target_n rays
        al = CardEnc.atleast(sel_lits, bound=target_n, top_id=top_var,
                             encoding=EncType.totalizer)
        if al.clauses:
            top_var = max(top_var,
                          max(abs(l) for cl in al.clauses for l in cl))
            for cl in al.clauses:
                outer.add_clause(cl)

        am = CardEnc.atmost(sel_lits, bound=target_n, top_id=top_var,
                            encoding=EncType.totalizer)
        if am.clauses:
            top_var = max(top_var,
                          max(abs(l) for cl in am.clauses for l in cl))
            for cl in am.clauses:
                outer.add_clause(cl)

        # Pruning: rays with zero triads can't contribute
        for i in range(n_rays):
            if not ray_triads[i]:
                outer.add_clause([-(i + 1)])

        iterations = 0
        t_target = time.time()
        found_ks = False

        while time.time() - t0 < time_limit:
            if not outer.solve():
                elapsed = time.time() - t_target
                print(f"    n={target_n}: EXHAUSTED ({iterations:,} iters, "
                      f"{elapsed:.1f}s) -- no KS set of this size")
                outer.delete()
                proved_down_to = target_n
                break

            model = outer.get_model()
            selected = [i for i in range(n_rays) if model[i] > 0]

            iterations += 1

            if is_ks_subset(selected, triads, pairs):
                elapsed = time.time() - t_target
                print(f"    n={target_n}: FOUND KS set! "
                      f"({iterations} iters, {elapsed:.1f}s)")
                outer.delete()
                found_ks = True
                break

            # Get the coloring and derive correction clause
            sel_set = set(selected)
            sub_triads_sel = [(a, b, c) for a, b, c in triads
                              if a in sel_set and b in sel_set and c in sel_set]
            sub_pairs_sel = [(i, j) for i, j in pairs
                             if i in sel_set and j in sel_set]

            remap = {old: new for new, old in enumerate(sorted(selected))}
            inv_remap = {new: old for old, new in remap.items()}
            inner = Glucose4()
            for a, b, c in sub_triads_sel:
                ra, rb, rc = remap[a], remap[b], remap[c]
                va, vb, vc = ra + 1, rb + 1, rc + 1
                inner.add_clause([va, vb, vc])
                inner.add_clause([-va, -vb])
                inner.add_clause([-va, -vc])
                inner.add_clause([-vb, -vc])
            for i, j in sub_pairs_sel:
                ri, rj = remap[i], remap[j]
                inner.add_clause([-(ri + 1), -(rj + 1)])
            inner.solve()
            coloring_model = inner.get_model()
            inner.delete()

            colored = set()
            for new_idx in range(target_n):
                if new_idx < len(coloring_model) and coloring_model[new_idx] > 0:
                    colored.add(inv_remap[new_idx])

            correction = set()
            deselected = [i for i in range(n_rays) if i not in sel_set]

            for r in deselected:
                for t_idx in ray_triads[r]:
                    a, b, c = triads[t_idx]
                    others = [x for x in (a, b, c) if x != r]
                    if all(x in sel_set for x in others):
                        all_green = (r in colored and
                                     others[0] in colored and
                                     others[1] in colored)
                        none_green = (r not in colored and
                                      others[0] not in colored and
                                      others[1] not in colored)
                        if all_green or none_green:
                            correction.add(r)
                            break

                if r in correction:
                    continue

                for p_idx in ray_pairs[r]:
                    a, b = pairs[p_idx]
                    other = b if a == r else a
                    if other in sel_set:
                        if r in colored and other in colored:
                            correction.add(r)
                            break

            if correction:
                outer.add_clause([r + 1 for r in correction])
            else:
                outer.add_clause([-(i + 1) for i in selected])

            if iterations % 5000 == 0:
                elapsed = time.time() - t_target
                rate = iterations / elapsed if elapsed > 0 else 0
                print(f"      ... {iterations:,} iters [{elapsed:.1f}s, "
                      f"{rate:.0f}/s]")

        else:
            elapsed = time.time() - t_target
            print(f"    n={target_n}: time limit ({iterations:,} iters, "
                  f"{elapsed:.1f}s)")
            outer.delete()

        if found_ks:
            print(f"\n  UNEXPECTED: found KS set smaller than {known_min}!")
            return target_n

    elapsed = time.time() - t0
    if proved_down_to < known_min:
        print(f"\n  *** PROVED: minimum KS in {name} pool = {known_min} ***")
        print(f"      (exhausted n={known_min-1} down to n={proved_down_to}, "
              f"{elapsed:.1f}s)")
    else:
        print(f"\n  Could not complete proof ({elapsed:.1f}s)")

    return proved_down_to


# =====================================================================
# Build all six pools and run OCUS
# =====================================================================

def main():
    print("=" * 70)
    print("OCUS PROOF OF MINIMUM KS SIZE FOR ALL 6 ALGEBRAIC POOLS")
    print("=" * 70)

    t_start = time.time()
    results = {}

    # ---- 1. Integer (CK-31) ----
    print(f"\n{'='*70}")
    print("POOL 1: Integer {0,±1,±2}")
    print(f"{'='*70}")

    int_rays = []
    seen = set()
    for a in range(-2, 3):
        for b in range(-2, 3):
            for c in range(-2, 3):
                if a == 0 and b == 0 and c == 0:
                    continue
                g = gcd(gcd(abs(a), abs(b)), abs(c))
                v = (a // g, b // g, c // g)
                for coord in v:
                    if coord != 0:
                        if coord < 0:
                            v = (-v[0], -v[1], -v[2])
                        break
                if v not in seen:
                    seen.add(v)
                    int_rays.append(v)

    int_pairs, int_triads, int_adj = build_int_pairs_triads(int_rays)
    print(f"  Pool: {len(int_rays)} rays, {len(int_pairs)} pairs, "
          f"{len(int_triads)} triads")
    proved = ocus_proof("Integer", len(int_rays), int_triads, int_pairs,
                        known_min=31, time_limit=120)
    results["Integer"] = (49, 31, proved)

    # ---- 2. Peres (Z[sqrt(2)]) ----
    print(f"\n{'='*70}")
    print("POOL 2: Peres Z[sqrt(2)]")
    print(f"{'='*70}")

    s2 = math.sqrt(2)
    peres_alph = [complex(x) for x in [0, 1, -1, s2, -s2]]
    peres_rays = generate_rays_from_alphabet(peres_alph)
    peres_pairs, peres_triads, peres_adj = build_pairs_triads(peres_rays)
    print(f"  Pool: {len(peres_rays)} rays, {len(peres_pairs)} pairs, "
          f"{len(peres_triads)} triads")
    proved = ocus_proof("Peres", len(peres_rays), peres_triads, peres_pairs,
                        known_min=33, time_limit=120)
    results["Peres"] = (len(peres_rays), 33, proved)

    # ---- 3. Eisenstein (Z[omega]) ----
    print(f"\n{'='*70}")
    print("POOL 3: Eisenstein Z[omega]")
    print(f"{'='*70}")

    eis_rays = generate_eisenstein_rays(max_coeff=1, dim=3, norm_cutoff=3)
    eis_pairs, eis_triads, eis_adj = build_pairs_triads(eis_rays)
    print(f"  Pool: {len(eis_rays)} rays, {len(eis_pairs)} pairs, "
          f"{len(eis_triads)} triads")
    proved = ocus_proof("Eisenstein", len(eis_rays), eis_triads, eis_pairs,
                        known_min=33, time_limit=120)
    results["Eisenstein"] = (len(eis_rays), 33, proved)

    # ---- 4. Z[sqrt(-2)] ----
    print(f"\n{'='*70}")
    print("POOL 4: Z[sqrt(-2)]")
    print(f"{'='*70}")

    sd2 = cmath.sqrt(-2)
    zsqrt2_alph = [0, 1, -1, sd2, -sd2]
    zsqrt2_rays = generate_rays_from_alphabet(zsqrt2_alph)
    zsqrt2_pairs, zsqrt2_triads, zsqrt2_adj = build_pairs_triads(zsqrt2_rays)
    print(f"  Pool: {len(zsqrt2_rays)} rays, {len(zsqrt2_pairs)} pairs, "
          f"{len(zsqrt2_triads)} triads")
    proved = ocus_proof("Z[sqrt(-2)]", len(zsqrt2_rays), zsqrt2_triads,
                        zsqrt2_pairs, known_min=33, time_limit=120)
    results["Z[sqrt(-2)]"] = (len(zsqrt2_rays), 33, proved)

    # ---- 5. Heegner-7 ----
    print(f"\n{'='*70}")
    print("POOL 5: Heegner-7 Z[(1+sqrt(-7))/2]")
    print(f"{'='*70}")

    gen7 = (1 + cmath.sqrt(-7)) / 2
    h7_alph = [0, 1, -1, gen7, -gen7, gen7.conjugate(), -gen7.conjugate()]
    h7_rays = generate_rays_from_alphabet(h7_alph)
    h7_pairs, h7_triads, h7_adj = build_pairs_triads(h7_rays)
    print(f"  Pool: {len(h7_rays)} rays, {len(h7_pairs)} pairs, "
          f"{len(h7_triads)} triads")
    proved = ocus_proof("Heegner-7", len(h7_rays), h7_triads, h7_pairs,
                        known_min=43, time_limit=300)
    results["Heegner-7"] = (len(h7_rays), 43, proved)

    # ---- 6. Golden (Z[phi] + completion) ----
    print(f"\n{'='*70}")
    print("POOL 6: Golden Z[phi] + cross-product completion")
    print(f"{'='*70}")

    phi = (1 + math.sqrt(5)) / 2
    gold_alph = [complex(x) for x in [0, 1, -1, phi, -phi]]
    gold_rays_raw = generate_rays_from_alphabet(gold_alph)
    gold_rays = hermitian_completion(gold_rays_raw)
    gold_pairs, gold_triads, gold_adj = build_pairs_triads(gold_rays)
    print(f"  Pool: {len(gold_rays)} rays, {len(gold_pairs)} pairs, "
          f"{len(gold_triads)} triads")
    proved = ocus_proof("Golden", len(gold_rays), gold_triads, gold_pairs,
                        known_min=52, time_limit=600)
    results["Golden"] = (len(gold_rays), 52, proved)

    # ---- Summary ----
    t_total = time.time() - t_start

    print(f"\n{'='*70}")
    print("SUMMARY: OCUS CERTIFICATION OF MINIMUM KS SIZES")
    print(f"{'='*70}")
    print(f"{'Island':<20} {'Pool':>5} {'Known':>6} {'Proved':>7} {'Status':>12}")
    print("-" * 55)

    all_certified = True
    for name in ["Integer", "Peres", "Eisenstein", "Z[sqrt(-2)]",
                 "Heegner-7", "Golden"]:
        pool_size, known, proved_to = results[name]
        if proved_to < known:
            status = "CERTIFIED"
        else:
            status = "INCOMPLETE"
            all_certified = False
        print(f"{name:<20} {pool_size:>5} {known:>6} {proved_to:>7} "
              f"{status:>12}")

    print(f"\nTotal time: {t_total:.1f}s")

    if all_certified:
        print(f"\n*** ALL six pool minima certified by OCUS ***")
        print(f"    Every entry in Table I is the exact minimum within its pool.")
    else:
        incomplete = [n for n, (_, _, p) in results.items()
                      if p >= results[n][1]]
        print(f"\n  Incomplete: {', '.join(incomplete)}")
        print(f"  (May need more time or different strategy for large pools)")


if __name__ == "__main__":
    main()
