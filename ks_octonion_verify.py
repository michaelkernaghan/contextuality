"""
ks_octonion_verify.py -- Verify the suspicious 10-vector octonion result
=========================================================================

The main script found a 10-vector "KS set" from the full octonion alphabet.
This is suspicious because the theoretical lower bound for KS sets in dim 3
is 22 (Uijlen-Westerbaan). The likely cause: our GCD+sign canonicalization
doesn't handle right-multiplication by non-real octonions, so the pool
contains duplicate rays that create false orthogonality structure.

This script checks for duplicate rays in the octonionic pool.
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

import random
import numpy as np
from ks_octonion import (
    ZERO_O, ONE_O, E, o_neg, o_mul, o_conj, o_norm_sq, o_add, o_is_zero,
    inner_product, are_orthogonal, vec_norm_sq, vec_is_zero,
    generate_oct_pool, build_pairs_triads, is_ks_uncolorable,
    canonicalize_ovec, greedy_minimize,
)

random.seed(42)


def rays_are_parallel(u, v):
    """Check if two O^3 vectors represent the same ray.

    Two nonzero vectors u, v in O^3 represent the same ray if
    v = u * a for some nonzero octonion a (right scalar mult).

    Equivalently: the rank of the 3x1 "matrix" [u1, u2, u3] vs [v1, v2, v3]
    over the octonions is 1.

    For a practical test: convert to R^24, check if the 24-dim real vectors
    are proportional (same direction up to sign). This handles REAL scalar
    multiples. For non-real octonion scalars, we need a different test.

    Better test: u and v represent the same ray iff <u,v> * <v,u> = |u|^2 * |v|^2.
    Since <v,u> = conj(<u,v>), this becomes |<u,v>|^2 = |u|^2 * |v|^2.
    This is the octonionic Cauchy-Schwarz equality condition.
    """
    ip = inner_product(u, v)
    ip_norm_sq = o_norm_sq(ip)
    u_norm_sq = vec_norm_sq(u)
    v_norm_sq = vec_norm_sq(v)

    # Cauchy-Schwarz: |<u,v>|^2 <= |u|^2 * |v|^2, equality iff parallel
    return ip_norm_sq == u_norm_sq * v_norm_sq


# =====================================================================
# Check for duplicate rays in the unit octonion pool
# =====================================================================
print("=" * 70)
print("Checking for duplicate rays in octonion pools")
print("=" * 70)

# Small pool first: {0, +/-1, +/-2, +/-e1}
TWO_O = (2, 0, 0, 0, 0, 0, 0, 0)
alph_small = [ZERO_O, ONE_O, o_neg(ONE_O), TWO_O, o_neg(TWO_O),
              E[1], o_neg(E[1])]

pool_small = generate_oct_pool(alph_small, dim=3, norm_cutoff=9)
print(f"\n{'{0,+/-1,+/-2,+/-e1}'} pool: {len(pool_small)} rays")

dup_count = 0
dup_pairs = []
for i in range(len(pool_small)):
    for j in range(i + 1, len(pool_small)):
        if rays_are_parallel(pool_small[i], pool_small[j]):
            dup_count += 1
            if dup_count <= 5:
                dup_pairs.append((i, j))

print(f"Duplicate ray pairs: {dup_count}")
for i, j in dup_pairs:
    print(f"  Ray {i}: {pool_small[i]}")
    print(f"  Ray {j}: {pool_small[j]}")
    print()

# Full unit pool
oct_units = [ZERO_O, ONE_O, o_neg(ONE_O)]
for i in range(1, 8):
    oct_units.append(E[i])
    oct_units.append(o_neg(E[i]))

pool_units = generate_oct_pool(oct_units, dim=3)
print(f"\nUnit pool {{0,+/-1,+/-e1,...,+/-e7}}: {len(pool_units)} rays")

# Sample for duplicate check (full check is O(n^2))
sample_size = min(500, len(pool_units))
sample_idx = random.sample(range(len(pool_units)), sample_size)
sample = [pool_units[i] for i in sample_idx]

dup_count2 = 0
for i in range(sample_size):
    for j in range(i + 1, sample_size):
        if rays_are_parallel(sample[i], sample[j]):
            dup_count2 += 1
            if dup_count2 <= 3:
                print(f"\nDuplicate in unit pool:")
                print(f"  Ray {sample_idx[i]}: {sample[i]}")
                print(f"  Ray {sample_idx[j]}: {sample[j]}")

print(f"\nDuplicate pairs in sample of {sample_size}: {dup_count2}")
if dup_count2 > 0:
    estimated_total = dup_count2 * (len(pool_units) / sample_size) ** 2
    print(f"Estimated total duplicates: ~{int(estimated_total)}")

# =====================================================================
# Full octonion pool with proper deduplication
# =====================================================================
print()
print("=" * 70)
print("Full pool with Cauchy-Schwarz deduplication")
print("=" * 70)

full_alph = [ZERO_O, ONE_O, o_neg(ONE_O), TWO_O, o_neg(TWO_O)] + \
            [x for i in range(1, 8) for x in (E[i], o_neg(E[i]))]

pool_full = generate_oct_pool(full_alph, dim=3, norm_cutoff=9)
print(f"Raw pool: {len(pool_full)} rays")

# Deduplicate using Cauchy-Schwarz
deduped = []
for ray in pool_full:
    is_dup = False
    for existing in deduped:
        if rays_are_parallel(ray, existing):
            is_dup = True
            break
    if not is_dup:
        deduped.append(ray)

print(f"After Cauchy-Schwarz dedup: {len(deduped)} rays")
print(f"Duplicates removed: {len(pool_full) - len(deduped)}")

if len(deduped) <= 1500:
    pairs, triads, adj = build_pairs_triads(deduped)
    print(f"Pairs: {len(pairs)}, Triads: {len(triads)}")

    if triads:
        ks = is_ks_uncolorable(len(deduped), triads, pairs)
        print(f"KS-uncolorable: {ks}")
        if ks:
            print("Minimizing (300 trials)...")
            mi, mn = greedy_minimize(len(deduped), pairs, triads, n_trials=300)
            min_rays = [deduped[i] for i in mi]
            mp, mt, _ = build_pairs_triads(min_rays)
            print(f"MINIMAL: {mn} vectors, {len(mp)} pairs, {len(mt)} triads")

            has_oct = False
            for v in min_rays:
                for qi in v:
                    if any(qi[k] != 0 for k in range(1, 8)):
                        has_oct = True
                        break
            print(f"Uses octonionic coords: {has_oct}")
else:
    print("Still too large -- sampling 600 with dedup")
    sample = random.sample(deduped, 600)
    pairs, triads, _ = build_pairs_triads(sample)
    print(f"Sample: {len(pairs)} pairs, {len(triads)} triads")
    if triads:
        ks = is_ks_uncolorable(600, triads, pairs)
        print(f"KS: {ks}")
        if ks:
            mi, mn = greedy_minimize(600, pairs, triads, n_trials=200)
            print(f"Minimal: {mn}")
