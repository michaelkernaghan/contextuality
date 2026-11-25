"""Round 8: review of the version 12 draft.

Version 12 is version 11.1 with (1) a new opening section, the Prolegomena, abridged from the
companion note idea/cube_idea.tex, and (2) a change of vocabulary through the whole paper
(alphabet/letter/word/pool -> coordinate values/coordinate value/grid point/grid; raw pool ->
grid; completed pool -> completed grid).  No theorem, proof, table or number is meant to change.
This round asks the reviewer to attack the new section and to find any place where the renaming
changed what a sentence says.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import oxford_review_v10 as O

MAIN = "algebraic_islands_v12.tex"

PROMPT = r"""You are conducting an AGGRESSIVE Oxford-style challenge review of the VERSION 12 DRAFT of "The Algebraic Landscape of Kochen-Specker Sets in Dimension Three". You reviewed version 11 in rounds 6 and 7 (reports in paper/reviews/ of the repository C:\Users\Michael Kernaghan\contextuality). Version 12 claims to be version 11.1 with exactly two changes. (1) A new Section 1, "Prolegomena" (paper/v12_s0_prolegomena.tex), abridged from a companion note (idea/cube_idea.tex); the Introduction is now Section 2 and has lost its "alphabet" paragraph and two figures, which moved into the Prolegomena. (2) A change of vocabulary through the whole paper: "alphabet" -> "coordinate values" (of a grid); "letter"/"symbol" -> "coordinate value"; "word" -> "grid point"; "pool" and "raw pool" -> "grid"; "completed pool" -> "completed grid"; "two-symbol alphabets" -> "grids with two coordinate values", and likewise for three; "conjugate-closed alphabets" -> "conjugate-closed grids". The author states that no theorem, proof, table or number was changed. All of the new text and the renaming were produced with a large language model, much of the renaming by scripted replacement; treat every changed sentence as unverified.

Version 12 sources: paper/algebraic_islands_v12.tex and paper/v12_*.tex. Version 11.1 sources for comparison: paper/algebraic_islands_v11.tex and paper/v11_*.tex (git tag v11.1). Do not re-review the mathematics of the theorems or the Lean proofs, which you have passed. Do not run lake build. Be specific, quote the paper, and where a short calculation settles a point, do it and show it.

STEP 1 -- THE PROLEGOMENA. Read it as a hostile referee. For every factual sentence say whether it is correct, and whether it agrees with the theorems and definitions later in the paper. In particular:
(a) Section 1.1: the cube versus the sphere (normalising by the largest coordinate): correct as worded, including for the phrase "the largest coordinate has size x" when the ray has no coordinate equal to x?
(b) Section 1.2: the rule and its two clauses; the claim that two orthogonal rays of a finite set "belong to a triad of space whose third ray may be absent" and are still forbidden to be both colored; the spin-one statement (squares of spin components along three orthogonal directions commute, eigenvalues 0 and 1 in units of hbar^2, sum 2); the convention that the colored ray is the direction with square 0 and that this is f = 1 in the formal definition of a coloring in Section 3; the statement of what a KS set excludes.
(c) Section 1.3: the definitions of coordinate value, grid point, grid, completed grid. Do they agree exactly with the formal definitions in "Definitions and methods" (S(A), completed grid)? Is "grid" used for a set of rays everywhere, or sometimes for the lines or for the list of numbers? Check the worked example by hand: with lines at 0, +-1, +-2, are (1,1,2) and (2,0,-1) grid points, orthogonal, and is the ray orthogonal to both (1,-5,2), and is that ray not a grid point? Is "49 rays ... (exceptions ... such as x = 1)" consistent with Theorem thm:twosymbol and its proof (x in {+-1, +-i})? Is the counting rule ("leave out 0 and take a value and its negative as one") consistent with every later use of "two coordinate values" and "three coordinate values", including the roots-of-unity grids and grids that lack some negatives? Is "one coordinate value can always be taken to be 1" right?
(d) Section 1.4: the two inner products; the paragraph beginning "The computation is always of the kind just made": is it true that a product of two grid points is a sum of at most three terms each a product of two coordinate values; that "there are finitely many such equations and they can be listed in full (Table tab:zerosums)"; that "it is at their solutions, and nowhere else, that orthogonal pairs are gained"; that "on the real line each equation has at most two solutions, so the positions at which anything can happen are finite in number"; and the last sentence "the grid is harder to color at these positions than elsewhere"? Does any of this overstate what Section 3 proves, or ignore coincidences of grid points?
(e) Section 1.5 and 1.6: the counts 13, 49, 145 and "in general 145"; "A grid that lacks some of the minus signs is part of one of these and needs no separate treatment"; "The hope"; "What was found": is each clause of the elimination statement ("not on the first rung, not on the second for any real or complex x (Theorem thm:twosymbol), and not on the third with real coordinate values (Theorem thm:threesymbol)") exactly what those theorems prove, for grids and not completed grids, and does the text make that restriction clear? Is "It must be sought on a grid outside these: one with more coordinate values, or with complex ones on the third rung" right, given completed grids and Theorem thm:conj(iii)? Is "every finite set of rays lies on some grid if enough lines are allowed" right?
(f) The closing paragraph ("Something was found that had not been looked for ... His set is thus not an isolated curiosity. It is one point of a circle."): is every clause supported by Theorems thm:twosymbol, thm:conj, thm:circle and Corollary cor:points? Is "On the second rung the positions at which the grid cannot be colored are separate points. On the third they are not." correct as a general statement, or only for the conjugate-closed family and trivially for the real family? Does "one point of a circle" overclaim or mislead (the 45 grid points collapse to 33 rays at x = sqrt 2; and there is a second, different circle |x|^2 = 1/2 carrying the Gould-Aravind family through Peres's set)?
(g) Does the Prolegomena duplicate or contradict the Introduction, the Definitions, or the Conclusion? Is anything defined twice in incompatible ways? Is the section too long or pitched wrongly for a research paper, and what would you cut?

STEP 2 -- THE RENAMING. Compare each v12 file with its v11 counterpart (a diff will show the changed lines). (a) List every sentence whose MEANING changed, became false, became ambiguous or became ungrammatical because of the renaming. Look especially for: "raw pool" -> "grid" where the distinction from the completed grid mattered; "coordinates in an alphabet" -> "a set on a grid"; "three nonzero letters up to sign" -> "three coordinate values"; "word" -> "grid point" where a word was a triple and several words can be the same ray (proofs of thm:twosymbol, thm:threesymbol, thm:conj, thm:circle, Corollary cor:points); "the pool" -> "the grid" where the object was a completed pool or the set P in the certified-minima paragraph; "alphabet" -> "grid" in sentences that were about the list of numbers and not the set of rays (e.g. "Theorem thm:6n is a statement about ...", "the list of coordinate values, and not the field, is the operative choice", "The Gaussian grid {0,+-1,+-i,+-(1+i)}"); table captions and column headings (tab:alphabets, tab:twosymbol, tab:threesymbol, tab:conj, tab:catalogue, tab:profiles). (b) List every place where an old term survives and say whether it is one of the intended survivals (the mapping sentence in Section 1.3; "alphabets, as grids were then called" in the Introduction; the note at the head of the corrections appendix; quoted claims and names of old surveys in that appendix; labels, script names, Lean names, figure file names) or a leftover. (c) List inconsistent usage: "grid" versus "completed grid", "coordinate value" shortened to "value", "set" as a column heading, "the Eisenstein values", "the case of CK-31", etc.

STEP 3 -- NOTHING ELSE CHANGED. Confirm or refute: every theorem statement, proof step, table entry and number of v11.1 is unchanged in v12 apart from the vocabulary. Report any number, sign, exponent, reference or label that differs. Check that every cross-reference still points at the right object after the renumbering of sections (the Introduction is now Section 2), including "Section 1.2"-style references and the figures fig:generic and fig:triptych, which moved.

STEP 4 -- ABSTRACT AND INTRODUCTION. Is every clause of the new abstract a correct statement of a theorem as proved? Is the new sentence in "Relation to earlier versions" ("The present version adds the prolegomena and renames the objects as stated there; no theorem, proof or number is changed") true?

STEP 5 -- VERDICT. Is version 12 fit to replace version 11.1 on arXiv? What must change first? Is the new vocabulary an improvement for a specialist reader, or does it cost precision anywhere?

OUTPUT FORMAT.
1. Up-front verdict on each of: the Prolegomena; the renaming; "nothing else changed". One of CORRECT AS STATED / CORRECT WITH WORDING FIXES / OVERCLAIMS / WRONG, with a one-line justification each.
2. A table of actionable issues: | Priority (High/Med/Low) | Step | Where (file and line or section) | Issue (quote the paper) | Suggested fix |. Separate demonstrated errors from unsupported claims and from things you could not check.
3. A short list: claims you independently confirmed, with the method used.
4. The Step 5 answer as short prose.

Do not flatter. Do not equivocate. If a part is solid, say so once and move on."""


def assemble() -> str:
    tex = (O.PAPER / MAIN).read_text(encoding="utf-8")

    def inline(m: "re.Match[str]") -> str:
        f = O.PAPER / m.group(1)
        return f.read_text(encoding="utf-8") if f.exists() else m.group(0)
    for _ in range(2):
        tex = re.sub(r"\\input\{([^}]+)\}", inline, tex)
    return tex


def main() -> int:
    tex = assemble()
    hits = [(i, ln) for i, ln in enumerate(tex.splitlines(), 1)
            for p in O.INJECTION if re.search(p, ln, re.IGNORECASE)]
    if hits:
        print("Injection pre-scan flagged %d line(s); aborting." % len(hits))
        for i, ln in hits[:20]:
            print("  %5d  %s" % (i, ln.strip()[:100]))
        return 1
    text = O.strip_latex(tex)
    print("Extracted %d words from the assembled v12 draft" % len(text.split()))
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "algebraic_islands_v12.txt"
        f.write_text(text, encoding="utf-8")
        cmd = [sys.executable, str(O.REVIEWER), str(f), "--prompt", PROMPT, "--model", O.MODEL,
               "--timeout", "3300"]
        return subprocess.run(cmd).returncode


if __name__ == "__main__":
    raise SystemExit(main())
