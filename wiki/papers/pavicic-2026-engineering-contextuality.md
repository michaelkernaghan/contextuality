---
title: "Engineering and Applying Quantum Contextuality"
slug: pavicic-2026-engineering-contextuality
authors: ["Mladen Pavičić"]
year: 2026
journal: "Entropy"
doi: "10.3390/e28040446"
tags: [kochen-specker, MMP-hypergraph, NBMMPH, criticality, 3D, 4D, 69-50, Williams-Constantin, BPQS, pseudo-telepathy, Hadamard]
status: read
---

# Engineering and Applying Quantum Contextuality

## Summary

A wide-ranging survey-plus-position paper by Pavičić (Entropy 28, 446, April 2026) consolidating two decades of MMP-hypergraph work on Kochen-Specker (KS) sets and related contextual structures, and arguing that contextuality is a generic ("99% typical") property of the algebraic / combinatorial objects his group produces. The paper defends the non-binary MMP-hypergraph language (NBMMPH) as the correct formalism, re-iterates the distinction between *critical* and *non-critical* contextual sets, critiques several recent "simplest KS" claims (Cabello-Kleinmann, Williams-Constantin), and surveys engineering applications: Bell-KS pseudo-telepathy games, weak-measurement protocols, and Hadamard-matrix constructions.

## Core Contributions

- **NBMMPH as a unifying formalism**: Extends MMP hypergraphs to non-binary (>2-valent) hyperedges; argues this captures contextual structure uniformly across dimensions and over arbitrary coordinate rings.
- **Criticality doctrine**: Distinguishes *critical* KS sets (no proper sub-KS) from non-critical ones. Claims many recent "smallest" results in the literature refer to non-critical sets and therefore do not establish minimality.
- **Critique of Cabello-Kleinmann "simplest" 33-50**: Argues the 33-vertex / 50-edge Peres-like set promoted as the simplest 3D KS set is *not critical* once embedded in its ambient hypergraph, and contrasts it with Pavičić's own 69-50 master class (169-120 family) from which many smaller subsets descend.
- **Critique of Williams-Constantin 3D lower bound**: Challenges the 168-direction construction and associated lower-bound claims on methodological grounds (boundary conditions, hyperedge counting).
- **Revisits Clifton's "bug" theorem**: Re-examines dimensional constraints on parity-proof-free KS sets in C^3.
- **Engineering survey**: Summarizes Bell-KS / bipartite perfect quantum strategies (BPQS), weak-measurement schemes, Hadamard-matrix KS coordinatizations, and claims generic (>99%) contextuality of randomly chosen MMP hypergraphs above threshold size.

## Key Results

| Topic | Claim |
|-------|-------|
| 3D simplest KS | 33-50 (Cabello 2025) is non-critical inside a larger master set; the true master is 69-50 / 169-120 |
| 3D lower bound | Williams-Constantin 168-direction construction and bound are contested |
| Criticality | Critical KS sets are rare relative to non-critical contextual sets |
| Typicality | >99% of MMP hypergraphs above a size threshold are contextual (empirical) |
| Engineering | NBMMPH enables systematic search for BPQS, pseudo-telepathy, and Hadamard-based protocols |

## Methods

- NBMMPH formalism, MMPSTRIP / MMPSUBGRAPH / VECFIND pipeline (see [[pavicic-2019-automated-ks]])
- Master-set downward generation from 69-50 and 169-120 hypergraphs in 3D
- Constraint propagation + nauty/Traces isomorphism filtering
- Empirical sampling for typicality claims

## Relevance to Our Work

**Primary overlap — the completion principle.** The substantive point of contact with [[algebraic-islands-main]] is Pavičić's insistence that stripped "non-KS" vertex configurations are misleading unless the geometrically forced completion vectors are restored. He treats the *filled* hypergraph as the genuine carrier of structure. This maps directly onto our cross-product completion caveat (Section 2.4 of the main paper): the island classification is properly a classification of *completed coordinate algebras*, not of the raw generating alphabets. The golden island is the cleanest example — the raw alphabet $\{0, \pm 1, \pm\varphi\}$ is colorable, but completion introduces $1/\varphi$ and yields KS-uncolorability. Pavičić's methodological line therefore lends outside support to our framing and is the right citation target.

**Secondary points (not threats, not primary citation material):**

- *33-50 non-criticality critique of [[cabello-2025-simplest-ks]]*: Pavičić argues the set is not critical in NBMMPH and descends from a 69-50 / 169-120 master. This is orthogonal to our minimality notions (coordinate-ring minimality, ray-count minimality). The three "simplest" claims need not coincide and here do not.
- *Williams-Constantin critique (§2.8)*: Pavičić attacks a Clifton-bug-style lower-bound route. Our lower-bound discussion uses SAT/OCUS and realizability instead, so this critique neither helps nor hurts.

**What Pavičić's paper does NOT do**: no algebraic classification of coordinate fields, no modulus-2 / phase-cancellation dichotomy, no number-theoretic substrate as the explanatory variable. His language is hypergraph-first; ours is coordinate-algebra-first. Our main novelty claim is untouched.

**Implication for the paper**: A short citation placed at the completion caveat (Section 2.4, near line 128 of algebraic_islands.tex) is sufficient. The earlier-drafted longer insert at Section 5.4 (BPQS) was removed — wrong axis of contact.

## Connections to Existing Wiki Articles

- [[algebraic-islands-main]] — our classification; Pavičić's master sets are the combinatorial upper bound
- [[cabello-2025-simplest-ks]] — the 33-50 claim Pavičić critiques
- [[pavicic-2005-ks-vectors]] — foundational MMP-hypergraph paper
- [[pavicic-2019-automated-ks]] — automated master-set generation
- [[trandafir-cabello-2025-rigid-ks]] — rigidity notion orthogonal to criticality
- [[cabello-2025-bipartite]] — BPQS / Bell-KS, one of Pavičić's engineering applications

## Open Questions

- Is every one of our six algebraic islands a sub-hypergraph of Pavičić's 69-50 / 169-120 master class, or do the Heegner-7 and Golden islands require a larger master?
- Does the empirical ">99% contextuality typicality" claim survive when the sampling is constrained to coordinatizable hypergraphs (i.e., those admitting a realization over some number field)?
- Relationship between NBMMPH-criticality and the Galois-rigidity criterion: can one imply the other under dimensional or arithmetic constraints?

## Citation

Pavičić, M. (2026). Engineering and Applying Quantum Contextuality. *Entropy*, 28(4), 446. https://doi.org/10.3390/e28040446
