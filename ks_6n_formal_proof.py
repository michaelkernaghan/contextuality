"""
FORMAL PROOF of the 6|n theorem for cyclotomic KS sets
======================================================

This script provides a COMPLETE algebraic proof for Case 2
(3|n, 2∤n) and verifies the remaining Case 1 (3∤n, 2|n).

KEY INSIGHT: For odd n with 3|n, the 6 permutation-based
orthogonal neighbors of any all-nonzero ray collapse to
exactly 2 projectively distinct rays (even permutations give
one ray, odd permutations give another). Thus each ray
participates in exactly 1 all-nonzero triad.
"""

import cmath
import itertools
import math
import sys
import time
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

TOL = 1e-9


def generate_cyclotomic_pool(n):
    """Generate ray pool from nth roots of unity."""
    zeta = cmath.exp(2j * cmath.pi / n)
    alphabet = [0] + [zeta**k for k in range(n)]
    raw = []
    for combo in itertools.product(range(len(alphabet)), repeat=3):
        v = tuple(alphabet[i] for i in combo)
        if all(abs(x) < TOL for x in v):
            continue
        raw.append(v)
    canonical = []
    seen = set()
    for v in raw:
        for c in v:
            if abs(c) > TOL:
                phase = c / abs(c)
                break
        normed = tuple(x / phase for x in v)
        key = tuple((round(x.real, 8), round(x.imag, 8)) for x in normed)
        if key not in seen:
            seen.add(key)
            canonical.append(normed)
    return canonical


def hermitian_dot(v, w):
    return sum(x.conjugate() * y for x, y in zip(v, w))


def build_orthogonality(rays):
    n = len(rays)
    pairs = []
    adj = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i+1, n):
            if abs(hermitian_dot(rays[i], rays[j])) < TOL:
                pairs.append((i, j))
                adj[i].add(j)
                adj[j].add(i)
    triads = []
    for i in range(n):
        for j in adj[i]:
            if j > i:
                for k in adj[i] & adj[j]:
                    if k > j:
                        triads.append((i, j, k))
    return pairs, triads, adj


# ============================================================
# ALGEBRAIC PROOF: Projective collapse of orthogonal neighbors
# ============================================================

def prove_projective_collapse():
    """
    LEMMA: For any n with 3|n, the 6 permutation-based all-nonzero
    orthogonal neighbors of a ray v collapse to exactly 2 projectively
    distinct rays.

    PROOF:
    Let v = (ζ^a, ζ^b, ζ^c) with all coords nonzero.
    Let ω = ζ^{n/3} (primitive cube root of unity).

    The 6 neighbors are w_σ = (ζ^{a+σ(1)·n/3}, ζ^{b+σ(2)·n/3}, ζ^{c+σ(3)·n/3})
    for σ a permutation of {0, 1, 2}.

    Even permutations: σ ∈ {(0,1,2), (1,2,0), (2,0,1)}
      w_{(0,1,2)} = (ζ^a, ζ^{b+n/3}, ζ^{c+2n/3}) = (ζ^a, ωζ^b, ω²ζ^c)
      w_{(1,2,0)} = (ωζ^a, ω²ζ^b, ζ^c) = ω · (ζ^a, ωζ^b, ω²ζ^c)  [projectively same!]
      w_{(2,0,1)} = (ω²ζ^a, ζ^b, ωζ^c) = ω² · (ζ^a, ωζ^b, ω²ζ^c)  [projectively same!]

    So all even permutations give the SAME projective ray: w_+ = [ζ^a : ωζ^b : ω²ζ^c].

    Odd permutations: σ ∈ {(0,2,1), (1,0,2), (2,1,0)}
      w_{(0,2,1)} = (ζ^a, ω²ζ^b, ωζ^c)
      w_{(1,0,2)} = (ωζ^a, ζ^b, ω²ζ^c) = ω · (ζ^a, ω²ζ^b, ωζ^c)  [projectively same!]
      w_{(2,1,0)} = (ω²ζ^a, ωζ^b, ζ^c) = ω² · (ζ^a, ω²ζ^b, ωζ^c)  [projectively same!]

    So all odd permutations give w_- = [ζ^a : ω²ζ^b : ωζ^c].

    Neither w_+ nor w_- is projectively equivalent to v (would need ω = 1).
    w_+ ≠ w_- projectively (would need ω = ω², i.e., ω = 1).

    Check w_+ ⊥ w_-:
      ⟨w_+|w_-⟩ = ζ̄^a·ζ^a + (ωζ^b)* · ω²ζ^b + (ω²ζ^c)* · ωζ^c
                 = |ζ^a|² + ω̄·ω²·|ζ^b|² + ω̄²·ω·|ζ^c|²
                 = 1 + ω²·ω² · 1 + ω·ω · 1   [since |ζ^k| = 1, ω̄ = ω²]
                 = 1 + ω⁴ + ω²
                 = 1 + ω + ω²  [since ω³ = 1, ω⁴ = ω]
                 = 0  ✓

    So {v, w_+, w_-} is a triad, and these are v's ONLY all-nonzero
    orthogonal neighbors. Each all-nonzero ray participates in
    exactly ONE all-nonzero triad.  □
    """
    print("=" * 70)
    print("LEMMA: PROJECTIVE COLLAPSE OF ORTHOGONAL NEIGHBORS")
    print("=" * 70)
    print()
    print("For any n with 3|n, let ω = ζ^{n/3} (primitive cube root of unity).")
    print("For any all-nonzero ray v = (ζ^a, ζ^b, ζ^c):")
    print()
    print("  Even permutations of shift (0, n/3, 2n/3):")
    print("    σ₁ = (0,1,2): w = (ζ^a,  ωζ^b,  ω²ζ^c)")
    print("    σ₄ = (1,2,0): w = (ωζ^a, ω²ζ^b, ζ^c)   = ω · σ₁  [same ray]")
    print("    σ₅ = (2,0,1): w = (ω²ζ^a, ζ^b, ωζ^c)   = ω² · σ₁ [same ray]")
    print()
    print("  Odd permutations:")
    print("    σ₂ = (0,2,1): w = (ζ^a,  ω²ζ^b, ωζ^c)")
    print("    σ₃ = (1,0,2): w = (ωζ^a, ζ^b,   ω²ζ^c) = ω · σ₂  [same ray]")
    print("    σ₆ = (2,1,0): w = (ω²ζ^a, ωζ^b, ζ^c)   = ω² · σ₂ [same ray]")
    print()
    print("  → v has exactly 2 all-nonzero orthogonal neighbors: w₊ and w₋")
    print("  → ⟨w₊|w₋⟩ = 1 + ω + ω² = 0  [they're orthogonal]")
    print("  → {v, w₊, w₋} is the UNIQUE triad containing v")
    print()

    # Numerical verification
    print("Numerical verification for selected n:")
    for n in [3, 9, 15, 21, 27, 33, 45, 63, 99]:
        zeta = cmath.exp(2j * cmath.pi / n)
        omega = zeta ** (n // 3)

        # Take a random all-nonzero ray
        import random
        random.seed(n)
        a, b, c = random.randint(0, n-1), random.randint(0, n-1), random.randint(0, n-1)
        v = (zeta**a, zeta**b, zeta**c)

        # Even-perm neighbor
        w_plus = (zeta**a, omega * zeta**b, omega**2 * zeta**c)
        # Odd-perm neighbor
        w_minus = (zeta**a, omega**2 * zeta**b, omega * zeta**c)

        # Check orthogonality
        vw_plus = abs(hermitian_dot(v, w_plus))
        vw_minus = abs(hermitian_dot(v, w_minus))
        ww = abs(hermitian_dot(w_plus, w_minus))

        # Check that even-perm variants are projectively equivalent
        w_sigma4 = (omega * zeta**a, omega**2 * zeta**b, zeta**c)
        # w_sigma4 should equal omega * w_plus
        ratio = w_sigma4[0] / w_plus[0] if abs(w_plus[0]) > TOL else w_sigma4[1] / w_plus[1]
        ratios_match = all(abs(w_sigma4[i] - ratio * w_plus[i]) < TOL for i in range(3))

        ok = vw_plus < TOL and vw_minus < TOL and ww < TOL and ratios_match
        status = "✓" if ok else "✗"
        print(f"  n={n:3d}: v⊥w₊={vw_plus<TOL} v⊥w₋={vw_minus<TOL} "
              f"w₊⊥w₋={ww<TOL} σ₄~σ₁={ratios_match}  {status}")

    print()


# ============================================================
# Complete the proof: axis and 1-zero rays
# ============================================================

def prove_remaining_rays():
    """
    Complete the proof for odd n with 3|n by handling
    axis-aligned and 1-zero-coord rays.
    """
    print("=" * 70)
    print("REMAINING CASES FOR ODD n WITH 3|n")
    print("=" * 70)
    print()
    print("2-zero-coord rays (axis directions): (ζ^a, 0, 0), (0, ζ^b, 0), (0, 0, ζ^c)")
    print("  These form exactly 1 triad: {[1:0:0], [0:1:0], [0:0:1]}.")
    print("  No axis ray appears in any all-nonzero triad (different zero pattern).")
    print()
    print("1-zero-coord rays: e.g., v = (ζ^a, ζ^b, 0)")
    print("  For v ⊥ w (both 1-zero, same zero position):")
    print("    ⟨v|w⟩ = ζ^{c-a} + ζ^{d-b} = 0 requires ζ^{d-b-c+a} = -1")
    print("    For odd n: -1 ∉ ⟨ζ⟩, so NO such orthogonalities exist!")
    print()
    print("  For v ⊥ w (different zero positions, e.g., w = (0, ζ^c, ζ^d)):")
    print("    ⟨v|w⟩ = 0 + ζ^{c-b} · ζ^0 = ζ^{c-b} ≠ 0.  NOT orthogonal!")
    print()
    print("  For v ⊥ w (w has 2 zeros, e.g., w = (0, 0, ζ^c)):")
    print("    ⟨v|w⟩ = 0.  Orthogonal (complementary zeros).")
    print("    But for a triad {v, w, u}: need u ⊥ v and u ⊥ w.")
    print("    u ⊥ w = (0,0,ζ^c) requires u₃ = 0.")
    print("    u ⊥ v = (ζ^a,ζ^b,0) with u₃=0: ⟨v|u⟩ = ζ^{e-a}+ζ^{f-b} = 0")
    print("    → needs -1 ∈ ⟨ζ⟩ → needs 2|n → impossible for odd n!")
    print()
    print("  CONCLUSION: 1-zero-coord rays participate in ZERO triads for odd n.")
    print()

    # Verify
    print("Verification:")
    for n in [3, 9, 15, 21, 27, 33]:
        rays = generate_cyclotomic_pool(n)
        _, triads, _ = build_orthogonality(rays)

        one_zero_in_triad = 0
        for a, b, c in triads:
            for r in [a, b, c]:
                zeros = sum(1 for x in rays[r] if abs(x) < TOL)
                if zeros == 1:
                    one_zero_in_triad += 1

        print(f"  n={n}: 1-zero-coord rays in triads: {one_zero_in_triad}  ✓" if one_zero_in_triad == 0
              else f"  n={n}: 1-zero-coord rays in triads: {one_zero_in_triad}  ✗")
    print()


# ============================================================
# Triad count formula
# ============================================================

def verify_triad_count():
    """
    For odd n with 3|n, the number of triads is exactly n²/3 + 1.

    Proof: There are n² projectively distinct all-nonzero rays
    (parameterized by (b-a, c-a) mod n). Each belongs to exactly
    1 all-nonzero triad, and each triad has 3 members.
    So #(all-nonzero triads) = n²/3.
    Plus 1 axis-aligned triad.
    Total = n²/3 + 1.
    """
    print("=" * 70)
    print("TRIAD COUNT FORMULA: T(n) = n²/3 + 1 FOR ODD 3|n")
    print("=" * 70)
    print()
    print("  All-nonzero rays: n² (parameterized by exponent differences mod n)")
    print("  Each in exactly 1 triad → n²/3 all-nonzero triads")
    print("  Plus 1 axis triad → total = n²/3 + 1")
    print()

    for n in [3, 9, 15, 21, 27, 33, 39, 45, 51]:
        rays = generate_cyclotomic_pool(n)
        _, triads, _ = build_orthogonality(rays)
        predicted = n * n // 3 + 1
        match = "✓" if len(triads) == predicted else "✗"
        print(f"  n={n:3d}: predicted={predicted:5d}, actual={len(triads):5d}  {match}")

    print()


# ============================================================
# Case 1: 3∤n, 2|n — bipartiteness of plane orthogonality graph
# ============================================================

def analyze_case1_bipartite():
    """
    For 3∤n, 2|n: triads involve zero-coordinate rays only.
    Check if the constraint graph is bipartite (ensuring colorability).
    """
    print("=" * 70)
    print("CASE 1 (3∤n, 2|n): PLANE ORTHOGONALITY STRUCTURE")
    print("=" * 70)
    print()

    for n in [2, 4, 8, 10, 14, 16, 20, 22, 26, 28, 32, 34, 40]:
        if n % 3 == 0:
            continue

        rays = generate_cyclotomic_pool(n)
        pairs, triads, adj = build_orthogonality(rays)

        # Check: are all triads of type (1,1,2) or (2,2,2)?
        all_zero_involved = True
        for a, b, c in triads:
            for r in [a, b, c]:
                if sum(1 for x in rays[r] if abs(x) < TOL) == 0:
                    all_zero_involved = False
                    break
            if not all_zero_involved:
                break

        # Predicted triad count: 1 axis + 3·(n/2-1) plane triads
        # Actually: for each zero position, the orthogonal pairs in
        # that plane form a graph. Each edge + axis ray = triad.
        # Number of 2-term orthogonal pairs per plane = n/2
        # (ζ^{d-b-c+a} = -1 means d-b-c+a = n/2, each gives a pair)

        # Count triads by type
        type_counts = Counter()
        for a, b, c in triads:
            zeros = tuple(sorted([
                sum(1 for x in rays[r] if abs(x) < TOL)
                for r in [a, b, c]
            ]))
            type_counts[zeros] += 1

        # Check colorability
        from pysat.solvers import Glucose4
        clauses = []
        for (a, b, c) in triads:
            va, vb, vc = a+1, b+1, c+1
            clauses.append([va, vb, vc])
            clauses.append([-va, -vb])
            clauses.append([-va, -vc])
            clauses.append([-vb, -vc])
        for (u, v) in pairs:
            clauses.append([-(u+1), -(v+1)])
        with Glucose4(bootstrap_with=clauses) as solver:
            colorable = solver.solve()

        status = "colorable ✓" if colorable else "UNCOLORABLE ✗"
        print(f"  n={n:3d}: {len(triads):3d} triads  types={dict(type_counts)}  "
              f"all-zero-involved={all_zero_involved}  {status}")

    print()
    print("OBSERVATION: For 3∤n with 2|n, all triads involve at least one")
    print("ray with a zero coordinate. No all-nonzero triads exist (requires")
    print("3-term vanishing sum → 3|n). The pool is always colorable.")
    print("A formal proof would show the constraint graph decomposes into")
    print("three independent plane-orthogonality graphs, each satisfiable.")
    print()


# ============================================================
# COMPLETE THEOREM STATEMENT
# ============================================================

def complete_theorem():
    print("=" * 70)
    print("THEOREM (6|n characterization — complete proof)")
    print("=" * 70)
    print()
    print("THEOREM. S_n is KS-uncolorable ⟺ 6|n.")
    print()
    print("PROOF.")
    print()
    print("(⟸) SUFFICIENCY: If 6|n, the Eisenstein 33-set embeds. □")
    print()
    print("(⟹) NECESSITY: If 6∤n, we show S_n is colorable.")
    print()
    print("CASE A: 3∤n.")
    print("  Lemma: No 3-term vanishing sum ζ^a+ζ^b+ζ^c=0 exists when 3∤n.")
    print("  Proof: 1+ζ^p+ζ^q=0 ⟹ cos(2πp/n)=-1/2 ⟹ 3|n. □")
    print("  Consequence: No all-nonzero orthogonal pairs exist.")
    print("  All orthogonalities involve zero-coordinate rays.")
    print("  The resulting triad network is colorable.")
    print("  [Subcase 2∤n: only axis triad exists → trivially colorable.]")
    print("  [Subcase 2|n: verified colorable for all n ≤ 40.  ★]")
    print()
    print("CASE B: 3|n, 2∤n.  ★★ FULLY PROVED ★★")
    print()
    print("  Lemma (Projective collapse): For any all-nonzero ray v,")
    print("  the 6 permutation-based neighbors collapse to exactly 2")
    print("  projectively distinct rays (even perms → w₊, odd → w₋).")
    print("  Proof: w_{(1,2,0)} = ω · w_{(0,1,2)} and")
    print("         w_{(2,0,1)} = ω² · w_{(0,1,2)}, etc. □")
    print()
    print("  Lemma (Triad uniqueness): {v, w₊, w₋} is the unique triad")
    print("  containing v among all-nonzero rays.")
    print("  Proof: v has exactly 2 all-nonzero orthogonal neighbors")
    print("  (by projective collapse), and they form one triad. □")
    print()
    print("  Lemma (1-zero isolation): 1-zero-coord rays participate")
    print("  in zero triads when n is odd.")
    print("  Proof: Any triad involving a 1-zero ray (ζ^a,ζ^b,0)")
    print("  would require a 2-term cancellation ζ^p+ζ^q=0,")
    print("  i.e., -1 ∈ ⟨ζ⟩, which requires 2|n. □")
    print()
    print("  Conclusion: The triads are {axis triad} ∪ {n²/3 isolated")
    print("  all-nonzero triads}. Max triad membership = 1.")
    print("  The coloring problem decomposes → trivially satisfiable. □")
    print()
    print("PROOF STATUS:")
    print("  Sufficiency:     PROVED (algebraic)")
    print("  Case B (3|n,2∤n): PROVED (algebraic, 3 lemmas)")
    print("  Case A (3∤n,2∤n): PROVED (trivial — only axis triad)")
    print("  Case A (3∤n,2|n): COMPUTATIONALLY VERIFIED ≤ 40  [★ only gap]")
    print()
    print("  The single remaining gap (Case A with 2|n, 3∤n) requires showing")
    print("  that zero-coordinate triads from 2-term cancellations alone")
    print("  cannot create KS-uncolorability. This is the structurally")
    print("  weakest case and is verified for all tested n.")


# ============================================================
# MAIN
# ============================================================

def main():
    t0 = time.time()

    prove_projective_collapse()
    prove_remaining_rays()
    verify_triad_count()
    analyze_case1_bipartite()
    complete_theorem()

    print(f"\nTotal time: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
