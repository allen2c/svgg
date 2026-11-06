#!/usr/bin/env python3
"""Local drag-to-rank page for one iteration's SVG outputs.

Usage:
    python3 -I docs/experiments/scripts/rank_server.py RUN_DIR [--port 8765]

Open http://127.0.0.1:8765/ . Each task row shows the source (photo,
reference, input SVG, or the prompt text) and every model's output. Drag the
outputs into order, best on the left. Every change is saved to
RUN_DIR/ranking.json (and reloaded on the next start), so the page can be
closed and reopened at any time. Each task is saved as
{"status": "ranked" | "tie" | "unranked", "order": [...]}; only tasks
you dragged become "ranked", and "tie" marks outputs you cannot tell apart. Model names are hidden and unranked
outputs start in random order, so the ranking is blind.
"""
import json
import random
import re
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TASKS_DIR = REPO / "docs/experiments/tasks"
SOURCE_PATTERN = re.compile(r"@@REPO@@/(\S+?\.(?:jpg|jpeg|png|webp|svg))")  # inputs named in a task prompt

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>SVG Ranking</title>
<style>
:root{--bg:#f4f4f2;--card:#fff;--ink:#222;--muted:#777;--line:#ddd;--accent:#2a6df4}
body{margin:0;font:14px system-ui,sans-serif;background:var(--bg);color:var(--ink)}
header{position:sticky;top:0;background:var(--bg);padding:10px 16px;border-bottom:1px solid var(--line);display:flex;gap:16px;align-items:center;z-index:2}
header b{font-size:16px} #status{color:var(--muted)}
section{padding:12px 16px;border-bottom:1px solid var(--line)}
h2{font-size:15px;margin:0 0 4px} .prompt{color:var(--muted);margin:0 0 8px;max-width:1100px}
.row{display:flex;gap:12px;align-items:flex-start;overflow-x:auto;padding-bottom:6px}
.source{flex:0 0 260px} .source img{width:260px;border:2px dashed var(--line);background:#fff}
.source .text{width:240px;padding:10px;border:2px dashed var(--line);background:#fff;font-size:12px}
.list{display:flex;gap:12px;min-height:200px}
.item{flex:0 0 260px;background:var(--card);border:2px solid var(--line);border-radius:8px;padding:6px;cursor:grab;user-select:none}
.item.dragging{opacity:.4} .item img{width:100%;height:240px;object-fit:contain;pointer-events:none;background:repeating-conic-gradient(#eee 0 25%,#fff 0 50%) 0/16px 16px}
.item .meta{display:flex;justify-content:space-between;font-size:12px;margin-top:4px}
.rank{font-weight:700;color:var(--accent)} .name{color:var(--muted)} .blind .name{visibility:hidden}
.item.missing{opacity:.5} .tie{font-weight:400;font-size:13px;margin-left:12px;color:var(--muted)} .state{font-size:12px;margin-left:8px;color:var(--accent)}
</style></head><body>
<header><b>SVG Ranking</b><span>Drag outputs: best on the left.</span>
<label><input type="checkbox" id="show"> show model names</label><span id="status"></span></header>
<main id="main" class="blind"></main>
<script>
const data = __DATA__;
const main = document.getElementById('main'), status = document.getElementById('status');
document.getElementById('show').onchange = e => main.classList.toggle('blind', !e.target.checked);
const state = {};  // task -> 'ranked' | 'tie' | 'unranked'
for (const t of data.tasks) state[t.task] = t.status;
function save(){
  const ranking = {};
  document.querySelectorAll('.list').forEach(l => ranking[l.dataset.task] = {status: state[l.dataset.task], order: [...l.children].map(c => c.dataset.model)});
  document.querySelectorAll('.state').forEach(e => e.textContent = state[e.dataset.task]);
  fetch('/ranking', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(ranking)})
    .then(r => status.textContent = r.ok ? 'saved ' + new Date().toLocaleTimeString() : 'save failed')
    .catch(() => status.textContent = 'save failed');
  renumber();
}
function renumber(){ document.querySelectorAll('.list').forEach(l => [...l.children].forEach((c,i) => c.querySelector('.rank').textContent = '#' + (i+1))); }
let dragged = null;
for (const t of data.tasks) {
  const s = document.createElement('section');
  s.innerHTML = `<h2>${t.task}<span class="state" data-task="${t.task}">${t.status}</span><label class="tie"><input type="checkbox" ${t.status==='tie'?'checked':''}> indistinguishable (tie)</label></h2><p class="prompt"></p><div class="row"><div class="source"></div><div class="list" data-task="${t.task}"></div></div>`;
  s.querySelector('.prompt').textContent = t.prompt;
  const src = s.querySelector('.source');
  src.innerHTML = t.sources.length ? t.sources.map((p, i) => `<img src="/file/${p}" title="reference ${i + 1}" style="margin-bottom:6px">`).join('') : `<div class="text">No source image (create task).</div>`;
  const list = s.querySelector('.list');
  s.querySelector('.tie input').onchange = e => { state[t.task] = e.target.checked ? 'tie' : 'unranked'; save(); };
  for (const m of t.models) {
    const d = document.createElement('div');
    d.className = 'item' + (m.svg ? '' : ' missing'); d.draggable = true; d.dataset.model = m.model;
    d.innerHTML = (m.svg ? `<img src="/file/${m.svg}?v=${Date.now()}">` : `<div style="height:240px;display:grid;place-items:center">no output</div>`) +
      `<div class="meta"><span class="rank"></span><span class="name">${m.model}</span></div>`;
    d.addEventListener('dragstart', () => { dragged = d; d.classList.add('dragging'); });
    d.addEventListener('dragend', () => { d.classList.remove('dragging'); dragged = null; state[t.task] = 'ranked'; s.querySelector('.tie input').checked = false; save(); });
    list.appendChild(d);
  }
  list.addEventListener('dragover', e => {
    e.preventDefault(); if (!dragged || dragged.parentNode !== list) return;
    const after = [...list.children].find(c => c !== dragged && e.clientX < c.getBoundingClientRect().left + c.offsetWidth / 2);
    after ? list.insertBefore(dragged, after) : list.appendChild(dragged);
  });
  main.appendChild(s);
}
renumber();
</script></body></html>"""


def build_data(run_dir):
    ranking_file = run_dir / "ranking.json"
    saved = json.loads(ranking_file.read_text()) if ranking_file.exists() else {}
    models = sorted(p.name for p in run_dir.iterdir() if p.is_dir())
    tasks = []
    task_files = sorted(TASKS_DIR.glob("*.md")) + sorted(TASKS_DIR.glob("retired/*.md"))
    for task_file in task_files:
        task = task_file.stem
        if not any((run_dir / m / f"{task}.svg").exists() for m in models):
            continue  # task not run in this iteration
        text = task_file.read_text()
        prompt = text.split(f"Task ({task}):", 1)[-1].split("Save the final SVG", 1)[0].strip()
        entry = saved.get(task, {})
        if isinstance(entry, list):  # older format: a bare order list
            entry = {"status": "ranked", "order": entry}
        order = [m for m in entry.get("order", []) if m in models]
        rest = [m for m in models if m not in order]
        random.shuffle(rest)  # blind start: unranked outputs come in random order
        order += rest
        entries = []
        for m in order:
            svg = run_dir / m / f"{task}.svg"
            entries.append({"model": m, "svg": str(svg.relative_to(REPO)) if svg.exists() else None})
        tasks.append({"task": task, "prompt": prompt.replace("@@REPO@@/", ""),
                      "sources": list(dict.fromkeys(SOURCE_PATTERN.findall(text))), "models": entries,
                      "status": entry.get("status", "unranked")})
    return {"tasks": tasks}


def main():
    run_dir = Path(sys.argv[1]).resolve()
    port = int(sys.argv[sys.argv.index("--port") + 1]) if "--port" in sys.argv else 8765

    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path in ("/", "/index.html"):
                body = PAGE.replace("__DATA__", json.dumps(build_data(run_dir))).encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(body)
                return
            if self.path.startswith("/file/"):
                target = (REPO / self.path[6:].split("?")[0]).resolve()
                if REPO in target.parents and target.is_file():
                    kind = {".svg": "image/svg+xml", ".jpg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}.get(target.suffix, "application/octet-stream")
                    self.send_response(200)
                    self.send_header("Content-Type", kind)
                    self.send_header("Cache-Control", "no-store")
                    self.end_headers()
                    self.wfile.write(target.read_bytes())
                    return
            self.send_error(404)

        def do_POST(self):
            if self.path != "/ranking":
                return self.send_error(404)
            body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
            (run_dir / "ranking.json").write_text(json.dumps(json.loads(body), indent=2) + "\n")
            self.send_response(204)
            self.end_headers()

        def log_message(self, format, *args):  # quiet server
            pass

    print(f"http://127.0.0.1:{port}/  (saving to {run_dir / 'ranking.json'})")
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
