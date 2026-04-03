---
source: raw/contextual_TQFT.pdf
date_ingested: 2026-04-03
type: paper
authors: Ryan J. Buchanan, Derik A. Monroe
year: 2025
---

# Diagnosing Contextuality in a Topological Quantum Field Theory: a Toy Model

**Authors:** Ryan J. Buchanan (Active Inference Institute), Derik A. Monroe
**Date:** June 2025

## Abstract

This paper synthesizes the authors' previously developed modal contexts with quantum contextuality. It reformulates the Kochen-Specker (KS) theorem in terms of cobordisms and provides a concrete example of a (1+1)-dimensional topological quantum field theory (TQFT) as a toy model. The central claim is that the KS theorem is equivalent to a special type of TQFT.

## Core Framework

### Measurement Scenarios as Fiber Bundles

The paper recasts measurement scenarios in the language of fiber bundles. A scenario is defined as a pair (M, C) where M is the product of measurements over an I-indexed family of orbifolds O_i. Contextuality arises when fibers over measurement points fail to be globally sectionable — i.e., when local sections cannot be glued into a global one (the standard sheaf-theoretic interpretation from Abramsky-Brandenburger).

The obstruction is formalized via the bundle:

    pi : C -> union(O_i)

The KS theorem states that for a point p_i in O_i, the fiber pi^{-1}(p_i) fails to be dense if and only if p_i is outside the measurement scenario S.

### Modal Logic Encoding

Contextuality is expressed modally. In a context-free scenario, the truth value assigned to a measurement in any context C_i must equal the truth value under any other context (necessary equality). Contextuality violates:

    forall i, p, C: [box Omega_{C_bullet}(p_i)]

where the necessity operator boxes the join of all possible subcontexts.

## The TQFT Construction

### Cobordism Category Cob_2

The paper works in the oriented 2-dimensional cobordism category Cob_2 (Atiyah's axioms). Objects are disjoint unions of oriented circles (S^1). Morphisms are oriented 2-dimensional cobordisms M : Sigma_1 -> Sigma_2.

Key morphism types:

| Cobordism | Diagrammatic | Physical Meaning |
|---|---|---|
| S^1 sqcup S^1 -> S^1 | Pair of pants | Fusion of two particles |
| S^1 -> S^1 sqcup S^1 | Cobranching | Branching of a single system |
| S^1 -> S^1 | Cylinder | Identity/time evolution |
| empty -> S^1 | Cap | Creation of a state |
| S^1 -> empty | Cup | Annihilation of a state |

### Hilbert Space Bifurcation and Contextuality

Each O_i is treated as the disjoint union of two strata corresponding to two possible Hilbert spaces H_{diamond,1} and H_{diamond,2}. The "necessary" Hilbert space is H_square. The cobordism becomes:

    Sigma : H_square -> H_{diamond,(1)} sqcup H_{diamond,(2)}

**Theorem 3.1 (TQFT Kochen-Specker):** A cobordism is contextual if and only if for some time evolution operator U acting on H_square, the resulting scenarios are mutually incompatible.

**Theorem 3.2:** In a contextual TQFT, the reversed cobordism Sigma-bar is not well-defined.

### Minimal Example

The worked example uses two non-commuting observables {A, B} with AB = -BA. Context C_{diamond,1} = {A}, C_{diamond,2} = {B}. Since A and B cannot be simultaneously diagonalized, no assignment phi: A |-> a, B |-> b can be extended from H_{diamond,1} and H_{diamond,2} back to H_square while preserving spectral constraints.

The monoidal structure consequently breaks:

    Z(Sigma) != Z(H_{diamond,1}) tensor Z(H_{diamond,2})

This is a precise modal obstruction: each context admits a local section, but the pullback to C_square fails.

## Future Directions

1. Extension to higher-dimensional TQFTs (Cob_n for n > 2)
2. Cohomological formulations (Cech or sheaf cohomology capturing contextual obstructions)
3. Functorial quantization: functor Z : MeasCob -> Vect_C
4. Computational models for classifying contextual phenomena in quantum computation
5. Ultranautical Observables: diagnosing discrepancies between measurement contexts

## Assessment Notes

The paper operates at an expository/philosophical level rather than a technical one. The "proof" of Theorem 1.1 is brief and leans heavily on appeal to the KS theorem without constructing the required algebraic maps explicitly. The TQFT Kochen-Specker theorems (3.1, 3.2) are presented as interpretive reformulations rather than proven theorems in the formal sense. The cobordism reversal argument is intuitive but not rigorously derived.

This is nonetheless useful background for thinking about categorical/topological framings of KS contextuality, and the MeasCob proposal is a concrete research direction.

## References (Selected)

- Kochen & Specker (1967) — original KS theorem
- Abramsky, Mansfield & Barbosa (2012) — cohomology of non-locality and contextuality
- Isham & Butterfield — topos perspective on KS theorem
- Atiyah (1988) — topological quantum field theories
- Buchanan & Monroe — "Context-Dependent Logic" (DOI: 10.22541/au.173801320.09343751/v1)

## Related

- [[kochen-specker-theorem]]
- [[abramsky-sheaf-contextuality]]
- [[algebraic-islands-main]]
