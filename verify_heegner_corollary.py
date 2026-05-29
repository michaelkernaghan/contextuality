"""Verify the corrected Heegner corollary for galois_letter.tex.

Question: among imaginary quadratic fields K = Q(sqrt(-d)), for which
squarefree d>0 does there exist a ring-of-integers generator y such that
the RAW ray set {0, +/-1, +/-y}^3 in C^3 is KS-uncolorable, under the
REFORMULATED three-condition theorem?

  (i)  Tr(y) = 0 and |y|^2 = 2
  (ii) N(y) = 1 and |Tr(y)| = 1

For imaginary quadratic, the nontrivial Galois automorphism is complex
conjugation, so Tr(y) = y + ybar = 2 Re(y) and N(y) = |y|^2.

We (a) evaluate the conditions analytically and (b) build the raw ray
set and SAT-test it, then confirm the two agree.
"""
import cmath
import math
import sys

from ks_sat import is_uncolorable as sat_uncolorable
from ks_new_islands import generate_rays_from_alphabet
from ks_new_island_analysis import build_pairs_triads

sys.stdout.reconfigure(line_buffering=True)

TOL = 1e-9


def squarefree(n):
    if n < 1:
        return False
    k = 2
    while k * k <= n:
        if n % (k * k) == 0:
            return False
        k += 1
    return True


def canonical_generator(d):
    """x_0 generating O_K for K = Q(sqrt(-d)), d>0 squarefree."""
    s = cmath.sqrt(-d)  # = i*sqrt(d)
    if d % 4 == 3:
        return (1 + s) / 2          # x_0 = (1+sqrt(-d))/2,  Tr=1, |x_0|^2=(1+d)/4
    else:                            # d % 4 in {1,2}
        return s                     # x_0 = sqrt(-d),        Tr=0, |x_0|^2=d


def tr(z):      # Galois trace = z + conj(z) = 2 Re
    return 2 * z.real


def norm(z):    # Galois norm = z*conj(z) = |z|^2 (imaginary quadratic)
    return abs(z) ** 2


def cond_i(y):
    return abs(tr(y)) < TOL and abs(norm(y) - 2) < TOL


def cond_ii(y):
    return abs(norm(y) - 1) < TOL and abs(abs(tr(y)) - 1) < TOL


def raw_uncolorable(y):
    alphabet = [0 + 0j, 1 + 0j, -1 + 0j, y, -y]
    rays = generate_rays_from_alphabet(alphabet)
    if len(rays) < 3:
        return False
    pairs, triads = build_pairs_triads(rays)
    if not triads:
        return False
    return sat_uncolorable(len(rays), pairs, triads)


def main():
    print(f"{'d':>3} {'gen y (a,eps)':>16} {'Tr':>5} {'|y|^2':>6} "
          f"{'(i)':>4} {'(ii)':>4} {'SAT-uncol':>10} {'match':>6}")
    print("-" * 70)
    raw_uncol_ds = set()
    any_mismatch = False
    A_RANGE = range(-3, 4)
    for d in range(1, 44):
        if not squarefree(d):
            continue
        x0 = canonical_generator(d)
        for eps in (+1, -1):
            for a in A_RANGE:
                y = a + eps * x0
                if abs(y) < TOL or abs(y - 1) < TOL or abs(y + 1) < TOL:
                    continue  # y must not be 0, +/-1
                ci, cii = cond_i(y), cond_ii(y)
                theorem_says = ci or cii
                sat = raw_uncolorable(y)
                if theorem_says != sat:
                    any_mismatch = True
                if theorem_says or sat:
                    print(f"{d:>3} {f'({a},{eps:+d})':>16} {tr(y):>5.1f} "
                          f"{norm(y):>6.2f} {str(ci):>4} {str(cii):>4} "
                          f"{str(sat):>10} {'OK' if theorem_says==sat else 'MISMATCH!':>6}")
                if sat:
                    raw_uncol_ds.add(d)
    print("-" * 70)
    print(f"Imaginary quadratic d with a RAW-uncolorable generator: "
          f"{sorted(raw_uncol_ds)}")
    print(f"Theorem<->SAT agreement across all tested generators: "
          f"{'PERFECT' if not any_mismatch else 'MISMATCH FOUND'}")


if __name__ == "__main__":
    main()
