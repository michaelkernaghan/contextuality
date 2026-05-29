"""
Find explicit {0,1}-colorings for the two raw-colorable alphabets where
Step 2's structural argument (no type-B triads) fails:

  A. Gaussian: x = 1 + i  (d = -1)
  B. Heegner-7 halfint: x = (1 + sqrt(-7))/2  (d = -7)

Both have |x|^2 = 2 but Tr(x) != 0, so the Row-2 vanishing sum
(1 + 1 - |x|^2 = 0) creates type-B triads despite the raw set being
colorable. We exhibit concrete colorings and verify them.
"""

import cmath
import math
from itertools import product
from pysat.solvers import Glucose4
from itertools import combinations


def generate_rays(alphabet):
    """Generate all projective rays from alphabet^3, canonicalized by first nonzero."""
    rays = []
    seen = set()
    for v in product(alphabet, repeat=3):
        if all(abs(c) < 1e-12 for c in v):
            continue
        for c in v:
            if abs(c) > 1e-12:
                pivot = c
                break
        canonical = tuple(c / pivot for c in v)
        key = tuple((round(c.real, 9), round(c.imag, 9)) for c in canonical)
        if key not in seen:
            seen.add(key)
            rays.append(canonical)
    return rays


def original_vector(canonical_ray, alphabet):
    """Find an 'original' vector in alphabet^3 representing the given canonical ray."""
    tol = 1e-8
    for v in product(alphabet, repeat=3):
        if all(abs(c) < 1e-12 for c in v):
            continue
        for c in v:
            if abs(c) > 1e-12:
                pivot = c
                break
        canon = tuple(c / pivot for c in v)
        if all(abs(canon[j] - canonical_ray[j]) < tol for j in range(3)):
            return v
    return canonical_ray


def hdot(a, b):
    return sum(ak.conjugate() * bk for ak, bk in zip(a, b))


def build_pairs_triads(rays):
    tol = 1e-9
    n = len(rays)
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            if abs(hdot(rays[i], rays[j])) < tol:
                pairs.append((i, j))
    pair_set = set(pairs)

    triads = []
    for i in range(n):
        for j in range(i + 1, n):
            if (i, j) not in pair_set:
                continue
            for k in range(j + 1, n):
                if (i, k) in pair_set and (j, k) in pair_set:
                    triads.append((i, j, k))
    return pairs, triads


def find_coloring(n, pairs, triads):
    """Return a valid {0,1}-coloring as a list of length n, or None if unsat."""
    triad_pair_set = set()
    clauses = []
    for a, b, c in triads:
        A, B, C = a + 1, b + 1, c + 1
        clauses.append([A, B, C])
        clauses.append([-A, -B])
        clauses.append([-A, -C])
        clauses.append([-B, -C])
        for x, y in combinations([a, b, c], 2):
            triad_pair_set.add((min(x, y), max(x, y)))
    for a, b in pairs:
        if (min(a, b), max(a, b)) not in triad_pair_set:
            clauses.append([-(a + 1), -(b + 1)])

    with Glucose4() as solver:
        for c in clauses:
            solver.add_clause(c)
        if not solver.solve():
            return None
        model = solver.get_model()
        return [1 if (i + 1) in model else 0 for i in range(n)]


def verify_coloring(rays, pairs, triads, coloring):
    """Manually verify that a coloring satisfies all KS constraints."""
    errors = []
    for a, b in pairs:
        if coloring[a] == 1 and coloring[b] == 1:
            errors.append(f"Pair ({a},{b}) both 1")
    for a, b, c in triads:
        s = coloring[a] + coloring[b] + coloring[c]
        if s != 1:
            errors.append(f"Triad ({a},{b},{c}) has sum {s}, need 1")
    return errors


def analyze(label, x, alphabet):
    print("\n" + "=" * 70)
    print(f"Case: {label}")
    print(f"  x = {x}")
    print(f"  |x|^2 = {abs(x)**2:.6f}")
    print("=" * 70)

    rays = generate_rays(alphabet)
    pairs, triads = build_pairs_triads(rays)
    print(f"  {len(rays)} rays, {len(pairs)} orthogonal pairs, {len(triads)} triads")

    coloring = find_coloring(len(rays), pairs, triads)
    if coloring is None:
        print("  RESULT: UNSAT (KS-uncolorable) -- unexpected!")
        return

    errors = verify_coloring(rays, pairs, triads, coloring)
    if errors:
        print("  Manual verification FAILED:")
        for e in errors[:5]:
            print(f"    {e}")
        return

    n_green = sum(coloring)
    print(f"  Valid coloring found: {n_green} green rays (f=1), {len(rays)-n_green} red rays (f=0)")
    print(f"  Manually verified: all {len(pairs)} pair constraints hold, all {len(triads)} triads have sum=1")

    print("\n  Green rays (f=1) in canonical form:")
    green_indices = [i for i, c in enumerate(coloring) if c == 1]
    for idx in green_indices:
        orig = original_vector(rays[idx], alphabet)
        orig_str = "(" + ", ".join(
            ("0" if abs(c) < 1e-9 else f"{c.real:+.4g}" if abs(c.imag) < 1e-9 else f"{c.real:+.4g}{c.imag:+.4g}i")
            for c in orig
        ) + ")"
        canon_str = "(" + ", ".join(
            ("0" if abs(c) < 1e-9 else f"{c.real:+.4g}" if abs(c.imag) < 1e-9 else f"{c.real:+.4g}{c.imag:+.4g}i")
            for c in rays[idx]
        ) + ")"
        print(f"    ray {idx:2d}: canonical {canon_str}   original-vector {orig_str}")


def main():
    print("EXPLICIT COLORINGS FOR RAW-COLORABLE |x|^2=2 ALPHABETS")
    print("These are the two cases where Step 2's 'no type-B triads' claim fails.")

    # Case A: Gaussian d=-1, x = 1+i
    analyze("Gaussian (d=-1)", complex(1, 1), [0, 1, -1, 1 + 1j, -(1 + 1j)])

    # Case B: Heegner-7 halfint d=-7, x = (1+sqrt(-7))/2
    h7 = complex(0.5, math.sqrt(7) / 2)
    analyze("Heegner-7 halfint (d=-7)", h7, [0, 1, -1, h7, -h7])


if __name__ == "__main__":
    main()
