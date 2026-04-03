---
title: "The Contextual Fraction as a Measure of Contextuality"
slug: abramsky-2017-contextual-fraction
authors: ["Samson Abramsky", "Rui Soares Barbosa", "Giovanni Carù", "Simon Perdrix"]
year: 2017
journal: "Physical Review Letters"
doi: "10.1103/PhysRevLett.119.050504"
tags: [contextual-fraction, sheaf-theory, linear-programming, Bell-inequalities, MBQC, resource-theory, monotone]
status: read
---

# The Contextual Fraction as a Measure of Contextuality

## Summary

This paper introduces the **contextual fraction** CF(e) ∈ [0, 1] as a canonical quantitative measure of contextuality for empirical models (joint probability distributions over measurement outcomes). The contextual fraction is defined as the maximum weight of the noncontextual part in a decomposition of e into noncontextual and contextual components. It equals the maximum normalized violation of any Bell/noncontextuality inequality and is computable via linear programming. It is shown to be a monotone under free (noncontextual) operations and to bound the failure probability in measurement-based quantum computation (MBQC).

## Core Definitions

- **Empirical model** e: A sheaf of probability distributions over measurement contexts (a section of the "events" sheaf), in the Abramsky-Brandenburger framework.
- **Noncontextual model**: An empirical model admitting a global probability distribution (a global section). CF(e) = 0 iff e is noncontextual.
- **Contextual fraction**:
  CF(e) = 1 − max{ λ : e = λ · d + (1−λ) · c,  d noncontextual, c any valid model }
  Equivalently, CF(e) = 1 − NC(e) where NC(e) is the maximum noncontextual weight.
- **Maximally contextual**: CF(e) = 1; e has no noncontextual part (all-or-nothing / pseudotelepathy).

## Key Results

1. **LP computation**: CF(e) is computed by a linear program over the space of probability distributions on global assignments. The dual LP provides the witnessing Bell inequality.
2. **Bell inequality equivalence**: CF(e) equals the maximum normalized violation:
   CF(e) = max_{Bell inequality I} (violation of I by e) / (max quantum violation of I)
   (up to normalization convention; the paper gives the precise statement).
3. **Monotonicity**: CF is non-increasing under free operations (local operations + shared randomness in the nonlocality setting; noncontextual wirings in the contextuality setting). Hence it is a valid resource monotone.
4. **MBQC bound**: The probability that an MBQC computation fails (outputs the wrong answer) when using a resource state with empirical model e satisfies:
   P(failure) ≤ 1 − CF(e)
   Thus higher contextual fraction → lower failure probability → better computational resource.
5. **Strong contextuality** (CF = 1): Characterized as models with no global section at all — the "all-versus-nothing" case; connects to [[liu-2024-equivalences]] (FNS = FN = AVN = PT).

## Methods

- **Sheaf-theoretic framework**: Empirical models are sections of a sheaf over the measurement scenario (Čech cohomology perspective available but not required).
- **Linear programming**: The LP for NC(e) has variables indexed by global deterministic assignments; the dual witnesses the contextual fraction via a Bell functional.
- **Cohomological obstructions**: Strong contextuality detectable via sheaf cohomology (H¹ ≠ 0 implies contextuality; converse not always true).

## Connections to Existing Wiki Articles

- [[contextuality]] — contextual fraction is the central quantitative measure
- [[kochen-specker-theorem]] — KS models are maximally contextual (CF = 1)
- [[graph-contextuality]] — CSW graph-theoretic bounds (α, θ, α*) and contextual fraction are related but distinct hierarchies
- [[csw-inequality]] — Bell inequalities used in the CF equivalence
- [[budroni-2022-ks-review]] — the review covers contextual fraction in its resource theory section
- [[liu-2024-equivalences]] — strong contextuality (CF = 1) = all-versus-nothing (AVN) = pseudotelepathy
- [[algebraic-islands-main]] — the algebraic hidden-state approach provides another route to contextuality certificates

## Resource Theory Position

| Quantity | Role |
|----------|------|
| CF(e) = 0 | Free (noncontextual) |
| 0 < CF(e) < 1 | Partial resource |
| CF(e) = 1 | Maximal resource (pseudotelepathy / AVN) |

## Citation

Abramsky, S., Barbosa, R. S., Carù, G., & Perdrix, S. (2017). The contextual fraction as a measure of contextuality. *Physical Review Letters*, 119, 050504. https://doi.org/10.1103/PhysRevLett.119.050504
