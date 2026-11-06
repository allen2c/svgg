# Public concepts mapped to skill rules

Source: public product documentation and launch write-ups of a commercial
text-to-SVG model family (read 2026-11-06). Only public, general concepts are
used here; this project ships no code, prompts, or assets from any vendor.

| Public concept | Where it lives in `SKILL.md` |
| --- | --- |
| One model covers four jobs: text to SVG, image to SVG (vectorize), edit, animate | §1 Modes (`create`, `reference`, `vectorize`, `edit`, `animate`) |
| Up to 14 reference images; style and palette transfer is prompt-driven | §1 `reference` mode, 1–14 references |
| With several references, give each one role (silhouette from one, palette from another); separate what to preserve from what to change | §2 Brief, reference roles and preserve/change |
| Generation runs in phases: reasoning, draft, content | §2 Brief → §3 Plan → §4 Draw |
| Prompt template: subject, use and size, style, colors, composition, required details, avoid | §2 Brief fields |
| Size is controlled by asking for a viewBox (e.g. `0 0 24 24`) | §2 `viewBox`, §4 Root |
| Fewer, more precise control points; less node clutter; fewer overlapping paths | §4 Geometry |
| Prefer primitives (shapes, text) over stacked paths | §3 Plan step 3, §4 Geometry |
| Respect spacing, padding, alignment | §2 default 8% margin, §3 coordinate grid |
| Animation moves the groups already in the SVG; a flattened single path will not move cleanly | §5 `animate`, §3 own group for parts that may move |
| Animation prompt structure: element, motion, playback, preserve | §5 `animate` (duration, easing, looping, nothing else moves) |
| Edits: one change per turn with a list of fixed elements | §5 `edit` |
| Vectorize: crop tight, drop background clutter, one explicit simplification | §5 `vectorize` (4–10 flat regions, keep proportions) |
| Judge silhouette, geometry, prompt adherence, legibility at the final size | §6 Check items 4–7 |
| Sanitize SVG: no scripts | §4 Forbidden |

## Not adopted (yet)

- Sampling `n` 1–16 and picking the best: costly for an agent; candidate for a
  later "draft 2–3 thumbnails, pick one" feature experiment.
- Streaming drafts: not portable across agent hosts.
