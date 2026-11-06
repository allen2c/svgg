---
name: svgg
description: Draw, vectorize, edit, and animate clean, editable SVG directly as text. Use when asked for an icon, logo, badge, app tile, illustration, scene, or animation as SVG, when turning a reference image into vector art, or when changing or animating an existing SVG. Works in any agent, with or without file, image, or shell tools.
metadata:
  version: 0.3.0
---

# SVG Drawing

You write the SVG yourself, as source code. No image model, no tracing
library. The result is a file a designer could open and keep editing: few
shapes, named groups, a real `viewBox`, no junk.

Steps: pick the **mode** and **asset type**, write the **brief**, **plan**,
**draw**, **check**, **deliver**. Most bad SVGs come from drawing before
deciding what makes the subject recognizable and where everything goes.

## 1. Mode and asset type

| Mode | Input | Output |
| --- | --- | --- |
| `create` | Text request | New SVG |
| `reference` | Text plus 1–14 images or SVGs | New SVG that borrows named traits from each reference |
| `vectorize` | One raster image | SVG that reproduces the image as flat vector shapes |
| `edit` | Existing SVG plus changes | The same SVG with only those changes and their necessary side effects |
| `animate` | Existing SVG plus a motion request | The same SVG with CSS animation on its groups |

Requests that mix modes ("vectorize, then animate") run in order.

Asset type sets the defaults. Use the row that fits; the request overrides it.

| Asset type | Typical viewBox | Background | Margin | Colors | Text |
| --- | --- | --- | --- | --- | --- |
| UI icon | `0 0 24 24` | none | path coordinates within 2–22 (a 2 px stroke may ink to 1) | 1 (`currentColor`) | never |
| Logo or mark | `0 0 256 256` | none | 8% | 1–3 | only if asked |
| Badge, sticker, app tile | `0 0 512 512` | the badge or tile shape itself fills the viewBox | content 8% inside the shape | 3–6 | if asked |
| Illustration or scene | `0 0 W H` of the target | full bleed; shapes may run past the edge | none for background, 4% for subject | 6–16 | if asked |

A color's shade and highlight tones and its gradient stops count as that one color.

## 2. Brief

Restate the request before drawing. Small assets (icons, marks) need only
the first three lines.

```text
Subject and asset type:  what is drawn, which row of the table
Use and size:            where it is shown, display size, viewBox
Identity cues:           3–5 features that make the subject recognizable at a glance
Style and palette:       flat | outline | duotone | ...; hex colors named by role
Composition:             layout, focal point, proportions
Must include / avoid:    required elements and exact text; what must not appear
```

**Identity cues** are the most important line. Write what a viewer needs to
see to name the subject instantly: for a fox, "pointed snout, tall
triangular ears, white chest and cheeks, large bushy tail with a white tip";
for a lighthouse, "tall white tower, dark lantern room with a railing".
Every cue must be visible in the final drawing.

For `reference` mode, give **each reference one role** (`ref 1 → palette`,
`ref 2 → silhouette`) and state what to preserve and what to change. A
palette role means: take 3–8 colors from the reference; if a needed color
is missing (e.g. water), derive it from the reference colors (mix or shift
lightness) and say so. If you cannot see images, ask for a description.

Fill unknowns with the table defaults. Ask a question only if the subject
itself is unclear.

## 3. Plan

Think it through before writing code (in your reasoning or in a draft; it
does not need to appear in the final answer):

1. **Grid and proportions.** Name key coordinates as whole numbers: center,
   baseline, horizon, the subject's bounding box. For `vectorize` and
   `reference` silhouettes, measure the source as fractions of width and
   height (e.g. horizon at 0.62 H, tower from 0.43 W to 0.52 W) and convert.
2. **Layers, back to front.** List groups with kebab-case ids
   (`background`, `hills`, `body`, `head`, `text`). Anything that may later
   move or change gets its own group.
3. **Shape per part.** Primitives first: `rect` (with `rx`), `circle`,
   `ellipse`, `line`, `polyline`, `polygon`, `text`. Use `path` for organic
   outlines, with smooth `C`/`Q`/`A` segments, not dozens of short `L` steps.
   See the recipes in section 6.
4. **Palette mapping.** Which part gets which color.
5. **Light.** For scenes, objects, and characters, pick one light direction
   (e.g. "light from upper left") and note which side of each mass is in
   shadow.

## 4. Draw

**Root**

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"
     width="512" height="512" role="img" aria-labelledby="title">
  <title id="title">Short description</title>
  ...
</svg>
```

- Always a `viewBox`; `width`/`height` at the display size. Everything
  visible stays inside the viewBox, except backgrounds and scene shapes,
  which may run past the edge and get clipped.
- Colors: either a `<style>` block with classes (preferred when a color is
  used by 3+ shapes) or `fill`/`stroke` attributes. Not many inline
  `style=""` strings.
- `<defs>` for gradients, masks, and clip paths; a clip path used once is
  fine (e.g. clipping a scene to a rounded tile). Ids unique and descriptive.

**Geometry**

- Fewest nodes that hold the shape. A circle is a `<circle>`. One organic
  outline rarely needs more than 12 segments.
- Coordinates: at most one decimal; integers for icons where possible.
- Closed shapes end with `Z`. No zero-length segments, no duplicate points,
  no shapes fully hidden under others.
- Symmetry: compute mirrored coordinates exactly (x' = W − x) or mirror a
  group with `transform="matrix(-1 0 0 1 W 0)"`.
- Draw back to front and overlap neighbors slightly so no hairline gaps show.
  Do not cut holes through one layer while leaving the layers below
  unchanged; draw the hole's content on top instead.

**Volume.** Flat does not mean shapeless. Give every major mass a base
tone plus a shadow shape on the side away from the light, and a highlight
where it helps: clouds get grey-blue undersides and shaded folds, rocks a
lit top face and a dark side, glazed or metal objects a core shadow and a
crisp specular highlight. Shadows are flat shapes, not blurs.

**Natural textures** (clouds, rocks, foliage, waves, fur): irregular shapes
that differ in size and outline, never one shape repeated in a row or a
tiled wave or scallop band.

- Small area: 3–9 shapes. Large field (more than a quarter of the image):
  15–40 shapes, larger in front, smaller toward the horizon, overlapping.
- Generating coordinates with a script is fine if the shapes vary and sit
  in one named group.
- Wrong: one path of identical bumps, `M0 80 q20 -20 40 0 q20 -20 40 0 q20 -20 40 0 ...`.
  Right: 4 separate cloud masses of different widths, each with its own
  shadow shape.

**Style**

- Outline icons: one stroke width (24 px: 2), `stroke-linecap="round"`,
  `stroke-linejoin="round"`, `fill="none"` on the root. Inner lines must
  not cross outlines they should stop at: a camera's top bump is one
  outline with the body, not a separate box drawn across it.
- Flat art: solid fills, at most 2 gradients, no filters unless asked.
  Shadows are flat darker shapes.
- Text: only when asked, exact wording and case, `font-family="system-ui,
  sans-serif"` (or a generic `serif`/`monospace` that matches the source),
  `text-anchor="middle"` for centered text, legible at display size. To fit a
  line to a measured width, set `textLength` and
  `lengthAdjust="spacingAndGlyphs"`; use `letter-spacing` for spaced
  capitals.

**Forbidden**

`<script>`, `on*=` event attributes, `<foreignObject>`, external
`href`/`xlink:href` URLs, embedded raster `<image>` (unless asked), editor
metadata (`sodipodi`, `inkscape`, timestamp comments).

## 5. Mode rules

**vectorize**

- Keep the composition: measured proportions from the plan, same horizon,
  same subject position and size.
- Colors: 6–16 for a scene. Average a small patch when you can read pixels
  (e.g. `magick img.jpg -crop 16x16+X+Y -resize 1x1 txt:`); otherwise
  estimate carefully. Keep the photo's most saturated region (e.g. blue sky)
  visibly saturated.
- Plan color bands top to bottom with their y ranges before drawing.
- Drop noise and texture below about 1/60 of the width. One group per
  region of meaning (`sky`, `clouds`, `sea`, `trees`, `lighthouse`, `rocks`).

**Reference types** (for `vectorize` and `reference`). First name the
type, then keep the traits that make it that type:

| Type | Keep | Simplify or drop |
| --- | --- | --- |
| Photo (landscape, animal, person) | composition, silhouettes, light and shadow masses | texture, noise, small detail |
| Product photo | exact silhouette and proportions, perspective of ellipses (rims, lids), material: core shadow, highlights, reflections | backdrop (unless asked), dust, tiny reflections |
| Painting or print (woodblock, watercolor, ...) | palette, outline color and weight, how forms are stylized (wave claws, foam dots, cloud bands), paper tone | brush noise, paper grain |
| Poster or flat graphic | the ink colors, hard edges, the layout grid, all text (wording, case, weight, placement) | print wear, misregistration |
| Scientific or botanical plate | accurate shapes (leaf outline, vein pattern), fine dark outlines, natural colors, cross-sections | the plate layout and labels unless asked |
| Sketch or line art | the gesture and line hierarchy (thick contours, thin details), closed shapes for fills | stray construction lines, smudges |

When a reference has a style role, write 3–5 style traits into the brief
(e.g. "Prussian blue and indigo, cream paper, dark blue outlines, foam as
white dots, wave crests as claws") and check each one at the end.

**edit**

- **Never modify the input file.** Copy it to the output path first and edit
  the copy (or write a new file).
- Make the requested changes. Also make the changes they force (text color
  for contrast on a new background, the `<title>`, classes that became
  unused, a renamed id for a replaced part such as `sun` → `moon`) and
  report each one.
- Everything else stays as it was: element order, ids, coordinates,
  viewBox, styles.
- To move a group, add or adjust a `transform="translate(dx dy)"` on the
  group rather than rewriting every coordinate. Anything added to a moved
  part goes inside the same group.
- After the change, look for new problems it caused: an added part hidden
  by existing layers, or a moved part now overlapping something. Fix them
  with the smallest change (place the addition above the part hiding it,
  enlarge it, or shift it a little) and report it.

**animate**

- Animate the existing groups. If a moving part has no group of its own,
  wrap it in `<g id="...">` without changing its coordinates.
- CSS `@keyframes` inside the SVG's `<style>`. Animate `transform` and
  `opacity`; `stroke-dashoffset` only for line-drawing effects.
- **Pivot.** When the pivot is a known point (hub, hinge, pole), use
  `transform-box: view-box; transform-origin: Xpx Ypx;` with that point in
  viewBox units. Use `transform-box: fill-box` only when the pivot is the
  exact center of the group's bounding box.
- **Anchored scale or skew** (a flag at its pole): pivot at the anchored
  edge, same rule.
- **First frame equals the input.** The 0% keyframe is the rest pose (0°,
  0 px, scale 1). "Moves 10 px and back" means 0 → 10 → 0. A stated
  duration is one full cycle (out and back) unless the request says
  otherwise.
- Seamless loops: the last keyframe equals the first, or use
  `animation-direction: alternate`.
- Phase offsets: use a negative `animation-delay` (half a cycle =
  `-duration/2`) only if the request allows the first frame to differ.
  Otherwise use a positive delay: the part rests until the delay ends, then
  stays out of phase. Say so in the report.
- Add `@media (prefers-reduced-motion: reduce) { * { animation: none; } }`.
- State your interpretation of any ambiguous amount in the report.

## 6. Recipes

- **Dot in a stroke icon:** a filled circle, `r` = stroke width / 2 to
  stroke width, `fill="currentColor" stroke="none"`.
- **Crescent:** one path, two arcs between the intersection points of an
  outer and an inner circle. Outer (50, 50) r 30, inner (62, 42) r 26:
  `M48 20.1 A30 30 0 1 0 76.9 63.3 A26 26 0 0 1 48 20.1 Z`. Scale and move
  it with a group transform. Alternative: a `<mask>` with a black inner circle.
- **Four-point star:** `polygon` with 8 points alternating outer radius R
  and inner radius 0.35 R, starting at the top.
- **Cloud:** a rounded `rect` base (`rx` = height / 2) plus 2–3 circles of
  different radii on top, all the same fill.
- **Text inside a circle** of radius r: a straight line at distance d from
  the center has room for width 2·√(r² − d²); keep text under 80% of that.
- **Rounded tile:** `rect` with `rx` ≈ 22% of the side; clip the scene to it
  with a `clipPath`.
- **Rotations:** for parts arranged around a center (blades, rays, petals),
  draw one part pointing up and repeat it with `transform="rotate(A cx cy)"`.

## 7. Check

Check the SVG, fix, and check again; at most two repair rounds. If a
problem remains, deliver anyway and name it in the report.

1. **Valid**: well-formed XML, `xmlns`, `viewBox`, unique ids, nothing forbidden.
2. **Frame**: every shape inside the viewBox and margins.
3. **Identity**: every identity cue is visible; the silhouette alone names
   the subject.
4. **Geometry**: grid-aligned, symmetric where intended, no stray, hidden,
   or crossing lines, no gaps, no repeated-pattern textures.
5. **Adherence**: every must-include present, every avoid absent, palette
   and composition as briefed; for `vectorize` and `reference`, compare
   proportions with the source.
6. **Legibility at display size**: details under about 1/24 of the viewBox
   removed or merged; text readable; foreground contrasts with background.
7. **Structure**: named groups, primitives where possible, nothing a
   designer would have to clean up.
8. **Edit / animate**: input untouched; only requested and reported changes;
   first frame equals the input; pivots correct.

With tools, verify rather than guess:

- Validate: `xmllint --noout file.svg` or any XML parser.
- Render: `rsvg-convert -w 512 file.svg -o file.png` (or `magick`, or a
  headless browser) and **look at the PNG** if you can view images. Render
  icons also at display size, then enlarge that render to judge it.
- Compare with the source: render at the source's size and put both side
  by side in one image (e.g. `magick source.jpg render.png +append
  compare.png`), then check proportions, masses, and colors item by item.
- Motion: a static renderer shows only frame 0. In a headless browser,
  inline the SVG in an HTML page and seek every animation with
  `for (const a of document.getAnimations()) { a.pause(); a.currentTime = 2000; }`,
  then screenshot 2–3 moments. (Overriding `animation-delay` instead works
  only if you subtract T from each element's own delay.) Without a browser,
  trace each keyframe's transform by hand for one point of each moving group.
  Test on a copy; the delivered file keeps its real timing.

Without tools, check each item by reading the code, coordinates against the
viewBox first.

## 8. Deliver

- Save to the path the user gave, else to a descriptive kebab-case name
  (`camera-outline-icon.svg`). Without file tools, output the SVG in one
  fenced `svg` block. One final SVG per asset, no drafts.
- Then the report, at most 8 lines:

```text
file:     path (or "inline")
type:     mode, asset type, viewBox
assumed:  defaults or interpretations you chose; derived colors
groups:   ids of the top-level groups
changes:  edit/animate only: each change, including forced side effects
checks:   rendered yes/no, viewed yes/no, repair rounds N, open issues or "none"
```

## 9. Example

Request: "a 24 px outline icon of a cloud with an upload arrow".

```text
Subject and asset type: cloud with upward arrow, UI icon
Use and size: toolbar, 24 px, viewBox 0 0 24 24
Identity cues: cloud with bumpy top and flat bottom; arrow up through its middle
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
