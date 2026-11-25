"""Figures for the companion note idea/cube_idea.tex (TikZ, standalone, black and white).

Reads idea/idea_data.json (written by ks_idea_forcing.py), so the rays drawn in
Figure 5 are the rays that script checked, not a second list. Reuses the
projection of make_alphabet_cube_figures.py.

Run:  python ks_idea_forcing.py && python make_idea_figures.py
Exit status 0 means all seven figures were written and compiled.
"""
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

import make_alphabet_cube_figures as mc

ROOT = Path(__file__).resolve().parent
FIG = ROOT / "idea" / "figures"
DATA = ROOT / "idea" / "idea_data.json"
MIKTEX = Path.home() / "AppData/Local/Programs/MiKTeX/miktex/bin/x64/pdflatex.exe"
X = mc.X
fmt = mc.fmt


def to_word(strings):
    table = {"0": (0, 0), "1": (1, 1), "-1": (-1, 1), "x": (1, X), "-x": (-1, X)}
    return tuple(table[s] for s in strings)


def tex_word(w):
    def letter(s, k):
        body = "0" if s == 0 else ("x" if k == X else "1")
        return "\\bar %s" % body if s < 0 else body
    return "(" + ",".join(letter(s, k) for s, k in w) + ")"


# ---- cube helpers -------------------------------------------------------------


def projector(scale, origin=(0.0, 0.0)):
    def P(p):
        u, v = mc.proj(p)
        return (origin[0] + scale * u, origin[1] + scale * v)
    return P


def wireframe(P, h, hidden=True):
    """The twelve edges; the three that meet the hidden corner are dashed."""
    out = []
    back = (-h, h, -h)
    corners = [(a, b, c) for a in (-h, h) for b in (-h, h) for c in (-h, h)]
    for i, p in enumerate(corners):
        for q in corners[i + 1:]:
            if sum(1 for a, b in zip(p, q) if a != b) != 1:
                continue
            if back in (p, q):
                if hidden:
                    out.append("\\draw[densely dashed,gray,line width=0.3pt] %s -- %s;" % (fmt(P(p)), fmt(P(q))))
            else:
                out.append("\\draw[line width=0.7pt] %s -- %s;" % (fmt(P(p)), fmt(P(q))))
    return out


def face_cm(face):
    axis, sign, (i, j) = face
    ei, ej = [0.0] * 3, [0.0] * 3
    ei[i], ej[j] = 1.0, 1.0
    (b0, b1), (c0, c1) = mc.proj(tuple(ei)), mc.proj(tuple(ej))
    return "%.4f,%.4f,%.4f,%.4f" % (b0, b1, c0, c1)


def lattice_points(xval):
    """Visible lattice points of the cube [-x, x]^3: (face, point, word), each point once."""
    ticks = [-xval, -1.0, 0.0, 1.0, xval]
    seen, out = set(), []
    for face in mc.FACES:
        for a in ticks:
            for b in ticks:
                p = mc.face_point(face, a, b, xval)
                key = tuple(round(c, 6) for c in p)
                if key not in seen:
                    seen.add(key)
                    out.append((face, p, mc.point_word(p, xval)))
    return out


def grid_lines(P, xval):
    out = []
    ticks = [-xval, -1.0, 0.0, 1.0, xval]
    for face in mc.FACES:
        for t in ticks:
            style = "line width=0.7pt" if abs(abs(t) - xval) < 1e-9 else "line width=0.3pt,gray"
            out.append("\\draw[%s] %s -- %s;" % (style, fmt(P(mc.face_point(face, t, -xval, xval))),
                                                 fmt(P(mc.face_point(face, t, xval, xval)))))
            out.append("\\draw[%s] %s -- %s;" % (style, fmt(P(mc.face_point(face, -xval, t, xval))),
                                                 fmt(P(mc.face_point(face, xval, t, xval)))))
    return out


def state_cube(rays, state, numbers, ringed, scale, origin, title):
    """The 33 rays on the cube. state[i] is 1 (marked), 0 (unmarked) or absent (undecided).
    Returns (tikz lines, set of words drawn)."""
    xval = math.sqrt(2)
    P = projector(scale / xval, origin)
    index = {w: i for i, w in enumerate(rays)}
    out = grid_lines(P, xval)
    drawn, labelled = set(), set()
    for face, p, w in lattice_points(xval):
        if w not in index:
            continue
        i = index[w]
        drawn.add(w)
        cm, q = face_cm(face), P(p)
        if i in ringed:
            out.append("\\draw[cm={%s,%s},line width=0.5pt] (0,0) circle (0.21);" % (cm, fmt(q)))
        if state.get(i) == 1:
            out.append("\\fill[cm={%s,%s}] (0,0) circle (0.13);" % (cm, fmt(q)))
            if i in numbers and i not in labelled:
                labelled.add(i)
                out.append("\\node[font=\\footnotesize\\bfseries,fill=white,inner sep=0.8pt,circle] at (%.4f,%.4f) {%d};"
                           % (q[0] + 0.24, q[1] + 0.24, numbers[i]))
        elif state.get(i) == 0:
            out.append("\\draw[cm={%s,%s},fill=black!38,line width=0.3pt] (0,0) circle (0.11);" % (cm, fmt(q)))
        else:
            out.append("\\draw[cm={%s,%s},fill=white,line width=0.3pt] (0,0) circle (0.085);" % (cm, fmt(q)))
    lo = P((xval, -xval, -xval))
    out.append("\\node[font=\\small,align=center] at (%.4f,%.4f) {%s};" % (origin[0], lo[1] - 0.7, title))
    return out, drawn


# ---- flat faces ---------------------------------------------------------------


def flat_face(origin, half, ticks, maxval, special=None, labels=True, dot=0.07):
    """One face seen square-on. ticks: list of (value, label). special: {(a, b): tikz shape}."""
    ox, oy = origin
    s = half / maxval
    out = []
    for t, _ in ticks:
        style = "line width=0.7pt" if abs(abs(t) - maxval) < 1e-9 else "line width=0.3pt,gray"
        out.append("\\draw[%s] (%.4f,%.4f) -- (%.4f,%.4f);" % (style, ox + s * t, oy - half, ox + s * t, oy + half))
        out.append("\\draw[%s] (%.4f,%.4f) -- (%.4f,%.4f);" % (style, ox - half, oy + s * t, ox + half, oy + s * t))
    for a, _ in ticks:
        for b, _ in ticks:
            key = next((k for k in (special or {}) if abs(k[0] - a) < 1e-9 and abs(k[1] - b) < 1e-9), None)
            x, y = ox + s * a, oy + s * b
            if key is None:
                out.append("\\draw[fill=white,line width=0.3pt] (%.4f,%.4f) circle (%.3f);" % (x, y, dot))
            elif special[key] == "square":
                out.append("\\fill (%.4f,%.4f) rectangle (%.4f,%.4f);" % (x - 0.11, y - 0.11, x + 0.11, y + 0.11))
            elif special[key] == "triangle":
                out.append("\\fill (%.4f,%.4f) -- (%.4f,%.4f) -- (%.4f,%.4f) -- cycle;"
                           % (x - 0.14, y - 0.10, x + 0.14, y - 0.10, x, y + 0.15))
            else:
                out.append("\\fill (%.4f,%.4f) circle (%.3f);" % (x, y, dot * 1.5))
    if labels:
        for t, lab in ticks:
            out.append("\\node[below=3pt,font=\\footnotesize] at (%.4f,%.4f) {$%s$};" % (ox + s * t, oy - half, lab))
            out.append("\\node[left=3pt,font=\\footnotesize] at (%.4f,%.4f) {$%s$};" % (ox - half, oy + s * t, lab))
    return out


def five(xval, name):
    return [(-xval, "-" + name), (-1.0, "-1"), (0.0, "0"), (1.0, "1"), (xval, name)]


# ---- the figures --------------------------------------------------------------


def fig1_ray():
    h = 1.0
    P = projector(2.3)
    body = wireframe(P, h)
    p = (h, -0.35, 0.45)                                   # leaves through the face first coordinate = +h
    q = tuple(-c for c in p)
    far = tuple(1.45 * c for c in p)
    near = tuple(-1.45 * c for c in p)
    body.append("\\draw[line width=0.5pt,densely dashed] %s -- %s;" % (fmt(P(q)), fmt(P(p))))
    body.append("\\draw[line width=0.8pt] %s -- %s;" % (fmt(P(p)), fmt(P(far))))
    body.append("\\draw[line width=0.8pt] %s -- %s;" % (fmt(P(q)), fmt(P(near))))
    body.append("\\fill %s circle (0.07) node[above left=1pt,font=\\small] {$P$};" % fmt(P(p)))
    body.append("\\draw[fill=white,line width=0.4pt] %s circle (0.07) node[below right=1pt,font=\\small] {$P'$};" % fmt(P(q)))
    body.append("\\fill[gray] %s circle (0.05) node[below=2pt,font=\\small,black] {$O$};" % fmt(P((0, 0, 0))))
    mc.standalone(body, FIG / "fig1_ray.tex")


def fig2_rule():
    h = 1.0
    P = projector(2.3)
    body = wireframe(P, h)
    pts = [((h, 0, 0), "(1,0,0)", "right", False), ((0, -h, 0), "(0,\\bar 1,0)", "left", False),
           ((0, 0, h), "(0,0,1)", "above", True)]
    for p, lab, pos, marked in pts:
        tip = tuple(1.4 * c for c in p)
        body.append("\\draw[line width=0.5pt,densely dashed] %s -- %s;" % (fmt(P((0, 0, 0))), fmt(P(p))))
        body.append("\\draw[line width=0.8pt] %s -- %s node[%s=1pt,font=\\small,fill=white,inner sep=1.5pt] {$%s$};"
                    % (fmt(P(p)), fmt(P(tip)), pos, lab))
        if marked:
            body.append("\\fill %s circle (0.085);" % fmt(P(p)))
        else:
            body.append("\\draw[fill=white,line width=0.4pt] %s circle (0.085);" % fmt(P(p)))
    body.append("\\fill[gray] %s circle (0.05);" % fmt(P((0, 0, 0))))
    mc.standalone(body, FIG / "fig2_rule.tex")


def fig3_face():
    xval, half = 1.7, 2.3
    s = half / xval
    body = flat_face((0, 0), half, five(xval, "x"), xval)
    notes = [((0.0, 0.0), "(0,0,x)", "the ray $(0,0,1)$"), ((1.0, -1.0), "(1,\\bar 1,x)", ""),
             ((-1.0, xval), "(\\bar 1,x,x)", ""), ((xval, 0.0), "(x,0,x)", "the ray $(1,0,1)$"),
             ((xval, xval), "(x,x,x)", "the ray $(1,1,1)$")]
    for n, ((a, b), lab, same) in enumerate(notes):
        tag = "abcde"[n]
        body.append("\\fill (%.4f,%.4f) circle (0.085);" % (s * a, s * b))
        body.append("\\node[font=\\footnotesize\\itshape,fill=white,inner sep=1pt] at (%.4f,%.4f) {%s};"
                    % (s * a - 0.27, s * b + 0.27, tag))
        body.append("\\node[right,font=\\footnotesize] at (%.4f,%.4f) {\\textit{%s}\\quad $%s$%s};"
                    % (half + 0.7, 1.2 - 0.6 * n, tag, lab, (", " + same) if same else ""))
    body.append("\\node[font=\\footnotesize] at (0,%.4f) {first coordinate $\\longrightarrow$};" % (-half - 0.85))
    body.append("\\node[font=\\footnotesize,rotate=90] at (%.4f,0) {second coordinate $\\longrightarrow$};" % (-half - 1.0))
    mc.standalone(body, FIG / "fig3_face.tex")


def fig4_slide():
    half, gap = 1.9, 5.6
    panels = [(math.sqrt(2), "\\sqrt2", "$x^2-2=0$: orthogonal", "$x-2\\neq0$: not orthogonal"),
              (math.sqrt(3), "\\sqrt3", "$x^2-2=1$: not orthogonal", "$x-2\\neq0$: not orthogonal"),
              (2.0, "2", "$x^2-2=2$: not orthogonal", "$x-2=0$: orthogonal")]
    body = []
    for n, (xval, name, la, lb) in enumerate(panels):
        ox = n * gap
        special = {(1.0, 1.0): "square", (-1.0, -1.0): "square", (-xval, xval): "triangle", (1.0, -1.0): "triangle"}
        body += flat_face((ox, 0), half, five(xval, name), xval, special)
        body.append("\\node[font=\\small] at (%.4f,%.4f) {$x=%s$};" % (ox, half + 0.45, name))
        body.append("\\fill (%.4f,%.4f) rectangle (%.4f,%.4f);" % (ox - 2.05, -half - 1.12, ox - 1.85, -half - 0.92))
        body.append("\\node[right,font=\\footnotesize] at (%.4f,%.4f) {%s};" % (ox - 1.8, -half - 1.02, la))
        body.append("\\fill (%.4f,%.4f) -- (%.4f,%.4f) -- (%.4f,%.4f) -- cycle;"
                    % (ox - 2.08, -half - 1.60, ox - 1.82, -half - 1.60, ox - 1.95, -half - 1.37))
        body.append("\\node[right,font=\\footnotesize] at (%.4f,%.4f) {%s};" % (ox - 1.8, -half - 1.50, lb))
    mc.standalone(body, FIG / "fig4_slide.tex")


def fig5_forcing(data):
    rays = [to_word(r) for r in data["rays"]]
    steps, dead = data["first_case"]["steps"], data["first_case"]["dead"]
    numbers = {st["ray"]: n + 1 for n, st in enumerate(steps)}

    def state_after(k):
        state = {}
        for st in steps[:k]:
            state[st["ray"]] = 1
            for m in st["unmarks"]:
                state[m] = 0
        return state

    a, drawn_a = state_cube(rays, state_after(1), numbers, set(), 2.8, (0.0, 0.0),
                            "(a) after the first choice")
    b, drawn_b = state_cube(rays, state_after(len(steps)), numbers, set(dead), 2.8, (8.6, 0.0),
                            "(b) after all seven: the ringed triad has no ray left")
    assert drawn_a == drawn_b == set(rays), "Figure 5 does not show exactly the checked rays"
    final = state_after(len(steps))
    assert all(final.get(m) == 0 for m in dead)
    mc.standalone(a + b, FIG / "fig5_forcing.tex")


def fig6_triptych():
    old = mc.OUT
    mc.OUT = FIG
    try:
        mc.triptych()
    finally:
        mc.OUT = old
    (FIG / "fig6_triptych.tex").write_text((FIG / "alphabet_cube_triptych.tex").read_text(encoding="utf-8"),
                                           encoding="utf-8")
    (FIG / "alphabet_cube_triptych.tex").unlink()


def fig7_ladder(data):
    n1, n2, n3 = data["ladder_counts"]
    half, gap = 1.7, 5.2
    x, y = 1.55, 2.3
    rungs = [([(-1.0, "-1"), (0.0, "0"), (1.0, "1")], 1.0, "coordinate values $0,\\pm1$", "%d rays" % n1),
             (five(x, "x"), x, "coordinate values $0,\\pm1,\\pm x$", "%d rays" % n2),
             ([(-y, "-y"), (-x, "-x"), (-1.0, "-1"), (0.0, "0"), (1.0, "1"), (x, "x"), (y, "y")], y,
              "coordinate values $0,\\pm1,\\pm x,\\pm y$", "%d rays" % n3)]
    body = []
    for n, (ticks, maxval, l1, l2) in enumerate(rungs):
        ox = n * gap
        body += flat_face((ox, 0), half, ticks, maxval)
        body.append("\\node[font=\\small] at (%.4f,%.4f) {%s};" % (ox, -half - 0.95, l1))
        body.append("\\node[font=\\small] at (%.4f,%.4f) {%s};" % (ox, -half - 1.45, l2))
    mc.standalone(body, FIG / "fig7_ladder.tex")


def fig8_map():
    """The plane of x for the grid with coordinate values 0, +-1, +-x, +-x*. Black: cannot be
    colored (two circles, four lines through the origin, the points +-2 and +-1/2), as in
    Fig. 3 of the paper. Lettered points tie the map to the cubes of this note."""
    r2, r7 = math.sqrt(2), math.sqrt(7)
    body = ["\\begin{scope}[scale=1.6]",
            "\\draw[->,gray] (-2.4,0) -- (2.5,0);",
            "\\node[font=\\footnotesize,anchor=north west] at (-2.45,-1.75) {across: real part of $x$};",
            "\\draw[->,gray] (0,-2.05) -- (0,2.2);",
            "\\node[font=\\footnotesize,anchor=north west] at (-2.45,-1.97) {up: imaginary part of $x$};",
            "\\foreach \\t in {30,60,120,150} \\draw[line width=0.9pt] (\\t:-1.9) -- (\\t:1.9);",
            "\\draw[line width=0.9pt] (0,0) circle (%.4f);" % r2,
            "\\draw[line width=0.9pt] (0,0) circle (%.4f);" % (1 / r2),
            "\\foreach \\p in {-2,-0.5,0.5,2} \\fill (\\p,0) circle (0.05);",
            "\\draw[fill=white,line width=0.5pt] (0,0) circle (0.06);"]
    # (tag, x, y, filled, label offset, legend text)
    pts = [("A", r2, 0.0, True, (0.14, 0.15), "$x=\\sqrt2$: fewest 33 (Peres)"),
           ("B", 2.0, 0.0, True, (0.0, 0.2), "$x=2$: fewest 31 (Conway and Kochen)"),
           ("C", math.sqrt(3), 0.0, False, (0.0, -0.2), "$x=\\sqrt3$: can be colored"),
           ("D", 0.0, r2, True, (0.15, 0.16), "$x=\\sqrt{-2}$: fewest 33"),
           ("E", 0.5, math.sqrt(3) / 2, True, (-0.17, 0.06), "$x=e^{i\\pi/3}$: fewest 33"),
           ("F", 0.5, r7 / 2, True, (0.04, 0.2), "$x=(1+\\sqrt{-7})/2$: fewest 43"),
           ("G", 1.0, 1.0, True, (0.17, 0.14), "$x=1+i$: between 24 and 45, not settled")]
    for n, (tag, px, py, filled, (dx, dy), text) in enumerate(pts):
        if filled:
            body.append("\\fill (%.4f,%.4f) circle (0.055);" % (px, py))
        else:
            body.append("\\draw[fill=white,line width=0.6pt] (%.4f,%.4f) circle (0.055);" % (px, py))
        if tag == "G":
            body.append("\\draw[line width=0.5pt] (%.4f,%.4f) circle (0.1);" % (px, py))
        body.append("\\node[font=\\footnotesize\\itshape,fill=white,inner sep=0.8pt] at (%.4f,%.4f) {%s};"
                    % (px + dx, py + dy, tag))
        body.append("\\node[right,font=\\footnotesize] at (2.85,%.4f) {\\textit{%s}\\quad %s};"
                    % (1.5 - 0.36 * n, tag, text))
    body.append("\\node[right,font=\\footnotesize,align=left] at (2.85,%.4f) {black: cannot be colored\\\\"
                "white: can be colored};" % (1.5 - 0.36 * 7 - 0.25))
    body.append("\\end{scope}")
    mc.standalone(body, FIG / "fig8_map.tex")


NAMES = ["fig1_ray", "fig2_rule", "fig3_face", "fig4_slide", "fig5_forcing", "fig6_triptych", "fig7_ladder",
         "fig8_map"]


def compile_all():
    exe = str(MIKTEX) if MIKTEX.exists() else shutil.which("pdflatex")
    assert exe, "pdflatex not found"
    for name in NAMES:
        res = subprocess.run([exe, "-interaction=nonstopmode", "-halt-on-error", name + ".tex"],
                             cwd=FIG, capture_output=True, text=True, errors="replace")
        assert res.returncode == 0 and (FIG / (name + ".pdf")).exists(), \
            "%s did not compile:\n%s" % (name, res.stdout[-1500:])
        for ext in (".aux", ".log"):
            (FIG / (name + ext)).unlink(missing_ok=True)
    print("compiled", len(NAMES), "figures")


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    FIG.mkdir(parents=True, exist_ok=True)
    fig1_ray()
    fig2_rule()
    fig3_face()
    fig4_slide()
    fig5_forcing(data)
    fig6_triptych()
    fig7_ladder(data)
    fig8_map()
    compile_all()
    return 0


if __name__ == "__main__":
    sys.exit(main())
