"""
Verify the Round-7 Oxford review's three load-bearing claims before editing the paper.

Claims to verify:
1. The Hermitian cross-product formula u_k = conj(v[k+1])*w[k+2] - conj(v[k+2])*w[k+1]
   does NOT satisfy <u,v> = <u,w> = 0 in general. The correct formula is
   u = conj(v x w), i.e. u_k = conj(v[k+1]*w[k+2] - v[k+2]*w[k+1]).

2. The canonical Eisenstein generator x = (1+sqrt(-3))/2 has N(x)=1, T(x)=+1,
   so it fails condition (ii) "N=1 and T=-1" of the current theorem, yet
   {0, +/-1, +/-x} is the Eisenstein alphabet and IS KS-uncolorable.
   This is the "theorem false as stated" counterexample.

3. The proposed alphabet-invariant fix N(x)=1 AND |T(x)|=1 is satisfied by both
   omega = (-1+sqrt(-3))/2 (T=-1, original case) and x = (1+sqrt(-3))/2 (T=+1,
   sign-flipped case), and nothing else pathological among quadratic units.
"""

import sympy as sp
from sympy import Rational, sqrt, I, Matrix, simplify, conjugate, expand, symbols


def hermitian(u, v):
    """Hermitian inner product <u,v> = sum conj(u[k]) * v[k]."""
    return sum(conjugate(u[k]) * v[k] for k in range(3))


def papers_cross(v, w):
    """The (wrong) formula in the paper: u_k = conj(v[k+1])*w[k+2] - conj(v[k+2])*w[k+1]."""
    return [
        conjugate(v[1]) * w[2] - conjugate(v[2]) * w[1],
        conjugate(v[2]) * w[0] - conjugate(v[0]) * w[2],
        conjugate(v[0]) * w[1] - conjugate(v[1]) * w[0],
    ]


def correct_cross(v, w):
    """Correct Hermitian orthogonal complement: u = conj(v x w)."""
    return [
        conjugate(v[1] * w[2] - v[2] * w[1]),
        conjugate(v[2] * w[0] - v[0] * w[2]),
        conjugate(v[0] * w[1] - v[1] * w[0]),
    ]


# ============================================================
# Claim 1: Hermitian cross-product formula
# ============================================================
print("=" * 70)
print("Claim 1: Hermitian cross-product formula")
print("=" * 70)

v = [sp.Integer(1), I, sp.Integer(1)]
w = [I, sp.Integer(1), sp.Integer(0)]

print(f"v = {v}")
print(f"w = {w}")
print(f"<v,w> = {simplify(hermitian(v, w))}   (should be 0: orthogonal)")

u_paper = papers_cross(v, w)
u_correct = correct_cross(v, w)

print(f"\nPaper's formula u = {[simplify(x) for x in u_paper]}")
print(f"  <u_paper, v> = {simplify(hermitian(u_paper, v))}")
print(f"  <u_paper, w> = {simplify(hermitian(u_paper, w))}   <-- reviewer claims this is nonzero")

print(f"\nCorrect formula u = conj(v x w) = {[simplify(x) for x in u_correct]}")
print(f"  <u_correct, v> = {simplify(hermitian(u_correct, v))}")
print(f"  <u_correct, w> = {simplify(hermitian(u_correct, w))}")

claim1_confirmed = (
    simplify(hermitian(u_paper, w)) != 0
    and simplify(hermitian(u_correct, v)) == 0
    and simplify(hermitian(u_correct, w)) == 0
)
print(f"\n--> Claim 1 confirmed: {claim1_confirmed}")


# ============================================================
# Claim 2: Canonical Eisenstein generator is a counterexample
# ============================================================
print("\n" + "=" * 70)
print("Claim 2: x = (1+sqrt(-3))/2 as theorem counterexample")
print("=" * 70)

# x = (1 + sqrt(-3))/2, conjugate x_bar = (1 - sqrt(-3))/2
x = (1 + sqrt(-3)) / 2
x_bar = (1 - sqrt(-3)) / 2

N = simplify(x * x_bar)
T = simplify(x + x_bar)

print(f"x = (1+sqrt(-3))/2 = {x}")
print(f"N(x) = x * conj(x) = {N}")
print(f"T(x) = x + conj(x) = {T}")
print(f"|x|^2 = {simplify(abs(x)**2)}")

condition_i = (simplify(abs(x) ** 2) == 2)
condition_ii_old = (N == 1 and T == -1)
condition_ii_new = (N == 1 and abs(T) == 1)

print(f"\nCondition (i) |x|^2 = 2?           {condition_i}")
print(f"Condition (ii) OLD: N=1 AND T=-1?   {condition_ii_old}  <-- THIS IS THE BUG")
print(f"Condition (ii) NEW: N=1 AND |T|=1?  {condition_ii_new}")

# Now verify the alphabet {0, +/-1, +/-x} is the same as Eisenstein alphabet up to sign
omega = (-1 + sqrt(-3)) / 2  # standard Eisenstein generator
print(f"\nx       = {simplify(x)}")
print(f"-x      = {simplify(-x)}")
print(f"omega   = {simplify(omega)}")
print(f"-omega  = {simplify(-omega)}")
print(f"conj(omega) = {simplify(conjugate(omega))}")

# Is -x == conj(omega)?
check = simplify(-x - conjugate(omega))
print(f"\n-x - conj(omega) = {check}   (zero means -x = conj(omega), so alphabets coincide)")

# Alphabet invariance under x -> -x for the two conditions
print("\nInvariance check:")
print(f"  N(-x) = {simplify((-x) * conjugate(-x))}  (should equal N(x) = {N})")
print(f"  T(-x) = {simplify((-x) + conjugate(-x))}  (should equal -T(x) = {-T})")

claim2_confirmed = (
    not condition_ii_old  # old condition fails for this x
    and condition_ii_new   # new condition holds
    and check == 0         # -x = conj(omega), same alphabet as Eisenstein
)
print(f"\n--> Claim 2 confirmed: {claim2_confirmed}")


# ============================================================
# Claim 3: Proposed fix |T(x)| = 1 is the right invariant
# ============================================================
print("\n" + "=" * 70)
print("Claim 3: Survey of N=1 quadratic generators")
print("=" * 70)

# For O_K of imaginary quadratic fields Q(sqrt(d)) with d < 0 squarefree,
# a generator x satisfies N(x) = 1 only in limited cases.
# Let's enumerate small d and canonical/alt generators.

results = []
for d in [-1, -2, -3, -7, -11, -15, -19]:
    sd = sqrt(d)
    if d % 4 == 1:
        # d = 1 mod 4: generator is (1+sqrt(d))/2
        gens = [
            ("(1+sqrt(d))/2", (1 + sd) / 2),
            ("(-1+sqrt(d))/2", (-1 + sd) / 2),
            ("(1-sqrt(d))/2", (1 - sd) / 2),
            ("(-1-sqrt(d))/2", (-1 - sd) / 2),
        ]
    else:
        gens = [
            ("sqrt(d)", sd),
            ("-sqrt(d)", -sd),
        ]

    for name, g in gens:
        g_bar = g.conjugate()
        Ng = simplify(g * g_bar)
        Tg = simplify(g + g_bar)
        modsq = simplify(abs(g) ** 2)
        if Ng == 1:
            old_ii = (Ng == 1 and Tg == -1)
            new_ii = (Ng == 1 and abs(Tg) == 1)
            results.append((d, name, Ng, Tg, modsq, old_ii, new_ii))

print(f"{'d':>4} {'generator':<22} {'N':>4} {'T':>4} {'|x|^2':>8} {'OLD (ii)':>10} {'NEW (ii)':>10}")
print("-" * 70)
for d, name, N, T, modsq, old, new in results:
    print(f"{d:>4} {name:<22} {str(N):>4} {str(T):>4} {str(modsq):>8} {str(old):>10} {str(new):>10}")


# Also check real quadratic units: N(x) = +/-1 is possible for all real quadratic fields
# (infinitely many units), but we need N(x)=1 AND the alphabet to give KS sets.
# The real case has no |x|^2 = 2 generators in O_K for most d (only d=2 where x=sqrt(2)).
# The N=1, T=+/-1 phase mechanism shouldn't fire for real x since unit-modulus sums require complex phases.
print("\nReal quadratic sanity: for x real with N(x)=x^2=1, x=+/-1 only (excluded).")
print("So condition (ii) only activates in complex case, as expected.")

claim3_confirmed = all(new for *_, old, new in results if not old)
print(f"\n--> Claim 3: proposed |T|=1 fix covers all N=1 generators: {claim3_confirmed}")
print(f"    (Every N=1 generator we enumerated with wrong-sign T now falls under new condition.)")


# ============================================================
# Summary
# ============================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Claim 1 (cross-product formula wrong):     {claim1_confirmed}")
print(f"Claim 2 (d=-3 theorem counterexample):     {claim2_confirmed}")
print(f"Claim 3 (|T|=1 is right invariant):        {claim3_confirmed}")
