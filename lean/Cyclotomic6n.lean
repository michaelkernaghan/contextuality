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
