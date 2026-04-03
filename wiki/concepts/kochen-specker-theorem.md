---
date_ingested: 2026-04-03
type: concept
---

# Kochen-Specker Theorem

## Definition

The Kochen-Specker (KS) theorem states that no noncontextual hidden-variable (NCHV) model can reproduce the predictions of quantum mechanics in Hilbert space dimension d ≥ 3. Concretely: there exists no assignment of definite values {0, 1} to all projection operators on C^3 that simultaneously (a) assigns exactly one 1 to each orthogonal basis (completeness) and (b) is consistent across shared basis elements (noncontextuality). Such an assignment is called a KS coloring; the theorem says no valid coloring exists.

In the algebraic formulation of [[contextuality-logic-probability]], the theorem states there is no morphism of partial Boolean algebras from Proj(C^3) to the two-element Boolean algebra 2 — equivalently, the projection lattice of C^3 cannot be embedded into a Boolean algebra.

## Key Results

- Original proof (Kochen-Specker 1967): 117 vectors in R^3; subsequently reduced by Bell, Conway, Kochen, Peres, Cabello, and others
- The theorem requires d ≥ 3; in d = 2 (qubit), NCHV models do exist
- A finite witness suffices: a [[ks-set]] is a finite set of vectors admitting no valid KS coloring
- Current smallest known KS set in C^3: 31 vectors (CK-31); see [[ks-set]]
- The theorem implies state-independent contextuality (SI-C): any quantum state violates some noncontextuality inequality derivable from the KS configuration
- The [[contextuality-logic-probability]] paper establishes that Stone's theorem for Boolean algebras implies no contextuality obstruction in classical logic; the KS theorem marks precisely where the classical framework fails

## Connections

- [[ks-set]] — the finite combinatorial witnesses of the theorem
- [[contextuality]] — the broader resource-theoretic and operational framework
- [[kochen-specker-theorem]] is reviewed extensively in [[budroni-2022-ks-review]]
- [[algebraic-islands-main]] — establishes which coordinate alphabets support KS constructions
- [[cyclotomic-letter]] — proves a sharp characterization theorem for the cyclotomic family

## In Our Work

The KS theorem is the foundational result that our algebraic islands program is organized around. Our main question is: for which algebraic number rings do finite KS sets exist in C^3? The answer turns out to be structured into six discrete [[algebraic-islands]], each supporting KS-uncolorable ray sets. The [[cyclotomic-letter]] gives the sharpest such classification: for cyclotomic coordinate alphabets, KS-uncolorability occurs if and only if 6 divides n.

## Open Questions

- What is the minimum number of vectors in any C^3 KS set? The current bounds are 24 (SAT lower bound, [[li-2024-sat-ks]]) and 31 (smallest known, CK-31)
- Is there a human-readable proof of the ≥ 24 lower bound?
- Does a KS theorem analogue hold for other algebraic structures beyond Hilbert spaces?
