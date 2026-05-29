---
title: "Algebraic Substrate as a Design Rule for Contextuality Engineering"
slug: algebraic-substrate-design-guide
date: 2026-04-18
type: companion-note
audience: "Pavičić program (MMP-hypergraph engineering, BPQS, weak measurements, Hadamard constructions)"
status: draft
---

# Algebraic Substrate as a Design Rule for Contextuality Engineering

*Companion note to the algebraic-islands program, aimed at readers working on empirical applications of Kochen-Specker and contextual sets.*

## Pitch

Pavičić's program asks *where* contextual sets can actually be used — BPQS, weak-measurement protocols, Hadamard-matrix coordinatizations, pseudo-telepathy games. Our algebraic-landscape work contributes a **substrate-level design guide**, not a new family of applications. Not all KS realizations are operationally equivalent, and the underlying coordinate algebra predicts which constructions are cheaper, simpler, or stronger for concrete tasks.

The MMP-hypergraph machinery is powerful combinatorially but substrate-blind: it generates KS sets from master hypergraphs without regard to the coordinate ring in which they live. We find that the ring choice is not cosmetic. It controls BPQS cost, CSW contextual advantage, completion behaviour, and the density of realizable contextual sets.

## Three contributions

### 1. An experimental selection map, not just more KS sets

The six algebraic islands we identify in 3D — integer (CK-31), Peres, Eisenstein, $\Z[\sqrt{-2}]$, Heegner-7, and Golden — are not interchangeable. Each realizes a different trade-off across four axes relevant to protocol design:

- **Ray count** — qutrit Hilbert-space footprint, state-preparation cost
- **Context count** — input-setting cost in a Bell scenario
- **BPQS cost** $|S_A| \times |S_B|$ — the total number of input pairs in the induced bipartite perfect quantum strategy
- **CSW contextual advantage** $\vartheta/\alpha$ — the size of the quantum-over-classical gap

The main deliverable is a cost sheet:

| Island | Rays | Bases | BPQS cost | $\vartheta/\alpha$ | Notes |
|---|---|---|---|---|---|
| Eisenstein | 33 | 14 | $5 \times 9 = 45$ (exact) | 1.004 | Simplest Bell scenario |
| Peres | 33 | 16 | $7 \times 9 = 63$ (exact) | 1.000 | Baseline |
| $\Z[\sqrt{-2}]$ | 33 | 16 | $7 \times 9 = 63$ (exact) | — | New; matches Peres cost |
| CK-31 | 31 | 17 | $\le 8 \times 9 = 72$ (best found) | **1.065** | Tightest advantage |
| Heegner-7 | 43 | 23 | $\le 9 \times 12 = 108$ (best found) | — | Appears especially promising on CSW-type advantage measures |
| Golden | 52 | 25 | $\le 12 \times 13 = 156$ (best found) | — | Requires $1/\varphi$ via completion |

For an experimenter committing to a 3D BPQS implementation, this is a direct lookup. Eisenstein minimizes Bell-scenario complexity; CK-31 minimizes Hilbert-space dimension and maximizes the CSW gap; Heegner-7 and Golden are new options unavailable to substrate-blind enumeration.

### 2. Algebraic substrate matters operationally

The real message is that the coordinate ring changes what Bell scenarios, completions, and contextual advantages are available. Two concrete manifestations:

**Ray-economy vs. context-economy trade-off.** CK-31 gives the smallest ray count (31) but the largest context count among the 33-class islands (17). Eisenstein sacrifices two rays (33 instead of 31) to cut bases from 17 to 14, yielding a $5 \times 9$ BPQS rather than $\le 8 \times 9$. No single island dominates on all axes. The right choice depends on whether the bottleneck is state preparation or input-setting control — a distinction invisible to a classification that treats all KS sets as combinatorially equivalent.

**The completion principle.** A raw alphabet need not be KS-uncolorable even when its cross-product completion is. The golden-ratio case is clean: $\{0, \pm 1, \pm\varphi\}$ is colorable, but completion generates $1/\varphi$ — whose squared modulus is $(3-\sqrt{5})/2 < 1$ — and the completed pool supports effective cancellations that render it KS-uncolorable. The algebraically relevant object is the completed coordinate algebra, not the generating alphabet. This is consistent with the methodological point Pavičić makes in his own work about restoring geometrically forced completion vectors before analyzing a stripped configuration.

### 3. A search heuristic for physically realizable constructions

A norm-2-type cancellation heuristic replaces blind enumeration. The empirical pattern across the six islands is that KS-uncolorability rides on one of two cancellation mechanisms:

- **Modulus-2 cancellation** — an integer relation of the form $|x|^2 + |y|^2 - |z|^2 = 0$ with small coordinates; available in the integer, Peres, $\Z[\sqrt{-2}]$, and Heegner-7 alphabets
- **Phase cancellation** — a cube-root-of-unity identity $1 + \omega + \omega^2 = 0$; available in the Eisenstein alphabet

The Golden island reduces to the first mechanism only after completion introduces $1/\varphi$. No coordinate generator $x$ with $|x|^2 \ge 3$ (and not a root of unity) has produced a KS set in our broad survey.

For the master-set / downward-generation program, this is actionable. Rather than enumerating coordinate choices by convention (e.g. $\{0, \pm 1, \omega^k\}$), one can select coordinate rings by their cancellation inventory:

- Imaginary quadratic fields $\Q(\sqrt{-d})$ whose ring of integers has an element of squared modulus 2 — Heegner numbers $d = 2, 7$
- Cyclotomic fields $\Q(\zeta_n)$ with $(\Z/n\Z)^* \twoheadrightarrow \Z/6\Z$, i.e. $6 \mid n$
- Real fields whose cross-product completion introduces effective modulus-2 relations (as happens for $\Q(\varphi)$)

This narrows the search space for higher-dimensional extensions of the automated generation pipeline, especially 6D where the existing ω-coordinatization is one choice among several that the cancellation rule predicts should work.

## What to keep in mind

### A caveat on typicality

The empirical claim that contextuality is generic above a threshold MMP-hypergraph size is consistent with our results at the combinatorial level. But realizable contextual sets — those that admit a coordinatization over some number field — concentrate on a sparse algebraic variety. Across a broad sweep of coordinate rings we find only six islands. For any application that tacitly assumes a random large contextual hypergraph is physically realizable (density arguments, expected performance of random protocols), the distinction matters: the density of abstract contextual hypergraphs is not the density of physically realizable ones.

### What this note does not claim

- No universal norm-2 theorem. The claim is a cancellation heuristic consistent with all examples we know, not a proof that modulus-2 or phase cancellation is necessary.
- No claim that our six islands exhaust the realizable landscape — they are what a broad but not exhaustive survey has surfaced.
- No engineering critique of Pavičić's criticality framework, which operates on a different axis (sub-hypergraph inclusion) from our substrate classification.

## Short version

If you are trying to engineer a concrete contextuality-based protocol in 3D — a BPQS, a pseudo-telepathy game, a randomness-certification scheme — the algebraic substrate is a design parameter, not an aesthetic choice. Pick Eisenstein when you want the simplest Bell scenario; pick CK-31 when you want the maximum contextual advantage and smallest Hilbert space; pick Heegner-7 or Golden when you need options the substrate-blind enumeration cannot see. For higher dimensions, let the cancellation inventory of the candidate coordinate ring guide the search before committing compute to exhaustive master-set generation.
