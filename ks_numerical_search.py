"""
ks_numerical_search.py -- Numerical optimization search for sub-31 KS sets
==========================================================================

Strategy 5: Non-algebraic numerical search.
  - Simulated annealing to place n rays in R^3 / C^3
  - Perturbation from CK-31 (remove rays, add new ones)
  - Greedy orthogonal construction from random seeds

The key challenge: exact orthogonality is measure-zero for random rays,
so we use a tolerance-based approach with gradual tightening.
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

import math
import random
import time
import numpy as np
from itertools import combinations

from pysat.solvers import Glucose4

random.seed(42)
np.random.seed(42)


# =====================================================================
# Core utilities
# =====================================================================

def random_unit_ray_R3():
    """Random unit vector in R^3 (uniform on S^2)."""
    v = np.random.randn(3)
    v /= np.linalg.norm(v)
    # Canonicalize: first nonzero component positive
    for i in range(3):
        if abs(v[i]) > 1e-12:
            if v[i] < 0:
                v = -v
            break
    return v


def random_unit_ray_C3():
    """Random unit vector in C^3."""
    v = np.random.randn(3) + 1j * np.random.randn(3)
    v /= np.linalg.norm(v)
    # Canonicalize: first nonzero component has phase 0
    for i in range(3):
        if abs(v[i]) > 1e-12:
            v = v * np.conj(v[i]) / abs(v[i])
            break
    return v


def hermitian_dot(a, b):
    """Hermitian inner product <a|b> = sum(conj(a_i) * b_i)."""
    return np.dot(np.conj(a), b)


def build_ortho_graph(rays, tol=1e-9):
    """Build orthogonality pairs and triads."""
    n = len(rays)
    pairs = []
    adj = {i: set() for i in range(n)}
    for i in range(n):
        for j in range(i + 1, n):
            dot = hermitian_dot(rays[i], rays[j])
            if abs(dot) < tol:
                pairs.append((i, j))
                adj[i].add(j)
                adj[j].add(i)
    triads = []
    for i in range(n):
        ni = sorted(adj[i])
        for idx_j, j in enumerate(ni):
            if j <= i:
                continue
            for k in ni[idx_j + 1:]:
                if k <= j:
                    continue
                if k in adj[j]:
                    triads.append((i, j, k))
    return pairs, triads, adj


def is_ks_uncolorable(n_vertices, triads, pairs):
    """Test KS-uncolorability via SAT."""
    if not triads:
        return False
    solver = Glucose4()
    for a, b, c in triads:
        va, vb, vc = a + 1, b + 1, c + 1
        solver.add_clause([va, vb, vc])
        solver.add_clause([-va, -vb])
        solver.add_clause([-va, -vc])
        solver.add_clause([-vb, -vc])
    for i, j in pairs:
        vi, vj = i + 1, j + 1
        solver.add_clause([-vi, -vj])
    result = solver.solve()
    solver.delete()
    return not result


# =====================================================================
# CK-31 vectors (for perturbation methods)
# =====================================================================

CK31_VECS = [
    (1,0,0), (0,1,0), (0,0,1),
    (1,1,0), (1,-1,0), (1,0,1), (1,0,-1), (0,1,1), (0,1,-1),
    (1,1,1), (1,1,-1), (1,-1,1), (1,-1,-1),
    (2,1,0), (2,-1,0), (2,0,1), (2,0,-1), (0,2,1), (0,2,-1),
    (1,2,0), (1,0,2), (0,1,2),
    (2,1,1), (2,1,-1), (2,-1,1), (1,2,1), (1,2,-1), (1,1,2),
    (1,-2,1), (1,1,-2), (1,-1,2),
]

CK31_RAYS = []
for v in CK31_VECS:
    r = np.array(v, dtype=float)
    r /= np.linalg.norm(r)
    CK31_RAYS.append(r)


# =====================================================================
# Method 1: Simulated Annealing from scratch
# =====================================================================

def sa_score(rays, tol=1e-6):
    """Score a ray configuration. Higher = better."""
    n = len(rays)
    n_pairs = 0
    adj = {i: set() for i in range(n)}
    for i in range(n):
        for j in range(i + 1, n):
            dot = abs(hermitian_dot(rays[i], rays[j]))
            if dot < tol:
                n_pairs += 1
                adj[i].add(j)
                adj[j].add(i)

    # Count triads
    n_triads = 0
    for i in range(n):
        ni = sorted(adj[i])
        for idx_j, j in enumerate(ni):
            if j <= i:
                continue
            for k in ni[idx_j + 1:]:
                if k <= j:
                    continue
                if k in adj[j]:
                    n_triads += 1

    # Bonus for uncolorability
    ks_bonus = 0
    if n_triads >= 10:
        pairs = [(i, j) for i in range(n) for j in adj[i] if i < j]
        triads = []
        for i in range(n):
            ni = sorted(adj[i])
            for idx_j, j in enumerate(ni):
                if j <= i:
                    continue
                for k in ni[idx_j + 1:]:
                    if k <= j:
                        continue
                    if k in adj[j]:
                        triads.append((i, j, k))
        if is_ks_uncolorable(n, triads, pairs):
            ks_bonus = 10000

    return n_pairs * 10 + n_triads * 100 + ks_bonus


def sa_near_ortho_score(rays, tol=0.05):
    """Softer score using near-orthogonality for gradient signal."""
    n = len(rays)
    score = 0.0
    for i in range(n):
        for j in range(i + 1, n):
            dot = abs(hermitian_dot(rays[i], rays[j]))
            if dot < tol:
                # Reward near-orthogonality, more reward for closer to 0
                score += (tol - dot) / tol
    return score


def simulated_annealing_R3(n_rays, n_steps=200000, tol=1e-6):
    """SA search for KS-uncolorable set of n_rays in R^3."""
    # Initialize random rays
    rays = [random_unit_ray_R3() for _ in range(n_rays)]
    best_score = sa_score(rays, tol)
    best_rays = [r.copy() for r in rays]
    current_score = best_score

    T = 1.0
    T_min = 0.001
    alpha = (T_min / T) ** (1.0 / n_steps)

    found_ks = False
    last_report = 0

    for step in range(n_steps):
        # Perturb a random ray
        idx = random.randint(0, n_rays - 1)
        old_ray = rays[idx].copy()

        perturbation = np.random.randn(3) * T * 0.3
        rays[idx] = rays[idx] + perturbation
        rays[idx] /= np.linalg.norm(rays[idx])
        # Canonicalize
        for i in range(3):
            if abs(rays[idx][i]) > 1e-12:
                if rays[idx][i] < 0:
                    rays[idx] = -rays[idx]
                break

        new_score = sa_score(rays, tol)

        # Accept or reject
        delta = new_score - current_score
        if delta > 0 or random.random() < math.exp(delta / max(T, 1e-10)):
            current_score = new_score
            if current_score > best_score:
                best_score = current_score
                best_rays = [r.copy() for r in rays]
                if best_score >= 10000:
                    found_ks = True
        else:
            rays[idx] = old_ray

        T *= alpha

        if (step + 1) % 50000 == 0 or (step + 1 == n_steps):
            pairs, triads, _ = build_ortho_graph(rays, tol)
            print(f"    Step {step+1}/{n_steps}: T={T:.4f}, "
                  f"pairs={len(pairs)}, triads={len(triads)}, "
                  f"best_score={best_score}")

    return best_rays, best_score, found_ks


def simulated_annealing_C3(n_rays, n_steps=200000, tol=1e-6):
    """SA search for KS-uncolorable set of n_rays in C^3."""
    rays = [random_unit_ray_C3() for _ in range(n_rays)]
    best_score = sa_score(rays, tol)
    best_rays = [r.copy() for r in rays]
    current_score = best_score

    T = 1.0
    T_min = 0.001
    alpha = (T_min / T) ** (1.0 / n_steps)

    found_ks = False

    for step in range(n_steps):
        idx = random.randint(0, n_rays - 1)
        old_ray = rays[idx].copy()

        perturbation = (np.random.randn(3) + 1j * np.random.randn(3)) * T * 0.3
        rays[idx] = rays[idx] + perturbation
        rays[idx] /= np.linalg.norm(rays[idx])
        # Canonicalize
        for i in range(3):
            if abs(rays[idx][i]) > 1e-12:
                rays[idx] = rays[idx] * np.conj(rays[idx][i]) / abs(rays[idx][i])
                break

        new_score = sa_score(rays, tol)

        delta = new_score - current_score
        if delta > 0 or random.random() < math.exp(delta / max(T, 1e-10)):
            current_score = new_score
            if current_score > best_score:
                best_score = current_score
                best_rays = [r.copy() for r in rays]
                if best_score >= 10000:
                    found_ks = True
        else:
            rays[idx] = old_ray

        T *= alpha

        if (step + 1) % 50000 == 0 or (step + 1 == n_steps):
            pairs, triads, _ = build_ortho_graph(rays, tol)
            print(f"    Step {step+1}/{n_steps}: T={T:.4f}, "
                  f"pairs={len(pairs)}, triads={len(triads)}, "
                  f"best_score={best_score}")

    return best_rays, best_score, found_ks


# =====================================================================
# Method 2: Perturbation from CK-31
# =====================================================================

def perturb_from_ck31(target_n, n_attempts=1000):
    """Try to find a KS set with target_n rays by modifying CK-31.

    Strategy: remove (31-target_n) rays from CK-31, then try adding
    new rays (not from the integer pool) that restore uncolorability.
    """
    base_pairs, base_triads, base_adj = build_ortho_graph(CK31_RAYS)
    n_remove = 31 - target_n

    found = False
    best_replacement_triads = 0

    for attempt in range(n_attempts):
        # Pick random rays to remove
        to_remove = set(random.sample(range(31), n_remove))
        remaining = [i for i in range(31) if i not in to_remove]
        sub_rays = [CK31_RAYS[i] for i in remaining]

        # Check if already KS (shouldn't be, due to criticality)
        remap = {old: new for new, old in enumerate(remaining)}
        sub_pairs = [(remap[i], remap[j]) for i, j in base_pairs
                     if i in remap and j in remap]
        sub_triads = [(remap[a], remap[b], remap[c])
                      for a, b, c in base_triads
                      if a in remap and b in remap and c in remap]

        if is_ks_uncolorable(len(sub_rays), sub_triads, sub_pairs):
            print(f"  *** FOUND KS with {target_n} rays (attempt {attempt+1})! ***")
            found = True
            break

        # Try adding a random replacement ray
        for _ in range(50):
            new_ray = random_unit_ray_R3()
            test_rays = sub_rays + [new_ray]
            tp, tt, _ = build_ortho_graph(test_rays)
            if len(tt) > len(sub_triads) and is_ks_uncolorable(len(test_rays), tt, tp):
                print(f"  *** FOUND KS with {target_n+1} rays "
                      f"(replaced {n_remove}, added 1, attempt {attempt+1})! ***")
                if target_n + 1 < 31:
                    found = True
                break
            if len(tt) > best_replacement_triads:
                best_replacement_triads = len(tt)

        if found:
            break

        if (attempt + 1) % 200 == 0:
            print(f"    ... {attempt+1}/{n_attempts} attempts, "
                  f"best replacement triads = {best_replacement_triads}")

    return found


# =====================================================================
# Method 3: Orthogonal completion from random seeds
# =====================================================================

def cross_product_real(a, b):
    """Cross product of two R^3 vectors, normalized."""
    c = np.cross(a, b)
    norm = np.linalg.norm(c)
    if norm < 1e-12:
        return None
    c /= norm
    # Canonicalize
    for i in range(3):
        if abs(c[i]) > 1e-12:
            if c[i] < 0:
                c = -c
            break
    return c


def completion_search(n_target, n_attempts=500, max_rays=60):
    """Build KS sets by orthogonal completion from random seeds.

    Start with random orthogonal triads, complete by adding cross products,
    test for KS-uncolorability at each stage.
    """
    best_triads = 0
    found = False

    for attempt in range(n_attempts):
        # Start with a random orthonormal basis
        v1 = random_unit_ray_R3()
        # v2 orthogonal to v1
        t = np.random.randn(3)
        t -= np.dot(t, v1) * v1
        t /= np.linalg.norm(t)
        v2 = t.copy()
        for i in range(3):
            if abs(v2[i]) > 1e-12:
                if v2[i] < 0:
                    v2 = -v2
                break
        v3 = cross_product_real(v1, v2)

        rays = [v1, v2, v3]
        seen = set()
        for r in rays:
            seen.add(tuple(np.round(r, 8)))

        # Iteratively add cross products of orthogonal pairs
        for _ in range(200):
            if len(rays) >= max_rays:
                break
            # Pick two rays, compute cross product
            i, j = random.sample(range(len(rays)), 2)
            dot = abs(np.dot(rays[i], rays[j]))
            if dot < 1e-9:
                cp = cross_product_real(rays[i], rays[j])
                if cp is not None:
                    key = tuple(np.round(cp, 8))
                    if key not in seen:
                        seen.add(key)
                        rays.append(cp)

            # Also try random perturbation + projection
            if random.random() < 0.3:
                base = rays[random.randint(0, len(rays) - 1)]
                perturb = np.random.randn(3) * 0.5
                new = base + perturb
                new /= np.linalg.norm(new)
                for ii in range(3):
                    if abs(new[ii]) > 1e-12:
                        if new[ii] < 0:
                            new = -new
                        break
                key = tuple(np.round(new, 8))
                if key not in seen:
                    seen.add(key)
                    rays.append(new)

        # Test subsets around n_target
        if len(rays) >= n_target:
            pairs, triads, adj = build_ortho_graph(rays)
            if len(triads) > best_triads:
                best_triads = len(triads)

            if is_ks_uncolorable(len(rays), triads, pairs):
                print(f"  *** FOUND KS with {len(rays)} rays "
                      f"(attempt {attempt+1})! ***")
                if len(rays) < 31:
                    found = True
                    break
                # Try to minimize
                current = list(range(len(rays)))
                random.shuffle(current)
                for cand in list(current):
                    test = [r for r in current if r != cand]
                    if len(test) < n_target:
                        break
                    ts = set(test)
                    rm = {old: new for new, old in enumerate(test)}
                    st = [(rm[a], rm[b], rm[c]) for a, b, c in triads
                          if a in ts and b in ts and c in ts]
                    sp = [(rm[i], rm[j]) for i, j in pairs
                          if i in ts and j in ts]
                    if is_ks_uncolorable(len(test), st, sp):
                        current = test
                if len(current) < 31:
                    print(f"  *** Minimized to {len(current)} rays! ***")
                    found = True
                    break

        if (attempt + 1) % 100 == 0:
            print(f"    ... {attempt+1}/{n_attempts}, "
                  f"max rays built = {len(rays)}, "
                  f"best triads = {best_triads}")

    return found


# =====================================================================
# Method 4: Soft-tolerance SA with tightening
# =====================================================================

def soft_sa_search(n_rays, n_steps=300000):
    """SA with gradually tightening orthogonality tolerance.

    Start with generous tolerance (0.1), let SA find configurations
    with many near-orthogonal pairs, then tighten to exact.
    """
    rays = [random_unit_ray_R3() for _ in range(n_rays)]

    # Schedule: tolerance decreases over time
    tol_start = 0.1
    tol_end = 1e-6
    T_start = 2.0
    T_end = 0.001

    best_exact_pairs = 0
    best_exact_triads = 0

    for step in range(n_steps):
        frac = step / n_steps
        tol = tol_start * (tol_end / tol_start) ** frac
        T = T_start * (T_end / T_start) ** frac

        # Current score with current tolerance
        n_pairs = 0
        for i in range(n_rays):
            for j in range(i + 1, n_rays):
                if abs(np.dot(rays[i], rays[j])) < tol:
                    n_pairs += 1
        current_score = n_pairs

        # Perturb
        idx = random.randint(0, n_rays - 1)
        old = rays[idx].copy()
        rays[idx] = rays[idx] + np.random.randn(3) * T * 0.2
        rays[idx] /= np.linalg.norm(rays[idx])
        for i in range(3):
            if abs(rays[idx][i]) > 1e-12:
                if rays[idx][i] < 0:
                    rays[idx] = -rays[idx]
                break

        new_pairs = 0
        for i in range(n_rays):
            for j in range(i + 1, n_rays):
                if abs(np.dot(rays[i], rays[j])) < tol:
                    new_pairs += 1
        new_score = new_pairs

        delta = new_score - current_score
        if delta >= 0 or random.random() < math.exp(delta / max(T, 1e-10)):
            pass  # accept
        else:
            rays[idx] = old

        # Periodic check with exact tolerance
        if (step + 1) % 50000 == 0:
            ep, et, _ = build_ortho_graph(rays, tol=1e-9)
            if len(ep) > best_exact_pairs:
                best_exact_pairs = len(ep)
            if len(et) > best_exact_triads:
                best_exact_triads = len(et)
            print(f"    Step {step+1}/{n_steps}: tol={tol:.6f}, T={T:.4f}, "
                  f"soft_pairs={new_score}, "
                  f"exact_pairs={len(ep)}, exact_triads={len(et)}")

            if len(et) >= 10:
                if is_ks_uncolorable(n_rays, et, ep):
                    print(f"  *** KS-UNCOLORABLE with {n_rays} rays! ***")
                    return rays, True

    return rays, False


# =====================================================================
# Main execution
# =====================================================================

print("=" * 70)
print("STRATEGY 5: NUMERICAL OPTIMIZATION SEARCH FOR SUB-31 KS SETS")
print("=" * 70)


# --- Method 1: SA from scratch in R^3 ---
print("\n--- Method 1: Simulated annealing in R^3 ---")
for n in [28, 29, 30]:
    print(f"\n  Searching for {n}-ray KS set in R^3 (200k steps)...")
    t0 = time.time()
    rays, score, found = simulated_annealing_R3(n, n_steps=200000, tol=1e-6)
    elapsed = time.time() - t0
    pairs, triads, _ = build_ortho_graph(rays, tol=1e-6)
    status = "*** KS FOUND ***" if found else "not found"
    print(f"  Result: {len(pairs)} pairs, {len(triads)} triads, "
          f"KS: {status} [{elapsed:.1f}s]")


# --- Method 1b: SA from scratch in C^3 ---
print("\n--- Method 1b: Simulated annealing in C^3 ---")
for n in [28, 30]:
    print(f"\n  Searching for {n}-ray KS set in C^3 (200k steps)...")
    t0 = time.time()
    rays, score, found = simulated_annealing_C3(n, n_steps=200000, tol=1e-6)
    elapsed = time.time() - t0
    pairs, triads, _ = build_ortho_graph(rays, tol=1e-6)
    status = "*** KS FOUND ***" if found else "not found"
    print(f"  Result: {len(pairs)} pairs, {len(triads)} triads, "
          f"KS: {status} [{elapsed:.1f}s]")


# --- Method 2: Perturbation from CK-31 ---
print("\n--- Method 2: Perturbation from CK-31 ---")
for target in [28, 29, 30]:
    print(f"\n  Trying to build {target}-ray KS set from CK-31 "
          f"(1000 attempts)...")
    t0 = time.time()
    found = perturb_from_ck31(target, n_attempts=1000)
    elapsed = time.time() - t0
    status = "*** FOUND ***" if found else "not found"
    print(f"  Result: {status} [{elapsed:.1f}s]")


# --- Method 3: Completion from random seeds ---
print("\n--- Method 3: Orthogonal completion from random seeds ---")
for target in [25, 28, 30]:
    print(f"\n  Building ray sets targeting {target} rays (500 attempts)...")
    t0 = time.time()
    found = completion_search(target, n_attempts=500, max_rays=60)
    elapsed = time.time() - t0
    status = "*** FOUND ***" if found else "not found"
    print(f"  Result: {status} [{elapsed:.1f}s]")


# --- Method 4: Soft-tolerance SA ---
print("\n--- Method 4: Soft-tolerance SA with tightening (R^3) ---")
for n in [28, 30]:
    print(f"\n  Soft SA for {n}-ray KS set (300k steps)...")
    t0 = time.time()
    rays, found = soft_sa_search(n, n_steps=300000)
    elapsed = time.time() - t0
    pairs, triads, _ = build_ortho_graph(rays, tol=1e-9)
    status = "*** KS FOUND ***" if found else "not found"
    print(f"  Final: {len(pairs)} exact pairs, {len(triads)} exact triads, "
          f"KS: {status} [{elapsed:.1f}s]")


print(f"\n{'='*70}")
print("NUMERICAL SEARCH COMPLETE")
print("=" * 70)
