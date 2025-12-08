# History of Contextuality

## Introduction

The concept now called **contextuality**—the dependence of measurement outcomes on the broader experimental context—did not emerge fully formed. It developed gradually through nearly a century of quantum physics, shaped by foundational debates, mathematical discoveries, and shifting interpretations of what quantum mechanics tells us about reality.

This section traces the historical arc from the earliest days of quantum theory to the modern resource-theoretic understanding of contextuality in quantum computation.

---

## The Central Question

Throughout this history, one question recurs in various guises:

!!! question "The Core Problem"
    Can the outcomes of quantum measurements be understood as revealing pre-existing properties of the system, independent of how and alongside what else we choose to measure?

The answer, increasingly refined over decades, is **no**. This negative answer—formalized as contextuality—has profound implications for our understanding of physical reality and, surprisingly, for the power of quantum computers.

---

## Historical Timeline

### Pre-Contextuality Era (1900–1935)

The foundations were laid before anyone used the word "contextuality":

| Year | Development | Significance |
|------|-------------|--------------|
| 1900 | Planck's quantum hypothesis | Discreteness enters physics |
| 1913 | Bohr's atomic model | Stationary states, quantum jumps |
| 1925–26 | Matrix and wave mechanics | Heisenberg, Schrödinger create QM |
| 1927 | Uncertainty principle | Measurement disturbance formalized |
| 1927 | Solvay Conference | Copenhagen interpretation crystallizes |
| 1932 | von Neumann's impossibility proof | First no-hidden-variables argument |
| 1935 | EPR paper | "Elements of reality" and completeness challenged |

**Key insight**: Bohr's complementarity already contained proto-contextual ideas—the experimental arrangement determines what can be meaningfully said about the system.

→ [Read more: Early Quantum Theory (1900–1930)](early-quantum.md)

### The Hidden-Variables Debate (1935–1966)

| Year | Development | Significance |
|------|-------------|--------------|
| 1935 | EPR paradox | Locality vs. completeness |
| 1951 | Bohm's textbook | Spin-½ version of EPR |
| 1952 | Bohm's pilot-wave theory | Hidden variables possible after all |
| 1957 | Bohm–Aharonov analysis | Contextual elements in measurement |
| 1964 | Bell's theorem | Nonlocality proven |
| 1966 | Bell's critique of von Neumann | Opens door to contextual HV theories |

**Key insight**: Bohm showed that hidden variables are possible, but Bell showed they must be nonlocal. The question of contextuality was implicit in these debates.

→ [Read more: EPR, Bohm, and Measurement (1930–1960)](epr-bohm.md)

### The Kochen–Specker Theorem (1967)

| Year | Development | Significance |
|------|-------------|--------------|
| 1967 | Kochen–Specker theorem | Noncontextual value assignments impossible |

This was the watershed moment: Kochen and Specker proved that in Hilbert spaces of dimension ≥ 3, you cannot consistently assign definite values to all observables in a way that is independent of measurement context.

**Key insight**: Contextuality was now a theorem, not just a philosophical stance.

→ [Read more: The Kochen–Specker Theorem (1967)](kochen-specker.md)

### Contextuality Across Interpretations (1970–2000)

Different interpretations of quantum mechanics respond to contextuality in different ways:

| Interpretation | How it handles contextuality |
|----------------|------------------------------|
| Copenhagen | Measurement context is fundamental |
| Bohmian mechanics | Contextual but deterministic |
| Many-Worlds | Context determines branching basis |
| GRW (objective collapse) | Context influences collapse outcomes |
| QBism | Radical perspectival contextuality |

**Key insight**: Contextuality is not interpretation-dependent—it's a feature any interpretation must accommodate.

→ [Read more: Contextuality in Interpretations of QM](contextuality-in-interpretations.md)

### Modern Era (2000–present)

| Year | Development | Significance |
|------|-------------|--------------|
| 2005 | Spekkens' generalized contextuality | Operational framework |
| 2008 | Negativity-contextuality equivalence | Wigner function connection |
| 2011 | Abramsky–Brandenburger sheaf theory | Mathematical unification |
| 2014 | Howard et al. on magic states | Contextuality as computational resource |
| 2013+ | Raussendorf on MBQC | Contextuality powers measurement-based QC |

**Key insight**: Contextuality has transformed from a foundational curiosity into a practical resource for quantum technology.

→ [Read more: Modern Contextuality & Quantum Information](contextuality-modern.md)

---

## Themes Across the History

Several themes recur throughout this history:

### 1. From Philosophy to Mathematics to Technology

Contextuality began as a philosophical puzzle about the nature of measurement, became a mathematical theorem about value assignments, and is now understood as a computational resource.

### 2. The Persistence of the Question

Every generation of physicists has grappled with whether quantum systems have definite properties independent of measurement. The answer keeps being "no," but in increasingly precise and useful ways.

### 3. Hidden Variables and Their Constraints

The hidden-variables program did not fail—it succeeded in showing exactly what hidden variables must be like: nonlocal and contextual. This is valuable knowledge.

### 4. Unification

Modern contextuality theory unifies:
- Kochen–Specker contextuality (projective measurements)
- Bell nonlocality (spatially separated measurements)
- Spekkens' generalized contextuality (preparations and transformations)

### 5. Resource Theory

The most recent development is understanding contextuality as a **resource**—something that can be quantified, manipulated, and consumed for computational advantage.

---

## How to Use This Section

This history section complements the other parts of the atlas:

- **For conceptual foundations**: Start with [Contextuality Basics](../topics/contextuality-basics.md), then read the history for deeper context
- **For specific KS sets**: The [KS sets pages](../ks-sets/kernaghan-20-4d.md) give technical details; the history explains why they matter
- **For computation**: [Contextuality & Quantum Computation](../topics/contextuality-and-quantum-computation.md) explains the modern applications; the history shows how we got there

---

## Chapter Overview

1. **[Early Quantum Theory (1900–1930)](early-quantum.md)**
   Proto-contextual ideas in Bohr, Heisenberg, and von Neumann

2. **[EPR, Bohm, and Measurement (1930–1960)](epr-bohm.md)**
   The hidden-variables debate and the road to Bell

3. **[The Kochen–Specker Theorem (1967)](kochen-specker.md)**
   Contextuality becomes a theorem

4. **[Contextuality in Interpretations of QM](contextuality-in-interpretations.md)**
   How different interpretations handle contextuality

5. **[Modern Contextuality & Quantum Information](contextuality-modern.md)**
   From foundations to computational resource

---

!!! note "Why This History Matters Today"
    Understanding the history of contextuality is not merely academic. The conceptual struggles of Bohr, Einstein, Bohm, and Bell directly inform how we think about quantum computers, quantum cryptography, and the foundations of physics today. The KS sets documented in this atlas are direct descendants of questions asked nearly a century ago.

---

## Glossary

**Complementarity**
: Bohr's principle that quantum systems exhibit mutually exclusive properties depending on experimental arrangement.

**Hidden variables**
: Hypothetical additional parameters beyond the quantum state that would determine measurement outcomes.

**Noncontextuality**
: The assumption that measurement outcomes depend only on the observable measured, not on what else is measured alongside it.

**Contextuality**
: The failure of noncontextuality; the dependence of outcomes on measurement context.

**KS set**
: A finite set of rays demonstrating that noncontextual value assignments are impossible.
