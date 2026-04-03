---
source: references/corpus/LiBrightGanesh2024-SAT-KS-2306.13319.pdf
date_ingested: 2026-04-03
type: paper
---

# SAT-Based Lower Bounds for Kochen-Specker Sets in Three Dimensions (Li, Bright & Ganesh, 2024)

## Summary

This paper gives the first fully verifiable, computer-generated proof that any Kochen-Specker (KS) system in three-dimensional real or complex Hilbert space must contain at least 24 vectors. The result closes the gap between the known lower bound of 22 (Arends, Ouaknine, Wampler 2011) and the smallest known KS set of 31 elements by advancing the bound to 24.

The proof uses the MathCheck pipeline: a Cube-and-Conquer (CnC) satisfiability solver (combining MapleSAT for cubing and CaDiCaL for solving) paired with a computer algebra system (CAS) for verifying algebraic witnesses. The pipeline generates a DRAT proof certificate of 40.3 TiB that can be independently verified by proof checkers. The paper also establishes that the bound applies to both real and complex KS systems.

The approach is independent of the SMS (Schur multiplier/symmetry) method of Kirchweger, Peitl, and Szeider, providing a cross-validation. The proof was parallelized across a computing cluster using orderly isomorph-free generation to eliminate symmetrically equivalent cases.

## Key Claims

- Any KS system (real or complex) in C^3 (or R^3) must have at least 24 vectors
- The proof is machine-verifiable: a 40.3 TiB DRAT proof certificate was generated and checked
- The bound applies to both real and complex Hilbert spaces in 3D
- The result is independent of the Kirchweger-Peitl-Szeider SMS approach, providing cross-validation
- Cube-and-Conquer with CaDiCaL/MapleSAT is the core SAT technology; CAS handles algebraic side conditions
- Order 23 was the critical case: showing no KS system on 23 vectors exists required the full 40.3 TiB certificate

## Methods

- MathCheck pipeline: SAT solving + CAS verification in a tight loop
- Cube-and-Conquer (CnC): partition the search space into "cubes" (subproblems) using MapleSAT's lookahead, solve each cube with CaDiCaL
- Orderly isomorph-free generation: enumerate KS candidate configurations up to isomorphism to avoid redundant search
- DRAT proof certificates: standard SAT proof format, checkable by DRAT-trim and related tools
- CAS (computer algebra system) used to verify that alleged orthogonality witnesses satisfy the algebraic conditions (integer or algebraic number arithmetic, no floating point)

## Relevance to Our Work

- The >=24 lower bound is the strongest current constraint on the size of any C^3 KS set, directly relevant to the conjecture in [[trandafir-cabello-2025-rigid-ks]] that 31 is the minimum
- Our algebraic islands paper ([[algebraic-islands-main]]) provides an OCUS-certified proof that no KS-uncolorable subset of <=30 rays exists within the specific 49-ray integer pool; this paper's bound is dimension-wide and alphabet-independent
- The SAT+CAS methodology (MathCheck) is closely related to our use of Glucose4 for KS-uncolorability testing; comparing pipeline designs may reveal efficiency improvements
- The 40.3 TiB certificate size is a benchmark for the computational difficulty of exhaustive search in this domain
- The proof that the bound holds for complex as well as real KS sets confirms that working over C^3 (as our paper does) does not open an escape route to smaller sets

## Open Questions

- Can the bound be pushed from 24 to a larger number, closer to 31?
- Is a human-readable proof of the >=24 bound achievable, or is this inherently a computer-search result?
- Does the MathCheck approach scale to d=4 (minimum known KS set: 18 vectors by Cabello-Estebaranz-Garcia-Alcaine)?
- Could the DRAT certificate be compressed or summarized without losing verifiability?
