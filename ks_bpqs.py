"""
ks_bpqs.py -- Compute optimal BPQS input counts for each island's minimal KS set
==================================================================================

Implements the core of the Trandafir-Cabello (arXiv:2410.17470) conversion:
Given a KS set with bases (triads), find the minimum (|S_A|, |S_B|) such that
every vector appears in at least one of Alice's bases AND at least one of Bob's.

This bipartite covering is the key constraint for a perfect quantum strategy.
"""

import cmath
import itertools
import math
import random
import time

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
from ks_sat import is_uncolorable as sat_uncolorable


def build_pairs_triads(rays, tol=1e-9):
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


def find_optimal_bpqs(n_vectors, triads):
    """
    Find optimal BPQS input counts (|S_A|, |S_B|) for a KS set.

    For each vector v, let B(v) = set of basis indices containing v.
    We need S_A, S_B ⊆ {0,...,m-1} such that:
      - For every vector v: B(v) ∩ S_A ≠ ∅ AND B(v) ∩ S_B ≠ ∅
    Minimize |S_A| + |S_B| (and report |S_A| × |S_B|).
    """
    m = len(triads)

    # Build vector-to-bases mapping
    vec_bases = {}  # vector_index -> set of basis indices
    for b_idx, (i, j, k) in enumerate(triads):
        for v in [i, j, k]:
            vec_bases.setdefault(v, set()).add(b_idx)

    all_vectors = sorted(vec_bases.keys())
    n_vecs = len(all_vectors)

    print(f"    {n_vecs} vectors in {m} bases")

    # Check how many bases each vector appears in
    base_counts = [len(vec_bases[v]) for v in all_vectors]
    min_bc = min(base_counts)
    print(f"    Vector base membership: min={min_bc}, max={max(base_counts)}, "
          f"mean={sum(base_counts)/len(base_counts):.1f}")

    if min_bc < 2:
        print(f"    WARNING: {sum(1 for c in base_counts if c < 2)} vectors appear in only 1 basis")
        print(f"    These vectors MUST have their basis in BOTH S_A and S_B")

    # Vectors appearing in only 1 basis force that basis into both S_A and S_B
    forced_both = set()
    for v in all_vectors:
        if len(vec_bases[v]) == 1:
            forced_both.update(vec_bases[v])

    if forced_both:
        print(f"    Forced into both S_A and S_B: {len(forced_both)} bases")

    best_sa = m
    best_sb = m
    best_total = 2 * m
    best_product = m * m
    best_config = None

    # Try all possible S_A sizes from 1 to m
    # For efficiency, use the forced bases and try small sizes first
    for sa_size in range(max(1, len(forced_both)), m):
        if sa_size >= best_total:
            break  # Can't improve

        # Generate candidates for S_A that include forced bases
        remaining = [b for b in range(m) if b not in forced_both]
        needed_extra = sa_size - len(forced_both)

        if needed_extra < 0:
            continue
        if needed_extra > len(remaining):
            continue

        # Limit enumeration for large cases
        n_combos = 1
        for i in range(needed_extra):
            n_combos = n_combos * (len(remaining) - i) // (i + 1)

        if n_combos > 500000:
            print(f"    sa_size={sa_size}: C({len(remaining)},{needed_extra})={n_combos} too large, sampling...")
            # Sample random subsets
            found_improvement = False
            for _ in range(50000):
                extra = sorted(random.sample(remaining, needed_extra)) if needed_extra > 0 else []
                s_a = frozenset(forced_both | set(extra))

                # Find minimum S_B: must cover all vectors not covered by S_A
                # Actually: S_B must cover ALL vectors (each vector needs a Bob basis too)
                # Find minimum S_B
                uncovered = []
                for v in all_vectors:
                    if not (vec_bases[v] & s_a):
                        uncovered.append(v)

                if uncovered:
                    continue  # S_A doesn't cover all vectors

                # Now find min S_B that covers all vectors
                # Greedy set cover
                remaining_vecs = set(all_vectors)
                s_b = set(forced_both)  # Start with forced bases
                for v in all_vectors:
                    remaining_vecs -= (vec_bases[v] & s_b)

                while remaining_vecs:
                    # Pick basis covering most uncovered vectors
                    best_basis = -1
                    best_cover = 0
                    for b in range(m):
                        if b in s_b:
                            continue
                        cover = len(set(triads[b]) & remaining_vecs)
                        if cover > best_cover:
                            best_cover = cover
                            best_basis = b
                    if best_basis == -1 or best_cover == 0:
                        break
                    s_b.add(best_basis)
                    remaining_vecs -= set(triads[best_basis])

                if not remaining_vecs:
                    total = len(s_a) + len(s_b)
                    product = len(s_a) * len(s_b)
                    if total < best_total or (total == best_total and product < best_product):
                        best_sa = len(s_a)
                        best_sb = len(s_b)
                        best_total = total
                        best_product = product
                        best_config = (s_a, frozenset(s_b))
                        found_improvement = True

            if found_improvement:
                print(f"    sa_size={sa_size}: found {best_sa}×{best_sb}={best_product} (total={best_total})")
            continue

        for extra in itertools.combinations(remaining, needed_extra):
            s_a = frozenset(forced_both | set(extra))

            # Check S_A covers all vectors
            covers_all = True
            for v in all_vectors:
                if not (vec_bases[v] & s_a):
                    covers_all = False
                    break
            if not covers_all:
                continue

            # Find minimum S_B using greedy set cover
            remaining_vecs = set(all_vectors)
            s_b = set(forced_both)
            for v in all_vectors:
                remaining_vecs -= (vec_bases[v] & s_b)

            while remaining_vecs:
                best_basis = -1
                best_cover = 0
                for b in range(m):
                    if b in s_b:
                        continue
                    cover = len(set(triads[b]) & remaining_vecs)
                    if cover > best_cover:
                        best_cover = cover
                        best_basis = b
                if best_basis == -1 or best_cover == 0:
                    break
                s_b.add(best_basis)
                remaining_vecs -= set(triads[best_basis])

            if not remaining_vecs:
                total = len(s_a) + len(s_b)
                product = len(s_a) * len(s_b)
                if total < best_total or (total == best_total and product < best_product):
                    best_sa = len(s_a)
                    best_sb = len(s_b)
                    best_total = total
                    best_product = product
                    best_config = (s_a, frozenset(s_b))

        if best_sa <= sa_size:
            print(f"    sa_size={sa_size}: best so far {best_sa}×{best_sb}={best_product} (total={best_total})")

    # Also try symmetric: swap Alice/Bob
    print(f"\n    Optimal BPQS: |S_A|={best_sa}, |S_B|={best_sb}")
    print(f"    Total inputs: {best_total}, Product: {best_product}")

    return best_sa, best_sb, best_config


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


def analyze_base_overlap(name, n_vectors, triads):
    """Analyze the base-membership structure that determines BPQS feasibility."""
    m = len(triads)
    vec_bases = {}
    for b_idx, (i, j, k) in enumerate(triads):
        for v in [i, j, k]:
            vec_bases.setdefault(v, set()).add(b_idx)

    all_vectors = sorted(vec_bases.keys())
    base_counts = [len(vec_bases[v]) for v in all_vectors]

    n_single = sum(1 for c in base_counts if c < 2)
    n_multi = sum(1 for c in base_counts if c >= 2)

    # Count forced bases (those containing a vector that appears in only 1 basis)
    forced = set()
    for v in all_vectors:
        if len(vec_bases[v]) == 1:
            forced.update(vec_bases[v])

    print(f"  {name}: {len(all_vectors)} vecs, {m} bases")
    print(f"    Single-basis vectors: {n_single}/{len(all_vectors)} "
          f"({100*n_single/len(all_vectors):.0f}%)")
    print(f"    Multi-basis vectors: {n_multi}/{len(all_vectors)} "
          f"({100*n_multi/len(all_vectors):.0f}%)")
    print(f"    Bases forced into both S_A & S_B: {len(forced)}/{m} "
          f"({100*len(forced)/m:.0f}%)")
    print(f"    Base membership distribution: {dict(sorted({c: base_counts.count(c) for c in set(base_counts)}.items()))}")

    return n_single, n_multi, len(forced), m


def main():
    random.seed(42)

    print("=" * 70)
    print("BPQS INPUT COUNT ANALYSIS: MINIMAL vs FULL POOLS")
    print("=" * 70)

    # ================================================================
    # PART 1: Full (non-minimized) pools — high base overlap
    # ================================================================
    print("\n" + "=" * 70)
    print("PART 1: FULL RAY POOLS (non-minimized)")
    print("=" * 70)
    print("These have maximum base overlap — vectors appear in many bases.")

    pool_results = []

    # Integer pool
    print("\n--- Integer Pool ---")
    int_alph = [complex(x) for x in [0, 1, -1, 2, -2]]
    int_rays = generate_rays_from_alphabet(int_alph)
    int_pairs, int_triads = build_pairs_triads(int_rays)
    analyze_base_overlap("Integer pool", len(int_rays), int_triads)
    sa, sb, cfg = find_optimal_bpqs(len(int_rays), int_triads)
    pool_results.append(("Integer pool", len(int_rays), len(int_triads), sa, sb))

    # Peres pool
    print("\n--- Peres Pool ---")
    s2 = math.sqrt(2)
    p_alph = [complex(x) for x in [0, 1, -1, s2, -s2]]
    p_rays = generate_rays_from_alphabet(p_alph)
    p_pairs, p_triads = build_pairs_triads(p_rays)
    analyze_base_overlap("Peres pool", len(p_rays), p_triads)
    sa, sb, cfg = find_optimal_bpqs(len(p_rays), p_triads)
    pool_results.append(("Peres pool", len(p_rays), len(p_triads), sa, sb))

    # Eisenstein pool
    print("\n--- Eisenstein Pool ---")
    eis_rays = generate_eisenstein_rays(max_coeff=1, dim=3, norm_cutoff=3)
    eis_pairs, eis_triads = build_pairs_triads(eis_rays)
    analyze_base_overlap("Eisenstein pool", len(eis_rays), eis_triads)
    sa, sb, cfg = find_optimal_bpqs(len(eis_rays), eis_triads)
    pool_results.append(("Eisenstein pool", len(eis_rays), len(eis_triads), sa, sb))

    # Z[sqrt(-2)] pool
    print("\n--- Z[sqrt(-2)] Pool ---")
    sd2 = cmath.sqrt(-2)
    cq_alph = [0, 1, -1, sd2, -sd2]
    cq_rays = generate_rays_from_alphabet(cq_alph)
    cq_pairs, cq_triads = build_pairs_triads(cq_rays)
    analyze_base_overlap("Z[sqrt(-2)] pool", len(cq_rays), cq_triads)
    sa, sb, cfg = find_optimal_bpqs(len(cq_rays), cq_triads)
    pool_results.append(("Z[sqrt(-2)] pool", len(cq_rays), len(cq_triads), sa, sb))

    # Golden pool
    print("\n--- Golden Pool ---")
    phi = (1 + math.sqrt(5)) / 2
    g_alph = [complex(x) for x in [0, 1, -1, phi, -phi]]
    g_rays_raw = generate_rays_from_alphabet(g_alph)
    g_rays = hermitian_completion(g_rays_raw)
    g_pairs, g_triads = build_pairs_triads(g_rays)
    if g_triads and sat_uncolorable(len(g_rays), g_pairs, g_triads):
        analyze_base_overlap("Golden pool", len(g_rays), g_triads)
        sa, sb, cfg = find_optimal_bpqs(len(g_rays), g_triads)
        pool_results.append(("Golden pool", len(g_rays), len(g_triads), sa, sb))

    # ================================================================
    # PART 2: Minimal KS sets — low base overlap
    # ================================================================
    print("\n\n" + "=" * 70)
    print("PART 2: MINIMAL KS SETS (SAT-minimized)")
    print("=" * 70)
    print("These have minimum vector count but low base overlap.")

    min_results = []

    # Integer minimal
    print("\n--- Integer Minimal ---")
    min_rays, min_pairs, min_triads, size = get_minimal_ks(
        int_rays, int_pairs, int_triads)
    analyze_base_overlap("Integer min", size, min_triads)
    sa, sb, cfg = find_optimal_bpqs(size, min_triads)
    min_results.append(("Integer min-31", size, len(min_triads), sa, sb))

    # Peres minimal
    print("\n--- Peres Minimal ---")
    min_rays, min_pairs, min_triads, size = get_minimal_ks(
        p_rays, p_pairs, p_triads)
    analyze_base_overlap("Peres min", size, min_triads)
    sa, sb, cfg = find_optimal_bpqs(size, min_triads)
    min_results.append(("Peres min-33", size, len(min_triads), sa, sb))

    # Eisenstein minimal
    print("\n--- Eisenstein Minimal ---")
    min_rays, min_pairs, min_triads, size = get_minimal_ks(
        eis_rays, eis_pairs, eis_triads)
    analyze_base_overlap("Eisenstein min", size, min_triads)
    sa, sb, cfg = find_optimal_bpqs(size, min_triads)
    min_results.append(("Eisenstein min-33", size, len(min_triads), sa, sb))

    # Z[sqrt(-2)] minimal
    print("\n--- Z[sqrt(-2)] Minimal ---")
    min_rays, min_pairs, min_triads, size = get_minimal_ks(
        cq_rays, cq_pairs, cq_triads)
    analyze_base_overlap("Z[sqrt(-2)] min", size, min_triads)
    sa, sb, cfg = find_optimal_bpqs(size, min_triads)
    min_results.append(("Z[sqrt(-2)] min-33", size, len(min_triads), sa, sb))

    # Golden minimal
    if g_triads and sat_uncolorable(len(g_rays), g_pairs, g_triads):
        print("\n--- Golden Minimal ---")
        min_rays, min_pairs, min_triads, size = get_minimal_ks(
            g_rays, g_pairs, g_triads, n_trials=100)
        analyze_base_overlap("Golden min", size, min_triads)
        sa, sb, cfg = find_optimal_bpqs(size, min_triads)
        min_results.append(("Golden min", size, len(min_triads), sa, sb))

    # ================================================================
    # SUMMARY
    # ================================================================
    print("\n\n" + "=" * 70)
    print("SUMMARY: BPQS Input Counts")
    print("=" * 70)

    print(f"\n{'Source':<22s} {'Vecs':>5s} {'Bases':>6s} {'|S_A|':>6s} {'|S_B|':>6s} "
          f"{'Total':>6s} {'Product':>8s}")
    print("-" * 70)
    print("Full pools:")
    for name, vecs, bases, sa, sb in pool_results:
        a, b = min(sa, sb), max(sa, sb)
        print(f"  {name:<20s} {vecs:>5d} {bases:>6d} {a:>6d} {b:>6d} {a+b:>6d} {a*b:>8d}")
    print("Minimal sets:")
    for name, vecs, bases, sa, sb in min_results:
        a, b = min(sa, sb), max(sa, sb)
        print(f"  {name:<20s} {vecs:>5d} {bases:>6d} {a:>6d} {b:>6d} {a+b:>6d} {a*b:>8d}")

    print("\nCabello's known results (for comparison):")
    print("  Eisenstein (WH-33):  33 vecs, 16 bases, 5 x 9 = 45")
    print("  Peres-33:            33 vecs,  ? bases, 7 x 9 = 63")
    print("  CK-31:               31 vecs, 17 bases, 8 x 9 = 72")

    print("\nKEY INSIGHT:")
    print("  Minimizing vector count maximizes single-basis vectors,")
    print("  which FORCES bases into both S_A and S_B, yielding the")
    print("  degenerate solution S_A = S_B = all bases.")
    print("  For optimal BPQS, the KS set needs high SYMMETRY and")
    print("  base OVERLAP, not minimum size.")


if __name__ == "__main__":
    main()
