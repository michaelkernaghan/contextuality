# Contextuality Video Presentation Design

## Overview

A popular science video presentation (~5-12 minutes) explaining the ideas behind the paper "The Algebraic Landscape of Kochen-Specker Sets in Dimension Three." Targets a physics-literate audience (PBS Space Time level) who know linear algebra and basic QM but not KS theory.

**Format**: Voiceover narration over Manim animations + static book illustrations
**Production model**: Storyboard-first (Approach B)
**Narration**: AI text-to-speech (ElevenLabs-style) from written script
**Visual style**: 3Blue1Brown-inspired mathematical animations, anchored by published diagrams

---

## Keystone Assets

Four published diagrams, ideally all rendered as 3D cube lattice diagrams in a unified visual style:

| Image | Source | File | Alphabet | Grid |
|-------|--------|------|----------|------|
| KS-117 | Kochen-Specker 1967 | `scans/ks-117.gif` | Q(cos pi/10) — irrationals | **No grid possible** |
| KS-33 | Peres book p.198 | `scans/peres-33-page198-cube.jpg` | {0, +/-1, +/-sqrt(2)} | 5x5x5 |
| KS-31 | Peres book p.114 | `scans/conway-kochen-31.jpg` | {0, +/-1, +/-2} | 5x5x5 |
| KS-10 | Gamma graph | `scans/ks-10-gamma.gif` | {0, +/-1} at x=y=1 | 3x3x3 |

**Key discovery**: The KS-117 cannot be rendered as a cube — its coordinates live in the cyclotomic field Q(cos(pi/10)), involving golden-ratio-related irrationals from 18-degree rotations. No finite lattice grid suffices. This is narratively significant: the progression from 117 to 33 to 31 is not just fewer vectors but simpler coordinates. The ability to draw the later constructions as cubes IS the algebraic breakthrough.

**Visual plan**: Show KS-117 as its published circular orthogonality graph (the dense, intimidating web). Then transition to the cubes for KS-33 and KS-31 with narration emphasizing the coordinate simplification. The KS-10 Gamma gadget can be rendered as a small 3x3x3 cube (at x=y=1 it uses only {0, +/-1}) or as its published graph diagram.

Additional reference: Rajan & Visser 2019 (arXiv:1708.01380) for the Gleason's theorem connection.

---

## Narrative Arc

The story: "I stared at two pictures in a textbook and noticed a pattern in the coordinates. Following that pattern led to a whole landscape of discovery."

### Scene 1: The Puzzle (30-45s)

**Visual**: Fade in on a 3D coordinate system. Three arrows appear (an orthogonal basis). Colors pulse.

**Narration concept**: "Can nature have pre-existing answers to every question you could ask it? In 1967, two mathematicians proved the answer is no -- at least not if those answers have to be consistent. The proof is a coloring puzzle."

**Manim elements**:
- 3D orthogonal basis vectors appearing
- Simple coloring animation: assign 0 or 1 to each ray, one 1 per triple
- Brief flash of the KS-117 graph (the original, intimidating web)
- Transition: "Over the decades, mathematicians found simpler and simpler versions of this puzzle..."

### Scene 2: The Two Cubes (60-90s)

**Visual**: The heart of the video. Start with book scan full-screen (2-3 seconds each for authenticity), then crossfade to Manim-rendered 3D cube that matches the same construction, allowing rotation and coordinate highlighting.

**Narration concept**: "In 1991, Asher Peres found a version with just 33 vectors. They fit inside a cube." [Show KS-33 cube] "The coordinates use zero, one, and the square root of two." [Highlight coordinate values on the cube]

"Then John Conway and Simon Kochen found an even smaller version -- 31 vectors." [Show KS-31 cube] "This time, the coordinates are just integers: zero, one, and two."

"Look at these two cubes side by side." [Both cubes on screen] "They're different sizes, different alphabets, different numbers of dots. But something about them feels... related."

**Manim elements**:
- 3D rotating cube lattice for KS-33 (5x5x5 with sqrt(2) positions)
- 3D rotating cube lattice for KS-31 (5x5x5 with integer positions)
- Side-by-side comparison with coordinate labels highlighted
- Book scan insets shown briefly for authenticity

### Scene 3: The Coloring Game (45-60s)

**Visual**: Animate the coloring contradiction on one of the cubes (KS-31 preferred -- fewer vectors, cleaner).

**Narration concept**: "Here's the puzzle. Take these 31 directions. Group them into sets of three mutually perpendicular rays -- orthogonal triples. Now try to color them: each triple must have exactly one green ray and two red rays. And if a ray appears in multiple triples, it must have the same color everywhere."

"Try it." [Animate coloring attempts] "You can't. No matter what you do, you get stuck. That's the proof: nature can't have pre-assigned answers to all these questions simultaneously."

**Manim elements**:
- Orthogonality graph (vertices = rays, edges = orthogonal pairs)
- Animated coloring: green/red propagation through the graph
- Show contradiction: forced assignment creates a conflict
- The coloring "breaks" visually (flash/shake)

### Scene 4: The Pattern (45-60s)

**Visual**: Zoom into coordinates on each cube. Numbers highlighted and extracted.

**Narration concept**: "Look at the coordinates again. The 33-vector set uses zero, one, and the square root of two. The 31-vector set uses zero, one, and two. One set has sqrt(2). The other has 2. What if that's not a coincidence?"

"Both of these numbers have something in common: when you square them, you get 2. The square root of two squared is two. And two... well, one plus one is two. They're both ways of making the number two from the alphabet."

"This is the pattern. Both cubes work because their coordinate system supports a specific algebraic identity -- a way to make dot products vanish exactly."

**Manim elements**:
- Coordinate labels extracted from cubes and displayed
- sqrt(2)^2 = 2 and 1+1 = 2 shown as equations
- Visual: the "cancellation identity" -- how dot products hit zero
- Orthogonal triple shown with explicit dot product computation

### Scene 5: Two Architectures (45-60s)

**Visual**: The KS-10 Gamma graph, then show it embedded inside KS-31. Then show KS-33's hub structure.

**Narration concept**: "But here's what's surprising. Despite looking similar, these two sets achieve their contradiction in completely different ways."

"The 31-vector set inherits the architecture of the original 117-vector proof from 1967. Inside it, you can find six copies of this little pattern" [show KS-10 Gamma graph] "-- a cycle of interlocking triples that forces a parity contradiction. It's the engine of the proof, used since the very beginning."

"The 33-vector set has zero copies of this pattern. It achieves its contradiction through a hub-and-spoke architecture, where three high-degree axis rays anchor the whole structure."

"Same puzzle, same impossibility, completely different engineering."

**Manim elements**:
- KS-10 Gamma graph animated (10 vertices, cyclic structure)
- Highlight 6 copies of Gamma inside the KS-31 orthogonality graph
- Show KS-33 hub structure: 3 axis rays (degree 8) with spokes
- Side-by-side: cyclic vs hub architecture

### Scene 6: Following the Pattern (60-90s)

**Visual**: The alphabet exploration. New cubes appearing as different number systems are tried.

**Narration concept**: "If integers give 31 vectors and the square root of two gives 33... what happens if we try other number systems?"

"Cube roots of unity -- the Eisenstein integers. 33 vectors, but a completely new graph type."

"The ring of integers in the field generated by the square root of negative seven. 43 vectors. A genuinely new construction that no one had seen before."

"The golden ratio. 52 vectors -- but these are invisible to a direct search. You only find them if you close the coordinate system under cross products."

"Six algebraic islands. Each one a different number system. Each one producing a KS set with its own geometry."

"We tried combining them -- merging the 31-vector integer pool with the 33-vector sqrt(2) pool, hoping to find something smaller. But the two pools don't interlock. There are zero orthogonal triples mixing rays from both. The algebraic islands are truly isolated."

**Manim elements**:
- New cube lattices appearing for each island (Eisenstein, Heegner-7, Golden)
- "Island map" visualization: six islands with ray counts
- Pool merge animation: two pools overlap, but no cross-island triads form
- The algebraic isolation visualized: oil-and-water metaphor

### Scene 7: Why Two and Three (30-45s)

**Visual**: The two cancellation mechanisms. The boundary.

**Narration concept**: "Every construction we found uses one of exactly two algebraic tricks. Either: make something square to two -- the modulus-2 mechanism. Or: make unit-modulus terms cancel to zero -- the phase mechanism, like one plus omega plus omega-squared equals zero."

"That's it. That's the boundary between number systems that support these impossible colorings and those that don't. If your alphabet can't do one of these two tricks, you can't build a Kochen-Specker set."

"Whether this boundary holds for all number fields remains an open question."

**Manim elements**:
- Two equations animated: |x|^2 = 2 and 1 + omega + omega^2 = 0
- "Boundary" visualization: alphabets above/below the threshold
- The six islands colored by mechanism type (modulus-2 vs phase)
- Close with the open question and paper citation

---

## Computational Results (for narration)

### Pool Merge Experiment
- Merged pool: 85 rays (49 integer + 49 Peres, 13 shared)
- Zero cross-island triads
- Minimum found: 31 (CK-31 again)
- Bimodal distribution: greedy minimization lands at 31 or 33

### 10-Ray Generator (Gamma Graph) Analysis
- CK-31: 6 copies of the cyclic Gamma graph
- Peres-33: 0 copies (uses hub-and-spoke instead)
- Both share: star gadgets (3 triads/hub), linear chains
- The cyclic contradiction mechanism is unique to the integer island

### KS-117 Coordinates (Research Complete)
- Alphabet: Q(cos pi/10) — the real cyclotomic field, involving cos(18 deg) = sqrt(10 + 2*sqrt(5))/4
- Construction: 15 copies of Gamma_1 rotated by 18-degree increments (3 groups of 5, between orthogonal reference axes)
- **Cannot be rendered on any finite integer grid** — coordinates are algebraic irrationals
- The Gamma_1 gadget alone at x=y=1 uses just {0, +/-1}, but the chaining/rotation construction introduces irrationals
- This is narratively significant: the history of KS sets is a history of coordinate simplification (irrationals -> algebraic irrationals -> integers)
- Use the published circular graph image for the 117; the cubes are reserved for the constructions that earned them

---

## Production Pipeline

### Project Structure
```
contextuality/video/
  storyboard/          # scene-by-scene notes + narration script
  manim/               # Manim scene files (one per scene)
  audio/               # Generated voiceover clips
  assets/              # Book scans, static images
  output/              # Rendered scenes + final composite
```

### Tools
- **Manim Community Edition** -- mathematical animations (3D cubes, graphs, coloring)
- **Static images** -- Peres book scans (KS-33 p.198, KS-31 p.114), KS-117 graph, KS-10 Gamma
- **ElevenLabs API** (or similar) -- text-to-speech from narration script
- **FFmpeg** -- composite audio + video segments, final assembly

### Production Order
1. Write full narration script (all 7 scenes)
2. Generate voiceover audio per scene
3. Build Manim animations scene by scene, timed to audio
4. Composite static images (book scans) at appropriate moments
5. Assemble final video with FFmpeg
6. Review and iterate

### Manim Scene Inventory

| Scene | Manim elements | Complexity |
|-------|---------------|------------|
| 1 | 3D basis vectors, simple coloring, KS-117 flash | Low |
| 2 | Two 3D cube lattices (KS-33, KS-31), rotation, coordinate labels | High |
| 3 | Orthogonality graph, animated coloring propagation, contradiction | High |
| 4 | Coordinate extraction, equation animations, dot product | Medium |
| 5 | KS-10 Gamma graph, subgraph highlighting, hub-spoke diagram | High |
| 6 | Multiple cube lattices, island map, pool merge animation | High |
| 7 | Equation animations, boundary visualization, closing | Medium |

---

## Open Items

1. **KS-117 alphabet**: Research in progress. Determines whether we can render it as a cube.
2. **KS-10 coordinates**: Need to extract from the KS-117 coordinate set.
3. **ElevenLabs voice selection**: Choose a voice that fits PBS Space Time tone.
4. **Music/sound design**: Background music or not? Sound effects for the contradiction moment?
5. **Pacing**: Aim for 5-8 minutes; may stretch to 12 if the story demands it.
6. **Copyright**: Book scans from Peres are for educational/fair use; confirm this is acceptable for YouTube.
7. **Gleason connection**: The Rajan-Visser paper shows KS follows trivially from Gleason. Worth a one-line mention in Scene 1 or 7? Or save for a follow-up video?
