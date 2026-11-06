---
name: svgg
description: Draw, vectorize, edit, and animate clean, editable SVG directly as text. Use when asked for an icon, logo, illustration, badge, diagram-like graphic, or animation as SVG, when turning a reference image into vector art, or when changing or animating an existing SVG. Works in any agent: with or without file, image, or shell tools.
metadata:
  version: 0.1.0
---

# SVG Drawing

You write the SVG yourself, as source code. No image model, no tracing
library. The output is a file a designer could open and keep editing: few
shapes, named groups, a real `viewBox`, no junk.

Pick the **mode**, write the **brief**, **plan**, **draw**, **check**,
then **deliver**. Do not skip the brief and the plan. Most bad SVGs come
from drawing before deciding on the composition.

## 1. Modes

| Mode | Input | Output |
| --- | --- | --- |
| `create` | Text request | New SVG |
| `reference` | Text plus 1–14 images or SVGs | New SVG that borrows named traits from each reference |
| `vectorize` | One raster image | SVG that reproduces the image as flat vector shapes |
| `edit` | Existing SVG plus a change | Same SVG with only that change |
| `animate` | Existing SVG plus a motion request | Same SVG with CSS animation on its existing groups |

If the request mixes modes (for example "vectorize this and then animate
it"), run them in order and keep each step's output.

## 2. Brief

Restate the request as this brief before drawing. Fill unknowns with
sensible defaults and say which ones you assumed. Do not ask questions
unless the subject itself is unclear.

```text
Subject:      what is drawn
Use and size: where it is shown and at what size (e.g. 24 px UI icon, 512 px app tile)
viewBox:      e.g. 0 0 24 24 for icons, 0 0 512 512 for tiles, 0 0 W H for scenes
Style:        flat | outline | duotone | geometric | line-art | isometric | ...
Palette:      3–6 hex colors, named by role (ink, fill, accent, background)
Composition:  layout, focal point, margins
Must include: required elements and exact text
Avoid:        what must not appear
```

Defaults when unstated: flat style, transparent background, 4–5 colors,
safe margin of 8% of the viewBox on every side, no text.

For `reference` mode, give **each reference one role** and write it into
the brief, for example: `ref 1 → silhouette`, `ref 2 → palette`,
`ref 3 → line weight`. State what to **preserve** and what to **change**.
If you cannot see images, ask for a text description of each reference.

## 3. Plan

Write a short plan, not code yet:

1. **Coordinate grid.** Name key coordinates: center, baseline, horizon,
   left and right edges of the subject. Snap them to whole numbers
   (icons: 0.5 or 1 unit; larger art: 1–4 units).
2. **Layers, back to front.** List the groups you will draw, each with a
   kebab-case id, e.g. `background`, `body`, `head`, `details`, `text`.
   Things that might be animated or edited later get their own group.
3. **Shape choice per part.** Prefer primitives: `rect` (with `rx`),
   `circle`, `ellipse`, `line`, `polyline`, `polygon`, `text`. Use `path`
   only for curves or outlines primitives cannot make.
4. **Palette mapping.** Which part gets which color role.

## 4. Draw

Write the SVG following these rules.

**Root**

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"
     width="512" height="512" role="img" aria-labelledby="title">
  <title id="title">Short description</title>
  ...
</svg>
```

- Always set `viewBox`. Set `width` and `height` to the intended display
  size. Everything visible stays inside the viewBox.
- Put shared colors in a `<style>` block with classes, or use `fill` and
  `stroke` attributes; never mix many one-off inline `style=""` strings.
- `<defs>` only for things used more than once or gradients you really
  need. Every `id` is unique and descriptive.

**Geometry**

- Fewest nodes that hold the shape. A circle is `<circle>`, not a 40-point
  path. A smooth curve uses 2–4 cubic or quadratic segments, not dozens of
  short lines.
- Round coordinates: at most one decimal place; integers for icons when
  possible.
- Closed shapes end with `Z`. No zero-length segments, no duplicate
  consecutive points, no shapes hidden fully under other shapes.
- Symmetric subjects: draw one half in a group and mirror it with
  `transform="matrix(-1 0 0 1 W 0)"` or compute mirrored coordinates
  exactly. Do not eyeball symmetry.
- Draw back to front. Overlap shapes on purpose to avoid hairline gaps
  between adjacent fills.

**Style**

- Outline icons: one stroke width for the whole icon (24 px icons: 1.5 or
  2), `stroke-linecap="round"`, `stroke-linejoin="round"`, `fill="none"`.
- Flat art: solid fills, at most 2 gradients, no filters unless asked.
  Shadows are flat darker shapes, not blurs.
- Text: only when requested, with the exact wording. Use a generic family
  stack (`font-family="system-ui, sans-serif"`), `text-anchor="middle"`
  for centered text, and keep it legible at the target size.

**Forbidden**

`<script>`, `on*=` event attributes, `<foreignObject>`, external
`href`/`xlink:href` URLs, embedded raster `<image>` (unless the user asks),
editor metadata (`sodipodi`, `inkscape`, comments with timestamps).

## 5. Mode-specific rules

**vectorize**

- Reduce the image to 4–10 flat color regions; sample the hex colors from
  the image (or estimate them carefully if you cannot sample).
- Keep the large silhouettes and the composition proportions (measure
  them as fractions of the width and height). Drop texture and noise.
- One group per region of meaning (`sky`, `ground`, `building`, ...).

**edit**

- Change only what was asked. Copy every untouched element byte for byte;
  keep ids, order, and the viewBox.
- After the SVG, list what changed in one or two lines.

**animate**

- Animate the groups that already exist. If a part that must move is not
  in its own group, first wrap it in a `<g id="...">` without changing
  any coordinates, then animate that group.
- Use CSS `@keyframes` in the SVG's `<style>`, animating `transform` and
  `opacity` only. Set `transform-box: fill-box; transform-origin: center;`
  (or an explicit origin) on rotating or scaling groups.
- State duration, easing, and looping in the CSS. Loops must be seamless
  (the last keyframe equals the first).
- Add `@media (prefers-reduced-motion: reduce) { * { animation: none; } }`.
- The first frame (and the reduced-motion version) must look complete.

## 6. Check

Before delivering, check the SVG against this list. Fix and redraw any
failure; at most two repair rounds.

1. **Valid XML**, root has `xmlns` and `viewBox`, all ids unique.
2. **Nothing forbidden** from section 4.
3. **Inside the frame**: every shape within the viewBox and margins.
4. **Silhouette**: the subject reads correctly as a solid shape at the
   final size.
5. **Geometry**: aligned to the grid, symmetric where it should be, no
   stray or hidden shapes, no hairline gaps.
6. **Prompt adherence**: every "must include" item is present, every
   "avoid" item absent, the palette matches.
7. **Legibility at final size**: details smaller than about 1/24 of the
   viewBox are removed or merged (for 24 px icons, nothing thinner than
   1 unit).
8. **Structure**: named groups, primitives where possible, nothing a
   designer would have to clean up.

If you can run tools, use them:

- Validate: `xmllint --noout file.svg` or any XML parser.
- Render: `rsvg-convert -w 512 file.svg -o file.png`, or
  `magick file.svg file.png`, or a headless browser. **Look at the PNG**
  if you can view images, and judge items 3–7 from the picture, not from
  the code. Also render at the final display size (e.g. 24 px) for icons.
- Optimize only if asked; never let an optimizer remove ids or groups.

If you cannot run tools, check the list by reading the code carefully,
especially coordinates against the viewBox.

## 7. Deliver

- If you can write files, save to the path the user gave, or to a
  descriptive kebab-case name such as `cloud-upload-icon.svg`.
- Otherwise output the SVG in a single fenced ```svg block. Only one
  final SVG per requested asset; no partial drafts in the final answer.
- After the SVG, give at most 5 lines: the brief's assumed defaults,
  the groups (for later edits or animation), and any check you could not
  run.

## 8. Example

Request: "a 24 px outline icon of a cloud with an upload arrow".

```text
Subject: cloud with upward arrow   Use and size: UI icon, 24 px
viewBox: 0 0 24 24   Style: outline, stroke 2, round caps
Palette: ink currentColor   Must include: cloud, arrow up   Avoid: fill
```

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"
     fill="none" stroke="currentColor" stroke-width="2"
     stroke-linecap="round" stroke-linejoin="round" role="img" aria-labelledby="title">
  <title id="title">Cloud upload</title>
  <g id="cloud">
    <path d="M7 18H6a4 4 0 0 1-.5-8A6 6 0 0 1 17 8.5h.5a4.5 4.5 0 0 1 .5 9H17"/>
  </g>
  <g id="arrow">
    <line x1="12" y1="12" x2="12" y2="21"/>
    <polyline points="9 15 12 12 15 15"/>
  </g>
</svg>
```
