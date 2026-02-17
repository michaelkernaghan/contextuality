"""
ks_larger_alphabets.py -- Search for sub-31 KS sets with larger alphabets
=========================================================================

Strategy 3: Expand beyond tested alphabets.
  - Integer: {0,+-1,+-2} -> {0,+-1,+-2,+-3}, {0,+-1,+-2,+-3,+-4}
  - Peres: {0,+-1,+-sqrt2} -> add +-2, +-2sqrt2, etc.
  - Eisenstein: increase max_coeff and norm_cutoff
  - Mixed: {0,+-1,+-2,+-sqrt2}, {0,+-1,+-2,+-w}, etc.
  - Complex: various imaginary quadratic fields with larger alphabets

Also try Strategy 4 (non-algebraic): optimization-based search
  - Start from known KS set, perturb rays, try to reduce count
  - Simulated annealing on ray configurations
"""

import sys
sys.stdout.reconfigure(line_buffering=True)

import cmath
import math
import random
import time
from itertools import product as cartprod

from pysat.solvers import Glucose4

from ks_complex import (
    generate_eisenstein_rays,
    hermitian_dot,
    canonicalize_complex_ray,
)
from ks_new_islands import (
    generate_rays_from_alphabet,
    hermitian_completion,
)

random.seed(42)


def build_pairs_triads(rays, tol=1e-9):
    """Build orthogonal pairs and triads."""
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
        neighbors_i = sorted(adj[i])
        for idx_j, j in enumerate(neighbors_i):
            if j <= i:
                continue
            for k in neighbors_i[idx_j + 1:]:
                if k <= j:
                    continue
                if k in adj[j]:
                    triads.append((i, j, k))
    return pairs, triads


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


def greedy_minimize(n_rays, all_pairs, all_triads, n_trials=500, floor=20):
    """Greedy minimization."""
    best_size = n_rays
    for trial in range(n_trials):
        current = list(range(n_rays))
        random.shuffle(current)
        for candidate in list(current):
            test = [r for r in current if r != candidate]
            if len(test) < floor:
                break
            test_set = set(test)
            remap = {old: new for new, old in enumerate(test)}
            sub_triads = [(remap[a], remap[b], remap[c])
                          for a, b, c in all_triads
                          if a in test_set and b in test_set and c in test_set]
            sub_pairs = [(remap[i], remap[j])
                         for i, j in all_pairs
                         if i in test_set and j in test_set]
            if is_ks_uncolorable(len(test), sub_triads, sub_pairs):
                current = test
        if len(current) < best_size:
            best_size = len(current)
            print(f"      Trial {trial+1}: new best = {best_size}")
        if (trial + 1) % 100 == 0:
            print(f"      ... {trial+1}/{n_trials}, best = {best_size}")
    return best_size


def test_alphabet(name, alphabet, use_completion=False, n_trials=500):
    """Test a single alphabet configuration."""
    t0 = time.time()
    rays = generate_rays_from_alphabet(alphabet)
    if use_completion:
        rays = hermitian_completion(rays)
    t_gen = time.time() - t0

    n = len(rays)
    if n > 2000:
        print(f"  {name:<35} {n:>5} rays -- TOO LARGE, skipping")
        return None

    pairs, triads = build_pairs_triads(rays)
    ks = is_ks_uncolorable(n, triads, pairs)

    print(f"  {name:<35} {n:>5} rays, {len(pairs):>5}p, {len(triads):>4}t, "
          f"KS={'YES' if ks else 'no ':>3} [{t_gen:.1f}s]", end='')

    if ks:
        t0 = time.time()
        best = greedy_minimize(n, pairs, triads, n_trials=n_trials, floor=20)
        elapsed = time.time() - t0
        marker = " *** SUB-31! ***" if best < 31 else ""
        print(f"  -> min={best}{marker} [{elapsed:.1f}s]")
        return best
    else:
        print()
        return None


# =====================================================================
# Strategy 3a: Larger integer alphabets
# =====================================================================

print("=" * 70)
print("STRATEGY 3: LARGER ALPHABETS")
print("=" * 70)

print(f"\n--- 3a: Extended integer alphabets ---")

int_alphabets = [
    ("{0,+-1,+-2} (baseline)", [complex(x) for x in [0, 1, -1, 2, -2]]),
    ("{0,+-1,+-2,+-3}", [complex(x) for x in [0, 1, -1, 2, -2, 3, -3]]),
    ("{0,+-1,+-2,+-3,+-4}", [complex(x) for x in [0, 1, -1, 2, -2, 3, -3, 4, -4]]),
    ("{0,+-1,+-3}", [complex(x) for x in [0, 1, -1, 3, -3]]),
    ("{0,+-1,+-4}", [complex(x) for x in [0, 1, -1, 4, -4]]),
    ("{0,+-1,+-2,+-4}", [complex(x) for x in [0, 1, -1, 2, -2, 4, -4]]),
    ("{0,+-1,+-2,+-5}", [complex(x) for x in [0, 1, -1, 2, -2, 5, -5]]),
]

for name, alph in int_alphabets:
    test_alphabet(name, alph, n_trials=500)


# =====================================================================
# Strategy 3b: Extended Peres/sqrt(2) alphabets
# =====================================================================

print(f"\n--- 3b: Extended Peres alphabets ---")

s2 = math.sqrt(2)
peres_alphabets = [
    ("{0,+-1,+-sqrt2} (baseline)", [complex(x) for x in [0, 1, -1, s2, -s2]]),
    ("{0,+-1,+-sqrt2,+-2}", [complex(x) for x in [0, 1, -1, s2, -s2, 2, -2]]),
    ("{0,+-1,+-sqrt2,+-2,+-2sqrt2}", [complex(x) for x in [0, 1, -1, s2, -s2, 2, -2, 2*s2, -2*s2]]),
    ("{0,+-1,+-sqrt2,+-3}", [complex(x) for x in [0, 1, -1, s2, -s2, 3, -3]]),
]

for name, alph in peres_alphabets:
    test_alphabet(name, alph, n_trials=500)


# =====================================================================
# Strategy 3c: Extended Eisenstein alphabets
# =====================================================================

print(f"\n--- 3c: Extended Eisenstein alphabets ---")

eis_configs = [
    ("Eisenstein coeff=1 norm<=3 (base)", 1, 3),
    ("Eisenstein coeff=1 norm<=5", 1, 5),
    ("Eisenstein coeff=2 norm<=4", 2, 4),
    ("Eisenstein coeff=2 norm<=5", 2, 5),
    ("Eisenstein coeff=2 norm<=7", 2, 7),
    ("Eisenstein coeff=3 norm<=6", 3, 6),
]

for name, mc, nc in eis_configs:
    t0 = time.time()
    rays = generate_eisenstein_rays(max_coeff=mc, dim=3, norm_cutoff=nc)
    t_gen = time.time() - t0
    n = len(rays)
    if n > 2000:
        print(f"  {name:<35} {n:>5} rays -- TOO LARGE, skipping")
        continue
    pairs, triads = build_pairs_triads(rays)
    ks = is_ks_uncolorable(n, triads, pairs)
    print(f"  {name:<35} {n:>5} rays, {len(pairs):>5}p, {len(triads):>4}t, "
          f"KS={'YES' if ks else 'no ':>3} [{t_gen:.1f}s]", end='')
    if ks:
        t0 = time.time()
        best = greedy_minimize(n, pairs, triads, n_trials=500, floor=20)
        elapsed = time.time() - t0
        marker = " *** SUB-31! ***" if best < 31 else ""
        print(f"  -> min={best}{marker} [{elapsed:.1f}s]")
    else:
        print()


# =====================================================================
# Strategy 3d: Extended complex field alphabets
# =====================================================================

print(f"\n--- 3d: Extended complex field alphabets ---")

# Z[sqrt(-2)] extended
sd2 = cmath.sqrt(-2)
complex_alphabets = [
    ("{0,+-1,+-sqrt-2} (baseline)", [0, 1, -1, sd2, -sd2]),
    ("{0,+-1,+-sqrt-2,+-2}", [0, 1, -1, sd2, -sd2, 2, -2]),
    ("{0,+-1,+-sqrt-2,+-2,+-2sqrt-2}", [0, 1, -1, sd2, -sd2, 2, -2, 2*sd2, -2*sd2]),
]

for name, alph in complex_alphabets:
    test_alphabet(name, alph, n_trials=500)

# Heegner-7 extended
gen7 = (1 + cmath.sqrt(-7)) / 2
h7_alphabets = [
    ("Heegner-7 (baseline)", [0, 1, -1, gen7, -gen7, gen7.conjugate(), -gen7.conjugate()]),
    ("Heegner-7 + +-2", [0, 1, -1, gen7, -gen7, gen7.conjugate(), -gen7.conjugate(), 2, -2]),
]

for name, alph in h7_alphabets:
    test_alphabet(name, alph, n_trials=300)

# Golden ratio extended
phi = (1 + math.sqrt(5)) / 2
golden_alphabets = [
    ("Golden (baseline, +compl)", [complex(x) for x in [0, 1, -1, phi, -phi]], True),
    ("Golden + +-2 (+compl)", [complex(x) for x in [0, 1, -1, phi, -phi, 2, -2]], True),
    ("Golden + +-phi^2 (+compl)", [complex(x) for x in [0, 1, -1, phi, -phi, phi**2, -phi**2]], True),
]

for name, alph, compl in golden_alphabets:
    test_alphabet(name, alph, use_completion=compl, n_trials=300)


# =====================================================================
# Strategy 3e: Mixed-field alphabets
# =====================================================================

print(f"\n--- 3e: Mixed-field alphabets ---")

mixed_alphabets = [
    ("{0,+-1,+-2,+-sqrt2}", [complex(x) for x in [0, 1, -1, 2, -2, s2, -s2]]),
    ("{0,+-1,+-2,+-w}", [0, 1, -1, 2, -2, cmath.exp(2j*cmath.pi/3), -cmath.exp(2j*cmath.pi/3)]),
    ("{0,+-1,+-sqrt2,+-w}", [0, 1, -1, complex(s2), complex(-s2),
                        cmath.exp(2j*cmath.pi/3), -cmath.exp(2j*cmath.pi/3)]),
    ("{0,+-1,+-2,+-i}", [0, 1, -1, 2, -2, 1j, -1j]),
    ("{0,+-1,+-2,+-sqrt-2}", [0, 1, -1, 2, -2, sd2, -sd2]),
    ("{0,+-1,+-i,+-(1+i)}", [0, 1, -1, 1j, -1j, 1+1j, -1-1j]),
    ("{0,+-1,+-2,+-i,+-2i}", [0, 1, -1, 2, -2, 1j, -1j, 2j, -2j]),
]

for name, alph in mixed_alphabets:
    test_alphabet(name, alph, n_trials=500)


# =====================================================================
# Strategy 3f: Completion-expanded pools
# =====================================================================

print(f"\n--- 3f: Completion-expanded pools ---")

completion_alphabets = [
    ("{0,+-1,+-2} + completion", [complex(x) for x in [0, 1, -1, 2, -2]]),
    ("{0,+-1,+-sqrt2} + completion", [complex(x) for x in [0, 1, -1, s2, -s2]]),
    ("{0,+-1,+-2,+-3} + completion", [complex(x) for x in [0, 1, -1, 2, -2, 3, -3]]),
]

for name, alph in completion_alphabets:
    test_alphabet(name, alph, use_completion=True, n_trials=500)


print(f"\n{'='*70}")
print("LARGER ALPHABET SEARCH COMPLETE")
print("=" * 70)
