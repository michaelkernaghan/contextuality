"""
ks_quaternion.py -- Explore KS sets in quaternionic Hilbert space H^3
=====================================================================

The KS theorem applies to any division-ring Hilbert space of sufficient
dimension. Quaternions (H) are one of three associative division algebras
(R, C, H). This script explores whether quaternionic alphabets produce
KS sets in H^3, and what cancellation identities they use.

Key differences from complex case:
  - Quaternion multiplication is non-commutative: ij = k, ji = -k
  - Inner product: <u,v> = conj(u1)*v1 + conj(u2)*v2 + conj(u3)*v3
  - Orthogonality is symmetric: <u,v>=0 iff <v,u>=0
  - Rays: v ~ v*q for any nonzero quaternion q (RIGHT scalar mult)
  - More cancellation identities available due to 4 imaginary units
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

import math
import random
import time
from itertools import combinations, product
from collections import Counter
from pysat.solvers import Glucose4

random.seed(42)


# =====================================================================
# Quaternion arithmetic (exact, integer/rational quaternions)
# =====================================================================
# Represent q = (a, b, c, d) meaning a + bi + cj + dk

def q_conj(q):
    """Quaternion conjugate."""
    return (q[0], -q[1], -q[2], -q[3])

def q_mul(p, q):
    """Quaternion multiplication p*q."""
    a1, b1, c1, d1 = p
    a2, b2, c2, d2 = q
    return (
        a1*a2 - b1*b2 - c1*c2 - d1*d2,
        a1*b2 + b1*a2 + c1*d2 - d1*c2,
        a1*c2 - b1*d2 + c1*a2 + d1*b2,
        a1*d2 + b1*c2 - c1*b2 + d1*a2,
    )

def q_norm_sq(q):
    """Squared norm |q|^2 = a^2 + b^2 + c^2 + d^2."""
    return q[0]**2 + q[1]**2 + q[2]**2 + q[3]**2

def q_is_zero(q):
    return all(c == 0 for c in q)

def q_add(p, q):
    return tuple(a + b for a, b in zip(p, q))

def q_neg(q):
    return tuple(-c for c in q)


# A vector in H^3 is a triple of quaternions: (q1, q2, q3)
ZERO_Q = (0, 0, 0, 0)
ONE_Q = (1, 0, 0, 0)
I_Q = (0, 1, 0, 0)
J_Q = (0, 0, 1, 0)
K_Q = (0, 0, 0, 1)


def inner_product(u, v):
    """Quaternionic inner product <u,v> = sum conj(u_i) * v_i."""
    result = ZERO_Q
    for ui, vi in zip(u, v):
        result = q_add(result, q_mul(q_conj(ui), vi))
    return result


def are_orthogonal(u, v):
    """Check if two H^3 vectors are orthogonal."""
    ip = inner_product(u, v)
    return q_is_zero(ip)


def vec_norm_sq(v):
    """Squared norm of H^3 vector."""
    return sum(q_norm_sq(qi) for qi in v)


def vec_is_zero(v):
    return all(q_is_zero(qi) for qi in v)


def vec_right_mul(v, q):
    """Right-multiply H^3 vector by quaternion: (v1*q, v2*q, v3*q)."""
    return tuple(q_mul(vi, q) for vi in v)


# =====================================================================
# Ray canonicalization for H^3
# =====================================================================
# Two vectors represent the same ray if v = w*q for some nonzero q.
# For integer quaternions, canonicalize by:
# 1. Find first nonzero component
# 2. Make it "positive" by a canonical form
# 3. Normalize by GCD of all integer entries

def gcd(a, b):
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a

def gcd_list(nums):
    result = 0
    for n in nums:
        result = gcd(result, abs(n))
    return result if result > 0 else 1

def canonicalize_qvec(v):
    """Canonicalize a quaternionic ray.

    Strategy: flatten to 4*dim integers, divide by GCD, then choose
    sign so first nonzero entry is positive.
    """
    dim = len(v)
    # Flatten to 4*dim integers
    flat = []
    for qi in v:
        flat.extend(qi)

    # GCD normalize
    g = gcd_list(flat)
    flat = [c // g for c in flat]

    # Sign: first nonzero positive
    for c in flat:
        if c != 0:
            if c < 0:
                flat = [-x for x in flat]
            break

    # Reconstruct
    return tuple(tuple(flat[4*i:4*(i+1)]) for i in range(dim))


# =====================================================================
# Generate quaternionic ray pool
# =====================================================================
def generate_quat_pool(alphabet_quats, dim=3, norm_cutoff=None):
    """Generate all rays with components drawn from quaternion alphabet.

    alphabet_quats: list of quaternion 4-tuples
    Returns: list of canonicalized, deduplicated rays
    """
    seen = set()
    pool = []

    for combo in product(alphabet_quats, repeat=dim):
        v = combo
        if vec_is_zero(v):
            continue
        if norm_cutoff and vec_norm_sq(v) > norm_cutoff:
            continue
        cv = canonicalize_qvec(v)
        if cv not in seen:
            seen.add(cv)
            pool.append(cv)

    return pool


def build_pairs_triads(rays):
    """Build orthogonal pairs and triads."""
    n = len(rays)
    pairs = []
    adj = {i: set() for i in range(n)}

    for i in range(n):
        for j in range(i + 1, n):
            if are_orthogonal(rays[i], rays[j]):
                pairs.append((i, j))
                adj[i].add(j)
                adj[j].add(i)

    triads = []
    for i in range(n):
        neighbors_i = sorted(adj[i])
        for idx_j, j in enumerate(neighbors_i):
            if j <= i:
                continue
            for k in neighbors_i[idx_j + 1:]:
                if k <= j:
                    continue
                if k in adj[j]:
                    triads.append((i, j, k))

    return pairs, triads, adj


def is_ks_uncolorable(n, triads, pairs):
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


def greedy_minimize(n_rays, pairs, triads, n_trials=200):
    """Greedy deletion to find minimal KS subset."""
    best = list(range(n_rays))
    best_size = n_rays

    for trial in range(n_trials):
        current = list(range(n_rays))
        order = list(range(n_rays))
        random.shuffle(order)

        for candidate in order:
            if candidate not in current:
                continue
            test = [r for r in current if r != candidate]
            if len(test) < 10:
                break
            keep_set = set(test)
            remap = {old: new for new, old in enumerate(test)}
            sub_triads = [(remap[a], remap[b], remap[c])
                          for a, b, c in triads
                          if a in keep_set and b in keep_set and c in keep_set]
            sub_pairs = [(remap[i], remap[j])
                         for i, j in pairs
                         if i in keep_set and j in keep_set]
            if is_ks_uncolorable(len(test), sub_triads, sub_pairs):
                current = test

        if len(current) < best_size:
            best = current
            best_size = len(current)

    return best, best_size


# =====================================================================
# SECTION 1: Quaternion cancellation identities
# =====================================================================
print("=" * 70)
print("SECTION 1: Quaternion cancellation identities")
print("=" * 70)

print()
print("Key quaternion identities relevant to KS orthogonality:")
print("  |1|^2 = 1, |i|^2 = 1, |j|^2 = 1, |k|^2 = 1")
print("  |1+i|^2 = 2  (norm-2 cancellation)")
print("  |1+j|^2 = 2  (norm-2 cancellation)")
print("  |1+k|^2 = 2  (norm-2 cancellation)")
print("  |i+j|^2 = 2  (norm-2 cancellation)")
print("  |i+k|^2 = 2  (norm-2 cancellation)")
print("  |j+k|^2 = 2  (norm-2 cancellation)")
print()

# Verify: conj(i)*j + conj(j)*(-i) = (-i)*j + (-j)*(-i) = -ij + ji = -k + (-k) = -2k != 0
# So (i,j,0) and (j,-i,0) are NOT orthogonal over H
# But: conj(1)*1 + conj(i)*(-i) = 1 + (-i)(-i) = 1 + i^2 = 1 - 1 = 0
# So (1,i,0) and (1,-i,0) ARE orthogonal

print("Verification of key orthogonalities:")
test_pairs = [
    ((ONE_Q, I_Q, ZERO_Q), (ONE_Q, q_neg(I_Q), ZERO_Q), "(1,i,0) vs (1,-i,0)"),
    ((ONE_Q, J_Q, ZERO_Q), (ONE_Q, q_neg(J_Q), ZERO_Q), "(1,j,0) vs (1,-j,0)"),
    ((ONE_Q, K_Q, ZERO_Q), (ONE_Q, q_neg(K_Q), ZERO_Q), "(1,k,0) vs (1,-k,0)"),
    ((I_Q, J_Q, ZERO_Q), (J_Q, q_neg(I_Q), ZERO_Q), "(i,j,0) vs (j,-i,0)"),
    ((ONE_Q, ONE_Q, ZERO_Q), (ONE_Q, q_neg(ONE_Q), ZERO_Q), "(1,1,0) vs (1,-1,0)"),
]

for u, v, label in test_pairs:
    ip = inner_product(u, v)
    print(f"  {label}: <u,v> = {ip}, orthogonal = {q_is_zero(ip)}")

# Key non-commutativity test
print()
print("Non-commutativity effects on orthogonality:")
u = (I_Q, J_Q, ZERO_Q)
v = (J_Q, q_neg(I_Q), ZERO_Q)
ip_uv = inner_product(u, v)
ip_vu = inner_product(v, u)
print(f"  (i,j,0) vs (j,-i,0): <u,v>={ip_uv}, <v,u>={ip_vu}")
print(f"  Note: <v,u> = conj(<u,v>) = {q_conj(ip_uv)}")

# =====================================================================
# SECTION 2: Minimal quaternion alphabet {0, +/-1, +/-i, +/-j, +/-k}
# =====================================================================
print()
print("=" * 70)
print("SECTION 2: Quaternion unit alphabet {0, +/-1, +/-i, +/-j, +/-k}")
print("=" * 70)

quat_units = [
    ZERO_Q,
    ONE_Q, (-1, 0, 0, 0),
    I_Q, (0, -1, 0, 0),
    J_Q, (0, 0, -1, 0),
    K_Q, (0, 0, 0, -1),
]

t0 = time.time()
pool_units = generate_quat_pool(quat_units, dim=3)
t1 = time.time()
print(f"Pool size: {len(pool_units)} rays (generated in {t1-t0:.1f}s)")

# Count norms
norms = Counter(vec_norm_sq(v) for v in pool_units)
print(f"Squared norms: {dict(sorted(norms.items()))}")

t0 = time.time()
pairs_u, triads_u, adj_u = build_pairs_triads(pool_units)
t1 = time.time()
print(f"Orthogonal pairs: {len(pairs_u)}")
print(f"Orthogonal triads: {len(triads_u)}")
print(f"Pair/triad computation: {t1-t0:.1f}s")

if len(triads_u) > 0:
    ks = is_ks_uncolorable(len(pool_units), triads_u, pairs_u)
    print(f"KS-uncolorable: {ks}")

    if ks:
        print("Minimizing...")
        min_idx, min_n = greedy_minimize(len(pool_units), pairs_u, triads_u)
        min_rays = [pool_units[i] for i in min_idx]
        min_pairs, min_triads, min_adj = build_pairs_triads(min_rays)
        print(f"Minimal KS set: {min_n} vectors, {len(min_pairs)} pairs, "
              f"{len(min_triads)} triads")
else:
    print("No triads -- cannot be KS-uncolorable")

# =====================================================================
# SECTION 3: Compare with complex case
# =====================================================================
print()
print("=" * 70)
print("SECTION 3: Embedding comparison")
print("=" * 70)

print()
print("The quaternion unit alphabet {0,+/-1,+/-i,+/-j,+/-k} contains")
print("the integer alphabet {0,+/-1} and the Gaussian alphabet {0,+/-1,+/-i}")
print("as sub-alphabets.")
print()

# Sub-alphabet: just {0, +/-1} (integer)
int_alph = [ZERO_Q, ONE_Q, (-1, 0, 0, 0)]
pool_int = generate_quat_pool(int_alph, dim=3)
pairs_int, triads_int, _ = build_pairs_triads(pool_int)
ks_int = is_ks_uncolorable(len(pool_int), triads_int, pairs_int) if triads_int else False
print(f"Integer sub-alphabet {{0,+/-1}}: {len(pool_int)} rays, "
      f"{len(pairs_int)} pairs, {len(triads_int)} triads, KS={ks_int}")

# Sub-alphabet: {0, +/-1, +/-i} (Gaussian)
gauss_alph = [ZERO_Q, ONE_Q, (-1, 0, 0, 0), I_Q, (0, -1, 0, 0)]
pool_gauss = generate_quat_pool(gauss_alph, dim=3)
pairs_gauss, triads_gauss, _ = build_pairs_triads(pool_gauss)
ks_gauss = is_ks_uncolorable(len(pool_gauss), triads_gauss, pairs_gauss) if triads_gauss else False
print(f"Gaussian sub-alphabet {{0,+/-1,+/-i}}: {len(pool_gauss)} rays, "
      f"{len(pairs_gauss)} pairs, {len(triads_gauss)} triads, KS={ks_gauss}")

if ks_gauss:
    print("  Minimizing Gaussian sub-pool...")
    g_idx, g_n = greedy_minimize(len(pool_gauss), pairs_gauss, triads_gauss, n_trials=100)
    print(f"  Gaussian minimal: {g_n} vectors")

# =====================================================================
# SECTION 4: Targeted alphabets with norm-2 cancellation
# =====================================================================
print()
print("=" * 70)
print("SECTION 4: Targeted quaternion alphabets")
print("=" * 70)

# The key insight from C^3: {0,+/-1} alone is NOT KS-uncolorable (13 rays).
# Need +/-2 to get the 1+1=2 cancellation identity -> 49 rays -> KS at 31.
# For quaternions: try {0, +/-1, +/-2, +/-i, +/-j, +/-k}

TWO_Q = (2, 0, 0, 0)

alphabets_to_test = [
    ("Real integer {0,+/-1,+/-2}", [ZERO_Q, ONE_Q, (-1,0,0,0), TWO_Q, (-2,0,0,0)]),
    ("{0,+/-1,+/-2,+/-i}", [ZERO_Q, ONE_Q, (-1,0,0,0), TWO_Q, (-2,0,0,0),
                             I_Q, (0,-1,0,0)]),
    ("{0,+/-1,+/-2,+/-i,+/-j,+/-k}", [ZERO_Q, ONE_Q, (-1,0,0,0), TWO_Q, (-2,0,0,0),
                                         I_Q, (0,-1,0,0), J_Q, (0,0,-1,0),
                                         K_Q, (0,0,0,-1)]),
    ("{0,+/-1,+/-i,+/-2i}", [ZERO_Q, ONE_Q, (-1,0,0,0),
                               I_Q, (0,-1,0,0), (0,2,0,0), (0,-2,0,0)]),
    ("{0,+/-1,+/-2,+/-i,+/-2i,+/-j,+/-2j,+/-k,+/-2k}",
     [ZERO_Q, ONE_Q, (-1,0,0,0), TWO_Q, (-2,0,0,0),
      I_Q, (0,-1,0,0), (0,2,0,0), (0,-2,0,0),
      J_Q, (0,0,-1,0), (0,0,2,0), (0,0,-2,0),
      K_Q, (0,0,0,-1), (0,0,0,2), (0,0,0,-2)]),
]

for name, alph in alphabets_to_test:
    print(f"\n--- {name} ---")
    t0 = time.time()
    pool = generate_quat_pool(alph, dim=3, norm_cutoff=9)
    t1 = time.time()
    print(f"  Pool: {len(pool)} rays ({t1-t0:.1f}s)")

    if len(pool) > 1000:
        print(f"  Too large -- sampling 600 rays")
        sample_idx = random.sample(range(len(pool)), 600)
        sample_rays = [pool[i] for i in sample_idx]
        sp, st, sa = build_pairs_triads(sample_rays)
        ks = is_ks_uncolorable(len(sample_rays), st, sp) if st else False
        print(f"  Sample: {len(sp)} pairs, {len(st)} triads, KS={ks}")
        if ks:
            print("  Minimizing sample...")
            mi, mn = greedy_minimize(len(sample_rays), sp, st, n_trials=100)
            print(f"  Minimal: {mn}")
        continue

    t0 = time.time()
    pairs, triads, adj = build_pairs_triads(pool)
    t1 = time.time()
    print(f"  Pairs: {len(pairs)}, Triads: {len(triads)} ({t1-t0:.1f}s)")

    if not triads:
        print("  No triads -- not KS")
        continue

    ks = is_ks_uncolorable(len(pool), triads, pairs)
    print(f"  KS-uncolorable: {ks}")

    if ks:
        print("  Minimizing...")
        mi, mn = greedy_minimize(len(pool), pairs, triads, n_trials=300)
        min_rays = [pool[i] for i in mi]
        mp, mt, ma = build_pairs_triads(min_rays)
        print(f"  MINIMAL KS: {mn} vectors, {len(mp)} pairs, {len(mt)} triads")

        # Check if it uses quaternionic coordinates
        has_imag = False
        for v in min_rays:
            for qi in v:
                if qi[1] != 0 or qi[2] != 0 or qi[3] != 0:
                    has_imag = True
                    break
            if has_imag:
                break
        print(f"  Uses quaternionic (non-real) coords: {has_imag}")

# =====================================================================
# SECTION 5: Summary and analysis
# =====================================================================
print()
print("=" * 70)
print("SECTION 5: Analysis")
print("=" * 70)

print("""
Key observations:

1. CANCELLATION IDENTITIES in H:
   The quaternion units {1,i,j,k} all have norm 1.
   Norm-2 cancellations: |1+i|^2 = |1+j|^2 = |1+k|^2 = 2
   Non-commutativity creates ASYMMETRIC inner products:
     <(i,j,0),(j,-i,0)> = -2k != 0 (NOT orthogonal!)
   but conj(i)*i = |i|^2 = 1 and conj(j)*j = 1 still give
   standard cancellations like 1*1 + (-1)*1 = 0.

2. THE FUNDAMENTAL QUESTION:
   In C^3, CK-31 is the smallest known KS set.
   Can quaternionic coordinates produce smaller KS sets in H^3?

   Arguments FOR: more cancellation identities (6 norm-2 pairs
   vs 1 for integers), richer algebraic structure.

   Arguments AGAINST: quaternionic projective space HP^2 has
   projective dimension 8 (vs 4 for CP^2), giving more room
   for colorings. The non-commutativity also REDUCES some
   orthogonalities (e.g., (i,j,0) perp (j,-i,0) fails).

3. COMPARISON WITH KNOWN RESULTS:
   R^3: 49 rays in {0,+/-1,+/-2}, min KS = 31
   C^3: 57 rays in Eisenstein, min KS = 33
   H^3: 364 rays in {0,+/-1,+/-i,+/-j,+/-k}, 832 triads, colorable

   The quaternion unit pool has MANY more triads but is still
   colorable -- the non-commutativity disrupts interlocking.
""")

print("=" * 70)
print("DONE")
print("=" * 70)
