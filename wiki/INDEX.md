# Contextuality Knowledge Base Index

> Auto-maintained by LLM. Do not edit manually.

**Last updated:** 2026-04-18
**Article count:** 45

## Concepts

- [[kochen-specker-theorem]] — Foundational impossibility theorem: no NCHV model exists for d>=3; current bounds 24-31 vectors in C^3
- [[contextuality]] — Strong/logical/weak hierarchy, contextual fraction, sheaf-theoretic interpretation, resource theory
- [[algebraic-islands]] — Six discrete algebraic rings supporting KS sets in C^3; two mechanisms (modulus-2 and phase cancellation)
- [[ks-set]] — Definition, key examples (Peres 33x16, CK-31, Cabello 33x14), the >=24 lower bound, rigidity, uniqueness conjecture
- [[cyclotomic-fields]] — Role of cyclotomic alphabets in KS constructions; the complete 6|n theorem
- [[graph-contextuality]] — CSW framework: exclusivity graphs, independence number, Lovasz theta, fractional packing
- [[peres-33-3d]] — The 1991 Peres 33-vector 16-basis set; graph isomorphism with Z[sqrt(-2)]; relation to CK-31
- [[csw-inequality]] — The noncontextuality inequality alpha(G) <= quantum <= theta(G) <= alpha*(G); contextual fraction connection
- [[gleason-theorem]] — Gleason's theorem: all measures on projections are traces; ancestor of KS theorem and algebraic islands program
- [[galois-theory-connection]] — Galois norm/trace characterization of cancellation mechanisms; Heegner number connection; cyclotomic Galois structure
- [[abramsky-sheaf-contextuality]] — Sheaf-theoretic contextuality framework; presheaf failure = contextuality; cohomological witnesses

## Papers

- [[algebraic-islands-main]] — Main paper surveying KS sets across algebraic number rings; establishes the six algebraic islands, two-mechanism (modulus-2 / phase cancellation) classification, and two new KS constructions
- [[cyclotomic-letter]] — PRL letter proving the 6|n theorem: S_n is KS-uncolorable iff 6 divides n; complete algebraic proof with explicit colorings for all non-uncolorable cases
- [[heegner7-letter]] — PRL letter reporting two new KS sets (Heegner-7 ring: 43 vectors; golden ratio field: 52 vectors); introduces the auxiliary ray mechanism and structural tension between proof minimization and CSW contextual advantage
- [[sub31-letter]] — PRL letter on computational evidence for CK-31 optimality; seven search strategies, OCUS certification of integer pool minimum, modulus-2 boundary, and realizability barrier
- [[sub31-overview]] — Extended companion paper surveying the 24-31 gap; eight strategies, full historical context, structural analysis of proof obstacles, plane matching property
- [[universality-letter]] — PRL letter on graph isomorphism of 31-vertex KS sets across coordinate alphabets; six algebraic islands, CK-31 uniqueness conjecture, VF2-verified convergence
- [[pavicic-2005-ks-vectors]] — Constructive/exhaustive enumeration of all 4D KS sets up to 24 vectors using MMP hypergraph encoding and interval arithmetic
- [[pavicic-2019-automated-ks]] — Downward-generation from integer master sets reproducing all 1233 known 4D KS sets; extends to 6D via Eisenstein integers
- [[pavicic-2026-engineering-contextuality]] — Entropy survey: NBMMPH formalism, criticality doctrine, critiques of Cabello-Kleinmann 33-50 and Williams-Constantin 168; 69-50 / 169-120 master class; >99% typicality claim
- [[budroni-2022-ks-review]] — 68-page Reviews of Modern Physics survey covering KS proofs, noncontextuality inequalities, graph theory (CSW), sheaf theory, and applications
- [[cortez-2022-minimal-ring]] — Algebraic hidden states on partial rings over Z[1/N] obstructed iff 6|N (d=3); new 85-vector uncolorable set
- [[abramsky-2017-contextual-fraction]] — Contextual fraction CF(e) via LP equals maximum normalized Bell-inequality violation; resource monotone bounding MBQC failure
- [[cabello-2025-bipartite]] — Every bipartite perfect quantum strategy defines a KS set; BPQSs impossible for 3x3 inputs/outputs
- [[liu-2024-equivalences]] — Proves face-nonsignaling = full-nonlocality = all-versus-nothing = pseudotelepathy for any correlation
- [[cabello-2025-simplest-ks]] — New 33-vector 14-basis KS set in d=3 (beats Peres 16-basis record) via Weyl-Heisenberg action on Yu-Oh rays
- [[trandafir-cabello-2025-rigid-ks]] — Two rigid KS sets in C^3: KS-81 from Hesse super-SIC and CK-31 from Yu-Oh SI-C set; conjectures 31 is minimum
- [[trandafir-cabello-2025-optimal-bpqs]] — ILP algorithm for minimum-cardinality bipartite perfect quantum strategies from KS sets; Peres-24 gives 3x3 BPQS
- [[li-2024-sat-ks]] — MathCheck SAT+CAS pipeline proves any C^3 KS set needs >=24 vectors; 40.3 TiB DRAT certificate
- [[bravyi-2018-quantum-advantage]] — First unconditional quantum advantage proof: constant-depth quantum circuits solve 2D Hidden Linear Function
- [[schwartz-2026-vibe-physics]] — SCET factorization at C-parameter Sudakov shoulder; notable as arXiv paper with calculations by Claude Opus 4.5
- [[faithful-real-embedding]] — Phase-adjusted realification embeds C^3 ray sets into R^6; 165-ray Cabello MUB KS set uncolorable in C^3 but admits classical states in R^6
- [[contextuality-logic-probability]] — Expository introduction to contextuality via partial Boolean algebras, Stone's theorem, and the KS theorem
- [[buchanan-monroe-tqft-2025]] — Reformulates KS theorem as (1+1)-D TQFT using cobordisms; identifies contextuality with failure of cobordism reversal

## People

(none yet)

## Computations

- [[ks-islands]] — Main survey script: six-experiment island analysis, attractor analysis, quadratic field scan, icosahedral exclusion, deep Eisenstein search
- [[ks-sat]] — SAT-based KS coloring engine (Glucose4); essential ray/triad identification; realizability checking via L-BFGS-B
- [[ks-complex]] — Hermitian inner product KS search in C^3 using Eisenstein integers and roots of unity; minimum complex KS = 33
- [[ks-search]] — Original alphabet-based search tool; verifies CK-31; deep-searches integer {0,+/-1,+/-2} alphabet
- [[ks-geometry]] — Geometry-first approach building KS configurations from chains of orthogonal frames via Rodrigues rotations

## Open Questions

(none yet)

## Outputs

- [[site-review-2026-03-16]] — GPT-5.4 peer review of KS atlas website; 7 critical findings including Heegner-7 CSW impossibility and island ontology issues
- [[oxford-review-2026-03-29]] — Oxford-style hostile review of revision's categorical correspondence claim; verdict: MAJOR REVISION
- [[peres-33-basis-record-note]] — Note on Peres-33 vs Cabello-33 basis-count record (33 vectors: 16 vs 14 bases)
- [[2026-04-03-smallest-ks-set-3d]] — Q&A: smallest known KS set is CK-31 (31 vectors); lower bound 24; gap open
- [[lint-2026-04-03]] — Structural lint report: 0 orphans, 1 dead link (abramsky-sheaf-contextuality), 0 stubs, count OK
- [[algebraic-substrate-design-guide]] — Companion note aimed at Pavicic-program audience: substrate-level design rule for contextuality engineering; BPQS cost table; cancellation-heuristic search guide; typicality caveat
