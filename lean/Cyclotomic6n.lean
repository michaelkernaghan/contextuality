/-
  Cyclotomic6n.lean — Lean 4 formalization of the main theorem of
  "Kochen–Specker uncolorability in root-of-unity coordinate alphabets
   requires exactly 6 | n"  (cyclotomic_letter.tex).

  STATUS: IN PROGRESS.  Concretely proved, sorry-free:
  ----------------------------------------------------------------------
    • Sufficiency (6 | n ⇒ KS-uncolorable): `ksUncolorable_mono` (monotonicity
      under supersets), `rootAlphabet_mono`/`S_mono` (the embedding S 6 ⊆ S n
      for 6 | n), assembled in `sufficiency` modulo the cited 33-set fact.
    • Vanishing-sum lemmas: `twoTerm_vanishing` (two n-th roots sum to 0 ↔ 2|n),
      `threeTerm_dvd` (three n-th roots sum to 0 ⇒ 3|n).
    • Necessity **Case 1** (3 ∤ n ∧ 2 ∤ n) is CLOSED: `sum_three_roots_eq_zero`
      → `case1_orthogonal_disjoint` (orthogonal ⇒ disjoint support) →
      `disjoint_support_unique_at_zero` (axis-triad classification) → the
      coloring `v ↦ (v 0 ≠ 0)` is valid.

  Remaining `sorry`s (3), each honest and clearly marked:
    • `cabello_S6_uncolorable` — S 6 contains Cabello's Eisenstein 33-vector KS
      set, hence is uncolorable.  The ONE fact the paper itself imports from
      Cabello (2025) rather than reproves; a Lean proof needs a finite
      orthogonality check over a computable subfield (e.g. ℤ[ω]).
    • necessity Case 2 (3 ∤ n, 2 | n) — perfect-matching coloring.
    • necessity Case 3 (3 | n, 2 ∤ n) — projective collapse.

  No machine-verification claim is made for the theorem as a whole until the
  `sorry`s are discharged.  Requires Lean 4.30.0 + Mathlib v4.30.0 (see
  lakefile.toml); the file compiles against that toolchain.

  cf. Tsoukalas et al., "Advancing Mathematics Research with AI-Driven Formal
  Proof Search" (AlphaProof Nexus), arXiv:2605.22763 (2026).
-/

import Mathlib

open scoped BigOperators

namespace KSCyclotomic

/-! ### Rays, orthogonality, triads, and KS colorings -/

/-- Hermitian inner product on ℂ³: ⟨v | w⟩ = Σₖ conj(vₖ) · wₖ.
    Marked `noncomputable`: it is a purely mathematical definition (complex
    conjugation pulls in noncomputable instances), never evaluated. -/
noncomputable def inner3 (v w : Fin 3 → ℂ) : ℂ := ∑ k, (starRingEnd ℂ) (v k) * w k

/-- Two rays are *orthogonal* when their Hermitian inner product vanishes. -/
def Orthogonal (v w : Fin 3 → ℂ) : Prop := inner3 v w = 0

/-- An orthogonal *triad*: three mutually orthogonal, pairwise distinct rays,
    all drawn from `R` (an orthonormal basis up to normalization). -/
def IsTriad (R : Set (Fin 3 → ℂ)) (t : Finset (Fin 3 → ℂ)) : Prop :=
  ↑t ⊆ R ∧ t.card = 3 ∧ ∀ a ∈ t, ∀ b ∈ t, a ≠ b → Orthogonal a b

/-- A *KS coloring* of `R`: a `Bool` labeling of rays such that
    (I) no two orthogonal rays of `R` are both `true`, and
    (II) every orthogonal triad of `R` contains exactly one `true`. -/
def IsColoring (R : Set (Fin 3 → ℂ)) (c : (Fin 3 → ℂ) → Bool) : Prop :=
  (∀ v ∈ R, ∀ w ∈ R, Orthogonal v w → ¬ (c v = true ∧ c w = true)) ∧
  (∀ t : Finset (Fin 3 → ℂ), IsTriad R t → (t.filter (fun v => c v = true)).card = 1)

/-- `R` is *KS-uncolorable* if it admits no KS coloring. -/
def KSUncolorable (R : Set (Fin 3 → ℂ)) : Prop := ¬ ∃ c, IsColoring R c

/-- **Monotonicity of KS-uncolorability.**  Any superset of a KS-uncolorable set
    is KS-uncolorable: a coloring of the larger set restricts to a coloring of
    the smaller one (orthogonal pairs and triads of `R` are also pairs and
    triads of `R'`), so an uncolorable `R` blocks any coloring of `R'`. -/
theorem ksUncolorable_mono {R R' : Set (Fin 3 → ℂ)} (h : R ⊆ R')
    (hR : KSUncolorable R) : KSUncolorable R' := by
  rintro ⟨c, hI, hII⟩
  exact hR ⟨c,
    fun v hv w hw hvw => hI v (h hv) w (h hw) hvw,
    fun t ht => hII t ⟨ht.1.trans h, ht.2.1, ht.2.2⟩⟩

/-! ### The cyclotomic ray set Sₙ and the divisibility embedding -/

/-- Coordinate alphabet at level `n`: a coordinate is `0` or an `n`-th root of
    unity.  (Equivalent to `{0} ∪ {ζⁿ_k}` without naming a primitive root.) -/
def rootAlphabet (n : ℕ) (x : ℂ) : Prop := x = 0 ∨ x ^ n = 1

/-- The cyclotomic ray set `Sₙ ⊂ ℂ³`: nonzero vectors whose every coordinate
    lies in the level-`n` root alphabet. -/
def S (n : ℕ) : Set (Fin 3 → ℂ) := { v | v ≠ 0 ∧ ∀ k, rootAlphabet n (v k) }

/-- An `m`-th root of unity is an `n`-th root of unity whenever `m ∣ n`. -/
theorem rootAlphabet_mono {m n : ℕ} (h : m ∣ n) {x : ℂ} :
    rootAlphabet m x → rootAlphabet n x := by
  rintro (rfl | hx)
  · exact Or.inl rfl
  · obtain ⟨k, rfl⟩ := h
    exact Or.inr (by rw [pow_mul, hx, one_pow])

/-- **Alphabet embedding.**  `S m ⊆ S n` whenever `m ∣ n`; in particular
    `S 6 ⊆ S n` for every `n` with `6 ∣ n`. -/
theorem S_mono {m n : ℕ} (h : m ∣ n) : S m ⊆ S n := by
  rintro v ⟨hv0, hv⟩
  exact ⟨hv0, fun k => rootAlphabet_mono h (hv k)⟩

/-! ### Vanishing-sum lemmas (building blocks for necessity)

These formalize Lemmas 1–2 of the letter: the only short vanishing sums of
`n`-th roots of unity that arise as orthogonality conditions in `ℂ³` are
2-term (needs `2 ∣ n`) and 3-term (needs `3 ∣ n`).  They are the engine of the
necessity direction (Cases 1–3); not yet wired into the main proof. -/

/-- A nonneg real whose `n`-th power (n ≠ 0) is `1` must itself be `1`;
    applied to `normSq` of a root of unity. -/
theorem normSq_one_of_pow {n : ℕ} (hn : n ≠ 0) {z : ℂ} (hz : z ^ n = 1) :
    Complex.normSq z = 1 := by
  have hpow : Complex.normSq z ^ n = 1 := by
    rw [← map_pow Complex.normSq z n, hz, map_one]
  have h0 : (0 : ℝ) ≤ Complex.normSq z := Complex.normSq_nonneg z
  rcases lt_trichotomy (Complex.normSq z) 1 with h | h | h
  · exact absurd hpow (pow_lt_one₀ h0 h hn).ne
  · exact h
  · exact absurd hpow (one_lt_pow₀ h hn).ne'

/-- For a root of unity, `z · conj z = 1` (its conjugate is its inverse). -/
theorem mul_conj_eq_one_of_pow {n : ℕ} (hn : n ≠ 0) {z : ℂ} (hz : z ^ n = 1) :
    z * (starRingEnd ℂ) z = 1 := by
  rw [Complex.mul_conj, normSq_one_of_pow hn hz, Complex.ofReal_one]

/-- **Two-term vanishing sums** (Lemma 2).  Two `n`-th roots of unity sum to
    zero iff `2 ∣ n`.  (`u + v = 0` forces `v = -u`, and `(-1)ⁿ = 1 ↔ n` even.) -/
theorem twoTerm_vanishing (n : ℕ) :
    (∃ u v : ℂ, u ^ n = 1 ∧ v ^ n = 1 ∧ u + v = 0) ↔ 2 ∣ n := by
  constructor
  · rintro ⟨u, v, hu, hv, hsum⟩
    have hvu : v = -u := by linear_combination hsum
    rw [hvu, neg_pow, hu, mul_one] at hv
    rw [neg_one_pow_eq_one_iff_even (by norm_num)] at hv
    obtain ⟨k, hk⟩ := hv
    exact ⟨k, by omega⟩
  · rintro ⟨k, hk⟩
    refine ⟨1, -1, one_pow n, ?_, by ring⟩
    rw [neg_one_pow_eq_one_iff_even (by norm_num)]
    exact ⟨k, by omega⟩

/-- **Three-term vanishing sums** (Lemma 1, divisibility part).  If three `n`-th
    roots of unity sum to zero, then `3 ∣ n`.  Proof: conjugating the sum and
    clearing denominators gives the second symmetric function `vw+uw+uv = 0`;
    with `u+v+w = 0` this yields `u²+uv+v² = 0`, so `g := u/v` satisfies
    `g²+g+1 = 0`, hence `g³ = 1` with `g ≠ 1`; as `gⁿ = 1` too, `ord g = 3 ∣ n`. -/
theorem threeTerm_dvd {n : ℕ} (hn : n ≠ 0) {u v w : ℂ}
    (hu : u ^ n = 1) (hv : v ^ n = 1) (hw : w ^ n = 1)
    (hsum : u + v + w = 0) : 3 ∣ n := by
  have hv0 : v ≠ 0 := by rintro rfl; rw [zero_pow hn] at hv; exact zero_ne_one hv
  -- conjugate the sum: conj u + conj v + conj w = 0
  have hconj : (starRingEnd ℂ) u + (starRingEnd ℂ) v + (starRingEnd ℂ) w = 0 := by
    rw [← map_add, ← map_add, hsum, map_zero]
  have cu := mul_conj_eq_one_of_pow hn hu
  have cv := mul_conj_eq_one_of_pow hn hv
  have cw := mul_conj_eq_one_of_pow hn hw
  -- second symmetric function vanishes
  have he2 : v * w + u * w + u * v = 0 := by
    linear_combination (-(v * w)) * cu + (-(u * w)) * cv + (-(u * v)) * cw
      + (u * v * w) * hconj
  -- hence u² + uv + v² = 0
  have hquad : u ^ 2 + u * v + v ^ 2 = 0 := by
    linear_combination (u + v) * hsum - he2
  -- g := u/v is a primitive cube root of unity
  have hgquad : (u * v⁻¹) ^ 2 + (u * v⁻¹) + 1 = 0 := by
    have key : ((u * v⁻¹) ^ 2 + (u * v⁻¹) + 1) * v ^ 2 = u ^ 2 + u * v + v ^ 2 := by
      field_simp
    rw [hquad] at key
    exact (mul_eq_zero.mp key).resolve_right (pow_ne_zero 2 hv0)
  have hg3 : (u * v⁻¹) ^ 3 = 1 := by
    linear_combination ((u * v⁻¹) - 1) * hgquad
  have hg1 : u * v⁻¹ ≠ 1 := by
    intro h; rw [h] at hgquad; norm_num at hgquad
  have hgn : (u * v⁻¹) ^ n = 1 := by
    rw [mul_pow, hu, inv_pow, hv, inv_one, mul_one]
  -- order of g is 3, and divides n
  have hord3 : orderOf (u * v⁻¹) ∣ 3 := orderOf_dvd_of_pow_eq_one hg3
  have hordn : orderOf (u * v⁻¹) ∣ n := orderOf_dvd_of_pow_eq_one hgn
  have hne1 : orderOf (u * v⁻¹) ≠ 1 := fun h => hg1 (orderOf_eq_one_iff.mp h)
  have hord_eq : orderOf (u * v⁻¹) = 3 :=
    ((Nat.dvd_prime Nat.prime_three).mp hord3).resolve_left hne1
  rwa [hord_eq] at hordn

/-- **Arithmetic core of Case 1.**  Three numbers, each `0` or an `n`-th root of
    unity, that sum to zero must all be zero when `2 ∤ n` and `3 ∤ n`: a single
    nonzero term cannot vanish, two would force `2 ∣ n` (`twoTerm_vanishing`), and
    three would force `3 ∣ n` (`threeTerm_dvd`). -/
theorem sum_three_roots_eq_zero {n : ℕ} (h2 : ¬ 2 ∣ n) (h3 : ¬ 3 ∣ n)
    {t0 t1 t2 : ℂ} (ht0 : t0 = 0 ∨ t0 ^ n = 1) (ht1 : t1 = 0 ∨ t1 ^ n = 1)
    (ht2 : t2 = 0 ∨ t2 ^ n = 1) (hsum : t0 + t1 + t2 = 0) :
    t0 = 0 ∧ t1 = 0 ∧ t2 = 0 := by
  have hn0 : n ≠ 0 := by rintro rfl; exact h2 (dvd_zero 2)
  rcases ht0 with h0 | h0 <;> rcases ht1 with h1 | h1 <;> rcases ht2 with ht | ht
  · exact ⟨h0, h1, ht⟩
  · rw [h0, h1] at hsum; simp only [zero_add, add_zero] at hsum
    rw [hsum, zero_pow hn0] at ht; exact absurd ht zero_ne_one
  · rw [h0, ht] at hsum; simp only [zero_add, add_zero] at hsum
    rw [hsum, zero_pow hn0] at h1; exact absurd h1 zero_ne_one
  · rw [h0] at hsum
    exact absurd ((twoTerm_vanishing n).mp ⟨t1, t2, h1, ht, by linear_combination hsum⟩) h2
  · rw [h1, ht] at hsum; simp only [add_zero] at hsum
    rw [hsum, zero_pow hn0] at h0; exact absurd h0 zero_ne_one
  · rw [h1] at hsum
    exact absurd ((twoTerm_vanishing n).mp ⟨t0, t2, h0, ht, by linear_combination hsum⟩) h2
  · rw [ht] at hsum
    exact absurd ((twoTerm_vanishing n).mp ⟨t0, t1, h0, h1, by linear_combination hsum⟩) h2
  · exact absurd (threeTerm_dvd hn0 h0 h1 ht hsum) h3

/-- **Case 1 — orthogonal ⇒ disjoint support.**  When `2 ∤ n` and `3 ∤ n`, two
    orthogonal rays of `S n` share no nonzero coordinate.  (Each coordinatewise
    product `conj(vₖ)·wₖ` is `0` or an `n`-th root of unity; their sum is the
    inner product, `= 0`, so `sum_three_roots_eq_zero` forces every product to
    vanish.)  Consequently the only triad in `S n` is the axis triad — the
    geometric heart of Case 1. -/
theorem case1_orthogonal_disjoint {n : ℕ} (h2 : ¬ 2 ∣ n) (h3 : ¬ 3 ∣ n)
    {v w : Fin 3 → ℂ} (hv : v ∈ S n) (hw : w ∈ S n) (horth : Orthogonal v w) :
    (v 0 = 0 ∨ w 0 = 0) ∧ (v 1 = 0 ∨ w 1 = 0) ∧ (v 2 = 0 ∨ w 2 = 0) := by
  obtain ⟨-, hvA⟩ := hv
  obtain ⟨-, hwA⟩ := hw
  -- each coordinatewise product is 0 or an n-th root of unity
  have hterm : ∀ k, (starRingEnd ℂ) (v k) * w k = 0 ∨ ((starRingEnd ℂ) (v k) * w k) ^ n = 1 := by
    intro k
    rcases hvA k with hvk | hvk
    · exact Or.inl (by rw [hvk, map_zero, zero_mul])
    · rcases hwA k with hwk | hwk
      · exact Or.inl (by rw [hwk, mul_zero])
      · exact Or.inr (by rw [mul_pow, ← map_pow (starRingEnd ℂ), hvk, map_one, hwk, one_mul])
  -- the inner product is the 3-term sum of these products
  have hsum : (starRingEnd ℂ) (v 0) * w 0 + (starRingEnd ℂ) (v 1) * w 1
      + (starRingEnd ℂ) (v 2) * w 2 = 0 := by
    have h := horth
    unfold Orthogonal inner3 at h
    rwa [Fin.sum_univ_three] at h
  have hzero := sum_three_roots_eq_zero h2 h3 (hterm 0) (hterm 1) (hterm 2) hsum
  refine ⟨?_, ?_, ?_⟩
  · rcases mul_eq_zero.mp hzero.1 with h | h
    · exact Or.inl (by simpa using h)
    · exact Or.inr h
  · rcases mul_eq_zero.mp hzero.2.1 with h | h
    · exact Or.inl (by simpa using h)
    · exact Or.inr h
  · rcases mul_eq_zero.mp hzero.2.2 with h | h
    · exact Or.inl (by simpa using h)
    · exact Or.inr h

/-- **Axis-triad classification.**  Three nonzero, pairwise disjoint-support
    vectors in `ℂ³` have supports partitioning `{0,1,2}` into singletons, so
    exactly one has a nonzero zeroth coordinate.  (At most one, since two would
    share coordinate 0; at least one, else all three are supported in `{1,2}`,
    impossible for three pairwise-disjoint nonempty supports in a 2-element set.)
    This is the structural fact behind "the only triad in Case 1 is the axis
    triad", and lets `fun v => v 0 ≠ 0` color exactly one ray per triad. -/
theorem disjoint_support_unique_at_zero
    {a b c : Fin 3 → ℂ} (ha : a ≠ 0) (hb : b ≠ 0) (hc : c ≠ 0)
    (hab : (a 0 = 0 ∨ b 0 = 0) ∧ (a 1 = 0 ∨ b 1 = 0) ∧ (a 2 = 0 ∨ b 2 = 0))
    (hac : (a 0 = 0 ∨ c 0 = 0) ∧ (a 1 = 0 ∨ c 1 = 0) ∧ (a 2 = 0 ∨ c 2 = 0))
    (hbc : (b 0 = 0 ∨ c 0 = 0) ∧ (b 1 = 0 ∨ c 1 = 0) ∧ (b 2 = 0 ∨ c 2 = 0)) :
    (a 0 ≠ 0 ∧ b 0 = 0 ∧ c 0 = 0) ∨ (a 0 = 0 ∧ b 0 ≠ 0 ∧ c 0 = 0)
      ∨ (a 0 = 0 ∧ b 0 = 0 ∧ c 0 ≠ 0) := by
  -- a nonzero vector that is zero at coordinate 0 is nonzero at coordinate 1 or 2
  have spread : ∀ {x : Fin 3 → ℂ}, x ≠ 0 → x 0 = 0 → x 1 ≠ 0 ∨ x 2 ≠ 0 := by
    intro x hx hx0
    by_contra h
    simp only [not_or, not_not] at h
    apply hx
    funext k
    fin_cases k <;> simp_all
  obtain ⟨hab0, hab1, hab2⟩ := hab
  obtain ⟨hac0, hac1, hac2⟩ := hac
  obtain ⟨hbc0, hbc1, hbc2⟩ := hbc
  -- not all three can be zero at coordinate 0 (pigeonhole on coordinates {1,2})
  have notall : ¬ (a 0 = 0 ∧ b 0 = 0 ∧ c 0 = 0) := by
    rintro ⟨ha0, hb0, hc0⟩
    have sa := spread ha ha0
    have sb := spread hb hb0
    have sc := spread hc hc0
    -- only the coordinate-{1,2} disjunctions matter here; drop the rest so the
    -- propositional search (`tauto`) stays small
    clear hab0 hac0 hbc0
    tauto
  -- at most one is nonzero at coordinate 0; combine with `notall`
  clear hab1 hab2 hac1 hac2 hbc1 hbc2
  tauto

/-! ### Sufficiency: 6 ∣ n ⇒ KS-uncolorable -/

/-- **Cited from Cabello (2025), arXiv:2508.07335.**  `S 6` contains a 33-vector
    Eisenstein (`ℤ[ω]`) KS set, hence is KS-uncolorable.  This is the single
    finite fact the paper imports rather than reproves; a Lean proof requires a
    decidable orthogonality check over a computable subfield such as `ℤ[ω]`. -/
theorem cabello_S6_uncolorable : KSUncolorable (S 6) := by
  sorry

/-- **Sufficiency.**  If `6 ∣ n` then `Sₙ` is KS-uncolorable: `S 6` embeds into
    `Sₙ` (`S_mono`) and KS-uncolorability is monotone (`ksUncolorable_mono`). -/
theorem sufficiency {n : ℕ} (h6 : 6 ∣ n) : KSUncolorable (S n) :=
  ksUncolorable_mono (S_mono h6) cabello_S6_uncolorable

/-! ### Main theorem -/

theorem six_divides_iff_ks_uncolorable (n : ℕ) (hn : 3 ≤ n) :
    KSUncolorable (S n) ↔ 6 ∣ n := by
  constructor
  · -- Necessity, by contraposition: if ¬(6 ∣ n) then S n admits a KS coloring,
    -- contradicting KS-uncolorability.  Split on (2 ∣ n) and (3 ∣ n).
    intro hKS
    by_contra h6
    by_cases h2 : 2 ∣ n <;> by_cases h3 : 3 ∣ n
    · -- 2 ∣ n and 3 ∣ n ⇒ 6 ∣ n, contradicting h6.
      exact h6 (by omega)
    · -- Case 2 (2 ∣ n, 3 ∤ n): plane perfect matching yields an explicit coloring.
      -- EVOLVE-BLOCK-START
      sorry
      -- EVOLVE-BLOCK-END
    · -- Case 3 (2 ∤ n, 3 ∣ n): projective collapse isolates triads.
      -- EVOLVE-BLOCK-START
      sorry
      -- EVOLVE-BLOCK-END
    · -- Case 1 (2 ∤ n, 3 ∤ n): color a ray `1` iff its 0th coordinate is nonzero.
      -- (I) holds because orthogonal pairs have disjoint support (so cannot both
      -- be nonzero at coordinate 0); (II) holds because in any triad the three
      -- rays have disjoint supports partitioning {0,1,2}, so exactly one is
      -- nonzero at coordinate 0 (`disjoint_support_unique_at_zero`).
      classical
      refine hKS ⟨fun v => decide (v 0 ≠ 0), ?_, ?_⟩
      · -- (I): no two orthogonal rays are both colored 1
        intro v hv w hw horth
        simp only [decide_eq_true_eq]
        rintro ⟨hcv, hcw⟩
        rcases (case1_orthogonal_disjoint h2 h3 hv hw horth).1 with h | h
        · exact hcv h
        · exact hcw h
      · -- (II): every triad has exactly one ray colored 1
        intro t ht
        obtain ⟨a, b, d, hne1, hne2, hne3, rfl⟩ := Finset.card_eq_three.mp ht.2.1
        have maS : a ∈ S n := ht.1 (by simp)
        have mbS : b ∈ S n := ht.1 (by simp)
        have mdS : d ∈ S n := ht.1 (by simp)
        have uniq := disjoint_support_unique_at_zero maS.1 mbS.1 mdS.1
          (case1_orthogonal_disjoint h2 h3 maS mbS (ht.2.2 a (by simp) b (by simp) hne1))
          (case1_orthogonal_disjoint h2 h3 maS mdS (ht.2.2 a (by simp) d (by simp) hne2))
          (case1_orthogonal_disjoint h2 h3 mbS mdS (ht.2.2 b (by simp) d (by simp) hne3))
        rw [Finset.card_eq_one]
        rcases uniq with ⟨pa, pb, pd⟩ | ⟨pa, pb, pd⟩ | ⟨pa, pb, pd⟩
        · refine ⟨a, ?_⟩
          ext x
          simp only [Finset.mem_filter, Finset.mem_insert, Finset.mem_singleton, decide_eq_true_eq]
          constructor
          · rintro ⟨rfl | rfl | rfl, hx0⟩
            · rfl
            · exact absurd pb hx0
            · exact absurd pd hx0
          · rintro rfl; exact ⟨Or.inl rfl, pa⟩
        · refine ⟨b, ?_⟩
          ext x
          simp only [Finset.mem_filter, Finset.mem_insert, Finset.mem_singleton, decide_eq_true_eq]
          constructor
          · rintro ⟨rfl | rfl | rfl, hx0⟩
            · exact absurd pa hx0
            · rfl
            · exact absurd pd hx0
          · rintro rfl; exact ⟨Or.inr (Or.inl rfl), pb⟩
        · refine ⟨d, ?_⟩
          ext x
          simp only [Finset.mem_filter, Finset.mem_insert, Finset.mem_singleton, decide_eq_true_eq]
          constructor
          · rintro ⟨rfl | rfl | rfl, hx0⟩
            · exact absurd pa hx0
            · exact absurd pb hx0
            · rfl
          · rintro rfl; exact ⟨Or.inr (Or.inr rfl), pd⟩
  · -- Sufficiency: proved above via monotone embedding of Cabello's S₆ KS set.
    exact fun h6 => sufficiency h6

end KSCyclotomic
