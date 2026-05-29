---
date_ingested: 2026-04-04
type: concept
---

# Galois Theory Connection

## Definition

The six [[algebraic-islands]] that support KS-uncolorable ray sets in C^3 are all quadratic extensions of Q (or Q itself). The Galois group Gal(K/Q) = Z/2Z acts on the coordinate ring and, by extension, on the ray sets, orthogonality graphs, and KS hypergraphs. The two cancellation mechanisms that classify the islands --- modulus-2 and phase --- restate as conditions on the Galois norm and trace of the ring generator.

## Galois Structure of the Six Islands

| Island | Field K | Gal(K/Q) | Generator x | N(x) | Tr(x) | Mechanism |
|--------|---------|----------|-------------|-------|--------|-----------|
| Integer | Q | trivial | 2 | 4 | 4 | modulus-2 (degenerate) |
| Peres | Q(sqrt(2)) | Z/2Z | sqrt(2) | -2 | 0 | modulus-2 |
| Eisenstein | Q(sqrt(-3)) | Z/2Z | omega | 1 | -1 | phase |
| Z[sqrt(-2)] | Q(sqrt(-2)) | Z/2Z | i*sqrt(2) | 2 | 0 | modulus-2 |
| Heegner-7 | Q(sqrt(-7)) | Z/2Z | (1+sqrt(-7))/2 | 2 | 1 | modulus-2 |
| Golden | Q(sqrt(5)) | Z/2Z | phi | -1 | 1 | completion-induced |

Here N(x) = x * sigma(x) is the algebraic norm and Tr(x) = x + sigma(x) is the algebraic trace, where sigma is the non-trivial Galois automorphism sending sqrt(d) to -sqrt(d).

## Key Results

### Cancellation mechanisms as Galois invariants

The two cancellation mechanisms have clean Galois-theoretic characterizations:

- **Modulus-2 cancellation**: The ring-of-integers generator x satisfies |N_{K/Q}(x)| = 2. For imaginary quadratic fields, this equals the Hermitian modulus |x|^2. The cancellation identity arises because the norm maps the generator to +/-2, which factors as 1+1 in Z. This is the characterization for the Peres, Z[sqrt(-2)], and Heegner-7 islands.

- **Phase cancellation**: The generator x satisfies Tr_{K/Q}(x) = -1 and N_{K/Q}(x) = 1. This characterizes roots of the cyclotomic polynomial x^2 + x + 1 = 0. The identity 1 + omega + omega^2 = 0 is equivalent to the statement that Tr(omega) = omega + sigma(omega) = omega + omega^2 = -1. This is the Eisenstein island.

Both mechanisms are therefore conditions on the Galois norm and trace --- the two fundamental invariants of a quadratic extension.

### Galois action on the KS hypergraph

The non-trivial Galois automorphism sigma acts coordinate-wise on K^3. Since sigma is a ring homomorphism:

- For real quadratic fields: sigma(<v|w>) = <sigma(v)|sigma(w)>, so sigma preserves orthogonality
- For imaginary quadratic fields: sigma commutes with complex conjugation (since sigma(sqrt(-d)) = -sqrt(-d) and conjugation gives -sqrt(-d) as well when d > 0), so sigma preserves Hermitian orthogonality
- Therefore sigma is an automorphism of the orthogonality graph, the basis hypergraph, and the KS coloring problem
- If f is a valid KS coloring, then f composed with sigma is also a valid coloring (or both fail to exist)

This gives an additional symmetry of the KS hypergraph beyond the unitary symmetries. For the [[universality-letter]] result that all 31-ray minimizations converge to the same graph, Galois conjugation may relate realizations across different islands.

### Heegner number connection

The imaginary quadratic fields Q(sqrt(-d)) with class number 1 (unique factorization in the ring of integers) are exactly the Heegner number fields: d = 1, 2, 3, 7, 11, 19, 43, 67, 163.

Among the tested imaginary quadratic fields, the KS-supporting ones are d = 2, 3, 7 --- all Heegner numbers. The failures have clear arithmetic explanations:

- d = 1 (Gaussian integers): |i|^2 = 1, norm too small (same as trivial alphabet)
- d = 11, 19, ..., 163: |sqrt(-d)|^2 = d >= 11, norm too large for low-complexity cancellation
- d = 5, 6, etc.: not class number 1, ring of integers is not a PID

This yields a precise characterization: **among imaginary quadratic fields, the KS-supporting ones are exactly the Heegner-number fields where the ring-of-integers generator has algebraic norm 2 (d = 2, 7) or is a primitive cube root of unity (d = 3)**.

Whether class number 1 is necessary for KS-uncolorability, or merely coincidental among low-norm fields, is an open question.

## Cyclotomic Galois Structure

The [[cyclotomic-fields]] result (S_n is KS-uncolorable iff 6|n) has a natural Galois reformulation. The Galois group Gal(Q(zeta_n)/Q) is isomorphic to (Z/nZ)*. The condition 6|n is equivalent to requiring that this group has quotients corresponding to both Z/2Z and Z/3Z:

- 2|n ensures -1 = zeta^{n/2} is in the alphabet, enabling interlocking (two-term cancellations)
- 3|n ensures omega = zeta^{n/3} is in the alphabet, enabling phase cancellation (three-term vanishing sums)

In Galois terms: the group (Z/nZ)* must have elements of order dividing both phi(2) and phi(3), which requires 6|n. The proof in [[cyclotomic-letter]] that isolated triads (Case 3: 3|n, 2 does not divide n) are always colorable is essentially the statement that the Galois group action decomposes the KS constraint network into independent orbits when only the order-3 subgroup acts.

## Connections

- [[algebraic-islands]] --- the six islands are quadratic extensions classified by Galois norm/trace
- [[cyclotomic-fields]] --- the 6|n theorem restated via Galois group structure of (Z/nZ)*
- [[kochen-specker-theorem]] --- Galois conjugation as a symmetry of the KS obstruction
- [[gleason-theorem]] --- the trace in Gleason's theorem (matrix trace) vs. the Galois trace (sum over conjugates); both encode the same 2-and-3 arithmetic
- [[cortez-2022-minimal-ring]] --- the 6|N condition as a ramification/invertibility condition on primes 2 and 3
- [[universality-letter]] --- Galois action as an additional symmetry explaining graph-isomorphism across islands

## In Our Work

The Galois-theoretic perspective reframes the algebraic islands program: instead of asking "which coordinate alphabets support KS sets?", one asks "for which number fields K/Q does the Galois norm or trace of the ring-of-integers generator produce the arithmetic needed for KS-uncolorability?" The answer is governed by the values N_{K/Q}(x) and Tr_{K/Q}(x) for the generator x of O_K.

The norm/trace formulation also suggests a path toward proving the two-mechanism pattern is exhaustive: any quadratic extension of Q has exactly two Galois invariants (norm and trace) of its generator, and these determine the cancellation arithmetic. A proof that |N| = 2 and (Tr = -1, N = 1) are the only norm/trace combinations yielding low-complexity cancellation would close the classification for quadratic fields.

## Open Questions

- Does the Galois automorphism sigma map KS sets within one island to KS sets in a "conjugate" island? (e.g., does sigma on Q(sqrt(2), sqrt(-3)) relate Peres and Eisenstein configurations?)
- Can the compositum field Q(sqrt(2), sqrt(-3)) with Galois group (Z/2Z)^2 (Klein four-group) produce denser KS sets or smaller minimums than either island alone?
- Is class number 1 necessary for KS-uncolorability, or merely a low-norm artifact? Testing d = 11 with larger alphabets (not just {0, +/-1, +/-sqrt(-11)}) would help distinguish.
- Can class field theory --- specifically the conductor of abelian extensions --- provide a unified framework? The conductor of Q(zeta_6) is 6, the same number appearing in Cortez's Z[1/6] and the cyclotomic 6|n theorem.
- Does the Frobenius element at primes 2 and 3 in Gal(K/Q) determine KS-uncolorability for a given field K?
- For higher-degree extensions (e.g., the cubic island Q(cbrt(2))), does the larger Galois group (S_3 for the splitting field) give additional structural constraints on KS sets?
