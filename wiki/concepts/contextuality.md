---
date_ingested: 2026-04-03
type: concept
---

# Contextuality

## Definition

Contextuality is the property of a set of measurement statistics that cannot be explained by a hidden-variable model in which each observable has a predetermined value independent of which other compatible observables are simultaneously measured. It is a general feature of collections of probability distributions, not specific to quantum mechanics — as demonstrated in [[contextuality-logic-probability]] via a classical Alice-Bob envelope game.

The hierarchy has three levels (from [[contextuality-logic-probability]] and [[budroni-2022-ks-review]]):

- **Strong contextuality**: no global value assignment is compatible with any local data (CF = 1; equivalently, all-versus-nothing / pseudotelepathy)
- **Logical contextuality**: some but not all local sections extend globally
- **Weak (probabilistic) contextuality**: local distributions agree on marginals but admit no global joint distribution

**KS contextuality** (state-independent contextuality, SI-C) is the strongest form: no valid {0,1} assignment exists across all projection operators regardless of the quantum state.

## Key Results

- [[budroni-2022-ks-review]]: comprehensive survey of KS contextuality, noncontextuality inequalities, graph-theoretic bounds, and applications to computation and cryptography
- [[abramsky-2017-contextual-fraction]]: the contextual fraction CF(e) ∈ [0,1] is the canonical quantitative measure; CF(e) = 0 iff noncontextual, CF(e) = 1 iff maximally contextual; computable via linear programming
- CF(e) equals the maximum normalized violation of any Bell/noncontextuality inequality and is a monotone under free (noncontextual) operations
- MBQC connection ([[abramsky-2017-contextual-fraction]]): higher contextual fraction → lower failure probability in measurement-based quantum computation
- [[contextuality-logic-probability]]: weak contextuality is the failure of the presheaf of local probability distributions to satisfy the sheaf condition; Stone's theorem explains why classical logic cannot be contextual

## Connections

- [[kochen-specker-theorem]] — the foundational impossibility result for NCHV models
- [[ks-set]] — finite witnesses of state-independent contextuality
- [[graph-contextuality]] — the CSW framework quantifies contextual advantage via graph invariants
- [[csw-inequality]] — operational noncontextuality inequalities
- [[abramsky-2017-contextual-fraction]] — quantitative resource theory
- [[budroni-2022-ks-review]] — comprehensive review

## In Our Work

Our algebraic islands research operates primarily at the level of KS contextuality (SI-C): a ray set is KS-uncolorable if and only if it witnesses state-independent contextuality. The [[algebraic-islands-main]] paper additionally computes CSW contextual advantage values (Lovász theta numbers) for each of the six islands, showing that no single island dominates on all operational measures of contextual advantage.

## Open Questions

- Can the CSW inequality violations in [[algebraic-islands-main]] be classified as strong, logical, or merely weak contextuality?
- Is there a sheaf-cohomological invariant that distinguishes the six algebraic islands?
- What is the right notion of morphism between KS configurations from different algebraic islands?
