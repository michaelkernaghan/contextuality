# Design Spec: Galois-Theoretic KS Classification Paper

**Date:** 2026-04-05
**Type:** PRL letter (4 pages)
**Title:** "The arithmetic of contextuality: a Galois-theoretic classification of Kochen-Specker sets in dimension three"
**Builds on:** algebraic_islands.tex (main paper, Section 5.3 Galois subsection)

## Main Theorem

For a quadratic extension K/Q with ring-of-integers generator x, the two-element alphabet {0, +/-1, +/-x} produces KS-uncolorable ray sets in C^3 if and only if one of:

- (i) |N_{K/Q}(x)| = 2 (modulus-2 mechanism), or
- (ii) N_{K/Q}(x) = 1 and Tr_{K/Q}(x) = -1 (phase mechanism)

## Proof Strategy (five-step chain)

1. In C^3, orthogonality <v|w> = 0 is a <=3-term vanishing sum from the product set
2. For {0, +/-1, +/-x}, the product set has five distinct magnitudes: {0, 1, x, x-bar, |x|^2}
3. Enumerate all primitive three-term vanishing sums over this product set (finite case analysis)
4. Every solution reduces to |N_{K/Q}(x)| = 2 or (N_{K/Q}(x) = 1, Tr_{K/Q}(x) = -1)
5. Without such a vanishing sum, the alphabet produces <=10 triads, which is too sparse for KS-uncolorability (the minimum known requires 16+ triads)

Step 3 is the core: it reuses and extends Table 5 / Observation 1 from the main paper, now framed as a Galois-invariant classification. Step 5 needs a sharp bound on triad count when no low-complexity cancellation exists (the main paper's data shows <=10 for all tested non-KS alphabets; we need to prove this or state it as a certified computational result).

## Structure

### 1. Introduction (~0.5 page)
- KS theorem statement (cite Kochen-Specker 1967)
- Algebraic islands program: six discrete islands classified by coordinate alphabets (cite main paper)
- Gap: the classification is computational; we provide the algebraic proof
- Announce: the cancellation mechanisms are Galois norm/trace conditions
- State main theorem informally

### 2. Setup (~0.5 page)
- Quadratic extensions K = Q(sqrt(d)), ring of integers O_K, Galois group Z/2Z
- Galois norm N_{K/Q}(x) = x * sigma(x), Galois trace Tr_{K/Q}(x) = x + sigma(x)
- Two-element coordinate alphabet A = {0, +/-1, +/-x} where x is the ring-of-integers generator
- Product set A-bar * A = {0, +/-1, +/-x, +/-x-bar, +/-|x|^2}
- Orthogonality in C^3: <v|w> = sum_{k=1}^3 v-bar_k w_k = 0 is a <=3-term vanishing sum from A-bar * A

### 3. Proof of Main Theorem (~1.5 pages)

**Sufficiency (brief):** For |N|=2: cite main paper's KS constructions (CK-31, Peres-33, Z[sqrt(-2)]-33, Heegner-7-43). For (N=1, Tr=-1): cite Eisenstein-33. All are verified KS-uncolorable by SAT.

**Necessity (the new content):**

Lemma 1 (Vanishing sum enumeration): Let A = {0, +/-1, +/-x} with x not in {0, +/-1}. Every primitive three-term vanishing sum t_1 + t_2 + t_3 = 0 with t_k in A-bar * A falls into one of six patterns:

| Pattern | Equation on x | Solution | N_{K/Q}(x) | Tr_{K/Q}(x) |
|---------|--------------|----------|------------|-------------|
| 1 + 1 - x = 0 | x = 2 | x = 2 | 4 | 4 |
| 1 + 1 - |x|^2 = 0 | |x|^2 = 2 | sqrt(2), sqrt(-2), alpha_7 | +/-2 | varies |
| 1 + x + x-bar = 0 | x + x-bar = -1; |x|^2 = 1 | omega | 1 | -1 |
| 1 + x - |x|^2 = 0 | |x|^2 = 1 + x | phi (real) | -1 | 1 |
| |x|^2 + |x|^2 - 1 = 0 | |x|^2 = 1/2 | 1/sqrt(2) | equiv. Peres | |
| x + x - |x|^2 = 0 | |x|^2 = 2x | x = 2 (real) | equiv. Integer | |

Every row with KS-uncolorable output has |N| = 2 or (N = 1, Tr = -1). Row 4 (golden ratio) has |N| = 1, Tr = 1 but only produces KS-uncolorability AFTER cross-product completion, which is outside our theorem scope.

Proof technique: The product set has 5 non-zero magnitudes. Three-term sums t_1 + t_2 + t_3 = 0 are enumerated by choosing three elements (with sign and repetition) from {1, x, x-bar, |x|^2}. There are finitely many essentially distinct patterns (up to sign, conjugation, and reordering). For each, solve for x and compute N, Tr.

Lemma 2 (Triad sparsity — ANALYTICAL PROOF): If the alphabet A = {0, +/-1, +/-x} admits no primitive cancellation identity from Lemma 1, then S(A) is KS-colorable.

Proof structure (five steps):

Step 1 (Definition): In C^3, orthogonality <v|w> = 0 is a <=3-term vanishing sum from the product set A-bar * A. This is immediate from the inner product having three terms.

Step 2 (Lemma 1): All primitive three-term vanishing sums require |N|=2 or (N=1, Tr=-1). Finite case analysis over the five-element product set {1, x, x-bar, |x|^2} with signs. Already proved above.

Step 3 (No all-nonzero orthogonality): Without these cancellations, no two all-nonzero rays in S(A) are orthogonal. Proof: if v, w both have entries in {+/-1, +/-x}, all three terms v-bar_k w_k are nonzero, so orthogonality requires a three-term vanishing sum — excluded by assumption. QED.

Step 4 (Cross product falls outside S(A)): An all-nonzero ray v and a one-zero ray w CAN be orthogonal via two-term cancellation (t_1 = -t_2, always available). But the third ray u = v x w completing the triad has coordinates involving:
- The third component u_3 = v_1 w_2 - v_2 w_1, which evaluates to expressions like:
  - -2 (from v=(1,1,c), w=(1,-1,0)): need x=2 (integer cancellation)
  - -(1+x^2) (from v=(1,x,c), w=(x,-1,0)): no real solution to 1+x^2 in {+/-1, +/-x}; for complex x, 1+|x|^2 > 1, never in A
  - -2x (from v=(x,x,c), w=(1,-1,0)): need x=0 (excluded)
- The first/second components can involve x^2, which is in A only if x^2 = +/-1 (excluded) or x^2 = +/-x (giving x = +/-1, excluded)

Exhaustive case analysis over v_1, v_2, v_3 in {+/-1, +/-x} and w_1, w_2 in {+/-1, +/-x} (w_3=0 WLOG by symmetry, with the orthogonality constraint v_1-bar w_1 + v_2-bar w_2 = 0) confirms: every cross product u = v x w has at least one coordinate outside A unless a Lemma 1 cancellation identity holds. The cases reduce to checking that 2, x^2+1, 2x, 1+|x|^2, x^2-1 are NOT in {0, +/-1, +/-x} when no cancellation exists. Each of these equalities (e.g., 2=x, x^2+1=x, 2x=1) either has no solution or implies a cancellation identity.

Therefore: no triad in raw S(A) contains an all-nonzero ray. QED.

Step 5 (Structural decomposition → explicit coloring):
- Only triads of form {one-zero ray, one-zero ray, axis ray} and the axis triad exist in S(A).
- One-zero rays per coordinate plane: <=6 (for generic real x); orthogonal pairs per plane: <=3.
- Total triads: <=10 (3 pairs x 3 planes + 1 axis).
- The coloring decomposes: choosing which axis ray gets value 1 fixes one plane (all one-zero rays there get 0) and leaves two independent planes, each with 3 independent pair-matching constraints.
- Explicit coloring: pick v(e_3)=1; in the xz-plane and yz-plane, assign 1 to one ray per orthogonal pair. Valid colorings: 3 x 2^3 x 2^3 = 192.
- Therefore S(A) is KS-colorable. QED.

**Edge cases verified:**
- Gaussian integers (x=i, |x|^2=1, Tr=0): 4 one-zero rays per plane (unit x creates projective identifications), <=2 pairs per plane, <=7 triads. Still decomposes and is colorable. Confirmed by main paper (Table 3: Z[i] colorable).
- Purely imaginary x with Tr=0 but |x|^2 != 2: 3 pairs per plane, 10 triads. Colorable.
- |x|^2 = 1 with Tr != -1: only possible for d=1 (Gaussian), already covered.

Theorem (Main): Combine Lemmas 1 and 2. For a two-element alphabet {0, +/-1, +/-x} over a quadratic field:
- If |N_{K/Q}(x)| = 2 or (N=1, Tr=-1): a cancellation identity exists, the ray set has >=16 triads, and known KS constructions are uncolorable (sufficiency, cite main paper).
- If neither holds: no cancellation exists, Step 3-5 prove S(A) is KS-colorable with an explicit 192-coloring (necessity).

The proof is entirely analytical: finite case analysis + structural decomposition. No SAT solvers, no computation certificates.

### 4. Consequences (~1 page)

**Corollary 1 (Heegner number characterization):**
Among imaginary quadratic fields Q(sqrt(-d)), the two-element alphabet supports KS-uncolorable ray sets iff d is a Heegner number (class number 1) AND the generator has |N| = 2 (d = 2, 7) or is a cube root of unity (d = 3). The remaining Heegner numbers fail because |N(sqrt(-d))| = d >= 11 (too large) or |N(i)| = 1 (too small).

**Corollary 2 (Galois symmetry):**
The non-trivial automorphism sigma in Gal(K/Q) acts as an automorphism of the orthogonality graph and KS hypergraph. Proof: sigma preserves inner products (for real fields: sigma(<v|w>) = <sigma(v)|sigma(w)>; for imaginary fields: sigma commutes with conjugation). This provides a discrete symmetry beyond unitary equivalence.

**Corollary 3 (Connection to Cortez Z[1/6]):**
The main theorem's two conditions involve exactly the primes 2 and 3: |N| = 2 requires the prime 2 in the norm factorization; (N = 1, Tr = -1) requires the prime 3 (since it characterizes Phi_3). This matches the Cortez-Schmid-Spekkens result that Z[1/N] supports algebraic hidden states iff 6|N. The conductor of Q(zeta_6) is 6.

**Remark (Cyclotomic restatement):**
The 6|n cyclotomic theorem (from the main paper) restates as: the Galois group (Z/nZ)* must surject onto Z/6Z. This requires elements of order dividing both phi(2) and phi(3), equivalent to 6|n.

### 5. Discussion (~0.5 page)
- Scope limitation: raw alphabets only. Cross-product completion can introduce new mechanisms (golden ratio). A classification of completion-expanded algebras remains open.
- Higher-degree extensions: the cubic island Q(cbrt(2)) has Galois closure with group S_3. The norm/trace framework extends but the enumeration is more complex.
- Connection to Gleason: Gleason constrains measures via matrix trace; our theorem constrains alphabets via Galois trace. Both traces encode the arithmetic of primes 2 and 3. The chain: Gleason -> KS -> Algebraic Islands -> Galois.
- Open: Can class field theory (specifically conductors of abelian extensions) provide a unified invariant?

## Explicit Non-Goals
- No completion-expanded alphabets (golden ratio is out of scope)
- No non-quadratic fields (cubic island mentioned but not classified)
- No sub-31 search or 24-31 gap results
- No CSW / contextual fraction computations (that's the main paper)
- No sheaf-theoretic framework

## Computational Requirements
- NONE for the proof (fully analytical)
- Optional: a verification script that confirms the cross-product case analysis (Step 4) symbolically, for reviewer confidence. Can reuse existing ks_search.py infrastructure.
- The main paper's existing data (Tables 1-3) provides empirical confirmation but is NOT required by the proof.

## Dependencies
- Main paper (algebraic_islands.tex) must be at least submitted
- Rajan-Visser 2019 (already fetched and cited)
- No new external papers needed

## Target Venue
- Physical Review Letters (4-page limit, supplemental material allowed)
- Alternative: Physical Review A Rapid Communications
