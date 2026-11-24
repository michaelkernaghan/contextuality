"""
KS Set Search Tool
==================
Searches for small Kochen-Specker sets in 3D by generating rays from
coordinate alphabets and finding minimal uncolorable subsets.

The Peres 33-vector set uses alphabet {0, ±1, ±√2}.
Conway-Kochen reduced this to 31 vectors.
Can we find anything smaller?

Strategy:
1. Generate all rays from a coordinate alphabet
2. Canonicalize (remove duplicates up to scaling)
3. Build orthogonality graph and enumerate triads
4. Test colorability of the full set
5. If uncolorable, greedily minimize by removing non-critical rays
"""

import math
import itertools
import random
import time
from fractions import Fraction


# ============================================================
# Core solver (from ks_test.py)
# ============================================================

def dot_product(v1, v2):
    return sum(a * b for a, b in zip(v1, v2))


def build_orthogonality_matrix(vectors):
    n = len(vectors)
    P = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if abs(dot_product(vectors[i], vectors[j])) < 1e-10:
                P[i][j] = 1
                P[j][i] = 1
    return P


def find_triads(P, n):
    triads = []
    for i in range(n):
        for j in range(i + 1, n):
            if P[i][j] != 1:
                continue
            for k in range(j + 1, n):
                if P[i][k] == 1 and P[j][k] == 1:
                    triads.append((i, j, k))
    return triads


def propagate(C, P, triads, n):
    changed = True
    while changed:
        changed = False
        for i in range(n):
            if C[i] == 1:
                for j in range(i + 1, n):
                    if P[i][j] == 1:
                        if C[j] == 1:
                            return False  # two orthogonal greens
                        if C[j] == -1:
                            C[j] = 0
                            changed = True
        for triad in triads:
            vals = [C[triad[0]], C[triad[1]], C[triad[2]]]
            if vals.count(0) >= 3:
                return False
            if vals.count(1) >= 2:
                return False
            if vals.count(0) == 2 and vals.count(-1) == 1:
                for idx in triad:
                    if C[idx] == -1:
                        C[idx] = 1
                        changed = True
                        break
    return True


def solve(C, P, triads, n):
    if not propagate(C, P, triads, n):
        return False
    pick = -1
    for i in range(n):
        if C[i] == -1:
            pick = i
            break
    if pick == -1:
        for triad in triads:
            if sum(1 for idx in triad if C[idx] == 1) != 1:
                return False
        return True
    saved = C[:]
    C[pick] = 1
    if solve(C, P, triads, n):
        return True
    for i in range(n):
        C[i] = saved[i]
    C[pick] = 0
    if solve(C, P, triads, n):
        return True
    for i in range(n):
        C[i] = saved[i]
    return False


def is_colorable(vectors):
    n = len(vectors)
    if n == 0:
        return True
    P = build_orthogonality_matrix(vectors)
    triads = find_triads(P, n)
    if len(triads) == 0:
        return True
    C = [-1] * n
    return solve(C, P, triads, n)


# ============================================================
# Ray generation from alphabet
# ============================================================

def canonicalize_ray(v):
    """
    Canonicalize a ray: make first nonzero component positive,
    and normalize to remove scalar multiples.
    Returns a tuple suitable for hashing, or None if zero vector.
    """
    # Skip zero vector
    if all(abs(x) < 1e-12 for x in v):
        return None

    # Find first nonzero component
    for x in v:
        if abs(x) > 1e-12:
            if x < 0:
                v = tuple(-x for x in v)
            break

    # Normalize by dividing by the magnitude of the largest component
    # to get a canonical form
    m = max(abs(x) for x in v)
    v = tuple(x / m for x in v)

    # Round to avoid floating point issues
    v = tuple(round(x, 10) for x in v)
    return v


def generate_rays(alphabet):
    """Generate all distinct rays from a coordinate alphabet in 3D."""
    rays_set = set()
    rays_list = []

    for combo in itertools.product(alphabet, repeat=3):
        canon = canonicalize_ray(list(combo))
        if canon is not None and canon not in rays_set:
            rays_set.add(canon)
            rays_list.append(combo)  # keep original coordinates

    return rays_list


def analyze_ray_set(vectors, label=""):
    """Analyze a set of vectors: count pairs, triads, test colorability."""
    n = len(vectors)
    P = build_orthogonality_matrix(vectors)
    triads = find_triads(P, n)
    pairs = sum(sum(row) for row in P) // 2

    return {
        'n': n,
        'pairs': pairs,
        'triads': len(triads),
        'triad_list': triads,
        'P': P,
    }


# ============================================================
# Minimization: find critical KS subsets
# ============================================================

def minimize_ks_set(vectors, verbose=False):
    """
    Given an uncolorable set, greedily remove rays to find a
    minimal (critical) uncolorable subset.
    A set is critical if removing ANY single ray makes it colorable.
    """
    current = list(vectors)

    removed = True
    while removed:
        removed = False
        for i in range(len(current)):
            candidate = current[:i] + current[i+1:]
            if not is_colorable(candidate):
                current = candidate
                removed = True
                break

    return current


def minimize_ks_set_randomized(vectors, verbose=False):
    """
    Randomized greedy minimization: try removing rays in random order.
    Different removal orders can reach different local minima.
    """
    current = list(vectors)

    removed = True
    while removed:
        removed = False
        indices = list(range(len(current)))
        random.shuffle(indices)
        for i in indices:
            candidate = current[:i] + current[i+1:]
            if not is_colorable(candidate):
                current = candidate
                removed = True
                break

    return current


def multi_trial_minimize(vectors, num_trials=200, verbose=True):
    """
    Run many randomized minimization trials to find the smallest
    critical KS subset. Reports each time a new record is set.
    """
    best = None
    best_size = len(vectors)
    sizes_found = {}

    if verbose:
        print(f"  Running {num_trials} randomized minimization trials...")
        print(f"  Starting pool: {len(vectors)} vectors")

    for trial in range(num_trials):
        minimal = minimize_ks_set_randomized(vectors)
        size = len(minimal)

        sizes_found[size] = sizes_found.get(size, 0) + 1

        if size < best_size:
            best = minimal
            best_size = size
            if verbose:
                print(f"    Trial {trial+1}: NEW RECORD! {size} vectors")
        elif verbose and trial < 5:
            print(f"    Trial {trial+1}: {size} vectors")

    if verbose:
        print(f"\n  Size distribution across {num_trials} trials:")
        for size in sorted(sizes_found.keys()):
            count = sizes_found[size]
            print(f"    {size} vectors: {count} times ({100*count/num_trials:.0f}%)")

    return best, best_size, sizes_found


def search_alphabet(alphabet, label="", num_trials=200):
    """
    Full search pipeline for a given coordinate alphabet.
    Uses multi-trial randomized minimization.
    """
    print(f"\n{'='*60}")
    print(f"Alphabet: {label}")
    print(f"Values: {alphabet}")
    print(f"{'='*60}")

    t0 = time.time()
    rays = generate_rays(alphabet)
    info = analyze_ray_set(rays)

    print(f"  Generated {info['n']} distinct rays")
    print(f"  Orthogonal pairs: {info['pairs']}")
    print(f"  Orthogonal triads: {info['triads']}")

    if info['triads'] == 0:
        print(f"  No triads found - cannot produce KS set.")
        return None

    t1 = time.time()
    colorable = is_colorable(rays)
    t2 = time.time()

    if colorable:
        print(f"  Full set is COLORABLE - no KS set here.")
        print(f"  (tested in {t2-t1:.2f}s)")
        return None
    else:
        print(f"  Full set is UNCOLORABLE! (tested in {t2-t1:.2f}s)")

    t3 = time.time()
    best, best_size, sizes = multi_trial_minimize(rays, num_trials=num_trials)
    t4 = time.time()

    info2 = analyze_ray_set(best)
    print(f"\n  BEST RESULT: {info2['n']}-vector KS set")
    print(f"    Pairs: {info2['pairs']}, Triads: {info2['triads']}")
    print(f"    Search took {t4-t3:.1f}s")
    print(f"    Vectors:")
    for i, v in enumerate(best):
        coords = tuple(round(x, 4) for x in v)
        print(f"      {i+1}: {coords}")

    return best

    return rays


# ============================================================
# Predefined alphabets
# ============================================================

S2 = math.sqrt(2)
S3 = math.sqrt(3)

ALPHABETS = {
    'peres': {
        'label': 'Peres {0, +/-1, +/-sqrt(2)}',
        'values': [0, 1, -1, S2, -S2],
    },
    'integer_2': {
        'label': 'Integer {0, ±1, ±2}',
        'values': [0, 1, -1, 2, -2],
    },
    'sqrt3': {
        'label': '{0, +/-1, +/-sqrt(3)}',
        'values': [0, 1, -1, S3, -S3],
    },
    'extended': {
        'label': '{0, +/-1, +/-sqrt(2), +/-2}',
        'values': [0, 1, -1, S2, -S2, 2, -2],
    },
    'golden': {
        'label': '{0, +/-1, +/-phi} where phi=(1+sqrt(5))/2',
        'values': [0, 1, -1, (1+math.sqrt(5))/2, -(1+math.sqrt(5))/2],
    },
    'small': {
        'label': 'Minimal {0, ±1}',
        'values': [0, 1, -1],
    },
}


if __name__ == "__main__":
    print("KS Set Search Tool")
    print("Searching for small Kochen-Specker sets in 3D")
    print("Current record: 31 vectors (Conway-Kochen)")

    # ============================================================
    # Phase 1: Verify the Conway-Kochen 31-vector set
    # ============================================================
    CK_31 = [
        (1, 0, 0), (0, 1, 0), (0, 0, 1),
        (1, 1, 0), (-1, 1, 0), (1, 0, 1), (1, 0, -1),
        (0, 1, 1), (0, -1, 1),
        (-2, 1, 0), (1, 2, 0), (2, 0, 1), (-2, 0, 1),
        (1, 1, 1), (-1, 1, 1), (1, -1, 1), (1, 1, -1),
        (0, 2, 1), (0, -2, 1), (1, 0, 2), (1, 0, -2),
        (0, 1, 2), (0, 1, -2),
        (-2, 1, 1), (2, -1, 1), (1, 2, 1), (1, 2, -1),
        (1, 1, 2), (-1, 1, 2), (1, -1, 2), (1, 1, -2),
    ]
    print("\n" + "=" * 60)
    print("VERIFICATION: Conway-Kochen 31-vector set")
    print("=" * 60)
    info = analyze_ray_set(CK_31)
    print(f"  Rays: {info['n']}, Pairs: {info['pairs']}, Triads: {info['triads']}")

    # Show all triads for debugging
    print(f"  Triads:")
    for t in info['triad_list']:
        v0, v1, v2 = CK_31[t[0]], CK_31[t[1]], CK_31[t[2]]
        print(f"    {t}: {v0}, {v1}, {v2}")

    colorable = is_colorable(CK_31)
    print(f"  Colorable: {colorable}")

    if colorable:
        # Show the coloring found - helps debug
        n = len(CK_31)
        P = build_orthogonality_matrix(CK_31)
        triads = find_triads(P, n)
        C = [-1] * n
        solve(C, P, triads, n)
        green = [i+1 for i in range(n) if C[i] == 1]
        red = [i+1 for i in range(n) if C[i] == 0]
        uncolored = [i+1 for i in range(n) if C[i] == -1]
        print(f"  Green rays: {green}")
        print(f"  Red rays: {red}")
        if uncolored:
            print(f"  Uncolored: {uncolored}")

        # Check: how many rays are NOT in any triad?
        in_triad = set()
        for t in triads:
            in_triad.update(t)
        not_in_triad = [i+1 for i in range(n) if i not in in_triad]
        print(f"  Rays NOT in any triad: {not_in_triad}")
        print(f"  ({len(not_in_triad)} unconstrained rays out of {n})")
        print()
        print("  WARNING: CK-31 tested COLORABLE - coordinates may be incorrect.")
        print("  The real CK-31 should be uncolorable. Investigating...")

        # Let's check how many of CK-31's rays are in our integer alphabet pool
        int_rays = generate_rays([0, 1, -1, 2, -2])
        int_canon = set()
        for r in int_rays:
            c = canonicalize_ray(list(r))
            if c:
                int_canon.add(c)
        print(f"\n  Integer alphabet has {len(int_canon)} canonical rays")
        missing = []
        for i, v in enumerate(CK_31):
            c = canonicalize_ray(list(v))
            if c not in int_canon:
                missing.append((i+1, v))
        if missing:
            print(f"  CK-31 rays NOT in integer alphabet: {missing}")
        else:
            print("  All CK-31 rays are in the integer alphabet pool.")

    # ============================================================
    # Phase 2: Broader alphabet search
    # ============================================================
    print("\n\n" + "=" * 60)
    print("ALPHABET SEARCH")
    print("=" * 60)
    # Deep search on integer alphabet (best performer)
    result = search_alphabet(
        ALPHABETS['integer_2']['values'],
        ALPHABETS['integer_2']['label'],
        num_trials=1000,
    )
