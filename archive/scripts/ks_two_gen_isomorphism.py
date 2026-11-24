"""
ks_two_gen_isomorphism.py -- Check if the 14 convergent two-generator pairs
produce graph-isomorphic minimal KS sets.

From the class-number survey: 25 of 28 two-generator alphabets are uncolorable,
with 14 converging to the same 33-vector minimum. If all 14 are graph-isomorphic,
this massively strengthens the "cancellation identity, not ambient field" thesis.
"""

import sys
sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

import cmath
import math
import random
import time
from collections import Counter

from pysat.solvers import Glucose4

from ks_complex import hermitian_dot, canonicalize_complex_ray
from ks_new_islands import generate_rays_from_alphabet

random.seed(42)


def build_pairs_triads(rays, tol=1e-9):
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


def is_ks_uncolorable(n, triads, pairs):
    if not triads:
        return False
    solver = Glucose4()
    for a, b, c in triads:
        va, vb, vc = a + 1, b + 1, c + 1
        solver.add_clause([va, vb, vc])
        solver.add_clause([-va, -vb])
        solver.add_clause([-va, -vc])
        solver.add_clause([-vb, -vc])
    for i, j in pairs:
        solver.add_clause([-(i+1), -(j+1)])
    result = solver.solve()
    solver.delete()
    return not result


def greedy_minimize(rays, pairs, triads, n_trials=200):
    n_rays = len(rays)
    best = list(range(n_rays))
    best_size = n_rays
    for trial in range(n_trials):
        current = list(range(n_rays))
        order = list(range(n_rays))
        random.shuffle(order)
        for candidate in order:
            if candidate not in current:
                continue
            test = [r for r in current if r != candidate]
            if len(test) < 20:
                break
            keep_set = set(test)
            remap = {old: new for new, old in enumerate(test)}
            sub_triads = [(remap[a], remap[b], remap[c])
                          for a, b, c in triads
                          if a in keep_set and b in keep_set and c in keep_set]
            sub_pairs = [(remap[i], remap[j])
                         for i, j in pairs
                         if i in keep_set and j in keep_set]
            if is_ks_uncolorable(len(test), sub_triads, sub_pairs):
                current = test
        if len(current) < best_size:
            best = current
            best_size = len(current)
    return best, best_size


def dedup_complex(vals):
    seen = set()
    result = []
    for v in vals:
        key = (round(v.real, 7), round(v.imag, 7))
        if key not in seen:
            seen.add(key)
            result.append(v)
    return result


def degree_sequence(n, pairs):
    """Return sorted degree sequence."""
    deg = [0] * n
    for i, j in pairs:
        deg[i] += 1
        deg[j] += 1
    return tuple(sorted(deg, reverse=True))


def try_vf2_isomorphism(n1, pairs1, n2, pairs2):
    """Check graph isomorphism using networkx VF2."""
    try:
        import networkx as nx
        from networkx.algorithms.isomorphism import GraphMatcher
        G1 = nx.Graph()
        G1.add_nodes_from(range(n1))
        G1.add_edges_from(pairs1)
        G2 = nx.Graph()
        G2.add_nodes_from(range(n2))
        G2.add_edges_from(pairs2)
        gm = GraphMatcher(G1, G2)
        return gm.is_isomorphic()
    except ImportError:
        return None  # networkx not available


# =================================================================
# Define the 8 generators
# =================================================================

sqrt2 = complex(math.sqrt(2))
sqrt3 = complex(math.sqrt(3))
sqrt5 = complex(math.sqrt(5))
phi = complex((1 + math.sqrt(5)) / 2)
omega = cmath.exp(2j * cmath.pi / 3)
sqrt_neg2 = cmath.sqrt(-2)
i_val = complex(0, 1)
h7 = (1 + cmath.sqrt(-7)) / 2

generators = {
    'sqrt2': sqrt2,
    'sqrt3': sqrt3,
    'sqrt5': sqrt5,
    'phi': phi,
    'omega': omega,
    'sqrt(-2)': sqrt_neg2,
    'i': i_val,
    'h7': h7,
}

from itertools import combinations


if __name__ == "__main__":
    print("=" * 70)
    print("TWO-GENERATOR ALPHABET ISOMORPHISM CHECK")
    print("=" * 70)
    print()

    t_start = time.time()

    all_pairs_list = list(combinations(sorted(generators.keys()), 2))
    print(f"Testing {len(all_pairs_list)} two-generator pairs...")
    print()

    # Phase 1: Build all pairs, find which are uncolorable and their minimums
    results = []
    for g1_name, g2_name in all_pairs_list:
        g1 = generators[g1_name]
        g2 = generators[g2_name]

        candidates = [0, 1, -1, g1, -g1, g2, -g2]
        if isinstance(g1, complex) and abs(g1.imag) > 1e-10:
            candidates.extend([g1.conjugate(), -g1.conjugate()])
        if isinstance(g2, complex) and abs(g2.imag) > 1e-10:
            candidates.extend([g2.conjugate(), -g2.conjugate()])
        alphabet = dedup_complex([complex(x) for x in candidates])

        rays = generate_rays_from_alphabet(alphabet)
        pairs, triads, adj = build_pairs_triads(rays)

        if not is_ks_uncolorable(len(rays), triads, pairs):
            results.append({
                'name': f"{g1_name}+{g2_name}",
                'uncol': False,
                'min_size': None,
                'rays': None,
                'min_pairs': None,
                'deg_seq': None,
            })
            print(f"  {g1_name:>8} + {g2_name:<8}: colorable")
            continue

        # Minimize
        min_idx, min_n = greedy_minimize(rays, pairs, triads, n_trials=200)
        min_rays = [rays[i] for i in min_idx]
        s = set(min_idx)
        remap = {old: new for new, old in enumerate(sorted(min_idx))}
        min_pairs = [(remap[a], remap[b]) for a, b in pairs if a in s and b in s]
        min_triads = [(remap[a], remap[b], remap[c]) for a, b, c in triads
                      if a in s and b in s and c in s]

        ds = degree_sequence(min_n, min_pairs)

        results.append({
            'name': f"{g1_name}+{g2_name}",
            'uncol': True,
            'min_size': min_n,
            'n_pairs': len(min_pairs),
            'n_triads': len(min_triads),
            'min_pairs': min_pairs,
            'deg_seq': ds,
        })
        print(f"  {g1_name:>8} + {g2_name:<8}: UNCOL min={min_n}, "
              f"pairs={len(min_pairs)}, triads={len(min_triads)}, "
              f"deg_seq_hash={hash(ds)}")

    # Phase 2: Group by minimum size
    print(f"\n{'='*70}")
    print("GROUPING BY MINIMUM SIZE")
    print(f"{'='*70}")

    uncol = [r for r in results if r['uncol']]
    color = [r for r in results if not r['uncol']]
    print(f"\nUncolorable: {len(uncol)}/28")
    print(f"Colorable: {len(color)}/28 ({', '.join(r['name'] for r in color)})")

    size_groups = {}
    for r in uncol:
        size_groups.setdefault(r['min_size'], []).append(r)

    for size, group in sorted(size_groups.items()):
        print(f"\n  Min = {size}: {len(group)} pairs")
        for r in group:
            print(f"    {r['name']}: {r['n_pairs']} pairs, {r['n_triads']} triads")

    # Phase 3: VF2 isomorphism check within each group
    print(f"\n{'='*70}")
    print("VF2 ISOMORPHISM CHECK")
    print(f"{'='*70}")

    for size, group in sorted(size_groups.items()):
        if len(group) < 2:
            print(f"\n  Min = {size}: only 1 pair, skipping")
            continue

        print(f"\n  Min = {size}: checking {len(group)} pairs for graph isomorphism")

        # First check degree sequences
        deg_seqs = set()
        for r in group:
            deg_seqs.add(r['deg_seq'])
        if len(deg_seqs) == 1:
            print(f"    All {len(group)} have identical degree sequence")
        else:
            print(f"    WARNING: {len(deg_seqs)} distinct degree sequences!")
            for ds in deg_seqs:
                members = [r['name'] for r in group if r['deg_seq'] == ds]
                print(f"      {Counter(ds)}: {', '.join(members)}")

        # VF2 check: compare all pairs against the first
        ref = group[0]
        all_iso = True
        for other in group[1:]:
            iso = try_vf2_isomorphism(ref['min_size'], ref['min_pairs'],
                                       other['min_size'], other['min_pairs'])
            if iso is None:
                print(f"    {ref['name']} vs {other['name']}: networkx not available")
                all_iso = None
            elif iso:
                print(f"    {ref['name']} vs {other['name']}: ISOMORPHIC")
            else:
                print(f"    {ref['name']} vs {other['name']}: NOT isomorphic")
                all_iso = False

        if all_iso is True:
            print(f"    ==> ALL {len(group)} minimal sets at min={size} are GRAPH-ISOMORPHIC")
        elif all_iso is False:
            print(f"    ==> NOT all isomorphic")

    t_total = time.time() - t_start
    print(f"\nTotal time: {t_total:.1f}s")
