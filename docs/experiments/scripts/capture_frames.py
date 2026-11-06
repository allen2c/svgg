#!/usr/bin/env python3
"""Capture frames of an animated SVG at chosen times with headless Chrome.

Usage:
    python3 -I docs/experiments/scripts/capture_frames.py FILE.svg [T1 T2 ...] [--out DIR]

Times are seconds (default 0 1 2 3 4). The SVG is inlined into an HTML page
whose script pauses every animation and seeks it to time T (delays included),
so positive and negative delays behave as in a real page. Writes
<stem>-t<T>.png per time and <stem>-frames.png (all frames in a row) to DIR
(default: next to the SVG). Requires Google Chrome; set CHROME to override.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")


def main():
    args = sys.argv[1:]
    out = None
    if "--out" in args:
        i = args.index("--out")
        out = Path(args[i + 1])
        args = args[:i] + args[i + 2:]
    svg_path = Path(args[0])
    times = [float(t) for t in args[1:]] or [0, 1, 2, 3, 4]
    out = out or svg_path.parent
    out.mkdir(parents=True, exist_ok=True)
    svg = svg_path.read_text()
    root = ET.fromstring(svg)
    width = int(float(root.get("width") or root.get("viewBox").split()[2]))
    height = int(float(root.get("height") or root.get("viewBox").split()[3]))
    frames = []
    with tempfile.TemporaryDirectory() as work:
        for t in times:
            html = Path(work) / f"frame-{t}.html"
            html.write_text(
                "<!doctype html><html><head><style>html,body{margin:0;background:#fff}"
                "svg{display:block}</style></head><body>" + svg +
                "<script>for (const a of document.getAnimations()) { a.pause(); a.currentTime = "
                f"{t * 1000}; }}</script></body></html>")
            png = out / f"{svg_path.stem}-t{t:g}.png"
            subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
                            f"--window-size={width},{height}", "--virtual-time-budget=500",
                            f"--screenshot={png}", html.as_uri()],
                           capture_output=True, timeout=60)
            if png.exists():
                frames.append(png)
    if frames and shutil.which("magick"):
        args = ["magick", "montage"]
        for png in frames:
            args += ["-label", png.stem.rsplit("-t", 1)[1] + " s", str(png)]
        args += ["-tile", f"{len(frames)}x1", "-geometry", "+6+6", str(out / f"{svg_path.stem}-frames.png")]
        subprocess.run(args, capture_output=True)
    print("\n".join(str(f) for f in frames))


if __name__ == "__main__":
    main()
