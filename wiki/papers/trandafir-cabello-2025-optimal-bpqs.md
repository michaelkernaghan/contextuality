---
source: references/corpus/TrandafirCabello2025-optimal-BPQS-2410.17470.pdf
date_ingested: 2026-04-03
type: paper
---

# Optimal Bipartite Perfect Quantum Strategies from Kochen-Specker Sets (Trandafir & Cabello, 2025)

## Summary

This paper establishes the systematic connection between Kochen-Specker sets and bipartite perfect quantum strategies (BPQS). A BPQS is a quantum strategy that allows two spatially isolated players to win every round of a nonlocal game, a task impossible for classical strategies. The paper proves that every BPQS of minimum input cardinality can be derived from a KS set of pure states (rank-one projectors), and provides an integer-linear-programming (ILP) algorithm for finding the minimum-cardinality BPQS associated with any given KS set.

The algorithm is applied to KS sets in dimensions 3 through 8. Key results include: in d=3, the Peres-24 KS set (24 vectors) yields a 3x3 BPQS — the smallest known BPQS by input count. In d=8, the KP-40 KS set yields a 3x4 BPQS. The paper also examines CK-31 and CK-33 (from [[trandafir-cabello-2025-rigid-ks]]) as sources of BPQS and compares cardinalities across algebraic constructions.

The structural theorem proved is: any BPQS of minimum cardinality is equivalent to one derived from a rank-one KS set. This means the search for optimal nonlocal game strategies reduces to the search for small KS sets, establishing a tight bidirectional connection between quantum contextuality and quantum nonlocality.

## Key Claims

- Every bipartite perfect quantum strategy (BPQS) of minimum input cardinality arises from a KS set of pure states
- The Peres-24 KS set (24 vectors in C^3) yields a 3x3 BPQS — the minimum known BPQS in terms of number of inputs per player
- An ILP algorithm finds minimum-cardinality BPQS from any KS set in polynomial time (given small KS sets)
- In d=8, KP-40 gives a 3x4 BPQS
- CK-31 and CK-33 each give BPQS; the exact cardinalities are computed and compared with other d=3 constructions
- The connection is tight: smaller KS sets give smaller (more efficient) BPQS

## Methods

- Integer linear programming (ILP) formulation: given a KS hypergraph, find the minimum set of contexts that can be partitioned into Alice's and Bob's measurement settings consistent with the BPQS winning conditions
- Exhaustive search over KS sets in d=3 through d=8 using known catalogues
- Theoretical proof that rank-one KS sets suffice: higher-rank KS sets do not yield more efficient BPQS

## Relevance to Our Work

- Our algebraic islands paper ([[algebraic-islands-main]]) identifies six algebraic islands in C^3, each with a minimal KS set; this paper's algorithm can be applied to each island's minimal set to compute the corresponding optimal BPQS
- The statement "different algebraic islands yield different bipartite perfect quantum strategies" in [[algebraic-islands-main]] is directly grounded in the framework developed here
- CK-31 (from [[trandafir-cabello-2025-rigid-ks]]) is among the KS sets for which BPQS are computed; comparing with our integer-ring 33-vector set is natural
- The Peres-24 lower bound (24 vectors for a 3x3 BPQS) relates to the SAT lower bound of >=24 in [[li-2024-sat-ks]]: if the minimum KS set in d=3 has >=24 vectors, the Peres-24 set is at or near optimal
- The quantum advantage literature (see [[bravyi-2018-quantum-advantage]]) connects to BPQS: nonlocal games with perfect quantum strategies are one route to provable quantum advantage

## Open Questions

- What is the minimum BPQS cardinality for each of our six algebraic islands' minimal KS sets?
- Does the Heegner-7 island (43-vector set) yield a competitive BPQS, or is it always dominated by smaller-island sets?
- Is there a BPQS with fewer than 3 inputs per player in any dimension >= 3?
- Can the ILP algorithm be extended to mixed-state (non-pure) KS sets?
