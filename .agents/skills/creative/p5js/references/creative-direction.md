---
title: "Creative Direction"
date: "2026-10-06"
type: "note"
stage: "Knowledge"
topic: "creative-direction"
tags: [skill-reference, p5js]
source_classes: [synthesis]
status: "verified"
related:
  - ".agents/skills/creative/p5js/SKILL.md"
summary: "| Dimension | Options | Reference |"
---

# Creative Direction

_Moved verbatim out of SKILL.md so the trigger body stays small._

## Creative Direction

### Aesthetic Dimensions

| Dimension | Options | Reference |
|-----------|---------|-----------|
| **Color system** | HSB/HSL, RGB, named palettes, procedural harmony, gradient interpolation | `references/color-systems.md` |
| **Noise vocabulary** | Perlin noise, simplex, fractal (octaved), domain warping, curl noise | `references/visual-effects.md` § Noise |
| **Particle systems** | Physics-based, flocking, trail-drawing, attractor-driven, flow-field following | `references/visual-effects.md` § Particles |
| **Shape language** | Geometric primitives, custom vertices, bezier curves, SVG paths | `references/shapes-and-geometry.md` |
| **Motion style** | Eased, spring-based, noise-driven, physics sim, lerped, stepped | `references/animation.md` |
| **Typography** | System fonts, loaded OTF, `textToPoints()` particle text, kinetic | `references/typography.md` |
| **Shader effects** | GLSL fragment/vertex, filter shaders, post-processing, feedback loops | `references/webgl-and-3d.md` § Shaders |
| **Composition** | Grid, radial, golden ratio, rule of thirds, organic scatter, tiled | `references/core-api.md` § Composition |
| **Interaction model** | Mouse follow, click spawn, drag, keyboard state, scroll-driven, mic input | `references/interaction.md` |
| **Blend modes** | `BLEND`, `ADD`, `MULTIPLY`, `SCREEN`, `DIFFERENCE`, `EXCLUSION`, `OVERLAY` | `references/color-systems.md` § Blend Modes |
| **Layering** | `createGraphics()` offscreen buffers, alpha compositing, masking | `references/core-api.md` § Offscreen Buffers |
| **Texture** | Perlin surface, stippling, hatching, halftone, pixel sorting | `references/visual-effects.md` § Texture Generation |

### Per-Project Variation Rules

Never use default configurations. For every project:
- **Custom color palette** — never raw `fill(255, 0, 0)`. Always a designed palette with 3-7 colors
- **Custom stroke weight vocabulary** — thin accents (0.5), medium structure (1-2), bold emphasis (3-5)
- **Background treatment** — never plain `background(0)` or `background(255)`. Always textured, gradient, or layered
- **Motion variety** — different speeds for different elements. Primary at 1x, secondary at 0.3x, ambient at 0.1x
- **At least one invented element** — a custom particle behavior, a novel noise application, a unique interaction response

### Project-Specific Invention

For every project, invent at least one of:
- A custom color palette matching the mood (not a preset)
- A novel noise field combination (e.g., curl noise + domain warp + feedback)
- A unique particle behavior (custom forces, custom trails, custom spawning)
- An interaction mechanic the user didn't request but that elevates the piece
- A compositional technique that creates visual hierarchy

### Parameter Design Philosophy

Parameters should emerge from the algorithm, not from a generic menu. Ask: "What properties of *this* system should be tunable?"

**Good parameters** expose the algorithm's character:
- **Quantities** — how many particles, branches, cells (controls density)
- **Scales** — noise frequency, element size, spacing (controls texture)
- **Rates** — speed, growth rate, decay (controls energy)
- **Thresholds** — when does behavior change? (controls drama)
- **Ratios** — proportions, balance between forces (controls harmony)

**Bad parameters** are generic controls unrelated to the algorithm:
- "color1", "color2", "size" — meaningless without context
- Toggle switches for unrelated effects
- Parameters that only change cosmetics, not behavior

Every parameter should change how the algorithm *thinks*, not just how it *looks*. A "turbulence" parameter that changes noise octaves is good. A "particle size" slider that only changes `ellipse()` radius is shallow.


## Creative Divergence (use only when user requests experimental/creative/unique output)

If the user asks for creative, experimental, surprising, or unconventional output, select the strategy that best fits and reason through its steps BEFORE generating code.

- **Conceptual Blending** — when the user names two things to combine or wants hybrid aesthetics
- **SCAMPER** — when the user wants a twist on a known generative art pattern
- **Distance Association** — when the user gives a single concept and wants exploration ("make something about time")

### Conceptual Blending
1. Name two distinct visual systems (e.g., particle physics + handwriting)
2. Map correspondences (particles = ink drops, forces = pen pressure, fields = letterforms)
3. Blend selectively — keep mappings that produce interesting emergent visuals
4. Code the blend as a unified system, not two systems side-by-side

### SCAMPER Transformation
Take a known generative pattern (flow field, particle system, L-system, cellular automata) and systematically transform it:
- **Substitute**: replace circles with text characters, lines with gradients
- **Combine**: merge two patterns (flow field + voronoi)
- **Adapt**: apply a 2D pattern to a 3D projection
- **Modify**: exaggerate scale, warp the coordinate space
- **Purpose**: use a physics sim for typography, a sorting algorithm for color
- **Eliminate**: remove the grid, remove color, remove symmetry
- **Reverse**: run the simulation backward, invert the parameter space

### Distance Association
1. Anchor on the user's concept (e.g., "loneliness")
2. Generate associations at three distances:
   - Close (obvious): empty room, single figure, silence
   - Medium (interesting): one fish in a school swimming the wrong way, a phone with no notifications, the gap between subway cars
   - Far (abstract): prime numbers, asymptotic curves, the color of 3am
3. Develop the medium-distance associations — they're specific enough to visualize but unexpected enough to be interesting
