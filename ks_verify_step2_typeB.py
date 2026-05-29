"""
Verify Step 2 of the Galois letter's necessity proof:

  For every raw-colorable alphabet {0, +/-1, +/-x} (no condition R, i, ii),
  there is no "type-B" triad -- i.e., no triad contains both an all-nonzero
  ray and a one-zero ray.

Equivalently: if v is all-nonzero, w is one-zero, and <v,w> = 0 (Hermitian),
then the unique third ray u completing the triad (namely u = conj(v x w) up
to scaling) is NOT projectively equivalent to any ray in the pool.

If this holds universally, Step 2's structural argument carries through after
the cross-product formula fix. If violated, the necessity proof needs deeper
rework.
"""

import cmath
import math
from itertools import product


def generate_rays(alphabet):
    """Generate all projective rays from alphabet^3, canonicalized."""
    rays = []
    seen = set()
    for v in product(alphabet, repeat=3):
        if all(abs(c) < 1e-12 for c in v):
            continue
        # Canonicalize: divide by first nonzero entry so that it becomes 1
        for c in v:
            if abs(c) > 1e-12:
                pivot = c
                break
        canonical = tuple(c / pivot for c in v)
        # Round to avoid float key issues
        key = tuple((round(c.real, 9), round(c.imag, 9)) for c in canonical)
        if key not in seen:
            seen.add(key)
            rays.append(canonical)
    return rays


def hdot(a, b):
    """Hermitian inner product <a,b> = sum conj(a_k) * b_k."""
    return sum(ak.conjugate() * bk for ak, bk in zip(a, b))


def conj_cross(v, w):
    """Correct Hermitian orthogonal complement: u = conj(v x w)."""
    cross = (
        v[1] * w[2] - v[2] * w[1],
        v[2] * w[0] - v[0] * w[2],
        v[0] * w[1] - v[1] * w[0],
    )
    return tuple(c.conjugate() for c in cross)


def same_ray(u, r, tol=1e-7):
    """Are u and r projectively equivalent (u = lambda * r for some nonzero lambda)?"""
    if all(abs(c) < tol for c in u):
        return False
    if all(abs(c) < tol for c in r):
        return False
    # Find lambda from first matching nonzero entry
    for i in range(3):
        if abs(r[i]) > tol and abs(u[i]) > tol:
            lam = u[i] / r[i]
            return all(abs(u[j] - lam * r[j]) < tol for j in range(3))
    # Handle pattern matches where both have same zero structure
    pattern_u = tuple(abs(c) < tol for c in u)
    pattern_r = tuple(abs(c) < tol for c in r)
    if pattern_u != pattern_r:
        return False
    # Both zero in same places; check ratio on nonzero components
    for i in range(3):
        if not pattern_u[i]:
            lam = u[i] / r[i]
            return all(
                pattern_u[j] or abs(u[j] - lam * r[j]) < tol for j in range(3)
            )
    return False


def count_type_b_triads(rays):
    """Count type-B triads: triads with at least one all-nonzero and at least one one-zero ray."""
    tol = 1e-9

    def nonzero_count(r):
        return sum(1 for c in r if abs(c) > tol)

    # Precompute orthogonality
    n = len(rays)
    is_orth = [[False] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if abs(hdot(rays[i], rays[j])) < tol:
                is_orth[i][j] = is_orth[j][i] = True

    type_b_count = 0
    type_b_examples = []
    for i in range(n):
        nc_i = nonzero_count(rays[i])
        for j in range(i + 1, n):
            if not is_orth[i][j]:
                continue
            for k in range(j + 1, n):
                if is_orth[i][k] and is_orth[j][k]:
                    ncs = sorted([nonzero_count(rays[idx]) for idx in (i, j, k)])
                    # Type B: at least one all-nonzero (3) AND at least one one-zero (2)
                    has_allnz = any(nc == 3 for nc in ncs)
                    has_onezero = any(nc == 2 for nc in ncs)
                    if has_allnz and has_onezero:
                        type_b_count += 1
                        if len(type_b_examples) < 3:
                            type_b_examples.append((rays[i], rays[j], rays[k]))
    return type_b_count, type_b_examples


def verify_case(d, label, x, expected_raw_ks):
    """For a single case, check Step 2's structural claim."""
    alphabet = [0, 1, -1, x, -x]
    rays = generate_rays(alphabet)
    n_rays = len(rays)

    tb_count, tb_examples = count_type_b_triads(rays)

    result = {
        "d": d,
        "label": label,
        "n_rays": n_rays,
        "type_b_count": tb_count,
        "expected_raw_ks": expected_raw_ks,
        "examples": tb_examples,
    }
    return result


def run():
    # Mirror the cases from ks_verify_theorem_sweep.py, but restrict to
    # alphabets that should NOT satisfy (R), (i), or (ii) -- the colorable cases.
    # We reuse a smaller representative set to keep runtime reasonable.

    cases = []
    # Colorable cases (neither R, i, nor ii) -- should have NO type-B triads
    # d=-3, x = 2 + sqrt(-3) type (|x|^2 = 7, out of range), skip
    # d=-1, x = i (|x|^2 = 1, T_gal=0, N=1; |T|=0, not 1 -- colorable)
    # d=-1, x = 1+i (|x|^2 = 2, T_gal=2, not 0 -- colorable)
    # d=-7, x = (1+sqrt(-7))/2 (|x|^2 = 2, T_gal=1, not 0 -- colorable)
    # d=-11, x = (1+sqrt(-11))/2 (|x|^2 = 3, T_gal=1 -- colorable)
    # d=2, x = 1+sqrt(2) (|x|^2 = (1+sqrt(2))^2 != 2, T_gal=2, colorable)
    # d=3, x = sqrt(3) (|x|^2 = 3, T_gal=0 -- colorable)
    # d=5, x = phi = (1+sqrt(5))/2 (|x|^2 != 2, colorable; golden ratio row 4)
    # d=-5, x = sqrt(-5) (|x|^2 = 5, colorable)

    colorable_cases = [
        (-1, "i", complex(0, 1)),
        (-1, "1+i", complex(1, 1)),
        (-7, "(1+sqrt(-7))/2", complex(0.5, math.sqrt(7) / 2)),
        (-11, "(1+sqrt(-11))/2", complex(0.5, math.sqrt(11) / 2)),
        (2, "1+sqrt(2)", complex(1 + math.sqrt(2), 0)),
        (3, "sqrt(3)", complex(math.sqrt(3), 0)),
        (5, "(1+sqrt(5))/2 (phi)", complex((1 + math.sqrt(5)) / 2, 0)),
        (-5, "sqrt(-5)", complex(0, math.sqrt(5))),
        (-2, "1+sqrt(-2)", complex(1, math.sqrt(2))),
        (-3, "2+sqrt(-3)", complex(2, math.sqrt(3))),
    ]

    # Uncolorable cases (should have type-B triads OR uncolorability from other structure)
    # Include for comparison
    uncolorable_cases = [
        (2, "sqrt(2) (Peres)", complex(math.sqrt(2), 0)),
        (-2, "sqrt(-2)", complex(0, math.sqrt(2))),
        (-3, "omega = (-1+sqrt(-3))/2", complex(-0.5, math.sqrt(3) / 2)),
        (-3, "(1+sqrt(-3))/2 (canonical)", complex(0.5, math.sqrt(3) / 2)),
        (0, "x=2 (rational CK)", complex(2, 0)),
    ]

    print("=" * 95)
    print("COLORABLE ALPHABETS  (neither R, i, nor ii -- Step 2 claims NO type-B triads)")
    print("=" * 95)
    print(f"{'d':>4} {'x':<35} {'rays':>5} {'type-B triads':>15} {'Step 2 OK?':>12}")
    print("-" * 95)
    any_fail = False
    for d, label, x in colorable_cases:
        res = verify_case(d, label, x, expected_raw_ks=False)
        ok = "YES" if res["type_b_count"] == 0 else "NO (FAIL)"
        if res["type_b_count"] > 0:
            any_fail = True
        print(f"{d:>4} {label:<35} {res['n_rays']:>5} {res['type_b_count']:>15} {ok:>12}")
        if res["examples"]:
            print(f"     Example type-B triad: {res['examples'][0]}")

    print()
    print("=" * 95)
    print("UNCOLORABLE ALPHABETS  (one of R, i, ii holds -- for comparison)")
    print("=" * 95)
    print(f"{'d':>4} {'x':<35} {'rays':>5} {'type-B triads':>15}")
    print("-" * 95)
    for d, label, x in uncolorable_cases:
        res = verify_case(d, label, x, expected_raw_ks=True)
        print(f"{d:>4} {label:<35} {res['n_rays']:>5} {res['type_b_count']:>15}")

    print()
    print("=" * 95)
    if any_fail:
        print("VERDICT: Step 2's structural claim FAILS on at least one colorable alphabet.")
        print("         The necessity proof needs deeper reworking than a formula fix.")
    else:
        print("VERDICT: Step 2's structural claim HOLDS on all tested colorable alphabets.")
        print("         The corrected-formula proof is structurally sound; only algebra rewrite needed.")


if __name__ == "__main__":
    run()
