---
title: "ascii-video — reference material"
date: "2026-10-06"
type: "note"
stage: "Knowledge"
topic: "ascii_video-reference"
tags: [skill-reference, ascii-video]
source_classes: [synthesis]
status: "verified"
summary: "Deep reference sections moved verbatim out of ascii-video/SKILL.md so the loaded body stays small."
---

## Creative Direction

### Aesthetic Dimensions

| Dimension | Options | Reference |
|-----------|---------|-----------|
| **Character palette** | Density ramps, block elements, symbols, scripts (katakana, Greek, runes, braille), project-specific | `architecture.md` § Palettes |
| **Color strategy** | HSV, OKLAB/OKLCH, discrete RGB palettes, auto-generated harmony, monochrome, temperature | `architecture.md` § Color System |
| **Background texture** | Sine fields, fBM noise, domain warp, voronoi, reaction-diffusion, cellular automata, video | `effects.md` |
| **Primary effects** | Rings, spirals, tunnel, vortex, waves, interference, aurora, fire, SDFs, strange attractors | `effects.md` |
| **Particles** | Sparks, snow, rain, bubbles, runes, orbits, flocking boids, flow-field followers, trails | `effects.md` § Particles |
| **Shader mood** | Retro CRT, clean modern, glitch art, cinematic, dreamy, industrial, psychedelic | `shaders.md` |
| **Grid density** | xs(8px) through xxl(40px), mixed per layer | `architecture.md` § Grid System |
| **Coordinate space** | Cartesian, polar, tiled, rotated, fisheye, Möbius, domain-warped | `effects.md` § Transforms |
| **Feedback** | Zoom tunnel, rainbow trails, ghostly echo, rotating mandala, color evolution | `composition.md` § Feedback |
| **Masking** | Circle, ring, gradient, text stencil, animated iris/wipe/dissolve | `composition.md` § Masking |
| **Transitions** | Crossfade, wipe, dissolve, glitch cut, iris, mask-based reveal | `shaders.md` § Transitions |

### Per-Section Variation

Never use the same config for the entire video. For each section/scene:
- **Different background effect** (or compose 2-3)
- **Different character palette** (match the mood)
- **Different color strategy** (or at minimum a different hue)
- **Vary shader intensity** (more bloom during peaks, more grain during quiet)
- **Different particle types** if particles are active

### Project-Specific Invention

For every project, invent at least one of:
- A custom character palette matching the theme
- A custom background effect (combine/modify existing building blocks)
- A custom color palette (discrete RGB set matching the brand/mood)
- A custom particle character set
- A novel scene transition or visual moment

Don't just pick from the catalog. The catalog is vocabulary — you write the poem.

## Creative Divergence (use only when user requests experimental/creative/unique output)

If the user asks for creative, experimental, surprising, or unconventional output, select the strategy that best fits and reason through its steps BEFORE generating code.

- **Forced Connections** — when the user wants cross-domain inspiration ("make it look organic," "industrial aesthetic")
- **Conceptual Blending** — when the user names two things to combine ("ocean meets music," "space + calligraphy")
- **Oblique Strategies** — when the user is maximally open ("surprise me," "something I've never seen")

### Forced Connections
1. Pick a domain unrelated to the visual goal (weather systems, microbiology, architecture, fluid dynamics, textile weaving)
2. List its core visual/structural elements (erosion → gradual reveal; mitosis → splitting duplication; weaving → interlocking patterns)
3. Map those elements onto ASCII characters and animation patterns
4. Synthesize — what does "erosion" or "crystallization" look like in a character grid?

### Conceptual Blending
1. Name two distinct visual/conceptual spaces (e.g., ocean waves + sheet music)
2. Map correspondences (crests = high notes, troughs = rests, foam = staccato)
3. Blend selectively — keep the most interesting mappings, discard forced ones
4. Develop emergent properties that exist only in the blend

### Oblique Strategies
1. Draw one: "Honor thy error as a hidden intention" / "Use an old idea" / "What would your closest friend do?" / "Emphasize the flaws" / "Turn it upside down" / "Only a part, not the whole" / "Reverse"
2. Interpret the directive against the current ASCII animation challenge
3. Apply the lateral insight to the visual design before writing code
