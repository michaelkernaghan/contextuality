"""
ks_triad_density.py -- Triad density bounds in R^3 and C^3
==========================================================

For n rays in R^3 or C^3, what is the maximum number of:
  - Orthogonal pairs
  - Orthonormal triads (complete bases)

And what is the minimum needed for KS-uncolorability?

We investigate empirically:
  1. Random ray sampling: for each n, sample many random n-ray sets,
     count max pairs/triads achievable
  2. Optimized configurations: try to maximize triads for given n
  3. Threshold detection: for each n, what's the minimum triads/pairs
     needed for uncolorability? (via random SAT instances)
  4. Compare R^3 vs C^3

Key question: Is there an n < 31 where achievable triads exceed
the uncolorability threshold?
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

import numpy as np
import random
import time
from collections import defaultdict

from pysat.solvers import Glucose4

random.seed(42)
np.random.seed(42)


def random_real_rays(n):
    """Generate n random unit rays in R^3 (on RP^2)."""
    rays = np.random.randn(n, 3)
    norms = np.linalg.norm(rays, axis=1, keepdims=True)
    rays = rays / norms
    # Canonicalize: first nonzero component positive
    for i in range(n):
        for j in range(3):
            if abs(rays[i, j]) > 1e-12:
                if rays[i, j] < 0:
                    rays[i] = -rays[i]
                break
    return rays


def random_complex_rays(n):
    """Generate n random unit rays in C^3 (on CP^2)."""
    real_part = np.random.randn(n, 3)
    imag_part = np.random.randn(n, 3)
    rays = real_part + 1j * imag_part
    norms = np.sqrt(np.sum(np.abs(rays)**2, axis=1, keepdims=True))
    rays = rays / norms
    # Canonicalize: first nonzero component real and positive
    for i in range(n):
        for j in range(3):
            if abs(rays[i, j]) > 1e-12:
                phase = rays[i, j] / abs(rays[i, j])
                rays[i] = rays[i] / phase
                break
    return rays


def count_pairs_triads_real(rays, tol=1e-6):
    """Count orthogonal pairs and triads for real rays."""
    n = len(rays)
    dots = rays @ rays.T

    pairs = []
    adj = defaultdict(set)
    for i in range(n):
        for j in range(i + 1, n):
            if abs(dots[i, j]) < tol:
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

    return len(pairs), len(triads), pairs, triads


def count_pairs_triads_complex(rays, tol=1e-6):
    """Count orthogonal pairs and triads for complex rays."""
    n = len(rays)
    # Hermitian dot product: <u|v> = u^dagger @ v
    dots = np.conjugate(rays) @ rays.T

    pairs = []
    adj = defaultdict(set)
    for i in range(n):
        for j in range(i + 1, n):
            if abs(dots[i, j]) < tol:
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

    return len(pairs), len(triads), pairs, triads


def is_ks_uncolorable(n_vertices, triads, ortho_pairs):
    """Test KS-uncolorability."""
    if not triads:
        return False
    solver = Glucose4()
    for a, b, c in triads:
        va, vb, vc = a + 1, b + 1, c + 1
        solver.add_clause([va, vb, vc])
        solver.add_clause([-va, -vb])
        solver.add_clause([-va, -vc])
        solver.add_clause([-vb, -vc])
    for i, j in ortho_pairs:
        vi, vj = i + 1, j + 1
        solver.add_clause([-vi, -vj])
    result = solver.solve()
    solver.delete()
    return not result


# =====================================================================
# Experiment 1: Random sampling — max pairs/triads achievable
# =====================================================================

def experiment_random_density(n_values, n_samples=500):
    """For each n, sample random ray sets and record max pairs/triads."""

    print(f"\n{'='*70}")
    print(f"EXPERIMENT 1: Random ray sampling — achievable pair/triad counts")
    print(f"{'='*70}")
    print(f"\n  {'n':>3}  |  {'R3 max pairs':>12} {'R3 max triads':>13} {'R3 avg triads':>13}"
          f"  |  {'C3 max pairs':>12} {'C3 max triads':>13} {'C3 avg triads':>13}")
    print(f"  {'---':>3}--+--{'---':>12}-{'---':>13}-{'---':>13}"
          f"--+--{'---':>12}-{'---':>13}-{'---':>13}")

    results = {}
    for n in n_values:
        r3_max_p, r3_max_t, r3_sum_t = 0, 0, 0
        c3_max_p, c3_max_t, c3_sum_t = 0, 0, 0

        for _ in range(n_samples):
            # Real
            rays_r = random_real_rays(n)
            np_r, nt_r, _, _ = count_pairs_triads_real(rays_r)
            r3_max_p = max(r3_max_p, np_r)
            r3_max_t = max(r3_max_t, nt_r)
            r3_sum_t += nt_r

            # Complex
            rays_c = random_complex_rays(n)
            np_c, nt_c, _, _ = count_pairs_triads_complex(rays_c)
            c3_max_p = max(c3_max_p, np_c)
            c3_max_t = max(c3_max_t, nt_c)
            c3_sum_t += nt_c

        r3_avg_t = r3_sum_t / n_samples
        c3_avg_t = c3_sum_t / n_samples

        print(f"  {n:3d}  |  {r3_max_p:12d} {r3_max_t:13d} {r3_avg_t:13.2f}"
              f"  |  {c3_max_p:12d} {c3_max_t:13d} {c3_avg_t:13.2f}")

        results[n] = {
            'r3_max_p': r3_max_p, 'r3_max_t': r3_max_t, 'r3_avg_t': r3_avg_t,
            'c3_max_p': c3_max_p, 'c3_max_t': c3_max_t, 'c3_avg_t': c3_avg_t,
        }

    return results


# =====================================================================
# Experiment 2: Algebraic configurations — achieved densities
# =====================================================================

def experiment_algebraic_density():
    """Report actual pair/triad counts from known algebraic constructions."""
    from ks_complex import generate_eisenstein_rays, hermitian_dot
    from ks_new_islands import generate_rays_from_alphabet, hermitian_completion
    import cmath

    print(f"\n{'='*70}")
    print(f"EXPERIMENT 2: Algebraic constructions — achieved density")
    print(f"{'='*70}")

    constructions = {}

    # Integer
    int_alph = [complex(x) for x in [0, 1, -1, 2, -2]]
    int_rays = generate_rays_from_alphabet(int_alph)
    constructions['Integer pool'] = int_rays

    # CK-31 specifically
    from ks_sat import CK31_VECTORS
    ck31_rays = [tuple(complex(x) for x in v) for v in CK31_VECTORS]
    constructions['CK-31 (minimized)'] = ck31_rays

    # Eisenstein
    eis_rays = generate_eisenstein_rays(max_coeff=1, dim=3, norm_cutoff=3)
    constructions['Eisenstein pool'] = eis_rays

    # Peres
    s2 = np.sqrt(2)
    constructions['Peres pool'] = generate_rays_from_alphabet(
        [complex(x) for x in [0, 1, -1, s2, -s2]])

    # Z[sqrt(-2)]
    sd2 = cmath.sqrt(-2)
    constructions['Z[sqrt(-2)] pool'] = generate_rays_from_alphabet([0, 1, -1, sd2, -sd2])

    # Heegner-7
    gen7 = (1 + cmath.sqrt(-7)) / 2
    constructions['Heegner-7 pool'] = generate_rays_from_alphabet(
        [0, 1, -1, gen7, -gen7, gen7.conjugate(), -gen7.conjugate()])

    # Golden ratio
    phi = (1 + np.sqrt(5)) / 2
    golden_raw = generate_rays_from_alphabet([complex(x) for x in [0, 1, -1, phi, -phi]])
    constructions['Golden pool'] = hermitian_completion(golden_raw)

    print(f"\n  {'Construction':<22} {'n':>4} {'pairs':>6} {'triads':>7}"
          f" {'p/n':>6} {'t/n':>6} {'p/n(n-1)/2':>11} {'KS':>4}")
    print(f"  {'-'*22} {'----':>4} {'------':>6} {'-------':>7}"
          f" {'------':>6} {'------':>6} {'-----------':>11} {'----':>4}")

    for name, rays in constructions.items():
        n = len(rays)
        # Convert to numpy for dot products
        ray_arr = np.array(rays, dtype=complex)
        dots = np.conjugate(ray_arr) @ ray_arr.T

        pairs = []
        adj = defaultdict(set)
        for i in range(n):
            for j in range(i + 1, n):
                if abs(dots[i, j]) < 1e-8:
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

        ks = is_ks_uncolorable(n, triads, pairs)
        max_pairs = n * (n - 1) / 2
        p_density = len(pairs) / max_pairs if max_pairs > 0 else 0

        print(f"  {name:<22} {n:4d} {len(pairs):6d} {len(triads):7d}"
              f" {len(pairs)/n:6.1f} {len(triads)/n:6.1f} {p_density:11.4f}"
              f" {'YES' if ks else 'no':>4}")


# =====================================================================
# Experiment 3: KS uncolorability threshold
# =====================================================================

def experiment_threshold():
    """For small n, what's the minimum triads/pairs for uncolorability?

    Generate random KS-like constraint structures and test satisfiability.
    This tells us the threshold between colorable and uncolorable.
    """

    print(f"\n{'='*70}")
    print(f"EXPERIMENT 3: Uncolorability threshold — minimum triads needed")
    print(f"  For each n, generate random hypergraphs and find the")
    print(f"  minimum number of triads that makes them KS-uncolorable.")
    print(f"{'='*70}")

    print(f"\n  Testing with ALGEBRAIC rays (integer alphabet, real)...")
    print(f"  For each subset size n of the 49-ray integer pool,")
    print(f"  sample subsets and check for uncolorability.\n")

    # Use integer pool as source of rays with known orthogonalities
    int_alph = [complex(x) for x in [0, 1, -1, 2, -2]]
    from ks_new_islands import generate_rays_from_alphabet
    all_rays = generate_rays_from_alphabet(int_alph)
    n_pool = len(all_rays)

    # Precompute all pairs and triads
    ray_arr = np.array(all_rays, dtype=complex)
    dots = np.conjugate(ray_arr) @ ray_arr.T
    all_pairs = []
    adj = defaultdict(set)
    for i in range(n_pool):
        for j in range(i + 1, n_pool):
            if abs(dots[i, j]) < 1e-8:
                all_pairs.append((i, j))
                adj[i].add(j)
                adj[j].add(i)
    all_triads = []
    for i in range(n_pool):
        ni = sorted(adj[i])
        for idx_j, j in enumerate(ni):
            if j <= i:
                continue
            for k in ni[idx_j + 1:]:
                if k <= j:
                    continue
                if k in adj[j]:
                    all_triads.append((i, j, k))

    print(f"  Integer pool: {n_pool} rays, {len(all_pairs)} pairs, {len(all_triads)} triads")
    print(f"\n  {'n':>3}  {'samples':>8}  {'KS found':>9}  {'min triads':>11}  {'min pairs':>10}")
    print(f"  {'---':>3}  {'--------':>8}  {'---------':>9}  {'-----------':>11}  {'----------':>10}")

    for n in range(20, 50):
        if n > n_pool:
            break
        n_samples = 2000 if n <= 35 else 500
        ks_found = 0
        min_triads_for_ks = float('inf')
        min_pairs_for_ks = float('inf')

        for _ in range(n_samples):
            subset = sorted(random.sample(range(n_pool), n))
            subset_set = set(subset)
            remap = {old: new for new, old in enumerate(subset)}

            sub_pairs = [(remap[i], remap[j]) for i, j in all_pairs
                        if i in subset_set and j in subset_set]
            sub_triads = [(remap[a], remap[b], remap[c]) for a, b, c in all_triads
                         if a in subset_set and b in subset_set and c in subset_set]

            if sub_triads and is_ks_uncolorable(n, sub_triads, sub_pairs):
                ks_found += 1
                if len(sub_triads) < min_triads_for_ks:
                    min_triads_for_ks = len(sub_triads)
                if len(sub_pairs) < min_pairs_for_ks:
                    min_pairs_for_ks = len(sub_pairs)

        mt = str(min_triads_for_ks) if ks_found > 0 else '--'
        mp = str(min_pairs_for_ks) if ks_found > 0 else '--'
        print(f"  {n:3d}  {n_samples:8d}  {ks_found:9d}  {mt:>11}  {mp:>10}")


# =====================================================================
# Experiment 4: Complex pool — threshold comparison
# =====================================================================

def experiment_complex_threshold():
    """Same as Experiment 3 but using complex pools."""

    print(f"\n{'='*70}")
    print(f"EXPERIMENT 4: Complex pool threshold comparison")
    print(f"  Using Eisenstein pool (C^3) to compare with integer (R^3)")
    print(f"{'='*70}")

    from ks_complex import generate_eisenstein_rays, hermitian_dot
    all_rays = generate_eisenstein_rays(max_coeff=1, dim=3, norm_cutoff=3)
    n_pool = len(all_rays)

    ray_arr = np.array(all_rays, dtype=complex)
    dots = np.conjugate(ray_arr) @ ray_arr.T
    all_pairs = []
    adj = defaultdict(set)
    for i in range(n_pool):
        for j in range(i + 1, n_pool):
            if abs(dots[i, j]) < 1e-8:
                all_pairs.append((i, j))
                adj[i].add(j)
                adj[j].add(i)
    all_triads = []
    for i in range(n_pool):
        ni = sorted(adj[i])
        for idx_j, j in enumerate(ni):
            if j <= i:
                continue
            for k in ni[idx_j + 1:]:
                if k <= j:
                    continue
                if k in adj[j]:
                    all_triads.append((i, j, k))

    print(f"  Eisenstein pool: {n_pool} rays, {len(all_pairs)} pairs, {len(all_triads)} triads")
    print(f"\n  {'n':>3}  {'samples':>8}  {'KS found':>9}  {'min triads':>11}  {'min pairs':>10}")
    print(f"  {'---':>3}  {'--------':>8}  {'---------':>9}  {'-----------':>11}  {'----------':>10}")

    for n in range(20, n_pool + 1):
        n_samples = 2000 if n <= 40 else 500
        ks_found = 0
        min_triads_for_ks = float('inf')
        min_pairs_for_ks = float('inf')

        for _ in range(n_samples):
            subset = sorted(random.sample(range(n_pool), n))
            subset_set = set(subset)
            remap = {old: new for new, old in enumerate(subset)}

            sub_pairs = [(remap[i], remap[j]) for i, j in all_pairs
                        if i in subset_set and j in subset_set]
            sub_triads = [(remap[a], remap[b], remap[c]) for a, b, c in all_triads
                         if a in subset_set and b in subset_set and c in subset_set]

            if sub_triads and is_ks_uncolorable(n, sub_triads, sub_pairs):
                ks_found += 1
                if len(sub_triads) < min_triads_for_ks:
                    min_triads_for_ks = len(sub_triads)
                if len(sub_pairs) < min_pairs_for_ks:
                    min_pairs_for_ks = len(sub_pairs)

        mt = str(min_triads_for_ks) if ks_found > 0 else '--'
        mp = str(min_pairs_for_ks) if ks_found > 0 else '--'
        print(f"  {n:3d}  {n_samples:8d}  {ks_found:9d}  {mt:>11}  {mp:>10}")


# =====================================================================
# Experiment 5: Heegner-7 complex pool threshold
# =====================================================================

def experiment_heegner7_threshold():
    """Heegner-7 pool threshold — largest complex pool (145 rays)."""

    print(f"\n{'='*70}")
    print(f"EXPERIMENT 5: Heegner-7 pool (C^3, 145 rays) threshold")
    print(f"{'='*70}")

    import cmath
    from ks_new_islands import generate_rays_from_alphabet

    gen7 = (1 + cmath.sqrt(-7)) / 2
    all_rays = generate_rays_from_alphabet(
        [0, 1, -1, gen7, -gen7, gen7.conjugate(), -gen7.conjugate()])
    n_pool = len(all_rays)

    ray_arr = np.array(all_rays, dtype=complex)
    dots = np.conjugate(ray_arr) @ ray_arr.T
    all_pairs = []
    adj = defaultdict(set)
    for i in range(n_pool):
        for j in range(i + 1, n_pool):
            if abs(dots[i, j]) < 1e-8:
                all_pairs.append((i, j))
                adj[i].add(j)
                adj[j].add(i)
    all_triads = []
    for i in range(n_pool):
        ni = sorted(adj[i])
        for idx_j, j in enumerate(ni):
            if j <= i:
                continue
            for k in ni[idx_j + 1:]:
                if k <= j:
                    continue
                if k in adj[j]:
                    all_triads.append((i, j, k))

    print(f"  Heegner-7 pool: {n_pool} rays, {len(all_pairs)} pairs, {len(all_triads)} triads")
    print(f"\n  {'n':>3}  {'samples':>8}  {'KS found':>9}  {'min triads':>11}")
    print(f"  {'---':>3}  {'--------':>8}  {'---------':>9}  {'-----------':>11}")

    for n in range(25, 80, 5):
        if n > n_pool:
            break
        n_samples = 1000
        ks_found = 0
        min_triads_for_ks = float('inf')

        for _ in range(n_samples):
            subset = sorted(random.sample(range(n_pool), n))
            subset_set = set(subset)
            remap = {old: new for new, old in enumerate(subset)}

            sub_pairs = [(remap[i], remap[j]) for i, j in all_pairs
                        if i in subset_set and j in subset_set]
            sub_triads = [(remap[a], remap[b], remap[c]) for a, b, c in all_triads
                         if a in subset_set and b in subset_set and c in subset_set]

            if sub_triads and is_ks_uncolorable(n, sub_triads, sub_pairs):
                ks_found += 1
                if len(sub_triads) < min_triads_for_ks:
                    min_triads_for_ks = len(sub_triads)

        mt = str(min_triads_for_ks) if ks_found > 0 else '--'
        print(f"  {n:3d}  {n_samples:8d}  {ks_found:9d}  {mt:>11}")


# =====================================================================
# Main
# =====================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("TRIAD DENSITY BOUNDS IN R^3 AND C^3")
    print("How many orthogonal pairs and triads can n rays achieve?")
    print("What is the minimum for KS-uncolorability?")
    print("=" * 70)

    # Experiment 1: Random sampling
    experiment_random_density(
        n_values=[10, 15, 20, 25, 30, 31, 35, 40, 50],
        n_samples=500
    )

    # Experiment 2: Algebraic constructions (known densities)
    experiment_algebraic_density()

    # Experiment 3: Integer pool threshold
    experiment_threshold()

    # Experiment 4: Eisenstein (C^3) threshold
    experiment_complex_threshold()

    # Experiment 5: Heegner-7 threshold
    experiment_heegner7_threshold()

    print(f"\n{'='*70}")
    print("DENSITY ANALYSIS COMPLETE")
    print("=" * 70)
