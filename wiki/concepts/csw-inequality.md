---
date_ingested: 2026-04-03
type: concept
---

# CSW Inequality (Cabello-Severini-Winter)

## Definition

A CSW inequality is a noncontextuality inequality (NCI) derived from the [[graph-contextuality|CSW framework]]: given a contextuality scenario with exclusivity graph G, the inequality

  ∑_e p(1|e) ≤ α(G)

bounds the sum of probabilities of obtaining outcome 1 for each event e by the **independence number** α(G) of the exclusivity graph. This bound holds for all noncontextual hidden-variable (NCHV) models. Quantum mechanics can violate it up to the **Lovász theta number** θ(G), and no-disturbance theories can reach the **fractional packing number** α*(G).

The general hierarchy is:

  α(G) ≤ θ(G) ≤ α*(G)

A quantum violation of a CSW inequality — i.e., achieving a value between α(G) and θ(G) — certifies contextuality. A KS set corresponds to the extreme case where no valid 0/1 coloring (no independent set of the required weight) exists at all, which can be understood as an infinite violation in the state-independent limit.

## Key Results

- [[budroni-2022-ks-review]] derives the CSW hierarchy and explains the operational significance of each bound; Lovász theta is computable by semidefinite programming
- [[algebraic-islands-main]] computes α(G), θ(G), and α*(G) for the orthogonality graphs of all six algebraic islands; no single island dominates all three measures
- [[abramsky-2017-contextual-fraction]]: the contextual fraction CF(e) is related to CSW inequalities — CF(e) equals the maximum normalized violation of any Bell/NCI; the dual LP of the contextual fraction optimization witnesses a specific CSW-type inequality. The two frameworks are complementary but distinct
- The CHSH inequality is a special case of a CSW inequality in the bipartite Bell scenario (exclusivity graph = the Kneser graph K(4,1) or related)

## Connections

- [[graph-contextuality]] — the CSW framework that generates these inequalities
- [[contextuality]] — CSW inequalities are the operational witnesses of contextual advantage
- [[kochen-specker-theorem]] — KS sets are state-independent CSW violations (α = 0 for the coloring problem)
- [[abramsky-2017-contextual-fraction]] — contextual fraction as an alternative/complementary measure
- [[algebraic-islands]] — different algebraic islands achieve different CSW advantages
- [[budroni-2022-ks-review]] — authoritative derivation and survey

## In Our Work

The CSW inequality analysis in [[algebraic-islands-main]] is an operationally significant output of the algebraic islands program: it answers the question "given that these six rings all support KS proofs, which provides the strongest contextual resource for practical use?" The computation of Lovász theta for each island's graph is done using exact arithmetic, and the result — that the islands differ in their CSW advantage profiles — motivates further study of which algebraic structures optimize contextual advantage for specific tasks (MBQC, device-independent QKD, certified randomness).

## Open Questions

- Is there an algebraic characterization of which rings maximize θ(G)/α(G) (the quantum-to-classical ratio)?
- Do the two new islands (Heegner-7, golden ratio) offer CSW advantages not achievable by the four known islands?
- Can the CSW violations of the six islands be ordered into a total preorder, or do they form an incomparable partial order?
- Is there a connection between the algebraic degree of the number field and the achieved Lovász theta value?
