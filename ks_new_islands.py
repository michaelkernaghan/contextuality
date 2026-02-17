"""
ks_new_islands.py -- Search for new algebraic islands
=====================================================

Systematic exploration of untested algebraic structures that might
support KS sets in C^3 or R^3.

Candidates:
1. Gaussian integers Z[i] with enriched alphabets (not just roots of unity)
2. Other complex quadratic rings: Z[sqrt(-2)], Z[sqrt(-5)], etc.
3. Mixed complex fields: Z[i, sqrt(2)], Z[omega, sqrt(2)]
4. Cubic extensions: Z[cbrt(2)]
5. Silver ratio and other metallic means
6. Ring-of-integers generators for d = 1 mod 4 (complex quadratics)
"""

import cmath
import itertools
import math
import random
import time

from ks_complex import (
    is_colorable,
    analyze_ray_set,
    canonicalize_complex_ray,
    hermitian_dot,
    multi_trial_minimize,
    build_orthogonality_matrix,
    find_triads,
)

try:
    from ks_sat import is_uncolorable as sat_uncolorable
    HAS_SAT = True
except ImportError:
    HAS_SAT = False


def sat_minimize(rays, pairs, triads, n_trials=200):
    """SAT-based randomized greedy minimization. Much faster than backtracking."""
    n = len(rays)
    best_size = n
    best_subset = list(range(n))
    sizes = {}

    for trial in range(n_trials):
        current = list(range(n))
        random.shuffle(current)
        removed = True
        while removed:
            removed = False
            order = list(current)
            random.shuffle(order)
            for r in order:
                candidate = [x for x in current if x != r]
                if len(candidate) < 3:
                    break
                # Rebuild pairs/triads for subset
                s = set(candidate)
                remap = {old: new for new, old in enumerate(sorted(candidate))}
                sp = [(remap[a], remap[b]) for a, b in pairs if a in s and b in s]
                st = [(remap[a], remap[b], remap[c]) for a, b, c in triads
                      if a in s and b in s and c in s]
                if st and sat_uncolorable(len(candidate), sp, st):
                    current = candidate
                    removed = True
                    break

        size = len(current)
        sizes[size] = sizes.get(size, 0) + 1
        if size < best_size:
            best_size = size
            best_subset = current

    return best_subset, best_size, sizes


# ============================================================
# Generic ray generation from a complex alphabet
# ============================================================

def generate_rays_from_alphabet(alphabet, dim=3):
    """Generate all distinct rays from a complex alphabet in C^dim."""
    rays_set = set()
    rays_list = []
    for combo in itertools.product(alphabet, repeat=dim):
        canon = canonicalize_complex_ray(list(combo))
        if canon is not None and canon not in rays_set:
            rays_set.add(canon)
            rays_list.append(tuple(complex(x) for x in combo))
    return rays_list


def hermitian_completion(rays, max_iter=10, tol=1e-9):
    """
    Complete a complex ray set by adding Hermitian orthogonal complements.
    For each pair v, w with <v,w>=0 in C^3, the complement u has:
        u_k = (-1)^(k+1) * det([[conj(v_{k+1}), conj(v_{k+2})],
                                  [conj(w_{k+1}), conj(w_{k+2})]])
    """
    rays_set = set()
    for r in rays:
        c = canonicalize_complex_ray(list(r))
        if c:
            rays_set.add(c)

    expanded = list(rays)
    changed = True
    iteration = 0
    while changed and iteration < max_iter:
        changed = False
        iteration += 1
        n = len(expanded)
        new_rays = []
        for i in range(n):
            for j in range(i + 1, n):
                dot = hermitian_dot(expanded[i], expanded[j])
                if abs(dot) < tol:
                    # Compute Hermitian orthogonal complement
                    v = [complex(x).conjugate() for x in expanded[i]]
                    w = [complex(x).conjugate() for x in expanded[j]]
                    u = [0, 0, 0]
                    for k in range(3):
                        k1 = (k + 1) % 3
                        k2 = (k + 2) % 3
                        u[k] = ((-1) ** (k + 1)) * (v[k1] * w[k2] - v[k2] * w[k1])
                    if all(abs(x) < tol for x in u):
                        continue
                    canon = canonicalize_complex_ray(u)
                    if canon and canon not in rays_set:
                        rays_set.add(canon)
                        new_rays.append(tuple(complex(x) for x in u))
                        changed = True
        expanded.extend(new_rays)
    return expanded


def test_alphabet(name, alphabet, do_completion=False, n_trials=200):
    """Test a complex alphabet for KS-uncolorability. Uses SAT solver for speed."""
    t0 = time.time()
    rays = generate_rays_from_alphabet(alphabet)
    t1 = time.time()

    if do_completion:
        rays_before = len(rays)
        rays = hermitian_completion(rays)
        completion_str = f" -> {len(rays)} (completed from {rays_before})"
    else:
        completion_str = ""

    n_rays = len(rays)

    # Build orthogonality graph using Hermitian inner product
    pairs = []
    for i in range(n_rays):
        for j in range(i + 1, n_rays):
            dot = hermitian_dot(rays[i], rays[j])
            if abs(dot) < 1e-9:
                pairs.append((i, j))

    # Find triads
    pair_set = set(pairs)
    triads = []
    for i in range(n_rays):
        for j in range(i + 1, n_rays):
            if (i, j) not in pair_set:
                continue
            for k in range(j + 1, n_rays):
                if (i, k) in pair_set and (j, k) in pair_set:
                    triads.append((i, j, k))

    n_pairs = len(pairs)
    n_triads = len(triads)

    if n_triads == 0:
        print(f"  {name:40s}: {n_rays:4d} rays{completion_str}, "
              f"{n_pairs:4d}p, {n_triads:3d}t -- no triads")
        return False, None

    # Use SAT solver (fast!) if available, fallback to backtracking
    if HAS_SAT:
        unc = sat_uncolorable(n_rays, pairs, triads)
    else:
        unc = not is_colorable(rays)

    if not unc:
        print(f"  {name:40s}: {n_rays:4d} rays{completion_str}, "
              f"{n_pairs:4d}p, {n_triads:3d}t -- colorable")
        return False, None

    # Uncolorable! Try to minimize using SAT-based greedy removal
    if HAS_SAT:
        _, best_size, sizes = sat_minimize(rays, pairs, triads, n_trials=n_trials)
    else:
        _, best_size, sizes = multi_trial_minimize(rays, num_trials=n_trials, verbose=False)
    print(f"  {name:40s}: {n_rays:4d} rays{completion_str}, "
          f"{n_pairs:4d}p, {n_triads:3d}t -- UNCOLORABLE! min={best_size}")
    return True, best_size


# ============================================================
# Experiment 1: Gaussian integers Z[i] with enriched alphabets
# ============================================================

def experiment_gaussian():
    """
    Z[i] with alphabet {0, 1, i} is n=4 roots of unity -- colorable.
    But what about richer alphabets like {0, 1, i, 1+i}?
    The key identity: |1+i|^2 = 2, so (1+i)(1-i) = 2.
    This is the Gaussian analogue of the 2:1 ratio.
    """
    print("\n" + "=" * 60)
    print("EXPERIMENT 1: Gaussian Integers Z[i]")
    print("Key identity: (1+i)(1-i) = 2, |1+i|^2 = 2")
    print("=" * 60)

    I = 1j

    alphabets = [
        ("Z[i]: {0, +/-1, +/-i}",
         [0, 1, -1, I, -I]),
        ("Z[i]: {0, +/-1, +/-i, +/-(1+i)}",
         [0, 1, -1, I, -I, 1+I, -(1+I)]),
        ("Z[i]: {0, +/-1, +/-i, +/-(1+i), +/-(1-i)}",
         [0, 1, -1, I, -I, 1+I, -(1+I), 1-I, -(1-I)]),
        ("Z[i]: {0, 1, i, 1+i, 2}",
         [0, 1, -1, I, -I, 1+I, -(1+I), 1-I, -(1-I), 2, -2]),
        ("Z[i]: all |a+bi| <= sqrt(2)",
         [0, 1, -1, I, -I, 1+I, 1-I, -1+I, -1-I]),
    ]

    for name, alph in alphabets:
        if len(generate_rays_from_alphabet(alph)) > 5000:
            print(f"  {name:40s}: too many rays, skipping")
            continue
        test_alphabet(name, alph)

    # Also test with Hermitian completion
    print("\n  --- With Hermitian completion ---")
    for name, alph in alphabets[:3]:
        test_alphabet(name + " +compl", alph, do_completion=True)


# ============================================================
# Experiment 2: Complex quadratic rings Z[sqrt(-d)]
# ============================================================

def experiment_complex_quadratic():
    """
    Test Z[sqrt(-d)] for d = 2, 3, 5, 6, 7, ...
    d=1: Gaussian (Z[i]), d=3: Eisenstein (Z[omega]) -- both tested.
    What about d=2, 5, 6, 7?

    Cancellation identities:
    - sqrt(-2)^2 = -2, so a^2 + 2b^2 type norms
    - sqrt(-5)^2 = -5
    """
    print("\n" + "=" * 60)
    print("EXPERIMENT 2: Complex Quadratic Rings Z[sqrt(-d)]")
    print("=" * 60)

    for d in [2, 5, 6, 7, 10, 11, 13, 14, 15]:
        sd = cmath.sqrt(-d)

        # Basic alphabet: {0, +/-1, +/-sqrt(-d)}
        alph_basic = [0, 1, -1, sd, -sd]
        test_alphabet(f"Z[sqrt-{d}]: {{0, +/-1, +/-sqrt-{d}}}", alph_basic)

        # Enriched: add +/-(1 + sqrt(-d))
        alph_rich = alph_basic + [1 + sd, -(1 + sd), 1 - sd, -(1 - sd)]
        test_alphabet(f"Z[sqrt-{d}]: +{{+/-(1+/-sqrt-{d})}}", alph_rich)

    # For d = 3 mod 4, ring of integers uses (1+sqrt(-d))/2
    print("\n  --- Ring-of-integers generators (d = 3 mod 4) ---")
    for d in [3, 7, 11, 15, 19, 23]:
        gen = (1 + cmath.sqrt(-d)) / 2
        alph = [0, 1, -1, gen, -gen, gen.conjugate(), -gen.conjugate()]
        test_alphabet(f"Z[(1+sqrt-{d})/2]", alph)


# ============================================================
# Experiment 3: Mixed fields -- combine real + complex generators
# ============================================================

def experiment_mixed_fields():
    """
    Test alphabets mixing real irrationals with complex roots.
    E.g., {0, 1, i, sqrt(2)} or {0, 1, omega, sqrt(2)}.
    """
    print("\n" + "=" * 60)
    print("EXPERIMENT 3: Mixed Fields")
    print("=" * 60)

    I = 1j
    OMEGA = cmath.exp(2j * cmath.pi / 3)
    OMEGA2 = OMEGA * OMEGA
    s2 = math.sqrt(2)
    phi = (1 + math.sqrt(5)) / 2

    alphabets = [
        ("Z[i,sqrt2]: {0, +/-1, +/-i, +/-sqrt2}",
         [0, 1, -1, I, -I, s2, -s2]),
        ("Z[i,sqrt2]: {0, +/-1, +/-i, +/-sqrt2, +/-isqrt2}",
         [0, 1, -1, I, -I, s2, -s2, I*s2, -I*s2]),
        ("Z[w,sqrt2]: {0, 1, w, w^2, sqrt2}",
         [0, 1, OMEGA, OMEGA2, s2, -s2]),
        ("Z[w,sqrt2]: {0, +/-1, +/-w, +/-w^2, +/-sqrt2}",
         [0, 1, -1, OMEGA, -OMEGA, OMEGA2, -OMEGA2, s2, -s2]),
        ("Z[i,phi]: {0, +/-1, +/-i, +/-phi}",
         [0, 1, -1, I, -I, phi, -phi]),
        ("Z[w,phi]: {0, 1, w, w^2, phi}",
         [0, 1, OMEGA, OMEGA2, phi, -phi]),
    ]

    for name, alph in alphabets:
        rays = generate_rays_from_alphabet(alph)
        if len(rays) > 5000:
            print(f"  {name:40s}: {len(rays)} rays -- too many, skipping")
            continue
        test_alphabet(name, alph)


# ============================================================
# Experiment 4: Cubic extensions
# ============================================================

def experiment_cubic():
    """
    Test cubic field extensions: Z[cbrt(2)], Z[cbrt(3)], etc.
    Key identity: cbrt(2)^3 = 2. Does this give a useful
    three-term cancellation in C^3?
    """
    print("\n" + "=" * 60)
    print("EXPERIMENT 4: Cubic Extensions")
    print("=" * 60)

    for d in [2, 3, 4, 5]:
        cr = d ** (1/3)

        # Real cubic root
        alph = [0, 1, -1, cr, -cr]
        test_alphabet(f"Z[cbrt{d}]: {{0, +/-1, +/-cbrt{d}}}", alph)

        # With square too
        cr2 = cr * cr
        alph2 = [0, 1, -1, cr, -cr, cr2, -cr2]
        test_alphabet(f"Z[cbrt{d}]: +{{+/-(cbrt{d})^2}}", alph2)

    # Complex cube root of unity * real cubic root
    OMEGA = cmath.exp(2j * cmath.pi / 3)
    cr2 = 2 ** (1/3)
    alph_complex = [0, 1, complex(cr2), complex(cr2) * OMEGA, complex(cr2) * OMEGA**2]
    test_alphabet("Z[cbrt2, w]: splitting field", alph_complex)


# ============================================================
# Experiment 5: Metallic means
# ============================================================

def experiment_metallic():
    """
    Metallic means: sig_n = (n + sqrt(n^2+4))/2
    - n=1: golden ratio phi (KNOWN ISLAND)
    - n=2: silver ratio sig = 1+sqrt2 (same field as sqrt2, but different generator)
    - n=3: bronze ratio (3+sqrt13)/2
    """
    print("\n" + "=" * 60)
    print("EXPERIMENT 5: Metallic Means")
    print("=" * 60)

    for n in [2, 3, 4, 5]:
        sigma = (n + math.sqrt(n*n + 4)) / 2
        name_map = {2: "silver", 3: "bronze", 4: "copper", 5: "nickel"}
        name = name_map.get(n, f"sig_{n}")

        alph = [0, 1, -1, sigma, -sigma]
        test_alphabet(f"{name} sig={sigma:.4f}: {{0,+/-1,+/-sig}}", alph)

        # Also test 1/sigma
        inv = 1.0 / sigma
        alph2 = [0, 1, -1, sigma, -sigma, inv, -inv]
        test_alphabet(f"{name}: +{{+/-1/sig}}", alph2)


# ============================================================
# Experiment 6: Systematic complex completion search
# ============================================================

def experiment_completion_search():
    """
    The golden ratio island was only found via cross-product completion.
    Systematically test all basic complex alphabets WITH completion.
    """
    print("\n" + "=" * 60)
    print("EXPERIMENT 6: Completion Search (looking for hidden islands)")
    print("=" * 60)

    I = 1j

    # Test Gaussian with completion (this is the big one)
    alph_gauss = [0, 1, -1, I, -I, 1+I, -(1+I), 1-I, -(1-I)]
    test_alphabet("Z[i] full +compl", alph_gauss, do_completion=True, n_trials=100)

    # Test some complex quadratics with completion
    for d in [2, 5, 7]:
        sd = cmath.sqrt(-d)
        alph = [0, 1, -1, sd, -sd]
        rays = generate_rays_from_alphabet(alph)
        if len(rays) < 500:  # Only complete if manageable
            test_alphabet(f"Z[sqrt-{d}] +compl", alph, do_completion=True, n_trials=100)


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    random.seed(42)

    print("=" * 60)
    print("NEW ISLAND SEARCH")
    print("Looking for algebraic structures beyond the four known islands")
    print("=" * 60)

    experiment_gaussian()
    experiment_complex_quadratic()
    experiment_mixed_fields()
    experiment_cubic()
    experiment_metallic()
    experiment_completion_search()

    print("\n" + "=" * 60)
    print("NEW ISLAND SEARCH COMPLETE")
    print("=" * 60)
