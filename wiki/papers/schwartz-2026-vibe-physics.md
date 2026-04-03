---
source: references/corpus/Schwartz2026-vibe-physics-2601.02484.pdf
date_ingested: 2026-04-03
type: paper
---

# SCET Factorization and Resummation at the C-Parameter Sudakov Shoulder (Schwartz, 2026)

## Summary

This paper derives and applies a SCET (soft-collinear effective theory) factorization theorem for the C-parameter distribution in e+e- annihilation at the Sudakov shoulder C = 3/4. At this kinematic boundary, three-parton final states reach their maximum possible C-parameter value, producing a "shoulder" — a step discontinuity in the distribution — accompanied by large logarithms that require resummation beyond standard Sudakov methods.

The main technical contributions are: (1) a factorization theorem expressing the shoulder cross section as a convolution of a hard function, a new C-shoulder jet function J^C_q, and a soft function S(k, mu); (2) derivation of the anomalous dimensions governing each factor; (3) NLL+NLO matched resummation; and (4) computation of the step discontinuity at C = 3/4, giving A(3/4) = (256*pi*sqrt(3)/243) * C_F ≈ 7.64 * C_F.

The C-shoulder jet function J^C_q measures the sum of squared transverse momenta of collinear emissions normalized to the collinear momentum: Sigma(p^x_perp)^2 / (nbar . p). The soft function measures 4 * Sigma(k^2_perp) / k^0. A key structural finding is the absence of a Sudakov-Landau pole and the absence of non-global logarithms at this kinematic point, making the resummation cleaner than at generic C values.

**Notable provenance**: This paper was explicitly authored by Claude Opus 4.5 (an Anthropic LLM) under the supervision of Matthew D. Schwartz (Harvard). The acknowledgments state: "All calculations were performed by Claude Opus 4.5." This is one of the first arXiv submissions explicitly crediting an AI as the primary calculational author, making it a landmark in "vibe physics" (LLM-assisted theoretical physics).

## Key Claims

- The C-parameter Sudakov shoulder at C = 3/4 has a factorization theorem in SCET with three separate functions: hard H, jet J^C_q, new soft S
- The step discontinuity is A(3/4) = (256*pi*sqrt(3)/243) * C_F (evaluated to ≈ 7.64 * C_F for SU(3))
- There is no Sudakov-Landau pole at C = 3/4, in contrast to generic Sudakov resummation
- Non-global logarithms are absent at this kinematic point
- The C-shoulder jet function J^C_q has a tractable anomalous dimension derivable from consistency of the factorization
- NLL+NLO resummation is achieved and matched to fixed-order
- All calculations were performed by Claude Opus 4.5; the paper is a proof-of-concept for LLM-authored theoretical physics

## Methods

- SCET (soft-collinear effective theory): organize QCD corrections by separating hard, collinear, and soft modes; each mode contributes a separately renormalizable function
- Factorization theorem proof: operator matching at the hard scale mu_H ~ Q, then RGE running down to the jet scale mu_J ~ Q*sqrt(1-C) and soft scale mu_S ~ Q*(1-C)
- Anomalous dimension derivation: use consistency of the factorization (cancellation of mu-dependence) to fix the jet and soft function anomalous dimensions
- NLL resummation: solve RGEs in Laplace/Fourier space; inverse transform gives the resummed distribution
- Fixed-order NLO: standard Catani-Seymour dipole subtraction for the singular real-emission contribution at C = 3/4

## Relevance to Our Work

- This paper is not directly relevant to Kochen-Specker sets or quantum contextuality; it is in the wiki as a reference on LLM-assisted research methods and "vibe physics"
- The methodology — an LLM performing detailed technical calculations under human expert supervision — is a workflow pattern relevant to how we use Claude in this project
- The explicit AI authorship credit and the arXiv submission are relevant to questions about AI contribution norms in academic research
- The absence of connection to contextuality makes this an outlier in the corpus; it was included to track the "vibe physics" phenomenon

## Open Questions

- Is the step discontinuity A(3/4) experimentally measurable with LEP or future e+e- collider data?
- How does the C-shoulder jet function relate to other event-shape jet functions (thrust, broadening)?
- Can Claude Opus 4.6 or later models reproduce or extend these calculations independently?
- What are the appropriate attribution norms when an LLM performs all calculations but a human frames and supervises the work?
