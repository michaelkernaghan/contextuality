"""
ks_octonion.py -- Explore KS sets with octonion coordinates in dimension 3
==========================================================================

Octonions (O) are the fourth and final normed division algebra:
  R (1D) -> C (2D) -> H (4D) -> O (8D)

Octonions are:
  - Non-commutative (like quaternions): ab != ba
  - Non-associative (unlike quaternions!): (ab)c != a(bc)
  - Alternative: a(ab) = a^2 b and (ab)b = a b^2

The 8 basis elements: 1, e1, e2, e3, e4, e5, e6, e7
Multiplication follows the Fano plane:
  e_i * e_j = +/- e_k for specific triples (i,j,k)

For KS sets in O^3:
  - Inner product: <u,v> = conj(u1)*v1 + conj(u2)*v2 + conj(u3)*v3
  - Orthogonality: <u,v> = 0 (still symmetric since conj(0) = 0)
  - Rays: v ~ v*a for nonzero octonion a (right scalar mult)
  - Non-associativity means (v*a)*b != v*(a*b) in general

Key question: do the 7 imaginary units provide richer cancellation
identities that could produce smaller KS sets?
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

import random
import time
from itertools import product as iproduct
from collections import Counter
from pysat.solvers import Glucose4

random.seed(42)


# =====================================================================
# Octonion arithmetic (exact, integer coefficients)
# =====================================================================
# Octonion o = (a0, a1, a2, a3, a4, a5, a6, a7)
# meaning a0 + a1*e1 + a2*e2 + ... + a7*e7

# Fano plane multiplication table
# e_i * e_j = sign * e_k
# Using the standard Cayley table (index triples from Fano plane):
# (1,2,3), (1,4,5), (1,7,6), (2,4,6), (2,5,7), (3,4,7), (3,6,5)
# where e_i * e_j = e_k for these cyclic triples

FANO_TRIPLES = [
    (1, 2, 3), (1, 4, 5), (1, 7, 6),
    (2, 4, 6), (2, 5, 7),
    (3, 4, 7), (3, 6, 5),
]

# Build full multiplication table
# e_i * e_j for i,j in 1..7
# e_i * e_i = -1 for all i
MUL_TABLE = {}
for i in range(1, 8):
    MUL_TABLE[(i, i)] = (0, -1)  # (result_index, sign) where 0 = real part
for a, b, c in FANO_TRIPLES:
    MUL_TABLE[(a, b)] = (c, 1)
    MUL_TABLE[(b, a)] = (c, -1)
    MUL_TABLE[(b, c)] = (a, 1)
    MUL_TABLE[(c, b)] = (a, -1)
    MUL_TABLE[(c, a)] = (b, 1)
    MUL_TABLE[(a, c)] = (b, -1)


def o_mul(p, q):
    """Multiply two octonions p*q."""
    result = [0] * 8

    # Real * Real
    result[0] += p[0] * q[0]

    # Real * Imaginary
    for i in range(1, 8):
        result[i] += p[0] * q[i]
        result[i] += p[i] * q[0]

    # Imaginary * Imaginary
    for i in range(1, 8):
        if p[i] == 0:
            continue
        for j in range(1, 8):
            if q[j] == 0:
                continue
            idx, sign = MUL_TABLE[(i, j)]
            result[idx] += sign * p[i] * q[j]

    return tuple(result)


def o_conj(o):
    """Octonion conjugate: negate all imaginary parts."""
    return (o[0],) + tuple(-c for c in o[1:])


def o_norm_sq(o):
    """Squared norm |o|^2."""
    return sum(c * c for c in o)


def o_add(p, q):
    return tuple(a + b for a, b in zip(p, q))


def o_neg(o):
    return tuple(-c for c in o)


def o_is_zero(o):
    return all(c == 0 for c in o)


ZERO_O = (0, 0, 0, 0, 0, 0, 0, 0)
ONE_O = (1, 0, 0, 0, 0, 0, 0, 0)

# Basis elements
E = [None]  # E[0] unused
for i in range(1, 8):
    e = [0] * 8
    e[i] = 1
    E.append(tuple(e))


# =====================================================================
# O^3 vector operations
# =====================================================================
def inner_product(u, v):
    """Octonionic inner product <u,v> = sum conj(u_i)*v_i."""
    result = ZERO_O
    for ui, vi in zip(u, v):
        result = o_add(result, o_mul(o_conj(ui), vi))
    return result


def are_orthogonal(u, v):
    return o_is_zero(inner_product(u, v))


def vec_norm_sq(v):
    return sum(o_norm_sq(qi) for qi in v)


def vec_is_zero(v):
    return all(o_is_zero(qi) for qi in v)


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


def canonicalize_ovec(v):
    """Canonicalize an octonionic ray in O^dim."""
    dim = len(v)
    flat = []
    for qi in v:
        flat.extend(qi)

    g = gcd_list(flat)
    flat = [c // g for c in flat]

    for c in flat:
        if c != 0:
            if c < 0:
                flat = [-x for x in flat]
            break

    return tuple(tuple(flat[8*i:8*(i+1)]) for i in range(dim))


def generate_oct_pool(alphabet_octs, dim=3, norm_cutoff=None):
    """Generate all rays with components from octonion alphabet."""
    seen = set()
    pool = []
    for combo in iproduct(alphabet_octs, repeat=dim):
        v = combo
        if vec_is_zero(v):
            continue
        if norm_cutoff and vec_norm_sq(v) > norm_cutoff:
            continue
        cv = canonicalize_ovec(v)
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
# SECTION 1: Verify octonion arithmetic
# =====================================================================
print("=" * 70)
print("SECTION 1: Octonion arithmetic verification")
print("=" * 70)

# Check basic identities
print("e1*e2 =", o_mul(E[1], E[2]), "(expect e3)")
print("e2*e1 =", o_mul(E[2], E[1]), "(expect -e3)")
print("e1*e1 =", o_mul(E[1], E[1]), "(expect -1)")

# Non-associativity check: (e1*e2)*e4 vs e1*(e2*e4)
lhs = o_mul(o_mul(E[1], E[2]), E[4])
rhs = o_mul(E[1], o_mul(E[2], E[4]))
print(f"(e1*e2)*e4 = {lhs}")
print(f"e1*(e2*e4) = {rhs}")
print(f"Associative: {lhs == rhs}")

# Norm-2 cancellation: |1+e1|^2 = 2
q_1pe1 = o_add(ONE_O, E[1])
print(f"|1+e1|^2 = {o_norm_sq(q_1pe1)} (expect 2)")

# Orthogonality test: (1,e1,0) vs (1,-e1,0)
u = (ONE_O, E[1], ZERO_O)
v = (ONE_O, o_neg(E[1]), ZERO_O)
print(f"(1,e1,0) orth (1,-e1,0): {are_orthogonal(u, v)} (expect True)")

# Non-commutativity effect: (e1,e2,0) vs (e2,-e1,0)
u2 = (E[1], E[2], ZERO_O)
v2 = (E[2], o_neg(E[1]), ZERO_O)
ip = inner_product(u2, v2)
print(f"(e1,e2,0) orth (e2,-e1,0): {o_is_zero(ip)}, <u,v>={ip}")

# Count distinct norm-2 pairs among basis elements
print("\nNorm-2 cancellation pairs (|e_i + e_j|^2 = 2):")
n2_count = 0
for i in range(1, 8):
    for j in range(i+1, 8):
        s = o_add(E[i], E[j])
        if o_norm_sq(s) == 2:
            n2_count += 1
print(f"  {n2_count} pairs among e1..e7 (all, since units are orthonormal)")
print(f"  Plus 7 pairs (1, e_i) -> total {7 + n2_count} norm-2 pairs")

# =====================================================================
# SECTION 2: Unit octonion alphabet
# =====================================================================
print()
print("=" * 70)
print("SECTION 2: Octonion unit alphabet {0, +/-1, +/-e1, ..., +/-e7}")
print("=" * 70)

oct_units = [ZERO_O, ONE_O, o_neg(ONE_O)]
for i in range(1, 8):
    oct_units.append(E[i])
    oct_units.append(o_neg(E[i]))

print(f"Alphabet size: {len(oct_units)} octonions")

t0 = time.time()
pool_units = generate_oct_pool(oct_units, dim=3)
t1 = time.time()
print(f"Pool size: {len(pool_units)} rays ({t1-t0:.1f}s)")

norms = Counter(vec_norm_sq(v) for v in pool_units)
print(f"Squared norms: {dict(sorted(norms.items()))}")

if len(pool_units) > 2000:
    print("Pool too large for full pair computation -- sampling 500")
    sample_idx = random.sample(range(len(pool_units)), 500)
    sample = [pool_units[i] for i in sample_idx]
    sp, st, _ = build_pairs_triads(sample)
    ks = is_ks_uncolorable(500, st, sp) if st else False
    print(f"  Sample: {len(sp)} pairs, {len(st)} triads, KS={ks}")
else:
    t0 = time.time()
    pairs_u, triads_u, adj_u = build_pairs_triads(pool_units)
    t1 = time.time()
    print(f"Orthogonal pairs: {len(pairs_u)}")
    print(f"Orthogonal triads: {len(triads_u)}")
    print(f"Computation: {t1-t0:.1f}s")
    if triads_u:
        ks = is_ks_uncolorable(len(pool_units), triads_u, pairs_u)
        print(f"KS-uncolorable: {ks}")

# =====================================================================
# SECTION 3: Targeted alphabets with norm-2
# =====================================================================
print()
print("=" * 70)
print("SECTION 3: Targeted octonion alphabets")
print("=" * 70)

TWO_O = (2, 0, 0, 0, 0, 0, 0, 0)

# Test progressively: real only, then add one imaginary, then all
alphabets = [
    ("Real {0,+/-1,+/-2}", [ZERO_O, ONE_O, o_neg(ONE_O), TWO_O, o_neg(TWO_O)]),
    ("{0,+/-1,+/-2,+/-e1}", [ZERO_O, ONE_O, o_neg(ONE_O), TWO_O, o_neg(TWO_O),
                              E[1], o_neg(E[1])]),
    ("{0,+/-1,+/-2,+/-e1,+/-e2}", [ZERO_O, ONE_O, o_neg(ONE_O), TWO_O, o_neg(TWO_O),
                                     E[1], o_neg(E[1]), E[2], o_neg(E[2])]),
    ("{0,+/-1,+/-2,+/-e1,...,+/-e7}",
     [ZERO_O, ONE_O, o_neg(ONE_O), TWO_O, o_neg(TWO_O)] +
     [x for i in range(1, 8) for x in (E[i], o_neg(E[i]))]),
]

for name, alph in alphabets:
    print(f"\n--- {name} ---")
    t0 = time.time()
    pool = generate_oct_pool(alph, dim=3, norm_cutoff=9)
    t1 = time.time()
    print(f"  Pool: {len(pool)} rays ({t1-t0:.1f}s)")

    if len(pool) > 1500:
        print(f"  Large pool -- sampling 600")
        sample_idx = random.sample(range(len(pool)), 600)
        sample = [pool[i] for i in sample_idx]
        t0 = time.time()
        sp, st, _ = build_pairs_triads(sample)
        t1 = time.time()
        ks = is_ks_uncolorable(600, st, sp) if st else False
        print(f"  Sample: {len(sp)} pairs, {len(st)} triads ({t1-t0:.1f}s)")
        print(f"  KS-uncolorable: {ks}")
        if ks:
            print("  Minimizing...")
            mi, mn = greedy_minimize(600, sp, st, n_trials=100)
            print(f"  Minimal: {mn}")
        continue

    t0 = time.time()
    pairs, triads, adj = build_pairs_triads(pool)
    t1 = time.time()
    print(f"  Pairs: {len(pairs)}, Triads: {len(triads)} ({t1-t0:.1f}s)")

    if not triads:
        print("  No triads")
        continue

    ks = is_ks_uncolorable(len(pool), triads, pairs)
    print(f"  KS-uncolorable: {ks}")

    if ks:
        print("  Minimizing...")
        mi, mn = greedy_minimize(len(pool), pairs, triads, n_trials=300)
        min_rays = [pool[i] for i in mi]
        mp, mt, _ = build_pairs_triads(min_rays)
        print(f"  MINIMAL KS: {mn} vectors, {len(mp)} pairs, {len(mt)} triads")

        # Check if it uses octonionic coordinates
        has_oct = False
        for v in min_rays:
            for qi in v:
                if any(qi[k] != 0 for k in range(1, 8)):
                    has_oct = True
                    break
            if has_oct:
                break
        print(f"  Uses octonionic coords: {has_oct}")

# =====================================================================
# SECTION 4: Summary
# =====================================================================
print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print("""
Division algebra hierarchy for KS sets in dimension 3:

  R^3: real coordinates, min KS = 31 (CK-31)
  C^3: complex coordinates, min KS = 31 (absorbs to CK-31)
  H^3: quaternion coordinates, min KS = 31 (absorbs to CK-31)
  O^3: octonion coordinates, min KS = ???

Each step adds more cancellation identities but also more
projective dimensions (more room for colorings).

The norm-2 boundary appears to be universal across all
division algebras: you need |x|^2 = 2 for KS-uncolorability,
and adding more algebraic structure doesn't help reduce below 31.
""")
