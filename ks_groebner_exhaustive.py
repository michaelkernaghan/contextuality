"""
ks_groebner_exhaustive.py -- Exhaustive algebraic proof via isomorphism classes
================================================================================

Strategy:
1. Enumerate ALL KS-uncolorable hypergraphs on n vertices
2. Reduce to isomorphism classes (canonical forms under vertex permutation)
3. Prove ONE representative per class non-realizable via Gröbner basis
4. This constitutes a complete proof that no KS set in R^3 exists with n rays

The isomorphism reduction is critical: ~988K hypergraphs on 6 vertices
collapse to far fewer isomorphism classes.
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

from sympy import symbols, groebner, QQ
from itertools import combinations, permutations
from pysat.solvers import Glucose4
import time


def is_ks_uncolorable(n_vertices, triads):
    if not triads:
        return False
    solver = Glucose4()
    for a, b, c in triads:
        va, vb, vc = a + 1, b + 1, c + 1
        solver.add_clause([va, vb, vc])
        solver.add_clause([-va, -vb])
        solver.add_clause([-va, -vc])
        solver.add_clause([-vb, -vc])
    result = solver.solve()
    solver.delete()
    return not result


def canonical_form(n_verts, triads):
    """Compute canonical form of a hypergraph under vertex permutation.

    Try all permutations of vertices and return the lexicographically
    smallest representation. For small n this is tractable.
    """
    best = None
    for perm in permutations(range(n_verts)):
        relabeled = []
        for a, b, c in triads:
            t = tuple(sorted([perm[a], perm[b], perm[c]]))
            relabeled.append(t)
        relabeled.sort()
        canon = tuple(relabeled)
        if best is None or canon < best:
            best = canon
    return best


def get_edges_from_triads(triads):
    edges = set()
    for a, b, c in triads:
        edges.add((min(a,b), max(a,b)))
        edges.add((min(a,c), max(a,c)))
        edges.add((min(b,c), max(b,c)))
    return sorted(edges)


def groebner_proof(n_verts, triads):
    """Prove non-realizability via Gröbner basis. Returns True if proved."""
    edges = get_edges_from_triads(triads)

    var_names = []
    for i in range(n_verts):
        for k in range(3):
            var_names.append(f'x{i}_{k}')
    X = symbols(var_names)

    def v(i, k):
        return X[i * 3 + k]

    polys = []
    for i, j in edges:
        dot = sum(v(i, k) * v(j, k) for k in range(3))
        polys.append(dot)
    for i in range(n_verts):
        norm_sq = sum(v(i, k)**2 for k in range(3)) - 1
        polys.append(norm_sq)

    try:
        gb = groebner(polys, *X, order='grevlex', domain=QQ)
        gb_polys = list(gb)
        return len(gb_polys) == 1 and gb_polys[0] == 1
    except Exception:
        return False


# =====================================================================
print("=" * 70)
print("EXHAUSTIVE ALGEBRAIC PROOF: No KS set in R^3 with n <= K rays")
print("=" * 70)
print()
print("Method: Enumerate all KS-uncolorable hypergraphs, reduce to")
print("isomorphism classes, prove each class non-realizable via Groebner basis.")
print()

grand_total_classes = 0
grand_total_proved = 0
grand_total_failed = 0

for n_v in [4, 5, 6]:
    print(f"\n{'='*70}")
    print(f"--- {n_v} vertices ---")
    print(f"{'='*70}")

    all_possible_triads = list(combinations(range(n_v), 3))
    n_possible = len(all_possible_triads)
    print(f"  Possible triads: {n_possible}")

    # Collect all KS-uncolorable hypergraphs and their canonical forms
    canon_to_representative = {}
    total_ks = 0

    t0 = time.time()

    for n_t in range(3, n_possible + 1):
        ks_this_level = 0
        new_classes_this_level = 0

        for triad_combo in combinations(all_possible_triads, n_t):
            triads = list(triad_combo)

            if is_ks_uncolorable(n_v, triads):
                total_ks += 1
                ks_this_level += 1

                canon = canonical_form(n_v, triads)
                if canon not in canon_to_representative:
                    canon_to_representative[canon] = triads
                    new_classes_this_level += 1

        if ks_this_level > 0:
            print(f"  {n_t} triads: {ks_this_level} uncolorable, "
                  f"{new_classes_this_level} new iso classes "
                  f"(total classes so far: {len(canon_to_representative)})")

    enum_time = time.time() - t0
    n_classes = len(canon_to_representative)
    print(f"\n  Enumeration complete in {enum_time:.1f}s")
    print(f"  Total KS-uncolorable: {total_ks}")
    print(f"  Isomorphism classes: {n_classes}")
    print(f"  Reduction factor: {total_ks/max(n_classes,1):.1f}x")

    # Now prove each isomorphism class non-realizable
    print(f"\n  Proving {n_classes} isomorphism classes non-realizable...")
    proved = 0
    failed = 0

    for idx, (canon, rep_triads) in enumerate(canon_to_representative.items()):
        t1 = time.time()
        result = groebner_proof(n_v, rep_triads)
        elapsed = time.time() - t1

        if result:
            proved += 1
        else:
            failed += 1
            print(f"    WARNING: Class {idx} NOT proved! Triads: {rep_triads}")

        if (idx + 1) % 10 == 0 or idx == n_classes - 1:
            print(f"    [{idx+1}/{n_classes}] proved={proved} failed={failed} "
                  f"(last: {elapsed:.1f}s)")

    print(f"\n  RESULT for {n_v} vertices:")
    print(f"    Isomorphism classes: {n_classes}")
    print(f"    Proved non-realizable: {proved}")
    if failed > 0:
        print(f"    FAILED to prove: {failed}")
    else:
        print(f"    >>> COMPLETE PROOF: No KS set in R^3 exists with {n_v} rays")

    grand_total_classes += n_classes
    grand_total_proved += proved
    grand_total_failed += failed


# =====================================================================
print(f"\n{'='*70}")
print("PROOF SUMMARY")
print("=" * 70)
print()
print(f"  Total isomorphism classes tested: {grand_total_classes}")
print(f"  Total proved non-realizable: {grand_total_proved}")
if grand_total_failed > 0:
    print(f"  Failed: {grand_total_failed}")
    print(f"\n  INCOMPLETE: Some classes could not be proved")
else:
    print(f"\n  THEOREM (computer-assisted):")
    print(f"  No Kochen-Specker set in R^3 exists with 6 or fewer rays.")
    print(f"  Proof: Exhaustive enumeration of all KS-uncolorable hypergraphs")
    print(f"  on 4-6 vertices yields {grand_total_classes} isomorphism classes.")
    print(f"  For each class, the Groebner basis of the orthogonality +")
    print(f"  normalization polynomial system over Q reduces to {{1}},")
    print(f"  certifying algebraic inconsistency (no solutions over any field).")
    print(f"  QED")

print(f"\n{'='*70}")
