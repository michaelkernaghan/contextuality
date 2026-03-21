#!/usr/bin/env python3
"""
Deep dive into d=15 halfint KS set — the one genuinely new class-number > 1 result.

Q(sqrt(-15)), h=2, O_K = Z[(1+sqrt(-15))/2], |gen|^2 = 4.
"""

import cmath
import random
import sys
import time
from collections import Counter

from ks_explore_new import test_alphabet
from ks_new_islands import generate_rays_from_alphabet, sat_minimize
from ks_new_island_analysis import build_pairs_triads
from ks_sat import is_uncolorable as sat_uncolorable
from ks_complex import canonicalize_complex_ray, hermitian_dot

random.seed(42)
sys.stdout.reconfigure(encoding='utf-8')


def main():
    d = 15
    sd = cmath.sqrt(-d)
    gen = (1 + sd) / 2
    gen_conj = (1 - sd) / 2

    print(f"d={d}, gen = (1+sqrt(-15))/2 = {gen}")
    print(f"gen_conj = (1-sqrt(-15))/2 = {gen_conj}")
    print(f"|gen|^2 = {abs(gen)**2:.4f}")
    print(f"|gen_conj|^2 = {abs(gen_conj)**2:.4f}")
    print(f"gen * gen_conj = {gen * gen_conj}")
    print(f"gen + gen_conj = {gen + gen_conj}")
    print(f"gen^2 = {gen**2}")
    print(f"gen_conj^2 = {gen_conj**2}")
    print()

    # Build the enriched alphabet (same as survey)
    basic = [0, 1, -1, gen, -gen, gen_conj, -gen_conj]
    extra = [
        gen * gen, -(gen * gen),
        gen_conj * gen_conj, -(gen_conj * gen_conj),
        1 + gen, -(1 + gen),
        1 + gen_conj, -(1 + gen_conj),
        gen + gen_conj, -(gen + gen_conj),
    ]
    candidates = basic + extra
    # Dedup
    seen = set()
    alphabet = []
    for v in candidates:
        key = (round(v.real, 7), round(v.imag, 7))
        if key not in seen:
            seen.add(key)
            alphabet.append(complex(v))
    # Filter pure integers > 1
    filtered = []
    for v in alphabet:
        if abs(v.imag) < 1e-8 and abs(v.real - round(v.real)) < 1e-8:
            if abs(v.real) <= 1:
                filtered.append(v)
        else:
            filtered.append(v)
    alphabet = filtered[:15]

    print(f"Enriched alphabet ({len(alphabet)} elements):")
    for i, a in enumerate(alphabet):
        norm = abs(a)**2
        print(f"  [{i}] {str(a):>40s}  |z|^2 = {norm:.4f}")
    print()

    # Step 1: Generate rays
    print("Generating rays...")
    rays = generate_rays_from_alphabet(alphabet)
    print(f"  Raw rays: {len(rays)}")

    # Step 2: Build orthogonality graph
    pairs, triads = build_pairs_triads(rays)
    print(f"  Pairs: {len(pairs)}, Triads: {len(triads)}")

    # Step 3: Check uncolorability
    uncol = sat_uncolorable(len(rays), pairs, triads)
    print(f"  Uncolorable (raw): {uncol}")
    print()

    if not uncol:
        print("Raw set is colorable — this shouldn't happen based on survey results.")
        print("The survey found UNCOL at 1537 rays without completion.")
        print("Checking if alphabet matches...")
        return

    # Step 4: Minimize with limited trials (1537 rays = slow per trial)
    print("Running 10-trial minimization (1537 rays, ~2min/trial)...")
    t0 = time.time()
    subset, min_size, size_dist = sat_minimize(rays, pairs, triads, n_trials=10)
    elapsed = time.time() - t0
    print(f"  Min size: {min_size} ({elapsed:.1f}s)")
    print(f"  Size distribution: {dict(sorted(size_dist.items()))}")
    print()

    # Step 5: Extract minimal set
    s = set(subset)
    min_rays = [rays[i] for i in sorted(subset)]
    remap = {old: new for new, old in enumerate(sorted(subset))}
    min_pairs = [(remap[a], remap[b]) for a, b in pairs if a in s and b in s]
    min_triads = [(remap[a], remap[b], remap[c]) for a, b, c in triads
                  if a in s and b in s and c in s]

    print(f"Minimal KS set: {min_size} rays, {len(min_triads)} bases")
    print()

    # Step 6: Degree sequence (orthogonality graph)
    degree = Counter()
    for a, b in min_pairs:
        degree[a] += 1
        degree[b] += 1
    deg_seq = sorted(degree.values(), reverse=True)
    print(f"Degree sequence: {deg_seq}")
    deg_counter = Counter(deg_seq)
    print(f"Degree distribution: {dict(sorted(deg_counter.items()))}")
    print()

    # Step 7: Rays per basis count
    ray_basis_count = Counter()
    for a, b, c in min_triads:
        ray_basis_count[a] += 1
        ray_basis_count[b] += 1
        ray_basis_count[c] += 1
    basis_dist = Counter(ray_basis_count.values())
    print(f"Bases-per-ray distribution: {dict(sorted(basis_dist.items()))}")
    print()

    # Step 8: Verify — every ray in at least 2 bases (necessary for KS)
    min_basis_count = min(ray_basis_count.values()) if ray_basis_count else 0
    print(f"Min bases per ray: {min_basis_count}")
    if min_basis_count < 2:
        print("  WARNING: Some rays in only 1 basis — not a proper KS set!")
    print()

    # Step 9: Print rays with algebraic identification
    print("Minimal KS set rays:")
    print(f"{'#':>3} {'Ray':>60} {'Bases':>6}")
    print("-" * 72)
    for i, ray in enumerate(min_rays):
        n_bases = ray_basis_count.get(i, 0)
        ray_str = f"({ray[0]:.6f}, {ray[1]:.6f}, {ray[2]:.6f})"
        print(f"{i:>3} {ray_str:>60} {n_bases:>6}")
    print()

    # Step 10: Algebraic content analysis
    # What alphabet elements actually appear in the minimal set?
    elem_usage = Counter()
    for ray in min_rays:
        for component in ray:
            # Find closest alphabet element
            best = None
            best_dist = 1e10
            for a in alphabet:
                d_val = abs(component - a)
                if d_val < best_dist:
                    best_dist = d_val
                    best = a
            if best_dist < 1e-6:
                key = f"{best:.6f}"
                elem_usage[key] += 1

    print("Alphabet element usage in minimal set:")
    for elem, count in elem_usage.most_common():
        print(f"  {elem:>30s}: {count}")
    print()

    # Step 11: Check — is this isomorphic to any known 45-ray KS set?
    # The h7+i pair also gave MIN 45 (22 bases) — compare signatures
    print("Comparison signatures:")
    print(f"  d=15 halfint: {min_size} rays, {len(min_triads)} bases, deg_seq hash = {hash(tuple(deg_seq))}")
    print()

    # Step 12: Check which generators are essential
    # Try removing gen/gen_conj from alphabet and see if still UNCOL
    print("Generator essentiality test:")
    for remove_name, remove_vals in [
        ("gen", [gen, -gen]),
        ("gen_conj", [gen_conj, -gen_conj]),
        ("gen^2", [gen**2, -(gen**2)]),
        ("1+gen", [1+gen, -(1+gen)]),
    ]:
        reduced = [a for a in alphabet if not any(abs(a - rv) < 1e-8 for rv in remove_vals)]
        if len(reduced) == len(alphabet):
            print(f"  Remove {remove_name}: not in alphabet, skip")
            continue
        r_rays = generate_rays_from_alphabet(reduced)
        r_pairs, r_triads = build_pairs_triads(r_rays)
        r_uncol = sat_uncolorable(len(r_rays), r_pairs, r_triads) if r_triads else False
        print(f"  Remove {remove_name}: {len(reduced)} elems -> {len(r_rays)} rays, "
              f"{len(r_triads)} triads, uncol={r_uncol}")
    print()

    # Step 13: Compare with basic alphabet (should be colorable)
    print("Basic alphabet check:")
    basic_alpha = [0, 1, -1, gen, -gen, gen_conj, -gen_conj]
    b_rays = generate_rays_from_alphabet(basic_alpha)
    b_pairs, b_triads = build_pairs_triads(b_rays)
    b_uncol = sat_uncolorable(len(b_rays), b_pairs, b_triads) if b_triads else False
    print(f"  Basic: {len(basic_alpha)} elems -> {len(b_rays)} rays, "
          f"{len(b_triads)} triads, uncol={b_uncol}")
    print(f"  Confirms: basic alphabet alone is {'UN' if b_uncol else ''}COLORABLE")


if __name__ == "__main__":
    main()
