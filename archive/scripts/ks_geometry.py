"""
ks_geometry.py — Geometry-first KS set search
===============================================
Build KS configurations from chains of orthogonal frames in R³,
exploring coordinates beyond any fixed alphabet.

The realizability gap showed that random abstract hypergraphs are almost
never realizable in R³. This script inverts the approach: build from
actual R³ geometry, guaranteeing realizability by construction.

Method:
  1. Start with a seed frame (orthonormal basis)
  2. Grow a tree of frames by rotating around shared axes
  3. Collect all rays, identify orthogonal pairs and triads
  4. Test KS-uncolorability
  5. If uncolorable, minimize to find the smallest KS subset

The rotation angles are continuous parameters — this searches
configurations invisible to any finite coordinate alphabet.

Requires: numpy, scipy, python-sat (optional, for fast SAT)
"""

import numpy as np
from scipy.optimize import minimize as scipy_min
from itertools import combinations
import time
import sys
import random
import math

# Import SAT checker from ks_sat.py if available
try:
    from ks_sat import is_uncolorable, check_realizability, build_graph
    HAS_SAT = True
except ImportError:
    HAS_SAT = False


# ============================================================
# Core geometry: rotations and frames
# ============================================================

def rodrigues_rotation(axis, angle):
    """
    Rotation matrix around unit vector `axis` by `angle` (radians).
    Rodrigues' formula: R = I + sin(θ)K + (1-cos(θ))K²
    where K is the skew-symmetric cross-product matrix of axis.
    """
    axis = np.asarray(axis, dtype=float)
    axis = axis / np.linalg.norm(axis)
    K = np.array([
        [0, -axis[2], axis[1]],
        [axis[2], 0, -axis[0]],
        [-axis[1], axis[0], 0]
    ])
    R = np.eye(3) + np.sin(angle) * K + (1 - np.cos(angle)) * (K @ K)
    return R


def random_frame():
    """Generate a random orthonormal frame (element of SO(3))."""
    # QR decomposition of random matrix gives uniform SO(3) element
    M = np.random.randn(3, 3)
    Q, R = np.linalg.qr(M)
    # Ensure det = +1 (SO(3), not O(3))
    Q = Q @ np.diag(np.sign(np.diag(R)))
    if np.linalg.det(Q) < 0:
        Q[:, 0] *= -1
    return Q  # columns are the three orthonormal rays


# ============================================================
# Ray management with tolerance-based identification
# ============================================================

class RayPool:
    """
    Manages a collection of rays (directions on S²).
    Rays that point in the same or opposite direction (within tolerance)
    are identified as the same ray.
    """

    def __init__(self, tol=1e-8):
        self.rays = []      # list of unit vectors (numpy arrays)
        self.tol = tol

    def add(self, v):
        """Add a ray, returning its index. Merges with existing if close."""
        v = np.asarray(v, dtype=float)
        v = v / np.linalg.norm(v)

        for i, r in enumerate(self.rays):
            # Check both v and -v (same ray = same projector)
            if np.linalg.norm(v - r) < self.tol or np.linalg.norm(v + r) < self.tol:
                return i

        idx = len(self.rays)
        self.rays.append(v)
        return idx

    def __len__(self):
        return len(self.rays)


# ============================================================
# Frame network builders
# ============================================================

def build_frame_tree(depth, branching, angle_source='random', seed_frame=None):
    """
    Build a tree of orthogonal frames by rotating around shared axes.

    Each frame is a triad (3 mutually orthogonal unit vectors).
    Child frames share one ray with their parent (the rotation axis).
    Additional interlocking occurs when rays from different branches coincide.

    Parameters:
        depth: tree depth (0 = just the root frame)
        branching: number of child frames per parent ray
        angle_source: 'random', 'grid', or a list of specific angles
        seed_frame: 3x3 orthogonal matrix (columns = rays), or None for identity

    Returns:
        pool: RayPool with all distinct rays
        triads: list of (i,j,k) index triples
    """
    pool = RayPool()
    triads = []

    if seed_frame is None:
        seed_frame = np.eye(3)

    # Add seed frame
    seed_indices = [pool.add(seed_frame[:, k]) for k in range(3)]
    triads.append(tuple(sorted(seed_indices)))

    # BFS queue: (frame_matrix, parent_depth)
    queue = [(seed_frame, 0)]

    while queue:
        frame, d = queue.pop(0)
        if d >= depth:
            continue

        # For each ray in this frame, create child frames by rotation
        for k in range(3):
            axis = frame[:, k]  # rotation axis (shared ray)

            if angle_source == 'random':
                angles = [random.uniform(0.1, np.pi - 0.1) for _ in range(branching)]
            elif angle_source == 'grid':
                angles = [np.pi * (i + 1) / (branching + 1) for i in range(branching)]
            elif isinstance(angle_source, (list, np.ndarray)):
                angles = angle_source[:branching]
            else:
                angles = [random.uniform(0.1, np.pi - 0.1) for _ in range(branching)]

            for angle in angles:
                R = rodrigues_rotation(axis, angle)
                child_frame = R @ frame

                # Add rays and record triad
                indices = [pool.add(child_frame[:, j]) for j in range(3)]
                t = tuple(sorted(indices))
                if t not in triads:
                    triads.append(t)

                queue.append((child_frame, d + 1))

    return pool, triads


def build_multi_root_network(n_roots, depth, branching, angle_source='random'):
    """
    Build from multiple seed frames that share one common ray.
    This creates a "star" topology where all roots connect through
    a central ray, then each root grows its own subtree.
    """
    pool = RayPool()
    triads = []

    # All seed frames share the z-axis
    z = np.array([0, 0, 1.0])
    pool.add(z)

    for i in range(n_roots):
        # Random angle around z-axis for this root frame
        phi = random.uniform(0, 2 * np.pi)
        x = np.array([np.cos(phi), np.sin(phi), 0.0])
        y = np.cross(z, x)

        frame = np.column_stack([x, y, z])
        indices = [pool.add(frame[:, k]) for k in range(3)]
        t = tuple(sorted(indices))
        if t not in triads:
            triads.append(t)

        # Grow subtree from this root
        sub_pool, sub_triads = build_frame_tree(
            depth, branching, angle_source, seed_frame=frame)

        # Merge into main pool
        remap = {}
        for j, ray in enumerate(sub_pool.rays):
            remap[j] = pool.add(ray)

        for st in sub_triads:
            remapped = tuple(sorted(remap[idx] for idx in st))
            if remapped not in triads:
                triads.append(remapped)

    return pool, triads


# ============================================================
# Orthogonality analysis
# ============================================================

def analyze_configuration(pool, triads, tol=1e-6):
    """
    Analyze a ray configuration: find all orthogonal pairs (including
    those not captured by the construction triads) and all triads.

    The construction guarantees some orthogonalities, but there may be
    additional "accidental" orthogonalities from the geometry.
    """
    n = len(pool)
    rays = pool.rays

    # Find ALL orthogonal pairs (not just those from construction triads)
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            if abs(np.dot(rays[i], rays[j])) < tol:
                pairs.append((i, j))

    pair_set = set(pairs)

    # Find ALL triads (complete orthogonal triples)
    all_triads = []
    for i in range(n):
        for j in range(i + 1, n):
            if (i, j) not in pair_set:
                continue
            for k in range(j + 1, n):
                if (i, k) in pair_set and (j, k) in pair_set:
                    all_triads.append((i, j, k))

    return pairs, all_triads


# ============================================================
# KS coloring (built-in fallback if ks_sat.py not available)
# ============================================================

def _backtrack_check(n, pairs, triads):
    """Check KS-uncolorability via backtracking."""
    P = [[0] * n for _ in range(n)]
    for a, b in pairs:
        P[a][b] = P[b][a] = 1

    def propagate(C):
        changed = True
        while changed:
            changed = False
            for i in range(n):
                if C[i] == 1:
                    for j in range(n):
                        if P[i][j]:
                            if C[j] == 1:
                                return False
                            if C[j] == -1:
                                C[j] = 0
                                changed = True
            for t in triads:
                v = [C[t[0]], C[t[1]], C[t[2]]]
                g, r = v.count(1), v.count(0)
                if g > 1 or r == 3:
                    return False
                if g == 1:
                    for idx in t:
                        if C[idx] == -1:
                            C[idx] = 0
                            changed = True
                if r == 2 and v.count(-1) == 1 and g == 0:
                    for idx in t:
                        if C[idx] == -1:
                            C[idx] = 1
                            changed = True
        return True

    def solve(C):
        C2 = C[:]
        if not propagate(C2):
            return False
        if -1 not in C2:
            return True
        best = max((sum(1 for j in range(n) if P[i][j] and C2[j] != -1), i)
                   for i in range(n) if C2[i] == -1)[1]
        for color in [1, 0]:
            C3 = C2[:]
            C3[best] = color
            if solve(C3):
                return True
        return False

    return not solve([-1] * n)


def check_uncolorable(n, pairs, triads):
    """Check KS-uncolorability, using SAT if available."""
    if HAS_SAT:
        return is_uncolorable(n, pairs, triads)
    return _backtrack_check(n, pairs, triads)


# ============================================================
# Greedy minimization
# ============================================================

def minimize_ks_set(n, rays, pairs, triads, num_trials=100, verbose=False):
    """
    Randomized greedy minimization: try removing rays in random order.
    Returns the smallest critical KS subset found.
    """
    best = None
    best_size = n

    for trial in range(num_trials):
        current_rays = list(range(n))
        random.shuffle(current_rays)

        removed = True
        while removed:
            removed = False
            candidates = list(current_rays)
            random.shuffle(candidates)
            for ray in candidates:
                subset = [r for r in current_rays if r != ray]
                if len(subset) < 4:  # need at least 4 rays for a triad pair
                    continue
                s = set(subset)
                remap = {old: new for new, old in enumerate(sorted(subset))}
                sp = [(remap[a], remap[b]) for a, b in pairs if a in s and b in s]
                st = [(remap[a], remap[b], remap[c]) for a, b, c in triads
                      if a in s and b in s and c in s]
                if st and check_uncolorable(len(subset), sp, st):
                    current_rays = subset
                    removed = True
                    break

        size = len(current_rays)
        if size < best_size:
            best_size = size
            best = current_rays
            if verbose:
                print(f"    Trial {trial+1}: NEW RECORD {size} rays")

    return best, best_size


# ============================================================
# Main search experiments
# ============================================================

def experiment_frame_tree(n_trials=500, depth=2, branching=2, verbose=True):
    """
    Experiment 1: Random frame trees.
    Grow trees of orthogonal frames and test for KS-uncolorability.
    """
    print(f"\n{'='*60}")
    print(f"EXPERIMENT: Frame Trees (depth={depth}, branching={branching})")
    print(f"{'='*60}")

    stats = {
        'tested': 0,
        'uncolorable': 0,
        'min_rays': float('inf'),
        'min_triads': 0,
        'min_pairs': 0,
        'best_config': None,
        'ray_counts': {},
        'unc_ray_counts': {},
    }

    t0 = time.time()

    for trial in range(n_trials):
        pool, construction_triads = build_frame_tree(depth, branching)
        pairs, all_triads = analyze_configuration(pool, construction_triads)
        n = len(pool)

        stats['tested'] += 1
        stats['ray_counts'][n] = stats['ray_counts'].get(n, 0) + 1

        if len(all_triads) < 2:
            continue

        unc = check_uncolorable(n, pairs, all_triads)

        if unc:
            stats['uncolorable'] += 1
            stats['unc_ray_counts'][n] = stats['unc_ray_counts'].get(n, 0) + 1

            if verbose and stats['uncolorable'] <= 5:
                print(f"  Trial {trial+1}: UNCOLORABLE! "
                      f"{n} rays, {len(pairs)} pairs, {len(all_triads)} triads")

            # Try to minimize
            best_subset, best_size = minimize_ks_set(
                n, pool.rays, pairs, all_triads, num_trials=50)

            if best_size < stats['min_rays']:
                stats['min_rays'] = best_size
                stats['min_triads'] = len(all_triads)
                stats['min_pairs'] = len(pairs)
                stats['best_config'] = (pool, best_subset, pairs, all_triads)
                if verbose:
                    print(f"    -> Minimized to {best_size} rays ***")
                    if best_size < 31:
                        print(f"    *** BELOW CK-31! THIS IS NEW! ***")

        if verbose and (trial + 1) % 100 == 0:
            dt = time.time() - t0
            print(f"  [{trial+1}/{n_trials}] {dt:.1f}s, "
                  f"{stats['uncolorable']} uncolorable, "
                  f"best minimal: {stats['min_rays']}")

    dt = time.time() - t0
    print(f"\n  Results ({dt:.1f}s):")
    print(f"    Tested: {stats['tested']}")
    print(f"    Uncolorable: {stats['uncolorable']}")
    if stats['uncolorable'] > 0:
        print(f"    Best minimal: {stats['min_rays']} rays")

    print(f"\n  Ray count distribution:")
    for n in sorted(stats['ray_counts'].keys()):
        c = stats['ray_counts'][n]
        u = stats.get('unc_ray_counts', {}).get(n, 0)
        print(f"    {n} rays: {c} configs, {u} uncolorable")

    return stats


def experiment_dense_star(n_trials=200, n_roots_range=(5, 15),
                          depth=1, branching=2, verbose=True):
    """
    Experiment 2: Dense star networks.
    Multiple root frames sharing a common axis, each with a small subtree.
    Maximizes interlocking through the shared axis.
    """
    print(f"\n{'='*60}")
    print(f"EXPERIMENT: Dense Star Networks")
    print(f"  n_roots: {n_roots_range}, depth={depth}, branching={branching}")
    print(f"{'='*60}")

    best_minimal = float('inf')
    best_config = None
    uncolorable_count = 0

    t0 = time.time()

    for trial in range(n_trials):
        n_roots = random.randint(*n_roots_range)
        pool, construction_triads = build_multi_root_network(
            n_roots, depth, branching)
        pairs, all_triads = analyze_configuration(pool, construction_triads)
        n = len(pool)

        if len(all_triads) < 2:
            continue

        unc = check_uncolorable(n, pairs, all_triads)

        if unc:
            uncolorable_count += 1
            if verbose and uncolorable_count <= 3:
                print(f"  Trial {trial+1}: UNCOLORABLE! "
                      f"{n} rays, {len(pairs)} pairs, {len(all_triads)} triads")

            best_subset, best_size = minimize_ks_set(
                n, pool.rays, pairs, all_triads, num_trials=30)

            if best_size < best_minimal:
                best_minimal = best_size
                best_config = (pool, best_subset, pairs, all_triads)
                if verbose:
                    print(f"    -> Minimized to {best_size} rays ***")
                    if best_size < 31:
                        print(f"    *** BELOW CK-31! THIS IS NEW! ***")

        if verbose and (trial + 1) % 50 == 0:
            dt = time.time() - t0
            print(f"  [{trial+1}/{n_trials}] {dt:.1f}s, "
                  f"{uncolorable_count} uncolorable, "
                  f"best minimal: {best_minimal}")

    dt = time.time() - t0
    print(f"\n  Results ({dt:.1f}s):")
    print(f"    Tested: {n_trials}")
    print(f"    Uncolorable: {uncolorable_count}")
    if uncolorable_count > 0:
        print(f"    Best minimal: {best_minimal} rays")

    return best_minimal, best_config


def experiment_angle_scan(n_trials=200, verbose=True):
    """
    Experiment 3: Systematic angle scan.
    Instead of random angles, scan specific angle families that
    might produce algebraically special configurations.

    Special angles to try:
    - pi/n for small n (creates n-fold symmetry)
    - arctan(k) for small integers k (creates integer-like coordinates)
    - arctan(sqrt(k)) (creates algebraic coordinates)
    """
    print(f"\n{'='*60}")
    print(f"EXPERIMENT: Angle Family Scan")
    print(f"{'='*60}")

    # Angle families that might produce interesting interlocking
    angle_families = {
        'pi/3': [np.pi / 3],
        'pi/4': [np.pi / 4],
        'pi/5': [np.pi / 5],
        'pi/6': [np.pi / 6],
        'arctan(1)': [np.arctan(1)],
        'arctan(2)': [np.arctan(2)],
        'arctan(1/2)': [np.arctan(0.5)],
        'arctan(sqrt2)': [np.arctan(np.sqrt(2))],
        'arctan(1)+arctan(2)': [np.arctan(1), np.arctan(2)],
        'pi/4+pi/3': [np.pi / 4, np.pi / 3],
        'pi/6+pi/4': [np.pi / 6, np.pi / 4],
        'pi/5+pi/3': [np.pi / 5, np.pi / 3],
    }

    results = {}

    for name, angles in angle_families.items():
        best_minimal = float('inf')
        unc_count = 0
        tested = 0

        for trial in range(n_trials):
            # Use these specific angles with some depth variation
            d = random.choice([2, 3])
            b = len(angles)

            pool, construction_triads = build_frame_tree(
                d, b, angle_source=angles)
            pairs, all_triads = analyze_configuration(pool, construction_triads)
            n = len(pool)
            tested += 1

            if len(all_triads) < 2:
                continue

            unc = check_uncolorable(n, pairs, all_triads)
            if unc:
                unc_count += 1
                best_subset, best_size = minimize_ks_set(
                    n, pool.rays, pairs, all_triads, num_trials=30)
                if best_size < best_minimal:
                    best_minimal = best_size

        rate = f"{100*unc_count/tested:.0f}%" if tested > 0 else "N/A"
        min_str = str(best_minimal) if best_minimal < float('inf') else '--'
        results[name] = (tested, unc_count, best_minimal)

        if verbose:
            print(f"  {name:25s}: {unc_count:3d}/{tested:3d} uncolorable ({rate}), "
                  f"best minimal: {min_str}")

    return results


def build_from_orthogonal_completion(n_seed=10, max_iterations=20, tol=1e-8):
    """
    Pool-based frame construction that maximizes ray reuse.

    Instead of growing a tree (which creates many unique rays),
    this approach:
    1. Starts with a set of seed rays
    2. Finds all orthogonal pairs in the pool
    3. For each pair, computes the cross product (completing the triad)
    4. Adds cross-product rays to the pool
    5. Repeats until pool stabilizes

    This is essentially what alphabets do, but starting from arbitrary
    (potentially irrational) seed rays.
    """
    pool = RayPool(tol=tol)

    # Seed with random unit vectors
    for _ in range(n_seed):
        v = np.random.randn(3)
        v = v / np.linalg.norm(v)
        pool.add(v)

    # Iteratively complete: find orthogonal pairs, add cross products
    for iteration in range(max_iterations):
        n_before = len(pool)
        rays = pool.rays

        for i in range(len(rays)):
            for j in range(i + 1, len(rays)):
                if abs(np.dot(rays[i], rays[j])) < tol:
                    # Found an orthogonal pair — complete the triad
                    cross = np.cross(rays[i], rays[j])
                    if np.linalg.norm(cross) > tol:
                        cross = cross / np.linalg.norm(cross)
                        pool.add(cross)

        if len(pool) == n_before:
            break  # Pool stabilized

    # Now analyze the full configuration
    pairs, triads = analyze_configuration(pool, [])
    return pool, pairs, triads


def build_from_perturbed_integer(perturbation=0.0, alphabet_range=2):
    """
    Start from integer-like coordinates but add a continuous perturbation.
    This explores the neighborhood of CK-31 in coordinate space.

    With perturbation=0, this reproduces the integer alphabet search.
    With small perturbation, it explores nearby configurations that
    might have different combinatorial structure.
    """
    pool = RayPool(tol=1e-6)
    values = list(range(-alphabet_range, alphabet_range + 1))

    for a in values:
        for b in values:
            for c in values:
                v = np.array([a, b, c], dtype=float)
                if np.linalg.norm(v) < 0.01:
                    continue
                # Add perturbation
                if perturbation > 0:
                    v += np.random.randn(3) * perturbation
                v = v / np.linalg.norm(v)

                # Canonicalize: first nonzero component positive
                for k in range(3):
                    if abs(v[k]) > 1e-10:
                        if v[k] < 0:
                            v = -v
                        break
                pool.add(v)

    pairs, triads = analyze_configuration(pool, [])
    return pool, pairs, triads


def build_from_two_alphabets(alpha1, alpha2, mix_fraction=0.5):
    """
    Generate rays from two different alphabets and mix them.
    This creates configurations that no single alphabet can produce.

    alpha1, alpha2: lists of coordinate values
    mix_fraction: fraction of rays to take from alpha2
    """
    pool = RayPool(tol=1e-8)

    import itertools
    for alphabet in [alpha1, alpha2]:
        for combo in itertools.product(alphabet, repeat=3):
            v = np.array(combo, dtype=float)
            if np.linalg.norm(v) < 0.01:
                continue
            v = v / np.linalg.norm(v)
            for k in range(3):
                if abs(v[k]) > 1e-10:
                    if v[k] < 0:
                        v = -v
                    break
            pool.add(v)

    # Now complete all orthogonal pairs
    rays = pool.rays
    for i in range(len(rays)):
        for j in range(i + 1, len(rays)):
            if abs(np.dot(rays[i], rays[j])) < 1e-8:
                cross = np.cross(rays[i], rays[j])
                if np.linalg.norm(cross) > 1e-8:
                    cross = cross / np.linalg.norm(cross)
                    pool.add(cross)

    pairs, triads = analyze_configuration(pool, [])
    return pool, pairs, triads


def experiment_completion(n_trials=200, n_seed_range=(8, 20), verbose=True):
    """
    Experiment: Orthogonal completion from random seeds.
    Start with random rays, complete all triads via cross products,
    test for KS-uncolorability.
    """
    print(f"\n{'='*60}")
    print(f"EXPERIMENT: Orthogonal Completion from Random Seeds")
    print(f"{'='*60}")

    best_minimal = float('inf')
    unc_count = 0
    t0 = time.time()

    for trial in range(n_trials):
        n_seed = random.randint(*n_seed_range)
        pool, pairs, triads = build_from_orthogonal_completion(n_seed)
        n = len(pool)

        if len(triads) < 2:
            continue

        unc = check_uncolorable(n, pairs, triads)
        if unc:
            unc_count += 1
            if verbose:
                print(f"  Trial {trial+1}: UNCOLORABLE! "
                      f"{n} rays, {len(pairs)} pairs, {len(triads)} triads")

            best_subset, best_size = minimize_ks_set(
                n, pool.rays, pairs, triads, num_trials=50)
            if best_size < best_minimal:
                best_minimal = best_size
                if verbose:
                    print(f"    -> Minimized to {best_size} rays")
                    if best_size < 31:
                        print(f"    *** BELOW CK-31! ***")

        if verbose and (trial + 1) % 50 == 0:
            dt = time.time() - t0
            print(f"  [{trial+1}/{n_trials}] {dt:.1f}s, {unc_count} uncolorable")

    dt = time.time() - t0
    print(f"\n  Results ({dt:.1f}s): {unc_count}/{n_trials} uncolorable, "
          f"best minimal: {best_minimal}")
    return best_minimal, unc_count


def experiment_perturbed_integer(n_trials=100, verbose=True):
    """
    Experiment: Perturb integer-alphabet coordinates.
    Start from {0, ±1, ±2} (which produces CK-31) and add
    increasing perturbations to explore the neighborhood.
    """
    print(f"\n{'='*60}")
    print(f"EXPERIMENT: Perturbed Integer Alphabet")
    print(f"{'='*60}")

    for eps in [0.0, 0.01, 0.05, 0.1, 0.2, 0.5]:
        best_minimal = float('inf')
        unc_count = 0

        for trial in range(n_trials):
            pool, pairs, triads = build_from_perturbed_integer(
                perturbation=eps, alphabet_range=2)
            n = len(pool)

            if len(triads) < 2:
                continue

            unc = check_uncolorable(n, pairs, triads)
            if unc:
                unc_count += 1
                best_subset, best_size = minimize_ks_set(
                    n, pool.rays, pairs, triads, num_trials=20)
                if best_size < best_minimal:
                    best_minimal = best_size

        min_str = str(best_minimal) if best_minimal < float('inf') else '--'
        print(f"  eps={eps:.2f}: {unc_count}/{n_trials} uncolorable, "
              f"best minimal: {min_str}")


def experiment_mixed_alphabets(verbose=True):
    """
    Experiment: Mix two algebraically independent alphabets.
    E.g., integer {0, ±1, ±2} with sqrt(2) {0, ±1, ±√2},
    then complete all orthogonal pairs via cross products.
    The cross products generate rays in NEITHER original alphabet.
    """
    print(f"\n{'='*60}")
    print(f"EXPERIMENT: Mixed Alphabet + Completion")
    print(f"{'='*60}")

    s2 = np.sqrt(2)
    s3 = np.sqrt(3)
    phi = (1 + np.sqrt(5)) / 2

    mixes = [
        ('int + sqrt2', [0, 1, -1, 2, -2], [0, 1, -1, s2, -s2]),
        ('int + sqrt3', [0, 1, -1, 2, -2], [0, 1, -1, s3, -s3]),
        ('int + phi', [0, 1, -1, 2, -2], [0, 1, -1, phi, -phi]),
        ('sqrt2 + sqrt3', [0, 1, -1, s2, -s2], [0, 1, -1, s3, -s3]),
        ('sqrt2 + phi', [0, 1, -1, s2, -s2], [0, 1, -1, phi, -phi]),
        ('int + sqrt5', [0, 1, -1, 2, -2], [0, 1, -1, np.sqrt(5), -np.sqrt(5)]),
    ]

    for name, a1, a2 in mixes:
        pool, pairs, triads = build_from_two_alphabets(a1, a2)
        n = len(pool)

        if len(triads) < 2:
            print(f"  {name:20s}: {n} rays, {len(pairs)} pairs, "
                  f"{len(triads)} triads — too few triads")
            continue

        unc = check_uncolorable(n, pairs, triads)
        if unc:
            best_subset, best_size = minimize_ks_set(
                n, pool.rays, pairs, triads, num_trials=200)
            print(f"  {name:20s}: {n} rays, {len(pairs)} pairs, "
                  f"{len(triads)} triads — UNCOLORABLE, minimal: {best_size}")
            if best_size < 31:
                print(f"    *** BELOW CK-31! ***")
        else:
            print(f"  {name:20s}: {n} rays, {len(pairs)} pairs, "
                  f"{len(triads)} triads — colorable")


def print_configuration(pool, subset, pairs, triads):
    """Print a KS configuration in detail."""
    s = set(subset)
    remap = {old: new for new, old in enumerate(sorted(subset))}

    print(f"\n  Configuration: {len(subset)} rays")
    for new_idx, old_idx in enumerate(sorted(subset)):
        v = pool.rays[old_idx]
        print(f"    {new_idx+1:3d}: ({v[0]:8.5f}, {v[1]:8.5f}, {v[2]:8.5f})")

    # Count triads in subset
    sub_triads = [(remap[a], remap[b], remap[c])
                  for a, b, c in triads if a in s and b in s and c in s]
    sub_pairs = [(remap[a], remap[b])
                 for a, b in pairs if a in s and b in s]
    print(f"    Pairs: {len(sub_pairs)}, Triads: {len(sub_triads)}")


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    np.random.seed(42)
    random.seed(42)

    print("=" * 60)
    print("KS Geometry-First Search v2")
    print("Searching for KS sets below Conway-Kochen 31")
    print(f"SAT engine: {'external (ks_sat.py)' if HAS_SAT else 'built-in backtracking'}")
    print("=" * 60)

    all_mins = []

    # ---- Experiment 1: Mixed alphabets + completion ----
    # This is the key new idea: combine algebraically independent
    # coordinate sets and complete via cross products. The cross products
    # generate rays in NEITHER original alphabet.
    experiment_mixed_alphabets(verbose=True)

    # ---- Experiment 2: Orthogonal completion from random seeds ----
    # Start with random rays, complete all triads via cross products.
    # Tests whether "generic" configurations can be KS-uncolorable.
    min2, unc2 = experiment_completion(
        n_trials=200, n_seed_range=(8, 25), verbose=True)
    if min2 < float('inf'):
        all_mins.append(min2)

    # ---- Experiment 3: Perturbed integer alphabet ----
    # Start from {0, ±1, ±2} (which produces CK-31) and add
    # perturbations to explore the neighborhood in coordinate space.
    experiment_perturbed_integer(n_trials=50, verbose=True)

    # ---- Experiment 4: Frame trees (for comparison) ----
    stats4 = experiment_frame_tree(
        n_trials=100, depth=2, branching=2, verbose=True)
    if stats4['uncolorable'] > 0:
        all_mins.append(stats4['min_rays'])

    # ---- Summary ----
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    if all_mins:
        overall_best = min(all_mins)
        print(f"\n  OVERALL BEST: {overall_best} rays")
        if overall_best < 31:
            print(f"  *** BELOW CK-31 ({overall_best} < 31) — NEW RESULT! ***")
        elif overall_best == 31:
            print(f"  Matches CK-31 — consistent with optimality conjecture")
        else:
            print(f"  Above CK-31 ({overall_best} > 31)")
    else:
        print("  No uncolorable configurations found in random/frame approaches.")

    print(f"\n  Reference: Trandafir & Cabello (2025) conjecture 31 is optimal.")
    print(f"  Theoretical lower bound: 24 (Uijlen-Westerbaan 2016).")
