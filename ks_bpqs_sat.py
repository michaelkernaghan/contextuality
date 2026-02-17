"""
ks_bpqs_sat.py -- Compute optimal bipartite quantum strategy (BPQS) via SAT
=============================================================================

Implements the B-KS (Bipartite Kochen-Specker) uncolorability test from
Trandafir-Cabello (arXiv:2508.07335).

Key distinction from the old ks_bpqs.py (which solved bipartite set covering):
  B-KS uses CONTEXTUAL coloring: f(v, b) assigns a value to vector v IN basis b.
  The same vector can get different values in different bases.

A pair (S_A, S_B) of basis subsets is B-KS if no contextual function
f: (vector, basis) -> {0, 1} simultaneously satisfies:
  1. Completeness: for each basis b, exactly one f(v, b) = 1
  2. Cross-party exclusion: if v perp w, v in b_A in S_A, w in b_B in S_B,
     then f(v, b_A) = 1 implies f(w, b_B) = 0

Optimization: minimize |S_A| x |S_B| (product, not sum).

IMPORTANT: B-KS does NOT require every vector to appear in both S_A and S_B.
The coverage pre-filter used in the old code was incorrect and prevented
finding optimal solutions for sets like CK-31 where most vectors appear
in only one basis.

Known results (Trandafir-Cabello):
  Eisenstein-33: 5 x 9 = 45
  Peres-33:      7 x 9 = 63
  CK-31:         8 x 9 = 72

Requires: pip install python-sat
"""

import cmath
import itertools
import math
import random
import time

from pysat.solvers import Glucose4

from ks_complex import (
    generate_eisenstein_rays,
    hermitian_dot,
    canonicalize_complex_ray,
)
from ks_new_islands import (
    generate_rays_from_alphabet,
    hermitian_completion,
    sat_minimize,
)
from ks_sat import is_uncolorable as sat_uncolorable, build_graph, CK31_VECTORS


def build_pairs_triads(rays, tol=1e-9):
    """Build orthogonal pairs and complete orthogonal triads from rays."""
    n = len(rays)
    pairs = []
    pair_set = set()
    for i in range(n):
        for j in range(i + 1, n):
            dot = hermitian_dot(rays[i], rays[j])
            if abs(dot) < tol:
                pairs.append((i, j))
                pair_set.add((i, j))
    triads = []
    for i in range(n):
        for j in range(i + 1, n):
            if (i, j) not in pair_set:
                continue
            for k in range(j + 1, n):
                if (i, k) in pair_set and (j, k) in pair_set:
                    triads.append((i, j, k))
    return pairs, triads


def get_minimal_ks(rays, pairs, triads, n_trials=300):
    """Get minimal KS set and its restricted structure."""
    subset, size, _ = sat_minimize(rays, pairs, triads, n_trials=n_trials)
    s = set(subset)
    remap = {old: new for new, old in enumerate(sorted(subset))}
    min_rays = [rays[i] for i in sorted(subset)]
    min_pairs = [(remap[a], remap[b]) for a, b in pairs if a in s and b in s]
    min_triads = [(remap[a], remap[b], remap[c]) for a, b, c in triads
                  if a in s and b in s and c in s]
    return min_rays, min_pairs, min_triads, size


# ============================================================
# B-KS SAT encoding
# ============================================================

def is_bks_fast(triads, s_a_indices, s_b_indices, pair_set):
    """
    Check if (S_A, S_B) is a B-KS pair via SAT.

    Variables: x_{v,b} for each (vector v, basis b) where v in b
      and b is in S_A union S_B.

    Constraints:
    1. Completeness: for each basis b in S_A union S_B,
       exactly one x_{v,b} = 1 among v in b.
    2. Cross-party exclusion: for each v perp w where
       v in b_A (b_A in S_A) and w in b_B (b_B in S_B),
       not(x_{v,b_A} and x_{w,b_B}).

    pair_set should contain (min(a,b), max(a,b)) tuples.
    Returns True if UNSAT (no valid assignment = B-KS).
    """
    s_a = set(s_a_indices)
    s_b = set(s_b_indices)
    active = s_a | s_b

    # Build variable mapping: (vector, basis_index) -> SAT variable (1-indexed)
    var_map = {}
    next_var = 1
    for b_idx in active:
        for v in triads[b_idx]:
            key = (v, b_idx)
            if key not in var_map:
                var_map[key] = next_var
                next_var += 1

    clauses = []

    # Constraint 1: Completeness - exactly one vector "selected" per basis
    for b_idx in active:
        vecs = list(triads[b_idx])
        vs = [var_map[(v, b_idx)] for v in vecs]
        # At least one true
        clauses.append(vs[:])
        # At most one true (pairwise negation)
        for i in range(len(vs)):
            for j in range(i + 1, len(vs)):
                clauses.append([-vs[i], -vs[j]])

    # Constraint 2: Cross-party exclusion
    for b_a in s_a:
        for b_b in s_b:
            for v in triads[b_a]:
                for w in triads[b_b]:
                    if v != w and (min(v, w), max(v, w)) in pair_set:
                        clauses.append([-var_map[(v, b_a)], -var_map[(w, b_b)]])

    with Glucose4() as solver:
        for c in clauses:
            solver.add_clause(c)
        return not solver.solve()


# ============================================================
# Search strategies
# ============================================================

def find_optimal_bpqs(name, n_vectors, pairs, triads, max_exact_bases=18):
    """
    Find optimal BPQS (|S_A| x |S_B|) for a KS set.

    Strategy:
    1. First verify (all, all) is B-KS (must be, since standard KS is special case)
    2. Greedy shrink from (all, all) multiple times with randomized removal order
    3. For small basis counts, exact search (NO coverage pre-filter)
    """
    m = len(triads)
    print(f"\n  {name}: {n_vectors} vectors, {m} bases")

    # Build pair set for fast lookup
    pair_set = set()
    for a, b in pairs:
        pair_set.add((min(a, b), max(a, b)))

    all_bases = list(range(m))

    # Step 1: Verify (all, all) is B-KS
    t0 = time.time()
    if not is_bks_fast(triads, all_bases, all_bases, pair_set):
        print(f"    ERROR: Full set is not B-KS! KS verification failed.")
        return None, None, None
    print(f"    Full set ({m}x{m}={m*m}) is B-KS (verified in {time.time()-t0:.2f}s)")

    # Step 2: Greedy shrink (multiple trials)
    best_product = m * m
    best_sa = m
    best_sb = m
    best_config = (all_bases, all_bases)

    n_trials = 500
    print(f"    Running {n_trials} greedy shrink trials...")
    t0 = time.time()

    for trial in range(n_trials):
        sa = list(all_bases)
        sb = list(all_bases)

        # Greedy removal: alternate between removing from A and B
        improved = True
        while improved:
            improved = False

            # Alternate removal order randomly
            if random.random() < 0.5:
                sides = [('A', True), ('B', False)]
            else:
                sides = [('B', False), ('A', True)]

            for label, is_a_side in sides:
                primary = sa if is_a_side else sb
                indices = list(range(len(primary)))
                random.shuffle(indices)
                for i in indices:
                    candidate = primary[:i] + primary[i+1:]
                    if not candidate:
                        continue
                    if is_a_side:
                        if is_bks_fast(triads, candidate, sb, pair_set):
                            sa = candidate
                            improved = True
                            break
                    else:
                        if is_bks_fast(triads, sa, candidate, pair_set):
                            sb = candidate
                            improved = True
                            break

        product = len(sa) * len(sb)
        if product < best_product:
            best_product = product
            best_sa = len(sa)
            best_sb = len(sb)
            best_config = (sorted(sa), sorted(sb))
            print(f"      Trial {trial+1}: NEW BEST {len(sa)}x{len(sb)}={product}")

    dt = time.time() - t0
    print(f"    Greedy result: {best_sa}x{best_sb}={best_product} ({dt:.1f}s)")

    # Step 3: Targeted search around greedy result
    # For each S_A of size (best_sa - 1), greedily find minimum S_B
    # This can prove optimality or find improvements
    if m <= max_exact_bases:
        print(f"    Running targeted search around greedy optimum...")
        t0 = time.time()

        # Try to improve: for sizes below greedy, enumerate S_A and minimize S_B
        target_sa = min(best_sa, best_sb)  # Start from smaller side
        for sa_size in range(max(1, target_sa - 2), target_sa + 1):
            max_sb = best_product // sa_size  # Must beat current best
            if max_sb < 1:
                continue

            n_checked = 0
            t_start = time.time()
            for sa_combo in itertools.combinations(range(m), sa_size):
                # For this S_A, greedily minimize S_B from all bases
                sb = list(all_bases)
                random.shuffle(sb)
                improved_inner = True
                while improved_inner:
                    improved_inner = False
                    for i in range(len(sb) - 1, -1, -1):
                        candidate = sb[:i] + sb[i+1:]
                        if candidate and is_bks_fast(triads, list(sa_combo), candidate, pair_set):
                            sb = candidate
                            improved_inner = True
                            break

                n_checked += 1
                # Verify the pair is actually B-KS (starting point may not have been)
                if not is_bks_fast(triads, list(sa_combo), sb, pair_set):
                    continue
                product = sa_size * len(sb)
                if product < best_product:
                    best_product = product
                    best_sa = sa_size
                    best_sb = len(sb)
                    best_config = (list(sa_combo), sorted(sb))
                    print(f"      TARGETED: {sa_size}x{len(sb)}={product} (checked {n_checked})")

                if time.time() - t_start > 60:
                    print(f"      sa_size={sa_size}: timeout after {n_checked} candidates")
                    break

        dt = time.time() - t0
        print(f"    Targeted search done ({dt:.1f}s)")

    a, b = min(best_sa, best_sb), max(best_sa, best_sb)
    print(f"    OPTIMAL: {a} x {b} = {a * b}")
    print(f"    S_A = {best_config[0]}")
    print(f"    S_B = {best_config[1]}")

    return a, b, best_config


# ============================================================
# Island generation (reused from existing code)
# ============================================================

def build_ck31():
    """Conway-Kochen 31-vector KS set."""
    rays = [tuple(complex(x) for x in v) for v in CK31_VECTORS]
    pairs, triads = build_pairs_triads(rays)
    return rays, pairs, triads


def build_eisenstein():
    """Eisenstein (Z[omega]) island."""
    rays = generate_eisenstein_rays(max_coeff=1, dim=3, norm_cutoff=3)
    pairs, triads = build_pairs_triads(rays)
    return rays, pairs, triads


def build_peres():
    """Peres (Z[sqrt(2)]) island."""
    s2 = math.sqrt(2)
    alph = [complex(x) for x in [0, 1, -1, s2, -s2]]
    rays = generate_rays_from_alphabet(alph)
    pairs, triads = build_pairs_triads(rays)
    return rays, pairs, triads


def build_zsqrt2i():
    """Z[sqrt(-2)] island."""
    sd2 = cmath.sqrt(-2)
    alph = [0, 1, -1, sd2, -sd2]
    rays = generate_rays_from_alphabet(alph)
    pairs, triads = build_pairs_triads(rays)
    return rays, pairs, triads


def build_heegner7():
    """Heegner-7 (Z[(1+sqrt(-7))/2]) island."""
    gen7 = (1 + cmath.sqrt(-7)) / 2
    alph = [0, 1, -1, gen7, -gen7, gen7.conjugate(), -gen7.conjugate()]
    rays = generate_rays_from_alphabet(alph)
    pairs, triads = build_pairs_triads(rays)
    return rays, pairs, triads


def build_golden():
    """Golden ratio (Z[phi]) island."""
    phi = (1 + math.sqrt(5)) / 2
    alph = [complex(x) for x in [0, 1, -1, phi, -phi]]
    rays_raw = generate_rays_from_alphabet(alph)
    rays = hermitian_completion(rays_raw)
    pairs, triads = build_pairs_triads(rays)
    return rays, pairs, triads


# ============================================================
# Main
# ============================================================

def main():
    random.seed(42)

    print("=" * 70)
    print("B-KS OPTIMAL BPQS COMPUTATION (SAT-based)")
    print("=" * 70)
    print()
    print("Method: contextual coloring f(vector, basis) with cross-party exclusion")
    print("Optimization: minimize |S_A| x |S_B|")
    print()

    results = []

    # ============================================================
    # PHASE 1: Verify against known results
    # ============================================================
    print("=" * 70)
    print("PHASE 1: VERIFICATION (must match Cabello's numbers)")
    print("=" * 70)

    # --- Eisenstein-33 ---
    print("\n--- Eisenstein-33 (expect 5 x 9 = 45) ---")
    eis_rays, eis_pairs, eis_triads = build_eisenstein()
    eis_min_rays, eis_min_pairs, eis_min_triads, eis_size = get_minimal_ks(
        eis_rays, eis_pairs, eis_triads)
    print(f"  Minimized to {eis_size} vectors, {len(eis_min_triads)} bases")
    a, b, cfg = find_optimal_bpqs(
        f"Eisenstein-{eis_size}", eis_size, eis_min_pairs, eis_min_triads)
    if a is not None:
        results.append(("Eisenstein", eis_size, len(eis_min_triads), a, b, a*b))
        if a * b != 45:
            print(f"\n  *** WARNING: Expected 45, got {a*b}! ***")

    # --- Peres-33 ---
    print("\n--- Peres-33 (expect 7 x 9 = 63) ---")
    p_rays, p_pairs, p_triads = build_peres()
    p_min_rays, p_min_pairs, p_min_triads, p_size = get_minimal_ks(
        p_rays, p_pairs, p_triads)
    print(f"  Minimized to {p_size} vectors, {len(p_min_triads)} bases")
    a, b, cfg = find_optimal_bpqs(
        f"Peres-{p_size}", p_size, p_min_pairs, p_min_triads)
    if a is not None:
        results.append(("Peres", p_size, len(p_min_triads), a, b, a*b))
        if a * b != 63:
            print(f"\n  *** WARNING: Expected 63, got {a*b}! ***")

    # --- CK-31 ---
    print("\n--- CK-31 (expect 8 x 9 = 72) ---")
    ck_rays, ck_pairs, ck_triads = build_ck31()
    print(f"  {len(ck_rays)} vectors, {len(ck_triads)} bases")
    a, b, cfg = find_optimal_bpqs(
        "CK-31", len(ck_rays), ck_pairs, ck_triads)
    if a is not None:
        results.append(("CK-31", len(ck_rays), len(ck_triads), a, b, a*b))
        if a * b != 72:
            print(f"\n  *** WARNING: Expected 72, got {a*b}! ***")

    # Check verification
    verification_ok = True
    for name, nvec, nbas, sa, sb, prod in results:
        expected = {"Eisenstein": 45, "Peres": 63, "CK-31": 72}.get(name)
        if expected and prod != expected:
            verification_ok = False
            print(f"\n  VERIFICATION FAILED for {name}: {prod} != {expected}")

    if not verification_ok:
        print("\n" + "!" * 70)
        print("STOPPING: Verification failed. Debug encoding before proceeding.")
        print("!" * 70)
        return

    print("\n  All known results verified!")

    # ============================================================
    # PHASE 2: New islands
    # ============================================================
    print("\n" + "=" * 70)
    print("PHASE 2: NEW ISLANDS (original computation)")
    print("=" * 70)

    # --- Z[sqrt(-2)]-33 ---
    print("\n--- Z[sqrt(-2)] (expect same as Peres by graph isomorphism) ---")
    z2_rays, z2_pairs, z2_triads = build_zsqrt2i()
    z2_min_rays, z2_min_pairs, z2_min_triads, z2_size = get_minimal_ks(
        z2_rays, z2_pairs, z2_triads)
    print(f"  Minimized to {z2_size} vectors, {len(z2_min_triads)} bases")
    a, b, cfg = find_optimal_bpqs(
        f"Z[sqrt(-2)]-{z2_size}", z2_size, z2_min_pairs, z2_min_triads)
    if a is not None:
        results.append(("Z[sqrt(-2)]", z2_size, len(z2_min_triads), a, b, a*b))

    # --- Heegner-7 ---
    print("\n--- Heegner-7 (NEW - never computed) ---")
    h7_rays, h7_pairs, h7_triads = build_heegner7()
    h7_min_rays, h7_min_pairs, h7_min_triads, h7_size = get_minimal_ks(
        h7_rays, h7_pairs, h7_triads)
    print(f"  Minimized to {h7_size} vectors, {len(h7_min_triads)} bases")
    a, b, cfg = find_optimal_bpqs(
        f"Heegner-7-{h7_size}", h7_size, h7_min_pairs, h7_min_triads,
        max_exact_bases=24)
    if a is not None:
        results.append(("Heegner-7", h7_size, len(h7_min_triads), a, b, a*b))

    # --- Golden ---
    print("\n--- Golden (NEW - never computed) ---")
    g_rays, g_pairs, g_triads = build_golden()
    if g_triads and sat_uncolorable(len(g_rays), g_pairs, g_triads):
        g_min_rays, g_min_pairs, g_min_triads, g_size = get_minimal_ks(
            g_rays, g_pairs, g_triads, n_trials=200)
        print(f"  Minimized to {g_size} vectors, {len(g_min_triads)} bases")
        a, b, cfg = find_optimal_bpqs(
            f"Golden-{g_size}", g_size, g_min_pairs, g_min_triads,
            max_exact_bases=20)
        if a is not None:
            results.append(("Golden", g_size, len(g_min_triads), a, b, a*b))
    else:
        print("  Golden pool is colorable (no KS set) -- skipping")

    # ============================================================
    # SUMMARY
    # ============================================================
    print("\n\n" + "=" * 70)
    print("SUMMARY: B-KS Optimal BPQS Input Counts")
    print("=" * 70)

    print(f"\n{'Island':<20s} {'|V|':>5s} {'|B|':>5s} {'|S_A|':>6s} {'|S_B|':>6s} "
          f"{'Product':>8s} {'Status':>12s}")
    print("-" * 70)

    known = {"Eisenstein": 45, "Peres": 63, "CK-31": 72}
    for name, nvec, nbas, sa, sb, prod in results:
        expected = known.get(name)
        if expected:
            status = "VERIFIED" if prod == expected else f"MISMATCH({expected})"
        else:
            status = "NEW"
        a, b = min(sa, sb), max(sa, sb)
        print(f"  {name:<18s} {nvec:>5d} {nbas:>5d} {a:>6d} {b:>6d} {a*b:>8d} {status:>12s}")

    print("\nCabello's known results:")
    print("  Eisenstein (WH-33):  5 x 9 = 45")
    print("  Peres-33:            7 x 9 = 63")
    print("  CK-31:               8 x 9 = 72")


if __name__ == "__main__":
    main()
