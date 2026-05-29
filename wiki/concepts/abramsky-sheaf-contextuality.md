---
date_ingested: 2026-04-04
type: concept
---

# Sheaf-Theoretic Contextuality (Abramsky-Brandenburger)

## Definition

The Abramsky-Brandenburger framework reformulates contextuality as the failure of a presheaf of local probability distributions to be a sheaf. A measurement scenario defines a presheaf on a poset of contexts (maximal sets of compatible observables). Local sections are probability distributions on individual contexts that agree on overlaps. Contextuality is the obstruction to gluing these local sections into a consistent global section.

## Key Results

- **Sheaf condition = noncontextuality**: if the presheaf of empirical models is a sheaf, there exists a global hidden-variable model (the model is noncontextual)
- **Strong contextuality**: no global section is compatible with any local data (e.g., PR box, KS sets)
- **Logical contextuality**: some local sections extend globally, others do not
- **Weak contextuality**: all local distributions agree on marginals, but no single global distribution reproduces all correlations
- **Contextual fraction** CF(e): the maximum weight of the contextual part of an empirical model, computed via LP; CF = 0 iff noncontextual, CF = 1 iff strongly contextual. See [[abramsky-2017-contextual-fraction]]
- **Cohomological witnesses**: Cech cohomology of the presheaf detects contextuality; non-trivial cohomology classes correspond to obstructions to global sections

## Connections

- [[contextuality]] --- the sheaf framework provides the hierarchy (strong/logical/weak)
- [[abramsky-2017-contextual-fraction]] --- the contextual fraction as a resource monotone
- [[kochen-specker-theorem]] --- KS sets are instances of strong (logical) contextuality in the sheaf framework
- [[contextuality-logic-probability]] --- the presheaf/sheaf outlook (Section 5) connects to this framework
- [[budroni-2022-ks-review]] --- surveys the sheaf-theoretic approach in Section 5
- [[buchanan-monroe-tqft-2025]] --- extends the sheaf perspective to TQFT cobordisms

## In Our Work

The sheaf-theoretic framework is the reference point for our contextual advantage computations. The CSW inequality alpha(G) <= theta(G) <= alpha*(G) can be seen as a hierarchy of approximations to the sheaf condition. Our algebraic islands produce different contextual fractions, confirming that the operational resource (contextuality) varies across islands even when the logical obstruction (KS-uncolorability) is the same.

## Open Questions

- Is there a sheaf-cohomological invariant that distinguishes the six algebraic islands from each other?
- Can the Cech cohomology of KS configurations be computed from the algebraic structure of the coordinate ring?
- What is the right notion of morphism between sheaf models from different algebraic islands?
