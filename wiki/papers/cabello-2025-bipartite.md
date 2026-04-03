---
title: "Bipartite Perfect Quantum Strategies and Kochen-Specker Sets"
slug: cabello-2025-bipartite
authors: ["Adán Cabello"]
year: 2025
journal: "Physical Review Letters"
doi: "10.1103/PhysRevLett.134.100201"
tags: [bipartite-perfect-quantum-strategy, pseudotelepathy, kochen-specker, magic-square, qutrit, BPQS, nonlocality]
status: read
---

# Bipartite Perfect Quantum Strategies and Kochen-Specker Sets

## Summary

This paper establishes a fundamental connection between **bipartite perfect quantum strategies** (BPQSs) — quantum correlations that win a two-player nonlocal game with probability 1, impossible classically — and **KS sets**. The main theorem proves that every BPQS defines a KS set. As a corollary, BPQSs are impossible when both players have 3 inputs and 3 outputs (|X|=|Y|=|A|=|B|=3), because no KS set exists in dimension 3 with the required structure. The paper conjectures that the magic-square game (3×3 inputs) is the simplest BPQS and that the simplest qutrit-qutrit BPQS uses 9×7 inputs.

## Core Contributions

- **Theorem 1**: Every BPQS defines a KS set. Specifically, the local measurement operators of each party in a BPQS form a KS set (or contain one as a subset).
- **Impossibility for 3×3×3×3**: Since no KS set exists in the relevant 3D structure for |X|=|Y|=|A|=|B|=3, BPQSs are impossible in this scenario. This strengthens earlier impossibility results for small nonlocal games.
- **Conjecture 1**: The magic-square game (|X|=|Y|=9, |A|=|B|=4, entangled qubits) is the simplest BPQS in terms of number of inputs.
- **Conjecture 2**: The simplest qutrit-qutrit BPQS uses 9×7 inputs. (Note: this conjecture is refuted by [[cabello-2025-simplest-ks]], which constructs a 5×9 strategy.)

## Key Definitions

- **Bipartite perfect quantum strategy (BPQS)**: A quantum strategy (shared state ψ, local measurements {Aˣ_a}, {Bʸ_b}) for a bipartite nonlocal game that achieves winning probability 1. Classical strategies cannot achieve this.
- **Pseudotelepathy**: Equivalent term for BPQS in the literature; see [[liu-2024-equivalences]] for the FNS=FN=AVN=PT equivalence chain.
- **Magic square**: The Mermin-Peres magic square provides the canonical example: 3×3 grid of observables, each row/column context commuting and squaring to ±I; quantum strategy assigns consistent values impossible classically.

## KS Sets Arising from BPQSs

The proof proceeds by showing that in any BPQS:
1. Each party's measurement operators for different inputs must pairwise commute within contexts.
2. The operator assignments form a partial ring / partial algebra.
3. The no-perfect-classical-strategy condition implies no global value assignment exists — the KS property.

This links directly to [[cortez-2022-minimal-ring]]'s algebraic hidden-state framework.

## Connections to Existing Wiki Articles

- [[kochen-specker-theorem]] — KS sets are the output of the main theorem
- [[ks-set]] — BPQSs generate KS sets as a byproduct
- [[contextuality]] — BPQSs are instances of maximal (strong) contextuality
- [[abramsky-2017-contextual-fraction]] — BPQSs have CF = 1 (pseudotelepathy = AVN)
- [[liu-2024-equivalences]] — FNS = FN = AVN = PT equivalence, which BPQSs instantiate
- [[cabello-2025-simplest-ks]] — refutes Conjecture 2; finds a 5×9 qutrit-qutrit BPQS
- [[cortez-2022-minimal-ring]] — algebraic hidden states and partial rings underlie the proof structure
- [[peres-33-3d]] — the impossibility in 3×3×3×3 connects to KS nonexistence in d=3 below a threshold

## Significance

The BPQS→KS-set direction shows that nonlocality witnesses (game-based) and contextuality witnesses (coloring-based) are not independent — every pseudotelepathy phenomenon leaves a KS fingerprint. This unification has implications for the resource theory of both nonlocality and contextuality.

## Citation

Cabello, A. (2025). Bipartite perfect quantum strategies and Kochen-Specker sets. *Physical Review Letters*, 134, 100201. https://doi.org/10.1103/PhysRevLett.134.100201
