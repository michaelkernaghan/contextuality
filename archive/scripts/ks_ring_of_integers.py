"""
ks_ring_of_integers.py - Test ring-of-integers generators for d≡1 mod 4.

For d≡1 mod 4, the ring of integers of Q(√d) is Z[(1+√d)/2],
NOT Z[√d]. The golden ratio φ = (1+√5)/2 is exactly this for d=5.

Reviewer asked: did we test analogous generators for d=13,17,21,29?

We test alphabets {0, ±1, ±(1+√d)/2} for d≡1 mod 4, d=5..30.
Also test cross-product completion for each.
"""

import math
import sys
import itertools
import random

sys.stdout.reconfigure(encoding='utf-8')

from ks_islands import (
    canonicalize_real_ray,
    generate_real_rays,
    real_orthog_pairs,
    real_triads,
    real_is_uncolorable,
    cross_product_completion,
)

from ks_complex import (
    is_colorable as complex_is_colorable,
    multi_trial_minimize as complex_minimize,
)


def test_ring_generator(d, verbose=True):
    """Test the ring-of-integers generator (1+√d)/2 for Q(√d)."""
    sd = math.sqrt(d)
    gen = (1 + sd) / 2

    # Standard alphabet with the generator
    alphabet = [0, 1, -1, gen, -gen]
    rays = generate_real_rays(alphabet)
    pairs = real_orthog_pairs(rays)
    triads = real_triads(rays, pairs)

    # Test with cross-product completion
    completed = cross_product_completion(rays, rays, tol=1e-9)
    c_pairs = real_orthog_pairs(completed, tol=1e-9)
    c_triads = real_triads(completed, c_pairs)

    # Check colorability of raw
    raw_unc = False
    raw_min = '--'
    if triads:
        cvecs = [tuple(complex(c) for c in v) for v in rays]
        colorable = complex_is_colorable(cvecs)
        raw_unc = not colorable
        if raw_unc:
            _, best_size, _ = complex_minimize(cvecs, num_trials=200, verbose=False)
            raw_min = str(best_size)

    # Check colorability of completed
    comp_unc = False
    comp_min = '--'
    if c_triads:
        cvecs_c = [tuple(complex(c) for c in v) for v in completed]
        colorable_c = complex_is_colorable(cvecs_c)
        comp_unc = not colorable_c
        if comp_unc:
            _, best_size_c, _ = complex_minimize(cvecs_c, num_trials=200, verbose=False)
            comp_min = str(best_size_c)

    gen_val = f"(1+sqrt({d}))/2 = {gen:.6f}"

    if verbose:
        print(f"  d={d:2d} gen={gen_val:30s}")
        print(f"    Raw:      {len(rays):3d} rays, {len(pairs):3d}p, {len(triads):2d}t, "
              f"{'UNC' if raw_unc else 'col':3s}, min: {raw_min}")
        print(f"    Completed: {len(completed):3d} rays, {len(c_pairs):3d}p, {len(c_triads):3d}t, "
              f"{'UNC' if comp_unc else 'col':3s}, min: {comp_min}")

    return {
        'd': d,
        'gen': gen,
        'raw_rays': len(rays),
        'raw_triads': len(triads),
        'raw_unc': raw_unc,
        'raw_min': raw_min,
        'comp_rays': len(completed),
        'comp_triads': len(c_triads),
        'comp_unc': comp_unc,
        'comp_min': comp_min,
    }


def test_sqrt_generator(d, verbose=True):
    """For comparison: test {0, ±1, ±√d} (the non-ring-of-integers generator)."""
    sd = math.sqrt(d)
    alphabet = [0, 1, -1, sd, -sd]
    rays = generate_real_rays(alphabet)
    pairs = real_orthog_pairs(rays)
    triads = real_triads(rays, pairs)

    completed = cross_product_completion(rays, rays, tol=1e-9)
    c_pairs = real_orthog_pairs(completed, tol=1e-9)
    c_triads = real_triads(completed, c_pairs)

    raw_unc = False
    raw_min = '--'
    if triads:
        cvecs = [tuple(complex(c) for c in v) for v in rays]
        colorable = complex_is_colorable(cvecs)
        raw_unc = not colorable
        if raw_unc:
            _, best_size, _ = complex_minimize(cvecs, num_trials=200, verbose=False)
            raw_min = str(best_size)

    comp_unc = False
    comp_min = '--'
    if c_triads:
        cvecs_c = [tuple(complex(c) for c in v) for v in completed]
        colorable_c = complex_is_colorable(cvecs_c)
        comp_unc = not colorable_c
        if comp_unc:
            _, best_size_c, _ = complex_minimize(cvecs_c, num_trials=200, verbose=False)
            comp_min = str(best_size_c)

    if verbose:
        print(f"    sqrt({d}):  {len(rays):3d} rays, {len(pairs):3d}p, {len(triads):2d}t, "
              f"{'UNC' if raw_unc else 'col':3s} -> "
              f"{len(completed):3d} rays, {len(c_triads):3d}t, "
              f"{'UNC' if comp_unc else 'col':3s}, min: {comp_min}")


if __name__ == "__main__":
    random.seed(42)
    print("=" * 70)
    print("RING-OF-INTEGERS GENERATOR TEST")
    print("For d=1 mod 4: generator = (1+sqrt(d))/2")
    print("For d=2,3 mod 4: generator = sqrt(d) [standard]")
    print("=" * 70)

    # Test d=1 mod 4 cases with both generators
    print("\n--- d = 1 mod 4: Ring-of-integers generator (1+sqrt(d))/2 ---\n")
    for d in [5, 13, 17, 21, 29]:
        if math.sqrt(d) == int(math.sqrt(d)):
            continue
        result = test_ring_generator(d)
        # Also test sqrt(d) for comparison
        print(f"    Comparison with sqrt(d) generator:")
        test_sqrt_generator(d)
        print()

    # Also test a few d != 1 mod 4 with the (1+sqrt(d))/2 generator
    # (not a ring of integers, but still a valid algebraic number)
    print("\n--- d != 1 mod 4: (1+sqrt(d))/2 is NOT ring-of-integers ---\n")
    for d in [2, 3, 6, 7]:
        result = test_ring_generator(d)
        print()

    print("=" * 70)
    print("COMPLETE")
    print("=" * 70)
