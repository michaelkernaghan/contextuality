"""Generate the alphabet-cube figures (TikZ, standalone) for the v10 paper.

Generalises the two cube diagrams in Peres, "Quantum Theory: Concepts and
Methods" (Fig. 7.2, p. 198 and Plate II, p. 114). A ray whose coordinates are a
word over {0, +-1, +-x} pierces the cube [-x, x]^3 at a point of the 5 x 5
lattice drawn on each face, whose lines sit at 0, +-1 and +-x. Changing x only
slides the two inner lines (they sit at the fraction 1/x of the half-edge);
the 49 lattice rays and their labels do not change, the orthogonalities do.

Writes paper/figures/alphabet_cube_generic.tex and alphabet_cube_triptych.tex.
Compile each with pdflatex. Coordinates of CK-31 are the repo's CK31_INT list.

Run:  python make_alphabet_cube_figures.py
"""
import itertools
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent / "paper" / "figures"
X = "x"                      # the symbolic letter
AZ, EL = math.radians(-32.0), math.radians(24.0)

CK31_INT = [
    (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 1, -1), (0, 1, 2), (0, 2, -1),
    (1, 0, 0), (1, 0, 1), (1, 0, -1), (1, 0, 2), (1, 0, -2),
    (1, 1, 0), (1, 1, 1), (1, 1, -1), (1, 1, 2), (1, -1, 0),
    (1, -1, 1), (1, -1, -1), (1, -1, -2), (1, 2, 0), (1, 2, -1),
    (1, -2, 0), (1, -2, 1), (2, 0, 1), (2, 0, -1), (2, 1, 0),
    (2, 1, 1), (2, 1, -1), (2, -1, 0), (2, -1, 1), (2, -1, -1),
]

# ---- words -----------------------------------------------------------------
# A letter is (sign, kind) with kind in {0, 1, X}; a word is three letters.


def canon(word):
    """Projective canonical form: no common factor x, first nonzero letter > 0."""
    kinds = {k for s, k in word if s}
    if kinds == {X}:                                   # (x, x, 0) is the ray (1, 1, 0)
        word = tuple((s, 1 if s else 0) for s, k in word)
    lead = next(s for s, k in word if s)
    return tuple((s * lead, k) for s, k in word)


def all_words():
    letters = [(0, 0), (1, 1), (-1, 1), (1, X), (-1, X)]
    return {canon(w) for w in itertools.product(letters, repeat=3) if any(s for s, k in w)}


def from_int(v):
    return canon(tuple((0, 0) if c == 0 else ((1 if c > 0 else -1), X if abs(c) == 2 else 1)
                       for c in v))


def kind_count(word):
    return sum(1 for s, k in word if k == 1), sum(1 for s, k in word if k == X)


POOL = all_words()
assert len(POOL) == 49, len(POOL)
# Peres-33: every pool ray except (1,1,1)-type and (1,x,x)-type (Peres 1991).
PERES33 = {w for w in POOL if kind_count(w) not in ((3, 0), (1, 2))}
assert len(PERES33) == 33, len(PERES33)
CK31 = {from_int(v) for v in CK31_INT}
assert len(CK31) == 31 and CK31 <= POOL, len(CK31)

# ---- geometry --------------------------------------------------------------


def proj(p):
    px, py, pz = p
    xr = px * math.cos(AZ) - py * math.sin(AZ)
    yr = px * math.sin(AZ) + py * math.cos(AZ)
    return (xr, pz * math.cos(EL) + yr * math.sin(EL))


def fmt(q):
    return "(%.4f,%.4f)" % q


# visible faces: (fixed axis, sign, in-plane axes)
FACES = [(0, +1, (1, 2)), (1, -1, (0, 2)), (2, +1, (0, 1))]


def face_point(face, a, b, h):
    axis, sign, (i, j) = face
    p = [0.0, 0.0, 0.0]
    p[axis], p[i], p[j] = sign * h, a, b
    return tuple(p)


def point_word(p, xval):
    """Word of the ray through a lattice point on the surface of [-x, x]^3."""
    word = []
    for c in p:
        if abs(c) < 1e-9:
            word.append((0, 0))
        elif abs(abs(c) - xval) < 1e-9:
            word.append((1 if c > 0 else -1, X))
        else:
            word.append((1 if c > 0 else -1, 1))
    return canon(tuple(word))


def cube(xval, scale, filled, labels, origin=(0.0, 0.0), dot=0.115, ticks_on="left"):
    """TikZ for one cube. `filled` is the set of words drawn as black dots; the
    rest of the 49-ray pool is drawn as open dots. `labels` are the five tick
    labels from -x up to x."""
    s = scale / xval                                  # every cube drawn the same size
    ox, oy = origin

    def P(p):
        u, v = proj(p)
        return (ox + s * u, oy + s * v)

    out = []
    ticks = [-xval, -1.0, 0.0, 1.0, xval]
    for face in FACES:
        for t in ticks:
            style = "line width=0.7pt" if abs(abs(t) - xval) < 1e-9 else "line width=0.35pt"
            out.append("\\draw[%s] %s -- %s;" % (
                style, fmt(P(face_point(face, t, -xval, xval))), fmt(P(face_point(face, t, xval, xval)))))
            out.append("\\draw[%s] %s -- %s;" % (
                style, fmt(P(face_point(face, -xval, t, xval))), fmt(P(face_point(face, xval, t, xval)))))
    seen = set()
    for face in FACES:
        axis, sign, (i, j) = face
        ei, ej = [0.0] * 3, [0.0] * 3
        ei[i], ej[j] = 1.0, 1.0
        (b0, b1), (c0, c1) = proj(tuple(ei)), proj(tuple(ej))   # disc drawn in the face plane
        cm = "%.4f,%.4f,%.4f,%.4f" % (b0, b1, c0, c1)
        for a in ticks:
            for b in ticks:
                p = face_point(face, a, b, xval)
                key = tuple(round(c, 6) for c in p)
                if key in seen:
                    continue
                seen.add(key)
                w = point_word(p, xval)
                q = P(p)
                if w in filled:
                    out.append("\\fill[cm={%s,%s}] (0,0) circle (%.3f);" % (cm, fmt(q), dot))
                else:
                    out.append("\\draw[cm={%s,%s},fill=white,line width=0.3pt] (0,0) circle (%.3f);"
                               % (cm, fmt(q), dot * 0.8))
    for t, lab in zip(ticks, labels):                 # letter ticks along one front edge
        if ticks_on == "left":
            q, where = P((-xval, -xval, t)), "left=2pt"
        else:
            q, where = P((t, -xval, -xval)), "below=3pt"
        out.append("\\node[%s,font=\\small] at %s {$%s$};" % (where, fmt(q), lab))
    return out, P


def standalone(body, path):
    doc = ["\\documentclass[tikz,border=4pt]{standalone}", "\\usepackage{amsmath,amssymb}",
           "\\usetikzlibrary{arrows.meta}", "\\begin{document}", "\\begin{tikzpicture}[line cap=round,line join=round]"]
    doc += body + ["\\end{tikzpicture}", "\\end{document}", ""]
    path.write_text("\n".join(doc), encoding="utf-8")
    print("wrote", path)


def generic_figure():
    xval, scale = 1.7, 2.6
    s = scale / xval
    body = []

    def P(p):
        u, v = proj(p)
        return (s * u, s * v)

    # hidden edges and the centre, so the cube reads as transparent
    h = xval
    back = (-h, h, -h)
    for other in ((h, h, -h), (-h, -h, -h), (-h, h, h)):
        body.append("\\draw[densely dashed,gray,line width=0.3pt] %s -- %s;" % (fmt(P(back)), fmt(P(other))))
    rays = [((h, 0, 0), "(1,0,0)", "right"), ((h, 1, 1), "(x,1,1)", "right"),
            ((h, -1, -1), "(x,\\bar 1,\\bar 1)", "right"), ((h, h, -1), "(x,x,\\bar 1)", "right"),
            ((0, 0, h), "(0,0,1)", "above"), ((-1, 1, h), "(\\bar 1,1,x)", "above"),
            ((h, -h, h), "(1,\\bar 1,1)", "above right"),
            ((0, -h, 0), "(0,1,0)", "below left"), ((-1, -h, 1), "(1,x,\\bar 1)", "left")]
    for p, _, _ in rays:                              # inside the cube: dashed
        body.append("\\draw[densely dashed,gray,line width=0.45pt] %s -- %s;" % (fmt(P((0, 0, 0))), fmt(P(p))))
    lines, _ = cube(xval, scale, POOL, ["-x", "-1", "0", "1", "x"], ticks_on="bottom")
    body += lines
    for p, lab, pos in rays:                          # outside the cube: arrow
        (u, v) = P(p)                                 # fixed drawn length, whatever the foreshortening
        r = math.hypot(u, v)
        tip = (u + 1.15 * u / r, v + 1.15 * v / r)
        body.append("\\draw[-{Stealth[length=5pt]},line width=0.8pt] %s -- %s "
                    "node[%s=1pt,font=\\footnotesize,fill=white,inner sep=1pt] {$%s$};"
                    % (fmt((u, v)), fmt(tip), pos, lab))
    body.append("\\fill[gray] %s circle (0.05);" % fmt(P((0, 0, 0))))
    standalone(body, OUT / "alphabet_cube_generic.tex")


def triptych():
    panels = [(math.sqrt(2), PERES33, ["-\\sqrt2", "-1", "0", "1", "\\sqrt2"],
               "$x=\\sqrt2$: Peres, 33 of 49"),
              (2.0, CK31, ["-2", "-1", "0", "1", "2"], "$x=2$: Conway--Kochen, 31 of 49"),
              (math.sqrt(3), set(), ["-\\sqrt3", "-1", "0", "1", "\\sqrt3"],
               "$x=\\sqrt3$: all 49 colorable")]
    body = []
    for n, (xval, filled, labels, title) in enumerate(panels):
        origin = (n * 6.6, 0.0)
        lines, P = cube(xval, 2.1, filled, labels, origin=origin)
        body += lines
        lo = P((xval, -xval, -xval))
        body.append("\\node[font=\\small] at (%.4f,%.4f) {%s};" % (origin[0], lo[1] - 0.75, title))
    standalone(body, OUT / "alphabet_cube_triptych.tex")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    generic_figure()
    triptych()
