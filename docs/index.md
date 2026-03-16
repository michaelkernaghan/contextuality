# The Contextuality & KS Set Atlas

Welcome to **The Contextuality & KS Set Atlas**, a research resource dedicated to Kochen–Specker (KS) sets, quantum contextuality, and their deep connections to quantum computation.

## What This Site Is For

This atlas serves as a comprehensive reference for researchers, students, and anyone interested in the foundational aspects of quantum mechanics—particularly the phenomenon of **contextuality** and its mathematical witnesses known as **Kochen–Specker sets**.

The site provides:

- **Detailed documentation** of important KS set constructions, including vector data and orthogonality structures
- **Conceptual introductions** to contextuality and its generalizations
- **Connections to quantum computation**, particularly the role of contextuality as a computational resource
- **Historical context** about the people who developed these ideas

## What Are KS Sets?

A **Kochen–Specker (KS) set** is a finite collection of rays (one-dimensional subspaces) in a Hilbert space that demonstrates the impossibility of assigning definite measurement outcomes to quantum observables in a noncontextual way. The famous **Kochen–Specker theorem** (1967) proves that in dimensions 3 and higher, no hidden-variable model can assign pre-existing values to all observables while respecting the functional relationships between compatible measurements.

KS sets provide explicit, finite proofs of this theorem. Finding small KS sets—especially in low dimensions—has been an active area of research since the original theorem.

## What Is Contextuality?

**Contextuality** is a fundamental feature of quantum mechanics: the outcome of a measurement can depend on which other compatible measurements are performed alongside it (the "context"). This goes beyond classical intuitions where measurement outcomes are assumed to be pre-determined properties of the system.

Contextuality is now understood to be a key **resource for quantum computation**. Operations that can be simulated classically (stabilizer operations) are precisely those that are noncontextual, while the "magic" needed for universal quantum computation requires contextual states and measurements.

## Quick Links

### Research (2026)

- **[The Six Algebraic Islands](research/algebraic-islands.md)** — Classification of all KS-producing number rings in dimension 3
- **[Research Papers](research/papers.md)** — One main paper and four PRL letters on the algebraic landscape of KS sets
- **[Research Overview](research/index.md)** — The algebraic islands programme and key results

### Featured KS Sets

**Classic Constructions:**

- **[Conway-Kochen 31-Vector Set (3D)](ks-sets/conway-kochen-31-3d.md)** — The minimal known KS set in 3 dimensions (strong optimality evidence)
- **[Peres 33-Vector Set (3D)](ks-sets/peres-33-3d.md)** — The classic 33-vector construction with full proof
- **[Kernaghan 20-Vector Set (4D)](ks-sets/kernaghan-20-4d.md)** — The first 20-vector KS set in 4 dimensions, a landmark construction from 1994
- **[Kernaghan–Peres 40-Vector Set (8D)](ks-sets/kernaghan-peres-40-8d.md)** — A highly efficient 40-vector construction in 8 dimensions (three qubits), connected to GHZ-type paradoxes
- **[Cabello 18-Vector Set (4D)](ks-sets/cabello-18-4d.md)** — The minimal known KS set in 4 dimensions

**New Constructions (2026):**

- **[Eisenstein 33-Vector Set (3D)](ks-sets/eisenstein-33-3d.md)** — Rigid 33-vector set over $\mathbb{Z}[\omega]$, smallest known BPQS (45)
- **[Heegner-7 43-Vector Set (3D)](ks-sets/heegner7-43-3d.md)** — First KS set from a Heegner number field, highest contextual advantage ($\theta/\alpha = 1.118$)
- **[Golden Ratio 52-Vector Set (3D)](ks-sets/golden-52-3d.md)** — Discovered via cross-product completion, invisible to raw alphabet search
- **[$\mathbb{Z}[\sqrt{-2}]$ 33-Vector Set (3D)](ks-sets/zsqrt2-neg-33-3d.md)** — Complex realization of the Peres graph, proving the flex belongs to the graph

### Key Topics

- **[Contextuality Basics](topics/contextuality-basics.md)** — Foundations of the KS theorem and noncontextual hidden-variable models
- **[Generalized Contextuality](topics/generalized-contextuality-spekkens.md)** — Spekkens' operational framework extending contextuality beyond projective measurements
- **[Contextuality & Quantum Computation](topics/contextuality-and-quantum-computation.md)** — Why contextuality is necessary for quantum computational advantage

### People & History

- [Michael Kernaghan](people/michael-kernaghan.md) | [Asher Peres](people/asher-peres.md) | [Adán Cabello](people/adan-cabello.md) | [Rob Spekkens](people/rob-spekkens.md)

### Institutional Affiliation

This atlas is a project of **[Pacific Quantum Systems](https://pacific-quantum-systems.com/)**, a research initiative based in Vancouver, BC, investigating the mathematical foundations of quantum mechanics and their applications to quantum computation, post-quantum cryptography, and quantum communications.

### Reference

- **[Bibliography](bibliography.md)** — Key papers and resources on KS sets and contextuality
- **[Recent Papers](recent-papers.md)** — Curated selection of recent papers (2022-2026)
