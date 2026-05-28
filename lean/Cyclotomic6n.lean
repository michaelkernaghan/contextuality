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
    • Necessity **Case 3** (3 | n, 2 ∤ n) — projective collapse, FULLY CLOSED
      (`sorry`-free end to end).  Built from:
        - `Tmap` (coordinatewise scaling `v ↦ (aᵏ vₖ)`), `inner_Tmap` (its
          Hermitian form collapses to a phase sum since |vₖ|=1).
        - the three orbit orthogonalities `orth_v_Tv`/`orth_v_T2v`/`orth_Tv_T2v`
          and `Orthogonal_symm`, assembled into `orbit_isTriad`: the orbit
          {v, Tω v, Tω² v} of an all-nonzero ray IS an orthogonal triad of Sₙ.
        - cube-root algebra `cubeRoot_sum` (1+ω+ω²=0), `conj_cubeRoot`
          (conj ω = ω²), `cubeRoot_dichotomy` (the only primitive cube roots are
          ω, ω²).
        - `Tmap_allNonzero` (Tₐ preserves Sₙ), `Tmap_ne`/`Tmap_ne'` (distinctness).
        - **`collapse`** (Lemma `collapse`, hard direction): any all-nonzero ray
          orthogonal to `v` is projectively `Tω v` or `Tω² v`.  Proved via the
          vanishing of BOTH symmetric functions of `tₖ = conj(vₖ)wₖ` (from the
          sum and its conjugate), forcing `t₁/t₀ ∈ {ω, ω²}` by `cubeRoot_dichotomy`,
          then rebuilding `w = t₀·Tω v` (or `t₀·Tω² v`).
        - **decoupling** (`2 ∤ n`): `two_roots_sum_zero` (two root-or-zero terms
          summing to 0 both vanish); `allNonzero_orth_imp` (an all-nonzero ray is
          orthogonal only to all-nonzero rays — the all-nonzero/zero-bearing
          sectors are decoupled); `orth_disjoint_of_zero` (orthogonal zero-bearing
          rays have disjoint support, so the sector is Case-1-like).
        - **classification**: `triad_homogeneous` (every triad is all-all-nonzero
          or all-zero-bearing); `zerobearing_triad_card` (a zero-bearing triad has
          exactly one ray nonzero at coordinate 0 — obligation (II) for that
          sector, via the same `v ↦ v 0 ≠ 0` rule as Case 1).
        - **coloring** (`case3_colorable`): the FULL Case 3 is assembled and
          compiles — the coloring `v ↦ if AllNonzero then sel v else (v 0 ≠ 0)`
          satisfies both KS obligations (helpers `allNonzero_sel_pair`/`_triad`,
          `filter_triple_card_one`, `orth_same_ray_absurd`).
        - **transversal** (`exists_orbit_selector`): the orbit selector is built on
          scale-invariant ratios `qRatio v = (v₁/v₀, v₂/v₀)` via the orbit quotient
          of the ℤ/3 action `gPair ω (a,b) = (ω a, ω² b)` (`pairRel`/`pairRel_equiv`,
          `Quotient.out` representative).  Necessity **Case 3 is now fully closed,
          `sorry`-free end to end.**

  Remaining `sorry`s (2), each honest and clearly marked:
    • `cabello_S6_uncolorable` — S 6 contains Cabello's Eisenstein 33-vector KS
      set, hence is uncolorable.  The ONE fact the paper itself imports from
      Cabello (2025) rather than reproves; a Lean proof needs a finite
      orthogonality check over a computable subfield (e.g. ℤ[ω]).
    • necessity Case 2 (3 ∤ n, 2 | n) — perfect-matching coloring (untouched).

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

/-! ### Case 3 (3 ∣ n, 2 ∤ n): projective collapse

The principal necessity case.  With `ω = ζ^{n/3}` a primitive cube root of unity,
the **projective-collapse map** `Tω : (v₀,v₁,v₂) ↦ (v₀, ω v₁, ω² v₂)` — coordinate
`k` scaled by `ωᵏ` — sends each all-nonzero ray to an orthogonal partner, and the
orbit `{v, Tω v, Tω² v}` is an orthogonal triad.  Because `|vₖ| = 1`, every orbit
orthogonality reduces to the cyclotomic identity `1 + ω + ω² = 0`.  This section
builds that computational core; the deeper "exactly two partners / one true per
orbit" combinatorics are isolated as marked sub-goals below. -/

/-- An *all-nonzero* ray of `S n`: every coordinate is a (nonzero) `n`-th root of
    unity. -/
def AllNonzero (n : ℕ) (v : Fin 3 → ℂ) : Prop := v ∈ S n ∧ ∀ k, v k ≠ 0

/-- Coordinates of an all-nonzero ray are `n`-th roots of unity. -/
theorem allNonzero_pow {n : ℕ} {v : Fin 3 → ℂ} (hv : AllNonzero n v) (k : Fin 3) :
    (v k) ^ n = 1 := (hv.1.2 k).resolve_left (hv.2 k)

/-- Each coordinate of an all-nonzero ray has unit modulus: `conj(vₖ)·vₖ = 1`. -/
theorem allNonzero_normSq {n : ℕ} (hn : n ≠ 0) {v : Fin 3 → ℂ} (hv : AllNonzero n v)
    (k : Fin 3) : (starRingEnd ℂ) (v k) * v k = 1 := by
  rw [mul_comm]; exact mul_conj_eq_one_of_pow hn (allNonzero_pow hv k)

/-- From `ω³ = 1` and `ω ≠ 1`, the defining cyclotomic identity `1 + ω + ω² = 0`. -/
theorem cubeRoot_sum {ω : ℂ} (hω3 : ω ^ 3 = 1) (hω1 : ω ≠ 1) : 1 + ω + ω ^ 2 = 0 := by
  have h : (ω - 1) * (1 + ω + ω ^ 2) = 0 := by linear_combination hω3
  exact (mul_eq_zero.mp h).resolve_left (fun he => hω1 (by linear_combination he))

/-- A cube root of unity has `conj ω = ω²` (its conjugate is its inverse `ω⁻¹ = ω²`). -/
theorem conj_cubeRoot {ω : ℂ} (hω3 : ω ^ 3 = 1) : (starRingEnd ℂ) ω = ω ^ 2 := by
  have hω0 : ω ≠ 0 := by rintro rfl; norm_num at hω3
  have h1 : ω * (starRingEnd ℂ) ω = 1 := mul_conj_eq_one_of_pow (by norm_num) hω3
  have h2 : ω * ω ^ 2 = 1 := by linear_combination hω3
  exact mul_left_cancel₀ hω0 (h1.trans h2.symm)

/-- **Primitive cube roots are `ω` or `ω²`.**  Any `g` with `g³ = 1` and `g ≠ 1`
    equals `ω` or `ω²`: both are roots of the quadratic factor `X² + X + 1` of
    `X³ - 1`, which has no others.  This is the algebraic core of the collapse
    lemma — it forces the two orthogonal partners of a ray to be its orbit-mates. -/
theorem cubeRoot_dichotomy {ω g : ℂ} (hω3 : ω ^ 3 = 1) (hω1 : ω ≠ 1)
    (hg3 : g ^ 3 = 1) (hg1 : g ≠ 1) : g = ω ∨ g = ω ^ 2 := by
  have hωsum := cubeRoot_sum hω3 hω1
  have hgsum := cubeRoot_sum hg3 hg1
  have hfac : (g - ω) * (g - ω ^ 2) = 0 := by
    linear_combination hgsum - g * hωsum + hω3
  rcases mul_eq_zero.mp hfac with h | h
  · exact Or.inl (by linear_combination h)
  · exact Or.inr (by linear_combination h)

/-- The projective-collapse map `Tₐ : v ↦ (aᵏ · vₖ)ₖ`.  For `a = ω` a primitive
    cube root this is `(v₀, ω v₁, ω² v₂)`; iterating gives `T_{ω²} = Tω ∘ Tω`. -/
def Tmap (a : ℂ) (v : Fin 3 → ℂ) : Fin 3 → ℂ := fun k => a ^ (k : ℕ) * v k

@[simp] theorem Tmap_one (v : Fin 3 → ℂ) : Tmap 1 v = v := by
  funext k; simp [Tmap]

/-- **Inner product of two scalings.**  For an all-nonzero ray, `⟨Tₐv | T_b v⟩`
    collapses to a pure phase sum `1 + (conj a)·b + (conj a)²·b²`, since the
    coordinate moduli are all `1`. -/
theorem inner_Tmap {n : ℕ} (hn : n ≠ 0) {v : Fin 3 → ℂ} (hv : AllNonzero n v) (a b : ℂ) :
    inner3 (Tmap a v) (Tmap b v)
      = 1 + (starRingEnd ℂ) a * b + (starRingEnd ℂ) a ^ 2 * b ^ 2 := by
  have key : ∀ k : Fin 3,
      (starRingEnd ℂ) (a ^ (k : ℕ) * v k) * (b ^ (k : ℕ) * v k)
        = (starRingEnd ℂ) a ^ (k : ℕ) * b ^ (k : ℕ) := by
    intro k
    rw [map_mul, map_pow]
    linear_combination ((starRingEnd ℂ) a ^ (k : ℕ) * b ^ (k : ℕ)) * allNonzero_normSq hn hv k
  unfold inner3 Tmap
  rw [Fin.sum_univ_three, key 0, key 1, key 2]
  norm_num

/-- `v ⊥ Tω v`: the ray is orthogonal to its image (`1 + ω + ω² = 0`). -/
theorem orth_v_Tv {n : ℕ} (hn : n ≠ 0) {v : Fin 3 → ℂ} (hv : AllNonzero n v)
    {ω : ℂ} (hω3 : ω ^ 3 = 1) (hω1 : ω ≠ 1) : Orthogonal v (Tmap ω v) := by
  have h := inner_Tmap hn hv 1 ω
  rw [Tmap_one] at h
  unfold Orthogonal
  rw [h, map_one]
  linear_combination cubeRoot_sum hω3 hω1

/-- `v ⊥ Tω² v`: orthogonal to the second image. -/
theorem orth_v_T2v {n : ℕ} (hn : n ≠ 0) {v : Fin 3 → ℂ} (hv : AllNonzero n v)
    {ω : ℂ} (hω3 : ω ^ 3 = 1) (hω1 : ω ≠ 1) : Orthogonal v (Tmap (ω ^ 2) v) := by
  have h := inner_Tmap hn hv 1 (ω ^ 2)
  rw [Tmap_one] at h
  unfold Orthogonal
  rw [h, map_one]
  linear_combination ω * hω3 + cubeRoot_sum hω3 hω1

/-- `Tω v ⊥ Tω² v`: the two images are orthogonal, completing the orbit triad. -/
theorem orth_Tv_T2v {n : ℕ} (hn : n ≠ 0) {v : Fin 3 → ℂ} (hv : AllNonzero n v)
    {ω : ℂ} (hω3 : ω ^ 3 = 1) (hω1 : ω ≠ 1) : Orthogonal (Tmap ω v) (Tmap (ω ^ 2) v) := by
  have h := inner_Tmap hn hv ω (ω ^ 2)
  unfold Orthogonal
  rw [h, conj_cubeRoot hω3]
  linear_combination (ω + ω ^ 2 * (ω ^ 3 + 1)) * hω3 + cubeRoot_sum hω3 hω1

/-- The Hermitian form is conjugate-symmetric, so orthogonality is a symmetric
    relation: `v ⊥ w → w ⊥ v`. -/
theorem Orthogonal_symm {v w : Fin 3 → ℂ} (h : Orthogonal v w) : Orthogonal w v := by
  unfold Orthogonal inner3 at h ⊢
  have hc : (starRingEnd ℂ) (∑ k, (starRingEnd ℂ) (v k) * w k)
      = ∑ k, (starRingEnd ℂ) (w k) * v k := by
    rw [map_sum]
    refine Finset.sum_congr rfl (fun k _ => ?_)
    simp only [map_mul, starRingEnd_apply, star_star]
    ring
  rw [← hc, h, map_zero]

/-- `Tₐ` preserves all-nonzero rays whenever `a` is itself an `n`-th root of unity:
    each coordinate `aᵏ·vₖ` is again a root of unity and nonzero. -/
theorem Tmap_allNonzero {n : ℕ} (hn : n ≠ 0) {a : ℂ} (ha : a ^ n = 1) {v : Fin 3 → ℂ}
    (hv : AllNonzero n v) : AllNonzero n (Tmap a v) := by
  have ha0 : a ≠ 0 := fun h => by rw [h, zero_pow hn] at ha; exact zero_ne_one ha
  have hcoord : ∀ k, (Tmap a v) k ≠ 0 := fun k =>
    mul_ne_zero (pow_ne_zero _ ha0) (hv.2 k)
  refine ⟨⟨fun hz => hcoord 0 (by rw [hz]; rfl), fun k => Or.inr ?_⟩, hcoord⟩
  have hpow : (a ^ (k : ℕ) * v k) ^ n = (a ^ n) ^ (k : ℕ) * (v k) ^ n := by
    rw [mul_pow, ← pow_mul, ← pow_mul, Nat.mul_comm (k : ℕ) n]
  simp only [Tmap]
  rw [hpow, ha, one_pow, one_mul, allNonzero_pow hv k]

/-- Distinct scalings of an all-nonzero ray are distinct vectors (they differ at
    coordinate 1, where `vₖ ≠ 0`). -/
theorem Tmap_ne' {n : ℕ} {v : Fin 3 → ℂ} (hv : AllNonzero n v) {a b : ℂ} (hab : a ≠ b) :
    Tmap a v ≠ Tmap b v := by
  intro h
  have h1 := congrFun h 1
  simp only [Tmap, Fin.val_one, pow_one] at h1
  have hz : (a - b) * v 1 = 0 := by linear_combination h1
  rcases mul_eq_zero.mp hz with hz | hz
  · exact hab (sub_eq_zero.mp hz)
  · exact hv.2 1 hz

/-- A ray differs from its nontrivial scaling: `v ≠ Tₐ v` when `a ≠ 1`. -/
theorem Tmap_ne {n : ℕ} {v : Fin 3 → ℂ} (hv : AllNonzero n v) {a : ℂ} (ha : a ≠ 1) :
    v ≠ Tmap a v := by
  intro h
  have h1 := congrFun h 1
  simp only [Tmap, Fin.val_one, pow_one] at h1
  have hz : (1 - a) * v 1 = 0 := by linear_combination h1
  rcases mul_eq_zero.mp hz with hz | hz
  · exact ha (by linear_combination -hz)
  · exact hv.2 1 hz

/-- **Orbit is a triad.**  For a primitive cube root `ω` that is also an `n`-th
    root of unity, the projective-collapse orbit `{v, Tω v, Tω² v}` of an
    all-nonzero ray is an orthogonal triad of `Sₙ`.  (This is the "easy" half of
    Lemma `unique` in the letter: the orbit *is* a triad; that it is the *only*
    one containing `v` is the harder collapse lemma below.) -/
theorem orbit_isTriad {n : ℕ} (hn : n ≠ 0) {v : Fin 3 → ℂ} (hv : AllNonzero n v)
    {ω : ℂ} (hωn : ω ^ n = 1) (hω3 : ω ^ 3 = 1) (hω1 : ω ≠ 1) :
    IsTriad (S n) {v, Tmap ω v, Tmap (ω ^ 2) v} := by
  have hω2ne : ω ^ 2 ≠ 1 := fun h => hω1 (by linear_combination hω3 - ω * h)
  have hne : ω ≠ ω ^ 2 := by
    intro h
    have hz : ω * (ω - 1) = 0 := by linear_combination -h
    rcases mul_eq_zero.mp hz with hz | hz
    · exact (fun h0 : ω = 0 => by simp [h0] at hω3) hz
    · exact hω1 (by linear_combination hz)
  have hω2n : (ω ^ 2) ^ n = 1 := by rw [← pow_mul, Nat.mul_comm, pow_mul, hωn, one_pow]
  have mv : v ∈ S n := hv.1
  have mTv : Tmap ω v ∈ S n := (Tmap_allNonzero hn hωn hv).1
  have mT2v : Tmap (ω ^ 2) v ∈ S n := (Tmap_allNonzero hn hω2n hv).1
  refine ⟨?_, ?_, ?_⟩
  · intro x hx
    simp only [Finset.coe_insert, Finset.coe_singleton, Set.mem_insert_iff,
      Set.mem_singleton_iff] at hx
    rcases hx with rfl | rfl | rfl
    · exact mv
    · exact mTv
    · exact mT2v
  · rw [Finset.card_eq_three]
    exact ⟨v, Tmap ω v, Tmap (ω ^ 2) v, Tmap_ne hv hω1, Tmap_ne hv hω2ne,
      Tmap_ne' hv hne, rfl⟩
  · intro a ha b hb hab
    simp only [Finset.mem_insert, Finset.mem_singleton] at ha hb
    have oVT := orth_v_Tv hn hv hω3 hω1
    have oVT2 := orth_v_T2v hn hv hω3 hω1
    have oTT2 := orth_Tv_T2v hn hv hω3 hω1
    rcases ha with rfl | rfl | rfl <;> rcases hb with rfl | rfl | rfl <;>
      first
        | exact absurd rfl hab
        | exact oVT
        | exact oVT2
        | exact oTT2
        | exact Orthogonal_symm oVT
        | exact Orthogonal_symm oVT2
        | exact Orthogonal_symm oTT2

/-- **Collapse lemma** (Lemma `collapse` of the letter, hard direction).  If `w`
    is all-nonzero and orthogonal to the all-nonzero ray `v`, then `w` is
    projectively one of the two orbit-mates `Tω v`, `Tω² v`.  Proof: the three
    coordinatewise products `tₖ = conj(vₖ)·wₖ` are roots of unity summing to `0`,
    and (with their conjugate sum `Σ tₖ⁻¹ = 0`) have vanishing first *and* second
    symmetric functions; hence `t₁/t₀` is a primitive cube root, `= ω` or `ω²`
    (`cubeRoot_dichotomy`).  Re-multiplying by `vₖ` (using `conj(vₖ)·vₖ = 1`)
    rebuilds `w = t₀ · Tω v` or `t₀ · Tω² v`. -/
theorem collapse {n : ℕ} (hn : n ≠ 0) {v w : Fin 3 → ℂ} (hv : AllNonzero n v)
    (hw : AllNonzero n w) {ω : ℂ} (hω3 : ω ^ 3 = 1) (hω1 : ω ≠ 1)
    (horth : Orthogonal v w) :
    (∃ μ : ℂ, w = fun k => μ * (Tmap ω v) k) ∨
      (∃ μ : ℂ, w = fun k => μ * (Tmap (ω ^ 2) v) k) := by
  set e0 := (starRingEnd ℂ) (v 0) * w 0 with he0d
  set e1 := (starRingEnd ℂ) (v 1) * w 1 with he1d
  set e2 := (starRingEnd ℂ) (v 2) * w 2 with he2d
  have hepow : ∀ k : Fin 3, ((starRingEnd ℂ) (v k) * w k) ^ n = 1 := fun k => by
    rw [mul_pow, ← map_pow, allNonzero_pow hv k, map_one, allNonzero_pow hw k, mul_one]
  have he0 : e0 ≠ 0 := by
    rw [he0d]
    exact mul_ne_zero (by rw [starRingEnd_apply]; exact star_ne_zero.mpr (hv.2 0)) (hw.2 0)
  have hc0 : e0 * (starRingEnd ℂ) e0 = 1 := by rw [he0d]; exact mul_conj_eq_one_of_pow hn (hepow 0)
  have hc1 : e1 * (starRingEnd ℂ) e1 = 1 := by rw [he1d]; exact mul_conj_eq_one_of_pow hn (hepow 1)
  have hc2 : e2 * (starRingEnd ℂ) e2 = 1 := by rw [he2d]; exact mul_conj_eq_one_of_pow hn (hepow 2)
  -- first symmetric function = orthogonality condition
  have hsum : e0 + e1 + e2 = 0 := by
    have h := horth
    unfold Orthogonal inner3 at h
    rw [Fin.sum_univ_three] at h
    rw [he0d, he1d, he2d]; exact h
  -- conjugate sum vanishes
  have hcsum : (starRingEnd ℂ) e0 + (starRingEnd ℂ) e1 + (starRingEnd ℂ) e2 = 0 := by
    have h := congrArg (starRingEnd ℂ) hsum
    rwa [map_add, map_add, map_zero] at h
  -- second symmetric function vanishes (multiply conjugate sum by e0·e1·e2)
  have hp2 : e0 * e1 + e0 * e2 + e1 * e2 = 0 := by
    have key : e0 * e1 + e0 * e2 + e1 * e2
        = e0 * e1 * e2 * ((starRingEnd ℂ) e0 + (starRingEnd ℂ) e1 + (starRingEnd ℂ) e2) := by
      linear_combination (-(e1 * e2)) * hc0 + (-(e0 * e2)) * hc1 + (-(e0 * e1)) * hc2
    rw [hcsum, mul_zero] at key; exact key
  -- t₁/t₀ is a primitive cube root
  have hquad' : (e1 / e0) ^ 2 + (e1 / e0) + 1 = 0 := by
    have hq : e0 ^ 2 + e0 * e1 + e1 ^ 2 = 0 := by linear_combination (e0 + e1) * hsum - hp2
    field_simp
    linear_combination hq
  have hg3 : (e1 / e0) ^ 3 = 1 := by linear_combination (e1 / e0 - 1) * hquad'
  have hg1 : e1 / e0 ≠ 1 := fun h => by rw [h] at hquad'; norm_num at hquad'
  have hωs := cubeRoot_sum hω3 hω1
  -- coordinate reconstruction wₖ = tₖ·vₖ
  have hw0 : w 0 = e0 * v 0 := by
    rw [he0d]; linear_combination (-(w 0)) * allNonzero_normSq hn hv 0
  have hw1 : w 1 = e1 * v 1 := by
    rw [he1d]; linear_combination (-(w 1)) * allNonzero_normSq hn hv 1
  have hw2 : w 2 = e2 * v 2 := by
    rw [he2d]; linear_combination (-(w 2)) * allNonzero_normSq hn hv 2
  rcases cubeRoot_dichotomy hω3 hω1 hg3 hg1 with hcase | hcase
  · -- t₁/t₀ = ω  ⇒  w = e0 • Tω v
    have he1' : e1 = ω * e0 := by rw [div_eq_iff he0] at hcase; linear_combination hcase
    have he2' : e2 = ω ^ 2 * e0 := by linear_combination hsum - he1' - e0 * hωs
    refine Or.inl ⟨e0, ?_⟩
    have g0 : w 0 = e0 * (Tmap ω v) 0 := by
      show w 0 = e0 * (ω ^ (0 : ℕ) * v 0); rw [hw0]; ring
    have g1 : w 1 = e0 * (Tmap ω v) 1 := by
      show w 1 = e0 * (ω ^ (1 : ℕ) * v 1); rw [hw1, he1']; ring
    have g2 : w 2 = e0 * (Tmap ω v) 2 := by
      show w 2 = e0 * (ω ^ (2 : ℕ) * v 2); rw [hw2, he2']; ring
    funext k; fin_cases k
    · exact g0
    · exact g1
    · exact g2
  · -- t₁/t₀ = ω²  ⇒  w = e0 • Tω² v
    have he1' : e1 = ω ^ 2 * e0 := by rw [div_eq_iff he0] at hcase; linear_combination hcase
    have he2' : e2 = ω * e0 := by linear_combination hsum - he1' - e0 * hωs
    refine Or.inr ⟨e0, ?_⟩
    have g0 : w 0 = e0 * (Tmap (ω ^ 2) v) 0 := by
      show w 0 = e0 * ((ω ^ 2) ^ (0 : ℕ) * v 0); rw [hw0]; ring
    have g1 : w 1 = e0 * (Tmap (ω ^ 2) v) 1 := by
      show w 1 = e0 * ((ω ^ 2) ^ (1 : ℕ) * v 1); rw [hw1, he1']; ring
    have g2 : w 2 = e0 * (Tmap (ω ^ 2) v) 2 := by
      show w 2 = e0 * ((ω ^ 2) ^ (2 : ℕ) * v 2)
      rw [hw2, he2']; linear_combination (-(e0 * v 2 * ω)) * hω3
    funext k; fin_cases k
    · exact g0
    · exact g1
    · exact g2

/-- **Two-term decoupling.**  When `2 ∤ n`, two numbers each `0` or an `n`-th root
    of unity that sum to zero must both vanish: a single nonzero term cannot, and
    two would force `2 ∣ n` (`twoTerm_vanishing`). -/
theorem two_roots_sum_zero {n : ℕ} (h2 : ¬ 2 ∣ n) {a b : ℂ}
    (ha : a = 0 ∨ a ^ n = 1) (hb : b = 0 ∨ b ^ n = 1) (hsum : a + b = 0) :
    a = 0 ∧ b = 0 := by
  rcases ha with rfl | ha
  · rw [zero_add] at hsum; exact ⟨rfl, hsum⟩
  · rcases hb with rfl | hb
    · rw [add_zero] at hsum; exact ⟨hsum, rfl⟩
    · exact absurd ((twoTerm_vanishing n).mp ⟨a, b, ha, hb, hsum⟩) h2

/-- **Sector decoupling** (the engine of Case 3's "all-nonzero and zero-bearing
    sectors are decoupled").  When `2 ∤ n`, an all-nonzero ray `w` of `Sₙ` is
    orthogonal only to all-nonzero rays: if `v ∈ Sₙ` and `w ⊥ v`, then `v` is
    all-nonzero.  (A zero coordinate of `v` would leave one or two surviving
    inner-product terms; one root cannot vanish and two would need `2 ∣ n`, so
    a zero coordinate forces all coordinates to vanish — impossible for `v ≠ 0`.) -/
theorem allNonzero_orth_imp {n : ℕ} (h2 : ¬ 2 ∣ n) {w v : Fin 3 → ℂ}
    (hw : AllNonzero n w) (hv : v ∈ S n) (horth : Orthogonal w v) : AllNonzero n v := by
  have hconj_ne : ∀ k, (starRingEnd ℂ) (w k) ≠ 0 := fun k => by
    rw [starRingEnd_apply]; exact star_ne_zero.mpr (hw.2 k)
  have ht_root : ∀ k, (starRingEnd ℂ) (w k) * v k = 0 ∨ ((starRingEnd ℂ) (w k) * v k) ^ n = 1 := by
    intro k
    rcases hv.2 k with hk | hk
    · exact Or.inl (by rw [hk, mul_zero])
    · exact Or.inr (by rw [mul_pow, ← map_pow, allNonzero_pow hw k, map_one, hk, mul_one])
  have ht_zero_iff : ∀ k, (starRingEnd ℂ) (w k) * v k = 0 ↔ v k = 0 := fun k =>
    ⟨fun h => (mul_eq_zero.mp h).resolve_left (hconj_ne k), fun h => by rw [h, mul_zero]⟩
  have hsum : (starRingEnd ℂ) (w 0) * v 0 + (starRingEnd ℂ) (w 1) * v 1
      + (starRingEnd ℂ) (w 2) * v 2 = 0 := by
    have h := horth; unfold Orthogonal inner3 at h; rwa [Fin.sum_univ_three] at h
  have allzero_absurd : v 0 = 0 → v 1 = 0 → v 2 = 0 → False := by
    intro a b c
    apply hv.1; funext k; fin_cases k <;> simp only [Pi.zero_apply]
    · exact a
    · exact b
    · exact c
  have hv0 : v 0 ≠ 0 := by
    intro h0
    have ht0 : (starRingEnd ℂ) (w 0) * v 0 = 0 := by rw [h0, mul_zero]
    have hs := hsum; rw [ht0, zero_add] at hs
    obtain ⟨z1, z2⟩ := two_roots_sum_zero h2 (ht_root 1) (ht_root 2) hs
    exact allzero_absurd h0 ((ht_zero_iff 1).mp z1) ((ht_zero_iff 2).mp z2)
  have hv1 : v 1 ≠ 0 := by
    intro h1
    have ht1 : (starRingEnd ℂ) (w 1) * v 1 = 0 := by rw [h1, mul_zero]
    have hs := hsum; rw [ht1, add_zero] at hs
    obtain ⟨z0, z2⟩ := two_roots_sum_zero h2 (ht_root 0) (ht_root 2) hs
    exact allzero_absurd ((ht_zero_iff 0).mp z0) h1 ((ht_zero_iff 2).mp z2)
  have hv2 : v 2 ≠ 0 := by
    intro hz2
    have ht2 : (starRingEnd ℂ) (w 2) * v 2 = 0 := by rw [hz2, mul_zero]
    have hs := hsum; rw [ht2, add_zero] at hs
    obtain ⟨z0, z1⟩ := two_roots_sum_zero h2 (ht_root 0) (ht_root 1) hs
    exact allzero_absurd ((ht_zero_iff 0).mp z0) ((ht_zero_iff 1).mp z1) hz2
  refine ⟨hv, fun k => ?_⟩
  fin_cases k
  · exact hv0
  · exact hv1
  · exact hv2

/-- **Zero-bearing sector is Case-1-like.**  When `2 ∤ n`, if `v ⊥ w` in `Sₙ` and
    `v` has a zero coordinate, then `v` and `w` have disjoint support (every
    coordinate is zero in at least one of them).  Reason: a zero coordinate of `v`
    kills one inner-product term, the remaining two sum to zero, and `2 ∤ n` forces
    both to vanish (`two_roots_sum_zero`); so all coordinatewise products vanish.
    Combined with `disjoint_support_unique_at_zero` this confines every
    zero-bearing triad to the axis triad. -/
theorem orth_disjoint_of_zero {n : ℕ} (h2 : ¬ 2 ∣ n) {v w : Fin 3 → ℂ}
    (hv : v ∈ S n) (hw : w ∈ S n) (horth : Orthogonal v w)
    (hvzero : v 0 = 0 ∨ v 1 = 0 ∨ v 2 = 0) :
    (v 0 = 0 ∨ w 0 = 0) ∧ (v 1 = 0 ∨ w 1 = 0) ∧ (v 2 = 0 ∨ w 2 = 0) := by
  have ht_root : ∀ k, (starRingEnd ℂ) (v k) * w k = 0 ∨ ((starRingEnd ℂ) (v k) * w k) ^ n = 1 := by
    intro k
    rcases hv.2 k with hk | hk
    · exact Or.inl (by rw [hk, map_zero, zero_mul])
    · rcases hw.2 k with hwk | hwk
      · exact Or.inl (by rw [hwk, mul_zero])
      · exact Or.inr (by rw [mul_pow, ← map_pow, hk, map_one, hwk, one_mul])
  have hsum : (starRingEnd ℂ) (v 0) * w 0 + (starRingEnd ℂ) (v 1) * w 1
      + (starRingEnd ℂ) (v 2) * w 2 = 0 := by
    have h := horth; unfold Orthogonal inner3 at h; rwa [Fin.sum_univ_three] at h
  -- every coordinatewise product vanishes
  have hall : (starRingEnd ℂ) (v 0) * w 0 = 0 ∧ (starRingEnd ℂ) (v 1) * w 1 = 0
      ∧ (starRingEnd ℂ) (v 2) * w 2 = 0 := by
    rcases hvzero with h | h | h
    · have ht0 : (starRingEnd ℂ) (v 0) * w 0 = 0 := by rw [h, map_zero, zero_mul]
      have hs := hsum; rw [ht0, zero_add] at hs
      obtain ⟨z1, z2⟩ := two_roots_sum_zero h2 (ht_root 1) (ht_root 2) hs
      exact ⟨ht0, z1, z2⟩
    · have ht1 : (starRingEnd ℂ) (v 1) * w 1 = 0 := by rw [h, map_zero, zero_mul]
      have hs := hsum; rw [ht1, add_zero] at hs
      obtain ⟨z0, z2⟩ := two_roots_sum_zero h2 (ht_root 0) (ht_root 2) hs
      exact ⟨z0, ht1, z2⟩
    · have ht2 : (starRingEnd ℂ) (v 2) * w 2 = 0 := by rw [h, map_zero, zero_mul]
      have hs := hsum; rw [ht2, add_zero] at hs
      obtain ⟨z0, z1⟩ := two_roots_sum_zero h2 (ht_root 0) (ht_root 1) hs
      exact ⟨z0, z1, ht2⟩
  -- conj(vₖ)·wₖ = 0  ⇒  vₖ = 0 ∨ wₖ = 0
  have split : ∀ {k}, (starRingEnd ℂ) (v k) * w k = 0 → v k = 0 ∨ w k = 0 := by
    intro k h
    rcases mul_eq_zero.mp h with h | h
    · exact Or.inl (by rw [starRingEnd_apply] at h; exact star_eq_zero.mp h)
    · exact Or.inr h
  exact ⟨split hall.1, split hall.2.1, split hall.2.2⟩

/-! ### Triad classification (Case 3) -/

/-- **Triad homogeneity.**  When `2 ∤ n`, every triad of `Sₙ` is *homogeneous*:
    either all three rays are all-nonzero, or all three are zero-bearing (each has
    a zero coordinate).  An all-nonzero member forces its two orthogonal partners
    to be all-nonzero (`allNonzero_orth_imp`), so the two types cannot mix. -/
theorem triad_homogeneous {n : ℕ} (h2 : ¬ 2 ∣ n) {t : Finset (Fin 3 → ℂ)}
    (ht : IsTriad (S n) t) :
    (∀ r ∈ t, AllNonzero n r) ∨ (∀ r ∈ t, r 0 = 0 ∨ r 1 = 0 ∨ r 2 = 0) := by
  by_cases hex : ∃ a ∈ t, AllNonzero n a
  · left
    obtain ⟨a, ha, haN⟩ := hex
    intro r hr
    by_cases hra : r = a
    · rw [hra]; exact haN
    · exact allNonzero_orth_imp h2 haN (ht.1 (Finset.mem_coe.mpr hr))
        (ht.2.2 a ha r hr (fun h => hra h.symm))
  · right
    push Not at hex
    intro r hr
    have hrS : r ∈ S n := ht.1 (Finset.mem_coe.mpr hr)
    by_contra hc
    push Not at hc
    exact hex r hr ⟨hrS, fun k => by fin_cases k; exacts [hc.1, hc.2.1, hc.2.2]⟩

/-- **Zero-bearing triads are axis triads.**  When `2 ∤ n`, a zero-bearing triad
    has exactly one ray nonzero at coordinate 0.  Mirrors the Case 1 argument:
    orthogonal zero-bearing rays have disjoint support (`orth_disjoint_of_zero`),
    and three pairwise-disjoint nonzero vectors partition `{0,1,2}` into singletons
    (`disjoint_support_unique_at_zero`).  This is obligation (II) of the KS coloring
    on the zero-bearing sector — the same `v ↦ v 0 ≠ 0` rule as Case 1. -/
theorem zerobearing_triad_card {n : ℕ} (h2 : ¬ 2 ∣ n) {t : Finset (Fin 3 → ℂ)}
    (ht : IsTriad (S n) t) (hz : ∀ r ∈ t, r 0 = 0 ∨ r 1 = 0 ∨ r 2 = 0) :
    (t.filter (fun r => r 0 ≠ 0)).card = 1 := by
  classical
  obtain ⟨a, b, d, hne1, hne2, hne3, rfl⟩ := Finset.card_eq_three.mp ht.2.1
  have maS : a ∈ S n := ht.1 (by simp)
  have mbS : b ∈ S n := ht.1 (by simp)
  have mdS : d ∈ S n := ht.1 (by simp)
  have hza : a 0 = 0 ∨ a 1 = 0 ∨ a 2 = 0 := hz a (by simp)
  have hzb : b 0 = 0 ∨ b 1 = 0 ∨ b 2 = 0 := hz b (by simp)
  have uniq := disjoint_support_unique_at_zero maS.1 mbS.1 mdS.1
    (orth_disjoint_of_zero h2 maS mbS (ht.2.2 a (by simp) b (by simp) hne1) hza)
    (orth_disjoint_of_zero h2 maS mdS (ht.2.2 a (by simp) d (by simp) hne2) hza)
    (orth_disjoint_of_zero h2 mbS mdS (ht.2.2 b (by simp) d (by simp) hne3) hzb)
  rw [Finset.card_eq_one]
  rcases uniq with ⟨pa, pb, pd⟩ | ⟨pa, pb, pd⟩ | ⟨pa, pb, pd⟩
  · refine ⟨a, ?_⟩
    ext x
    simp only [Finset.mem_filter, Finset.mem_insert, Finset.mem_singleton]
    constructor
    · rintro ⟨rfl | rfl | rfl, hx0⟩
      · rfl
      · exact absurd pb hx0
      · exact absurd pd hx0
    · rintro rfl; exact ⟨Or.inl rfl, pa⟩
  · refine ⟨b, ?_⟩
    ext x
    simp only [Finset.mem_filter, Finset.mem_insert, Finset.mem_singleton]
    constructor
    · rintro ⟨rfl | rfl | rfl, hx0⟩
      · exact absurd pa hx0
      · rfl
      · exact absurd pd hx0
    · rintro rfl; exact ⟨Or.inr (Or.inl rfl), pb⟩
  · refine ⟨d, ?_⟩
    ext x
    simp only [Finset.mem_filter, Finset.mem_insert, Finset.mem_singleton]
    constructor
    · rintro ⟨rfl | rfl | rfl, hx0⟩
      · exact absurd pa hx0
      · exact absurd pb hx0
      · rfl
    · rintro rfl; exact ⟨Or.inr (Or.inr rfl), pd⟩

/-! ### Coloring helpers (Case 3) -/

/-- A triple of distinct rays of which exactly one satisfies `P` has exactly one
    `P`-member in its `Finset`.  (Reusable form of the Case 1 `(II)` counting.) -/
theorem filter_triple_card_one {P : (Fin 3 → ℂ) → Prop} [DecidablePred P]
    {a b d : Fin 3 → ℂ} (hab : a ≠ b) (had : a ≠ d) (hbd : b ≠ d)
    (h : (P a ∧ ¬ P b ∧ ¬ P d) ∨ (¬ P a ∧ P b ∧ ¬ P d) ∨ (¬ P a ∧ ¬ P b ∧ P d)) :
    (({a, b, d} : Finset (Fin 3 → ℂ)).filter P).card = 1 := by
  rw [Finset.card_eq_one]
  rcases h with ⟨pa, pb, pd⟩ | ⟨pa, pb, pd⟩ | ⟨pa, pb, pd⟩
  · refine ⟨a, ?_⟩
    ext x; simp only [Finset.mem_filter, Finset.mem_insert, Finset.mem_singleton]
    constructor
    · rintro ⟨rfl | rfl | rfl, hx⟩
      · rfl
      · exact absurd hx pb
      · exact absurd hx pd
    · rintro rfl; exact ⟨Or.inl rfl, pa⟩
  · refine ⟨b, ?_⟩
    ext x; simp only [Finset.mem_filter, Finset.mem_insert, Finset.mem_singleton]
    constructor
    · rintro ⟨rfl | rfl | rfl, hx⟩
      · exact absurd hx pa
      · rfl
      · exact absurd hx pd
    · rintro rfl; exact ⟨Or.inr (Or.inl rfl), pb⟩
  · refine ⟨d, ?_⟩
    ext x; simp only [Finset.mem_filter, Finset.mem_insert, Finset.mem_singleton]
    constructor
    · rintro ⟨rfl | rfl | rfl, hx⟩
      · exact absurd hx pa
      · exact absurd hx pb
      · rfl
    · rintro rfl; exact ⟨Or.inr (Or.inr rfl), pd⟩

/-- The self inner product of an all-nonzero ray is `3` (each `|vₖ|² = 1`). -/
theorem inner_self_allNonzero {n : ℕ} (hn0 : n ≠ 0) {d : Fin 3 → ℂ} (hd : AllNonzero n d) :
    inner3 d d = 3 := by
  unfold inner3
  rw [Fin.sum_univ_three, allNonzero_normSq hn0 hd 0, allNonzero_normSq hn0 hd 1,
    allNonzero_normSq hn0 hd 2]
  norm_num

/-- **Parallel rays are not orthogonal.**  Two nonzero scalar multiples `p·x`,
    `q·x` of the same all-nonzero ray `x` cannot be orthogonal: their inner product
    is `conj p · q · ⟨x|x⟩ = 3·conj p·q ≠ 0`.  Used to show the two non-`a` members
    of an all-nonzero triad lie in *distinct* orbit classes. -/
theorem orth_same_ray_absurd {n : ℕ} (hn0 : n ≠ 0) {x : Fin 3 → ℂ} (hx : AllNonzero n x)
    {b d : Fin 3 → ℂ} {p q : ℂ} (hp : p ≠ 0) (hq : q ≠ 0)
    (hbx : b = fun k => p * x k) (hdx : d = fun k => q * x k) (horth : Orthogonal b d) :
    False := by
  have key : inner3 b d = (starRingEnd ℂ) p * q * inner3 x x := by
    simp only [inner3, hbx, hdx, map_mul]
    rw [Finset.mul_sum]
    exact Finset.sum_congr rfl (fun k _ => by ring)
  rw [inner_self_allNonzero hn0 hx] at key
  unfold Orthogonal at horth
  rw [horth] at key
  rcases mul_eq_zero.mp key.symm with h | h
  · rcases mul_eq_zero.mp h with h | h
    · exact hp (by rw [starRingEnd_apply] at h; exact star_eq_zero.mp h)
    · exact hq h
  · norm_num at h

/-! ### Orbit transversal (construction of the selector)

The selector is built on coordinate *ratios* `qRatio v = (v₁/v₀, v₂/v₀)`, which are
scale-invariant.  On ratios the projective-collapse map acts as the ℤ/3 action
`gPair ω (a,b) = (ω a, ω² b)`; a transversal of its orbits (via the orbit quotient
and `Quotient.out`) gives one ray per orbit. -/

/-- The ℤ/3 action on coordinate-ratio pairs: `g (a,b) = (ω a, ω² b)`. -/
def gPair (ω : ℂ) (p : ℂ × ℂ) : ℂ × ℂ := (ω * p.1, ω ^ 2 * p.2)

/-- `g` has order dividing 3: `g³ = id` (using `ω³ = 1`). -/
theorem gPair_cube {ω : ℂ} (hω3 : ω ^ 3 = 1) (p : ℂ × ℂ) :
    gPair ω (gPair ω (gPair ω p)) = p := by
  rw [Prod.ext_iff]
  refine ⟨?_, ?_⟩ <;> simp only [gPair]
  · linear_combination p.1 * hω3
  · linear_combination (p.2 * (ω ^ 3 + 1)) * hω3

/-- `g` applied with `ω²` is `g ∘ g`. -/
theorem gPair_sq (ω : ℂ) (p : ℂ × ℂ) : gPair (ω ^ 2) p = gPair ω (gPair ω p) := by
  rw [Prod.ext_iff]
  refine ⟨?_, ?_⟩ <;> simp only [gPair] <;> ring

/-- Orbit relation of the ℤ/3 action: `q` is in the orbit of `p`. -/
def pairRel (ω : ℂ) (p q : ℂ × ℂ) : Prop :=
  q = p ∨ q = gPair ω p ∨ q = gPair ω (gPair ω p)

/-- The orbit relation is an equivalence (uses `g³ = id`). -/
theorem pairRel_equiv {ω : ℂ} (hω3 : ω ^ 3 = 1) : Equivalence (pairRel ω) := by
  refine ⟨fun p => Or.inl rfl, ?_, ?_⟩
  · rintro p q (rfl | rfl | rfl)
    · exact Or.inl rfl
    · exact Or.inr (Or.inr (gPair_cube hω3 p).symm)
    · exact Or.inr (Or.inl (gPair_cube hω3 p).symm)
  · rintro p q r (rfl | rfl | rfl) (rfl | rfl | rfl)
    · exact Or.inl rfl
    · exact Or.inr (Or.inl rfl)
    · exact Or.inr (Or.inr rfl)
    · exact Or.inr (Or.inl rfl)
    · exact Or.inr (Or.inr rfl)
    · exact Or.inl (gPair_cube hω3 p)
    · exact Or.inr (Or.inr rfl)
    · exact Or.inl (gPair_cube hω3 p)
    · exact Or.inr (Or.inl (congrArg (gPair ω) (gPair_cube hω3 p)))

/-- Coordinate ratios `(v₁/v₀, v₂/v₀)` — a scale-invariant ray invariant. -/
noncomputable def qRatio (v : Fin 3 → ℂ) : ℂ × ℂ := (v 1 / v 0, v 2 / v 0)

/-- Ratios are scale-invariant: `qRatio (c·v) = qRatio v` for `c ≠ 0`. -/
theorem qRatio_smul {c : ℂ} (hc : c ≠ 0) (v : Fin 3 → ℂ) :
    qRatio (fun k => c * v k) = qRatio v := by
  simp only [qRatio]
  rw [mul_div_mul_left _ _ hc, mul_div_mul_left _ _ hc]

/-- `Tₐ` acts on ratios exactly as `gPair a`. -/
theorem qRatio_Tmap (a : ℂ) (v : Fin 3 → ℂ) : qRatio (Tmap a v) = gPair a (qRatio v) := by
  have e0 : Tmap a v 0 = v 0 := by simp [Tmap]
  have e1 : Tmap a v 1 = a * v 1 := by simp [Tmap]
  have e2 : Tmap a v 2 = a ^ 2 * v 2 := by simp [Tmap]
  simp only [qRatio, gPair, e0, e1, e2, mul_div_assoc]

/-- **Orbit transversal** — the sole remaining input for Case 3, a pure existence
    fact independent of the KS content.  `Tω` acts freely with order 3 on the
    all-nonzero rays (modulo scaling); a scale-invariant transversal `sel` picks
    exactly one ray per orbit `{v, Tω v, Tω² v}`.  Existence is by choice over the
    orbit quotient of the free ℤ/3 action (built on the scale-invariant ratios
    `qRatio` and the action `gPair`). -/
theorem exists_orbit_selector {n : ℕ} {ω : ℂ} (hω3 : ω ^ 3 = 1) (hω1 : ω ≠ 1) :
    ∃ sel : (Fin 3 → ℂ) → Bool,
      (∀ (c : ℂ), c ≠ 0 → ∀ v, sel (fun k => c * v k) = sel v) ∧
      (∀ v, AllNonzero n v →
        (sel v = true ∧ sel (Tmap ω v) = false ∧ sel (Tmap (ω ^ 2) v) = false) ∨
        (sel v = false ∧ sel (Tmap ω v) = true ∧ sel (Tmap (ω ^ 2) v) = false) ∨
        (sel v = false ∧ sel (Tmap ω v) = false ∧ sel (Tmap (ω ^ 2) v) = true)) := by
  classical
  letI s : Setoid (ℂ × ℂ) := ⟨pairRel ω, pairRel_equiv hω3⟩
  set rep : ℂ × ℂ → ℂ × ℂ := fun p => (Quotient.mk s p).out with hrep
  have rep_mem : ∀ p, pairRel ω p (rep p) := fun p =>
    (pairRel_equiv hω3).symm (Quotient.exact (Quotient.out_eq (Quotient.mk s p)))
  have rep_eq : ∀ {a b : ℂ × ℂ}, pairRel ω a b → rep a = rep b := fun {a b} h => by
    simp only [hrep]; rw [Quotient.sound h]
  have hω0 : ω ≠ 0 := fun h => by rw [h] at hω3; norm_num at hω3
  have hω2ne : ω ^ 2 ≠ 1 := fun h => hω1 (by linear_combination hω3 - ω * h)
  refine ⟨fun v => decide (qRatio v = rep (qRatio v)), ?_, ?_⟩
  · -- scale invariance: ratios are scale-invariant
    intro c hc v
    simp only [qRatio_smul hc]
  · -- one selected per orbit
    intro v hAv
    simp only [qRatio_Tmap, gPair_sq]
    set p0 := qRatio v with hp0
    have ha : p0.1 ≠ 0 := by
      rw [hp0]; simp only [qRatio]; exact div_ne_zero (hAv.2 1) (hAv.2 0)
    have hrep1 : rep (gPair ω p0) = rep p0 :=
      rep_eq (Or.inr (Or.inr (gPair_cube hω3 p0).symm))
    have hrep2 : rep (gPair ω (gPair ω p0)) = rep p0 :=
      rep_eq (Or.inr (Or.inl (gPair_cube hω3 p0).symm))
    rw [hrep1, hrep2]
    -- the three orbit points are pairwise distinct
    have d01 : gPair ω p0 ≠ p0 := by
      intro h; simp only [gPair, Prod.ext_iff] at h
      have hz : (ω - 1) * p0.1 = 0 := by linear_combination h.1
      exact (mul_eq_zero.mp hz).elim (fun h1 => hω1 (by linear_combination h1)) ha
    have d02 : gPair ω (gPair ω p0) ≠ p0 := by
      intro h; simp only [gPair, Prod.ext_iff] at h
      have hz : (ω ^ 2 - 1) * p0.1 = 0 := by linear_combination h.1
      exact (mul_eq_zero.mp hz).elim (fun h1 => hω2ne (by linear_combination h1)) ha
    have d12 : gPair ω (gPair ω p0) ≠ gPair ω p0 := by
      intro h; simp only [gPair, Prod.ext_iff] at h
      have hz : ω * (ω - 1) * p0.1 = 0 := by linear_combination h.1
      rcases mul_eq_zero.mp hz with h1 | h1
      · exact (mul_eq_zero.mp h1).elim hω0 (fun h2 => hω1 (by linear_combination h2))
      · exact ha h1
    rcases rep_mem p0 with hr | hr | hr
    · exact Or.inl ⟨by rw [hr, decide_eq_true_eq],
        by rw [hr]; exact decide_eq_false_iff_not.mpr d01,
        by rw [hr]; exact decide_eq_false_iff_not.mpr d02⟩
    · exact Or.inr (Or.inl ⟨by rw [hr]; exact decide_eq_false_iff_not.mpr (Ne.symm d01),
        by rw [hr, decide_eq_true_eq],
        by rw [hr]; exact decide_eq_false_iff_not.mpr d12⟩)
    · exact Or.inr (Or.inr ⟨by rw [hr]; exact decide_eq_false_iff_not.mpr (Ne.symm d02),
        by rw [hr]; exact decide_eq_false_iff_not.mpr (Ne.symm d12),
        by rw [hr, decide_eq_true_eq]⟩)

/-- **(I), all-nonzero sector.**  No two orthogonal all-nonzero rays are both
    selected.  If `v ⊥ w` are both selected, `w` is projectively `Tω v` or `Tω² v`
    (`collapse`), so `sel w = sel (Tω v)` or `sel (Tω² v)` by scale-invariance; but
    `sel v = true` forces both of those `false` (one-per-orbit). -/
theorem allNonzero_sel_pair {n : ℕ} (hn0 : n ≠ 0) {ω : ℂ} (hω3 : ω ^ 3 = 1) (hω1 : ω ≠ 1)
    {sel : (Fin 3 → ℂ) → Bool}
    (hsel_inv : ∀ (c : ℂ), c ≠ 0 → ∀ v, sel (fun k => c * v k) = sel v)
    (hsel_one : ∀ v, AllNonzero n v →
      (sel v = true ∧ sel (Tmap ω v) = false ∧ sel (Tmap (ω ^ 2) v) = false) ∨
      (sel v = false ∧ sel (Tmap ω v) = true ∧ sel (Tmap (ω ^ 2) v) = false) ∨
      (sel v = false ∧ sel (Tmap ω v) = false ∧ sel (Tmap (ω ^ 2) v) = true))
    {v w : Fin 3 → ℂ} (hAv : AllNonzero n v) (hAw : AllNonzero n w)
    (horth : Orthogonal v w) (hv : sel v = true) (hw : sel w = true) : False := by
  rcases collapse hn0 hAv hAw hω3 hω1 horth with ⟨μ, hμ⟩ | ⟨μ, hμ⟩
  · have hμ0 : μ ≠ 0 := fun h => hAw.2 0 (by rw [hμ]; simp [Tmap, h])
    have hsw : sel w = sel (Tmap ω v) := by rw [hμ]; exact hsel_inv μ hμ0 _
    rcases hsel_one v hAv with ⟨_, e, _⟩ | ⟨e, _, _⟩ | ⟨e, _, _⟩
    · rw [hsw, e] at hw; exact Bool.noConfusion hw
    · rw [e] at hv; exact Bool.noConfusion hv
    · rw [e] at hv; exact Bool.noConfusion hv
  · have hμ0 : μ ≠ 0 := fun h => hAw.2 0 (by rw [hμ]; simp [Tmap, h])
    have hsw : sel w = sel (Tmap (ω ^ 2) v) := by rw [hμ]; exact hsel_inv μ hμ0 _
    rcases hsel_one v hAv with ⟨_, _, e⟩ | ⟨e, _, _⟩ | ⟨e, _, _⟩
    · rw [hsw, e] at hw; exact Bool.noConfusion hw
    · rw [e] at hv; exact Bool.noConfusion hv
    · rw [e] at hv; exact Bool.noConfusion hv

/-- **(II), all-nonzero sector.**  An all-nonzero triad is exactly one orbit, so the
    transversal selects exactly one of its rays.  The two non-`a` members are
    projectively `Tω a` and `Tω² a` (`collapse`); they lie in *distinct* classes
    (`orth_same_ray_absurd`, since they are orthogonal), so by scale-invariance and
    one-per-orbit exactly one of `sel a, sel b, sel d` is `true`. -/
theorem allNonzero_sel_triad {n : ℕ} (hn0 : n ≠ 0) {ω : ℂ}
    (hωn : ω ^ n = 1) (hω3 : ω ^ 3 = 1) (hω1 : ω ≠ 1)
    {sel : (Fin 3 → ℂ) → Bool}
    (hsel_inv : ∀ (c : ℂ), c ≠ 0 → ∀ v, sel (fun k => c * v k) = sel v)
    (hsel_one : ∀ v, AllNonzero n v →
      (sel v = true ∧ sel (Tmap ω v) = false ∧ sel (Tmap (ω ^ 2) v) = false) ∨
      (sel v = false ∧ sel (Tmap ω v) = true ∧ sel (Tmap (ω ^ 2) v) = false) ∨
      (sel v = false ∧ sel (Tmap ω v) = false ∧ sel (Tmap (ω ^ 2) v) = true))
    {a b d : Fin 3 → ℂ} (hAa : AllNonzero n a) (hAb : AllNonzero n b) (hAd : AllNonzero n d)
    (hab : a ≠ b) (had : a ≠ d) (hbd : b ≠ d)
    (oab : Orthogonal a b) (oad : Orthogonal a d) (obd : Orthogonal b d) :
    (({a, b, d} : Finset (Fin 3 → ℂ)).filter (fun v => sel v = true)).card = 1 := by
  have nt : ∀ {x : Fin 3 → ℂ}, sel x = false → sel x ≠ true := fun hf ht => by
    rw [hf] at ht; exact Bool.noConfusion ht
  have hTω : AllNonzero n (Tmap ω a) := Tmap_allNonzero hn0 hωn hAa
  have hω2n : (ω ^ 2) ^ n = 1 := by rw [← pow_mul, Nat.mul_comm, pow_mul, hωn, one_pow]
  have hTω2 : AllNonzero n (Tmap (ω ^ 2) a) := Tmap_allNonzero hn0 hω2n hAa
  refine filter_triple_card_one hab had hbd ?_
  rcases collapse hn0 hAa hAb hω3 hω1 oab with ⟨μb, hμb⟩ | ⟨μb, hμb⟩ <;>
    rcases collapse hn0 hAa hAd hω3 hω1 oad with ⟨μd, hμd⟩ | ⟨μd, hμd⟩ <;>
    have hμb0 : μb ≠ 0 := fun h => hAb.2 0 (by rw [hμb]; simp [Tmap, h]) <;>
    have hμd0 : μd ≠ 0 := fun h => hAd.2 0 (by rw [hμd]; simp [Tmap, h])
  · -- b, d both ∼ Tω a: same class, contradicts b ⊥ d
    exact (orth_same_ray_absurd hn0 hTω hμb0 hμd0 hμb hμd obd).elim
  · -- b ∼ Tω a, d ∼ Tω² a
    have hsb : sel b = sel (Tmap ω a) := by rw [hμb]; exact hsel_inv μb hμb0 _
    have hsd : sel d = sel (Tmap (ω ^ 2) a) := by rw [hμd]; exact hsel_inv μd hμd0 _
    rcases hsel_one a hAa with ⟨ea, eb, ec⟩ | ⟨ea, eb, ec⟩ | ⟨ea, eb, ec⟩
    · exact Or.inl ⟨ea, nt (hsb.trans eb), nt (hsd.trans ec)⟩
    · exact Or.inr (Or.inl ⟨nt ea, hsb.trans eb, nt (hsd.trans ec)⟩)
    · exact Or.inr (Or.inr ⟨nt ea, nt (hsb.trans eb), hsd.trans ec⟩)
  · -- b ∼ Tω² a, d ∼ Tω a
    have hsb : sel b = sel (Tmap (ω ^ 2) a) := by rw [hμb]; exact hsel_inv μb hμb0 _
    have hsd : sel d = sel (Tmap ω a) := by rw [hμd]; exact hsel_inv μd hμd0 _
    rcases hsel_one a hAa with ⟨ea, eb, ec⟩ | ⟨ea, eb, ec⟩ | ⟨ea, eb, ec⟩
    · exact Or.inl ⟨ea, nt (hsb.trans ec), nt (hsd.trans eb)⟩
    · exact Or.inr (Or.inr ⟨nt ea, nt (hsb.trans ec), hsd.trans eb⟩)
    · exact Or.inr (Or.inl ⟨nt ea, hsb.trans ec, nt (hsd.trans eb)⟩)
  · -- b, d both ∼ Tω² a: same class, contradicts b ⊥ d
    exact (orth_same_ray_absurd hn0 hTω2 hμb0 hμd0 hμb hμd obd).elim

set_option maxHeartbeats 1000000 in
/-- **Case 3 colorability.**  When `2 ∤ n` and `3 ∣ n`, `Sₙ` admits a KS coloring,
    so it is *not* KS-uncolorable.  Coloring: all-nonzero rays by the orbit
    transversal `sel`; zero-bearing rays by the Case 1 rule `v ↦ v 0 ≠ 0`.
    Obligations (I)/(II) split by `triad_homogeneous` into the all-nonzero sector
    (`allNonzero_sel_pair`/`allNonzero_sel_triad`) and the zero-bearing sector
    (`orth_disjoint_of_zero`/`zerobearing_triad_card`), with cross-sector
    orthogonality excluded by `allNonzero_orth_imp`.  The `AllNonzero` test uses an
    explicit classical `Decidable` instance to avoid an expensive structural
    instance search on the nested predicate. -/
theorem case3_colorable {n : ℕ} (hn0 : n ≠ 0) (h2 : ¬ 2 ∣ n) (h3 : 3 ∣ n) :
    ∃ c : (Fin 3 → ℂ) → Bool, IsColoring (S n) c := by
  classical
  have hpr := Complex.isPrimitiveRoot_exp 3 (by norm_num)
  obtain ⟨ω, hω3, hω1⟩ : ∃ ω : ℂ, ω ^ 3 = 1 ∧ ω ≠ 1 :=
    ⟨_, hpr.pow_eq_one, hpr.ne_one (by norm_num)⟩
  have hωn : ω ^ n = 1 := by obtain ⟨m, rfl⟩ := h3; rw [pow_mul, hω3, one_pow]
  obtain ⟨sel, hsel_inv, hsel_one⟩ := exists_orbit_selector (n := n) hω3 hω1
  set c : (Fin 3 → ℂ) → Bool :=
    fun v => @ite _ (AllNonzero n v) (Classical.propDecidable _) (sel v) (decide (v 0 ≠ 0))
    with hc
  have hcA : ∀ {v}, AllNonzero n v → c v = sel v := fun hv => by rw [hc]; exact if_pos hv
  have hcN : ∀ {v}, ¬ AllNonzero n v → c v = decide (v 0 ≠ 0) :=
    fun hv => by rw [hc]; exact if_neg hv
  refine ⟨c, ?_, ?_⟩
  · -- (I) no two orthogonal rays both colored 1
    intro v hv w hw horth
    rintro ⟨hcv, hcw⟩
    by_cases hAv : AllNonzero n v <;> by_cases hAw : AllNonzero n w
    · rw [hcA hAv] at hcv; rw [hcA hAw] at hcw
      exact allNonzero_sel_pair hn0 hω3 hω1 hsel_inv hsel_one hAv hAw horth hcv hcw
    · exact hAw (allNonzero_orth_imp h2 hAv hw horth)
    · exact hAv (allNonzero_orth_imp h2 hAw hv (Orthogonal_symm horth))
    · rw [hcN hAv, decide_eq_true_eq] at hcv
      rw [hcN hAw, decide_eq_true_eq] at hcw
      have hvz : v 0 = 0 ∨ v 1 = 0 ∨ v 2 = 0 := by
        by_contra hcon; push Not at hcon
        exact hAv ⟨hv, fun k => by fin_cases k; exacts [hcon.1, hcon.2.1, hcon.2.2]⟩
      rcases (orth_disjoint_of_zero h2 hv hw horth hvz).1 with h | h
      · exact hcv h
      · exact hcw h
  · -- (II) every triad has exactly one ray colored 1
    intro t ht
    rcases triad_homogeneous h2 ht with hN | hZ
    · -- all-nonzero triad: bridge to the `sel` transversal
      obtain ⟨a, b, d, hab, had, hbd, rfl⟩ := Finset.card_eq_three.mp ht.2.1
      have hAa : AllNonzero n a := hN a (by simp)
      have hAb : AllNonzero n b := hN b (by simp)
      have hAd : AllNonzero n d := hN d (by simp)
      have hbridge : ({a, b, d} : Finset (Fin 3 → ℂ)).filter (fun v => c v = true)
          = ({a, b, d} : Finset (Fin 3 → ℂ)).filter (fun v => sel v = true) := by
        apply Finset.filter_congr
        intro x hx
        simp only [Finset.mem_insert, Finset.mem_singleton] at hx
        rcases hx with rfl | rfl | rfl
        · rw [hcA hAa]
        · rw [hcA hAb]
        · rw [hcA hAd]
      rw [hbridge]
      exact allNonzero_sel_triad hn0 hωn hω3 hω1 hsel_inv hsel_one hAa hAb hAd hab had hbd
        (ht.2.2 a (by simp) b (by simp) hab) (ht.2.2 a (by simp) d (by simp) had)
        (ht.2.2 b (by simp) d (by simp) hbd)
    · -- zero-bearing triad: bridge to the Case 1 rule `v 0 ≠ 0`
      have hbridge : t.filter (fun v => c v = true) = t.filter (fun r => r 0 ≠ 0) := by
        apply Finset.filter_congr
        intro x hx
        have hnA : ¬ AllNonzero n x := by
          rcases hZ x hx with h | h | h
          · exact fun hA => hA.2 0 h
          · exact fun hA => hA.2 1 h
          · exact fun hA => hA.2 2 h
        rw [hcN hnA, decide_eq_true_eq]
      rw [hbridge]
      exact zerobearing_triad_card h2 ht hZ

/-! ### Case 2 (3 ∤ n, 2 ∣ n): perfect matching -/

/-- When `3 ∤ n`, no two all-nonzero rays are orthogonal: their inner product is a
    3-term sum of roots of unity, which vanishes only if `3 ∣ n` (`threeTerm_dvd`).
    Hence no triad of `Sₙ` contains an all-nonzero ray. -/
theorem allNonzero_not_orth {n : ℕ} (hn : n ≠ 0) (h3 : ¬ 3 ∣ n) {v w : Fin 3 → ℂ}
    (hv : AllNonzero n v) (hw : AllNonzero n w) (horth : Orthogonal v w) : False := by
  apply h3
  have hpow : ∀ k, ((starRingEnd ℂ) (v k) * w k) ^ n = 1 := fun k => by
    rw [mul_pow, ← map_pow, allNonzero_pow hv k, map_one, allNonzero_pow hw k, mul_one]
  have hsum : (starRingEnd ℂ) (v 0) * w 0 + (starRingEnd ℂ) (v 1) * w 1
      + (starRingEnd ℂ) (v 2) * w 2 = 0 := by
    have h := horth; unfold Orthogonal inner3 at h; rwa [Fin.sum_univ_three] at h
  exact threeTerm_dvd hn (hpow 0) (hpow 1) (hpow 2) hsum

/-! #### Perfect-matching transversal (ℤ/2 negation)

In each coordinate plane, two one-zero rays are orthogonal iff their ratios are
negatives (`a' = -a`, using `-1 = ζ^{n/2}` for even `n`).  A transversal of the
negation action picks one ray of each matched pair. -/

/-- The ℤ/2 negation orbit relation on `ℂ`. -/
def negRel (a b : ℂ) : Prop := b = a ∨ b = -a

theorem negRel_equiv : Equivalence negRel := by
  refine ⟨fun a => Or.inl rfl, ?_, ?_⟩
  · rintro a b (rfl | rfl)
    · exact Or.inl rfl
    · exact Or.inr (by ring)
  · rintro a b c (rfl | rfl) (rfl | rfl)
    · exact Or.inl rfl
    · exact Or.inr rfl
    · exact Or.inr rfl
    · exact Or.inl (by ring)

/-- **Matching transversal.**  A `Bool` selector on `ℂ` choosing exactly one of each
    `{a, -a}` pair (for `a ≠ 0`).  Built as a transversal of the negation orbit
    quotient via `Quotient.out`. -/
theorem exists_match_selector :
    ∃ sel : ℂ → Bool, ∀ a : ℂ, a ≠ 0 →
      (sel a = true ∧ sel (-a) = false) ∨ (sel a = false ∧ sel (-a) = true) := by
  classical
  letI s : Setoid ℂ := ⟨negRel, negRel_equiv⟩
  set rep : ℂ → ℂ := fun a => (Quotient.mk s a).out with hrep
  have rep_mem : ∀ a, negRel a (rep a) := fun a =>
    negRel_equiv.symm (Quotient.exact (Quotient.out_eq (Quotient.mk s a)))
  have rep_eq : ∀ {a b : ℂ}, negRel a b → rep a = rep b := fun {a b} h => by
    simp only [hrep]; rw [Quotient.sound h]
  refine ⟨fun a => decide (a = rep a), ?_⟩
  intro a ha
  have hne : a ≠ -a := fun h => ha (by linear_combination h / 2)
  have hrn : rep (-a) = rep a := rep_eq (show negRel (-a) a from Or.inr (by ring))
  rcases rep_mem a with hr | hr
  · exact Or.inl ⟨by show decide (a = rep a) = true; rw [hr, decide_eq_true_eq],
      by show decide (-a = rep (-a)) = false
         rw [hrn, hr]; exact decide_eq_false_iff_not.mpr (fun h => hne h.symm)⟩
  · exact Or.inr ⟨by show decide (a = rep a) = false
                     rw [hr]; exact decide_eq_false_iff_not.mpr hne,
      by show decide (-a = rep (-a)) = true; rw [hrn, hr, decide_eq_true_eq]⟩

/-! #### Triad classification (Case 2) -/

/-- A ray orthogonal to an all-nonzero ray has at most one zero coordinate: two
    zeros at distinct `p ≠ k` would leave a single inner-product term
    `conj(aₘ)·bₘ`, forcing `bₘ = 0` and hence `b = 0`. -/
theorem allN_orth_two_zeros {n : ℕ} {a b : Fin 3 → ℂ} (haN : AllNonzero n a)
    (hbne : b ≠ 0) (hab : Orthogonal a b) {p k : Fin 3} (hpk : p ≠ k)
    (hp : b p = 0) (hk : b k = 0) : False := by
  have hconj : ∀ m, (starRingEnd ℂ) (a m) ≠ 0 := fun m => by
    rw [starRingEnd_apply]; exact star_ne_zero.mpr (haN.2 m)
  have hsum := hab
  unfold Orthogonal inner3 at hsum
  rw [Fin.sum_univ_three] at hsum
  have close : b 0 = 0 → b 1 = 0 → b 2 = 0 → False := fun e0 e1 e2 =>
    hbne (funext fun m => by fin_cases m <;> [exact e0; exact e1; exact e2])
  fin_cases p <;> fin_cases k <;>
    first
      | exact absurd rfl hpk
      | (rw [show b 0 = 0 from hp, show b 1 = 0 from hk] at hsum
         simp only [mul_zero, zero_add, add_zero] at hsum
         exact close hp hk ((mul_eq_zero.mp hsum).resolve_left (hconj _)))
      | (rw [show b 0 = 0 from hp, show b 2 = 0 from hk] at hsum
         simp only [mul_zero, zero_add, add_zero] at hsum
         exact close hp ((mul_eq_zero.mp hsum).resolve_left (hconj _)) hk)
      | (rw [show b 1 = 0 from hp, show b 0 = 0 from hk] at hsum
         simp only [mul_zero, zero_add, add_zero] at hsum
         exact close hk hp ((mul_eq_zero.mp hsum).resolve_left (hconj _)))
      | (rw [show b 1 = 0 from hp, show b 2 = 0 from hk] at hsum
         simp only [mul_zero, zero_add, add_zero] at hsum
         exact close ((mul_eq_zero.mp hsum).resolve_left (hconj _)) hp hk)
      | (rw [show b 2 = 0 from hp, show b 0 = 0 from hk] at hsum
         simp only [mul_zero, zero_add, add_zero] at hsum
         exact close hk ((mul_eq_zero.mp hsum).resolve_left (hconj _)) hp)
      | (rw [show b 2 = 0 from hp, show b 1 = 0 from hk] at hsum
         simp only [mul_zero, zero_add, add_zero] at hsum
         exact close ((mul_eq_zero.mp hsum).resolve_left (hconj _)) hk hp)

/-! #### Case 2 — no AllNonzero ray in any triad -/

/-- Under `3 ∤ n`, a ray `b ∈ Sₙ` orthogonal to an `AllNonzero` ray `a` has
    a unique zero coordinate: at least one (since `b` is not AllNonzero —
    otherwise `allNonzero_not_orth` would apply, which is invoked at the call
    site), and at most one (`allN_orth_two_zeros`). -/
theorem orth_allN_uniqueZero {n : ℕ} {a b : Fin 3 → ℂ}
    (haN : AllNonzero n a) (hbS : b ∈ S n) (hbN : ¬ AllNonzero n b)
    (hab : Orthogonal a b) :
    ∃ k : Fin 3, b k = 0 ∧ ∀ k' : Fin 3, k' ≠ k → b k' ≠ 0 := by
  classical
  have hex : ∃ k, b k = 0 := by
    by_contra h
    push Not at h
    exact hbN ⟨hbS, h⟩
  obtain ⟨k, hk⟩ := hex
  exact ⟨k, hk, fun k' hkk' hk'eq =>
    allN_orth_two_zeros haN hbS.1 hab hkk' hk'eq hk⟩

/-- **Off-diagonal Case-2 contradiction.**  If two rays of `Sₙ` have *different*
    unique zero coordinates `kb ≠ kd`, their inner product reduces to a single
    nonzero root-of-unity term at the third coordinate, so they cannot be
    orthogonal. -/
private theorem case2_off_diag_absurd {b d : Fin 3 → ℂ}
    (hbd : Orthogonal b d)
    {kb kd : Fin 3}
    (hbk : b kb = 0) (hbk' : ∀ k' : Fin 3, k' ≠ kb → b k' ≠ 0)
    (hdk : d kd = 0) (hdk' : ∀ k' : Fin 3, k' ≠ kd → d k' ≠ 0)
    (hkbd : kb ≠ kd) : False := by
  have ipbd : (starRingEnd ℂ) (b 0) * d 0 + (starRingEnd ℂ) (b 1) * d 1 +
              (starRingEnd ℂ) (b 2) * d 2 = 0 := by
    have h := hbd; unfold Orthogonal inner3 at h; rwa [Fin.sum_univ_three] at h
  -- A small helper closing each off-diagonal branch given the surviving coord `m`.
  -- After substituting `b kb = 0` and `d kd = 0`, only the `m`-term survives in
  -- `ipbd`, giving `conj(b m) * d m = 0` — contradicting both factors nonzero.
  fin_cases kb <;> fin_cases kd
  · exact absurd rfl hkbd                                                  -- (0, 0)
  · -- (0, 1): m = 2
    rw [show b 0 = 0 from hbk, show d 1 = 0 from hdk] at ipbd
    simp only [mul_zero, map_zero, zero_mul, zero_add, add_zero] at ipbd
    exact (mul_ne_zero
      (by rw [starRingEnd_apply]; exact star_ne_zero.mpr (hbk' 2 (by decide)))
      (hdk' 2 (by decide))) ipbd
  · -- (0, 2): m = 1
    rw [show b 0 = 0 from hbk, show d 2 = 0 from hdk] at ipbd
    simp only [mul_zero, map_zero, zero_mul, zero_add, add_zero] at ipbd
    exact (mul_ne_zero
      (by rw [starRingEnd_apply]; exact star_ne_zero.mpr (hbk' 1 (by decide)))
      (hdk' 1 (by decide))) ipbd
  · -- (1, 0): m = 2
    rw [show b 1 = 0 from hbk, show d 0 = 0 from hdk] at ipbd
    simp only [mul_zero, map_zero, zero_mul, zero_add, add_zero] at ipbd
    exact (mul_ne_zero
      (by rw [starRingEnd_apply]; exact star_ne_zero.mpr (hbk' 2 (by decide)))
      (hdk' 2 (by decide))) ipbd
  · exact absurd rfl hkbd                                                  -- (1, 1)
  · -- (1, 2): m = 0
    rw [show b 1 = 0 from hbk, show d 2 = 0 from hdk] at ipbd
    simp only [mul_zero, map_zero, zero_mul, zero_add, add_zero] at ipbd
    exact (mul_ne_zero
      (by rw [starRingEnd_apply]; exact star_ne_zero.mpr (hbk' 0 (by decide)))
      (hdk' 0 (by decide))) ipbd
  · -- (2, 0): m = 1
    rw [show b 2 = 0 from hbk, show d 0 = 0 from hdk] at ipbd
    simp only [mul_zero, map_zero, zero_mul, zero_add, add_zero] at ipbd
    exact (mul_ne_zero
      (by rw [starRingEnd_apply]; exact star_ne_zero.mpr (hbk' 1 (by decide)))
      (hdk' 1 (by decide))) ipbd
  · -- (2, 1): m = 0
    rw [show b 2 = 0 from hbk, show d 1 = 0 from hdk] at ipbd
    simp only [mul_zero, map_zero, zero_mul, zero_add, add_zero] at ipbd
    exact (mul_ne_zero
      (by rw [starRingEnd_apply]; exact star_ne_zero.mpr (hbk' 0 (by decide)))
      (hdk' 0 (by decide))) ipbd
  · exact absurd rfl hkbd                                                  -- (2, 2)

/-- **Case 2 — no AllNonzero ray in any triad.**  Under `2 ∣ n`, `3 ∤ n`,
    every triad of `Sₙ` consists entirely of zero-bearing rays.

    Proof sketch: suppose `a ∈ t` is AllNonzero, with other triad members
    `b`, `d`.  `allNonzero_not_orth` (under `3 ∤ n`) rules out `b`, `d`
    being AllNonzero; `allN_orth_two_zeros` bounds each below at one zero
    coord; so each has *exactly* one zero coord (`orth_allN_uniqueZero`).
    * `kb ≠ kd` (`case2_off_diag_absurd`): the `b ⊥ d` inner product reduces
      to a single nonzero root-of-unity term — contradiction.
    * `kb = kd = k`: the three orthogonalities `a ⊥ b`, `a ⊥ d`, `b ⊥ d` in
      the orthogonal plane combine under root-of-unity unitarity to force
      `2 · a_{k₁} · b_{k₁} · d_{k₂} = 0`, contradicting nonzero entries. -/
theorem case2_no_allNonzero_in_triad {n : ℕ} (hn : n ≠ 0) (h3 : ¬ 3 ∣ n)
    {t : Finset (Fin 3 → ℂ)} (ht : IsTriad (S n) t) :
    ∀ r ∈ t, ¬ AllNonzero n r := by
  classical
  -- Reduce to a sub-lemma on three named rays.
  suffices key : ∀ a b d : Fin 3 → ℂ, AllNonzero n a → b ∈ S n → d ∈ S n →
      Orthogonal a b → Orthogonal a d → Orthogonal b d → False by
    intro r hr hrN
    obtain ⟨x, y, z, hxy, hxz, hyz, hteq⟩ := Finset.card_eq_three.mp ht.2.1
    have hxS : x ∈ S n := ht.1 (by rw [hteq]; simp)
    have hyS : y ∈ S n := ht.1 (by rw [hteq]; simp)
    have hzS : z ∈ S n := ht.1 (by rw [hteq]; simp)
    have hxy_o : Orthogonal x y := ht.2.2 _ (by rw [hteq]; simp) _ (by rw [hteq]; simp) hxy
    have hxz_o : Orthogonal x z := ht.2.2 _ (by rw [hteq]; simp) _ (by rw [hteq]; simp) hxz
    have hyz_o : Orthogonal y z := ht.2.2 _ (by rw [hteq]; simp) _ (by rw [hteq]; simp) hyz
    rw [hteq] at hr
    simp only [Finset.mem_insert, Finset.mem_singleton] at hr
    rcases hr with rfl | rfl | rfl
    · exact key r y z hrN hyS hzS hxy_o hxz_o hyz_o
    · exact key r x z hrN hxS hzS (Orthogonal_symm hxy_o) hyz_o hxz_o
    · exact key r x y hrN hxS hyS (Orthogonal_symm hxz_o) (Orthogonal_symm hyz_o) hxy_o
  -- Sub-lemma.
  intro a b d haN hbS hdS hab had hbd
  have hbN : ¬ AllNonzero n b := fun hbN' => allNonzero_not_orth hn h3 haN hbN' hab
  have hdN : ¬ AllNonzero n d := fun hdN' => allNonzero_not_orth hn h3 haN hdN' had
  obtain ⟨kb, hbk, hbk'⟩ := orth_allN_uniqueZero haN hbS hbN hab
  obtain ⟨kd, hdk, hdk'⟩ := orth_allN_uniqueZero haN hdS hdN had
  -- Split on whether the unique zero coords agree.
  by_cases hkbd : kb = kd
  · -- Same-zero-coord case: derive `2 · (product of nonzero terms) = 0`.
    subst hkbd
    have apow : ∀ j, (a j) ^ n = 1 := fun j => (haN.1.2 j).resolve_left (haN.2 j)
    have ca : ∀ j, a j * (starRingEnd ℂ) (a j) = 1 := fun j =>
      mul_conj_eq_one_of_pow hn (apow j)
    have cb : ∀ j, j ≠ kb → b j * (starRingEnd ℂ) (b j) = 1 := fun j hj =>
      mul_conj_eq_one_of_pow hn ((hbS.2 j).resolve_left (hbk' j hj))
    have ipab : (starRingEnd ℂ) (a 0) * b 0 + (starRingEnd ℂ) (a 1) * b 1 +
                (starRingEnd ℂ) (a 2) * b 2 = 0 := by
      have h := hab; unfold Orthogonal inner3 at h; rwa [Fin.sum_univ_three] at h
    have ipad : (starRingEnd ℂ) (a 0) * d 0 + (starRingEnd ℂ) (a 1) * d 1 +
                (starRingEnd ℂ) (a 2) * d 2 = 0 := by
      have h := had; unfold Orthogonal inner3 at h; rwa [Fin.sum_univ_three] at h
    have ipbd : (starRingEnd ℂ) (b 0) * d 0 + (starRingEnd ℂ) (b 1) * d 1 +
                (starRingEnd ℂ) (b 2) * d 2 = 0 := by
      have h := hbd; unfold Orthogonal inner3 at h; rwa [Fin.sum_univ_three] at h
    have h2c : (2 : ℂ) ≠ 0 := by norm_num
    fin_cases kb
    · -- k = 0; non-zero coords (k₁, k₂) = (1, 2)
      have hb1 := hbk' 1 (by decide)
      have hd2 := hdk' 2 (by decide)
      have ca2 := ca 2
      have cb1 := cb 1 (by decide); have cb2 := cb 2 (by decide)
      rw [show b 0 = 0 from hbk] at ipab ipbd
      rw [show d 0 = 0 from hdk] at ipad ipbd
      simp only [mul_zero, map_zero, zero_mul, zero_add, add_zero] at ipab ipad ipbd
      have key : (2 : ℂ) * (a 1 * b 1 * d 2) = 0 := by
        linear_combination
          (- a 1 * a 2 * d 1) * ipab + (a 1 * a 2 * b 1) * ipad
          + (a 1 * b 1 * b 2) * ipbd
          + (a 1 * b 2 * d 1 - a 1 * b 1 * d 2) * ca2
          + (- a 1 * b 2 * d 1) * cb1 + (- a 1 * b 1 * d 2) * cb2
      rcases mul_eq_zero.mp key with h | h
      · exact h2c h
      · rcases mul_eq_zero.mp h with h | h
        · rcases mul_eq_zero.mp h with h | h
          · exact (haN.2 1) h
          · exact hb1 h
        · exact hd2 h
    · -- k = 1; non-zero coords (k₁, k₂) = (0, 2)
      have hb0 := hbk' 0 (by decide)
      have hd2 := hdk' 2 (by decide)
      have ca2 := ca 2
      have cb0 := cb 0 (by decide); have cb2 := cb 2 (by decide)
      rw [show b 1 = 0 from hbk] at ipab ipbd
      rw [show d 1 = 0 from hdk] at ipad ipbd
      simp only [mul_zero, map_zero, zero_mul, zero_add, add_zero] at ipab ipad ipbd
      have key : (2 : ℂ) * (a 0 * b 0 * d 2) = 0 := by
        linear_combination
          (- a 0 * a 2 * d 0) * ipab + (a 0 * a 2 * b 0) * ipad
          + (a 0 * b 0 * b 2) * ipbd
          + (a 0 * b 2 * d 0 - a 0 * b 0 * d 2) * ca2
          + (- a 0 * b 2 * d 0) * cb0 + (- a 0 * b 0 * d 2) * cb2
      rcases mul_eq_zero.mp key with h | h
      · exact h2c h
      · rcases mul_eq_zero.mp h with h | h
        · rcases mul_eq_zero.mp h with h | h
          · exact (haN.2 0) h
          · exact hb0 h
        · exact hd2 h
    · -- k = 2; non-zero coords (k₁, k₂) = (0, 1)
      have hb0 := hbk' 0 (by decide)
      have hd1 := hdk' 1 (by decide)
      have ca1 := ca 1
      have cb0 := cb 0 (by decide); have cb1 := cb 1 (by decide)
      rw [show b 2 = 0 from hbk] at ipab ipbd
      rw [show d 2 = 0 from hdk] at ipad ipbd
      simp only [mul_zero, map_zero, zero_mul, zero_add, add_zero] at ipab ipad ipbd
      have key : (2 : ℂ) * (a 0 * b 0 * d 1) = 0 := by
        linear_combination
          (- a 0 * a 1 * d 0) * ipab + (a 0 * a 1 * b 0) * ipad
          + (a 0 * b 0 * b 1) * ipbd
          + (a 0 * b 1 * d 0 - a 0 * b 0 * d 1) * ca1
          + (- a 0 * b 1 * d 0) * cb0 + (- a 0 * b 0 * d 1) * cb1
      rcases mul_eq_zero.mp key with h | h
      · exact h2c h
      · rcases mul_eq_zero.mp h with h | h
        · rcases mul_eq_zero.mp h with h | h
          · exact (haN.2 0) h
          · exact hb0 h
        · exact hd1 h
  · -- Different-zero-coord case: delegate to the off-diagonal helper.
    exact case2_off_diag_absurd hbd hbk hbk' hdk hdk' hkbd

/-! #### Case 2 — axis-0 ray dominates -/

/-- If a triad `t` of `Sₙ` contains a ray `w` with `w 1 = w 2 = 0` — necessarily
    a Case-2 axis-0 ray (`w 0 ≠ 0` since `w ≠ 0`) — then every other triad
    member has `v 0 = 0`.  Reason: each is orthogonal to `w`, but `w`'s inner
    product is just `conj(w 0) · v 0 = 0`, forcing `v 0 = 0`. -/
theorem case2_axis0_dominates {n : ℕ}
    {t : Finset (Fin 3 → ℂ)} (ht : IsTriad (S n) t)
    {w : Fin 3 → ℂ} (hw : w ∈ t) (hw1 : w 1 = 0) (hw2 : w 2 = 0) :
    ∀ v ∈ t, v ≠ w → v 0 = 0 := by
  intro v hv hvw
  have hwS : w ∈ S n := ht.1 (Finset.mem_coe.mpr hw)
  have hw0 : w 0 ≠ 0 := by
    intro h
    apply hwS.1
    funext k; fin_cases k <;> simp_all
  have horth : Orthogonal w v := ht.2.2 _ hw _ hv (Ne.symm hvw)
  have hsum : (starRingEnd ℂ) (w 0) * v 0 + (starRingEnd ℂ) (w 1) * v 1 +
              (starRingEnd ℂ) (w 2) * v 2 = 0 := by
    have h := horth; unfold Orthogonal inner3 at h; rwa [Fin.sum_univ_three] at h
  rw [hw1, hw2] at hsum
  simp only [map_zero, mul_zero, zero_mul, add_zero, zero_add] at hsum
  have hconj_ne : (starRingEnd ℂ) (w 0) ≠ 0 := by
    rw [starRingEnd_apply]; exact star_ne_zero.mpr hw0
  exact (mul_eq_zero.mp hsum).resolve_left hconj_ne

/-! #### Case 2 — no axis-0 ray ⇒ matched pair structure (IN PROGRESS) -/

/-- **(T,T,T) sub-claim.**  Three pairwise-orthogonal nonzero rays of `Sₙ`
    that all have `v 0 = 0` cannot exist — they would form an orthogonal
    triple inside `e₀⊥`, but only two orthogonal nonzero vectors fit in a
    2-D space.  Case-analyzed by `x`'s support (`{1}`, `{2}`, or `{1, 2}`):
    the size-1 cases force `y, z` onto a single axis where their inner
    product can't vanish; the size-2 case reduces to the same
    `2 · x_{1} · y_{1} · z_{2} = 0` rigidity identity as `case2_no_allNonzero_in_triad`. -/
private theorem case2_three_orth_e0_perp_absurd {n : ℕ} (hn : n ≠ 0)
    {x y z : Fin 3 → ℂ} (hxS : x ∈ S n) (hyS : y ∈ S n) (hzS : z ∈ S n)
    (hxy : Orthogonal x y) (hxz : Orthogonal x z) (hyz : Orthogonal y z)
    (hx0 : x 0 = 0) (hy0 : y 0 = 0) (hz0 : z 0 = 0) : False := by
  classical
  have ipxy : (starRingEnd ℂ) (x 0) * y 0 + (starRingEnd ℂ) (x 1) * y 1 +
              (starRingEnd ℂ) (x 2) * y 2 = 0 := by
    have h := hxy; unfold Orthogonal inner3 at h; rwa [Fin.sum_univ_three] at h
  have ipxz : (starRingEnd ℂ) (x 0) * z 0 + (starRingEnd ℂ) (x 1) * z 1 +
              (starRingEnd ℂ) (x 2) * z 2 = 0 := by
    have h := hxz; unfold Orthogonal inner3 at h; rwa [Fin.sum_univ_three] at h
  have ipyz : (starRingEnd ℂ) (y 0) * z 0 + (starRingEnd ℂ) (y 1) * z 1 +
              (starRingEnd ℂ) (y 2) * z 2 = 0 := by
    have h := hyz; unfold Orthogonal inner3 at h; rwa [Fin.sum_univ_three] at h
  rw [hx0, hy0] at ipxy
  rw [hx0, hz0] at ipxz
  rw [hy0, hz0] at ipyz
  simp only [map_zero, zero_mul, add_zero, zero_add] at ipxy ipxz ipyz
  -- After cleaning:
  --   ipxy : conj(x 1)*y 1 + conj(x 2)*y 2 = 0
  --   ipxz : conj(x 1)*z 1 + conj(x 2)*z 2 = 0
  --   ipyz : conj(y 1)*z 1 + conj(y 2)*z 2 = 0
  by_cases hx1 : x 1 = 0
  · by_cases hx2 : x 2 = 0
    · -- x has supp = ∅, but x ≠ 0
      exact hxS.1 (funext fun k => by fin_cases k <;> simp_all)
    · -- supp x = {2}: x 1 = 0, x 2 ≠ 0
      rw [hx1] at ipxy; rw [hx1] at ipxz
      simp only [map_zero, zero_mul, zero_add] at ipxy ipxz
      have hconj_x2 : (starRingEnd ℂ) (x 2) ≠ 0 := by
        rw [starRingEnd_apply]; exact star_ne_zero.mpr hx2
      have hy2 : y 2 = 0 := (mul_eq_zero.mp ipxy).resolve_left hconj_x2
      have hz2 : z 2 = 0 := (mul_eq_zero.mp ipxz).resolve_left hconj_x2
      have hy1ne : y 1 ≠ 0 := fun h => hyS.1 (funext fun k => by fin_cases k <;> simp_all)
      have hz1ne : z 1 ≠ 0 := fun h => hzS.1 (funext fun k => by fin_cases k <;> simp_all)
      rw [hy2, hz2] at ipyz
      simp only [map_zero, zero_mul, mul_zero, add_zero] at ipyz
      have hconj_y1 : (starRingEnd ℂ) (y 1) ≠ 0 := by
        rw [starRingEnd_apply]; exact star_ne_zero.mpr hy1ne
      exact hz1ne ((mul_eq_zero.mp ipyz).resolve_left hconj_y1)
  · by_cases hx2 : x 2 = 0
    · -- supp x = {1}: symmetric to the previous case
      rw [hx2] at ipxy; rw [hx2] at ipxz
      simp only [map_zero, zero_mul, add_zero] at ipxy ipxz
      have hconj_x1 : (starRingEnd ℂ) (x 1) ≠ 0 := by
        rw [starRingEnd_apply]; exact star_ne_zero.mpr hx1
      have hy1z : y 1 = 0 := (mul_eq_zero.mp ipxy).resolve_left hconj_x1
      have hz1z : z 1 = 0 := (mul_eq_zero.mp ipxz).resolve_left hconj_x1
      have hy2ne : y 2 ≠ 0 := fun h => hyS.1 (funext fun k => by fin_cases k <;> simp_all)
      have hz2ne : z 2 ≠ 0 := fun h => hzS.1 (funext fun k => by fin_cases k <;> simp_all)
      rw [hy1z, hz1z] at ipyz
      simp only [map_zero, zero_mul, mul_zero, zero_add] at ipyz
      have hconj_y2 : (starRingEnd ℂ) (y 2) ≠ 0 := by
        rw [starRingEnd_apply]; exact star_ne_zero.mpr hy2ne
      exact hz2ne ((mul_eq_zero.mp ipyz).resolve_left hconj_y2)
    · -- supp x = {1, 2}: x 1 ≠ 0, x 2 ≠ 0.  Apply the diagonal rigidity argument.
      have hconj_x1 : (starRingEnd ℂ) (x 1) ≠ 0 := by
        rw [starRingEnd_apply]; exact star_ne_zero.mpr hx1
      have hconj_x2 : (starRingEnd ℂ) (x 2) ≠ 0 := by
        rw [starRingEnd_apply]; exact star_ne_zero.mpr hx2
      -- y must have supp = {1, 2} (else x ⊥ y collapses)
      have hy1ne : y 1 ≠ 0 := by
        intro hy1z
        rw [hy1z] at ipxy
        simp only [mul_zero, zero_add] at ipxy
        have hy2z : y 2 = 0 := (mul_eq_zero.mp ipxy).resolve_left hconj_x2
        exact hyS.1 (funext fun k => by fin_cases k <;> simp_all)
      have hy2ne : y 2 ≠ 0 := by
        intro hy2z
        rw [hy2z] at ipxy
        simp only [mul_zero, add_zero] at ipxy
        have hy1z : y 1 = 0 := (mul_eq_zero.mp ipxy).resolve_left hconj_x1
        exact hyS.1 (funext fun k => by fin_cases k <;> simp_all)
      have hz1ne : z 1 ≠ 0 := by
        intro hz1z
        rw [hz1z] at ipxz
        simp only [mul_zero, zero_add] at ipxz
        have hz2z : z 2 = 0 := (mul_eq_zero.mp ipxz).resolve_left hconj_x2
        exact hzS.1 (funext fun k => by fin_cases k <;> simp_all)
      have hz2ne : z 2 ≠ 0 := by
        intro hz2z
        rw [hz2z] at ipxz
        simp only [mul_zero, add_zero] at ipxz
        have hz1z : z 1 = 0 := (mul_eq_zero.mp ipxz).resolve_left hconj_x1
        exact hzS.1 (funext fun k => by fin_cases k <;> simp_all)
      -- Now x, y all have supp = {1, 2}; the rigidity identity closes the case.
      have apow1 : (x 1) ^ n = 1 := (hxS.2 1).resolve_left hx1
      have apow2 : (x 2) ^ n = 1 := (hxS.2 2).resolve_left hx2
      have cx1 : x 1 * (starRingEnd ℂ) (x 1) = 1 := mul_conj_eq_one_of_pow hn apow1
      have cx2 : x 2 * (starRingEnd ℂ) (x 2) = 1 := mul_conj_eq_one_of_pow hn apow2
      have ypow1 : (y 1) ^ n = 1 := (hyS.2 1).resolve_left hy1ne
      have ypow2 : (y 2) ^ n = 1 := (hyS.2 2).resolve_left hy2ne
      have cy1 : y 1 * (starRingEnd ℂ) (y 1) = 1 := mul_conj_eq_one_of_pow hn ypow1
      have cy2 : y 2 * (starRingEnd ℂ) (y 2) = 1 := mul_conj_eq_one_of_pow hn ypow2
      have key : (2 : ℂ) * (x 1 * y 1 * z 2) = 0 := by
        linear_combination
          (- x 1 * x 2 * z 1) * ipxy + (x 1 * x 2 * y 1) * ipxz
          + (x 1 * y 1 * y 2) * ipyz
          + (x 1 * y 2 * z 1 - x 1 * y 1 * z 2) * cx2
          + (- x 1 * y 2 * z 1) * cy1 + (- x 1 * y 1 * z 2) * cy2
      have h2c : (2 : ℂ) ≠ 0 := by norm_num
      rcases mul_eq_zero.mp key with h | h
      · exact h2c h
      · rcases mul_eq_zero.mp h with h | h
        · rcases mul_eq_zero.mp h with h | h
          · exact hx1 h
          · exact hy1ne h
        · exact hz2ne h

/-- **Cross-plane non-orthogonality.**  If `a` has `a 1 = 0` (support ⊆ `{0, 2}`,
    with `a 0 ≠ 0`) and `b` has `b 2 = 0` (support ⊆ `{0, 1}`, with `b 0 ≠ 0`),
    then `a` and `b` cannot be orthogonal: their inner product reduces to
    `conj(a 0) · b 0`, a product of two nonzero values. -/
private theorem case2_cross_plane_absurd {a b : Fin 3 → ℂ}
    (ha0 : a 0 ≠ 0) (hb0 : b 0 ≠ 0)
    (ha1z : a 1 = 0) (hb2z : b 2 = 0)
    (horth : Orthogonal a b) : False := by
  have ipab : (starRingEnd ℂ) (a 0) * b 0 + (starRingEnd ℂ) (a 1) * b 1 +
              (starRingEnd ℂ) (a 2) * b 2 = 0 := by
    have h := horth; unfold Orthogonal inner3 at h; rwa [Fin.sum_univ_three] at h
  rw [ha1z, hb2z] at ipab
  simp only [map_zero, zero_mul, mul_zero, add_zero] at ipab
  exact mul_ne_zero
    (by rw [starRingEnd_apply]; exact star_ne_zero.mpr ha0) hb0 ipab

/-- **Lone-`v 0 ≠ 0`-ray forced to axis-0.**  If `u, v ∈ Sₙ` are pairwise
    orthogonal nonzero rays both with `_ 0 = 0` (so both lie in `e₀⊥`), and
    `r ∈ Sₙ` is orthogonal to both with `r 0 ≠ 0`, then `r 1 = r 2 = 0`
    (i.e., `r` is axis-0).

    Used in the (T,T,F)/(T,F,T)/(F,T,T) sub-cases of
    `case2_no_axis0_v0_count` to derive a contradiction with the no-axis-0
    hypothesis.

    Proof sketch: `u` and `v` together span `e₀⊥` (a 2-D subspace of `ℂ³`);
    any vector orthogonal to both is in `(e₀⊥)⊥ = span e₀`, hence axis-0.
    Formalized by case-analyzing `supp u`, `supp v` (each `⊆ {1,2}`,
    nonempty, of size 1 or 2 — and not both size 1 at the same axis, by
    `u ⊥ v`).  The size-2/size-2 sub-case uses the same rigidity
    `linear_combination` as `case2_three_orth_e0_perp_absurd`. -/
private theorem case2_lone_v0_force_axis0 {n : ℕ} (hn : n ≠ 0)
    {r u v : Fin 3 → ℂ} (hrS : r ∈ S n) (huS : u ∈ S n) (hvS : v ∈ S n)
    (hur : Orthogonal u r) (hvr : Orthogonal v r) (huv : Orthogonal u v)
    (hu0 : u 0 = 0) (hv0 : v 0 = 0) (hr0 : r 0 ≠ 0) :
    r 1 = 0 ∧ r 2 = 0 := by
  classical
  -- Inner products
  have ipur : (starRingEnd ℂ) (u 0) * r 0 + (starRingEnd ℂ) (u 1) * r 1 +
              (starRingEnd ℂ) (u 2) * r 2 = 0 := by
    have h := hur; unfold Orthogonal inner3 at h; rwa [Fin.sum_univ_three] at h
  have ipvr : (starRingEnd ℂ) (v 0) * r 0 + (starRingEnd ℂ) (v 1) * r 1 +
              (starRingEnd ℂ) (v 2) * r 2 = 0 := by
    have h := hvr; unfold Orthogonal inner3 at h; rwa [Fin.sum_univ_three] at h
  have ipuv : (starRingEnd ℂ) (u 0) * v 0 + (starRingEnd ℂ) (u 1) * v 1 +
              (starRingEnd ℂ) (u 2) * v 2 = 0 := by
    have h := huv; unfold Orthogonal inner3 at h; rwa [Fin.sum_univ_three] at h
  rw [hu0] at ipur ipuv
  rw [hv0] at ipvr ipuv
  simp only [map_zero, zero_mul, zero_add] at ipur ipvr ipuv
  -- ipur : conj(u 1)*r 1 + conj(u 2)*r 2 = 0
  -- ipvr : conj(v 1)*r 1 + conj(v 2)*r 2 = 0
  -- ipuv : conj(u 1)*v 1 + conj(u 2)*v 2 = 0
  -- Case-split on u's support in {1, 2}
  by_cases hu1z : u 1 = 0
  · -- supp u ⊆ {2}; nonzero ⇒ u 2 ≠ 0
    have hu2ne : u 2 ≠ 0 := by
      intro h; exact huS.1 (funext fun k => by fin_cases k <;> simp_all)
    -- ipur: conj(u 2)*r 2 = 0 ⇒ r 2 = 0
    rw [hu1z] at ipur ipuv
    simp only [map_zero, zero_mul, zero_add] at ipur ipuv
    have hconj_u2 : (starRingEnd ℂ) (u 2) ≠ 0 := by
      rw [starRingEnd_apply]; exact star_ne_zero.mpr hu2ne
    have hr2 : r 2 = 0 := (mul_eq_zero.mp ipur).resolve_left hconj_u2
    -- ipuv: conj(u 2)*v 2 = 0 ⇒ v 2 = 0
    have hv2z : v 2 = 0 := (mul_eq_zero.mp ipuv).resolve_left hconj_u2
    -- v 0 = v 2 = 0, v nonzero ⇒ v 1 ≠ 0
    have hv1ne : v 1 ≠ 0 := by
      intro h; exact hvS.1 (funext fun k => by fin_cases k <;> simp_all)
    -- ipvr: conj(v 1)*r 1 + conj(v 2)*r 2 = conj(v 1)*r 1 = 0 (since v 2 = 0)
    rw [hv2z] at ipvr
    simp only [map_zero, zero_mul, add_zero] at ipvr
    have hconj_v1 : (starRingEnd ℂ) (v 1) ≠ 0 := by
      rw [starRingEnd_apply]; exact star_ne_zero.mpr hv1ne
    have hr1 : r 1 = 0 := (mul_eq_zero.mp ipvr).resolve_left hconj_v1
    exact ⟨hr1, hr2⟩
  · -- u 1 ≠ 0
    by_cases hu2z : u 2 = 0
    · -- supp u = {1}: u = (0, u 1, 0)
      rw [hu2z] at ipur ipuv
      simp only [map_zero, zero_mul, add_zero] at ipur ipuv
      have hconj_u1 : (starRingEnd ℂ) (u 1) ≠ 0 := by
        rw [starRingEnd_apply]; exact star_ne_zero.mpr hu1z
      have hr1 : r 1 = 0 := (mul_eq_zero.mp ipur).resolve_left hconj_u1
      have hv1z : v 1 = 0 := (mul_eq_zero.mp ipuv).resolve_left hconj_u1
      have hv2ne : v 2 ≠ 0 := by
        intro h; exact hvS.1 (funext fun k => by fin_cases k <;> simp_all)
      rw [hv1z] at ipvr
      simp only [map_zero, zero_mul, zero_add] at ipvr
      have hconj_v2 : (starRingEnd ℂ) (v 2) ≠ 0 := by
        rw [starRingEnd_apply]; exact star_ne_zero.mpr hv2ne
      have hr2 : r 2 = 0 := (mul_eq_zero.mp ipvr).resolve_left hconj_v2
      exact ⟨hr1, hr2⟩
    · -- supp u = {1, 2}: both u 1, u 2 nonzero.  Need similar for v.
      -- From ipuv = conj(u 1)*v 1 + conj(u 2)*v 2 = 0 (2-term root sum form):
      -- if v 1 = 0: ipuv ⇒ conj(u 2)*v 2 = 0 ⇒ v 2 = 0 ⇒ v = 0, contradiction.
      -- if v 2 = 0: similarly contradiction.
      -- So v also has supp = {1, 2}.
      have hv1ne : v 1 ≠ 0 := by
        intro hv1z
        rw [hv1z] at ipuv
        simp only [mul_zero, zero_add] at ipuv
        have hconj_u2 : (starRingEnd ℂ) (u 2) ≠ 0 := by
          rw [starRingEnd_apply]; exact star_ne_zero.mpr hu2z
        have hv2z : v 2 = 0 := (mul_eq_zero.mp ipuv).resolve_left hconj_u2
        exact hvS.1 (funext fun k => by fin_cases k <;> simp_all)
      have hv2ne : v 2 ≠ 0 := by
        intro hv2z
        rw [hv2z] at ipuv
        simp only [mul_zero, add_zero] at ipuv
        have hconj_u1 : (starRingEnd ℂ) (u 1) ≠ 0 := by
          rw [starRingEnd_apply]; exact star_ne_zero.mpr hu1z
        have hv1z : v 1 = 0 := (mul_eq_zero.mp ipuv).resolve_left hconj_u1
        exact hvS.1 (funext fun k => by fin_cases k <;> simp_all)
      -- Now both u, v have supp = {1, 2}.  Use rigidity identities
      -- `2 · u 2 · v 1 · r 1 = 0` and `2 · u 2 · v 1 · r 2 = 0` derived via
      -- `linear_combination` from `ipur, ipvr, ipuv` + full `u, v` unitarity.
      have upow1 : (u 1) ^ n = 1 := (huS.2 1).resolve_left hu1z
      have upow2 : (u 2) ^ n = 1 := (huS.2 2).resolve_left hu2z
      have cu1 : u 1 * (starRingEnd ℂ) (u 1) = 1 := mul_conj_eq_one_of_pow hn upow1
      have cu2 : u 2 * (starRingEnd ℂ) (u 2) = 1 := mul_conj_eq_one_of_pow hn upow2
      have vpow1 : (v 1) ^ n = 1 := (hvS.2 1).resolve_left hv1ne
      have vpow2 : (v 2) ^ n = 1 := (hvS.2 2).resolve_left hv2ne
      have cv1 : v 1 * (starRingEnd ℂ) (v 1) = 1 := mul_conj_eq_one_of_pow hn vpow1
      have cv2 : v 2 * (starRingEnd ℂ) (v 2) = 1 := mul_conj_eq_one_of_pow hn vpow2
      have h2c : (2 : ℂ) ≠ 0 := by norm_num
      have key1 : (2 : ℂ) * (u 2 * v 1 * r 1) = 0 := by
        linear_combination
          (v 1 * u 1 * u 2) * ipur + (- u 1 * v 1 * v 2) * ipvr
          + (r 1 * u 1 * u 2) * ipuv
          + (- 2 * v 1 * r 1 * u 2) * cu1
          + (- u 1 * (v 1 * r 2 + r 1 * v 2)) * cu2
          + (u 1 * r 1 * v 2) * cv1 + (u 1 * r 2 * v 1) * cv2
      have hr1 : r 1 = 0 := by
        rcases mul_eq_zero.mp key1 with h | h
        · exact absurd h h2c
        · rcases mul_eq_zero.mp h with h | h
          · rcases mul_eq_zero.mp h with h | h
            · exact absurd h hu2z
            · exact absurd h hv1ne
          · exact h
      have key2 : (2 : ℂ) * (u 2 * v 1 * r 2) = 0 := by
        linear_combination
          (- v 2 * u 1 * u 2) * ipur + (u 2 * v 1 * v 2) * ipvr
          + (r 2 * u 1 * u 2) * ipuv
          + (u 2 * (v 2 * r 1 - r 2 * v 1)) * cu1
          + (- u 2 * r 1 * v 2) * cv1 + (- u 2 * r 2 * v 1) * cv2
      have hr2 : r 2 = 0 := by
        rcases mul_eq_zero.mp key2 with h | h
        · exact absurd h h2c
        · rcases mul_eq_zero.mp h with h | h
          · rcases mul_eq_zero.mp h with h | h
            · exact absurd h hu2z
            · exact absurd h hv1ne
          · exact h
      exact ⟨hr1, hr2⟩

theorem case2_no_axis0_v0_count {n : ℕ} (hn : n ≠ 0) (h3 : ¬ 3 ∣ n)
    {t : Finset (Fin 3 → ℂ)} (ht : IsTriad (S n) t)
    (hZ : ∀ r ∈ t, ¬ AllNonzero n r)
    (hno0 : ∀ w ∈ t, ¬ (w 1 = 0 ∧ w 2 = 0)) :
    (t.filter (fun v => v 0 ≠ 0)).card = 2 := by
  classical
  obtain ⟨x, y, z, hxy, hxz, hyz, hteq⟩ := Finset.card_eq_three.mp ht.2.1
  have hxS : x ∈ S n := ht.1 (by rw [hteq]; simp)
  have hyS : y ∈ S n := ht.1 (by rw [hteq]; simp)
  have hzS : z ∈ S n := ht.1 (by rw [hteq]; simp)
  have hxy_o : Orthogonal x y :=
    ht.2.2 _ (by rw [hteq]; simp) _ (by rw [hteq]; simp) hxy
  have hxz_o : Orthogonal x z :=
    ht.2.2 _ (by rw [hteq]; simp) _ (by rw [hteq]; simp) hxz
  have hyz_o : Orthogonal y z :=
    ht.2.2 _ (by rw [hteq]; simp) _ (by rw [hteq]; simp) hyz
  rw [hteq]
  -- 8-way case split on (x 0, y 0, z 0) ∈ Bool³.
  by_cases hx0 : x 0 = 0
  · by_cases hy0 : y 0 = 0
    · by_cases hz0 : z 0 = 0
      · -- (T,T,T): 3 orth rays all with `v 0 = 0` — closed by the helper.
        exact (case2_three_orth_e0_perp_absurd hn hxS hyS hzS hxy_o hxz_o hyz_o
          hx0 hy0 hz0).elim
      · -- (T,T,F): only z has v 0 ≠ 0; forced axis-0 contradicts hno0.
        exfalso
        have hzno0 : ¬ (z 1 = 0 ∧ z 2 = 0) := hno0 z (by rw [hteq]; simp)
        exact hzno0 (case2_lone_v0_force_axis0 hn hzS hxS hyS hxz_o hyz_o hxy_o
          hx0 hy0 hz0)
    · by_cases hz0 : z 0 = 0
      · -- (T,F,T): y is the lone v 0 ≠ 0 ray.
        exfalso
        have hyno0 : ¬ (y 1 = 0 ∧ y 2 = 0) := hno0 y (by rw [hteq]; simp)
        exact hyno0 (case2_lone_v0_force_axis0 hn hyS hxS hzS hxy_o
          (Orthogonal_symm hyz_o) hxz_o hx0 hz0 hy0)
      · -- (T,F,F) GOOD: filter = {y, z}.
        have hf : ({x, y, z} : Finset (Fin 3 → ℂ)).filter (fun v => v 0 ≠ 0) = {y, z} := by
          ext v
          simp only [Finset.mem_filter, Finset.mem_insert, Finset.mem_singleton]
          refine ⟨?_, ?_⟩
          · rintro ⟨hmem, hv⟩
            rcases hmem with rfl | rfl | rfl
            · exact absurd hx0 hv
            · exact Or.inl rfl
            · exact Or.inr rfl
          · rintro (rfl | rfl)
            · exact ⟨Or.inr (Or.inl rfl), hy0⟩
            · exact ⟨Or.inr (Or.inr rfl), hz0⟩
        rw [hf]
        exact Finset.card_eq_two.mpr ⟨y, z, hyz, rfl⟩
  · by_cases hy0 : y 0 = 0
    · by_cases hz0 : z 0 = 0
      · -- (F,T,T): x is the lone v 0 ≠ 0 ray.
        exfalso
        have hxno0 : ¬ (x 1 = 0 ∧ x 2 = 0) := hno0 x (by rw [hteq]; simp)
        exact hxno0 (case2_lone_v0_force_axis0 hn hxS hyS hzS
          (Orthogonal_symm hxy_o) (Orthogonal_symm hxz_o) hyz_o hy0 hz0 hx0)
      · -- (F,T,F) GOOD: filter = {x, z}.
        have hf : ({x, y, z} : Finset (Fin 3 → ℂ)).filter (fun v => v 0 ≠ 0) = {x, z} := by
          ext v
          simp only [Finset.mem_filter, Finset.mem_insert, Finset.mem_singleton]
          refine ⟨?_, ?_⟩
          · rintro ⟨hmem, hv⟩
            rcases hmem with rfl | rfl | rfl
            · exact Or.inl rfl
            · exact absurd hy0 hv
            · exact Or.inr rfl
          · rintro (rfl | rfl)
            · exact ⟨Or.inl rfl, hx0⟩
            · exact ⟨Or.inr (Or.inr rfl), hz0⟩
        rw [hf]
        exact Finset.card_eq_two.mpr ⟨x, z, hxz, rfl⟩
    · by_cases hz0 : z 0 = 0
      · -- (F,F,T) GOOD: filter = {x, y}.
        have hf : ({x, y, z} : Finset (Fin 3 → ℂ)).filter (fun v => v 0 ≠ 0) = {x, y} := by
          ext v
          simp only [Finset.mem_filter, Finset.mem_insert, Finset.mem_singleton]
          refine ⟨?_, ?_⟩
          · rintro ⟨hmem, hv⟩
            rcases hmem with rfl | rfl | rfl
            · exact Or.inl rfl
            · exact Or.inr rfl
            · exact absurd hz0 hv
          · rintro (rfl | rfl)
            · exact ⟨Or.inl rfl, hx0⟩
            · exact ⟨Or.inr (Or.inl rfl), hy0⟩
        rw [hf]
        exact Finset.card_eq_two.mpr ⟨x, y, hxy, rfl⟩
      · -- (F,F,F): 3 with v 0 ≠ 0, no axis-0, no AllN.
        -- Each ray has supp = {0, 1} or {0, 2}.  Two cases:
        -- mixed planes ⇒ cross-plane non-orth (case2_cross_plane_absurd);
        -- all same plane ⇒ same-plane rigidity (linear_combination).
        exfalso
        have hxno0 : ¬ (x 1 = 0 ∧ x 2 = 0) := hno0 x (by rw [hteq]; simp)
        have hyno0 : ¬ (y 1 = 0 ∧ y 2 = 0) := hno0 y (by rw [hteq]; simp)
        have hzno0 : ¬ (z 1 = 0 ∧ z 2 = 0) := hno0 z (by rw [hteq]; simp)
        have hxN : ¬ AllNonzero n x := hZ x (by rw [hteq]; simp)
        have hyN : ¬ AllNonzero n y := hZ y (by rw [hteq]; simp)
        have hzN : ¬ AllNonzero n z := hZ z (by rw [hteq]; simp)
        -- Each ray r with r 0 ≠ 0 and ¬ AllNonzero has r 1 = 0 ∨ r 2 = 0.
        have hxplane : x 1 = 0 ∨ x 2 = 0 := by
          by_contra hcon; push Not at hcon
          exact hxN ⟨hxS, fun k => by fin_cases k; exacts [hx0, hcon.1, hcon.2]⟩
        have hyplane : y 1 = 0 ∨ y 2 = 0 := by
          by_contra hcon; push Not at hcon
          exact hyN ⟨hyS, fun k => by fin_cases k; exacts [hy0, hcon.1, hcon.2]⟩
        have hzplane : z 1 = 0 ∨ z 2 = 0 := by
          by_contra hcon; push Not at hcon
          exact hzN ⟨hzS, fun k => by fin_cases k; exacts [hz0, hcon.1, hcon.2]⟩
        rcases hxplane with hx1 | hx2 <;> rcases hyplane with hy1 | hy2 <;>
          rcases hzplane with hz1 | hz2
        · -- all v 1 = 0: same plane {0, 2}.  Rigidity argument.
          have hx2ne : x 2 ≠ 0 := fun h => hxno0 ⟨hx1, h⟩
          have hy2ne : y 2 ≠ 0 := fun h => hyno0 ⟨hy1, h⟩
          have hz2ne : z 2 ≠ 0 := fun h => hzno0 ⟨hz1, h⟩
          have ipxy : (starRingEnd ℂ) (x 0) * y 0 + (starRingEnd ℂ) (x 1) * y 1 +
                      (starRingEnd ℂ) (x 2) * y 2 = 0 := by
            have h := hxy_o; unfold Orthogonal inner3 at h; rwa [Fin.sum_univ_three] at h
          have ipxz : (starRingEnd ℂ) (x 0) * z 0 + (starRingEnd ℂ) (x 1) * z 1 +
                      (starRingEnd ℂ) (x 2) * z 2 = 0 := by
            have h := hxz_o; unfold Orthogonal inner3 at h; rwa [Fin.sum_univ_three] at h
          have ipyz : (starRingEnd ℂ) (y 0) * z 0 + (starRingEnd ℂ) (y 1) * z 1 +
                      (starRingEnd ℂ) (y 2) * z 2 = 0 := by
            have h := hyz_o; unfold Orthogonal inner3 at h; rwa [Fin.sum_univ_three] at h
          rw [hx1, hy1] at ipxy
          rw [hx1, hz1] at ipxz
          rw [hy1, hz1] at ipyz
          simp only [map_zero, zero_mul, mul_zero, add_zero] at ipxy ipxz ipyz
          have apow0 : (x 0) ^ n = 1 := (hxS.2 0).resolve_left hx0
          have apow2 : (x 2) ^ n = 1 := (hxS.2 2).resolve_left hx2ne
          have cx0 : x 0 * (starRingEnd ℂ) (x 0) = 1 := mul_conj_eq_one_of_pow hn apow0
          have cx2 : x 2 * (starRingEnd ℂ) (x 2) = 1 := mul_conj_eq_one_of_pow hn apow2
          have ypow0 : (y 0) ^ n = 1 := (hyS.2 0).resolve_left hy0
          have ypow2 : (y 2) ^ n = 1 := (hyS.2 2).resolve_left hy2ne
          have cy0 : y 0 * (starRingEnd ℂ) (y 0) = 1 := mul_conj_eq_one_of_pow hn ypow0
          have cy2 : y 2 * (starRingEnd ℂ) (y 2) = 1 := mul_conj_eq_one_of_pow hn ypow2
          have key : (2 : ℂ) * (x 0 * y 0 * z 2) = 0 := by
            linear_combination
              (- x 0 * x 2 * z 0) * ipxy + (x 0 * x 2 * y 0) * ipxz
              + (x 0 * y 0 * y 2) * ipyz
              + (x 0 * y 2 * z 0 - x 0 * y 0 * z 2) * cx2
              + (- x 0 * y 2 * z 0) * cy0 + (- x 0 * y 0 * z 2) * cy2
          have h2c : (2 : ℂ) ≠ 0 := by norm_num
          rcases mul_eq_zero.mp key with h | h
          · exact h2c h
          · rcases mul_eq_zero.mp h with h | h
            · rcases mul_eq_zero.mp h with h | h
              · exact hx0 h
              · exact hy0 h
            · exact hz2ne h
        · -- x 1 = 0, y 1 = 0, z 2 = 0: mixed. (x in {0,2}, z in {0,1}).
          exact case2_cross_plane_absurd hx0 hz0 hx1 hz2 hxz_o
        · -- x 1 = 0, y 2 = 0, z 1 = 0: (x in {0,2}, y in {0,1}).
          exact case2_cross_plane_absurd hx0 hy0 hx1 hy2 hxy_o
        · -- x 1 = 0, y 2 = 0, z 2 = 0: (x in {0,2}, y in {0,1}).
          exact case2_cross_plane_absurd hx0 hy0 hx1 hy2 hxy_o
        · -- x 2 = 0, y 1 = 0, z 1 = 0: (y in {0,2}, x in {0,1}).
          exact case2_cross_plane_absurd hy0 hx0 hy1 hx2 (Orthogonal_symm hxy_o)
        · -- x 2 = 0, y 1 = 0, z 2 = 0: (y in {0,2}, x in {0,1}).
          exact case2_cross_plane_absurd hy0 hx0 hy1 hx2 (Orthogonal_symm hxy_o)
        · -- x 2 = 0, y 2 = 0, z 1 = 0: (z in {0,2}, x in {0,1}).
          exact case2_cross_plane_absurd hz0 hx0 hz1 hx2 (Orthogonal_symm hxz_o)
        · -- all v 2 = 0: same plane {0, 1}.  Rigidity argument.
          have hx1ne : x 1 ≠ 0 := fun h => hxno0 ⟨h, hx2⟩
          have hy1ne : y 1 ≠ 0 := fun h => hyno0 ⟨h, hy2⟩
          have hz1ne : z 1 ≠ 0 := fun h => hzno0 ⟨h, hz2⟩
          have ipxy : (starRingEnd ℂ) (x 0) * y 0 + (starRingEnd ℂ) (x 1) * y 1 +
                      (starRingEnd ℂ) (x 2) * y 2 = 0 := by
            have h := hxy_o; unfold Orthogonal inner3 at h; rwa [Fin.sum_univ_three] at h
          have ipxz : (starRingEnd ℂ) (x 0) * z 0 + (starRingEnd ℂ) (x 1) * z 1 +
                      (starRingEnd ℂ) (x 2) * z 2 = 0 := by
            have h := hxz_o; unfold Orthogonal inner3 at h; rwa [Fin.sum_univ_three] at h
          have ipyz : (starRingEnd ℂ) (y 0) * z 0 + (starRingEnd ℂ) (y 1) * z 1 +
                      (starRingEnd ℂ) (y 2) * z 2 = 0 := by
            have h := hyz_o; unfold Orthogonal inner3 at h; rwa [Fin.sum_univ_three] at h
          rw [hx2, hy2] at ipxy
          rw [hx2, hz2] at ipxz
          rw [hy2, hz2] at ipyz
          simp only [map_zero, zero_mul, mul_zero, add_zero] at ipxy ipxz ipyz
          have apow0 : (x 0) ^ n = 1 := (hxS.2 0).resolve_left hx0
          have apow1 : (x 1) ^ n = 1 := (hxS.2 1).resolve_left hx1ne
          have cx0 : x 0 * (starRingEnd ℂ) (x 0) = 1 := mul_conj_eq_one_of_pow hn apow0
          have cx1 : x 1 * (starRingEnd ℂ) (x 1) = 1 := mul_conj_eq_one_of_pow hn apow1
          have ypow0 : (y 0) ^ n = 1 := (hyS.2 0).resolve_left hy0
          have ypow1 : (y 1) ^ n = 1 := (hyS.2 1).resolve_left hy1ne
          have cy0 : y 0 * (starRingEnd ℂ) (y 0) = 1 := mul_conj_eq_one_of_pow hn ypow0
          have cy1 : y 1 * (starRingEnd ℂ) (y 1) = 1 := mul_conj_eq_one_of_pow hn ypow1
          have key : (2 : ℂ) * (x 0 * y 0 * z 1) = 0 := by
            linear_combination
              (- x 0 * x 1 * z 0) * ipxy + (x 0 * x 1 * y 0) * ipxz
              + (x 0 * y 0 * y 1) * ipyz
              + (x 0 * y 1 * z 0 - x 0 * y 0 * z 1) * cx1
              + (- x 0 * y 1 * z 0) * cy0 + (- x 0 * y 0 * z 1) * cy1
          have h2c : (2 : ℂ) ≠ 0 := by norm_num
          rcases mul_eq_zero.mp key with h | h
          · exact h2c h
          · rcases mul_eq_zero.mp h with h | h
            · rcases mul_eq_zero.mp h with h | h
              · exact hx0 h
              · exact hy0 h
            · exact hz1ne h

/-! #### Case 2 — matched-pair ratio in a coordinate plane -/

/-- **Matched-pair ratio in the `{0, 1}` plane.**  For `a, b ∈ Sₙ` supported on
    `{0, 1}` (i.e., `a 2 = b 2 = 0`, with `a 0, a 1, b 0, b 1` all nonzero
    `n`-th roots of unity), orthogonality forces `b 1 / b 0 = -(a 1 / a 0)`.

    Reason: orthogonality is `conj(a 0)·b 0 + conj(a 1)·b 1 = 0`.  Multiplying
    by `a 0 · a 1` and using `a j · conj(a j) = 1` (unitarity of nth roots)
    yields `a 1 · b 0 + a 0 · b 1 = 0`, giving the ratio identity after
    division by `a 0 · b 0`. -/
theorem case2_plane01_ratio {n : ℕ} (hn : n ≠ 0)
    {a b : Fin 3 → ℂ} (ha : a ∈ S n) (hb : b ∈ S n)
    (ha0 : a 0 ≠ 0) (ha1 : a 1 ≠ 0) (ha2 : a 2 = 0)
    (hb0 : b 0 ≠ 0) (hb1 : b 1 ≠ 0) (hb2 : b 2 = 0)
    (horth : Orthogonal a b) :
    b 1 / b 0 = -(a 1 / a 0) := by
  have apow0 : (a 0) ^ n = 1 := (ha.2 0).resolve_left ha0
  have apow1 : (a 1) ^ n = 1 := (ha.2 1).resolve_left ha1
  have ca0 : a 0 * (starRingEnd ℂ) (a 0) = 1 := mul_conj_eq_one_of_pow hn apow0
  have ca1 : a 1 * (starRingEnd ℂ) (a 1) = 1 := mul_conj_eq_one_of_pow hn apow1
  have ipab : (starRingEnd ℂ) (a 0) * b 0 + (starRingEnd ℂ) (a 1) * b 1 +
              (starRingEnd ℂ) (a 2) * b 2 = 0 := by
    have h := horth; unfold Orthogonal inner3 at h; rwa [Fin.sum_univ_three] at h
  rw [ha2] at ipab
  simp only [map_zero, zero_mul, add_zero] at ipab
  -- ipab : conj(a 0) * b 0 + conj(a 1) * b 1 = 0
  have key : a 1 * b 0 + a 0 * b 1 = 0 := by
    linear_combination (a 0 * a 1) * ipab + (- a 1 * b 0) * ca0 + (- a 0 * b 1) * ca1
  -- Now `key` gives the conjugate-free orthogonality; turn into the ratio identity.
  have ha0b0 : a 0 * b 0 ≠ 0 := mul_ne_zero ha0 hb0
  field_simp
  linear_combination key

/-- **Matched-pair ratio in the `{0, 2}` plane.**  Analogue of
    `case2_plane01_ratio` with coordinates `1` and `2` swapped. -/
theorem case2_plane02_ratio {n : ℕ} (hn : n ≠ 0)
    {a b : Fin 3 → ℂ} (ha : a ∈ S n) (hb : b ∈ S n)
    (ha0 : a 0 ≠ 0) (ha1 : a 1 = 0) (ha2 : a 2 ≠ 0)
    (hb0 : b 0 ≠ 0) (hb1 : b 1 = 0) (hb2 : b 2 ≠ 0)
    (horth : Orthogonal a b) :
    b 2 / b 0 = -(a 2 / a 0) := by
  have apow0 : (a 0) ^ n = 1 := (ha.2 0).resolve_left ha0
  have apow2 : (a 2) ^ n = 1 := (ha.2 2).resolve_left ha2
  have ca0 : a 0 * (starRingEnd ℂ) (a 0) = 1 := mul_conj_eq_one_of_pow hn apow0
  have ca2 : a 2 * (starRingEnd ℂ) (a 2) = 1 := mul_conj_eq_one_of_pow hn apow2
  have ipab : (starRingEnd ℂ) (a 0) * b 0 + (starRingEnd ℂ) (a 1) * b 1 +
              (starRingEnd ℂ) (a 2) * b 2 = 0 := by
    have h := horth; unfold Orthogonal inner3 at h; rwa [Fin.sum_univ_three] at h
  rw [ha1] at ipab
  simp only [map_zero, zero_mul, zero_add] at ipab
  -- ipab : conj(a 0) * b 0 + conj(a 2) * b 2 = 0
  have key : a 2 * b 0 + a 0 * b 2 = 0 := by
    linear_combination (a 0 * a 2) * ipab + (- a 2 * b 0) * ca0 + (- a 0 * b 2) * ca2
  have ha0b0 : a 0 * b 0 ≠ 0 := mul_ne_zero ha0 hb0
  field_simp
  linear_combination key

/-! #### Case 2 — coloring and obligation (I) -/

/-- The Case-2 coloring of `Sₙ` (under `2 ∣ n`, `3 ∤ n`):
    * `v 0 = 0`: `false`.
    * `v 0 ≠ 0`, `v 1 = v 2 = 0` (axis-0 ray): `true`.
    * `v 0 ≠ 0`, `v 1 = 0`, `v 2 ≠ 0` ({0,2}-plane ray): `sel (v 2 / v 0)`.
    * `v 0 ≠ 0`, `v 1 ≠ 0`, `v 2 = 0` ({0,1}-plane ray): `sel (v 1 / v 0)`.
    * `v 0 ≠ 0`, `v 1 ≠ 0`, `v 2 ≠ 0` (AllNonzero, never in Case-2 triads): `false`. -/
noncomputable def case2_color (sel : ℂ → Bool) (v : Fin 3 → ℂ) : Bool := by
  classical
  exact
    if v 0 = 0 then false
    else if v 1 = 0 then
      if v 2 = 0 then true
      else sel (v 2 / v 0)
    else if v 2 = 0 then sel (v 1 / v 0)
    else false

/-- `case2_color sel v = true` unfolds to the three possible "true" support
    structures: axis-0 (supp `{0}`), `{0,2}`-plane with `sel`-true ratio, or
    `{0,1}`-plane with `sel`-true ratio. -/
private theorem case2_color_true_iff {sel : ℂ → Bool} {v : Fin 3 → ℂ}
    (h : case2_color sel v = true) :
    v 0 ≠ 0 ∧
    ((v 1 = 0 ∧ v 2 = 0) ∨
     (v 1 = 0 ∧ v 2 ≠ 0 ∧ sel (v 2 / v 0) = true) ∨
     (v 1 ≠ 0 ∧ v 2 = 0 ∧ sel (v 1 / v 0) = true)) := by
  classical
  unfold case2_color at h
  by_cases hv0 : v 0 = 0
  · rw [if_pos hv0] at h; exact absurd h (by decide)
  · rw [if_neg hv0] at h
    refine ⟨hv0, ?_⟩
    by_cases hv1 : v 1 = 0
    · rw [if_pos hv1] at h
      by_cases hv2 : v 2 = 0
      · exact Or.inl ⟨hv1, hv2⟩
      · rw [if_neg hv2] at h
        exact Or.inr (Or.inl ⟨hv1, hv2, h⟩)
    · rw [if_neg hv1] at h
      by_cases hv2 : v 2 = 0
      · rw [if_pos hv2] at h
        exact Or.inr (Or.inr ⟨hv1, hv2, h⟩)
      · rw [if_neg hv2] at h
        exact absurd h (by decide)

/-- **Case 2 — obligation (I).**  Under `2 ∣ n`, `3 ∤ n`, no two orthogonal
    rays of `Sₙ` are both colored `true` by the Case-2 coloring.

    Proof by case-analysis on `(v, w)`'s support patterns (3 "true" structures
    each = 9 sub-cases): the 7 cross-structure cases have inner product
    reducing to a single nonzero root-of-unity term (so non-orthogonal); the
    2 same-plane cases (both `{0,1}` or both `{0,2}`) invoke
    `case2_plane01_ratio` / `case2_plane02_ratio` to derive
    `sel (w_k / w 0) = sel (-(v_k / v 0))`, contradicting the
    `exists_match_selector` invariant that exactly one of `{sel a, sel (-a)}`
    is `true` for `a ≠ 0`. -/
theorem case2_color_obligation_I {n : ℕ} (hn : n ≠ 0)
    {sel : ℂ → Bool}
    (hsel : ∀ a : ℂ, a ≠ 0 →
       (sel a = true ∧ sel (-a) = false) ∨ (sel a = false ∧ sel (-a) = true))
    {v w : Fin 3 → ℂ} (hv : v ∈ S n) (hw : w ∈ S n) (horth : Orthogonal v w)
    (hcv : case2_color sel v = true) (hcw : case2_color sel w = true) : False := by
  obtain ⟨hv0, hvstruct⟩ := case2_color_true_iff hcv
  obtain ⟨hw0, hwstruct⟩ := case2_color_true_iff hcw
  have ipvw : (starRingEnd ℂ) (v 0) * w 0 + (starRingEnd ℂ) (v 1) * w 1 +
              (starRingEnd ℂ) (v 2) * w 2 = 0 := by
    have h := horth; unfold Orthogonal inner3 at h; rwa [Fin.sum_univ_three] at h
  have hconj_v0_ne : (starRingEnd ℂ) (v 0) ≠ 0 := by
    rw [starRingEnd_apply]; exact star_ne_zero.mpr hv0
  rcases hvstruct with ⟨hv1z, hv2z⟩ | ⟨hv1z, hv2ne, hsv⟩ | ⟨hv1ne, hv2z, hsv⟩
  · -- v is the axis-0 ray: any orthogonal w has `v 0` non-vanishing inner contribution.
    rw [hv1z, hv2z] at ipvw
    simp only [map_zero, zero_mul, add_zero] at ipvw
    exact mul_ne_zero hconj_v0_ne hw0 ipvw
  · -- v is in plane `{0, 2}`: case-analyze w.
    rcases hwstruct with ⟨hw1z, hw2z⟩ | ⟨hw1z, hw2ne, hsw⟩ | ⟨hw1ne, hw2z, _⟩
    · -- w axis-0: inner product reduces to conj(v 0) * w 0
      rw [hw1z, hw2z] at ipvw
      simp only [mul_zero, add_zero] at ipvw
      exact mul_ne_zero hconj_v0_ne hw0 ipvw
    · -- w also in plane `{0, 2}`: matched pair contradicts the selector invariant.
      have h2v : v 2 / v 0 ≠ 0 := div_ne_zero hv2ne hv0
      have hratio : w 2 / w 0 = -(v 2 / v 0) :=
        case2_plane02_ratio hn hv hw hv0 hv1z hv2ne hw0 hw1z hw2ne horth
      rw [hratio] at hsw
      rcases hsel (v 2 / v 0) h2v with ⟨_, hf⟩ | ⟨hf, _⟩
      · exact absurd hsw (by rw [hf]; decide)
      · exact absurd hsv (by rw [hf]; decide)
    · -- w in plane `{0, 1}` (cross-plane): inner reduces to conj(v 0) * w 0
      rw [hv1z, hw2z] at ipvw
      simp only [map_zero, zero_mul, mul_zero, add_zero] at ipvw
      exact mul_ne_zero hconj_v0_ne hw0 ipvw
  · -- v is in plane `{0, 1}`: case-analyze w.
    rcases hwstruct with ⟨hw1z, hw2z⟩ | ⟨hw1z, hw2ne, _⟩ | ⟨hw1ne, hw2z, hsw⟩
    · -- w axis-0
      rw [hw1z, hw2z] at ipvw
      simp only [mul_zero, add_zero] at ipvw
      exact mul_ne_zero hconj_v0_ne hw0 ipvw
    · -- w in plane `{0, 2}` (cross-plane)
      rw [hv2z, hw1z] at ipvw
      simp only [map_zero, zero_mul, mul_zero, add_zero] at ipvw
      exact mul_ne_zero hconj_v0_ne hw0 ipvw
    · -- w also in plane `{0, 1}`: matched pair contradicts the selector invariant.
      have h1v : v 1 / v 0 ≠ 0 := div_ne_zero hv1ne hv0
      have hratio : w 1 / w 0 = -(v 1 / v 0) :=
        case2_plane01_ratio hn hv hw hv0 hv1ne hv2z hw0 hw1ne hw2z horth
      rw [hratio] at hsw
      rcases hsel (v 1 / v 0) h1v with ⟨_, hf⟩ | ⟨hf, _⟩
      · exact absurd hsw (by rw [hf]; decide)
      · exact absurd hsv (by rw [hf]; decide)

/-- **Case 2 colorable.**  Under `2 ∣ n` and `3 ∤ n`, the ray set `Sₙ` admits
    a KS coloring (`case2_color` paired with the matched-pair selector from
    `exists_match_selector`).  This is the necessity direction for Case 2 of
    the main theorem.

    Obligation (I) is `case2_color_obligation_I`.  Obligation (II) splits
    each triad on whether it contains an axis-0 ray:
    * Axis-0 ray `w` exists ⇒ `case2_axis0_dominates` forces the other two
      to have `v 0 = 0`, so only `w` is `true`-colored.
    * Otherwise, `case2_no_axis0_v0_count` gives exactly two `v 0 ≠ 0`
      rays.  Cross-plane non-orthogonality (`case2_cross_plane_absurd`)
      forces them into the same coordinate plane; the matched-pair ratio
      (`case2_plane0k_ratio`) and `exists_match_selector` invariant pick
      exactly one as `true`. -/
theorem case2_colorable {n : ℕ} (hn0 : n ≠ 0) (h2 : 2 ∣ n) (h3 : ¬ 3 ∣ n) :
    ∃ c : (Fin 3 → ℂ) → Bool, IsColoring (S n) c := by
  classical
  obtain ⟨sel, hsel⟩ := exists_match_selector
  refine ⟨case2_color sel, ?_, ?_⟩
  · -- (I)
    intro v hv w hw horth h
    exact case2_color_obligation_I hn0 hsel hv hw horth h.1 h.2
  · -- (II) every triad has exactly one `true`.
    intro t ht
    have hZ : ∀ r ∈ t, ¬ AllNonzero n r := case2_no_allNonzero_in_triad hn0 h3 ht
    by_cases hax0 : ∃ w ∈ t, w 1 = 0 ∧ w 2 = 0
    · -- Has an axis-0 ray.
      obtain ⟨w, hwt, hw1, hw2⟩ := hax0
      have hwS : w ∈ S n := ht.1 (Finset.mem_coe.mpr hwt)
      have hw0 : w 0 ≠ 0 := by
        intro h; exact hwS.1 (funext fun k => by fin_cases k <;> simp_all)
      have hothers : ∀ v ∈ t, v ≠ w → v 0 = 0 :=
        case2_axis0_dominates ht hwt hw1 hw2
      have hcw : case2_color sel w = true := by
        unfold case2_color
        rw [if_neg hw0, if_pos hw1, if_pos hw2]
      have hf : t.filter (fun v => case2_color sel v = true) = {w} := by
        ext v
        simp only [Finset.mem_filter, Finset.mem_singleton]
        refine ⟨?_, ?_⟩
        · rintro ⟨hvt, hcvt⟩
          by_contra hne
          have hv0 : v 0 = 0 := hothers v hvt hne
          have hcv_f : case2_color sel v = false := by
            unfold case2_color; rw [if_pos hv0]
          rw [hcv_f] at hcvt; exact absurd hcvt (by decide)
        · rintro rfl; exact ⟨hwt, hcw⟩
      rw [hf, Finset.card_singleton]
    · -- No axis-0 ray.
      have hno0 : ∀ w ∈ t, ¬ (w 1 = 0 ∧ w 2 = 0) := fun w hw h12 =>
        hax0 ⟨w, hw, h12⟩
      have hcount := case2_no_axis0_v0_count hn0 h3 ht hZ hno0
      obtain ⟨p, q, hpq, hpq_eq⟩ := Finset.card_eq_two.mp hcount
      have hp_mem : p ∈ t.filter (fun v => v 0 ≠ 0) := by rw [hpq_eq]; simp
      have hq_mem : q ∈ t.filter (fun v => v 0 ≠ 0) := by rw [hpq_eq]; simp
      have hp_t : p ∈ t := (Finset.mem_filter.mp hp_mem).1
      have hp0 : p 0 ≠ 0 := (Finset.mem_filter.mp hp_mem).2
      have hq_t : q ∈ t := (Finset.mem_filter.mp hq_mem).1
      have hq0 : q 0 ≠ 0 := (Finset.mem_filter.mp hq_mem).2
      have hpS : p ∈ S n := ht.1 (Finset.mem_coe.mpr hp_t)
      have hqS : q ∈ S n := ht.1 (Finset.mem_coe.mpr hq_t)
      have hpN : ¬ AllNonzero n p := hZ p hp_t
      have hqN : ¬ AllNonzero n q := hZ q hq_t
      have hpno0 : ¬ (p 1 = 0 ∧ p 2 = 0) := hno0 p hp_t
      have hqno0 : ¬ (q 1 = 0 ∧ q 2 = 0) := hno0 q hq_t
      have hpq_o : Orthogonal p q :=
        ht.2.2 p (Finset.mem_coe.mpr hp_t) q (Finset.mem_coe.mpr hq_t) hpq
      have hp_plane : p 1 = 0 ∨ p 2 = 0 := by
        by_contra hcon; push Not at hcon
        exact hpN ⟨hpS, fun k => by fin_cases k; exacts [hp0, hcon.1, hcon.2]⟩
      have hq_plane : q 1 = 0 ∨ q 2 = 0 := by
        by_contra hcon; push Not at hcon
        exact hqN ⟨hqS, fun k => by fin_cases k; exacts [hq0, hcon.1, hcon.2]⟩
      -- t.filter (c v = true) ⊆ {p, q}, since v 0 = 0 ⇒ c v = false.
      have hf_eq : t.filter (fun v => case2_color sel v = true)
                 = ({p, q} : Finset (Fin 3 → ℂ)).filter (fun v => case2_color sel v = true) := by
        ext v
        simp only [Finset.mem_filter, Finset.mem_insert, Finset.mem_singleton]
        refine ⟨?_, ?_⟩
        · rintro ⟨hvt, hcv⟩
          have hv0 : v 0 ≠ 0 := by
            intro h
            have : case2_color sel v = false := by
              unfold case2_color; rw [if_pos h]
            rw [this] at hcv; exact absurd hcv (by decide)
          have hvf : v ∈ t.filter (fun w => w 0 ≠ 0) :=
            Finset.mem_filter.mpr ⟨hvt, hv0⟩
          rw [hpq_eq] at hvf
          rcases Finset.mem_insert.mp hvf with rfl | hvq
          · exact ⟨Or.inl rfl, hcv⟩
          · exact ⟨Or.inr (Finset.mem_singleton.mp hvq), hcv⟩
        · rintro ⟨hv_pq, hcv⟩
          rcases hv_pq with rfl | rfl
          · exact ⟨hp_t, hcv⟩
          · exact ⟨hq_t, hcv⟩
      rw [hf_eq]
      -- Case-split p, q's planes.  Cross-plane is impossible by case2_cross_plane_absurd.
      -- Same-plane gives matched pair, sel picks exactly one.
      have key : (({p, q} : Finset (Fin 3 → ℂ)).filter
                    (fun v => case2_color sel v = true)).card = 1 := by
        rcases hp_plane with hp1z | hp2z <;> rcases hq_plane with hq1z | hq2z
        · -- both p 1 = 0, q 1 = 0: both supp = {0, 2}.
          have hp2ne : p 2 ≠ 0 := fun h => hpno0 ⟨hp1z, h⟩
          have hq2ne : q 2 ≠ 0 := fun h => hqno0 ⟨hq1z, h⟩
          have hcp : case2_color sel p = sel (p 2 / p 0) := by
            unfold case2_color
            rw [if_neg hp0, if_pos hp1z, if_neg hp2ne]
          have hcq : case2_color sel q = sel (q 2 / q 0) := by
            unfold case2_color
            rw [if_neg hq0, if_pos hq1z, if_neg hq2ne]
          have hratio : q 2 / q 0 = -(p 2 / p 0) :=
            case2_plane02_ratio hn0 hpS hqS hp0 hp1z hp2ne hq0 hq1z hq2ne hpq_o
          have hp2div : p 2 / p 0 ≠ 0 := div_ne_zero hp2ne hp0
          rcases hsel (p 2 / p 0) hp2div with ⟨hsv_t, hsv_f⟩ | ⟨hsv_f, hsv_t⟩
          · -- sel(p 2/p 0) = true, sel(-(p 2/p 0)) = false.  c p = true, c q = false.
            have hcp_t : case2_color sel p = true := by rw [hcp]; exact hsv_t
            have hcq_f : case2_color sel q = false := by rw [hcq, hratio]; exact hsv_f
            have : ({p, q} : Finset (Fin 3 → ℂ)).filter
                     (fun v => case2_color sel v = true) = {p} := by
              ext v
              simp only [Finset.mem_filter, Finset.mem_insert, Finset.mem_singleton]
              refine ⟨?_, ?_⟩
              · rintro ⟨hv_pq, hcv⟩
                rcases hv_pq with rfl | rfl
                · rfl
                · rw [hcq_f] at hcv; exact absurd hcv (by decide)
              · rintro rfl; exact ⟨Or.inl rfl, hcp_t⟩
            rw [this, Finset.card_singleton]
          · -- sel(p 2/p 0) = false, sel(-(p 2/p 0)) = true.  c p = false, c q = true.
            have hcp_f : case2_color sel p = false := by rw [hcp]; exact hsv_f
            have hcq_t : case2_color sel q = true := by rw [hcq, hratio]; exact hsv_t
            have : ({p, q} : Finset (Fin 3 → ℂ)).filter
                     (fun v => case2_color sel v = true) = {q} := by
              ext v
              simp only [Finset.mem_filter, Finset.mem_insert, Finset.mem_singleton]
              refine ⟨?_, ?_⟩
              · rintro ⟨hv_pq, hcv⟩
                rcases hv_pq with rfl | rfl
                · rw [hcp_f] at hcv; exact absurd hcv (by decide)
                · rfl
              · rintro rfl; exact ⟨Or.inr rfl, hcq_t⟩
            rw [this, Finset.card_singleton]
        · -- p 1 = 0, q 2 = 0: cross-plane.  Contradiction via case2_cross_plane_absurd.
          have hq1ne : q 1 ≠ 0 := fun h => hqno0 ⟨h, hq2z⟩
          exact (case2_cross_plane_absurd hp0 hq0 hp1z hq2z hpq_o).elim
        · -- p 2 = 0, q 1 = 0: cross-plane (q in {0,2}-plane, p in {0,1}-plane).
          have hp1ne : p 1 ≠ 0 := fun h => hpno0 ⟨h, hp2z⟩
          exact (case2_cross_plane_absurd hq0 hp0 hq1z hp2z
            (Orthogonal_symm hpq_o)).elim
        · -- both p 2 = 0, q 2 = 0: both supp = {0, 1}.
          have hp1ne : p 1 ≠ 0 := fun h => hpno0 ⟨h, hp2z⟩
          have hq1ne : q 1 ≠ 0 := fun h => hqno0 ⟨h, hq2z⟩
          have hcp : case2_color sel p = sel (p 1 / p 0) := by
            unfold case2_color
            rw [if_neg hp0, if_neg hp1ne, if_pos hp2z]
          have hcq : case2_color sel q = sel (q 1 / q 0) := by
            unfold case2_color
            rw [if_neg hq0, if_neg hq1ne, if_pos hq2z]
          have hratio : q 1 / q 0 = -(p 1 / p 0) :=
            case2_plane01_ratio hn0 hpS hqS hp0 hp1ne hp2z hq0 hq1ne hq2z hpq_o
          have hp1div : p 1 / p 0 ≠ 0 := div_ne_zero hp1ne hp0
          rcases hsel (p 1 / p 0) hp1div with ⟨hsv_t, hsv_f⟩ | ⟨hsv_f, hsv_t⟩
          · have hcp_t : case2_color sel p = true := by rw [hcp]; exact hsv_t
            have hcq_f : case2_color sel q = false := by rw [hcq, hratio]; exact hsv_f
            have : ({p, q} : Finset (Fin 3 → ℂ)).filter
                     (fun v => case2_color sel v = true) = {p} := by
              ext v
              simp only [Finset.mem_filter, Finset.mem_insert, Finset.mem_singleton]
              refine ⟨?_, ?_⟩
              · rintro ⟨hv_pq, hcv⟩
                rcases hv_pq with rfl | rfl
                · rfl
                · rw [hcq_f] at hcv; exact absurd hcv (by decide)
              · rintro rfl; exact ⟨Or.inl rfl, hcp_t⟩
            rw [this, Finset.card_singleton]
          · have hcp_f : case2_color sel p = false := by rw [hcp]; exact hsv_f
            have hcq_t : case2_color sel q = true := by rw [hcq, hratio]; exact hsv_t
            have : ({p, q} : Finset (Fin 3 → ℂ)).filter
                     (fun v => case2_color sel v = true) = {q} := by
              ext v
              simp only [Finset.mem_filter, Finset.mem_insert, Finset.mem_singleton]
              refine ⟨?_, ?_⟩
              · rintro ⟨hv_pq, hcv⟩
                rcases hv_pq with rfl | rfl
                · rw [hcp_f] at hcv; exact absurd hcv (by decide)
                · rfl
              · rintro rfl; exact ⟨Or.inr rfl, hcq_t⟩
            rw [this, Finset.card_singleton]
      exact key

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
      exact hKS (case2_colorable (by omega) h2 h3)
    · -- Case 3 (2 ∤ n, 3 ∣ n): projective collapse isolates triads.
      exact hKS (case3_colorable (by omega) h2 h3)
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
