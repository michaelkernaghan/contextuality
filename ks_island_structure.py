"""
ks_island_structure.py -- Analyze structural properties of each island's minimal KS set
=========================================================================================

For each island, extract a minimal KS set and compute:
1. Number of orthogonal bases (complete triads)
2. Automorphism group order (permutations preserving orthogonality graph)
3. Number of orbit types under the automorphism group
4. Vertex degree distribution

These properties determine BPQS efficiency per the Trandafir-Cabello algorithm.
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
    sat_minimize,
)

from ks_sat import is_uncolorable as sat_uncolorable


def build_pairs_triads(rays, tol=1e-9):
    """Build orthogonal pairs and triads."""
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


def count_bases(triads):
    """Count complete orthogonal bases (triads)."""
    return len(triads)


def degree_distribution(n, pairs):
    """Compute degree distribution of orthogonality graph."""
    deg = [0] * n
    for a, b in pairs:
        deg[a] += 1
        deg[b] += 1
    dist = {}
    for d in deg:
        dist[d] = dist.get(d, 0) + 1
    return dist, deg


def count_automorphisms(n, pair_set, triads, max_check=100000):
    """
    Estimate automorphism group order by checking permutations that
    preserve the orthogonality graph. For small n, try systematic approach.
    For larger n, sample random permutations.

    Uses degree-based partitioning to reduce search space.
    """
    # Build adjacency for fast lookup
    adj = [set() for _ in range(n)]
    for a, b in pair_set:
        adj[a].add(b)
        adj[b].add(a)

    # Group vertices by degree
    degrees = [len(adj[i]) for i in range(n)]
    deg_groups = {}
    for i in range(n):
        d = degrees[i]
        deg_groups.setdefault(d, []).append(i)

    # Sort degree classes
    deg_classes = sorted(deg_groups.keys())
    class_sizes = [len(deg_groups[d]) for d in deg_classes]

    print(f"    Degree classes: {dict(zip(deg_classes, class_sizes))}")

    # For small cases, try to count by sampling
    # An automorphism must map each degree class to itself
    auto_count = 0
    tested = 0

    # Try identity
    auto_count = 1  # identity is always an automorphism

    # For small n, try all permutations within degree classes
    total_perms = 1
    for size in class_sizes:
        total_perms *= math.factorial(size)

    if total_perms <= max_check:
        print(f"    Trying all {total_perms} degree-preserving permutations...")

        # Generate all permutations respecting degree classes
        from itertools import permutations as perms

        class_perms = []
        for d in deg_classes:
            class_perms.append(list(perms(deg_groups[d])))

        auto_count = 0
        for combo in itertools.product(*class_perms):
            # Build full permutation
            perm = [0] * n
            for cls_idx, d in enumerate(deg_classes):
                orig = deg_groups[d]
                mapped = combo[cls_idx]
                for i, v in enumerate(orig):
                    perm[v] = mapped[i]

            # Check if this permutation preserves adjacency
            valid = True
            for a, b in pair_set:
                if perm[b] not in adj[perm[a]]:
                    valid = False
                    break
            if valid:
                auto_count += 1
            tested += 1

        return auto_count, tested
    else:
        print(f"    Too many permutations ({total_perms}). Sampling {max_check}...")
        # Sample random degree-preserving permutations
        auto_count = 0
        for _ in range(max_check):
            perm = [0] * n
            for d in deg_classes:
                orig = deg_groups[d]
                shuffled = list(orig)
                random.shuffle(shuffled)
                for i, v in enumerate(orig):
                    perm[v] = shuffled[i]

            valid = True
            for a, b in pair_set:
                if perm[b] not in adj[perm[a]]:
                    valid = False
                    break
            if valid:
                auto_count += 1
            tested += 1

        # Estimate: auto_count/tested * total_perms
        est = auto_count / tested * total_perms if tested > 0 else 0
        return auto_count, tested, est


def orbit_types(n, pair_set, adj, sample=10000):
    """Estimate number of vertex orbit types by sampling automorphisms."""
    degrees = [len(adj[i]) for i in range(n)]

    # Group by degree first (upper bound on orbits)
    deg_groups = {}
    for i in range(n):
        deg_groups.setdefault(degrees[i], []).append(i)

    # Within each degree class, check if vertices are equivalent
    # Two vertices are in the same orbit if some automorphism maps one to the other
    # Approximate: check local neighborhood structure
    def neighborhood_sig(v, depth=2):
        """Signature based on sorted neighbor degrees (depth-limited)."""
        sig = [degrees[v]]
        nbrs = sorted(adj[v])
        sig.append(tuple(sorted(degrees[u] for u in nbrs)))
        if depth >= 2:
            for u in nbrs:
                sig.append(tuple(sorted(degrees[w] for w in adj[u])))
        return tuple(sig)

    sigs = {}
    for i in range(n):
        s = neighborhood_sig(i)
        sigs.setdefault(s, []).append(i)

    return len(sigs), {k: len(v) for k, v in sigs.items()}


def analyze_island(name, rays, pairs, triads, pair_set, max_auto_check=100000):
    """Full structural analysis of a minimal KS set."""
    n = len(rays)
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")
    print(f"  Vectors: {n}")
    print(f"  Pairs: {len(pairs)}")
    print(f"  Bases (triads): {len(triads)}")

    # Degree distribution
    dist, deg = degree_distribution(n, pairs)
    print(f"  Degree distribution: {dict(sorted(dist.items()))}")

    # Adjacency
    adj = [set() for _ in range(n)]
    for a, b in pair_set:
        adj[a].add(b)
        adj[b].add(a)

    # Orbit types
    n_orbits, orbit_info = orbit_types(n, pair_set, adj)
    print(f"  Vertex orbit types (neighborhood signature): {n_orbits}")
    for sig, count in sorted(orbit_info.items(), key=lambda x: -x[1]):
        print(f"    {count} vertices with signature hash")

    # Automorphism group
    print(f"  Automorphism group:")
    result = count_automorphisms(n, pair_set, triads, max_check=max_auto_check)
    if len(result) == 2:
        auto_count, tested = result
        print(f"    |Aut| = {auto_count} (exact, checked {tested} permutations)")
    else:
        auto_count, tested, est = result
        print(f"    Found {auto_count}/{tested} automorphisms (estimated |Aut| ~ {est:.0f})")


def get_minimal_set(rays, pairs, triads, n_trials=500):
    """Get a minimal KS set via SAT minimization."""
    best_subset, best_size, sizes = sat_minimize(rays, pairs, triads, n_trials=n_trials)
    return best_subset, best_size, sizes


def main():
    random.seed(42)

    print("=" * 60)
    print("STRUCTURAL ANALYSIS OF ALGEBRAIC ISLAND KS SETS")
    print("=" * 60)

    # ---- Island 1: Integer (CK-31) ----
    print("\n\nGenerating Integer island (CK-31)...")
    int_alph = [0, 1, -1, 2, -2]
    int_rays = generate_rays_from_alphabet([complex(x) for x in int_alph])
    int_pairs, int_triads = build_pairs_triads(int_rays)
    print(f"  Pool: {len(int_rays)} rays, {len(int_pairs)} pairs, {len(int_triads)} triads")
    int_subset, int_size, _ = get_minimal_set(int_rays, int_pairs, int_triads, n_trials=200)
    print(f"  Minimal set: {int_size} vectors")

    # Restrict to minimal set
    s = set(int_subset)
    remap = {old: new for new, old in enumerate(sorted(int_subset))}
    min_rays = [int_rays[i] for i in sorted(int_subset)]
    min_pairs = [(remap[a], remap[b]) for a, b in int_pairs if a in s and b in s]
    min_pair_set = set(min_pairs) | set((b, a) for a, b in min_pairs)
    min_triads = [(remap[a], remap[b], remap[c]) for a, b, c in int_triads if a in s and b in s and c in s]
    analyze_island("Integer Island (CK-31)", min_rays, min_pairs, min_triads, min_pair_set)

    # ---- Island 2: Peres / sqrt(2) ----
    print("\n\nGenerating Peres island (sqrt(2))...")
    s2 = math.sqrt(2)
    peres_alph = [complex(x) for x in [0, 1, -1, s2, -s2]]
    peres_rays = generate_rays_from_alphabet(peres_alph)
    peres_pairs, peres_triads = build_pairs_triads(peres_rays)
    print(f"  Pool: {len(peres_rays)} rays, {len(peres_pairs)} pairs, {len(peres_triads)} triads")
    p_subset, p_size, _ = get_minimal_set(peres_rays, peres_pairs, peres_triads, n_trials=200)
    print(f"  Minimal set: {p_size} vectors")

    s = set(p_subset)
    remap = {old: new for new, old in enumerate(sorted(p_subset))}
    min_rays = [peres_rays[i] for i in sorted(p_subset)]
    min_pairs = [(remap[a], remap[b]) for a, b in peres_pairs if a in s and b in s]
    min_pair_set = set(min_pairs) | set((b, a) for a, b in min_pairs)
    min_triads = [(remap[a], remap[b], remap[c]) for a, b, c in peres_triads if a in s and b in s and c in s]
    analyze_island("Peres Island (sqrt(2), min=33)", min_rays, min_pairs, min_triads, min_pair_set)

    # ---- Island 3: Eisenstein ----
    print("\n\nGenerating Eisenstein island...")
    eis_rays = generate_eisenstein_rays(max_coeff=1, dim=3, norm_cutoff=3)
    eis_pairs, eis_triads = build_pairs_triads(eis_rays)
    print(f"  Pool: {len(eis_rays)} rays, {len(eis_pairs)} pairs, {len(eis_triads)} triads")
    e_subset, e_size, _ = get_minimal_set(eis_rays, eis_pairs, eis_triads, n_trials=200)
    print(f"  Minimal set: {e_size} vectors")

    s = set(e_subset)
    remap = {old: new for new, old in enumerate(sorted(e_subset))}
    min_rays = [eis_rays[i] for i in sorted(e_subset)]
    min_pairs = [(remap[a], remap[b]) for a, b in eis_pairs if a in s and b in s]
    min_pair_set = set(min_pairs) | set((b, a) for a, b in min_pairs)
    min_triads = [(remap[a], remap[b], remap[c]) for a, b, c in eis_triads if a in s and b in s and c in s]
    analyze_island("Eisenstein Island (min=33)", min_rays, min_pairs, min_triads, min_pair_set)

    # ---- Island 4: Z[sqrt(-2)] ----
    print("\n\nGenerating Z[sqrt(-2)] island...")
    sd2 = cmath.sqrt(-2)
    cq_alph = [0, 1, -1, sd2, -sd2]
    cq_rays = generate_rays_from_alphabet(cq_alph)
    cq_pairs, cq_triads = build_pairs_triads(cq_rays)
    print(f"  Pool: {len(cq_rays)} rays, {len(cq_pairs)} pairs, {len(cq_triads)} triads")
    cq_subset, cq_size, _ = get_minimal_set(cq_rays, cq_pairs, cq_triads, n_trials=200)
    print(f"  Minimal set: {cq_size} vectors")

    s = set(cq_subset)
    remap = {old: new for new, old in enumerate(sorted(cq_subset))}
    min_rays = [cq_rays[i] for i in sorted(cq_subset)]
    min_pairs = [(remap[a], remap[b]) for a, b in cq_pairs if a in s and b in s]
    min_pair_set = set(min_pairs) | set((b, a) for a, b in min_pairs)
    min_triads = [(remap[a], remap[b], remap[c]) for a, b, c in cq_triads if a in s and b in s and c in s]
    analyze_island("Z[sqrt(-2)] Island (min=33)", min_rays, min_pairs, min_triads, min_pair_set)

    # ---- Island 5: Golden ratio ----
    # Note: Golden island needs cross-product completion, which is real-valued
    # We skip automorphism for this one due to the large size (52 vectors)
    print("\n\nGenerating Golden island...")
    phi = (1 + math.sqrt(5)) / 2
    gold_alph = [complex(x) for x in [0, 1, -1, phi, -phi]]
    gold_rays_raw = generate_rays_from_alphabet(gold_alph)
    print(f"  Raw pool: {len(gold_rays_raw)} rays")

    # Need cross-product completion for golden island
    # Use the hermitian_completion from ks_new_islands
    from ks_new_islands import hermitian_completion
    gold_rays = hermitian_completion(gold_rays_raw)
    gold_pairs, gold_triads = build_pairs_triads(gold_rays)
    print(f"  Completed pool: {len(gold_rays)} rays, {len(gold_pairs)} pairs, {len(gold_triads)} triads")

    if gold_triads and sat_uncolorable(len(gold_rays), gold_pairs, gold_triads):
        g_subset, g_size, _ = get_minimal_set(gold_rays, gold_pairs, gold_triads, n_trials=100)
        print(f"  Minimal set: {g_size} vectors")

        s = set(g_subset)
        remap = {old: new for new, old in enumerate(sorted(g_subset))}
        min_rays = [gold_rays[i] for i in sorted(g_subset)]
        min_pairs = [(remap[a], remap[b]) for a, b in gold_pairs if a in s and b in s]
        min_pair_set = set(min_pairs) | set((b, a) for a, b in min_pairs)
        min_triads = [(remap[a], remap[b], remap[c]) for a, b, c in gold_triads if a in s and b in s and c in s]
        # Skip automorphism for 52-vector set (too large for exact enumeration)
        analyze_island("Golden Island (min=52)", min_rays, min_pairs, min_triads, min_pair_set, max_auto_check=50000)
    else:
        print("  Golden island not uncolorable (completion may need real cross-product)")

    print("\n\n" + "=" * 60)
    print("SUMMARY: Structural comparison across islands")
    print("=" * 60)


if __name__ == "__main__":
    main()
