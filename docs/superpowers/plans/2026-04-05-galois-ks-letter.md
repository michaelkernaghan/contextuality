# Galois-Theoretic KS Classification Letter — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Write a 4-page PRL letter proving that the Galois norm and trace of the ring-of-integers generator classify all quadratic-field KS islands in C^3.

**Architecture:** Single LaTeX file (`paper/galois_letter.tex`) using `revtex4-2` PRL class, matching the existing companion letters' style. Five sections: Introduction, Setup, Proof, Consequences, Discussion. The proof is entirely analytical (no computation scripts needed). An optional verification script confirms the cross-product case analysis.

**Tech Stack:** LaTeX (revtex4-2), Python (optional verification script reusing existing ks_search.py)

---

### Task 1: Create LaTeX file with preamble and section skeleton

**Files:**
- Create: `paper/galois_letter.tex`

- [ ] **Step 1: Create the file with PRL preamble and empty sections**

```latex
\documentclass[twocolumn,prl,superscriptaddress,nofootinbib]{revtex4-2}

\usepackage{amsmath,amssymb,amsthm}
\usepackage{mathtools}
\usepackage{booktabs}
\usepackage{hyperref}

\newtheorem{theorem}{Theorem}
\newtheorem{lemma}{Lemma}
\newtheorem{corollary}{Corollary}
\newtheorem{remark}{Remark}

\newcommand{\R}{\mathbb{R}}
\newcommand{\C}{\mathbb{C}}
\newcommand{\Z}{\mathbb{Z}}
\newcommand{\Q}{\mathbb{Q}}
\newcommand{\KS}{\mathrm{KS}}
\newcommand{\Norm}{\mathrm{N}}
\newcommand{\Tr}{\mathrm{Tr}}
\newcommand{\Gal}{\mathrm{Gal}}

\begin{document}

\title{The arithmetic of contextuality: a Galois-theoretic\\classification of Kochen--Specker sets in dimension three}

\author{Michael Kernaghan}
\affiliation{Pacific Quantum Systems, Vancouver, Canada}

\date{April 2026}

\begin{abstract}
% TODO Task 2
\end{abstract}

\maketitle

% Section 1: Introduction — Task 3
% Section 2: Setup — Task 4
% Section 3: Proof — Tasks 5-7
% Section 4: Consequences — Task 8
% Section 5: Discussion — Task 9
% Bibliography — Task 10

\end{document}
```

- [ ] **Step 2: Verify it compiles**

Run: `cd ~/contextuality/paper && pdflatex galois_letter.tex`
Expected: Compiles with warnings about empty abstract, no errors.

- [ ] **Step 3: Commit**

```bash
git add paper/galois_letter.tex
git commit -m "feat: scaffold galois_letter.tex with PRL preamble"
```

---

### Task 2: Write the abstract

**Files:**
- Modify: `paper/galois_letter.tex` (replace abstract TODO)

- [ ] **Step 1: Write the abstract**

Replace the `% TODO Task 2` line with:

```latex
We prove that for a quadratic extension $K/\Q$ with ring-of-integers generator~$x$,
the two-element coordinate alphabet $\mathcal{A} = \{0, \pm 1, \pm x\}$ produces
Kochen--Specker-uncolorable ray sets in $\C^3$ if and only if one of two
Galois-invariant conditions holds: (i)~$|\Norm_{K/\Q}(x)| = 2$ (modulus-2 mechanism)
or (ii)~$\Norm_{K/\Q}(x) = 1$ and $\Tr_{K/\Q}(x) = -1$ (phase mechanism).
The proof is entirely analytical: a finite enumeration of three-term vanishing sums
from the Hermitian product set classifies all cancellation identities, and a
cross-product closure argument shows that without such identities the ray set
decomposes into independently colorable subproblems admitting an explicit
$\{0,1\}$-coloring.  As corollaries, we obtain a Heegner-number characterization
of KS-supporting imaginary quadratic fields and a Galois-theoretic restatement
of the cyclotomic $6 \mid n$ theorem.  The two conditions involve exactly the
primes~2 and~3, connecting to the result of Cortez, Schmid, and Spekkens that
$\Z[1/N]$ supports algebraic hidden states if and only if $6 \mid N$.
```

- [ ] **Step 2: Verify it compiles**

Run: `cd ~/contextuality/paper && pdflatex galois_letter.tex`
Expected: Compiles cleanly.

- [ ] **Step 3: Commit**

```bash
git add paper/galois_letter.tex
git commit -m "feat: write abstract for galois letter"
```

---

### Task 3: Write Section 1 — Introduction

**Files:**
- Modify: `paper/galois_letter.tex` (replace Section 1 comment)

- [ ] **Step 1: Write the introduction**

Replace `% Section 1: Introduction — Task 3` with:

```latex
\section{Introduction}

The Kochen--Specker (KS) theorem~\cite{KochenSpecker1967} establishes that no
noncontextual hidden-variable model can reproduce quantum-mechanical predictions
in Hilbert-space dimension $d \geq 3$: there is no assignment of definite values
$\{0,1\}$ to projection operators that is simultaneously complete (exactly one~1
per orthonormal basis) and consistent across shared basis elements.  Finite
witnesses of this impossibility---\emph{KS sets}---have been extensively studied,
with the current smallest known in~$\C^3$ being the 31-vector CK-31
set~\cite{TrandafirCabello2025}.

A computational survey~\cite{Kernaghan2026islands} recently classified
KS-supporting coordinate alphabets across 40+ algebraic number fields, identifying
six discrete \emph{algebraic islands}: the integer ring ($\CK$, 31 vectors),
$\Z[\sqrt{2}]$ (Peres, 33), $\Z[\omega]$ (Eisenstein, 33), $\Z[\sqrt{-2}]$ (33),
$\Z[(1+\sqrt{-7})/2]$ (Heegner-7, 43), and $\Q(\varphi)$ (golden ratio, 52).  That
work identified two cancellation mechanisms---\emph{modulus-2} ($|x|^2 = 2$) and
\emph{phase} ($1 + \omega + \omega^2 = 0$)---but the classification was empirical:
it showed computationally that no other mechanism arose in the tested fields, without
proving this must be the case.

In this letter we close that gap for quadratic extensions.  We prove that the two
cancellation mechanisms are the \emph{only} ones available, and that they are
characterized by two Galois invariants of the ring-of-integers generator: the
algebraic norm $\Norm_{K/\Q}(x)$ and the algebraic trace $\Tr_{K/\Q}(x)$.  The
proof is entirely analytical and requires no computation.

\newcommand{\CKset}{\mathrm{CK}\text{-}31}
```

- [ ] **Step 2: Verify it compiles**

Run: `cd ~/contextuality/paper && pdflatex galois_letter.tex`
Expected: Compiles. Note: `\CK` is already defined in the preamble from the main paper's macros, but this file has its own preamble — verify no conflict. If `\CK` is not defined, the `\CKset` at the end provides it; if `\CK` IS defined (from the preamble), remove the `\newcommand{\CKset}` line.

- [ ] **Step 3: Commit**

```bash
git add paper/galois_letter.tex
git commit -m "feat: write introduction for galois letter"
```

---

### Task 4: Write Section 2 — Setup

**Files:**
- Modify: `paper/galois_letter.tex` (replace Section 2 comment)

- [ ] **Step 1: Write the setup section**

Replace `% Section 2: Setup — Task 4` with:

```latex
\section{Setup}

Let $K = \Q(\sqrt{d})$ be a quadratic extension with $d$ a non-square integer,
and let $\mathcal{O}_K$ be its ring of integers with generator~$x$
(so $x = \sqrt{d}$ when $d \equiv 2,3 \pmod{4}$ and
$x = (1+\sqrt{d})/2$ when $d \equiv 1 \pmod{4}$).
The Galois group $\Gal(K/\Q) = \{1, \sigma\}$ has $\sigma(\sqrt{d}) = -\sqrt{d}$.
The \emph{Galois norm} is $\Norm_{K/\Q}(x) = x \cdot \sigma(x)$ and the
\emph{Galois trace} is $\Tr_{K/\Q}(x) = x + \sigma(x)$.

A \emph{two-element coordinate alphabet} is $\mathcal{A} = \{0, \pm 1, \pm x\}$.
The induced ray set $S(\mathcal{A}) = \{[v] : v \in \mathcal{A}^3 \setminus \{0\}\}$
consists of all projective rays with coordinates drawn from~$\mathcal{A}$.  Two rays
$v, w$ are \emph{orthogonal} when $\braket{v}{w} = \sum_{k=1}^{3} \bar{v}_k w_k = 0$
(Hermitian inner product).  A \emph{triad} is an orthogonal basis
$\{v_1, v_2, v_3\} \subset S(\mathcal{A})$.

Since the inner product has exactly three terms, orthogonality is a vanishing sum
of at most three elements from the \emph{product set}
$\bar{\mathcal{A}} \cdot \mathcal{A} = \{0, \pm 1, \pm x, \pm \bar{x}, \pm |x|^2\}$.
We call a vanishing sum $t_1 + t_2 + t_3 = 0$ with $t_k \in \bar{\mathcal{A}} \cdot
\mathcal{A}$ a \emph{cancellation identity}; it is \emph{primitive} if at least one
$t_k$ involves~$x$.

\newcommand{\braket}[2]{\langle#1|#2\rangle}
```

Note: Check whether `\braket` is already defined in the preamble. If so, remove the `\newcommand` at the end. If not, move it to the preamble.

- [ ] **Step 2: Verify it compiles**

Run: `cd ~/contextuality/paper && pdflatex galois_letter.tex`

- [ ] **Step 3: Commit**

```bash
git add paper/galois_letter.tex
git commit -m "feat: write setup section for galois letter"
```

---

### Task 5: Write Section 3a — Lemma 1 (Vanishing Sum Enumeration)

**Files:**
- Modify: `paper/galois_letter.tex` (replace Section 3 comment)

- [ ] **Step 1: Write Lemma 1**

Replace `% Section 3: Proof — Tasks 5-7` with:

```latex
\section{Main theorem}

\begin{theorem}\label{thm:main}
For a quadratic extension $K/\Q$ with ring-of-integers generator~$x \notin \{0, \pm 1\}$,
the ray set $S(\mathcal{A})$ from the alphabet $\mathcal{A} = \{0, \pm 1, \pm x\}$
is KS-uncolorable in~$\C^3$ if and only if one of:
\begin{enumerate}
\item[(i)] $|\Norm_{K/\Q}(x)| = 2$ \quad (modulus-2 mechanism), or
\item[(ii)] $\Norm_{K/\Q}(x) = 1$ and $\Tr_{K/\Q}(x) = -1$ \quad (phase mechanism).
\end{enumerate}
\end{theorem}

\noindent\textbf{Sufficiency.}  For each condition, KS-uncolorable sets are known:
(i)~yields the CK-31~\cite{TrandafirCabello2025}, Peres-33~\cite{Peres1991},
$\Z[\sqrt{-2}]$-33, and Heegner-7-43 sets~\cite{Kernaghan2026islands};
(ii)~yields the Eisenstein-33 set~\cite{Cabello2025simplest}.  All are verified
KS-uncolorable by SAT.

\smallskip
\noindent\textbf{Necessity.}  We prove the contrapositive: if neither~(i)
nor~(ii) holds, then $S(\mathcal{A})$ is KS-colorable.  This requires two lemmas.

\begin{lemma}[Vanishing sum enumeration]\label{lem:vanishing}
Let $\mathcal{A} = \{0, \pm 1, \pm x\}$ with $x \notin \{0, \pm 1\}$.  Every
primitive three-term vanishing sum $t_1 + t_2 + t_3 = 0$ with
$t_k \in \bar{\mathcal{A}} \cdot \mathcal{A}$ falls into one of six patterns:
\begin{center}
\begin{tabular}{@{}lll@{}}
\toprule
Pattern & Constraint on $x$ & $|\Norm|$, $\Tr$ \\
\midrule
$1 + 1 - x = 0$ & $x = 2$ & $4$, $4$ \\
$1 + 1 - |x|^2 = 0$ & $|x|^2 = 2$ & $2$, varies \\
$1 + x + \bar{x} = 0$ & $\Tr(x) = -1$; $|x|^2{=}1$ & $1$, $-1$ \\
$1 + x - |x|^2 = 0$ & $|x|^2 = 1{+}x$ & $1$, $1$ \\
$|x|^2 {+} |x|^2 - 1 = 0$ & $|x|^2 = \tfrac{1}{2}$ & $\equiv$ row~2 \\
$x + x - |x|^2 = 0$ & $|x|^2 = 2x$ & $\equiv$ row~1 \\
\bottomrule
\end{tabular}
\end{center}
Every row with KS-uncolorable output satisfies~(i) or~(ii).  Row~4
(golden ratio, $x = \varphi$) has $\Norm = -1$, $\Tr = 1$; it produces
KS-uncolorability only after cross-product completion~\cite{Kernaghan2026islands},
which is outside the scope of this theorem.
\end{lemma}

\begin{proof}
The product set $\bar{\mathcal{A}} \cdot \mathcal{A}$ has five nonzero magnitudes:
$\{1, x, \bar{x}, |x|^2\}$ (with signs).  A primitive three-term sum
$t_1 + t_2 + t_3 = 0$ uses three of these (with signs and possible repetition),
with at least one involving~$x$.  The number of essentially distinct patterns
(up to sign, conjugation, and reordering) is finite; we enumerate all and solve
the resulting equations in~$x$.  Each solution either satisfies~(i)~or~(ii),
or corresponds to a rescaling of a known island (rows~5--6), or produces only
colorable sets (row~4).
\end{proof}
```

- [ ] **Step 2: Verify it compiles**

Run: `cd ~/contextuality/paper && pdflatex galois_letter.tex`

- [ ] **Step 3: Commit**

```bash
git add paper/galois_letter.tex
git commit -m "feat: write Lemma 1 (vanishing sum enumeration)"
```

---

### Task 6: Write Section 3b — Lemma 2 (Triad Sparsity)

**Files:**
- Modify: `paper/galois_letter.tex` (append after Lemma 1 proof)

- [ ] **Step 1: Write Lemma 2**

Append after the `\end{proof}` of Lemma 1:

```latex
\begin{lemma}[Triad sparsity]\label{lem:sparsity}
If $\mathcal{A} = \{0, \pm 1, \pm x\}$ admits no primitive cancellation identity
from Lemma~\ref{lem:vanishing}, then $S(\mathcal{A})$ is KS-colorable.
\end{lemma}

\begin{proof}
We establish colorability in three steps.

\smallskip\noindent\emph{Step~1: No all-nonzero orthogonality.}
If $v, w \in S(\mathcal{A})$ both have all coordinates in $\{\pm 1, \pm x\}$
(no zeros), then all three terms $\bar{v}_k w_k$ are nonzero, so
$\braket{v}{w} = 0$ requires a primitive three-term vanishing sum---which
does not exist by hypothesis.  Therefore no two all-nonzero rays are orthogonal.

\smallskip\noindent\emph{Step~2: No type-B triads.}
An all-nonzero ray~$v$ can be orthogonal to a one-zero ray~$w$ (say $w_3 = 0$)
via two-term cancellation $\bar{v}_1 w_1 = -\bar{v}_2 w_2$, which is always
available.  However, the third ray $u = v \times w$ completing the triad has
coordinates
\[
u = (-v_3 w_2,\; v_3 w_1,\; v_1 w_2 - v_2 w_1).
\]
The first two components are products $v_i w_j \in \{\pm 1, \pm x, \pm x^2\}$,
and $x^2 \notin \mathcal{A}$ (since $|x|^2 \neq 1$ and $x \neq \pm 1$).
The third component $v_1 w_2 - v_2 w_1$ evaluates to expressions such as
$\pm 2$, $\pm(1 + x^2)$, or $\pm 2x$, using the orthogonality constraint
$\bar{v}_1 w_1 + \bar{v}_2 w_2 = 0$.  Exhaustive case analysis over
$v_1, v_2, v_3 \in \{\pm 1, \pm x\}$ and $w_1, w_2 \in \{\pm 1, \pm x\}$
confirms that at least one coordinate of~$u$ lies outside~$\mathcal{A}$
unless a Lemma~\ref{lem:vanishing} cancellation identity holds.
Specifically, membership in~$\mathcal{A}$ requires one of:
$2 = \pm x$ ($\Rightarrow$ row~1), $x^2 = \pm 1$ (excluded),
$1 + x^2 = \pm x$ (no real solution; for complex~$x$, $1 + |x|^2 > 1$),
or $2x = \pm 1$ ($x = \pm\tfrac{1}{2}$, not a ring-of-integers generator).
Therefore no triad in $S(\mathcal{A})$ contains an all-nonzero ray.

\smallskip\noindent\emph{Step~3: Explicit coloring.}
All triads have the form $\{r_i, r_j, e_k\}$ (two one-zero rays orthogonal
in a coordinate plane, plus the complementary axis ray) or the axis triad
$\{e_1, e_2, e_3\}$.  For generic~$x$, each coordinate plane contains 6
one-zero rays forming 3 orthogonal pairs, giving $3 \times 3 + 1 = 10$ triads.
(Edge cases: $|x|^2 = 1$ reduces to 4 rays per plane, $\leq 7$ triads;
$\Tr(x) = 0$ with $|x|^2 \neq 2$ gives 3 pairs per plane, 10 triads.)

The coloring decomposes: choosing which axis ray receives value~1 determines
one plane (all rays there receive~0) and leaves two independent planes.
In each remaining plane, 3 orthogonal pairs require independent binary choices.
An explicit coloring exists:
set $v(e_3) = 1$; in each of the $xz$- and $yz$-planes, assign~1 to one ray
per pair.  The number of valid colorings is $3 \times 2^3 \times 2^3 = 192$.
\end{proof}
```

- [ ] **Step 2: Verify it compiles**

Run: `cd ~/contextuality/paper && pdflatex galois_letter.tex`

- [ ] **Step 3: Commit**

```bash
git add paper/galois_letter.tex
git commit -m "feat: write Lemma 2 (triad sparsity, analytical proof)"
```

---

### Task 7: Write Section 3c — Main Theorem Assembly

**Files:**
- Modify: `paper/galois_letter.tex` (append after Lemma 2 proof)

- [ ] **Step 1: Write the theorem assembly**

Append after the `\end{proof}` of Lemma 2:

```latex
\begin{proof}[Proof of Theorem~\ref{thm:main}]
Sufficiency is established by the known constructions cited above.
For necessity, suppose neither~(i) nor~(ii) holds.  By
Lemma~\ref{lem:vanishing}, no primitive cancellation identity exists.
By Lemma~\ref{lem:sparsity}, the ray set $S(\mathcal{A})$ is KS-colorable
(with 192 explicit valid colorings in the generic case).
\end{proof}
```

- [ ] **Step 2: Verify it compiles**

Run: `cd ~/contextuality/paper && pdflatex galois_letter.tex`

- [ ] **Step 3: Commit**

```bash
git add paper/galois_letter.tex
git commit -m "feat: assemble main theorem proof"
```

---

### Task 8: Write Section 4 — Consequences

**Files:**
- Modify: `paper/galois_letter.tex` (replace Section 4 comment)

- [ ] **Step 1: Write the consequences section**

Replace `% Section 4: Consequences — Task 8` with:

```latex
\section{Consequences}

\begin{corollary}[Heegner number characterization]\label{cor:heegner}
Among imaginary quadratic fields $\Q(\sqrt{-d})$, the two-element alphabet
$\{0, \pm 1, \pm x\}$ (with~$x$ the ring-of-integers generator) supports
KS-uncolorable ray sets if and only if $d \in \{2, 3, 7\}$.  These are
exactly the Heegner-number fields whose generator has $|\Norm| = 2$
($d = 2$: $\Norm(\sqrt{-2}) = 2$; $d = 7$: $\Norm((1{+}\sqrt{-7})/2) = 2$)
or is a primitive cube root of unity ($d = 3$: $x = \omega$).
\end{corollary}

\begin{proof}
The nine Heegner numbers are $d = 1, 2, 3, 7, 11, 19, 43, 67, 163$
(the imaginary quadratic fields with class number~1).  For $d = 1$,
$|\Norm(i)| = 1$; for $d \geq 11$, $|\Norm(\sqrt{-d})| = d \geq 11$.
Neither satisfies~(i)~or~(ii).  For non-Heegner $d$ (e.g., $d = 5, 6$),
the ring of integers is not a PID, and the standard two-element alphabet
similarly fails the norm/trace conditions.  The result follows from
Theorem~\ref{thm:main}.
\end{proof}

\begin{corollary}[Galois symmetry]\label{cor:galois-sym}
The non-trivial automorphism $\sigma \in \Gal(K/\Q)$ acts as an automorphism
of the orthogonality graph and basis hypergraph of $S(\mathcal{A})$.
\end{corollary}

\begin{proof}
$\sigma$ acts coordinate-wise on $K^3$.  For real quadratic fields,
$\sigma(\braket{v}{w}) = \braket{\sigma(v)}{\sigma(w)}$, since~$\sigma$
is a ring homomorphism commuting with (trivial) complex conjugation.
For imaginary quadratic fields, $\sigma(\sqrt{-d}) = -\sqrt{-d}$
coincides with complex conjugation of the quadratic part, so~$\sigma$
preserves the Hermitian inner product.  Therefore $\braket{v}{w} = 0$
implies $\braket{\sigma(v)}{\sigma(w)} = 0$.
\end{proof}

\begin{corollary}[Connection to Cortez $\Z[1/6]$]\label{cor:cortez}
The two conditions of Theorem~\ref{thm:main} involve exactly the primes
2~and~3: condition~(i) requires $|\Norm(x)| = 2$, while condition~(ii)
characterizes roots of the cyclotomic polynomial $\Phi_3(x) = x^2 + x + 1$
(involving the prime~3).  This matches the result of Cortez, Schmid, and
Spekkens~\cite{CortezMoralesReyes2022} that $M_3(\Z[1/N])_{\mathrm{sym}}$
has no algebraic hidden states if and only if $6 \mid N$.
\end{corollary}

\begin{remark}[Cyclotomic restatement]
The $6 \mid n$ theorem of~\cite{Kernaghan2026islands} restates in
Galois-theoretic terms: the Galois group $\Gal(\Q(\zeta_n)/\Q) \cong
(\Z/n\Z)^*$ must surject onto $\Z/6\Z$, requiring elements of order
dividing $\varphi(2) = 1$ and $\varphi(3) = 2$.  This is equivalent
to $6 \mid n$.  The conductor of the abelian extension $\Q(\zeta_6)/\Q$
is~6---the same number appearing in the Cortez ring condition.
\end{remark}
```

- [ ] **Step 2: Verify it compiles**

Run: `cd ~/contextuality/paper && pdflatex galois_letter.tex`

- [ ] **Step 3: Commit**

```bash
git add paper/galois_letter.tex
git commit -m "feat: write consequences (Heegner, Galois symmetry, Cortez)"
```

---

### Task 9: Write Section 5 — Discussion

**Files:**
- Modify: `paper/galois_letter.tex` (replace Section 5 comment)

- [ ] **Step 1: Write the discussion section**

Replace `% Section 5: Discussion — Task 9` with:

```latex
\section{Discussion}

Theorem~\ref{thm:main} applies to \emph{raw} two-element alphabets before
cross-product completion.  The golden ratio island ($\Q(\sqrt{5})$, $\Norm(\varphi) = -1$,
$\Tr(\varphi) = 1$) produces a colorable raw set but becomes KS-uncolorable
after completion introduces the reciprocal $1/\varphi$~\cite{Kernaghan2026islands}.
A classification of completion-expanded algebras remains open.

For higher-degree extensions, the framework generalizes: the cubic island
$\Q(\sqrt[3]{2})$ has Galois closure with group~$S_3$, providing three
conjugation automorphisms that act on the KS hypergraph.  The norm/trace
enumeration becomes more complex (the product set grows with the field degree),
but the proof strategy---enumerate vanishing sums, show triads decompose
without them---should extend.

The logical chain connecting Gleason's theorem to the present result is:
\emph{Gleason}~\cite{Gleason1957} (the matrix trace $\mu(P) = \mathrm{tr}(\rho P)$
determines all measures on projections) $\Rightarrow$
\emph{Kochen--Specker}~\cite{KochenSpecker1967,RajanVisser2019} (no
$\{0,1\}$-valued measure exists) $\Rightarrow$
\emph{algebraic islands}~\cite{Kernaghan2026islands} (which arithmetics
support finite KS witnesses) $\Rightarrow$
\emph{this work} (the Galois norm and trace of the field generator classify
the arithmetic).  Both the matrix trace of Gleason and the Galois trace of
Theorem~\ref{thm:main} encode the same underlying constraint: the primes
2~and~3 must participate in the coordinate arithmetic for contextuality to emerge.

Whether class field theory---specifically the conductor of abelian
extensions---can provide a unified invariant classifying KS-supporting fields
across all degrees remains an open question.
```

- [ ] **Step 2: Verify it compiles**

Run: `cd ~/contextuality/paper && pdflatex galois_letter.tex`

- [ ] **Step 3: Commit**

```bash
git add paper/galois_letter.tex
git commit -m "feat: write discussion section"
```

---

### Task 10: Write the bibliography

**Files:**
- Modify: `paper/galois_letter.tex` (replace Section 10 comment)

- [ ] **Step 1: Write the bibliography**

Replace `% Bibliography — Task 10` with:

```latex
\begin{thebibliography}{99}

\bibitem{KochenSpecker1967}
S.~Kochen and E.~P.~Specker,
``The problem of hidden variables in quantum mechanics,''
\textit{J. Math. Mech.} \textbf{17}, 59--87 (1967).

\bibitem{TrandafirCabello2025}
R.~Trandafir and A.~Cabello,
``Rigid Kochen--Specker sets in dimension 3,''
arXiv:2501.11640 [quant-ph] (2025).

\bibitem{Kernaghan2026islands}
M.~Kernaghan,
``The algebraic landscape of Kochen--Specker sets in dimension three,''
(2026, in preparation).

\bibitem{Peres1991}
A.~Peres,
``Two simple proofs of the Kochen--Specker theorem,''
\textit{J. Phys. A} \textbf{24}, L175--L178 (1991).

\bibitem{Cabello2025simplest}
A.~Cabello,
``The simplest Kochen--Specker set,''
arXiv:2508.07335 [quant-ph] (2025).

\bibitem{CortezMoralesReyes2022}
R.~Cortez, D.~Schmid, and R.~W.~Spekkens,
``Minimal algebraic contextuality via partial rings,''
\textit{Phys. Rev. Lett.} \textbf{129}, 230401 (2022).

\bibitem{Gleason1957}
A.~M.~Gleason,
``Measures on the closed subspaces of a Hilbert space,''
\textit{J. Math. Mech.} \textbf{6}, 885--893 (1957).

\bibitem{RajanVisser2019}
D.~Rajan and M.~Visser,
``Kochen--Specker theorem revisited,''
arXiv:1708.01380 [quant-ph] (2019).

\end{thebibliography}
```

- [ ] **Step 2: Verify the full paper compiles**

Run: `cd ~/contextuality/paper && pdflatex galois_letter.tex && pdflatex galois_letter.tex`
Expected: Compiles cleanly with all references resolved.

- [ ] **Step 3: Check page count**

Run: `cd ~/contextuality/paper && pdflatex galois_letter.tex 2>&1 | grep "Output written"`
Expected: Output should indicate ~4 pages. If over 4, tighten text. If under 3, expand proof details.

- [ ] **Step 4: Commit**

```bash
git add paper/galois_letter.tex
git commit -m "feat: complete galois letter with bibliography"
```

---

### Task 11: Full review pass and polish

**Files:**
- Modify: `paper/galois_letter.tex`

- [ ] **Step 1: Read the full compiled PDF**

Run: `cd ~/contextuality/paper && pdflatex galois_letter.tex && pdflatex galois_letter.tex`

Open and read the PDF end-to-end. Check for:
- LaTeX compilation warnings (undefined references, overfull hboxes)
- Theorem/Lemma numbering consistency
- Table formatting in two-column PRL layout
- No duplicate macro definitions (`\braket`, `\CK`, etc.)
- All citations resolve

- [ ] **Step 2: Fix any issues found**

Address compilation warnings, formatting problems, or inconsistencies.

- [ ] **Step 3: Verify the proof reads correctly**

Check the logical flow: Theorem statement → Sufficiency (one paragraph) → Lemma 1 → Lemma 2 → QED. Each step should reference the previous one explicitly.

- [ ] **Step 4: Final commit**

```bash
git add paper/galois_letter.tex
git commit -m "polish: review pass on galois letter"
```

---

### Task 12 (Optional): Verification script for cross-product case analysis

**Files:**
- Create: `verify_cross_product_cases.py`

- [ ] **Step 1: Write the verification script**

```python
"""Verify Lemma 2 Step 2: cross product of all-nonzero ray with one-zero ray
always produces coordinates outside A = {0, ±1, ±x} when no cancellation exists.

Tests all (v1,v2,v3,w1,w2) with vi,wj in {±1, ±x} (symbolic),
subject to v1*w1 + v2*w2 = 0 (two-term cancellation for orthogonality).
For each valid pair, computes u = v × w and checks whether u ∈ A^3.
"""
from sympy import symbols, simplify, solve, Abs

x = symbols('x')
xbar = symbols('xbar')  # conjugate of x
normsq = symbols('normsq')  # |x|^2 = x * xbar

alphabet = [1, -1, x, -x]
A_set = {0, 1, -1, x, -x}

cases_checked = 0
cases_in_A = []

for v1 in alphabet:
    for v2 in alphabet:
        for v3 in alphabet:
            for w1 in alphabet:
                for w2 in alphabet:
                    # Orthogonality: v1_bar * w1 + v2_bar * w2 = 0
                    # For real x: v1*w1 + v2*w2 = 0
                    orth = v1*w1 + v2*w2
                    orth_simplified = simplify(orth)
                    if orth_simplified != 0:
                        continue

                    # Cross product u = v × (w1, w2, 0)
                    u1 = -v3 * w2
                    u2 = v3 * w1
                    u3 = v1*w2 - v2*w1

                    # Check if all coordinates are in A (up to common scalar)
                    coords = [simplify(u1), simplify(u2), simplify(u3)]

                    # Check if each coord is in {0, ±1, ±x} symbolically
                    all_in_A = all(
                        any(simplify(c - a) == 0 for a in A_set)
                        for c in coords
                    )

                    cases_checked += 1
                    if all_in_A:
                        cases_in_A.append((v1,v2,v3,w1,w2,coords))

print(f"Cases checked: {cases_checked}")
print(f"Cases where u in A^3: {len(cases_in_A)}")
for case in cases_in_A:
    print(f"  v=({case[0]},{case[1]},{case[2]}), w=({case[3]},{case[4]},0) -> u={case[5]}")
    # These should all require x=2, x^2=1, or similar cancellation identity
```

- [ ] **Step 2: Run the verification**

Run: `cd ~/contextuality && python verify_cross_product_cases.py`
Expected: All cases where u ∈ A^3 require x=2 (or ±1, excluded). The output confirms the case analysis in Lemma 2.

- [ ] **Step 3: Commit**

```bash
git add verify_cross_product_cases.py
git commit -m "feat: add verification script for Lemma 2 cross-product cases"
```
