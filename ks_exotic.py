"""
ks_exotic.py -- Test exotic cancellation identities beyond two-element alphabets
================================================================================

Explores multi-element alphabets from higher-degree number fields:

1. PLASTIC RATIO: rho^3 = rho + 1 (smallest Pisot number, rho ~ 1.3247)
   Alphabet: {0, +/-1, +/-rho, +/-rho^2}
   Cancellation: rho*rho^2 - 1*rho - 1*1 = 0 (minimal polynomial cancellation)

2. TRIBONACCI CONSTANT: tau^3 = tau^2 + tau + 1 (tau ~ 1.8393)
   Alphabet: {0, +/-1, +/-tau, +/-tau^2}

3. CLASS-NUMBER > 1 FIELDS: Z[sqrt(-5)] with extended alphabets
   Non-unique factorization: 2*3 = (1+sqrt(-5))(1-sqrt(-5))

4. PISOT NUMBER SURVEY: Plastic, supersilver, silver ratios

Requires: numpy, python-sat (optional)
"""

import numpy as np
import math
import itertools
import random
import time
from collections import defaultdict

# Import from existing tools
try:
    from ks_sat import is_uncolorable as sat_uncolorable
    HAS_SAT = True
except ImportError:
    HAS_SAT = False

try:
    from ks_complex import (
        is_colorable as complex_is_colorable,
        multi_trial_minimize as complex_minimize,
        canonicalize_complex_ray,
        hermitian_dot,
    )
    HAS_COMPLEX = True
except ImportError:
    HAS_COMPLEX = False


# ============================================================
# Constants
# ============================================================

# Plastic ratio: real root of x^3 - x - 1 = 0
PLASTIC = np.real(np.roots([1, 0, -1, -1])[0])  # ~ 1.32472

# Tribonacci constant: real root of x^3 - x^2 - x - 1 = 0
TRIBONACCI = np.real(np.roots([1, -1, -1, -1])[0])  # ~ 1.83929

print(f"Plastic ratio rho = {PLASTIC:.6f}")
print(f"  Verify: rho^3 - rho - 1 = {PLASTIC**3 - PLASTIC - 1:.2e}")
print(f"Tribonacci constant tau = {TRIBONACCI:.6f}")
print(f"  Verify: tau^3 - tau^2 - tau - 1 = {TRIBONACCI**3 - TRIBONACCI**2 - TRIBONACCI - 1:.2e}")


# ============================================================
# Real-valued tools (from ks_islands.py)
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
        return False, len(pairs), 0, []
    if HAS_SAT:
        unc = sat_uncolorable(n, pairs, triads)
    elif HAS_COMPLEX:
        unc = not complex_is_colorable(
            [tuple(complex(x) for x in v) for v in vectors])
    else:
        print("  WARNING: No SAT solver or complex solver available")
        return None, len(pairs), len(triads), triads
    return unc, len(pairs), len(triads), triads


def cross_product_completion(rays, tol=1e-9, max_iter=10):
    """Complete a ray set by adding cross products of orthogonal pairs."""
    rays_set = set()
    for r in rays:
        c = canonicalize_real_ray(r)
        if c:
            rays_set.add(c)

    expanded = list(rays)
    changed = True
    iterations = 0
    while changed and iterations < max_iter:
        changed = False
        iterations += 1
        n = len(expanded)
        new_rays = []
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
                        new_rays.append(cross)
                        changed = True
        expanded.extend(new_rays)
        if new_rays:
            print(f"    Completion iter {iterations}: +{len(new_rays)} rays (total {len(expanded)})")
    return expanded


def minimize_real(vectors, num_trials=200):
    """Greedy minimization for real vectors."""
    random.seed(42)
    n = len(vectors)
    best_size = n
    best_set = None
    sizes = []

    for trial in range(num_trials):
        current = list(range(n))
        order = list(range(n))
        random.shuffle(order)

        for idx in order:
            candidate = [i for i in current if i != idx]
            if len(candidate) < 3:
                break
            sub_vecs = [vectors[i] for i in candidate]
            unc, _, _, _ = real_is_uncolorable(sub_vecs)
            if unc:
                current = candidate

        sizes.append(len(current))
        if len(current) < best_size:
            best_size = len(current)
            best_set = current
            print(f"    Trial {trial+1}: new best = {best_size}")

    hist = defaultdict(int)
    for s in sizes:
        hist[s] += 1
    return best_set, best_size, dict(sorted(hist.items()))


def complex_ray_minimize(vectors, num_trials=200):
    """Minimize using ks_complex if available, else fall back to real."""
    if HAS_COMPLEX:
        cvecs = [tuple(complex(x) for x in v) for v in vectors]
        best_set, best_size, hist = complex_minimize(cvecs, num_trials=num_trials)
        return best_set, best_size, hist
    else:
        return minimize_real(vectors, num_trials=num_trials)


# ============================================================
# Experiment 1: Plastic Ratio
# ============================================================

def experiment_plastic_ratio():
    """
    Test the plastic ratio field Q(rho) where rho^3 = rho + 1.
    Cancellation identity: rho*rho^2 - rho - 1 = 0.
    """
    print("\n" + "=" * 60)
    print("EXPERIMENT 1: Plastic Ratio (rho ~ 1.3247)")
    print("  rho^3 = rho + 1  (cubic minimal polynomial cancellation)")
    print("=" * 60)

    rho = PLASTIC
    rho2 = rho ** 2

    # Verify cancellation identity
    dot_check = rho * rho2 - rho - 1  # should be 0
    print(f"  Cancellation check: rho*rho^2 - rho - 1 = {dot_check:.2e}")
    print(f"  Verify orthogonality: (rho, 1, 1).(rho^2, -rho, -1) = "
          f"{rho*rho2 + 1*(-rho) + 1*(-1):.2e}")

    # Basic alphabet
    alphabet_basic = [0, 1, -1, rho, -rho, rho2, -rho2]
    print(f"\n  Basic alphabet: {{0, +/-1, +/-rho, +/-rho^2}}")
    print(f"    rho = {rho:.6f}, rho^2 = {rho2:.6f}")

    rays = generate_real_rays(alphabet_basic)
    print(f"    Rays: {len(rays)}")

    pairs = real_orthog_pairs(rays)
    triads = real_triads(rays, pairs)
    print(f"    Orthogonal pairs: {len(pairs)}")
    print(f"    Triads: {len(triads)}")

    if triads:
        triads_per_ray = len(triads) / len(rays)
        print(f"    Triads/ray: {triads_per_ray:.3f}")

        unc, _, _, _ = real_is_uncolorable(rays)
        print(f"    KS-uncolorable: {unc}")

        if unc:
            print("    Minimizing...")
            _, best_size, hist = complex_ray_minimize(rays, num_trials=200)
            print(f"    Minimum KS set: {best_size}")
            print(f"    Size histogram: {hist}")
    else:
        print("    No triads -- cannot be KS-uncolorable")

    # Extended alphabet with rho+1 = rho^3
    rho3 = rho + 1
    alphabet_ext = [0, 1, -1, rho, -rho, rho2, -rho2, rho3, -rho3]
    print(f"\n  Extended alphabet: {{0, +/-1, +/-rho, +/-rho^2, +/-(rho+1)}}")
    print(f"    rho+1 = rho^3 = {rho3:.6f}")

    rays_ext = generate_real_rays(alphabet_ext)
    print(f"    Rays: {len(rays_ext)}")

    pairs_ext = real_orthog_pairs(rays_ext)
    triads_ext = real_triads(rays_ext, pairs_ext)
    print(f"    Orthogonal pairs: {len(pairs_ext)}")
    print(f"    Triads: {len(triads_ext)}")

    if triads_ext:
        print(f"    Triads/ray: {len(triads_ext) / len(rays_ext):.3f}")

        unc_ext, _, _, _ = real_is_uncolorable(rays_ext)
        print(f"    KS-uncolorable: {unc_ext}")

        if unc_ext:
            print("    Minimizing...")
            _, best_ext, hist_ext = complex_ray_minimize(rays_ext, num_trials=200)
            print(f"    Minimum KS set: {best_ext}")
            print(f"    Size histogram: {hist_ext}")
    else:
        print("    No triads -- cannot be KS-uncolorable")

    # Cross-product completion of basic alphabet
    print(f"\n  Cross-product completion of basic alphabet:")
    completed = cross_product_completion(rays)
    print(f"    Completed pool: {len(completed)} rays")

    if len(completed) > len(rays):
        pairs_c = real_orthog_pairs(completed)
        triads_c = real_triads(completed, pairs_c)
        print(f"    Orthogonal pairs: {len(pairs_c)}")
        print(f"    Triads: {len(triads_c)}")

        if triads_c:
            print(f"    Triads/ray: {len(triads_c) / len(completed):.3f}")
            unc_c, _, _, _ = real_is_uncolorable(completed)
            print(f"    KS-uncolorable: {unc_c}")

            if unc_c:
                print("    Minimizing (500 trials for larger pool)...")
                _, best_c, hist_c = complex_ray_minimize(completed, num_trials=500)
                print(f"    Minimum KS set: {best_c}")
                print(f"    Size histogram: {hist_c}")


# ============================================================
# Experiment 2: Tribonacci Constant
# ============================================================

def experiment_tribonacci():
    """
    Test the tribonacci field Q(tau) where tau^3 = tau^2 + tau + 1.
    """
    print("\n" + "=" * 60)
    print("EXPERIMENT 2: Tribonacci Constant (tau ~ 1.8393)")
    print("  tau^3 = tau^2 + tau + 1")
    print("=" * 60)

    tau = TRIBONACCI
    tau2 = tau ** 2

    # Check for three-term zero sums among products
    products = {
        '1*1': 1,
        '1*tau': tau,
        '1*tau^2': tau2,
        'tau*tau': tau2,
        'tau*tau^2': tau ** 3,  # = tau^2+tau+1
        'tau^2*tau^2': tau ** 4,  # = 2*tau^2+2*tau+1
    }
    print("  Product algebra:")
    for name, val in products.items():
        print(f"    {name} = {val:.6f}")

    # Search for three-term zero sums
    print("\n  Searching for three-term zero sums among products...")
    prod_list = list(products.items())
    found_any = False
    for i in range(len(prod_list)):
        for j in range(i, len(prod_list)):
            for k in range(j, len(prod_list)):
                vals = [prod_list[i][1], prod_list[j][1], prod_list[k][1]]
                # Check all sign combinations
                for signs in itertools.product([1, -1], repeat=3):
                    s = sum(si * vi for si, vi in zip(signs, vals))
                    if abs(s) < 1e-9:
                        names = [f"{'+' if si > 0 else '-'}{prod_list[idx][0]}"
                                 for si, idx in zip(signs, [i, j, k])]
                        print(f"    Zero sum: {' '.join(names)} = {s:.2e}")
                        found_any = True
    if not found_any:
        print("    No non-trivial three-term zero sums found among basic products")

    # Basic alphabet
    alphabet = [0, 1, -1, tau, -tau, tau2, -tau2]
    print(f"\n  Basic alphabet: {{0, +/-1, +/-tau, +/-tau^2}}")

    rays = generate_real_rays(alphabet)
    print(f"    Rays: {len(rays)}")

    pairs = real_orthog_pairs(rays)
    triads = real_triads(rays, pairs)
    print(f"    Orthogonal pairs: {len(pairs)}")
    print(f"    Triads: {len(triads)}")

    if triads:
        print(f"    Triads/ray: {len(triads) / len(rays):.3f}")
        unc, _, _, _ = real_is_uncolorable(rays)
        print(f"    KS-uncolorable: {unc}")

        if unc:
            print("    Minimizing...")
            _, best_size, hist = complex_ray_minimize(rays, num_trials=200)
            print(f"    Minimum KS set: {best_size}")
    else:
        print("    No triads -- cannot be KS-uncolorable")

    # Extended with tau^3 = tau^2+tau+1
    tau3 = tau2 + tau + 1
    alphabet_ext = [0, 1, -1, tau, -tau, tau2, -tau2, tau3, -tau3]
    print(f"\n  Extended alphabet: {{0, +/-1, +/-tau, +/-tau^2, +/-(tau^2+tau+1)}}")
    print(f"    tau^2+tau+1 = tau^3 = {tau3:.6f}")

    rays_ext = generate_real_rays(alphabet_ext)
    print(f"    Rays: {len(rays_ext)}")

    pairs_ext = real_orthog_pairs(rays_ext)
    triads_ext = real_triads(rays_ext, pairs_ext)
    print(f"    Orthogonal pairs: {len(pairs_ext)}")
    print(f"    Triads: {len(triads_ext)}")

    if triads_ext:
        print(f"    Triads/ray: {len(triads_ext) / len(rays_ext):.3f}")
        unc_ext, _, _, _ = real_is_uncolorable(rays_ext)
        print(f"    KS-uncolorable: {unc_ext}")

        if unc_ext:
            print("    Minimizing...")
            _, best_ext, hist_ext = complex_ray_minimize(rays_ext, num_trials=200)
            print(f"    Minimum KS set: {best_ext}")

    # Cross-product completion
    print(f"\n  Cross-product completion of basic alphabet:")
    completed = cross_product_completion(rays)
    print(f"    Completed pool: {len(completed)} rays")

    if len(completed) > len(rays):
        pairs_c = real_orthog_pairs(completed)
        triads_c = real_triads(completed, pairs_c)
        print(f"    Orthogonal pairs: {len(pairs_c)}")
        print(f"    Triads: {len(triads_c)}")
        if triads_c:
            print(f"    Triads/ray: {len(triads_c) / len(completed):.3f}")
            unc_c, _, _, _ = real_is_uncolorable(completed)
            print(f"    KS-uncolorable: {unc_c}")
            if unc_c:
                print("    Minimizing...")
                _, best_c, hist_c = complex_ray_minimize(completed, num_trials=500)
                print(f"    Minimum KS set: {best_c}")


# ============================================================
# Experiment 3: Class-number > 1 fields
# ============================================================

def experiment_class_gt1():
    """
    Test imaginary quadratic fields with class number > 1.
    Z[sqrt(-5)] has class number 2: non-unique factorization
    2*3 = (1+sqrt(-5))(1-sqrt(-5)) = 6
    """
    print("\n" + "=" * 60)
    print("EXPERIMENT 3: Class-number > 1 fields")
    print("  Z[sqrt(-5)], class number 2")
    print("=" * 60)

    sqrt5i = complex(0, math.sqrt(5))  # sqrt(-5) = i*sqrt(5)

    # Basic alphabet
    alpha = 1 + sqrt5i  # 1+sqrt(-5), |alpha|^2 = 6
    alpha_bar = 1 - sqrt5i
    print(f"  alpha = 1+sqrt(-5) = {alpha}")
    print(f"  |alpha|^2 = {abs(alpha)**2:.1f}")
    print(f"  Non-unique factorization: 2*3 = (1+sqrt(-5))(1-sqrt(-5)) = {alpha * alpha_bar:.1f}")

    # Need complex ray machinery
    if not HAS_COMPLEX:
        print("  SKIPPED: requires ks_complex.py")
        return

    alphabet_vals = [0, 1, -1, sqrt5i, -sqrt5i, alpha, -alpha, alpha_bar, -alpha_bar]
    print(f"\n  Alphabet: {{0, +/-1, +/-sqrt(-5), +/-(1+sqrt(-5)), +/-(1-sqrt(-5))}}")

    # Generate complex rays
    rays_set = set()
    rays_list = []
    for combo in itertools.product(alphabet_vals, repeat=3):
        canon = canonicalize_complex_ray(combo)
        if canon is not None and canon not in rays_set:
            rays_set.add(canon)
            rays_list.append(combo)

    print(f"    Rays: {len(rays_list)}")

    # Check colorability
    colorable = complex_is_colorable(rays_list)
    print(f"    Colorable: {colorable}")
    print(f"    KS-uncolorable: {not colorable}")

    if not colorable:
        print("    Minimizing...")
        _, best_size, hist = complex_minimize(rays_list, num_trials=200)
        print(f"    Minimum KS set: {best_size}")
        print(f"    Size histogram: {hist}")

    # Extended alphabet with (1+sqrt(-5))/2
    half_alpha = (1 + sqrt5i) / 2
    half_alpha_bar = (1 - sqrt5i) / 2
    alphabet_ext = alphabet_vals + [half_alpha, -half_alpha, half_alpha_bar, -half_alpha_bar]
    print(f"\n  Extended alphabet: add +/-(1+sqrt(-5))/2, +/-(1-sqrt(-5))/2")
    print(f"    (1+sqrt(-5))/2 = {half_alpha}, |(1+sqrt(-5))/2|^2 = {abs(half_alpha)**2:.2f}")

    rays_set2 = set()
    rays_list2 = []
    for combo in itertools.product(alphabet_ext, repeat=3):
        canon = canonicalize_complex_ray(combo)
        if canon is not None and canon not in rays_set2:
            rays_set2.add(canon)
            rays_list2.append(combo)

    print(f"    Rays: {len(rays_list2)}")

    colorable2 = complex_is_colorable(rays_list2)
    print(f"    Colorable: {colorable2}")
    print(f"    KS-uncolorable: {not colorable2}")

    if not colorable2:
        print("    Minimizing...")
        _, best_size2, hist2 = complex_minimize(rays_list2, num_trials=200)
        print(f"    Minimum KS set: {best_size2}")


# ============================================================
# Experiment 4: Supersilver ratio and other Pisot numbers
# ============================================================

def experiment_pisot():
    """
    Test other small Pisot-Vijayaraghavan numbers.
    These are algebraic integers > 1 whose conjugates all have |x| < 1.
    """
    print("\n" + "=" * 60)
    print("EXPERIMENT 4: Pisot Numbers")
    print("=" * 60)

    pisots = {
        'Plastic ratio': (PLASTIC, "rho^3 = rho + 1"),
        'Supersilver ratio': (np.real(np.roots([1, -2, 0, -1])[0]), "psi^3 = 2*psi^2 + 1"),
        'Silver ratio': (1 + math.sqrt(2), "delta = 1+sqrt(2), delta^2 = 2+2*sqrt(2) (degree 2)"),
    }

    for name, (val, identity) in pisots.items():
        print(f"\n  {name}: {val:.6f}")
        print(f"    Identity: {identity}")

        alphabet = [0, 1, -1, val, -val, val**2, -val**2]
        rays = generate_real_rays(alphabet)
        pairs = real_orthog_pairs(rays)
        triads = real_triads(rays, pairs)

        print(f"    Alphabet: {{0, +/-1, +/-x, +/-x^2}}")
        print(f"    Rays: {len(rays)}, Pairs: {len(pairs)}, Triads: {len(triads)}")

        if triads:
            print(f"    Triads/ray: {len(triads) / len(rays):.3f}")
            unc, _, _, _ = real_is_uncolorable(rays)
            print(f"    KS-uncolorable: {unc}")
            if unc:
                print("    Minimizing...")
                _, best_size, hist = complex_ray_minimize(rays, num_trials=200)
                print(f"    Minimum: {best_size}")
        else:
            print(f"    No triads -- not KS-viable")


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    t0 = time.time()

    experiment_plastic_ratio()
    experiment_tribonacci()
    experiment_pisot()

    # Class > 1 only if complex tools available
    if HAS_COMPLEX:
        experiment_class_gt1()
    else:
        print("\n  Skipping class-number > 1 experiment (requires ks_complex.py)")

    elapsed = time.time() - t0
    print(f"\n{'=' * 60}")
    print(f"Total elapsed: {elapsed:.1f}s")
    print(f"SAT solver: {'available' if HAS_SAT else 'NOT available'}")
    print(f"Complex solver: {'available' if HAS_COMPLEX else 'NOT available'}")
