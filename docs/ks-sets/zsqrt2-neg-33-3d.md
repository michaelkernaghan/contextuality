# Z[sqrt(-2)] 33-Vector Kochen-Specker Set (3D)

## Basic Metadata

| Property | Value |
|----------|-------|
| **Name** | $\mathbb{Z}[\sqrt{-2}]$ 33-Vector KS Set |
| **Dimension** | 3 (spin-1 Hilbert space) |
| **Number of Rays** | 33 |
| **Ring** | $\mathbb{Z}[\sqrt{-2}]$ |
| **Type** | State-independent KS set |
| **Author** | Michael Kernaghan |
| **Year** | 2026 |
| **Cancellation Identity** | $|\sqrt{-2}|^2 = 2$ |

---

## Overview

The **$\mathbb{Z}[\sqrt{-2}]$ 33-vector KS set** is constructed over the ring of Gaussian-like integers $\mathbb{Z}[\sqrt{-2}]$. The cancellation identity $|\sqrt{-2}|^2 = 2$ provides the same norm-2 mechanism as the Peres set's $(\sqrt{2})^2 = 2$, but using a complex quadratic extension rather than a real one.

This construction is significant as a demonstration that the **flex belongs to the graph, not the algebra**:

- **Graph-isomorphic to Peres**: The orthogonality graph of the $\mathbb{Z}[\sqrt{-2}]$ set is isomorphic to the Peres-33 graph
- **Same flex**: Despite using complex coordinates, the set has exactly the same 1-dimensional flex as Peres — confirming that the deformation mode is a property of the graph structure
- **Same configuration, different parameter value**: the two sets are not merely graph-isomorphic. They are the same 33-ray configuration at two points of one continuous family (see Rigidity below), so this is a new *algebraic route* to the Peres configuration rather than a geometrically distinct realization of it

Key features:

- **49-ray pool**: The $\mathbb{Z}[\sqrt{-2}]$ alphabet generates 49 rays (same count as the integer and Peres pools)
- **Norm-2 cancellation**: $|\sqrt{-2}|^2 = 2$ satisfies the controlling invariant
- **BPQS**: $7 \times 9 = 63$, identical to Peres (consistent with graph isomorphism)

---

## Structure

The 33 rays live in $\mathbb{C}^3$, using coordinates from $\{0, \pm 1, \pm \sqrt{-2}\}$. Orthogonality between vectors relies on the identity $|\sqrt{-2}|^2 = 1 \cdot 1 + (\sqrt{2})^2 = 2$ (more precisely, $\sqrt{-2} \cdot \overline{\sqrt{-2}} = 2$).

### Orthogonality Structure

| Property | Value |
|----------|-------|
| **Orthogonal pairs** | 72 |
| **Ray pool size** | 49 |
| **Minimum KS subset** | 33 vectors |

---

## Rigidity (Flex)

The $\mathbb{Z}[\sqrt{-2}]$ set is **flexible** with one **finite** deformation dimension — the same status as the Peres set:

| Property | $\mathbb{Z}[\sqrt{-2}]$-33 | Peres-33 |
|----------|---------------------------|----------|
| Orthogonal pairs | 72 | 72 |
| Null space dim | 42 | 42 |
| Symmetry dim | 41 | 41 |
| Deformation modes | **1 (flex)** | **1 (flex)** |
| Finitely rigid? | No — flex is finite | No — flex is finite |

The flex is finite: it integrates to the continuous one-parameter family of Gould and Aravind (*Found. Phys.* **40**, 1096 (2010)), and the two sets sit at antipodal parameter values on that circle. This confirms that **the flex belongs to the graph**: any embedding of this particular 33-vertex, 72-edge orthogonality graph — whether in $\mathbb{Z}[\sqrt{2}]$, $\mathbb{Z}[\sqrt{-2}]$, or any other ring — will exhibit the same 1-dimensional flex. It also shows the two islands are one object seen twice.

> **Corrected 2026-07-27.** This section previously stated the flex was blocked at second order with cokernel component 0.075, making both sets finitely rigid. That was an artifact of a constraint-ordering bug in `ks_rigidity_finite.py`; the true cokernel component is zero. Reported by Manuel Flores Gordillo, doi:10.5281/zenodo.21488474.

---

## BPQS (Bipartite Perfect Quantum Strategy)

$$|S_A| \times |S_B| = 7 \times 9 = 63$$

Exact, verified. Identical to the Peres-33 BPQS, as expected from graph isomorphism.

---

## Relation to Other KS Sets

| Construction | Dimension | Vectors | Pairs | Rigid? | Ring | Graph type |
|-------------|-----------|---------|-------|--------|------|------------|
| Peres | 3 | 33 | 72 | Flex | $\mathbb{Z}[\sqrt{2}]$ | Peres graph |
| **$\mathbb{Z}[\sqrt{-2}]$** | **3** | **33** | **72** | **Flex** | $\mathbb{Z}[\sqrt{-2}]$ | **Peres graph** |
| Eisenstein | 3 | 33 | 78 | Rigid | $\mathbb{Z}[\omega]$ | Eisenstein graph |

The Peres and $\mathbb{Z}[\sqrt{-2}]$ sets share the same graph (and therefore the same flex, BPQS, and coloring properties) but are algebraically distinct: one uses real coordinates, the other complex. Together with Gaussian integers $\mathbb{Z}[i]$ (which also produce the Peres graph), these three rings demonstrate that the norm-2 cancellation $x \cdot \bar{x} = 2$ can be realized in multiple algebraic settings while preserving graph structure.

---

## References

- M. Kernaghan, "The Algebraic Landscape of Kochen-Specker Sets in Dimension Three" (2026)

---

## Cross-Links

- [Peres 33-Vector KS Set (3D)](peres-33-3d.md) — Graph-isomorphic construction over $\mathbb{Z}[\sqrt{2}]$
- [Eisenstein 33-Vector KS Set (3D)](eisenstein-33-3d.md) — Different 33-vector set with rigid graph
- [The Six Algebraic Islands](../research/algebraic-islands.md) — Classification of all known 3D KS constructions
