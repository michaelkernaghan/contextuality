"""
KS coloring test - tests whether a set of rays admits a consistent
noncontextual value assignment (one green per orthogonal triad).

Based on the algorithm from: A. Peres, "Quantum Theory: Concepts and Methods"
(Kluwer, 1993), Appendix to Chapter 7.

Rewritten as clean recursive backtracking for correctness.

Color code: UNCOLORED = -1, GREEN = 1, RED = 0
"""

import math


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
    """
    Propagate constraints:
    - Orthogonal to green -> red
    - Two reds in a triad -> third must be green
    Returns False if contradiction found (three reds in a triad).
    """
    changed = True
    while changed:
        changed = False
        # Green forces orthogonal rays to red
        for i in range(n):
            if C[i] == 1:
                for j in range(i + 1, n):
                    if P[i][j] == 1:
                        if C[j] == 1:
                            return False  # two orthogonal greens
                        if C[j] == -1:
                            C[j] = 0
                            changed = True
        # Two reds in triad force third to green
        for triad in triads:
            vals = [C[triad[0]], C[triad[1]], C[triad[2]]]
            reds = vals.count(0)
            greens = vals.count(1)
            uncolored = vals.count(-1)
            if reds >= 3:
                return False  # contradiction
            if greens >= 2:
                return False  # contradiction: two greens in same triad
            if reds == 2 and uncolored == 1:
                for idx in triad:
                    if C[idx] == -1:
                        C[idx] = 1
                        changed = True
                        break
        # Check for contradictions
        for triad in triads:
            vals = [C[triad[0]], C[triad[1]], C[triad[2]]]
            if vals.count(0) == 3:
                return False
            if vals.count(1) >= 2:
                return False
    return True


def solve(C, P, triads, n):
    """Recursive backtracking search for consistent coloring."""
    # Propagate current constraints
    if not propagate(C, P, triads, n):
        return False

    # Find first uncolored ray
    pick = -1
    for i in range(n):
        if C[i] == -1:
            pick = i
            break

    if pick == -1:
        # All colored - verify
        for triad in triads:
            greens = sum(1 for idx in triad if C[idx] == 1)
            if greens != 1:
                return False
        return True

    # Try green
    saved = C[:]
    C[pick] = 1
    if solve(C, P, triads, n):
        return True

    # Restore and try red
    for i in range(n):
        C[i] = saved[i]
    C[pick] = 0
    if solve(C, P, triads, n):
        return True

    # Both failed - restore and backtrack
    for i in range(n):
        C[i] = saved[i]
    return False


def ks_coloring_test(vectors, label=""):
    n = len(vectors)
    P = build_orthogonality_matrix(vectors)
    triads = find_triads(P, n)
    pairs = sum(sum(row) for row in P) // 2

    print(f"  Rays: {n}, Orthogonal pairs: {pairs}, Triads: {len(triads)}")

    C = [-1] * n
    found = solve(C, P, triads, n)

    if found:
        green_rays = [i + 1 for i in range(n) if C[i] == 1]
        print(f"  Result: COLORABLE  (green rays: {green_rays})")
    else:
        print(f"  Result: NO CONSISTENT COLORING")
    return found


# ============================================================
# Peres 33-vector set
# ============================================================

S2 = math.sqrt(2)

PERES_33 = [
    (1, 0, 0), (0, 1, 0), (0, 0, 1),                           # axes
    (1, 1, 0), (1, -1, 0), (1, 0, 1), (1, 0, -1),              # face diag
    (0, 1, 1), (0, 1, -1),
    (S2, 1, 0), (S2, -1, 0), (1, S2, 0), (1, -S2, 0),          # mixed
    (S2, 0, 1), (S2, 0, -1), (1, 0, S2), (1, 0, -S2),
    (0, S2, 1), (0, S2, -1), (0, 1, S2), (0, 1, -S2),
    (1, 1, S2), (1, -1, S2), (1, 1, -S2), (1, -1, -S2),        # type IV
    (1, S2, 1), (1, S2, -1), (1, -S2, 1), (1, -S2, -1),
    (S2, 1, 1), (S2, 1, -1), (S2, -1, 1), (S2, -1, -1),
]


if __name__ == "__main__":
    print("=" * 60)
    print("Kochen-Specker Coloring Test")
    print("=" * 60)

    print("\nTest 1: Peres 33-vector set (should be UN-colorable)")
    ks_coloring_test(PERES_33)

    print("\nTest 2: Peres 33 minus last ray (should be colorable)")
    ks_coloring_test(PERES_33[:-1])

    print("\nTest 3: Just the 3 coordinate axes (trivially colorable)")
    ks_coloring_test([(1, 0, 0), (0, 1, 0), (0, 0, 1)])
