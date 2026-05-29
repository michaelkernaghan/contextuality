# Contextuality Video Presentation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a 5-12 minute popular science video explaining the algebraic landscape of Kochen-Specker sets, narrated by AI voiceover over Manim animations and published diagrams.

**Architecture:** Seven scenes produced independently (storyboard-first). Each scene = narration script + Manim animation + voiceover audio, composited into a final video. Static book scans are woven in as image overlays. The KS-117 is shown as its published graph; KS-33 and KS-31 are rendered as 3D cube lattices.

**Tech Stack:** Manim Community Edition (Python), ElevenLabs API (TTS), FFmpeg (compositing), PySAT/NetworkX (data for animations from existing scripts)

---

## File Structure

```
contextuality/video/
  storyboard/
    narration_script.md          # Full narration script, all 7 scenes
  manim/
    scene1_puzzle.py             # 3D basis, coloring intro, KS-117 flash
    scene2_two_cubes.py          # KS-33 and KS-31 cube lattices
    scene3_coloring_game.py      # Animated coloring contradiction
    scene4_pattern.py            # Coordinate comparison, equations
    scene5_architectures.py      # Gamma graph, hub-spoke comparison
    scene6_following_pattern.py  # Island exploration, pool merge
    scene7_boundary.py           # Two mechanisms, closing
    shared/
      ks_data.py                 # Ray coordinates, triads, graphs for all KS sets
      cube_lattice.py            # Reusable 3D cube lattice renderer
      graph_layout.py            # Reusable orthogonality graph renderer
      colors.py                  # Color palette constants
  audio/
    scene1.mp3 ... scene7.mp3   # Generated voiceover clips
  assets/
    ks-117.gif                   # Original KS-117 orthogonality graph
    conway-kochen-31.jpg         # CK-31 cube from Peres book
    peres-33-cube.jpg            # Peres-33 cube from Peres book
    ks-10-gamma.gif              # Gamma graph diagram
  output/
    scene1.mp4 ... scene7.mp4   # Rendered scene videos
    contextuality_video.mp4      # Final assembled video
```

---

### Task 1: Environment Setup

**Files:**
- Create: `contextuality/video/requirements.txt`

- [ ] **Step 1: Install Manim Community Edition**

```bash
pip install manim
```

Manim requires FFmpeg. Install on Windows:

```bash
winget install FFmpeg
```

Or download from https://www.gyan.dev/ffmpeg/builds/ and add to PATH.

- [ ] **Step 2: Verify Manim works**

```bash
python -c "from manim import *; print('Manim version:', __version__)"
```

Expected: prints version number (e.g., `0.18.x`)

- [ ] **Step 3: Test Manim rendering**

```bash
cd C:/Users/Michael\ Kernaghan/contextuality/video/manim
python -c "
from manim import *
class Test(Scene):
    def construct(self):
        self.play(Write(Text('Manim works')))
        self.wait(1)
" && manim -pql -o test.mp4 __main__.py Test
```

Expected: opens a preview window with "Manim works" text

- [ ] **Step 4: Install ElevenLabs SDK**

```bash
pip install elevenlabs
```

- [ ] **Step 5: Create requirements.txt**

```
manim>=0.18.0
elevenlabs>=1.0.0
numpy>=2.0.0
networkx>=3.0
pysat>=0.1.8
```

Save to `contextuality/video/requirements.txt`.

- [ ] **Step 6: Create project directory structure**

```bash
cd C:/Users/Michael\ Kernaghan/contextuality
mkdir -p video/{storyboard,manim/shared,audio,assets,output}
```

- [ ] **Step 7: Copy assets into video/assets/**

```bash
cp docs/ks-sets/scans/ks-117.gif video/assets/
cp docs/ks-sets/scans/conway-kochen-31.jpg video/assets/
cp docs/ks-sets/scans/peres-33-page198-cube.jpg video/assets/peres-33-cube.jpg
cp docs/ks-sets/scans/ks-10-gamma.gif video/assets/
```

- [ ] **Step 8: Commit**

```bash
git add video/
git commit -m "feat(video): scaffold project structure and copy assets"
```

---

### Task 2: Shared Data Module

**Files:**
- Create: `contextuality/video/manim/shared/ks_data.py`
- Create: `contextuality/video/manim/shared/__init__.py`

This module provides ray coordinates, triads, and graph data for all KS sets used in the video. Data is extracted from the existing codebase scripts (`ks_islands.py`, `ks_generator_subgraph.py`, `ks_pool_merge_experiment.py`).

- [ ] **Step 1: Create __init__.py**

```python
# contextuality/video/manim/shared/__init__.py
```

Empty file to make shared/ a package.

- [ ] **Step 2: Write ks_data.py with CK-31 data**

Extract the 31 ray coordinates and 17 triads from the existing `ks_islands.py` output. The CK-31 uses alphabet {0, +/-1, +/-2}.

```python
# contextuality/video/manim/shared/ks_data.py
"""KS set data for video animations.

All rays are unnormalized integer/algebraic coordinates.
Triads are lists of 3 ray indices forming orthogonal triples.
"""

import numpy as np
from math import sqrt

# CK-31: 31 rays, alphabet {0, ±1, ±2}, 17 triads
# Coordinates from Peres, "Quantum Theory: Concepts and Methods" p.198 table
CK31_RAYS = [
    (1, 0, 0), (0, 1, 0), (0, 0, 1),
    (1, 1, 0), (1, -1, 0), (1, 0, 1), (1, 0, -1), (0, 1, 1), (0, 1, -1),
    (1, 1, 1), (1, 1, -1), (1, -1, 1), (-1, 1, 1),
    (2, 1, 0), (2, -1, 0), (2, 0, 1), (2, 0, -1),
    (0, 2, 1), (0, 2, -1), (1, 0, 2), (1, 0, -2),
    (0, 1, 2), (0, 1, -2),
    (1, 2, 1), (1, 2, -1), (1, -2, 1), (-1, 2, 1),
    (1, 1, 2), (1, 1, -2), (1, -1, 2), (-1, 1, 2),
]

# Note: The exact 31 rays and 17 triads should be verified by running
# the existing ks_islands.py script and extracting the CK-31 data.
# The above is a placeholder that MUST be replaced with verified data.
# Run: python ks_islands.py and extract the integer pool KS-31 result.
```

- [ ] **Step 3: Extract verified CK-31 data from existing scripts**

Run the existing island survey to get exact coordinates:

```bash
cd C:/Users/Michael\ Kernaghan/contextuality
python -u -c "
from ks_islands import *
# Extract integer pool rays and triads
# Print in format suitable for ks_data.py
"
```

Replace the placeholder CK31_RAYS with the verified output. Also extract CK31_TRIADS (list of 17 triples of ray indices).

- [ ] **Step 4: Add Peres-33 data**

Extract from `find_peres33.py` or `docs/ks-sets/peres-33-3d.md`. The Peres-33 uses alphabet {0, +/-1, +/-sqrt(2)}.

Add to `ks_data.py`:

```python
S2 = sqrt(2)

PERES33_RAYS = [
    (1, 0, 0), (0, 1, 0), (0, 0, 1),
    (1, 1, 0), (1, -1, 0), (1, 0, 1), (1, 0, -1), (0, 1, 1), (0, 1, -1),
    (S2, 1, 0), (S2, -1, 0), (S2, 0, 1), (S2, 0, -1),
    (0, S2, 1), (0, S2, -1), (1, 0, S2), (1, 0, -S2),
    (0, 1, S2), (0, 1, -S2),
    (1, S2, 0), (1, -S2, 0), (0, 1, S2), (0, -1, S2),
    (1, 1, S2), (1, 1, -S2), (1, -1, S2), (-1, 1, S2),
    (S2, 1, 1), (S2, 1, -1), (S2, -1, 1), (-S2, 1, 1),
    (1, S2, 1), (1, S2, -1),
]

# Note: Same as CK-31 — verify against find_peres33.py output.
# Replace with verified data.
```

- [ ] **Step 5: Add Gamma-10 data**

The Gamma graph at x=y=1 uses alphabet {0, +/-1}:

```python
GAMMA10_RAYS = [
    (1, 0, 0),   # a5
    (0, 0, 1),   # a6
    (0, 1, 1),   # a1
    (1, 1, 0),   # a2
    (0, -1, 1),  # a3
    (1, -1, 0),  # a4
    (-1, 1, -1), # a0
    (-1, -1, -1),# a7
    # a8 and a9 require specific orthogonality constraints
    # Extract from ks_generator_subgraph.py output
]

GAMMA10_LABELS = ['a5', 'a6', 'a1', 'a2', 'a3', 'a4', 'a0', 'a7', 'a8', 'a9']
```

- [ ] **Step 6: Add island summary data for Scene 6**

```python
ISLANDS = [
    {"name": "Integer (CK-31)", "ring": "Z", "min_ks": 31, "mechanism": "modulus-2", "alphabet": "{0,±1,±2}"},
    {"name": "Peres", "ring": "Z[√2]", "min_ks": 33, "mechanism": "modulus-2", "alphabet": "{0,±1,±√2}"},
    {"name": "Eisenstein", "ring": "Z[ω]", "min_ks": 33, "mechanism": "phase", "alphabet": "{0,±1,±ω}"},
    {"name": "Z[√-2]", "ring": "Z[√-2]", "min_ks": 33, "mechanism": "modulus-2", "alphabet": "{0,±1,±√-2}"},
    {"name": "Heegner-7", "ring": "Z[(1+√-7)/2]", "min_ks": 43, "mechanism": "modulus-2", "alphabet": "{0,±1,±α}"},
    {"name": "Golden", "ring": "Z[φ]", "min_ks": 52, "mechanism": "modulus-2", "alphabet": "{0,±1,±φ}"},
]
```

- [ ] **Step 7: Add helper functions**

```python
def compute_triads(rays):
    """Find all orthogonal triples among a list of rays."""
    n = len(rays)
    triads = []
    for i in range(n):
        for j in range(i+1, n):
            if abs(np.dot(rays[i], rays[j])) < 1e-9:
                for k in range(j+1, n):
                    if (abs(np.dot(rays[i], rays[k])) < 1e-9 and
                        abs(np.dot(rays[j], rays[k])) < 1e-9):
                        triads.append((i, j, k))
    return triads

def build_orthogonality_graph(rays):
    """Build NetworkX graph: vertices=rays, edges=orthogonal pairs."""
    import networkx as nx
    G = nx.Graph()
    G.add_nodes_from(range(len(rays)))
    for i in range(len(rays)):
        for j in range(i+1, len(rays)):
            if abs(np.dot(rays[i], rays[j])) < 1e-9:
                G.add_edge(i, j)
    return G
```

- [ ] **Step 8: Verify data by running a quick test**

```bash
cd C:/Users/Michael\ Kernaghan/contextuality/video/manim
python -u -c "
import sys; sys.path.insert(0, '.')
from shared.ks_data import *
print(f'CK-31: {len(CK31_RAYS)} rays')
triads = compute_triads([np.array(r, dtype=float) for r in CK31_RAYS])
print(f'CK-31 triads: {len(triads)}')
print(f'Peres-33: {len(PERES33_RAYS)} rays')
print(f'Gamma-10: {len(GAMMA10_RAYS)} rays')
print(f'Islands: {len(ISLANDS)}')
"
```

Expected: CK-31: 31 rays, 17 triads. Peres-33: 33 rays, 16 triads.

- [ ] **Step 9: Commit**

```bash
git add video/manim/shared/
git commit -m "feat(video): add KS data module with ray coordinates and triads"
```

---

### Task 3: Shared Cube Lattice Renderer

**Files:**
- Create: `contextuality/video/manim/shared/cube_lattice.py`

A reusable Manim class that renders a 3D cube lattice with highlighted ray positions.

- [ ] **Step 1: Write cube_lattice.py**

```python
# contextuality/video/manim/shared/cube_lattice.py
"""Reusable 3D cube lattice renderer for KS set visualization."""

from manim import *
import numpy as np


class CubeLattice(ThreeDScene):
    """Renders a 3D lattice cube with highlighted ray positions.

    Usage:
        lattice = CubeLatticeGroup(
            grid_values=[-2, -1, 0, 1, 2],
            active_rays=[(1, 0, 0), (0, 1, 1), ...],
            ray_color=GREEN,
            grid_color=GREY,
            grid_opacity=0.2,
            ray_radius=0.08,
        )
        self.play(Create(lattice))
    """
    pass


class CubeLatticeGroup(VGroup):
    """A VGroup containing the wireframe cube grid and active ray dots."""

    def __init__(
        self,
        grid_values,
        active_rays,
        ray_color=GREEN,
        highlight_rays=None,
        highlight_color=YELLOW,
        grid_color=GREY,
        grid_opacity=0.15,
        ray_radius=0.08,
        scale_factor=1.0,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.grid_values = grid_values
        self.active_rays = active_rays

        # Normalize grid to [-1, 1] range for display
        vmin = min(grid_values)
        vmax = max(grid_values)
        span = vmax - vmin if vmax != vmin else 1

        def normalize(v):
            return 2.0 * (v - vmin) / span - 1.0

        # Draw wireframe grid edges
        for v1 in grid_values:
            for v2 in grid_values:
                for axis in range(3):
                    start = [0, 0, 0]
                    end = [0, 0, 0]
                    other_axes = [i for i in range(3) if i != axis]
                    start[other_axes[0]] = normalize(v1)
                    start[other_axes[1]] = normalize(v2)
                    end[other_axes[0]] = normalize(v1)
                    end[other_axes[1]] = normalize(v2)
                    start[axis] = normalize(grid_values[0])
                    end[axis] = normalize(grid_values[-1])
                    line = Line3D(
                        start=np.array(start) * scale_factor,
                        end=np.array(end) * scale_factor,
                        color=grid_color,
                    ).set_opacity(grid_opacity)
                    self.add(line)

        # Draw active ray dots
        highlight_set = set()
        if highlight_rays:
            for r in highlight_rays:
                highlight_set.add(tuple(r))

        for ray in active_rays:
            pos = np.array([normalize(ray[0]), normalize(ray[1]), normalize(ray[2])]) * scale_factor
            color = highlight_color if tuple(ray) in highlight_set else ray_color
            dot = Sphere(radius=ray_radius * scale_factor, color=color).move_to(pos)
            dot.set_opacity(1.0)
            self.add(dot)
```

- [ ] **Step 2: Test the cube lattice renderer**

```bash
cd C:/Users/Michael\ Kernaghan/contextuality/video/manim
manim -pql -o test_cube.mp4 -c "
from manim import *
import sys; sys.path.insert(0, '.')
from shared.cube_lattice import CubeLatticeGroup

class TestCube(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=70*DEGREES, theta=30*DEGREES)
        cube = CubeLatticeGroup(
            grid_values=[-2, -1, 0, 1, 2],
            active_rays=[(1,0,0),(0,1,0),(0,0,1),(1,1,0),(1,-1,0),(2,1,0)],
        )
        self.play(Create(cube), run_time=2)
        self.begin_ambient_camera_rotation(rate=0.2)
        self.wait(4)
"
```

Expected: a rotating 5x5x5 wireframe cube with 6 green dots at the ray positions.

- [ ] **Step 3: Commit**

```bash
git add video/manim/shared/cube_lattice.py
git commit -m "feat(video): add reusable 3D cube lattice renderer"
```

---

### Task 4: Shared Graph Renderer

**Files:**
- Create: `contextuality/video/manim/shared/graph_layout.py`
- Create: `contextuality/video/manim/shared/colors.py`

A reusable Manim class for orthogonality graph visualization with coloring animation.

- [ ] **Step 1: Write colors.py**

```python
# contextuality/video/manim/shared/colors.py
"""Color palette for the video."""

from manim import *

KS_GREEN = GREEN_C       # "value 1" / selected
KS_RED = RED_C           # "value 0" / not selected
KS_NEUTRAL = GREY_B      # uncolored vertex
KS_EDGE = GREY_C         # orthogonality edge
KS_HIGHLIGHT = YELLOW    # highlighted substructure
KS_CONFLICT = PURE_RED   # contradiction flash
ISLAND_COLORS = [BLUE_C, TEAL_C, GREEN_C, ORANGE, PURPLE_C, GOLD_C]
```

- [ ] **Step 2: Write graph_layout.py**

```python
# contextuality/video/manim/shared/graph_layout.py
"""Reusable orthogonality graph renderer with coloring animation."""

from manim import *
import networkx as nx
import numpy as np
from .colors import *


def create_ks_graph(rays, triads, layout="spring", scale=3.0):
    """Create a Manim Graph from rays and triads.

    Returns a Manim Graph object with vertices at layout positions
    and edges for orthogonal pairs.
    """
    n = len(rays)
    edges = set()
    for triad in triads:
        i, j, k = triad
        edges.add((i, j))
        edges.add((i, k))
        edges.add((j, k))

    # Use NetworkX for layout
    G_nx = nx.Graph()
    G_nx.add_nodes_from(range(n))
    G_nx.add_edges_from(edges)

    if layout == "spring":
        pos = nx.spring_layout(G_nx, seed=42, k=2.0/np.sqrt(n))
    elif layout == "circular":
        pos = nx.circular_layout(G_nx)
    elif layout == "spectral":
        pos = nx.spectral_layout(G_nx)
    else:
        pos = nx.spring_layout(G_nx, seed=42)

    # Scale positions
    layout_dict = {i: np.array([pos[i][0], pos[i][1], 0]) * scale for i in range(n)}

    vertices = list(range(n))
    edge_list = list(edges)

    graph = Graph(
        vertices,
        edge_list,
        layout=layout_dict,
        vertex_config={"radius": 0.12, "color": KS_NEUTRAL, "fill_opacity": 1.0},
        edge_config={"color": KS_EDGE, "stroke_width": 1.5},
    )
    return graph


def animate_coloring_attempt(scene, graph, triads, rays):
    """Animate a coloring attempt that ends in contradiction.

    Propagates green/red assignments through the graph,
    showing the forced choices, then flashes red when contradiction hit.
    """
    # Simple greedy coloring that will fail
    colors = {}  # ray_index -> 'green' or 'red'

    # Start by coloring the first triad
    first_triad = triads[0]
    colors[first_triad[0]] = 'green'
    colors[first_triad[1]] = 'red'
    colors[first_triad[2]] = 'red'

    # Animate first assignment
    scene.play(
        graph.vertices[first_triad[0]].animate.set_color(KS_GREEN),
        graph.vertices[first_triad[1]].animate.set_color(KS_RED),
        graph.vertices[first_triad[2]].animate.set_color(KS_RED),
        run_time=0.5,
    )

    # Propagate through remaining triads
    for triad in triads[1:]:
        i, j, k = triad
        known = {v: colors[v] for v in (i, j, k) if v in colors}
        new_assignments = {}

        if len(known) == 0:
            new_assignments = {i: 'green', j: 'red', k: 'red'}
        elif len(known) == 1:
            v, c = list(known.items())[0]
            others = [x for x in (i, j, k) if x != v]
            if c == 'green':
                new_assignments = {others[0]: 'red', others[1]: 'red'}
            else:
                new_assignments = {others[0]: 'green', others[1]: 'red'}
        elif len(known) == 2:
            greens = sum(1 for c in known.values() if c == 'green')
            unknown = [x for x in (i, j, k) if x not in known][0] if len(known) < 3 else None
            if unknown is not None:
                if greens == 1:
                    new_assignments = {unknown: 'red'}
                elif greens == 0:
                    new_assignments = {unknown: 'green'}
                else:
                    # Contradiction: two greens in one triad
                    scene.play(
                        *[graph.vertices[v].animate.set_color(KS_CONFLICT) for v in (i, j, k)],
                        Flash(graph.vertices[unknown], color=KS_CONFLICT),
                        run_time=0.3,
                    )
                    scene.play(
                        *[graph.vertices[v].animate.set_color(KS_CONFLICT)
                          for v in range(len(rays))],
                        run_time=0.5,
                    )
                    return  # Contradiction reached

        for v, c in new_assignments.items():
            colors[v] = c
            color = KS_GREEN if c == 'green' else KS_RED
            scene.play(graph.vertices[v].animate.set_color(color), run_time=0.15)
```

- [ ] **Step 3: Test graph renderer**

```bash
cd C:/Users/Michael\ Kernaghan/contextuality/video/manim
manim -pql -o test_graph.mp4 -c "
from manim import *
import sys; sys.path.insert(0, '.')
from shared.graph_layout import create_ks_graph
from shared.ks_data import CK31_RAYS, compute_triads
import numpy as np

class TestGraph(Scene):
    def construct(self):
        rays = [np.array(r, dtype=float) for r in CK31_RAYS]
        triads = compute_triads(rays)
        graph = create_ks_graph(rays, triads, layout='spring')
        self.play(Create(graph), run_time=2)
        self.wait(2)
"
```

Expected: spring-layout orthogonality graph of CK-31 (31 vertices, ~71 edges).

- [ ] **Step 4: Commit**

```bash
git add video/manim/shared/colors.py video/manim/shared/graph_layout.py
git commit -m "feat(video): add graph renderer and color palette"
```

---

### Task 5: Write Narration Script

**Files:**
- Create: `contextuality/video/storyboard/narration_script.md`

The full narration script for all 7 scenes. This is the creative writing task — the script drives all subsequent animation work.

- [ ] **Step 1: Write Scene 1 narration (The Puzzle)**

```markdown
# Contextuality Video — Narration Script

## Scene 1: The Puzzle (approx 35 seconds)

Can nature have pre-existing answers to every question you could ask it?

In 1967, Simon Kochen and Ernst Specker proved the answer is no — at least
not if those answers have to be consistent. Their proof was a coloring puzzle
built from 117 directions in three-dimensional space.

[Show KS-117 graph]

The original proof used coordinates from a cyclotomic number field — algebraic
irrationals related to the golden ratio. It couldn't even be drawn on a grid.

Over the decades, mathematicians found simpler and simpler versions of this
puzzle. And the key to simplification wasn't just fewer vectors — it was
simpler numbers.
```

- [ ] **Step 2: Write Scene 2 narration (The Two Cubes)**

```markdown
## Scene 2: The Two Cubes (approx 75 seconds)

[Show Peres book scan, crossfade to Manim cube]

In 1991, Asher Peres found a version with just 33 vectors. For the first
time, the proof could be drawn as points inside a cube. The coordinates use
zero, one, and the square root of two.

[Show KS-33 cube with coordinate labels]

Then John Conway and Simon Kochen found an even smaller version — 31 vectors.
This time, the coordinates are pure integers: zero, one, and two. No
irrationals at all.

[Show KS-31 cube with coordinate labels]

Look at these two cubes side by side. They're different constructions, different
coordinate alphabets. The 33-vector set lives in the world of the square root
of two. The 31-vector set lives in the world of integers.

But something about them feels related. As if they're two instances of the
same underlying pattern.
```

- [ ] **Step 3: Write Scene 3 narration (The Coloring Game)**

```markdown
## Scene 3: The Coloring Game (approx 50 seconds)

[Show orthogonality graph of CK-31]

Here's the puzzle. Take these 31 directions. Each one is a ray through the
origin of three-dimensional space. Group them into sets of three mutually
perpendicular rays — orthogonal triples.

Now try to color them. Each triple must have exactly one green ray and two
red rays. And here's the catch: if a ray appears in more than one triple,
it has to be the same color in all of them.

[Animate coloring propagation]

Try it. You assign green here, which forces red there, which forces green
somewhere else...

[Contradiction flash]

And eventually you get stuck. Two greens in the same triple, or no way to
assign green at all. It's impossible. That's the proof: nature cannot have
pre-assigned answers to all these questions simultaneously. The answers
depend on which other questions you ask alongside them. That's contextuality.
```

- [ ] **Step 4: Write Scene 4 narration (The Pattern)**

```markdown
## Scene 4: The Pattern (approx 50 seconds)

[Zoom into coordinates on both cubes]

Now look at the coordinates again. The 33-vector set uses zero, one, and the
square root of two. The 31-vector set uses zero, one, and two. One has the
square root of two. The other has two itself.

What do these numbers have in common? When you square them, you get two. The
square root of two squared is two. And in the integer case, one plus one
equals two.

[Show equations: (√2)² = 2 and 1 + 1 = 2]

Both alphabets support the same algebraic trick: a way to make dot products
vanish exactly. Two vectors are perpendicular when their dot product is zero.
And to get a dot product of zero from small integer-like coordinates, you need
cancellation — you need the number two to appear from your alphabet's
arithmetic.

[Show dot product computation]

That's the pattern. Both cubes work because their number system can produce
the number two through its own operations.
```

- [ ] **Step 5: Write Scene 5 narration (Two Architectures)**

```markdown
## Scene 5: Two Architectures (approx 55 seconds)

[Show KS-10 Gamma graph]

But here's what's surprising. Despite sharing the same algebraic trick, these
two sets achieve their contradiction in completely different ways.

The original 117-vector proof from 1967 was built from copies of this little
ten-ray pattern — the Gamma graph. It's a cycle of interlocking triples that
forces a parity contradiction. It's the engine of every early KS proof.

[Highlight 6 Gamma copies inside CK-31]

The 31-vector set inherits this architecture. Inside it, you can find six
copies of the Gamma graph, chained together.

[Show Peres-33 hub structure]

The 33-vector set has zero copies. It achieves its contradiction through a
completely different mechanism: a hub-and-spoke architecture. Three
high-degree axis rays — the coordinate axes themselves — anchor the entire
structure. The contradiction flows through the hubs, not around cycles.

Same puzzle. Same impossibility. Completely different engineering.
```

- [ ] **Step 6: Write Scene 6 narration (Following the Pattern)**

```markdown
## Scene 6: Following the Pattern (approx 80 seconds)

[New cubes appear]

If integers give 31 vectors and the square root of two gives 33... what
happens if we try other number systems?

[Eisenstein cube]

Cube roots of unity — the Eisenstein integers, where omega satisfies one
plus omega plus omega squared equals zero. 33 vectors, but a completely
new graph type. This time the cancellation isn't about the number two — it's
about phases adding up to zero.

[Heegner-7]

The ring of integers in the field of the square root of negative seven. 43
vectors. A genuinely new construction that had never been seen before.

[Golden]

The golden ratio. 52 vectors — but these are invisible if you only look at
the raw alphabet. You find them only when you close the coordinate system
under cross products.

[Island map]

Six algebraic islands. Each one a different number system. Each one producing
a Kochen-Specker set with its own geometry.

[Pool merge animation]

We tried combining them — merging the 31-vector integer pool with the
33-vector square-root-of-two pool, 85 rays in total, hoping to find something
smaller than 31. But the two pools don't interlock. There are zero orthogonal
triples mixing rays from the two alphabets. The dot products between them are
irrational — they never hit zero.

The algebraic islands are truly isolated.
```

- [ ] **Step 7: Write Scene 7 narration (Why Two and Three)**

```markdown
## Scene 7: Why Two and Three (approx 40 seconds)

[Two equations side by side]

Every construction we found uses one of exactly two algebraic tricks.

The modulus-two mechanism: the generator satisfies the absolute value of x
squared equals two. This is how integers, the square root of two, the square
root of negative two, and the Heegner-7 ring all work.

The phase mechanism: a vanishing sum of unit-modulus terms. One plus omega
plus omega squared equals zero. This is how the Eisenstein integers work.

[Boundary visualization]

That's the complete boundary. If your number system can do one of these two
tricks, you can build a Kochen-Specker set. If it can't, you can't. Every
tested alphabet with generator norm three or higher fails.

Whether this boundary holds for all number fields remains an open question.

[Paper citation]

The full results are in the paper: "The Algebraic Landscape of Kochen-Specker
Sets in Dimension Three," available on the arXiv.
```

- [ ] **Step 8: Review full script for timing**

Read through the complete script aloud (or estimate at ~150 words/minute for narration). Target:
- Scenes 1-4: ~3.5 minutes
- Scenes 5-7: ~3 minutes
- Total: ~6.5 minutes (within 5-8 target, room for pauses and visual beats)

- [ ] **Step 9: Commit**

```bash
git add video/storyboard/narration_script.md
git commit -m "feat(video): write full narration script for all 7 scenes"
```

---

### Task 6: Scene 1 — The Puzzle

**Files:**
- Create: `contextuality/video/manim/scene1_puzzle.py`

- [ ] **Step 1: Write scene1_puzzle.py**

```python
# contextuality/video/manim/scene1_puzzle.py
"""Scene 1: The Puzzle — intro to KS theorem with 3D basis and KS-117 flash."""

from manim import *
import sys
sys.path.insert(0, str(Path(__file__).parent))
from shared.colors import *


class ThePuzzle(ThreeDScene):
    def construct(self):
        # Title
        title = Text("The Coloring Puzzle", font_size=48).to_edge(UP)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title), run_time=1)

        # 3D coordinate axes
        self.set_camera_orientation(phi=70 * DEGREES, theta=30 * DEGREES)
        axes = ThreeDAxes(
            x_range=[-2, 2], y_range=[-2, 2], z_range=[-2, 2],
            x_length=4, y_length=4, z_length=4,
        )
        self.play(Create(axes), run_time=1.5)

        # Three orthogonal rays
        ray1 = Arrow3D(ORIGIN, [1.5, 0, 0], color=KS_GREEN)
        ray2 = Arrow3D(ORIGIN, [0, 1.5, 0], color=KS_RED)
        ray3 = Arrow3D(ORIGIN, [0, 0, 1.5], color=KS_RED)

        self.play(Create(ray1), Create(ray2), Create(ray3), run_time=1)
        self.wait(1)

        # Label: "one green, two red per triple"
        rule = Text("One green, two red\nper orthogonal triple", font_size=28)
        rule.to_corner(DR)
        self.add_fixed_in_frame_mobjects(rule)
        self.play(FadeIn(rule), run_time=0.5)
        self.wait(2)

        # Clear and show KS-117
        self.play(FadeOut(axes), FadeOut(ray1), FadeOut(ray2), FadeOut(ray3),
                  FadeOut(rule), FadeOut(title), run_time=0.5)

        # Switch to 2D for the KS-117 image
        self.stop_ambient_camera_rotation()
        ks117 = ImageMobject("../assets/ks-117.gif").scale(2.5)
        label117 = Text("Kochen-Specker, 1967: 117 vectors", font_size=32)
        label117.next_to(ks117, DOWN, buff=0.3)

        self.add_fixed_in_frame_mobjects(ks117, label117)
        self.play(FadeIn(ks117), Write(label117), run_time=1.5)
        self.wait(3)

        # Transition text
        transition = Text(
            "Coordinates: algebraic irrationals\nfrom the golden ratio family",
            font_size=24, color=GREY_B,
        )
        transition.next_to(label117, DOWN, buff=0.2)
        self.add_fixed_in_frame_mobjects(transition)
        self.play(FadeIn(transition), run_time=1)
        self.wait(2)

        self.play(FadeOut(ks117), FadeOut(label117), FadeOut(transition), run_time=1)
```

- [ ] **Step 2: Test render Scene 1**

```bash
cd C:/Users/Michael\ Kernaghan/contextuality/video/manim
manim -pql scene1_puzzle.py ThePuzzle
```

Expected: ~15 second low-quality preview showing 3D axes, colored rays, then KS-117 image.

- [ ] **Step 3: Iterate on timing and visual polish**

Adjust `run_time` values, camera angles, and text placement based on preview. Re-render until it looks right.

- [ ] **Step 4: Commit**

```bash
git add video/manim/scene1_puzzle.py
git commit -m "feat(video): implement Scene 1 — The Puzzle"
```

---

### Task 7: Scene 2 — The Two Cubes

**Files:**
- Create: `contextuality/video/manim/scene2_two_cubes.py`

- [ ] **Step 1: Write scene2_two_cubes.py**

```python
# contextuality/video/manim/scene2_two_cubes.py
"""Scene 2: The Two Cubes — KS-33 and KS-31 side by side."""

from manim import *
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from shared.cube_lattice import CubeLatticeGroup
from shared.ks_data import CK31_RAYS, PERES33_RAYS
from shared.colors import *
from math import sqrt


S2 = sqrt(2)


class TheTwoCubes(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=65 * DEGREES, theta=30 * DEGREES)

        # --- KS-33 book scan first ---
        peres_scan = ImageMobject("../assets/peres-33-cube.jpg").scale(2)
        peres_label = Text("Peres, 1991", font_size=36)
        peres_label.next_to(peres_scan, DOWN, buff=0.2)
        self.add_fixed_in_frame_mobjects(peres_scan, peres_label)
        self.play(FadeIn(peres_scan), Write(peres_label), run_time=1.5)
        self.wait(2)
        self.play(FadeOut(peres_scan), FadeOut(peres_label), run_time=0.5)

        # --- KS-33 Manim cube ---
        peres_grid = [-S2, -1, 0, 1, S2]
        peres_cube = CubeLatticeGroup(
            grid_values=peres_grid,
            active_rays=PERES33_RAYS,
            ray_color=TEAL_C,
            scale_factor=1.2,
        ).shift(LEFT * 3.5)

        peres_title = Text("33 vectors: {0, ±1, ±√2}", font_size=28)
        peres_title.to_edge(UP).shift(LEFT * 3)
        self.add_fixed_in_frame_mobjects(peres_title)

        self.play(Create(peres_cube), Write(peres_title), run_time=2)
        self.wait(1)

        # --- KS-31 book scan ---
        ck_scan = ImageMobject("../assets/conway-kochen-31.jpg").scale(1.5)
        self.add_fixed_in_frame_mobjects(ck_scan)
        self.play(FadeIn(ck_scan), run_time=1)
        self.wait(1.5)
        self.play(FadeOut(ck_scan), run_time=0.5)

        # --- KS-31 Manim cube ---
        ck_grid = [-2, -1, 0, 1, 2]
        ck_cube = CubeLatticeGroup(
            grid_values=ck_grid,
            active_rays=CK31_RAYS,
            ray_color=GREEN_C,
            scale_factor=1.2,
        ).shift(RIGHT * 3.5)

        ck_title = Text("31 vectors: {0, ±1, ±2}", font_size=28)
        ck_title.to_edge(UP).shift(RIGHT * 3)
        self.add_fixed_in_frame_mobjects(ck_title)

        self.play(Create(ck_cube), Write(ck_title), run_time=2)
        self.wait(1)

        # --- Side by side rotation ---
        self.begin_ambient_camera_rotation(rate=0.15)
        self.wait(5)
        self.stop_ambient_camera_rotation()

        # --- Highlight the question ---
        question = Text("What's the pattern?", font_size=40, color=YELLOW)
        question.to_edge(DOWN)
        self.add_fixed_in_frame_mobjects(question)
        self.play(Write(question), run_time=1)
        self.wait(2)

        self.play(
            FadeOut(peres_cube), FadeOut(ck_cube),
            FadeOut(peres_title), FadeOut(ck_title),
            FadeOut(question),
            run_time=1,
        )
```

- [ ] **Step 2: Test render Scene 2**

```bash
cd C:/Users/Michael\ Kernaghan/contextuality/video/manim
manim -pql scene2_two_cubes.py TheTwoCubes
```

Expected: book scan → Manim KS-33 cube (teal) → book scan → KS-31 cube (green) → side by side rotation.

- [ ] **Step 3: Iterate on visual polish**

Adjust camera angle, cube spacing, dot sizes, label positions. The two cubes should be clearly distinguishable but visually similar enough to invite comparison.

- [ ] **Step 4: Commit**

```bash
git add video/manim/scene2_two_cubes.py
git commit -m "feat(video): implement Scene 2 — The Two Cubes"
```

---

### Task 8: Scene 3 — The Coloring Game

**Files:**
- Create: `contextuality/video/manim/scene3_coloring_game.py`

- [ ] **Step 1: Write scene3_coloring_game.py**

This scene shows the CK-31 orthogonality graph and animates a coloring attempt that ends in contradiction.

```python
# contextuality/video/manim/scene3_coloring_game.py
"""Scene 3: The Coloring Game — animated coloring contradiction on CK-31."""

from manim import *
from pathlib import Path
import sys
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
from shared.ks_data import CK31_RAYS, compute_triads
from shared.graph_layout import create_ks_graph, animate_coloring_attempt
from shared.colors import *


class TheColoringGame(Scene):
    def construct(self):
        rays = [np.array(r, dtype=float) for r in CK31_RAYS]
        triads = compute_triads(rays)

        title = Text("The Coloring Game", font_size=42).to_edge(UP)
        self.play(Write(title), run_time=0.8)

        # Create and show the graph
        graph = create_ks_graph(rays, triads, layout="spring", scale=2.8)
        self.play(Create(graph), run_time=2)
        self.wait(1)

        # Show rule
        rule = Text(
            "Rule: exactly one green per triple\nSame color everywhere a ray appears",
            font_size=22,
        ).to_edge(DOWN)
        self.play(FadeIn(rule), run_time=0.5)
        self.wait(1.5)

        # Animate the coloring attempt
        animate_coloring_attempt(self, graph, triads, rays)
        self.wait(1)

        # Contradiction label
        contradiction = Text("CONTRADICTION", font_size=48, color=KS_CONFLICT)
        contradiction.move_to(ORIGIN)
        self.play(FadeIn(contradiction, scale=1.5), run_time=0.5)
        self.wait(2)

        self.play(FadeOut(graph), FadeOut(title), FadeOut(rule),
                  FadeOut(contradiction), run_time=1)
```

- [ ] **Step 2: Test render Scene 3**

```bash
cd C:/Users/Michael\ Kernaghan/contextuality/video/manim
manim -pql scene3_coloring_game.py TheColoringGame
```

Expected: graph appears, coloring propagates vertex by vertex, then contradiction flash.

- [ ] **Step 3: Tune the coloring animation**

The `animate_coloring_attempt` function uses a simple greedy approach. If it doesn't hit a visible contradiction quickly enough, adjust the triad ordering in the function to reach contradiction within ~15 coloring steps (enough to show the process but not bore the viewer).

- [ ] **Step 4: Commit**

```bash
git add video/manim/scene3_coloring_game.py
git commit -m "feat(video): implement Scene 3 — The Coloring Game"
```

---

### Task 9: Scene 4 — The Pattern

**Files:**
- Create: `contextuality/video/manim/scene4_pattern.py`

- [ ] **Step 1: Write scene4_pattern.py**

```python
# contextuality/video/manim/scene4_pattern.py
"""Scene 4: The Pattern — coordinate comparison and cancellation identity."""

from manim import *
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from shared.colors import *


class ThePattern(Scene):
    def construct(self):
        title = Text("The Pattern", font_size=42).to_edge(UP)
        self.play(Write(title), run_time=0.8)

        # Show the two alphabets
        alpha_peres = MathTex(r"\{0, \pm 1, \pm\sqrt{2}\}", font_size=40)
        alpha_ck = MathTex(r"\{0, \pm 1, \pm 2\}", font_size=40)
        label_peres = Text("Peres-33:", font_size=28, color=TEAL_C)
        label_ck = Text("CK-31:", font_size=28, color=GREEN_C)

        left_group = VGroup(label_peres, alpha_peres).arrange(DOWN, buff=0.2).shift(LEFT * 3)
        right_group = VGroup(label_ck, alpha_ck).arrange(DOWN, buff=0.2).shift(RIGHT * 3)

        self.play(FadeIn(left_group), FadeIn(right_group), run_time=1)
        self.wait(2)

        # The key insight: both produce 2
        arrow_left = Arrow(alpha_peres.get_bottom(), DOWN * 0.5 + LEFT * 3, color=YELLOW)
        arrow_right = Arrow(alpha_ck.get_bottom(), DOWN * 0.5 + RIGHT * 3, color=YELLOW)

        eq_peres = MathTex(r"(\sqrt{2})^2 = 2", font_size=36, color=YELLOW)
        eq_ck = MathTex(r"1 + 1 = 2", font_size=36, color=YELLOW)
        eq_peres.next_to(arrow_left, DOWN, buff=0.2)
        eq_ck.next_to(arrow_right, DOWN, buff=0.2)

        self.play(Create(arrow_left), Create(arrow_right), run_time=0.5)
        self.play(Write(eq_peres), Write(eq_ck), run_time=1)
        self.wait(2)

        # Highlight "2" in both
        box_peres = SurroundingRectangle(eq_peres[-1], color=YELLOW, buff=0.1)
        box_ck = SurroundingRectangle(eq_ck[-1], color=YELLOW, buff=0.1)
        self.play(Create(box_peres), Create(box_ck), run_time=0.5)
        self.wait(1)

        # The principle
        self.play(FadeOut(left_group), FadeOut(right_group),
                  FadeOut(arrow_left), FadeOut(arrow_right),
                  FadeOut(box_peres), FadeOut(box_ck), run_time=0.5)

        eq_peres.generate_target()
        eq_ck.generate_target()
        eq_peres.target.move_to(UP * 0.5 + LEFT * 2.5)
        eq_ck.target.move_to(UP * 0.5 + RIGHT * 2.5)
        self.play(MoveToTarget(eq_peres), MoveToTarget(eq_ck), run_time=0.5)

        # Dot product example
        dot_title = Text("Why 2 matters: the dot product", font_size=28)
        dot_title.next_to(eq_peres, DOWN, buff=0.8).shift(RIGHT * 2.5)

        dot_eq = MathTex(
            r"\vec{v}_1 \cdot \vec{v}_2 = ",
            r"1 \cdot 1 + 1 \cdot 1 + 0 \cdot (-2) = 2",
            r"\neq 0",
            font_size=32,
        )
        dot_eq.next_to(dot_title, DOWN, buff=0.3)

        dot_eq2 = MathTex(
            r"\vec{v}_1 \cdot \vec{v}_3 = ",
            r"1 \cdot 1 + 1 \cdot (-1) + 0 \cdot 0 = 0",
            r"\ \checkmark",
            font_size=32,
        )
        dot_eq2.next_to(dot_eq, DOWN, buff=0.3)
        dot_eq2[-1].set_color(KS_GREEN)

        self.play(Write(dot_title), run_time=0.5)
        self.play(Write(dot_eq), run_time=1)
        self.wait(1)
        self.play(Write(dot_eq2), run_time=1)
        self.wait(2)

        principle = Text(
            "Cancellation to zero requires the number 2\nfrom the alphabet's arithmetic",
            font_size=26, color=YELLOW,
        ).to_edge(DOWN)
        self.play(Write(principle), run_time=1)
        self.wait(3)

        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1)
```

- [ ] **Step 2: Test render and commit**

```bash
cd C:/Users/Michael\ Kernaghan/contextuality/video/manim
manim -pql scene4_pattern.py ThePattern
git add video/manim/scene4_pattern.py
git commit -m "feat(video): implement Scene 4 — The Pattern"
```

---

### Task 10: Scene 5 — Two Architectures

**Files:**
- Create: `contextuality/video/manim/scene5_architectures.py`

- [ ] **Step 1: Write scene5_architectures.py**

This scene shows the Gamma-10 graph, highlights its copies inside CK-31, then contrasts with Peres-33's hub architecture.

```python
# contextuality/video/manim/scene5_architectures.py
"""Scene 5: Two Architectures — Gamma graph vs hub-spoke."""

from manim import *
from pathlib import Path
import sys
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
from shared.colors import *


class TwoArchitectures(Scene):
    def construct(self):
        title = Text("Two Architectures", font_size=42).to_edge(UP)
        self.play(Write(title), run_time=0.8)

        # Show KS-10 Gamma graph image
        gamma_img = ImageMobject("../assets/ks-10-gamma.gif").scale(2)
        gamma_label = Text("The Gamma Graph: 10 rays, cyclic structure", font_size=26)
        gamma_label.next_to(gamma_img, DOWN, buff=0.3)

        self.play(FadeIn(gamma_img), Write(gamma_label), run_time=1.5)
        self.wait(3)

        # Transition to CK-31: "6 copies inside"
        copies_text = Text("CK-31 contains 6 copies", font_size=30, color=KS_HIGHLIGHT)
        copies_text.to_edge(DOWN)
        self.play(Write(copies_text), run_time=0.8)
        self.wait(2)

        self.play(FadeOut(gamma_img), FadeOut(gamma_label), FadeOut(copies_text),
                  run_time=0.5)

        # Side-by-side comparison
        # Left: CK-31 = cyclic architecture
        ck_label = Text("CK-31: Cyclic", font_size=30, color=GREEN_C)
        ck_desc = Text("6 Gamma cycles\nchained together", font_size=22)
        ck_group = VGroup(ck_label, ck_desc).arrange(DOWN, buff=0.3).shift(LEFT * 3)

        # Right: Peres-33 = hub architecture
        p_label = Text("Peres-33: Hub-Spoke", font_size=30, color=TEAL_C)
        p_desc = Text("3 axis rays (degree 8)\nanchor the structure", font_size=22)
        p_group = VGroup(p_label, p_desc).arrange(DOWN, buff=0.3).shift(RIGHT * 3)

        # Divider
        divider = Line(UP * 2, DOWN * 2, color=GREY)

        self.play(Create(divider), FadeIn(ck_group), FadeIn(p_group), run_time=1)
        self.wait(1)

        # Gamma count comparison
        ck_count = Text("Gamma copies: 6", font_size=26, color=YELLOW).next_to(ck_group, DOWN, buff=0.5)
        p_count = Text("Gamma copies: 0", font_size=26, color=GREY_B).next_to(p_group, DOWN, buff=0.5)

        self.play(Write(ck_count), Write(p_count), run_time=0.8)
        self.wait(2)

        # Punchline
        punchline = Text(
            "Same puzzle. Same impossibility.\nCompletely different engineering.",
            font_size=28, color=YELLOW,
        ).to_edge(DOWN)
        self.play(Write(punchline), run_time=1)
        self.wait(3)

        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1)
```

- [ ] **Step 2: Test render and commit**

```bash
cd C:/Users/Michael\ Kernaghan/contextuality/video/manim
manim -pql scene5_architectures.py TwoArchitectures
git add video/manim/scene5_architectures.py
git commit -m "feat(video): implement Scene 5 — Two Architectures"
```

---

### Task 11: Scene 6 — Following the Pattern

**Files:**
- Create: `contextuality/video/manim/scene6_following_pattern.py`

- [ ] **Step 1: Write scene6_following_pattern.py**

```python
# contextuality/video/manim/scene6_following_pattern.py
"""Scene 6: Following the Pattern — island exploration and pool merge."""

from manim import *
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from shared.ks_data import ISLANDS
from shared.colors import *


class FollowingThePattern(Scene):
    def construct(self):
        title = Text("Following the Pattern", font_size=42).to_edge(UP)
        self.play(Write(title), run_time=0.8)

        # Question
        question = Text(
            "If integers give 31 and √2 gives 33...\nwhat about other number systems?",
            font_size=28,
        )
        self.play(Write(question), run_time=1.5)
        self.wait(2)
        self.play(FadeOut(question), run_time=0.5)

        # Show islands appearing one by one
        island_mobjects = []
        for i, island in enumerate(ISLANDS):
            row = Text(
                f"{island['name']}: {island['min_ks']} vectors — {island['alphabet']}",
                font_size=24,
                color=ISLAND_COLORS[i],
            )
            row.move_to(UP * (1.5 - i * 0.6))
            island_mobjects.append(row)

        for mob in island_mobjects:
            self.play(FadeIn(mob, shift=RIGHT * 0.5), run_time=0.6)
            self.wait(0.3)

        self.wait(2)

        # Island map label
        map_label = Text("Six Algebraic Islands", font_size=32, color=YELLOW)
        map_label.to_edge(DOWN)
        self.play(Write(map_label), run_time=0.8)
        self.wait(2)

        # Clear for pool merge
        self.play(*[FadeOut(m) for m in island_mobjects], FadeOut(map_label), run_time=0.5)

        # Pool merge result
        merge_title = Text("Pool Merge Experiment", font_size=32).move_to(UP * 2)
        merge_desc = VGroup(
            Text("CK-31 pool (49 rays) + Peres-33 pool (49 rays)", font_size=24),
            Text("= 85 merged rays (13 shared)", font_size=24),
            Text("", font_size=10),
            Text("Cross-island orthogonal triples: 0", font_size=26, color=KS_CONFLICT),
            Text("", font_size=10),
            Text("Minimum KS subset found: 31", font_size=26, color=YELLOW),
            Text("(It's just CK-31 again)", font_size=22, color=GREY_B),
        ).arrange(DOWN, buff=0.15).next_to(merge_title, DOWN, buff=0.5)

        self.play(Write(merge_title), run_time=0.5)
        for mob in merge_desc:
            self.play(FadeIn(mob), run_time=0.4)

        self.wait(3)

        isolation = Text(
            "The algebraic islands are truly isolated.",
            font_size=28, color=YELLOW,
        ).to_edge(DOWN)
        self.play(Write(isolation), run_time=1)
        self.wait(3)

        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1)
```

- [ ] **Step 2: Test render and commit**

```bash
cd C:/Users/Michael\ Kernaghan/contextuality/video/manim
manim -pql scene6_following_pattern.py FollowingThePattern
git add video/manim/scene6_following_pattern.py
git commit -m "feat(video): implement Scene 6 — Following the Pattern"
```

---

### Task 12: Scene 7 — Why Two and Three

**Files:**
- Create: `contextuality/video/manim/scene7_boundary.py`

- [ ] **Step 1: Write scene7_boundary.py**

```python
# contextuality/video/manim/scene7_boundary.py
"""Scene 7: Why Two and Three — the two mechanisms and the boundary."""

from manim import *
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from shared.colors import *


class WhyTwoAndThree(Scene):
    def construct(self):
        title = Text("The Boundary", font_size=42).to_edge(UP)
        self.play(Write(title), run_time=0.8)

        # Mechanism 1: Modulus-2
        mech1_label = Text("Mechanism 1: Modulus-2", font_size=28, color=BLUE_C)
        mech1_eq = MathTex(r"|x|^2 = 2", font_size=44, color=BLUE_C)
        mech1_examples = Text(
            "Integer (1+1=2), √2, √-2, Heegner-7, Golden",
            font_size=20, color=GREY_B,
        )
        mech1 = VGroup(mech1_label, mech1_eq, mech1_examples).arrange(DOWN, buff=0.2)
        mech1.shift(LEFT * 3 + UP * 0.5)

        # Mechanism 2: Phase
        mech2_label = Text("Mechanism 2: Phase", font_size=28, color=PURPLE_C)
        mech2_eq = MathTex(r"1 + \omega + \omega^2 = 0", font_size=44, color=PURPLE_C)
        mech2_examples = Text("Eisenstein integers", font_size=20, color=GREY_B)
        mech2 = VGroup(mech2_label, mech2_eq, mech2_examples).arrange(DOWN, buff=0.2)
        mech2.shift(RIGHT * 3 + UP * 0.5)

        self.play(FadeIn(mech1), run_time=1)
        self.wait(1.5)
        self.play(FadeIn(mech2), run_time=1)
        self.wait(2)

        # The boundary
        boundary = Text(
            "Every KS set we found uses one of these two tricks.\nAlphabets with generator norm ≥ 3 never produce KS sets.",
            font_size=24, color=YELLOW,
        ).move_to(DOWN * 1.5)
        self.play(Write(boundary), run_time=1.5)
        self.wait(3)

        # Open question
        self.play(FadeOut(mech1), FadeOut(mech2), FadeOut(boundary), run_time=0.5)

        open_q = Text(
            "Whether this boundary holds for all number fields\nremains an open question.",
            font_size=28,
        ).move_to(UP * 0.5)
        self.play(Write(open_q), run_time=1.5)
        self.wait(2)

        # Paper citation
        citation = Text(
            '"The Algebraic Landscape of Kochen-Specker Sets\nin Dimension Three"',
            font_size=24, color=GREY_B,
        ).move_to(DOWN * 0.5)
        arxiv = Text("Available on arXiv", font_size=22, color=GREY).next_to(citation, DOWN)

        self.play(FadeIn(citation), FadeIn(arxiv), run_time=1)
        self.wait(4)

        self.play(*[FadeOut(m) for m in self.mobjects], run_time=2)
```

- [ ] **Step 2: Test render and commit**

```bash
cd C:/Users/Michael\ Kernaghan/contextuality/video/manim
manim -pql scene7_boundary.py WhyTwoAndThree
git add video/manim/scene7_boundary.py
git commit -m "feat(video): implement Scene 7 — The Boundary"
```

---

### Task 13: Generate Voiceover Audio

**Files:**
- Create: `contextuality/video/generate_audio.py`
- Output: `contextuality/video/audio/scene1.mp3` through `scene7.mp3`

- [ ] **Step 1: Set up ElevenLabs API key**

Check for existing key or add to api-keys-master.txt:

```bash
grep -i "eleven" "E:/Blockchain-Backups/Keystores/API-Keys/api-keys-master.txt"
```

If no key exists, sign up at elevenlabs.io and save the key.

- [ ] **Step 2: Write generate_audio.py**

```python
# contextuality/video/generate_audio.py
"""Generate voiceover audio from narration script using ElevenLabs API."""

import os
from pathlib import Path
from elevenlabs import ElevenLabs

# Read API key
api_key = None
for line in Path(r"E:\Blockchain-Backups\Keystores\API-Keys\api-keys-master.txt").read_text(encoding="utf-8").splitlines():
    if "elevenlabs" in line.lower() or "eleven_labs" in line.lower():
        api_key = line.strip().split(": ")[-1]
        break

if not api_key:
    raise ValueError("ElevenLabs API key not found in api-keys-master.txt")

client = ElevenLabs(api_key=api_key)

AUDIO_DIR = Path(__file__).parent / "audio"
AUDIO_DIR.mkdir(exist_ok=True)

# Scene narration texts (extracted from narration_script.md)
SCENES = {
    "scene1": """Can nature have pre-existing answers to every question you could ask it? ...""",
    # ... fill in from narration_script.md
}

VOICE_ID = "pNInz6obpgDQGcFmaJgB"  # "Adam" - deep, clear, authoritative
# Alternative: browse voices at api.elevenlabs.io/v1/voices

for scene_name, text in SCENES.items():
    print(f"Generating {scene_name}...")
    audio = client.text_to_speech.convert(
        voice_id=VOICE_ID,
        text=text,
        model_id="eleven_multilingual_v2",
    )
    output_path = AUDIO_DIR / f"{scene_name}.mp3"
    with open(output_path, "wb") as f:
        for chunk in audio:
            f.write(chunk)
    print(f"  Saved to {output_path}")

print("Done!")
```

- [ ] **Step 3: Extract scene texts from narration_script.md into the script**

Copy the finalized narration text for each scene into the SCENES dict.

- [ ] **Step 4: Run audio generation**

```bash
cd C:/Users/Michael\ Kernaghan/contextuality/video
python -u generate_audio.py
```

Expected: 7 MP3 files in `video/audio/`.

- [ ] **Step 5: Listen to each audio file and note timings**

```bash
start "" "C:/Users/Michael Kernaghan/contextuality/video/audio/scene1.mp3"
```

Note the duration of each scene's audio for Manim timing adjustment.

- [ ] **Step 6: Commit**

```bash
git add video/generate_audio.py video/audio/*.mp3
git commit -m "feat(video): generate voiceover audio for all 7 scenes"
```

---

### Task 14: Render Final Quality and Composite

**Files:**
- Create: `contextuality/video/render_all.py`
- Create: `contextuality/video/composite.py`

- [ ] **Step 1: Write render_all.py**

```python
# contextuality/video/render_all.py
"""Render all scenes at production quality."""

import subprocess
from pathlib import Path

MANIM_DIR = Path(__file__).parent / "manim"
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

SCENES = [
    ("scene1_puzzle.py", "ThePuzzle"),
    ("scene2_two_cubes.py", "TheTwoCubes"),
    ("scene3_coloring_game.py", "TheColoringGame"),
    ("scene4_pattern.py", "ThePattern"),
    ("scene5_architectures.py", "TwoArchitectures"),
    ("scene6_following_pattern.py", "FollowingThePattern"),
    ("scene7_boundary.py", "WhyTwoAndThree"),
]

for filename, classname in SCENES:
    print(f"\n{'='*60}")
    print(f"Rendering {filename}::{classname}")
    print(f"{'='*60}")
    cmd = [
        "manim", "-qh",  # high quality (1080p)
        "--format", "mp4",
        "-o", f"{classname}.mp4",
        str(MANIM_DIR / filename),
        classname,
    ]
    subprocess.run(cmd, check=True)
    print(f"Done: {classname}.mp4")
```

- [ ] **Step 2: Write composite.py**

```python
# contextuality/video/composite.py
"""Composite scene videos with voiceover audio into final video."""

import subprocess
from pathlib import Path

VIDEO_DIR = Path(__file__).parent / "output"
AUDIO_DIR = Path(__file__).parent / "audio"
FINAL = VIDEO_DIR / "contextuality_video.mp4"

# Each scene: (video_file, audio_file)
SCENES = [
    ("ThePuzzle.mp4", "scene1.mp3"),
    ("TheTwoCubes.mp4", "scene2.mp3"),
    ("TheColoringGame.mp4", "scene3.mp3"),
    ("ThePattern.mp4", "scene4.mp3"),
    ("TwoArchitectures.mp4", "scene5.mp3"),
    ("FollowingThePattern.mp4", "scene6.mp3"),
    ("WhyTwoAndThree.mp4", "scene7.mp3"),
]

# Step 1: Merge each scene's video with its audio
merged = []
for i, (video, audio) in enumerate(SCENES):
    out = VIDEO_DIR / f"merged_scene{i+1}.mp4"
    cmd = [
        "ffmpeg", "-y",
        "-i", str(VIDEO_DIR / video),
        "-i", str(AUDIO_DIR / audio),
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        str(out),
    ]
    subprocess.run(cmd, check=True)
    merged.append(out)

# Step 2: Create concat list
concat_file = VIDEO_DIR / "concat.txt"
with open(concat_file, "w") as f:
    for m in merged:
        f.write(f"file '{m.name}'\n")

# Step 3: Concatenate all scenes
cmd = [
    "ffmpeg", "-y",
    "-f", "concat",
    "-safe", "0",
    "-i", str(concat_file),
    "-c", "copy",
    str(FINAL),
]
subprocess.run(cmd, check=True)
print(f"\nFinal video: {FINAL}")
```

- [ ] **Step 3: Render all scenes at production quality**

```bash
cd C:/Users/Michael\ Kernaghan/contextuality/video
python -u render_all.py
```

This will take 10-30 minutes depending on scene complexity.

- [ ] **Step 4: Composite final video**

```bash
cd C:/Users/Michael\ Kernaghan/contextuality/video
python -u composite.py
```

- [ ] **Step 5: Watch the final video**

```bash
start "" "C:/Users/Michael Kernaghan/contextuality/video/output/contextuality_video.mp4"
```

Review for:
- Audio/video sync
- Visual timing (do animations match narration beats?)
- Text readability
- Pacing (too fast? too slow?)

- [ ] **Step 6: Commit**

```bash
git add video/render_all.py video/composite.py
git commit -m "feat(video): add render and composite pipeline"
```

---

### Task 15: Follow-up — Paper Note on KS-117 Coordinates

**Files:**
- Modify: `contextuality/paper/algebraic_islands.tex`
- Modify: `contextuality/paper/arxiv-submission/algebraic_islands.tex`

This is a separate follow-up: add a brief historical note in the Introduction mentioning that the original KS-117 construction uses coordinates from Q(cos(pi/10)) — a cyclotomic field — demonstrating that the alphabet-centric perspective has roots in the very first KS construction.

- [ ] **Step 1: Draft a one-sentence addition to the Introduction**

In the paragraph discussing previous approaches (around line 53), add after the sentence about Li, Bright, and Ganesh:

```latex
(Indeed, the original Kochen--Specker construction~\cite{KochenSpecker1967}
uses coordinates from the real cyclotomic field $\Q(\cos\pi/10)$, with
the 18-degree rotations that chain its 15 copies of the fundamental
10-ray gadget introducing algebraic irrationals related to the golden
ratio---an early, if implicit, instance of the alphabet-dependence that
the present paper makes explicit.)
```

- [ ] **Step 2: Add to both paper/ and arxiv-submission/ copies**

- [ ] **Step 3: Recompile and verify**

```bash
cd C:/Users/Michael\ Kernaghan/contextuality/paper
"$LOCALAPPDATA/Programs/MiKTeX/miktex/bin/x64/pdflatex.exe" -interaction=nonstopmode algebraic_islands.tex
"$LOCALAPPDATA/Programs/MiKTeX/miktex/bin/x64/pdflatex.exe" -interaction=nonstopmode algebraic_islands.tex
```

- [ ] **Step 4: Commit (but do NOT push — save for next arXiv revision)**

```bash
git add paper/algebraic_islands.tex paper/arxiv-submission/algebraic_islands.tex
git commit -m "feat(paper): add historical note on KS-117 cyclotomic coordinates"
```
