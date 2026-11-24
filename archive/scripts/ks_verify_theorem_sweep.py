"""
SAT sweep to verify the biconditional form of the proposed reformulated theorem.

Proposed theorem (option B):
  Let x in O_K with x not in {0, +/-1}, K = Q(sqrt(d)) quadratic.
  The raw ray set {0, +/-1, +/-x}^3 (projective in C^3) is KS-uncolorable iff
    (i)  |x|^2 = 2, or
    (ii') N(x) = 1 and |T(x)| = 1  (i.e., 1 +/- (x + xbar) = 0).

Sweep: enumerate generators x of O_K for small d, signed both ways, and small
Z-combinations. For each, check:
  - Does (i) or (ii') hold?
  - Is the raw ray set SAT-uncolorable?
  - Are these two answers equal?

Flag any discrepancy.
"""

import cmath
import sys
from ks_sat import is_uncolorable as sat_uncolorable
from ks_new_islands import generate_rays_from_alphabet
from ks_new_island_analysis import build_pairs_triads


def test_raw_uncol(alphabet):
    """Return True iff the raw ray set from the alphabet is KS-uncolorable."""
    rays = generate_rays_from_alphabet(alphabet)
    if len(rays) < 3:
        return False, 0, 0
    pairs, triads = build_pairs_triads(rays)
    if not triads:
        return False, len(rays), 0
    return sat_uncolorable(len(rays), pairs, triads), len(rays), len(triads)


def conditions(x, d):
    """Return (cond_i_v1_loose, cond_i_refined, cond_ii_new, cond_ii_old, cond_rational, |x|^2, N_gal, T_gal).

    Uses the GALOIS trace/norm, not complex-conjugate.
    For x = a + b*sqrt(d) in Q(sqrt(d)): sigma(x) = a - b*sqrt(d).
    Galois trace T(x) = 2a,  Galois norm N(x) = a^2 - b^2 * d.

    For imaginary quadratic (d<0), sigma = complex conjugate, so |x|^2 = N_gal.
    For real quadratic (d>0), they differ: |x|^2 = (a+b sqrt d)^2, N_gal = a^2 - b*d^2.
    """
    modsq = abs(x) ** 2

    # Extract (a, b) from x = a + b*sqrt(d) for d != 0
    if d == 0:
        # Rational case
        a_part = x.real
        b_part = 0.0
    elif d < 0:
        # x = a + b*i*sqrt(|d|): a = Re(x), b*sqrt(|d|) = Im(x), so b = Im(x)/sqrt(|d|)
        import math as _math
        a_part = x.real
        b_part = x.imag / _math.sqrt(-d)
    else:
        # x = a + b*sqrt(d), both real: a = Re(x) - b*sqrt(d), but x is real
        # We need to recover b. We have x = a + b*sqrt(d) with a,b possibly half-integer.
        # Use knowledge from construction: caller supplied x; we extract via pairing.
        # Since the caller knows (a,b), we require x's provenance. Use a numeric trick:
        # sigma(x) = 2a - x (since a+b sqrt(d) + a - b sqrt(d) = 2a, so a = (x+sigma)/2).
        # But we don't have sigma yet. Fallback: trust that x came from "a + b*sqrt(d)" form,
        # and we reconstruct by the identity x + sigma(x) = 2a = 2*(<integer or half-int>).
        # We'll compute sigma(x) below via field-specific logic in the caller. For now,
        # leave this function purely algebraic using only (x, d).
        import math as _math
        # x_val = a + b * sqrt(d). We cannot uniquely split without more info.
        # Use: T_gal = x + sigma(x), and for x real, sigma(x) = 2a - x, so we'd need a.
        # Instead, compute numerically: try small-denominator (a, b) fits.
        sd = _math.sqrt(d)
        # Search for a,b with x = a + b*sd, allowing a,b in halves up to 5
        a_part = None
        for two_a in range(-20, 21):
            for two_b in range(-20, 21):
                aa = two_a / 2.0
                bb = two_b / 2.0
                if abs(aa + bb * sd - x.real) < 1e-9 and abs(x.imag) < 1e-9:
                    a_part = aa
                    b_part = bb
                    break
            if a_part is not None:
                break
        if a_part is None:
            a_part = x.real
            b_part = 0.0

    N_gal = a_part * a_part - b_part * b_part * d   # a^2 - b^2 * d
    T_gal = 2 * a_part

    def close(a, b, tol=1e-9):
        return abs(a - b) < tol

    cond_i_v1_loose = close(modsq, 2)
    cond_i_refined = close(T_gal, 0) and close(modsq, 2)
    cond_ii_new = close(N_gal, 1) and close(abs(T_gal), 1)
    cond_ii_old = close(N_gal, 1) and close(T_gal, -1)
    cond_rational = (close(x.real, 2) or close(x.real, -2)) and close(abs(x.imag), 0)
    return cond_i_v1_loose, cond_i_refined, cond_ii_new, cond_ii_old, cond_rational, modsq, N_gal, T_gal


def run():
    """Run the sweep."""
    cases = []

    # Imaginary quadratic: d = -m (m > 0 squarefree)
    # Enumerate x = a + b*sqrt(d) and a + b*(1+sqrt(d))/2 with small a, b
    # Filter by |x|^2 <= 3 (covers (i) |x|^2 = 2 and (ii) |x|^2 = 1)
    for m in [1, 2, 3, 5, 6, 7, 10, 11, 13, 14, 15, 17, 19, 21, 22, 23]:
        d = -m
        sd = cmath.sqrt(d)
        # Enumerate candidate x not in {0, +/-1} with small |x|^2
        # Over Z[sqrt(d)]: x = a + b*sqrt(d), a,b in Z, (a,b) != (0,0), b != 0 (else x=a in Z)
        # We include b=0 with a=+/-2 as the degenerate rational case x=2
        # Over Z[(1+sqrt(d))/2] (d = -3, -7, -11, -15, -19, -23 mod 4 = 1):
        #   x = a + b*(1+sqrt(d))/2

        ring_type = "halfint" if (d % 4) == 1 else "standard"

        candidates = []
        # Z-basis generators (standard): a*1 + b*sqrt(d) with (a,b) having |x|^2 <= 3
        for a in range(-3, 4):
            for b in range(-3, 4):
                if b == 0 and abs(a) <= 1:
                    continue  # 0, +/-1 excluded (but we keep a=+/-2 as the rational case)
                x = a + b * sd
                if abs(x) ** 2 > 3 + 0.01:
                    continue
                label = f"{a}+{b}sqrt({d})" if b >= 0 else f"{a}{b}sqrt({d})"
                candidates.append((label, x, "std"))

        if ring_type == "halfint":
            half = (1 + sd) / 2
            for a in range(-3, 4):
                for b in range(-3, 4):
                    if b == 0:
                        continue  # would just be a in Z
                    x = a + b * half
                    if abs(x) ** 2 > 3 + 0.01:
                        continue
                    label = f"{a}+{b}*(1+sqrt({d}))/2" if b >= 0 else f"{a}{b}*(1+sqrt({d}))/2"
                    candidates.append((label, x, "half"))

        for label, x, kind in candidates:
            cases.append((d, label, x, kind))

    # Real quadratic: d > 1 squarefree
    for m in [2, 3, 5, 6, 7, 10, 11, 13]:
        d = m
        sd = cmath.sqrt(d)
        ring_type = "halfint" if (d % 4) == 1 else "standard"

        for a in range(-3, 4):
            for b in range(-3, 4):
                if b == 0 and abs(a) <= 1:
                    continue
                x = a + b * sd
                if abs(x) ** 2 > 3 + 0.01:
                    continue
                label = f"{a}+{b}sqrt({d})" if b >= 0 else f"{a}{b}sqrt({d})"
                cases.append((d, label, x, "std"))

        if ring_type == "halfint":
            half = (1 + sd) / 2
            for a in range(-3, 4):
                for b in range(-3, 4):
                    if b == 0:
                        continue
                    x = a + b * half
                    if abs(x) ** 2 > 3 + 0.01:
                        continue
                    label = f"{a}+{b}*(1+sqrt({d}))/2" if b >= 0 else f"{a}{b}*(1+sqrt({d}))/2"
                    cases.append((d, label, x, "half"))

    # Degenerate rational case x = 2
    cases.append((0, "2", complex(2, 0), "rational"))
    cases.append((0, "-2", complex(-2, 0), "rational"))

    print(f"Total test cases: {len(cases)}")
    print(f"{'d':>4} {'x label':<28} {'|x|^2':>7} {'N':>7} {'T':>7} "
          f"{'(i)':>4} {'(ii_new)':>9} {'(ii_old)':>9} "
          f"{'rays':>5} {'triads':>7} {'raw_KS':>7} {'pred_new':>9} {'match':>6}")
    print("-" * 140)

    discrepancies_new = []
    discrepancies_old = []
    stats = {"uncol": 0, "colorable": 0, "skipped_nosym": 0}

    discrepancies_refined = []

    print(f"{'d':>4} {'x':<28} {'|x|^2':>7} {'T':>7} {'triads':>7} "
          f"{'raw_KS':>7} {'pure':>5} {'phase':>6} {'rat':>4} {'pred':>5} {'match':>6}")
    print("-" * 110)

    for d, label, x, kind in cases:
        ci_loose, ci_ref, cii_new, cii_old, crat, modsq, N, T = conditions(x, d)
        alphabet = [0, 1, -1, x, -x]
        try:
            raw_ks, n_rays, n_triads = test_raw_uncol(alphabet)
        except Exception as e:
            print(f"  ERROR on {label}: {e}")
            continue

        pred_refined = ci_ref or cii_new or crat  # proposed final theorem
        pred_new = ci_loose or cii_new            # review's proposal
        pred_old = ci_loose or cii_old            # original paper
        match_refined = "OK" if pred_refined == raw_ks else "FAIL"

        if raw_ks:
            stats["uncol"] += 1
        else:
            stats["colorable"] += 1

        print(f"{d:>4} {label:<28} {modsq:>7.3f} {T:>7.3f} "
              f"{n_triads:>7} {str(raw_ks):>7} {str(ci_ref):>5} {str(cii_new):>6} "
              f"{str(crat):>4} {str(pred_refined):>5} {match_refined:>6}")

        if pred_refined != raw_ks:
            discrepancies_refined.append((d, label, x, ci_ref, cii_new, crat, raw_ks, modsq, N, T))
        if pred_new != raw_ks:
            discrepancies_new.append((d, label, x, ci_loose, cii_new, raw_ks, modsq, N, T))
        if pred_old != raw_ks:
            discrepancies_old.append((d, label, x, ci_loose, cii_old, raw_ks, modsq, N, T))

    print("\n" + "=" * 70)
    print(f"SUMMARY ({stats})")
    print("=" * 70)
    print(f"Discrepancies against OLD  theorem ((|x|^2=2) or (N=1,T=-1)):            {len(discrepancies_old)}")
    print(f"Discrepancies against NEW  theorem ((|x|^2=2) or (N=1,|T|=1)):           {len(discrepancies_new)}")
    print(f"Discrepancies against REFINED theorem ((T=0 & |x|^2=2) or phase or +/-2): {len(discrepancies_refined)}")

    if discrepancies_refined:
        print("\nREFINED theorem failures:")
        for d, label, x, ci, ci2, crat, raw_ks, modsq, N, T in discrepancies_refined:
            print(f"  d={d}, x={label}, |x|^2={modsq:.3f}, N={N:.3f}, T={T:.3f}, "
                  f"pure={ci}, phase={ci2}, rational={crat}, raw_KS={raw_ks}")
    else:
        print("\nREFINED theorem: ZERO DISCREPANCIES across sweep.")


if __name__ == "__main__":
    run()
