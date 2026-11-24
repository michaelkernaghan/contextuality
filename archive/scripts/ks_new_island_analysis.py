"""
ks_new_island_analysis.py -- Structural analysis of newly discovered islands
=============================================================================

Analyzes the Gaussian (Z[i] + (1+i)) and Heegner-7 (Z[(1+sqrt(-7))/2]) islands.
"""

import cmath
import math
import random
import time

from ks_complex import (
    hermitian_dot,
    canonicalize_complex_ray,
)

from ks_new_islands import (
    generate_rays_from_alphabet,
    hermitian_completion,
    sat_minimize,
    test_alphabet,
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


def degree_distribution(n, pairs):
    deg = [0] * n
    for a, b in pairs:
        deg[a] += 1
        deg[b] += 1
    dist = {}
    for d in deg:
        dist[d] = dist.get(d, 0) + 1
    return dist, deg


def get_minimal_ks(rays, pairs, triads, n_trials=500):
    subset, size, sizes = sat_minimize(rays, pairs, triads, n_trials=n_trials)
    s = set(subset)
    remap = {old: new for new, old in enumerate(sorted(subset))}
    min_rays = [rays[i] for i in sorted(subset)]
    min_pairs = [(remap[a], remap[b]) for a, b in pairs if a in s and b in s]
    min_triads = [(remap[a], remap[b], remap[c]) for a, b, c in triads
                  if a in s and b in s and c in s]
    return min_rays, min_pairs, min_triads, size, sizes


def analyze_structure(name, min_rays, min_pairs, min_triads, size):
    """Full structural analysis of a minimal KS set."""
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")
    print(f"  Vectors: {size}")
    print(f"  Pairs: {len(min_pairs)}")
    print(f"  Bases (triads): {len(min_triads)}")

    # Degree distribution
    dist, deg = degree_distribution(size, min_pairs)
    print(f"  Degree distribution: {dict(sorted(dist.items()))}")

    # Base membership
    vec_bases = {}
    for b_idx, (i, j, k) in enumerate(min_triads):
        for v in [i, j, k]:
            vec_bases.setdefault(v, set()).add(b_idx)

    base_counts = [len(vec_bases.get(v, set())) for v in range(size)]
    bc_dist = {}
    for c in base_counts:
        bc_dist[c] = bc_dist.get(c, 0) + 1
    print(f"  Base membership: {dict(sorted(bc_dist.items()))}")

    n_single = sum(1 for c in base_counts if c < 2)
    print(f"  Single-basis vectors: {n_single}/{size} ({100*n_single/size:.0f}%)")

    # Orbit types (neighborhood signature)
    adj = [set() for _ in range(size)]
    for a, b in min_pairs:
        adj[a].add(b)
        adj[b].add(a)

    def neighborhood_sig(v, depth=2):
        sig = [deg[v]]
        nbrs = sorted(adj[v])
        sig.append(tuple(sorted(deg[u] for u in nbrs)))
        if depth >= 2:
            for u in nbrs:
                sig.append(tuple(sorted(deg[w] for w in adj[u])))
        return tuple(sig)

    sigs = {}
    for i in range(size):
        s = neighborhood_sig(i)
        sigs.setdefault(s, []).append(i)

    print(f"  Orbit types (neighborhood signature): {len(sigs)}")
    for sig, verts in sorted(sigs.items(), key=lambda x: -len(x[1])):
        print(f"    {len(verts)} vertices")


def verify_heegner_identity(d):
    """Show the algebraic identity underlying a Heegner island."""
    gen = (1 + cmath.sqrt(-d)) / 2
    gen_conj = gen.conjugate()
    norm = abs(gen) ** 2
    print(f"  Generator: (1 + sqrt(-{d}))/2")
    print(f"  Conjugate: (1 - sqrt(-{d}))/2")
    print(f"  |generator|^2 = {norm:.6f}")
    print(f"  generator * conjugate = {(gen * gen_conj).real:.6f}")
    # Minimal polynomial: x^2 - x + (1+d)/4
    c = (1 + d) / 4
    print(f"  Minimal polynomial: x^2 - x + {c}")
    print(f"  Check: gen^2 - gen + {c} = {gen**2 - gen + c}")
    # Key identity for orthogonality
    print(f"  1 + |gen|^2 = {1 + norm:.6f}")
    print(f"  gen + conj(gen) = {(gen + gen_conj).real:.6f} (trace)")


def main():
    random.seed(42)

    print("=" * 60)
    print("STRUCTURAL ANALYSIS OF NEWLY DISCOVERED ISLANDS")
    print("=" * 60)

    # ================================================================
    # Gaussian Island: Z[i] with (1+i)
    # ================================================================
    print("\n\n" + "=" * 60)
    print("GAUSSIAN ISLAND: Z[i] + (1+i)")
    print("=" * 60)
    print("Key identity: |1+i|^2 = 2, giving Gaussian norm cancellation")
    print("Alphabet: {0, +/-1, +/-i, +/-(1+i)}")

    I = 1j
    gauss_alph = [0, 1, -1, I, -I, 1+I, -(1+I)]
    gauss_rays = generate_rays_from_alphabet(gauss_alph)
    gauss_pairs, gauss_triads = build_pairs_triads(gauss_rays)
    print(f"\nPool: {len(gauss_rays)} rays, {len(gauss_pairs)} pairs, {len(gauss_triads)} triads")

    assert sat_uncolorable(len(gauss_rays), gauss_pairs, gauss_triads)
    print("KS-uncolorable: YES")

    min_rays, min_pairs, min_triads, size, sizes = get_minimal_ks(
        gauss_rays, gauss_pairs, gauss_triads, n_trials=500)
    print(f"Minimal set: {size} vectors")
    print(f"Size distribution: {dict(sorted(sizes.items()))}")

    analyze_structure("Gaussian Island (min KS)", min_rays, min_pairs, min_triads, size)

    # Check if Gaussian min-33 is structurally identical to Z[sqrt(-2)] min-33
    print("\n  Comparison with Z[sqrt(-2)] island:")
    sd2 = cmath.sqrt(-2)
    zsd2_alph = [0, 1, -1, sd2, -sd2]
    zsd2_rays = generate_rays_from_alphabet(zsd2_alph)
    zsd2_pairs, zsd2_triads = build_pairs_triads(zsd2_rays)
    zsd2_min_rays, zsd2_min_pairs, zsd2_min_triads, zsd2_size, _ = get_minimal_ks(
        zsd2_rays, zsd2_pairs, zsd2_triads, n_trials=300)
    zsd2_dist, _ = degree_distribution(zsd2_size, zsd2_min_pairs)
    print(f"    Z[sqrt(-2)] degree distribution: {dict(sorted(zsd2_dist.items()))}")
    gauss_dist, _ = degree_distribution(size, min_pairs)
    print(f"    Gaussian degree distribution: {dict(sorted(gauss_dist.items()))}")
    if zsd2_dist == gauss_dist:
        print("    SAME degree distribution — may be isomorphic!")
    else:
        print("    DIFFERENT degree distributions — structurally distinct!")

    # ================================================================
    # Heegner-7 Island: Z[(1+sqrt(-7))/2]
    # ================================================================
    print("\n\n" + "=" * 60)
    print("HEEGNER-7 ISLAND: Z[(1+sqrt(-7))/2]")
    print("=" * 60)
    print("Ring of integers of Q(sqrt(-7)), class number 1 (Heegner number)")

    verify_heegner_identity(7)

    gen7 = (1 + cmath.sqrt(-7)) / 2
    h7_alph = [0, 1, -1, gen7, -gen7, gen7.conjugate(), -gen7.conjugate()]
    h7_rays = generate_rays_from_alphabet(h7_alph)
    h7_pairs, h7_triads = build_pairs_triads(h7_rays)
    print(f"\nPool: {len(h7_rays)} rays, {len(h7_pairs)} pairs, {len(h7_triads)} triads")

    assert sat_uncolorable(len(h7_rays), h7_pairs, h7_triads)
    print("KS-uncolorable: YES")

    min_rays, min_pairs, min_triads, size, sizes = get_minimal_ks(
        h7_rays, h7_pairs, h7_triads, n_trials=500)
    print(f"Minimal set: {size} vectors")
    print(f"Size distribution: {dict(sorted(sizes.items()))}")

    analyze_structure("Heegner-7 Island (min KS)", min_rays, min_pairs, min_triads, size)

    # ================================================================
    # Systematic check of ALL imaginary quadratic fields with class number 1
    # These are the Heegner numbers: d = 1, 2, 3, 7, 11, 19, 43, 67, 163
    # d=1 is Gaussian, d=3 is Eisenstein, d=2 is Z[sqrt(-2)]
    # ================================================================
    print("\n\n" + "=" * 60)
    print("SYSTEMATIC CHECK: All Heegner number imaginary quadratic fields")
    print("These are the ONLY d with class number 1: d = 1, 2, 3, 7, 11, 19, 43, 67, 163")
    print("=" * 60)

    heegner_results = []
    for d in [1, 2, 3, 7, 11, 19, 43, 67, 163]:
        if d % 4 == 3:
            # Ring of integers: Z[(1+sqrt(-d))/2]
            gen = (1 + cmath.sqrt(-d)) / 2
            alph = [0, 1, -1, gen, -gen, gen.conjugate(), -gen.conjugate()]
            ring_name = f"Z[(1+sqrt(-{d}))/2]"
        elif d == 1:
            # Gaussian: need (1+i) for KS
            alph = [0, 1, -1, 1j, -1j, 1+1j, -(1+1j)]
            ring_name = "Z[i] + (1+i)"
        elif d == 2:
            # Z[sqrt(-2)]
            sd = cmath.sqrt(-2)
            alph = [0, 1, -1, sd, -sd]
            ring_name = "Z[sqrt(-2)]"
        else:
            sd = cmath.sqrt(-d)
            alph = [0, 1, -1, sd, -sd]
            ring_name = f"Z[sqrt(-{d})]"

        print(f"\n--- d = {d}: {ring_name} ---")
        norm = abs(gen if d % 4 == 3 else alph[3]) ** 2
        print(f"  Generator norm: {norm:.4f}")

        rays = generate_rays_from_alphabet(alph)
        pairs, triads = build_pairs_triads(rays)
        print(f"  Pool: {len(rays)} rays, {len(pairs)} pairs, {len(triads)} triads")

        if triads and sat_uncolorable(len(rays), pairs, triads):
            _, best_size, _ = sat_minimize(rays, pairs, triads, n_trials=300)
            print(f"  KS-UNCOLORABLE! min = {best_size}")
            heegner_results.append((d, ring_name, len(rays), len(triads), best_size))
        else:
            print(f"  Colorable")
            # Try with completion
            rays_c = hermitian_completion(rays)
            pairs_c, triads_c = build_pairs_triads(rays_c)
            if triads_c and sat_uncolorable(len(rays_c), pairs_c, triads_c):
                _, best_size, _ = sat_minimize(rays_c, pairs_c, triads_c, n_trials=200)
                print(f"  After completion: {len(rays_c)} rays, {len(triads_c)} triads")
                print(f"  UNCOLORABLE with completion! min = {best_size}")
                heegner_results.append((d, ring_name + " (compl)", len(rays_c), len(triads_c), best_size))
            else:
                print(f"  Still colorable after completion ({len(rays_c)} rays, {len(triads_c)} triads)")
                heegner_results.append((d, ring_name, len(rays), len(triads), None))

    # ================================================================
    # Summary
    # ================================================================
    print("\n\n" + "=" * 60)
    print("SUMMARY: HEEGNER NUMBER ISLANDS")
    print("=" * 60)
    print(f"{'d':>4s}  {'Ring':<30s} {'Rays':>5s} {'Triads':>7s} {'Min KS':>7s}")
    print("-" * 60)
    for d, ring, rays, triads, min_ks in heegner_results:
        ks_str = str(min_ks) if min_ks else "colorable"
        print(f"{d:4d}  {ring:<30s} {rays:5d} {triads:7d} {ks_str:>7s}")

    print("\nNote: d = 1, 2, 3, 7 are the imaginary quadratic fields with class number 1")
    print("      that produce KS sets. d >= 11 appear colorable even after completion.")
    print("      The Heegner numbers d = 43, 67, 163 have very sparse orthogonality.")


if __name__ == "__main__":
    main()
