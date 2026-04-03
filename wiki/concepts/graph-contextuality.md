---
date_ingested: 2026-04-03
type: concept
---

# Graph Contextuality (CSW Framework)

## Definition

The graph-theoretic approach to contextuality, developed by Cabello, Severini, and Winter (CSW), models a contextuality scenario as a graph where vertices are measurement events and edges connect mutually exclusive events. This **exclusivity graph** (also called the orthogonality graph for projective measurements) captures the structure of compatibility and mutual exclusivity among outcomes.

The three key graph invariants form a hierarchy of bounds:

| Quantity | Meaning |
|----------|---------|
| α(G) | Independence number — classical (NCHV) bound on any noncontextuality inequality |
| θ(G) | Lovász theta number — quantum bound |
| α*(G) | Fractional packing number — no-disturbance (general probabilistic) bound |

The relation α(G) ≤ θ(G) ≤ α*(G) holds for all graphs, and quantum mechanics saturates the middle position exactly.

A **KS set** defines an exclusivity graph in which the independence number and quantum bound differ: no valid {0,1} coloring (independent set of maximum weight) exists, yet quantum states achieve nonzero contextual advantage.

## Key Results

- [[budroni-2022-ks-review]] covers the CSW framework extensively, including derivation of the Lovász theta bound as the quantum limit for contextuality inequalities
- [[algebraic-islands-main]] computes α(G), θ(G), and α*(G) for the orthogonality graphs of all six algebraic islands, finding that no single island dominates on all CSW measures
- [[abramsky-2017-contextual-fraction]]: the contextual fraction CF(e) and the CSW graph-theoretic hierarchy are related but distinct; CF is defined at the level of probability distributions while CSW bounds operate on the graph structure of the scenario
- In C^3, every triangle in the orthogonality graph is already a basis triple (any two orthogonal rays determine a unique third), so graph isomorphism implies basis hypergraph isomorphism ([[universality-letter]])

## Connections

- [[csw-inequality]] — the specific noncontextuality inequalities derived from the CSW framework
- [[contextuality]] — CSW provides the operational quantification of contextual advantage
- [[kochen-specker-theorem]] — KS sets are the extreme cases where the independence number argument shows no valid coloring exists
- [[ks-set]] — each KS set defines an exclusivity graph with computable CSW invariants
- [[algebraic-islands]] — the six islands produce different exclusivity graphs with different CSW advantages
- [[abramsky-2017-contextual-fraction]] — alternative quantitative framework for contextuality
- [[budroni-2022-ks-review]] — authoritative treatment of the CSW framework

## In Our Work

The CSW framework is used in [[algebraic-islands-main]] to compare the operational significance of the six algebraic islands. Computing θ(G) (Lovász theta) for each island's minimal KS graph reveals which algebraic constructions provide the strongest quantum contextual advantage in the CSW sense. The finding that no island uniformly dominates suggests the six islands represent genuinely different kinds of contextual resource.

## Open Questions

- Is there a systematic relationship between the algebraic origin of a KS set (its island) and its position in the CSW hierarchy (α, θ, α*)?
- Can the CSW violations for the Heegner-7 and golden ratio islands be related to known combinatorial properties of those rings?
- Does graph isomorphism of KS sets from different islands (e.g., Peres and Z[√(−2)] sharing the same graph) imply identical CSW advantage values?
