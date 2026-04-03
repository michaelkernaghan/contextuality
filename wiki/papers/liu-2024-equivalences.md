---
title: "Equivalences Among Face Nonsignaling, Full Nonlocality, All-Versus-Nothing, and Pseudotelepathy"
slug: liu-2024-equivalences
authors: ["Xiao-Li Liu", "Zhen-Peng Xu", "Adán Cabello"]
year: 2024
journal: "Physical Review A"
doi: "10.1103/PhysRevA.110.022424"
tags: [pseudotelepathy, all-versus-nothing, full-nonlocality, face-nonsignaling, nonlocality, equivalences, Bell-inequalities, qutrit]
status: read
---

# Equivalences Among Face Nonsignaling, Full Nonlocality, All-Versus-Nothing, and Pseudotelepathy

## Summary

This paper proves a four-way equivalence among seemingly distinct notions of maximal nonclassicality in multipartite correlations: **face nonsignaling (FNS)**, **full nonlocality (FN)**, **all-versus-nothing (AVN)**, and **pseudotelepathy (PT)**. The equivalences hold in arbitrary scenarios. The paper also shows that quantum mechanics forbids FNS=FN=AVN=PT correlations in the (3,3;3,2) and (3,2;3,4) scenarios, and that not all FNS=FN=AVN=PT correlations define tight Bell inequalities.

## Core Results

### Theorem: FNS = FN = AVN = PT

For any empirical model (joint probability distribution) e over a bipartite (or multipartite) measurement scenario:

- **FNS (face nonsignaling)**: e lies on a face of the nonsignaling polytope that contains no local deterministic point. Equivalently, e is not on the boundary shared with any local model.
- **FN (full nonlocality)**: e is not a mixture of any model with a local component; fully nonlocal.
- **AVN (all-versus-nothing)**: e violates some Bell inequality in an all-or-nothing fashion (the local bound is 0 and e achieves the maximum 1, or equivalently, no local strategy achieves any positive success probability).
- **PT (pseudotelepathy)**: e comes from a quantum strategy that wins a nonlocal game with probability 1, impossible for any classical (local) strategy.

**The theorem**: For any e, FNS ⟺ FN ⟺ AVN ⟺ PT.

### Impossibility Results

- In the **(3,3;3,2) scenario** (2 parties, 3 inputs each, one with 3 outputs and one with 2 outputs): quantum mechanics forbids any FNS=FN=AVN=PT correlation. No pseudotelepathy exists here.
- In the **(3,2;3,4) scenario**: Similarly forbidden.

These are derived by exhaustive analysis of the possible strategies and Bell inequality structure.

### Bell Inequality Tightness

Not all FNS=FN=AVN=PT correlations correspond to tight (facet-defining) Bell inequalities. Some maximally nonclassical correlations lie on non-facet faces of the local polytope — important for the resource theory and for experimental detection.

## Key Connections

The contextual fraction of any FNS=FN=AVN=PT correlation is CF = 1 (by definition: no noncontextual part). This connects to [[abramsky-2017-contextual-fraction]], where strong contextuality (CF=1) is the sheaf-theoretic version of AVN.

The connection to KS sets: every PT correlation (pseudotelepathy) arises from a quantum strategy whose local measurement operators form (or contain) a KS set — as shown in [[cabello-2025-bipartite]].

## Connections to Existing Wiki Articles

- [[contextuality]] — FNS=FN=AVN=PT are all forms of maximal contextuality/nonlocality
- [[abramsky-2017-contextual-fraction]] — CF = 1 iff strong contextuality iff AVN
- [[cabello-2025-bipartite]] — every BPQS (PT) defines a KS set
- [[cabello-2025-simplest-ks]] — the simplest KS set in d=3 enables a PT strategy
- [[kochen-specker-theorem]] — KS theorem as the origin of AVN-style arguments
- [[csw-inequality]] — Bell inequalities and their tight/non-tight facial structure
- [[graph-contextuality]] — graph-theoretic framework for the local polytope

## Proof Strategy

- **FNS → FN**: Show that being on a face disjoint from local deterministic points forces full nonlocality.
- **FN → AVN**: Construct an explicit Bell functional that witnesses all-or-nothing violation.
- **AVN → PT**: The all-or-nothing Bell functional corresponds to a nonlocal game with a perfect quantum strategy.
- **PT → FNS**: Perfect quantum strategies produce distributions outside any face containing local points.
- The circular chain of implications closes the equivalence.

## Citation

Liu, X.-L., Xu, Z.-P., & Cabello, A. (2024). Equivalences among face nonsignaling, full nonlocality, all-versus-nothing, and pseudotelepathy. *Physical Review A*, 110, 022424. https://doi.org/10.1103/PhysRevA.110.022424
