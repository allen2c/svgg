#!/usr/bin/env python3
"""Static acceptance check for SVG files written by agents following SKILL.md.

Usage:
    python3 -I docs/experiments/scripts/svg_check.py RUN_DIR [--render]

RUN_DIR holds <model>/<task>.svg files. Prints one row per file and writes
RUN_DIR/check.tsv. With --render, also writes <task>.png next to each SVG
(via rsvg-convert) and RUN_DIR/contact-sheet-<task>.png per task.
Re-runnable: it only reads the SVGs and overwrites its own outputs.
"""
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SVG_NS = "{http://www.w3.org/2000/svg}"
PRIMITIVES = {"rect", "circle", "ellipse", "line", "polyline", "polygon", "text"}
FORBIDDEN_TAGS = {"script", "foreignObject", "image"}
EDITOR_MARKERS = ("sodipodi", "inkscape:")


def local(tag):
    return tag.split("}", 1)[-1]


def check(path):
    text = path.read_text(errors="replace")
    row = {"file": f"{path.parent.name}/{path.name}", "bytes": len(text)}
    problems = []
    try:
        root = ET.fromstring(text)
    except ET.ParseError as error:
        row.update(valid="no", problems=f"xml: {error}")
        return row
    if local(root.tag) != "svg" or not root.tag.startswith(SVG_NS):
        problems.append("root not namespaced svg")
    if not root.get("viewBox"):
        problems.append("no viewBox")
    elements = list(root.iter())
    tags = [local(e.tag) for e in elements]
    ids = [e.get("id") for e in elements if e.get("id")]
    if len(ids) != len(set(ids)):
        problems.append("duplicate ids")
    bad = sorted(set(tags) & FORBIDDEN_TAGS)
    if bad:
        problems.append("forbidden " + ",".join(bad))
    if re.search(r"\son[a-z]+\s*=", text):
        problems.append("event attribute")
    if re.search(r'href\s*=\s*"(https?:|//)', text):
        problems.append("external href")
    if any(m in text for m in EDITOR_MARKERS):
        problems.append("editor metadata")
    shapes = [t for t in tags if t in PRIMITIVES or t == "path"]
    path_data = " ".join(e.get("d", "") for e in elements if local(e.tag) == "path")
    commands = len(re.findall(r"[MLHVCSQTAZmlhvcsqtaz]", path_data))
    numbers = re.findall(r"-?\d*\.\d+", text)
    long_decimals = sum(1 for n in numbers if len(n.split(".")[1]) > 2)
    named_groups = sum(1 for e in elements if local(e.tag) == "g" and e.get("id"))
    row.update(
        valid="yes" if not problems else "warn",
        elements=len(elements),
        shapes=len(shapes),
        primitive_share=f"{(len(shapes) - tags.count('path')) / len(shapes):.2f}" if shapes else "-",
        path_commands=commands,
        long_decimals=long_decimals,
        named_groups=named_groups,
        animated="yes" if "@keyframes" in text or "<animate" in text else "no",
        reduced_motion="yes" if "prefers-reduced-motion" in text else "no",
        problems="; ".join(problems) or "-",
    )
    return row


def render(svg):
    png = svg.with_suffix(".png")
    result = subprocess.run(["rsvg-convert", "-w", "512", str(svg), "-o", str(png)],
                            capture_output=True, text=True)
    return png if result.returncode == 0 else None


def main():
    run_dir = Path(sys.argv[1])
    do_render = "--render" in sys.argv
    svgs = sorted(run_dir.glob("*/*.svg"))
    rows = [check(p) for p in svgs]
    columns = ["file", "valid", "bytes", "elements", "shapes", "primitive_share",
               "path_commands", "long_decimals", "named_groups", "animated",
               "reduced_motion", "problems"]
    lines = ["\t".join(columns)] + ["\t".join(str(r.get(c, "")) for c in columns) for r in rows]
    (run_dir / "check.tsv").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    if do_render and shutil.which("rsvg-convert"):
        by_task = {}
        for svg in svgs:
            png = render(svg)
            if png:
                by_task.setdefault(svg.stem, []).append(png)
        if shutil.which("magick"):
            for task, pngs in by_task.items():
                args = ["magick", "montage"]
                for png in pngs:
                    args += ["-label", png.parent.name, str(png)]
                args += ["-tile", f"{len(pngs)}x1", "-geometry", "320x320+8+8",
                         "-background", "#dddddd", str(run_dir / f"contact-sheet-{task}.png")]
                subprocess.run(args, capture_output=True)


if __name__ == "__main__":
    main()
