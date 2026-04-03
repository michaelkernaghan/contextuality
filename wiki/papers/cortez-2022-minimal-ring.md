---
title: "Minimal Algebraic Contextuality via Partial Rings"
slug: cortez-2022-minimal-ring
authors: ["Raul Cortez", "David Schmid", "Robert W. Spekkens"]
year: 2022
journal: "Physical Review Letters"
doi: "10.1103/PhysRevLett.129.230401"
tags: [algebraic-contextuality, partial-rings, hidden-states, Z[1/N], matrix-algebras, coloring, 85-vector, 6D]
status: read
---

# Minimal Algebraic Contextuality via Partial Rings

## Summary

This paper develops an algebraic theory of KS contextuality using **partial rings** — algebraic structures capturing measurement contexts as partially defined commutative subalgebras of a matrix algebra. An **algebraic hidden state** on a partial ring is a ring homomorphism to a commutative ring (a generalized coloring). The central result: the symmetric part of the 3×3 matrix algebra over Z[1/N] has no algebraic hidden states if and only if 6 divides N. For d ≥ 6, the symmetric matrices over Z have no algebraic hidden states. The proofs use a new 85-vector uncolorable set in the 3-sphere S₃(462) and a computational result for S₆(3).

## Core Contributions

- **Algebraic hidden states**: A hidden state on a partial ring P is a ring homomorphism φ: P → R to a commutative ring R that restricts to an algebra homomorphism on each context (maximal commutative subalgebra). This generalizes KS colorings.
- **Main theorem (d=3)**: M₃(Z[1/N])_sym (symmetric 3×3 matrices with entries in Z[1/N]) has no algebraic hidden states if and only if 6 | N.
- **Main theorem (d≥6)**: M_d(Z)_sym has no algebraic hidden states for all d ≥ 6.
- **New 85-vector KS-type set**: An 85-vector set in the unit sphere of ℝ³ (embedded in S₃(462)) with no valid coloring, used in the d=3 proof.
- **Computational S₆(3) result**: The set S₆(3) of integer vectors in d=6 has no algebraic hidden states, verified computationally.

## Key Definitions

- **Partial ring**: A set P with partial addition and multiplication, compatible with a covering by commutative subrings (contexts).
- **Context**: A maximal commutative subalgebra of M_d(R), corresponding to a joint measurement.
- **Algebraic hidden state**: A map φ: P → R (commutative ring) that is a ring homomorphism on each context.
- **S_d(N)**: The set of symmetric d×d matrices with integer entries in [−N, N] (up to normalization).

## The 6 | N Condition

The condition 6 | N is sharp:
- For N not divisible by 6, algebraic hidden states exist (the ring Z[1/N] is "too small" to force contradiction).
- For 6 | N, the 6 torsion in Z[1/N] forces a contradiction via the 85-vector configuration.
- This connects to the fact that 6 = 2 × 3 is the product of primes appearing in the denominators of the magic-square proof entries.

The condition 6 | N echoes the role of **cyclotomic primes** in [[algebraic-islands-main]] and may relate to [[cyclotomic-fields]].

## Connections to Existing Wiki Articles

- [[algebraic-islands-main]] — the algebraic hidden-state framework is closely related; this paper provides the partial-ring version
- [[kochen-specker-theorem]] — algebraic hidden states generalize KS colorings
- [[ks-set]] — the 85-vector set is a new KS-type configuration in this algebraic sense
- [[cyclotomic-fields]] — the 6 | N condition and Z[1/N] arithmetic connect to cyclotomic/number-theoretic themes
- [[contextuality]] — algebraic contextuality as a variant of standard KS contextuality

## Significance

The paper bridges abstract algebra (ring theory, module theory) and quantum contextuality, showing that the obstruction to hidden-variable models is **arithmetic** in nature — depending on which primes divide N in the coefficient ring. This is a conceptually distinct approach from both the combinatorial (MMP) approach of [[pavicic-2005-ks-vectors]] and the operational (contextual fraction) approach of [[abramsky-2017-contextual-fraction]].

## Open Questions

- Does the 6 | N threshold have a direct physical interpretation?
- Can the partial-ring framework recover the full CSW graph-theoretic hierarchy?
- What is the analog for complex matrix algebras over cyclotomic integer rings?

## Citation

Cortez, R., Schmid, D., & Spekkens, R. W. (2022). Minimal algebraic contextuality via partial rings. *Physical Review Letters*, 129, 230401. https://doi.org/10.1103/PhysRevLett.129.230401
