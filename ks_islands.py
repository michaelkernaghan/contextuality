"""
ks_islands.py — Search for algebraic islands beyond CK-31
==========================================================

The core question: could there exist a KS set in R³ or C³ with fewer
than 31 vectors, built from a fundamentally different algebraic structure
than the integer coordinates of CK-31?

Key insight from perturbation analysis: CK-31 is an isolated point.
Any sub-31 KS set must live on a separate "algebraic island."

This script systematically explores candidate islands:

1. ATTRACTOR ANALYSIS: Show that any alphabet containing the identity
   xy=2 collapses to CK-31 under cross-product completion.

2. EISENSTEIN DEEP SEARCH: The only known non-integer island (min 33).
   Search larger Eisenstein pools for sub-33 complex KS sets.

3. MIXED COMPLEX FIELDS: Z[ω, √2], Z[ω, i], etc.
   Do novel cancellation patterns emerge?

4. ICOSAHEDRAL TEST: Does icosahedral symmetry provide orthogonalities
   that alphabets miss?

5. xy=2 FAMILY: Parametric search over {0, ±1, ±t, ±2/t} for
   various t, to verify all collapse to CK-31.

6. NOVEL QUADRATIC FIELDS: Systematic scan of {0, ±1, ±√d} for
   d = 2..20, checking which produce KS sets.

Requires: numpy, scipy, python-sat (optional)
"""

import numpy as np
import cmath
import math
import itertools
import random
import time
from collections import defaultdict

# Import from existing tools
try:
    from ks_sat import is_uncolorable as sat_uncolorable, build_graph
    HAS_SAT = True
except ImportError:
    HAS_SAT = False

from ks_complex import (
    is_colorable as complex_is_colorable,
    analyze_ray_set as complex_analyze,
    canonicalize_complex_ray,
    hermitian_dot,
    multi_trial_minimize as complex_minimize,
    OMEGA,
)


# ============================================================
# Real-valued tools
# ============================================================

def canonicalize_real_ray(v):
    """Canonicalize a real ray: first nonzero component positive, normalize."""
    v = list(v)
    if all(abs(x) < 1e-12 for x in v):
        return None
    for x in v:
        if abs(x) > 1e-12:
            if x < 0:
                v = [-x for x in v]
            break
    m = max(abs(x) for x in v)
    v = tuple(round(x / m, 10) for x in v)
    return v


def real_dot(v1, v2):
    return sum(a * b for a, b in zip(v1, v2))


def generate_real_rays(alphabet):
    """Generate all distinct rays from a real coordinate alphabet in 3D."""
    rays_set = set()
    rays_list = []
    for combo in itertools.product(alphabet, repeat=3):
        canon = canonicalize_real_ray(combo)
        if canon is not None and canon not in rays_set:
            rays_set.add(canon)
            rays_list.append(combo)
    return rays_list


def real_orthog_pairs(vectors, tol=1e-9):
    n = len(vectors)
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            if abs(real_dot(vectors[i], vectors[j])) < tol:
                pairs.append((i, j))
    return pairs


def real_triads(vectors, pairs):
    pair_set = set(pairs)
    triads = []
    n = len(vectors)
    for i in range(n):
        for j in range(i + 1, n):
            if (i, j) not in pair_set:
                continue
            for k in range(j + 1, n):
                if (i, k) in pair_set and (j, k) in pair_set:
                    triads.append((i, j, k))
    return triads


def real_is_uncolorable(vectors):
    """Check KS-uncolorability for real vectors."""
    n = len(vectors)
    pairs = real_orthog_pairs(vectors)
    triads = real_triads(vectors, pairs)
    if not triads:
        return False, 0, 0, []
    if HAS_SAT:
        unc = sat_uncolorable(n, pairs, triads)
    else:
        unc = not complex_is_colorable(
            [tuple(complex(x) for x in v) for v in vectors])
    return unc, len(pairs), len(triads), triads


def cross_product_completion(rays, alphabet_rays, tol=1e-9):
    """
    Complete a ray set by adding cross products of orthogonal pairs.
    Returns the expanded ray list.
    """
    rays_set = set()
    for r in rays:
        c = canonicalize_real_ray(r)
        if c:
            rays_set.add(c)

    expanded = list(rays)
    changed = True
    iterations = 0
    while changed and iterations < 10:
        changed = False
        iterations += 1
        n = len(expanded)
        for i in range(n):
            for j in range(i + 1, n):
                if abs(real_dot(expanded[i], expanded[j])) < tol:
                    cross = (
                        expanded[i][1] * expanded[j][2] - expanded[i][2] * expanded[j][1],
                        expanded[i][2] * expanded[j][0] - expanded[i][0] * expanded[j][2],
                        expanded[i][0] * expanded[j][1] - expanded[i][1] * expanded[j][0],
                    )
                    norm = math.sqrt(sum(x * x for x in cross))
                    if norm < tol:
                        continue
                    cross = tuple(x / norm for x in cross)
                    canon = canonicalize_real_ray(cross)
                    if canon and canon not in rays_set:
                        rays_set.add(canon)
                        expanded.append(cross)
                        changed = True
    return expanded


# ============================================================
# Experiment 1: Attractor analysis
# ============================================================

def experiment_attractor():
    """
    Show that any alphabet containing xy=2 collapses to CK-31
    under cross-product completion.

    Test the family {0, ±1, ±t, ±2/t} for various t.
    After completion, check if the pool contains all CK-31 vectors
    and what the minimum KS set size is.
    """
    print("\n" + "=" * 60)
    print("EXPERIMENT 1: Attractor Analysis (xy=2 family)")
    print("Alphabet: {0, ±1, ±t, ±2/t}, varying t")
    print("=" * 60)

    # CK-31 canonical rays for checking containment
    CK31 = [
        (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 1, -1), (0, 1, 2), (0, 2, -1),
        (1, 0, 0), (1, 0, 1), (1, 0, -1), (1, 0, 2), (1, 0, -2),
        (1, 1, 0), (1, 1, 1), (1, 1, -1), (1, 1, 2), (1, -1, 0),
        (1, -1, 1), (1, -1, -1), (1, -1, -2), (1, 2, 0), (1, 2, -1),
        (1, -2, 0), (1, -2, 1), (2, 0, 1), (2, 0, -1), (2, 1, 0),
        (2, 1, 1), (2, 1, -1), (2, -1, 0), (2, -1, 1), (2, -1, -1)
    ]
    ck31_canonical = set()
    for v in CK31:
        c = canonicalize_real_ray(v)
        if c:
            ck31_canonical.add(c)

    t_values = [
        ('sqrt(2)', math.sqrt(2)),
        ('sqrt(3)', math.sqrt(3)),
        ('phi', (1 + math.sqrt(5)) / 2),
        ('cbrt(4)', 4 ** (1 / 3)),
        ('sqrt(5)', math.sqrt(5)),
        ('3/2', 1.5),
        ('pi/2', math.pi / 2),
        ('e/2', math.e / 2),
    ]

    for name, t in t_values:
        s = 2.0 / t
        alphabet = [0, 1, -1, t, -t, s, -s]
        rays = generate_real_rays(alphabet)
        n_before = len(rays)

        # Complete via cross products
        completed = cross_product_completion(rays, rays)
        n_after = len(completed)

        # Check CK-31 containment
        completed_canonical = set()
        for v in completed:
            c = canonicalize_real_ray(v)
            if c:
                completed_canonical.add(c)

        ck31_in_pool = sum(1 for c in ck31_canonical if c in completed_canonical)

        # Test colorability
        unc, n_pairs, n_triads, _ = real_is_uncolorable(completed)

        # If uncolorable, try to minimize
        min_str = '--'
        if unc:
            # Quick minimize using complex solver
            cvecs = [tuple(complex(x) for x in v) for v in completed]
            _, best_size, _ = complex_minimize(cvecs, num_trials=100, verbose=False)
            min_str = str(best_size)

        print(f"  t={name:10s}: {n_before:3d} -> {n_after:3d} rays, "
              f"{n_pairs:3d}p, {n_triads:3d}t, "
              f"CK31: {ck31_in_pool}/31, "
              f"{'UNCOLORABLE' if unc else 'colorable':11s}, min: {min_str}")


# ============================================================
# Experiment 2: Novel quadratic fields
# ============================================================

def experiment_quadratic_fields():
    """
    Systematic scan: alphabet {0, ±1, ±√d} for d = 2..30.
    Which quadratic fields produce KS sets?
    """
    print("\n" + "=" * 60)
    print("EXPERIMENT 2: Quadratic Fields {0, +/-1, +/-sqrt(d)}")
    print("=" * 60)

    for d in range(2, 31):
        x = math.sqrt(d)
        # Skip if x is (close to) an integer — reduces to integer alphabet
        if abs(x - round(x)) < 1e-10:
            continue

        alphabet = [0, 1, -1, x, -x]
        rays = generate_real_rays(alphabet)
        pairs = real_orthog_pairs(rays)
        triads = real_triads(rays, pairs)

        if not triads:
            print(f"  d={d:2d} (√{d:2d}={x:.4f}): {len(rays):3d} rays, "
                  f"{len(pairs):3d}p, {len(triads):2d}t — no triads")
            continue

        # Test the cancellation identity: what equation does √d satisfy?
        # Products: 1·1=1, 1·√d=√d, √d·√d=d
        # Cancellations: d = a + b where a,b ∈ {1, √d, d}
        # d = 1 + (d-1): works if d-1 ∈ {1, √d, d}
        #   d-1=1 → d=2 (√2)
        #   d-1=√d → d=φ² → d≈2.618 (not integer)
        #   d-1=d → impossible
        # 1 + 1 = d: d=2
        # √d + √d = d: 2√d=d → d=4 (integer, skip)

        cancel = "unknown"
        if d == 2:
            cancel = "d=1+1"
        elif abs(d - 1 - x) < 1e-6:
            cancel = f"d=1+√d"
        elif abs(2 * x - d) < 1e-6:
            cancel = f"d=2√d"

        unc = False
        min_str = '--'
        if triads:
            cvecs = [tuple(complex(c) for c in v) for v in rays]
            colorable = complex_is_colorable(cvecs)
            unc = not colorable
            if unc:
                _, best_size, _ = complex_minimize(cvecs, num_trials=200,
                                                    verbose=False)
                min_str = str(best_size)

        status = "UNCOLORABLE" if unc else "colorable"
        print(f"  d={d:2d} (√{d:2d}={x:.4f}): {len(rays):3d} rays, "
              f"{len(pairs):3d}p, {len(triads):2d}t — {status:11s} min: {min_str}  "
              f"[{cancel}]")


# ============================================================
# Experiment 3: xy=2 generalized (non-square-root families)
# ============================================================

def experiment_product_families():
    """
    For the identity xy = k (k = 2, 3, 4, 5), test alphabets
    {0, ±1, ±t, ±k/t} for various t. Do any k > 2 produce
    different KS behavior?
    """
    print("\n" + "=" * 60)
    print("EXPERIMENT 3: Product Families (xy = k)")
    print("=" * 60)

    for k in [2, 3, 5]:
        print(f"\n  --- xy = {k} ---")
        for t_name, t in [('sqrt2', math.sqrt(2)),
                          ('sqrt3', math.sqrt(3)),
                          ('phi', (1 + math.sqrt(5)) / 2),
                          ('2', 2.0),
                          ('3', 3.0)]:
            s = k / t
            if abs(t - s) < 0.01:
                label = f"t={t_name} (t=k/t)"
            else:
                label = f"t={t_name}"

            alphabet = [0, 1, -1, t, -t, s, -s]
            rays = generate_real_rays(alphabet)
            pairs = real_orthog_pairs(rays)
            triads = real_triads(rays, pairs)

            if not triads:
                print(f"    {label:20s}: {len(rays):3d} rays, 0 triads")
                continue

            cvecs = [tuple(complex(c) for c in v) for v in rays]
            colorable = complex_is_colorable(cvecs)
            unc = not colorable
            min_str = '--'
            if unc:
                _, best_size, _ = complex_minimize(cvecs, num_trials=100,
                                                    verbose=False)
                min_str = str(best_size)

            print(f"    {label:20s}: {len(rays):3d} rays, "
                  f"{len(pairs):3d}p, {len(triads):2d}t, "
                  f"{'UNC' if unc else 'col':3s}, min: {min_str}")


# ============================================================
# Experiment 4: Icosahedral rays
# ============================================================

def experiment_icosahedral():
    """
    Generate all symmetry-axis directions of the icosahedron and test
    for KS-uncolorability. The icosahedral group is the largest finite
    subgroup of SO(3), but lacks 90° rotations.

    Key question: do icosahedral orthogonalities exist at all?
    """
    print("\n" + "=" * 60)
    print("EXPERIMENT 4: Icosahedral Symmetry Rays")
    print("=" * 60)

    phi = (1 + math.sqrt(5)) / 2

    # Icosahedron vertices (6 rays):
    ico_vertices = [
        (0, 1, phi), (0, 1, -phi),
        (1, phi, 0), (1, -phi, 0),
        (phi, 0, 1), (phi, 0, -1),
    ]

    # Icosahedron edge midpoints (15 rays):
    # Edges connect vertices at distance 2. Generate all edges,
    # take midpoints, canonicalize.
    all_verts = [
        (0, 1, phi), (0, -1, phi), (0, 1, -phi), (0, -1, -phi),
        (1, phi, 0), (-1, phi, 0), (1, -phi, 0), (-1, -phi, 0),
        (phi, 0, 1), (-phi, 0, 1), (phi, 0, -1), (-phi, 0, -1),
    ]

    edge_mids_set = set()
    edge_mids = []
    edge_dist = 2.0  # distance between adjacent icosahedron vertices
    for i in range(len(all_verts)):
        for j in range(i + 1, len(all_verts)):
            vi, vj = all_verts[i], all_verts[j]
            d = math.sqrt(sum((a - b) ** 2 for a, b in zip(vi, vj)))
            if abs(d - edge_dist) < 0.01:
                mid = tuple((a + b) / 2 for a, b in zip(vi, vj))
                c = canonicalize_real_ray(mid)
                if c and c not in edge_mids_set:
                    edge_mids_set.add(c)
                    edge_mids.append(mid)

    # Icosahedron face centers (10 rays):
    # Faces are equilateral triangles. Find all triples of adjacent vertices.
    face_centers_set = set()
    face_centers = []
    for i in range(len(all_verts)):
        for j in range(i + 1, len(all_verts)):
            di = math.sqrt(sum((a - b) ** 2 for a, b in zip(all_verts[i], all_verts[j])))
            if abs(di - edge_dist) > 0.01:
                continue
            for k in range(j + 1, len(all_verts)):
                dj = math.sqrt(sum((a - b) ** 2 for a, b in zip(all_verts[i], all_verts[k])))
                dk = math.sqrt(sum((a - b) ** 2 for a, b in zip(all_verts[j], all_verts[k])))
                if abs(dj - edge_dist) < 0.01 and abs(dk - edge_dist) < 0.01:
                    center = tuple((all_verts[i][m] + all_verts[j][m] + all_verts[k][m]) / 3
                                   for m in range(3))
                    c = canonicalize_real_ray(center)
                    if c and c not in face_centers_set:
                        face_centers_set.add(c)
                        face_centers.append(center)

    all_rays = ico_vertices + edge_mids + face_centers
    print(f"  Icosahedral rays: {len(ico_vertices)} vertex + "
          f"{len(edge_mids)} edge + {len(face_centers)} face = "
          f"{len(all_rays)} total")

    # Find orthogonal pairs
    pairs = real_orthog_pairs(all_rays, tol=1e-6)
    triads = real_triads(all_rays, pairs)

    print(f"  Orthogonal pairs: {len(pairs)}")
    print(f"  Triads: {len(triads)}")

    if pairs:
        print(f"  Orthogonal pairs found:")
        for i, j in pairs[:10]:
            vi = tuple(round(x, 4) for x in all_rays[i])
            vj = tuple(round(x, 4) for x in all_rays[j])
            dot = real_dot(all_rays[i], all_rays[j])
            print(f"    {vi} · {vj} = {dot:.6f}")

    if not triads:
        print(f"\n  No triads — icosahedral symmetry CANNOT produce KS sets.")
        print(f"  Reason: the icosahedral group lacks 90° rotations.")
        print(f"  Its rotation orders are 2, 3, 5 (angles 180°, 120°, 72°).")
        print(f"  None of these produce orthogonal pairs within orbits.")
    else:
        unc, _, _, _ = real_is_uncolorable(all_rays)
        print(f"  Uncolorable: {unc}")

    # Also test: icosahedral rays + cross-product completion
    print(f"\n  After cross-product completion:")
    completed = cross_product_completion(all_rays, all_rays, tol=1e-6)
    print(f"  {len(all_rays)} -> {len(completed)} rays")
    if len(completed) > len(all_rays):
        pairs2 = real_orthog_pairs(completed, tol=1e-6)
        triads2 = real_triads(completed, pairs2)
        print(f"  Pairs: {len(pairs2)}, Triads: {len(triads2)}")
        if triads2:
            unc2, _, _, _ = real_is_uncolorable(completed)
            print(f"  Uncolorable: {unc2}")


# ============================================================
# Experiment 5: Deep Eisenstein search
# ============================================================

def experiment_deep_eisenstein():
    """
    Push the Eisenstein search to larger coefficient bounds.
    Can we find a complex KS set with fewer than 33 vectors?
    """
    print("\n" + "=" * 60)
    print("EXPERIMENT 5: Deep Eisenstein Search")
    print("Looking for sub-33 complex KS sets in Z[omega]")
    print("=" * 60)

    from ks_complex import (
        generate_eisenstein_rays,
        analyze_ray_set,
        multi_trial_minimize,
        is_colorable,
    )

    configs = [
        (1, 3, 200),   # already tested: min 33
        (1, 4, 200),   # already tested: min 33
        (2, 4, 200),   # already tested: min 33
        (2, 5, 200),   # already tested: min 33
        (2, 7, 200),   # NEW: larger norm cutoff
        (3, 6, 100),   # NEW: larger coefficients
        (3, 7, 100),   # NEW
    ]

    for max_coeff, norm_cut, n_trials in configs:
        label = f"coeff={max_coeff}, |v|²≤{norm_cut}"
        t0 = time.time()
        rays = generate_eisenstein_rays(max_coeff, dim=3,
                                        norm_cutoff=norm_cut)
        t1 = time.time()

        if len(rays) > 3000:
            print(f"  {label}: {len(rays)} rays — too many, skipping")
            continue

        info = analyze_ray_set(rays)
        print(f"  {label}: {info['n']} rays, {info['pairs']}p, "
              f"{info['triads']}t ({t1-t0:.1f}s gen)", end='')

        if info['triads'] == 0:
            print(" — no triads")
            continue

        colorable = is_colorable(rays)
        if colorable:
            print(" — colorable")
            continue

        print(" — UNCOLORABLE!", end='')
        t2 = time.time()
        best, best_size, sizes = multi_trial_minimize(
            rays, num_trials=n_trials, verbose=False)
        t3 = time.time()

        print(f" min: {best_size} ({t3-t2:.1f}s)")

        if best_size < 33:
            print(f"    *** BELOW 33! New complex minimum: {best_size} ***")
        elif best_size == 33:
            print(f"    (matches known complex minimum)")

        # Show size distribution
        for size in sorted(sizes.keys()):
            count = sizes[size]
            print(f"      {size}: {count} ({100*count/n_trials:.0f}%)")


# ============================================================
# Experiment 6: Closure analysis — which fields are "closed"?
# ============================================================

def experiment_closure():
    """
    For each candidate number field, check whether cross-product
    completion generates coordinates outside the field (meaning the
    field "leaks" to a larger one, potentially collapsing to integers).

    A truly separate algebraic island must be CLOSED under cross products.
    """
    print("\n" + "=" * 60)
    print("EXPERIMENT 6: Cross-Product Closure Analysis")
    print("Which number fields are closed under completion?")
    print("=" * 60)

    s2 = math.sqrt(2)
    s3 = math.sqrt(3)
    s5 = math.sqrt(5)
    phi = (1 + s5) / 2

    fields = [
        ('Q (integers)', [0, 1, -1, 2, -2]),
        ('Q(√2)', [0, 1, -1, s2, -s2]),
        ('Q(√3)', [0, 1, -1, s3, -s3]),
        ('Q(√5)', [0, 1, -1, s5, -s5]),
        ('Q(φ)', [0, 1, -1, phi, -phi]),
        ('Q(√2,√3)', [0, 1, -1, s2, -s2, s3, -s3]),
        ('Q(2,√2)', [0, 1, -1, 2, -2, s2, -s2]),
        ('Q(2,√3)', [0, 1, -1, 2, -2, s3, -s3]),
    ]

    for name, alphabet in fields:
        rays = generate_real_rays(alphabet)
        n_before = len(rays)

        # Analyze the coordinate values present
        vals_before = set()
        for r in rays:
            for x in r:
                vals_before.add(round(abs(x), 8))

        # Complete
        completed = cross_product_completion(rays, rays, tol=1e-8)
        n_after = len(completed)

        # Analyze new coordinate values
        vals_after = set()
        for r in completed:
            for x in r:
                vals_after.add(round(abs(x), 8))

        new_vals = vals_after - vals_before

        # Check if 2 (or any integer > 1) appeared
        has_integer_ratio = any(
            abs(v - round(v)) < 1e-6 and round(v) > 1
            for v in vals_after
        )

        pairs = real_orthog_pairs(completed, tol=1e-8)
        triads = real_triads(completed, pairs)

        unc = False
        min_str = '--'
        if triads:
            cvecs = [tuple(complex(c) for c in v) for v in completed]
            colorable = complex_is_colorable(cvecs)
            unc = not colorable
            if unc:
                _, best_size, _ = complex_minimize(cvecs, num_trials=100,
                                                    verbose=False)
                min_str = str(best_size)

        closure_status = "CLOSED" if not new_vals else f"+{len(new_vals)} new values"
        leak_status = "LEAKS TO Z" if has_integer_ratio else "no integer leak"

        print(f"  {name:15s}: {n_before:3d}->{n_after:3d} rays, "
              f"{len(triads):3d}t, {closure_status:20s}, {leak_status:15s}, "
              f"{'UNC' if unc else 'col':3s} min:{min_str}")

        if new_vals and len(new_vals) <= 10:
            print(f"    New values: {sorted(new_vals)}")


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    np.random.seed(42)
    random.seed(42)

    print("=" * 60)
    print("ALGEBRAIC ISLAND SEARCH")
    print("Can any structure besides Z (integers) produce a sub-31 KS set?")
    print("=" * 60)

    # Run all experiments
    experiment_quadratic_fields()
    experiment_product_families()
    experiment_icosahedral()
    experiment_closure()
    experiment_attractor()

    # Deep Eisenstein is slow — run last
    experiment_deep_eisenstein()

    print("\n" + "=" * 60)
    print("ALGEBRAIC ISLAND ANALYSIS COMPLETE")
    print("=" * 60)
