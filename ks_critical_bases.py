"""
ks_critical_bases.py -- Critical bases analysis of KS sets
==========================================================

For each island's minimal KS set, determine:
1. Which individual bases are essential (removal breaks uncolorability)
2. The critical number: minimum bases to remove to make it colorable
3. The contextual fraction: critical_number / total_bases

This measures how "tightly woven" the KS proof is -- distinct from both
cardinality (number of rays) and CSW advantage (quantum/classical ratio).

A set with critical number 1 is fragile: removing any single essential basis
destroys the proof. A set with high critical number is robust: you must
remove many constraints before a coloring becomes possible.
"""

import cmath
import math
import random
import time
from itertools import combinations

from ks_complex import (
    generate_eisenstein_rays,
    hermitian_dot,
    canonicalize_complex_ray,
)

from ks_new_islands import (
    generate_rays_from_alphabet,
    sat_minimize,
)

from ks_sat import is_uncolorable as sat_uncolorable, CK31_VECTORS, build_graph


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


# ============================================================
# Core analysis: uncolorability with bases removed
# ============================================================

def is_uncolorable_without_bases(n, pairs, triads, removed_indices):
    """
    Check if the KS set remains uncolorable when certain bases (triads)
    are removed as constraints.

    Removing a basis means its "exactly one green" constraint no longer applies.
    The orthogonality constraints (at most one green per pair) remain --
    orthogonality is a geometric fact, not a contextual choice.

    However, triads whose constraint is removed no longer force
    "at least one green", which is the key weakening.
    """
    removed = set(removed_indices)
    active_triads = [t for i, t in enumerate(triads) if i not in removed]

    if not active_triads:
        return False  # No constraints left, trivially colorable

    # Pairs from active triads only -- if a pair only appears in removed
    # triads, the "at most one green" still holds (geometric), but
    # we need at least the triad constraints for uncolorability
    return sat_uncolorable(n, pairs, active_triads)


def find_essential_bases(n, pairs, triads):
    """
    Find bases whose individual removal makes the set colorable.
    Returns (essential_indices, removable_indices).
    """
    essential = []
    removable = []
    for i in range(len(triads)):
        if not is_uncolorable_without_bases(n, pairs, triads, {i}):
            essential.append(i)
        else:
            removable.append(i)
    return essential, removable


def find_critical_number(n, pairs, triads, max_k=None):
    """
    Find the minimum number of bases whose removal makes the set colorable.

    Strategy: test k=1, k=2, ... until we find a k-subset of bases
    whose removal breaks uncolorability.

    For efficiency, if single-basis removals exist (critical number = 1),
    we find them all. Otherwise we search upward.

    Returns (critical_number, example_removal_set, all_results_by_k).
    """
    n_triads = len(triads)
    if max_k is None:
        max_k = min(n_triads, 10)  # Cap search at 10

    results = {}

    for k in range(1, max_k + 1):
        n_combos = 1
        for i in range(k):
            n_combos = n_combos * (n_triads - i) // (i + 1)

        t0 = time.time()

        if n_combos > 500000:
            # Too many combinations -- use sampling
            print(f"    k={k}: {n_combos} combinations (sampling 50000)...")
            found = False
            example = None
            tested = 0
            for _ in range(50000):
                subset = tuple(sorted(random.sample(range(n_triads), k)))
                tested += 1
                if not is_uncolorable_without_bases(n, pairs, triads, set(subset)):
                    found = True
                    example = subset
                    break
            dt = time.time() - t0
            results[k] = {
                'tested': tested, 'total': n_combos,
                'found': found, 'example': example, 'time': dt,
                'exhaustive': False
            }
            if found:
                return k, example, results
        else:
            # Exhaustive search
            print(f"    k={k}: {n_combos} combinations (exhaustive)...")
            found_count = 0
            first_example = None
            tested = 0
            for combo in combinations(range(n_triads), k):
                tested += 1
                if not is_uncolorable_without_bases(n, pairs, triads, set(combo)):
                    found_count += 1
                    if first_example is None:
                        first_example = combo
                    if k == 1:
                        continue  # Count all essential bases at k=1
                    else:
                        break  # For k>1, finding one is enough
            dt = time.time() - t0
            results[k] = {
                'tested': tested, 'total': n_combos,
                'found': found_count > 0, 'count': found_count,
                'example': first_example, 'time': dt,
                'exhaustive': True
            }
            if found_count > 0:
                return k, first_example, results

    return None, None, results  # Not found within max_k


def analyze_critical_structure(n, pairs, triads, essential_indices):
    """
    For islands where critical number > 1, analyze which PAIRS of
    removable bases break uncolorability together.

    Returns the "critical pairs" -- minimal 2-element removal sets.
    """
    removable = [i for i in range(len(triads)) if i not in set(essential_indices)]
    critical_pairs = []

    for i, j in combinations(removable, 2):
        if not is_uncolorable_without_bases(n, pairs, triads, {i, j}):
            critical_pairs.append((i, j))

    return critical_pairs


def ray_participation(triads, n_rays):
    """Count how many bases each ray participates in."""
    counts = [0] * n_rays
    for a, b, c in triads:
        counts[a] += 1
        counts[b] += 1
        counts[c] += 1
    return counts


# ============================================================
# Build all islands
# ============================================================

def build_integer_island():
    """CK-31 integer island."""
    pairs, triads = build_graph(CK31_VECTORS)
    rays = [tuple(complex(x) for x in v) for v in CK31_VECTORS]
    return rays, pairs, triads, "Integer (CK-31)", 31


def build_peres_island():
    s2 = math.sqrt(2)
    alph = [complex(x) for x in [0, 1, -1, s2, -s2]]
    rays = generate_rays_from_alphabet(alph)
    pairs, triads = build_pairs_triads(rays)
    return rays, pairs, triads, "Peres", None


def build_eisenstein_island():
    rays = generate_eisenstein_rays(max_coeff=1, dim=3, norm_cutoff=3)
    pairs, triads = build_pairs_triads(rays)
    return rays, pairs, triads, "Eisenstein", None


def build_sqrt_neg2_island():
    sd2 = cmath.sqrt(-2)
    alph = [0, 1, -1, sd2, -sd2]
    rays = generate_rays_from_alphabet(alph)
    pairs, triads = build_pairs_triads(rays)
    return rays, pairs, triads, "Z[sqrt(-2)]", None


def build_heegner7_island():
    gen7 = (1 + cmath.sqrt(-7)) / 2
    alph = [0, 1, -1, gen7, -gen7, gen7.conjugate(), -gen7.conjugate()]
    rays = generate_rays_from_alphabet(alph)
    pairs, triads = build_pairs_triads(rays)
    return rays, pairs, triads, "Heegner-7", None


def get_minimal_ks(rays, pairs, triads, known_min=None):
    """Get a minimal KS set and rebuild its pairs/triads."""
    subset, size, _ = sat_minimize(rays, pairs, triads, n_trials=300)
    s = set(subset)
    remap = {old: new for new, old in enumerate(sorted(subset))}
    min_rays = [rays[i] for i in sorted(subset)]
    min_pairs = [(remap[a], remap[b]) for a, b in pairs if a in s and b in s]
    min_triads = [(remap[a], remap[b], remap[c]) for a, b, c in triads
                  if a in s and b in s and c in s]
    return min_rays, min_pairs, min_triads, size


# ============================================================
# Main analysis
# ============================================================

def analyze_island(name, n, pairs, triads, detail=True):
    """Run the full critical bases analysis on one island."""
    print(f"\n{'-' * 60}")
    print(f"  {name}: {n} rays, {len(pairs)} pairs, {len(triads)} bases")
    print(f"{'-' * 60}")

    # Verify uncolorable
    assert sat_uncolorable(n, pairs, triads), f"{name} is NOT uncolorable!"

    # Phase 1: Essential bases (single removal)
    t0 = time.time()
    essential, removable = find_essential_bases(n, pairs, triads)
    dt = time.time() - t0
    print(f"\n  Phase 1: Single-basis essentiality ({dt:.1f}s)")
    print(f"    Essential bases: {len(essential)}/{len(triads)}")
    print(f"    Removable bases: {len(removable)}/{len(triads)}")
    print(f"    Essentiality ratio: {len(essential)/len(triads):.3f}")

    if detail and essential:
        print(f"    Essential basis indices: {essential[:20]}{'...' if len(essential) > 20 else ''}")

    # Phase 2: Critical number
    t0 = time.time()
    critical_k, example, k_results = find_critical_number(n, pairs, triads)
    dt = time.time() - t0
    print(f"\n  Phase 2: Critical number ({dt:.1f}s)")

    if critical_k is not None:
        print(f"    Critical number: {critical_k}")
        print(f"    Contextual fraction: {critical_k}/{len(triads)} = {critical_k/len(triads):.4f}")
        if example:
            print(f"    Example removal: bases {example}")
            if detail:
                for idx in example:
                    a, b, c = triads[idx]
                    print(f"      Basis {idx}: rays ({a}, {b}, {c})")
    else:
        print(f"    Critical number: > {max(k_results.keys())} (not found)")

    for k, info in sorted(k_results.items()):
        exh = "exhaustive" if info.get('exhaustive') else f"sampled {info['tested']}"
        if info.get('count') is not None:
            print(f"    k={k}: {info.get('count', 0)} critical sets ({exh}, {info['time']:.1f}s)")
        else:
            found = "FOUND" if info['found'] else "none found"
            print(f"    k={k}: {found} ({exh}, {info['time']:.1f}s)")

    # Phase 3: Ray participation in essential vs removable bases
    print(f"\n  Phase 3: Structural analysis")
    participation = ray_participation(triads, n)
    ess_participation = [0] * n
    for idx in essential:
        a, b, c = triads[idx]
        ess_participation[a] += 1
        ess_participation[b] += 1
        ess_participation[c] += 1

    rem_participation = [0] * n
    for idx in removable:
        a, b, c = triads[idx]
        rem_participation[a] += 1
        rem_participation[b] += 1
        rem_participation[c] += 1

    avg_total = sum(participation) / n
    avg_ess = sum(ess_participation) / n if essential else 0
    print(f"    Avg bases per ray: {avg_total:.2f}")
    print(f"    Avg essential bases per ray: {avg_ess:.2f}")
    print(f"    Max bases per ray: {max(participation)}")
    print(f"    Min bases per ray: {min(participation)}")

    # Rays that only appear in essential bases
    pure_essential_rays = [i for i in range(n) if rem_participation[i] == 0 and participation[i] > 0]
    print(f"    Rays in essential bases only: {len(pure_essential_rays)}/{n}")

    # Phase 4: If critical number > 1, analyze critical pairs
    if critical_k and critical_k > 1 and len(removable) <= 50:
        t0 = time.time()
        crit_pairs = analyze_critical_structure(n, pairs, triads, essential)
        dt = time.time() - t0
        print(f"\n  Phase 4: Critical pair analysis ({dt:.1f}s)")
        print(f"    Removable bases: {len(removable)}")
        print(f"    Critical pairs: {len(crit_pairs)} / {len(removable)*(len(removable)-1)//2} pairs")
        if crit_pairs:
            print(f"    Critical pair density: {len(crit_pairs) / max(1, len(removable)*(len(removable)-1)//2):.3f}")

    return {
        'name': name,
        'n_rays': n,
        'n_bases': len(triads),
        'n_essential': len(essential),
        'n_removable': len(removable),
        'critical_k': critical_k,
        'essentiality_ratio': len(essential) / len(triads) if triads else 0,
        'contextual_fraction': critical_k / len(triads) if (critical_k and triads) else None,
    }


def main():
    random.seed(42)

    print("=" * 70)
    print("CRITICAL BASES ANALYSIS OF KOCHEN-SPECKER SETS")
    print("=" * 70)
    print("\nFor each island's minimal KS set, we ask:")
    print("  1. Which bases are individually essential?")
    print("  2. What is the minimum removal that breaks uncolorability?")
    print("  3. How does this 'contextual tightness' vary across islands?")

    all_results = []

    # ================================================================
    # Integer island (CK-31) -- already minimal
    # ================================================================
    print("\n\n" + "=" * 70)
    print("ISLAND 1: INTEGER (CK-31)")
    print("=" * 70)

    int_rays, int_pairs, int_triads, _, _ = build_integer_island()
    result = analyze_island("CK-31 (31 rays)", len(int_rays), int_pairs, int_triads)
    all_results.append(result)

    # ================================================================
    # Peres island -- minimize first
    # ================================================================
    print("\n\n" + "=" * 70)
    print("ISLAND 2: PERES")
    print("=" * 70)

    p_rays, p_pairs, p_triads, _, _ = build_peres_island()
    print(f"  Pool: {len(p_rays)} rays, {len(p_triads)} bases")
    p_min_rays, p_min_pairs, p_min_triads, p_size = get_minimal_ks(p_rays, p_pairs, p_triads)
    print(f"  Minimized: {p_size} rays, {len(p_min_triads)} bases")
    result = analyze_island(f"Peres min-{p_size}", p_size, p_min_pairs, p_min_triads)
    all_results.append(result)

    # Also analyze full pool
    print(f"\n  --- Full Peres pool for comparison ---")
    result_full = analyze_island(f"Peres pool ({len(p_rays)})", len(p_rays), p_pairs, p_triads, detail=False)
    all_results.append(result_full)

    # ================================================================
    # Eisenstein island
    # ================================================================
    print("\n\n" + "=" * 70)
    print("ISLAND 3: EISENSTEIN")
    print("=" * 70)

    e_rays, e_pairs, e_triads, _, _ = build_eisenstein_island()
    print(f"  Pool: {len(e_rays)} rays, {len(e_triads)} bases")
    e_min_rays, e_min_pairs, e_min_triads, e_size = get_minimal_ks(e_rays, e_pairs, e_triads)
    print(f"  Minimized: {e_size} rays, {len(e_min_triads)} bases")
    result = analyze_island(f"Eisenstein min-{e_size}", e_size, e_min_pairs, e_min_triads)
    all_results.append(result)

    # ================================================================
    # Z[sqrt(-2)] island
    # ================================================================
    print("\n\n" + "=" * 70)
    print("ISLAND 4: Z[sqrt(-2)]")
    print("=" * 70)

    cq_rays, cq_pairs, cq_triads, _, _ = build_sqrt_neg2_island()
    print(f"  Pool: {len(cq_rays)} rays, {len(cq_triads)} bases")
    cq_min_rays, cq_min_pairs, cq_min_triads, cq_size = get_minimal_ks(cq_rays, cq_pairs, cq_triads)
    print(f"  Minimized: {cq_size} rays, {len(cq_min_triads)} bases")
    result = analyze_island(f"Z[sqrt(-2)] min-{cq_size}", cq_size, cq_min_pairs, cq_min_triads)
    all_results.append(result)

    # ================================================================
    # Heegner-7 island
    # ================================================================
    print("\n\n" + "=" * 70)
    print("ISLAND 5: HEEGNER-7")
    print("=" * 70)

    h7_rays, h7_pairs, h7_triads, _, _ = build_heegner7_island()
    print(f"  Pool: {len(h7_rays)} rays, {len(h7_triads)} bases")
    h7_min_rays, h7_min_pairs, h7_min_triads, h7_size = get_minimal_ks(h7_rays, h7_pairs, h7_triads)
    print(f"  Minimized: {h7_size} rays, {len(h7_min_triads)} bases")
    result = analyze_island(f"Heegner-7 min-{h7_size}", h7_size, h7_min_pairs, h7_min_triads)
    all_results.append(result)

    # Also full pool
    print(f"\n  --- Full Heegner-7 pool for comparison ---")
    result_full = analyze_island(f"Heegner-7 pool ({len(h7_rays)})", len(h7_rays), h7_pairs, h7_triads, detail=False)
    all_results.append(result_full)

    # ================================================================
    # Summary table
    # ================================================================
    print("\n\n" + "=" * 70)
    print("SUMMARY: CRITICAL BASES ACROSS ALL ISLANDS")
    print("=" * 70)

    print(f"\n{'Set':<28s} {'rays':>5s} {'bases':>6s} {'ess':>5s} {'rem':>5s} "
          f"{'ess%':>6s} {'crit_k':>7s} {'CF':>7s}")
    print("-" * 70)

    for r in all_results:
        ess_pct = f"{r['essentiality_ratio']:.3f}"
        cf = f"{r['contextual_fraction']:.4f}" if r['contextual_fraction'] is not None else "?"
        ck = str(r['critical_k']) if r['critical_k'] is not None else ">10"
        print(f"{r['name']:<28s} {r['n_rays']:5d} {r['n_bases']:6d} {r['n_essential']:5d} "
              f"{r['n_removable']:5d} {ess_pct:>6s} {ck:>7s} {cf:>7s}")

    print("\nKey:")
    print("  ess    = essential bases (single removal breaks uncolorability)")
    print("  rem    = removable bases (single removal preserves uncolorability)")
    print("  ess%   = essentiality ratio (fraction of bases that are essential)")
    print("  crit_k = critical number (minimum bases to remove)")
    print("  CF     = contextual fraction (crit_k / total bases)")

    print("\nInterpretation:")
    print("  Higher CF = more tightly woven KS proof (harder to break)")
    print("  Lower CF  = fragile proof (few removals suffice)")
    print("  CF measures contextual resilience, orthogonal to CSW advantage")


if __name__ == "__main__":
    main()
