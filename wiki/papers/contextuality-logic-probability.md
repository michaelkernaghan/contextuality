---
source: references/corpus/On_Contextuality_as_a_Feature_of_Logic_and_Probabi.pdf
date_ingested: 2026-04-03
type: paper
---

# On Contextuality as a Feature of Logic and Probability Theory (Ellingsen, 2026)

## Summary

This expository paper presents contextuality as a property of collections of probability distributions — a general feature of logic and measure theory — rather than as a peculiarity of quantum mechanics. The paper covers the hierarchy of contextuality types (strong, logical, weak), the role of the Kochen-Specker theorem as a logical obstruction to global truth assignments, and the algebraic framework of partial Boolean algebras.

The paper begins with an Alice-Bob thought experiment (envelope game) that models nonlocal scenarios without quantum mechanics, introducing the key concepts of measurement scenarios, hidden global distributions, and the strong/logical/weak contextuality hierarchy via concrete probability tables. Bundle diagrams (from Abramsky et al.) visualize the obstruction to global sections.

The quantum probability section reviews the Born rule, Specker's principle (pairwise commensurability implies joint commensurability), and why quantum probability distributions can be contextual. The logical section develops Boolean algebras, Stone's representation theorem (every Boolean algebra has a sample space, hence no contextuality), and partial Boolean algebras (Kochen-Specker's original framework) as the correct generalization. The KS theorem is stated as: there exists no morphism of partial Boolean algebras Proj(C^3) -> 2, i.e., no global two-valued state on all C^3 projections.

The outlook section proposes that weak contextuality is the failure of the presheaf of local probability distributions to be a sheaf, connecting to Abramsky-Brandenburger's sheaf-theoretic framework.

## Key Claims

- Contextuality is a general feature of collections of probability distributions, not specific to quantum mechanics
- Strong contextuality: no global value assignment is compatible with any local data (PR box example)
- Logical contextuality: some but not all local sections extend to global sections
- Weak (probabilistic) contextuality: local distributions agree on marginals but no global distribution reproduces all correlations (CHSH example)
- Hierarchy: Strong implies Logical implies Weak; signalling is independent
- Stone's theorem implies that any Boolean algebra has a sample space, hence probability distributions over a Boolean algebra cannot be contextual
- Partial Boolean algebras (commensurability relation not assumed transitive globally) are the right framework for contextual logic
- Specker's principle (pairwise commensurability implies joint commensurability) is built into partial Boolean algebras
- KS theorem (Kochen-Specker): no morphism of partial Boolean algebras Proj(C^3) -> 2 exists
- Weak contextuality = failure of the presheaf of local probability measures to be a sheaf

## Methods

- Alice-Bob envelope game: probabilistic thought experiment modeling nonlocal scenarios; uses 4x4 conditional probability tables and bundle diagrams
- Bundle diagrams (Abramsky et al.): visualize contextuality as failure of global sections; closed loops in bundle diagram correspond to consistent global value assignments
- Boolean algebra theory: lattices, Stone's representation theorem, Stone spectrum S(A) = BA(A, 2)
- Partial Boolean algebras (Kochen-Specker): commensurability relation, colimit characterization (van den Berg-Heunen), KS theorem as corollary
- Presheaf/sheaf framework (outlook): sheaf condition = ability to glue compatible local sections to a global section; contextuality = failure of sheaf condition

## Relevance to Our Work

- The paper provides the clearest expository framework for the two types of contextuality our work engages: KS-type (logical obstruction to global truth assignments, relevant to our KS-uncolorability proofs in [[algebraic-islands-main]]) and Bell-type (probabilistic obstruction, relevant to our CSW inequality and BPQS computations)
- The partial Boolean algebra framework (Section 4.4) is the algebraic language in which our KS sets live: each algebraic island defines a partial Boolean algebra of orthogonal projections
- Stone's theorem result (any Boolean algebra is concrete, hence admits a sample space) explains why classical hidden-variable models fail for our KS sets: the partial Boolean algebra Proj(C^3) is not embeddable into a Boolean algebra
- The presheaf/sheaf outlook (Section 5) connects to the Abramsky-Brandenburger framework which is a reference point for our contextual advantage computations
- See also [[faithful-real-embedding]] for a concrete illustration of why KS-uncolorability is a property of the partial Boolean algebra with maximal contexts, not of the orthogonality hypergraph alone
- See also [[trandafir-cabello-2025-optimal-bpqs]] for the connection between KS sets (logical contextuality) and BPQS (strong contextuality in a bipartite game)

## Open Questions

- Can the CSW inequality violations computed in [[algebraic-islands-main]] be classified as strong, logical, or merely weak contextuality?
- Is there a sheaf-cohomological invariant that distinguishes the six algebraic islands from each other?
- Does the van den Berg-Heunen colimit characterization of partial Boolean algebras give a computational handle on KS-uncolorability that differs from SAT-based approaches?
- What is the right notion of "morphism" between KS configurations from different algebraic islands?
