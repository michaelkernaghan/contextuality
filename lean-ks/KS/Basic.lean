/-
Kochen-Specker colourings and a checkable certificate of uncolourability.

No imports: everything here is core Lean 4, and the final theorems are closed by `decide`,
so they rest on the kernel alone.
-/
namespace KS

/-- A finite set of rays `0, ..., n-1` with an orthogonality test. -/
structure Sys where
  n : Nat
  orth : Nat → Nat → Bool

/-- `f` is a KS colouring of `S`: no two orthogonal rays both get `true`, and every three
mutually orthogonal rays contain a ray that gets `true`.  (Together: exactly one per triad.) -/
def Valid (S : Sys) (f : Nat → Bool) : Prop :=
  (∀ i j, i < S.n → j < S.n → S.orth i j = true → ¬ (f i = true ∧ f j = true)) ∧
  (∀ i j k, i < S.n → j < S.n → k < S.n →
      S.orth i j = true → S.orth i k = true → S.orth j k = true →
      f i = true ∨ f j = true ∨ f k = true)

/-- `S` has no KS colouring. -/
def Uncolourable (S : Sys) : Prop := ¬ ∃ f : Nat → Bool, Valid S f

/-- A case-split refutation.  A leaf names a constraint that the current partial assignment
already violates; `split v t e` tries ray `v` coloured `true` (then `t`) and `false` (then `e`). -/
inductive Cert where
  | pair (i j : Nat)
  | triad (i j k : Nat)
  | split (v : Nat) (t e : Cert)

/-- Value of ray `v` in a partial assignment (most recent entry first). -/
def val : List (Nat × Bool) → Nat → Option Bool
  | [], _ => none
  | (w, b) :: r, v => if w = v then some b else val r v

def Agrees (f : Nat → Bool) (ρ : List (Nat × Bool)) : Prop :=
  ∀ p, p ∈ ρ → f p.1 = p.2

theorem agrees_nil (f : Nat → Bool) : Agrees f [] := by
  intro p hp
  cases hp

theorem agrees_cons {f : Nat → Bool} {ρ : List (Nat × Bool)} {v : Nat} {b : Bool}
    (h : Agrees f ρ) (hv : f v = b) : Agrees f ((v, b) :: ρ) := by
  intro p hp
  rcases List.mem_cons.mp hp with rfl | hp
  · exact hv
  · exact h p hp

theorem val_agrees {f : Nat → Bool} {ρ : List (Nat × Bool)} {v : Nat} {b : Bool}
    (h : Agrees f ρ) (hv : val ρ v = some b) : f v = b := by
  induction ρ with
  | nil => simp [val] at hv
  | cons p r ih =>
    obtain ⟨w, c⟩ := p
    by_cases hw : w = v
    · have hc : c = b := by simpa [val, hw] using hv
      have := h (w, c) List.mem_cons_self
      simpa [hw, hc] using this
    · have hv' : val r v = some b := by simpa [val, hw] using hv
      exact ih (fun q hq => h q (List.mem_cons_of_mem _ hq)) hv'

/-- Does the certificate refute every colouring that extends the partial assignment `ρ`? -/
def check (S : Sys) (ρ : List (Nat × Bool)) : Cert → Bool
  | .pair i j =>
      decide (i < S.n) && decide (j < S.n) && S.orth i j &&
      (val ρ i == some true) && (val ρ j == some true)
  | .triad i j k =>
      decide (i < S.n) && decide (j < S.n) && decide (k < S.n) &&
      S.orth i j && S.orth i k && S.orth j k &&
      (val ρ i == some false) && (val ρ j == some false) && (val ρ k == some false)
  | .split v t e => check S ((v, true) :: ρ) t && check S ((v, false) :: ρ) e

theorem sound (S : Sys) (c : Cert) :
    ∀ (ρ : List (Nat × Bool)) (f : Nat → Bool),
      Valid S f → Agrees f ρ → check S ρ c = true → False := by
  induction c with
  | pair i j =>
    intro ρ f hf ha hc
    simp only [check, Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq] at hc
    obtain ⟨⟨⟨⟨hi, hj⟩, ho⟩, vi⟩, vj⟩ := hc
    exact hf.1 i j hi hj ho ⟨val_agrees ha vi, val_agrees ha vj⟩
  | triad i j k =>
    intro ρ f hf ha hc
    simp only [check, Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq] at hc
    obtain ⟨⟨⟨⟨⟨⟨⟨⟨hi, hj⟩, hk⟩, oij⟩, oik⟩, ojk⟩, vi⟩, vj⟩, vk⟩ := hc
    have fi := val_agrees ha vi
    have fj := val_agrees ha vj
    have fk := val_agrees ha vk
    rcases hf.2 i j k hi hj hk oij oik ojk with h | h | h
    · rw [fi] at h; cases h
    · rw [fj] at h; cases h
    · rw [fk] at h; cases h
  | split v t e iht ihe =>
    intro ρ f hf ha hc
    simp only [check, Bool.and_eq_true] at hc
    cases hv : f v with
    | true => exact iht ((v, true) :: ρ) f hf (agrees_cons ha hv) hc.1
    | false => exact ihe ((v, false) :: ρ) f hf (agrees_cons ha hv) hc.2

/-- The checker is sound: a certificate that passes from the empty assignment proves that
the system has no KS colouring. -/
theorem uncolourable_of_check (S : Sys) (c : Cert) (h : check S [] c = true) :
    Uncolourable S := by
  intro ⟨f, hf⟩
  exact sound S c [] f hf (agrees_nil f) h

/-! ### Rays with coordinates in `ℤ[√d]`

A coordinate `(a, b)` stands for `a + b√d`.  For `d` a non-square integer, `a + b√d = 0`
exactly when `a = b = 0`, so the test below is orthogonality of real vectors.  For rays with
integer coordinates take `b = 0`; then `d` plays no role. -/

abbrev Coord := Int × Int
abbrev Ray := Coord × Coord × Coord

def mul (d : Int) (x y : Coord) : Coord := (x.1 * y.1 + d * (x.2 * y.2), x.1 * y.2 + x.2 * y.1)

def dot (d : Int) (u v : Ray) : Coord :=
  let p := mul d u.1 v.1
  let q := mul d u.2.1 v.2.1
  let r := mul d u.2.2 v.2.2
  (p.1 + q.1 + r.1, p.2 + q.2 + r.2)

def orthB (d : Int) (u v : Ray) : Bool :=
  let s := dot d u v
  s.1 == 0 && s.2 == 0

def zeroRay : Ray := ((0, 0), (0, 0), (0, 0))

/-- The system of a list of rays over `ℤ[√d]`. -/
def sysOf (d : Int) (rays : List Ray) : Sys :=
  ⟨rays.length, fun i j => orthB d (rays.getD i zeroRay) (rays.getD j zeroRay)⟩

end KS
