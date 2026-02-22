"""
ks_ck33_identify.py -- Identify CK-33 and compare with Eisenstein-33
====================================================================

CK-33 = Conway-Kochen 33-vector KS set (all real, {0,+/-1,+/-2} alphabet).
Proved rigid by Trandafir & Cabello (arXiv:2501.11640).

Questions:
1. Is CK-33 in our integer pool? (Yes -- same alphabet)
2. Is CK-33 graph-isomorphic to Eisenstein-33?
3. How do their structural properties compare?
4. Is CK-33 one of our 6 MUS sets in the integer pool?
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

import math
import random
import numpy as np
from itertools import combinations
from pysat.solvers import Glucose4

random.seed(42)


# =====================================================================
# CK-33 vectors from Trandafir & Cabello (arXiv:2501.11640)
# All real, components from {0, +/-1, +/-2}
# =====================================================================
CK33_VECS = [
    (0, 0, 1), (0, 1, -1), (0, 1, 0), (0, 1, 1),
    (1, -2, -1), (1, -2, 0), (1, -2, 1),
    (1, -1, -2), (1, -1, -1), (1, -1, 0), (1, -1, 1), (1, -1, 2),
    (1, 0, -2), (1, 0, -1), (1, 0, 0), (1, 0, 1), (1, 0, 2),
    (1, 1, -2), (1, 1, -1), (1, 1, 0), (1, 1, 1), (1, 1, 2),
    (1, 2, -1), (1, 2, 0), (1, 2, 1),
    (2, -1, -1), (2, -1, 0), (2, -1, 1),
    (2, 0, -1), (2, 0, 1),
    (2, 1, -1), (2, 1, 0), (2, 1, 1),
]


def dot_real(v1, v2):
    return sum(a * b for a, b in zip(v1, v2))


def hermitian_dot(v1, v2):
    return sum(a.conjugate() * b for a, b in zip(v1, v2))


def build_pairs_triads_real(rays):
    """Build orthogonal pairs and triads for real integer rays."""
    n = len(rays)
    pairs = []
    adj = {i: set() for i in range(n)}
    for i in range(n):
        for j in range(i + 1, n):
            if dot_real(rays[i], rays[j]) == 0:
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


def build_pairs_triads_complex(rays, tol=1e-9):
    """Build orthogonal pairs and triads for complex rays."""
    n = len(rays)
    pairs = []
    adj = {i: set() for i in range(n)}
    for i in range(n):
        for j in range(i + 1, n):
            if abs(hermitian_dot(rays[i], rays[j])) < tol:
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


def degree_sequence(adj, n):
    """Compute sorted degree sequence."""
    return sorted([len(adj[i]) for i in range(n)])


def canonicalize_real_ray(v):
    """Canonicalize a real ray: first nonzero positive, divide by GCD."""
    v = list(v)
    for i in range(len(v)):
        if v[i] != 0:
            if v[i] < 0:
                v = [-c for c in v]
            break
    g = 0
    for c in v:
        g = math.gcd(g, abs(c))
    if g > 0:
        v = [c // g for c in v]
    return tuple(v)


# =====================================================================
# Section 1: Verify CK-33
# =====================================================================
print("=" * 70)
print("SECTION 1: Verify CK-33 properties")
print("=" * 70)

assert len(CK33_VECS) == 33, f"Expected 33 vectors, got {len(CK33_VECS)}"

ck33_pairs, ck33_triads, ck33_adj = build_pairs_triads_real(CK33_VECS)
ck33_ks = is_ks_uncolorable(33, ck33_triads, ck33_pairs)

print(f"CK-33 vectors: {len(CK33_VECS)}")
print(f"Orthogonal pairs: {len(ck33_pairs)}")
print(f"Orthogonal triads: {len(ck33_triads)}")
print(f"KS-uncolorable: {ck33_ks}")
print(f"Degree sequence: {degree_sequence(ck33_adj, 33)}")

# Squared norms
norms_sq = [dot_real(v, v) for v in CK33_VECS]
from collections import Counter
norm_counts = Counter(norms_sq)
print(f"Squared norms: {dict(sorted(norm_counts.items()))}")

# =====================================================================
# Section 2: Build integer pool and check CK-33 membership
# =====================================================================
print()
print("=" * 70)
print("SECTION 2: CK-33 in our integer pool?")
print("=" * 70)

# Generate {0, +/-1, +/-2} integer pool (same as ks_islands.py)
def generate_integer_pool():
    """Generate all rays with components in {0, +/-1, +/-2}."""
    alphabet = [-2, -1, 0, 1, 2]
    raw = []
    for a in alphabet:
        for b in alphabet:
            for c in alphabet:
                if a == 0 and b == 0 and c == 0:
                    continue
                raw.append((a, b, c))

    # Canonicalize
    seen = set()
    pool = []
    for v in raw:
        cv = canonicalize_real_ray(v)
        if cv not in seen:
            seen.add(cv)
            pool.append(cv)
    return pool

int_pool = generate_integer_pool()
int_pool_canon = set(canonicalize_real_ray(v) for v in int_pool)
print(f"Integer pool size: {len(int_pool)}")

# Check each CK-33 vector
ck33_in_pool = 0
ck33_not_in_pool = []
for i, v in enumerate(CK33_VECS):
    cv = canonicalize_real_ray(v)
    if cv in int_pool_canon:
        ck33_in_pool += 1
    else:
        ck33_not_in_pool.append((i, v, cv))

print(f"CK-33 vectors in integer pool: {ck33_in_pool}/33")
if ck33_not_in_pool:
    print("Vectors NOT in pool:")
    for idx, v, cv in ck33_not_in_pool:
        print(f"  #{idx}: {v} -> canonical {cv}")

# =====================================================================
# Section 3: Build Eisenstein-33 and compare
# =====================================================================
print()
print("=" * 70)
print("SECTION 3: Compare CK-33 with Eisenstein-33")
print("=" * 70)

# Import Eisenstein construction
from ks_complex import generate_eisenstein_rays, canonicalize_complex_ray

eis_pool = generate_eisenstein_rays(max_coeff=1, dim=3, norm_cutoff=3)
eis_pairs, eis_triads, eis_adj = build_pairs_triads_complex(eis_pool)
print(f"Eisenstein pool: {len(eis_pool)} rays, {len(eis_pairs)} pairs, {len(eis_triads)} triads")

# Greedy minimize to get Eisenstein-33
def greedy_minimize(n_rays, pairs, triads, n_trials=500):
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
            if len(test) < 20:
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

eis_min_idx, eis_min_n = greedy_minimize(len(eis_pool), eis_pairs, eis_triads)
eis_min_rays = [eis_pool[i] for i in eis_min_idx]
eis_min_pairs, eis_min_triads, eis_min_adj = build_pairs_triads_complex(eis_min_rays)

print(f"Eisenstein-33: {eis_min_n} rays, {len(eis_min_pairs)} pairs, {len(eis_min_triads)} triads")
print(f"Eisenstein-33 degree sequence: {degree_sequence(eis_min_adj, eis_min_n)}")

# =====================================================================
# Section 4: Graph isomorphism test (degree sequence + spectral)
# =====================================================================
print()
print("=" * 70)
print("SECTION 4: Graph isomorphism test")
print("=" * 70)

# Build adjacency matrices
def adj_matrix(n, pairs):
    A = np.zeros((n, n))
    for i, j in pairs:
        A[i, j] = 1
        A[j, i] = 1
    return A

A_ck33 = adj_matrix(33, ck33_pairs)
A_eis33 = adj_matrix(eis_min_n, eis_min_pairs)

# Degree sequences
ds_ck33 = degree_sequence(ck33_adj, 33)
ds_eis33 = degree_sequence(eis_min_adj, eis_min_n)
print(f"CK-33 degree sequence:       {ds_ck33}")
print(f"Eisenstein-33 degree sequence: {ds_eis33}")
print(f"Same degree sequence: {ds_ck33 == ds_eis33}")

# Spectral comparison
eig_ck33 = sorted(np.linalg.eigvalsh(A_ck33))
eig_eis33 = sorted(np.linalg.eigvalsh(A_eis33))
spec_match = np.allclose(eig_ck33, eig_eis33, atol=1e-6)
print(f"Spectra match: {spec_match}")

if not spec_match:
    print("CK-33 and Eisenstein-33 are NOT graph-isomorphic (different spectra).")
    print(f"  CK-33 spectrum (first 10): {[f'{e:.4f}' for e in eig_ck33[:10]]}")
    print(f"  Eis-33 spectrum (first 10): {[f'{e:.4f}' for e in eig_eis33[:10]]}")

# Edge count comparison
print(f"\nCK-33: {len(ck33_pairs)} edges, {len(ck33_triads)} triads")
print(f"Eisenstein-33: {len(eis_min_pairs)} edges, {len(eis_min_triads)} triads")

# =====================================================================
# Section 5: Is CK-33 one of our 6 MUS sets?
# =====================================================================
print()
print("=" * 70)
print("SECTION 5: CK-33 vs MUS landscape")
print("=" * 70)

# CK-33 has 33 vectors but integer pool minimizes to 31
# So CK-33 is a non-minimal KS subset of the integer pool
# Check: can CK-33 be minimized further?
if ck33_ks:
    print("CK-33 is KS-uncolorable in the integer pool.")
    print("Attempting greedy minimization of CK-33...")

    ck33_min_idx, ck33_min_n = greedy_minimize(
        33, ck33_pairs, ck33_triads, n_trials=200)
    if ck33_min_n < 33:
        ck33_min_rays = [CK33_VECS[i] for i in ck33_min_idx]
        ck33_min_pairs, ck33_min_triads, _ = build_pairs_triads_real(ck33_min_rays)
        print(f"CK-33 minimizes to: {ck33_min_n} vectors, "
              f"{len(ck33_min_pairs)} pairs, {len(ck33_min_triads)} triads")
    else:
        print("CK-33 is already minimal (cannot remove any vector).")

# =====================================================================
# Section 6: Peres-33 comparison
# =====================================================================
print()
print("=" * 70)
print("SECTION 6: Peres-33 comparison")
print("=" * 70)

# Peres-33: real vectors with sqrt(2), from {0, +/-1, +/-sqrt(2)}
s2 = math.sqrt(2)
PERES_VECS = [
    (1, 0, 0), (0, 1, 0), (0, 0, 1),
    (1, 1, 0), (1, -1, 0), (1, 0, 1), (1, 0, -1), (0, 1, 1), (0, 1, -1),
    (1, 1, 1), (1, 1, -1), (1, -1, 1), (1, -1, -1),
    (s2, 1, 0), (s2, -1, 0), (s2, 0, 1), (s2, 0, -1),
    (0, s2, 1), (0, s2, -1), (1, 0, s2), (1, 0, -s2),
    (0, 1, s2), (0, 1, -s2),
    (1, s2, 0), (1, -s2, 0), (0, 1, 0),  # duplicate check
    (s2, 1, 1), (s2, 1, -1), (s2, -1, 1), (s2, -1, -1),
    (1, s2, 1), (1, s2, -1), (1, 1, s2),
]

# Use the Peres construction from our codebase (complex-typed)
from ks_new_islands import generate_rays_from_alphabet

peres_pool_alph = [complex(x) for x in [0, 1, -1, s2, -s2]]
peres_pool_raw = generate_rays_from_alphabet(peres_pool_alph, dim=3)

peres_p2, peres_t2, peres_a2 = build_pairs_triads_complex(peres_pool_raw)
print(f"Peres pool: {len(peres_pool_raw)} rays, "
      f"{len(peres_p2)} pairs, {len(peres_t2)} triads")

# Minimize Peres pool
peres_min_idx, peres_min_n = greedy_minimize(
    len(peres_pool_raw), peres_p2, peres_t2, n_trials=200)
peres_min_rays = [peres_pool_raw[i] for i in peres_min_idx]
peres_min_pairs, peres_min_triads, peres_min_adj = build_pairs_triads_complex(peres_min_rays)
print(f"Peres-33: {peres_min_n} rays, {len(peres_min_pairs)} pairs, "
      f"{len(peres_min_triads)} triads")
print(f"Peres-33 degree sequence: {degree_sequence(peres_min_adj, peres_min_n)}")

# Compare all three degree sequences
print()
print("=" * 70)
print("SECTION 7: Three-way comparison")
print("=" * 70)

print(f"{'Property':<30} {'CK-33':>10} {'Eisenstein-33':>15} {'Peres-33':>10}")
print("-" * 70)
print(f"{'Vectors':<30} {33:>10} {eis_min_n:>15} {peres_min_n:>10}")
print(f"{'Orthogonal pairs':<30} {len(ck33_pairs):>10} {len(eis_min_pairs):>15} {len(peres_min_pairs):>10}")
print(f"{'Triads':<30} {len(ck33_triads):>10} {len(eis_min_triads):>15} {len(peres_min_triads):>10}")
print(f"{'Field':<30} {'Z':>10} {'Z[omega]':>15} {'Z[sqrt(2)]':>10}")
print(f"{'Min degree':<30} {ds_ck33[0]:>10} {ds_eis33[0]:>15} {degree_sequence(peres_min_adj, peres_min_n)[0]:>10}")
print(f"{'Max degree':<30} {ds_ck33[-1]:>10} {ds_eis33[-1]:>15} {degree_sequence(peres_min_adj, peres_min_n)[-1]:>10}")

# Spectral comparison of all three
if peres_min_n == 33:
    A_peres33 = adj_matrix(33, peres_min_pairs)
    eig_peres33 = sorted(np.linalg.eigvalsh(A_peres33))

    ck_eis = np.allclose(eig_ck33, eig_eis33, atol=1e-6)
    ck_per = np.allclose(eig_ck33, eig_peres33, atol=1e-6)
    eis_per = np.allclose(eig_eis33, eig_peres33, atol=1e-6)

    print(f"\n{'Spectral comparison':}")
    print(f"  CK-33 ~ Eisenstein-33: {ck_eis}")
    print(f"  CK-33 ~ Peres-33:     {ck_per}")
    print(f"  Eisenstein-33 ~ Peres-33: {eis_per}")

# =====================================================================
# Section 8: VF2 graph isomorphism (if networkx available)
# =====================================================================
print()
print("=" * 70)
print("SECTION 8: VF2 graph isomorphism")
print("=" * 70)

try:
    import networkx as nx
    from networkx.algorithms.isomorphism import GraphMatcher

    def make_graph(n, pairs):
        G = nx.Graph()
        G.add_nodes_from(range(n))
        G.add_edges_from(pairs)
        return G

    G_ck33 = make_graph(33, ck33_pairs)
    G_eis33 = make_graph(eis_min_n, eis_min_pairs)

    iso_ck_eis = nx.is_isomorphic(G_ck33, G_eis33)
    print(f"CK-33 isomorphic to Eisenstein-33: {iso_ck_eis}")

    if peres_min_n == 33:
        G_peres33 = make_graph(33, peres_min_pairs)
        iso_ck_per = nx.is_isomorphic(G_ck33, G_peres33)
        iso_eis_per = nx.is_isomorphic(G_eis33, G_peres33)
        print(f"CK-33 isomorphic to Peres-33:     {iso_ck_per}")
        print(f"Eisenstein-33 isomorphic to Peres-33: {iso_eis_per}")

except ImportError:
    print("networkx not available -- skipping VF2 test")
    print("Install with: pip install networkx")

# =====================================================================
# Section 9: Summary
# =====================================================================
print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print("""
CK-33 (Conway-Kochen):
  - 33 real integer vectors from {0, +/-1, +/-2}
  - Subset of the same pool that contains CK-31
  - Proved rigid by Trandafir & Cabello (2025)
  - Historical: communicated by Conway & Kochen to Peres ~1990

Eisenstein-33 (this paper):
  - 33 complex vectors from Z[omega], omega = e^(2pi*i/3)
  - Components from {0, +/-1, +/-omega, +/-omega^2}
  - Cancellation: 1 + omega + omega^2 = 0
  - Proved rigid by our Jacobian analysis

The key question: are they the same graph?
If yes: CK-33 has a complex realization (Eisenstein) -- unexpected!
If no: they are genuinely different 33-vector KS sets.
""")
