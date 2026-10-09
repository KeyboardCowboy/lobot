#!/usr/bin/env python3
"""Lobot dashboard: a read-only local view of one Project Brain's records.

Usage (from the Project Brain root, or pass its path):
    python3 .ai/general/skills/dashboard/dashboard.py [PROJECT_DIR] [--port N] [--no-browser]

Serves http://127.0.0.1:<port>/ with one tab per record (overview, questions,
risks, decisions, RACI, kickoff checklists, people, glossary, journal,
meetings). Files are read fresh on every request; nothing is written.

One instance per project. The port is derived from the project's path, so
launching again from the same project finds the running instance, opens it,
and exits instead of starting a second one.

Needs Python 3.8+ and PyYAML (pip install pyyaml). No other dependencies.
"""
import argparse
import hashlib
import html
import json
import os
import re
import sys
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml")

APP = "lobot-dashboard"
BASE_PORT, PORT_RANGE = 8700, 100
HOST = "127.0.0.1"


# ---------------------------------------------------------------- project ---

def find_root(start):
    """Walk up from start to the directory holding .ai/general (a Project Brain)."""
    d = os.path.abspath(start)
    while True:
        if os.path.isdir(os.path.join(d, ".ai", "general")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def project_name(root):
    try:
        with open(os.path.join(root, "CLAUDE.md"), encoding="utf-8") as f:
            for line in f:
                if line.startswith("# "):
                    return re.sub(r"\s+Project Brain\s*$", "", line[2:].strip()) or os.path.basename(root)
    except OSError:
        pass
    return os.path.basename(root)


def read(root, rel):
    try:
        with open(os.path.join(root, rel), encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def mtime(root, rel):
    try:
        return os.path.getmtime(os.path.join(root, rel))
    except OSError:
        return None


def strip_frontmatter(text):
    m = re.match(r"^---\n.*?\n---\n", text or "", re.S)
    return text[m.end():] if m else (text or "")


def load_yaml(root, rel):
    text = read(root, rel)
    if text is None:
        return None
    try:
        return yaml.safe_load(text) or {}
    except yaml.YAMLError as e:
        return {"__error__": str(e)}


def cell(value):
    """Make a value safe for one markdown table cell."""
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        value = ", ".join(str(v) for v in value)
    return str(value).replace("|", "/").replace("\n", " ").strip()


def table(columns, rows):
    out = ["| " + " | ".join(columns) + " |", "|" + "---|" * len(columns)]
    out += ["| " + " | ".join(cell(v) for v in row) + " |" for row in rows]
    return "\n".join(out)


# ------------------------------------------------------------------- tabs ---
# Each tab builder returns markdown (the page renders it) or None if the
# record doesn't exist in this project.

def tab_markdown_file(rel, missing):
    def build(root):
        text = read(root, rel)
        return strip_frontmatter(text) if text is not None else missing
    return build


def tab_decisions(root):
    data = load_yaml(root, "docs/decisions.yaml")
    if data is None:
        return None
    if "__error__" in data:
        return "**decisions.yaml does not parse:** `%s`" % cell(data["__error__"])
    entries = {k: v for k, v in data.items() if isinstance(v, dict)}
    if not entries:
        return "# Decision log\n\nNo decisions logged yet. A decision is logged once a real choice between options has been made, with a driver and an approver."
    rows = [[k, v.get("decision"), v.get("status"), v.get("driver"), v.get("approver"),
             v.get("date") or v.get("created"), v.get("tags")] for k, v in sorted(entries.items())]
    return "# Decision log\n\n" + table(["ID", "Decision", "Status", "Driver", "Approver", "Date", "Tags"], rows)


def tab_raci(root):
    """One table per scope and area: Task | R | A | C | I, with people's names in the cells."""
    data = load_yaml(root, "docs/raci.yaml")
    if data is None:
        return None
    if "__error__" in data:
        return "**raci.yaml does not parse:** `%s`" % cell(data["__error__"])
    people = load_yaml(root, "docs/people.yaml") or {}
    roles = data.get("roles") or {}
    rows = data.get("rows") or {}
    scopes = data.get("scopes") or {}
    scope_keys = list(scopes) or ["all"]

    def person(key):
        if key in (None, "", "tbd"):
            return "TBD"
        entry = people.get(key) if isinstance(people, dict) else None
        name = (entry or {}).get("name") if isinstance(entry, dict) else None
        return name or key

    def who(role_key, scope):
        """Names filling a role in a scope, with the role title, e.g. 'Sam Lee — Technical lead'."""
        role = roles.get(role_key)
        if not isinstance(role, dict):
            return role_key
        filled = role.get("people") or {}
        value = filled.get(scope, filled.get("all")) if isinstance(filled, dict) else filled
        names = [person(v) for v in (value if isinstance(value, list) else [value])]
        return "%s — %s" % (", ".join(names), role.get("title") or role_key)

    def cells(values, scope):
        values = values if isinstance(values, list) else ([values] if values else [])
        return "; ".join(who(v, scope) for v in values)

    out = ["# RACI matrix", "",
           "R = does the work · A = owns the outcome and signs off (one person) · C = consulted before · I = informed after.",
           "Status: %s." % (data.get("status") or "unknown")]
    for scope in scope_keys:
        # Rows that apply here: key@scope replaces key; unscoped rows apply everywhere.
        chosen = {}
        for key, row in rows.items():
            if not isinstance(row, dict):
                continue
            base, _, sc = str(key).partition("@")
            if sc and sc != scope:
                continue
            if sc or base not in chosen:
                chosen[base] = row
        if len(scope_keys) > 1 or scopes:
            out += ["", "## %s" % scopes.get(scope, scope)]
        by_area = {}
        for base, row in chosen.items():
            by_area.setdefault(row.get("area") or "other", []).append(row)
        notes = []
        for area in by_area:  # file order, like the raci skill's --table
            out += ["", "### %s" % area.capitalize(), ""]
            lines = []
            for row in by_area[area]:
                a = cells(row.get("A"), scope)
                if row.get("backup"):
                    a += "; backup: " + cells(row.get("backup"), scope)
                lines.append([row.get("responsibility"), cells(row.get("R"), scope), a,
                              cells(row.get("C"), scope), cells(row.get("I"), scope)])
                role = roles.get(row.get("A")) if isinstance(row.get("A"), str) else None
                if isinstance(role, dict) and role.get("org") == "client" and not row.get("response_window"):
                    notes.append("No response window set for: %s" % row.get("responsibility"))
            out.append(table(["Task", "R", "A", "C", "I"], lines))
        if notes:
            out += ["", "**Open:**", ""] + ["- " + n for n in notes]
    return "\n".join(out)


def tab_people(root):
    data = load_yaml(root, "docs/people.yaml")
    if data is None:
        return None
    if "__error__" in data:
        return "**people.yaml does not parse:** `%s`" % cell(data["__error__"])
    rows = [[v.get("name"), v.get("org"), v.get("role"), v.get("status"), v.get("owns"), v.get("tz")]
            for k, v in sorted(data.items()) if isinstance(v, dict)]
    by_org = {}
    for r in rows:
        by_org.setdefault(r[1] or "Unknown", []).append(r)
    parts = ["# People\n"]
    for org in sorted(by_org):
        parts.append("## %s\n\n%s\n" % (org, table(["Name", "Org", "Role", "Status", "Owns", "Time zone"], by_org[org])))
    return "\n".join(parts)


def tab_glossary(root):
    data = load_yaml(root, "docs/glossary.yaml")
    if data is None:
        return None
    if "__error__" in data:
        return "**glossary.yaml does not parse:** `%s`" % cell(data["__error__"])
    rows = [[v.get("term"), v.get("expands"), v.get("means"), v.get("aka")]
            for k, v in sorted(data.items()) if isinstance(v, dict)]
    return "# Glossary\n\n" + table(["Term", "Expands", "Means", "Also seen as"], rows)


def latest(root, folder):
    try:
        names = sorted(n for n in os.listdir(os.path.join(root, folder)) if n.endswith(".md"))
    except OSError:
        return []
    return names


def tab_journal(root):
    names = latest(root, "docs/journals")
    if not names:
        return None
    return strip_frontmatter(read(root, "docs/journals/" + names[-1]))


def tab_meetings(root):
    names = latest(root, "docs/meetings")
    if not names:
        return None
    links = "\n".join("- [%s](#meeting/%s)" % (n[:-3], n[:-3]) for n in reversed(names))
    return "# Meeting notes\n\n" + links


def tabs(root):
    """Ordered list of (id, label, builder, source file)."""
    t = [
        ("overview", "Overview", tab_markdown_file("docs/overview/index.md", "No overview yet."), "docs/overview/index.md"),
        ("questions", "Questions", tab_markdown_file("docs/questions.md", None), "docs/questions.md"),
        ("risks", "Risks", tab_markdown_file("docs/risks.md", None), "docs/risks.md"),
        ("decisions", "Decisions", tab_decisions, "docs/decisions.yaml"),
        ("raci", "RACI", tab_raci, "docs/raci.yaml"),
    ]
    for name in latest(root, "docs"):
        if name.startswith("kickoff-checklist"):
            scope = name[len("kickoff-checklist"):-3].strip("-")
            label = "Kickoff checklist" + (" (%s)" % scope if scope else "")
            rel = "docs/" + name
            t.append(("checklist-" + (scope or "all"), label, tab_markdown_file(rel, None), rel))
    t += [
        ("people", "People", tab_people, "docs/people.yaml"),
        ("glossary", "Glossary", tab_glossary, "docs/glossary.yaml"),
        ("journal", "Journal", tab_journal, None),
        ("meetings", "Meetings", tab_meetings, None),
    ]
    return [x for x in t if x[3] is None or os.path.exists(os.path.join(root, x[3]))]


# ----------------------------------------------------------------- server ---

PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
:root{--bg:#f6f7f9;--surface:#fff;--fg:#1d2430;--muted:#5d6878;--line:#dde1e8;--accent:#1f5f8b;--accent-soft:#e3eef6;
--ok:#1d7a46;--ok-bg:#e1f3e8;--warn:#9a5b00;--warn-bg:#fdf0db;--bad:#a33a2b;--bad-bg:#fbe6e2;--na:#7b8290;--na-bg:#f0f1f3;
--f:system-ui,-apple-system,"Segoe UI",sans-serif;--m:ui-monospace,SFMono-Regular,Menlo,monospace}
@media (prefers-color-scheme:dark){:root{--bg:#12161c;--surface:#1a2028;--fg:#e4e8ee;--muted:#9aa4b2;--line:#2c3440;--accent:#7cb4dc;--accent-soft:#1c2c3a;
--ok:#6fcf97;--ok-bg:#183025;--warn:#f0b45a;--warn-bg:#33281a;--bad:#f08b7a;--bad-bg:#3a201c;--na:#8a919c;--na-bg:#222830;color-scheme:dark}}
*{box-sizing:border-box}html,body{height:100%}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 var(--f);display:grid;grid-template-columns:220px 1fr;grid-template-rows:auto 1fr}
header{grid-column:1/-1;display:flex;align-items:baseline;gap:12px;padding:14px 20px;border-bottom:1px solid var(--line);background:var(--surface)}
header h1{font-size:18px;margin:0}header .meta{color:var(--muted);font-size:13px}
nav{border-right:1px solid var(--line);padding:12px 8px;overflow:auto}
nav a{display:block;padding:7px 12px;border-radius:6px;color:var(--fg);text-decoration:none;font-size:14px}
nav a:hover{background:var(--accent-soft)}nav a[aria-current="page"]{background:var(--accent);color:var(--surface);font-weight:600}
main{overflow:auto;padding:20px 28px 48px;min-width:0}
.doc{max-width:1100px}.src{color:var(--muted);font-size:12px;font-family:var(--m);margin-bottom:8px}
h1,h2,h3{line-height:1.25;text-wrap:balance}main h1{font-size:24px}main h2{font-size:18px;margin-top:28px}main h3{font-size:15px}
a{color:var(--accent)}code{font-family:var(--m);font-size:.92em;background:var(--na-bg);padding:1px 4px;border-radius:4px}
pre{background:var(--na-bg);padding:12px;border-radius:8px;overflow:auto}
blockquote{margin:0;padding:4px 14px;border-left:3px solid var(--line);color:var(--muted)}
.tw{overflow-x:auto;margin:12px 0;border:1px solid var(--line);border-radius:8px;background:var(--surface)}
table{border-collapse:collapse;width:100%;font-size:14px}th,td{text-align:left;vertical-align:top;padding:8px 10px;border-top:1px solid var(--line)}
th{background:var(--bg);font-weight:600;border-top:0;position:sticky;top:0}
.pill{display:inline-block;padding:1px 8px;border-radius:999px;font-size:12px;font-weight:600;white-space:nowrap}
.ok{color:var(--ok);background:var(--ok-bg)}.warn{color:var(--warn);background:var(--warn-bg)}.bad{color:var(--bad);background:var(--bad-bg)}.na{color:var(--na);background:var(--na-bg)}
.err{color:var(--bad)}
@media (max-width:700px){body{grid-template-columns:1fr;grid-template-rows:auto auto 1fr}nav{display:flex;flex-wrap:wrap;border-right:0;border-bottom:1px solid var(--line)}}
</style></head><body>
<header><h1>__TITLE__</h1><span class="meta">Lobot dashboard · read-only · updates as the files change</span></header>
<nav id="nav"></nav>
<main><div class="doc" id="doc">Loading…</div></main>
<script>
const PILLS={open:"warn",answered:"ok","not started":"na","in progress":"warn",done:"ok","not applicable":"na",
 high:"bad",medium:"warn",low:"ok",tbd:"na",closed:"ok",monitoring:"warn",pending:"warn",approved:"ok",denied:"bad",
 superseded:"na",deprecated:"na",active:"ok",draft:"warn"};
const esc=s=>s.replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
function inline(s){
  s=esc(s);
  s=s.replace(/`([^`]+)`/g,"<code>$1</code>").replace(/\*\*([^*]+)\*\*/g,"<strong>$1</strong>")
   .replace(/(^|[^*])\*([^*\s][^*]*)\*/g,"$1<em>$2</em>")
   .replace(/\[([^\]]+)\]\(([^)\s]+)\)/g,(m,t,u)=>{const ext=/^https?:/.test(u);return `<a href="${u}"${ext?' target="_blank" rel="noopener"':""}>${t}</a>`});
  return s;
}
function cellHTML(c){const k=c.trim().toLowerCase();return PILLS[k]?`<span class="pill ${PILLS[k]}">${esc(c.trim())}</span>`:inline(c)}
function md(src){
  const L=src.replace(/\r/g,"").split("\n"),out=[];let i=0;
  const row=l=>l.trim().replace(/^\||\|$/g,"").split("|");
  while(i<L.length){
    let l=L[i];
    if(/^```/.test(l)){const b=[];i++;while(i<L.length&&!/^```/.test(L[i]))b.push(L[i++]);i++;out.push("<pre><code>"+esc(b.join("\n"))+"</code></pre>");continue}
    if(/^\s*\|/.test(l)&&i+1<L.length&&/^\s*\|?\s*:?-{2,}/.test(L[i+1])){
      const h=row(l);i+=2;const rs=[];while(i<L.length&&/^\s*\|/.test(L[i]))rs.push(row(L[i++]));
      out.push('<div class="tw"><table><thead><tr>'+h.map(x=>"<th>"+inline(x.trim())+"</th>").join("")+"</tr></thead><tbody>"+
        rs.map(r=>"<tr>"+r.map(x=>"<td>"+cellHTML(x)+"</td>").join("")+"</tr>").join("")+"</tbody></table></div>");continue}
    const h=l.match(/^(#{1,4})\s+(.*)/);if(h){out.push(`<h${h[1].length}>${inline(h[2])}</h${h[1].length}>`);i++;continue}
    if(/^\s*([-*]|\d+\.)\s+/.test(l)){const ol=/^\s*\d+\./.test(l),it=[];
      while(i<L.length&&/^\s*([-*]|\d+\.)\s+/.test(L[i])){let t=L[i].replace(/^\s*([-*]|\d+\.)\s+/,"");i++;
        while(i<L.length&&/^\s{2,}\S/.test(L[i])&&!/^\s*([-*]|\d+\.)\s+/.test(L[i]))t+=" "+L[i++].trim();it.push("<li>"+inline(t)+"</li>")}
      out.push((ol?"<ol>":"<ul>")+it.join("")+(ol?"</ol>":"</ul>"));continue}
    if(/^>\s?/.test(l)){const b=[];while(i<L.length&&/^>\s?/.test(L[i]))b.push(L[i++].replace(/^>\s?/,""));out.push("<blockquote>"+inline(b.join(" "))+"</blockquote>");continue}
    if(/^-{3,}\s*$/.test(l)){out.push("<hr>");i++;continue}
    if(!l.trim()){i++;continue}
    const p=[];while(i<L.length&&L[i].trim()&&!/^(#{1,4}\s|```|\s*\||\s*([-*]|\d+\.)\s|>)/.test(L[i]))p.push(L[i++]);
    if(!p.length){p.push(L[i++])}out.push("<p>"+inline(p.join(" "))+"</p>");
  }
  return out.join("\n");
}
let TABS=[],current=null,stamp=null;
async function loadTabs(){TABS=(await (await fetch("/api/tabs")).json()).tabs;
  document.getElementById("nav").innerHTML=TABS.map(t=>`<a href="#${t.id}" data-id="${t.id}">${esc(t.label)}</a>`).join("")}
async function show(force){
  const h=decodeURIComponent(location.hash.slice(1))||(TABS[0]&&TABS[0].id);
  const r=await fetch("/api/tab?id="+encodeURIComponent(h));const d=await r.json();
  if(!force&&h===current&&d.stamp===stamp)return;current=h;stamp=d.stamp;
  const top=h.startsWith("meeting/")?"meetings":h;
  document.querySelectorAll("nav a").forEach(a=>{if(a.dataset.id===top)a.setAttribute("aria-current","page");else a.removeAttribute("aria-current")});
  document.getElementById("doc").innerHTML=(d.source?`<div class="src">${esc(d.source)}</div>`:"")+(d.error?`<p class="err">${esc(d.error)}</p>`:md(d.markdown||""));
}
window.addEventListener("hashchange",()=>show(true));
setInterval(()=>{if(!document.hidden)show(false).catch(()=>{})},5000);
loadTabs().then(()=>show(true)).catch(e=>{document.getElementById("doc").textContent="The dashboard server isn't answering. Start it again from the project."});
</script></body></html>"""


def make_handler(root):
    name = project_name(root)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def send(self, code, body, ctype):
            data = body.encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def json(self, obj, code=200):
            self.send(code, json.dumps(obj), "application/json")

        def do_GET(self):
            path, _, query = self.path.partition("?")
            params = dict(p.split("=", 1) for p in query.split("&") if "=" in p)
            if path == "/":
                return self.send(200, PAGE.replace("__TITLE__", html.escape(name)), "text/html; charset=utf-8")
            if path == "/api/health":
                return self.json({"app": APP, "root": root, "project": name})
            if path == "/api/tabs":
                return self.json({"project": name, "tabs": [{"id": t[0], "label": t[1]} for t in tabs(root)]})
            if path == "/api/tab":
                from urllib.parse import unquote
                tid = unquote(params.get("id", ""))
                if tid.startswith("meeting/"):
                    slug = tid.split("/", 1)[1]
                    if slug + ".md" not in latest(root, "docs/meetings"):
                        return self.json({"error": "No such meeting notes."}, 404)
                    rel = "docs/meetings/%s.md" % slug
                    return self.json({"markdown": strip_frontmatter(read(root, rel)), "source": rel, "stamp": mtime(root, rel)})
                for t in tabs(root):
                    if t[0] == tid:
                        try:
                            body = t[2](root)
                        except Exception as e:  # show the problem rather than a blank page
                            return self.json({"error": "Couldn't read this record: %s" % e, "source": t[3]})
                        src = t[3] or {"journal": "docs/journals/", "meetings": "docs/meetings/"}.get(t[0])
                        if t[0] == "journal":
                            names = latest(root, "docs/journals")
                            src = "docs/journals/" + names[-1] if names else src
                        stamp = mtime(root, src) if src and not src.endswith("/") else None
                        if t[0] == "meetings":
                            stamp = len(latest(root, "docs/meetings"))
                        return self.json({"markdown": body or "Nothing here yet.", "source": src, "stamp": stamp})
                return self.json({"error": "Unknown tab."}, 404)
            self.send(404, "Not found", "text/plain")

    return Handler


def port_for(root):
    return BASE_PORT + int(hashlib.sha1(root.encode("utf-8")).hexdigest(), 16) % PORT_RANGE


def probe(port):
    """Return the health payload of a dashboard on this port, or None."""
    try:
        with urllib.request.urlopen("http://%s:%d/api/health" % (HOST, port), timeout=1) as r:
            data = json.loads(r.read().decode("utf-8"))
            return data if data.get("app") == APP else {"app": "other"}
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser(description="Read-only dashboard for one Project Brain.")
    ap.add_argument("project", nargs="?", default=".", help="Project Brain directory (default: current)")
    ap.add_argument("--port", type=int, help="Port to use (default: derived from the project path)")
    ap.add_argument("--no-browser", action="store_true", help="Don't open a browser")
    args = ap.parse_args()

    root = find_root(args.project)
    if not root:
        sys.exit("Not inside a Project Brain (no .ai/general folder found from %s)." % os.path.abspath(args.project))
    root = os.path.realpath(root)

    start = args.port or port_for(root)
    for port in range(start, start + 20):
        found = probe(port)
        if found and found.get("root") == root:
            url = "http://%s:%d/" % (HOST, port)
            print("Already running for %s at %s" % (found.get("project"), url))
            if not args.no_browser:
                webbrowser.open(url)
            return 0
        if found:
            continue  # another project's dashboard, or something else; try the next port
        try:
            server = ThreadingHTTPServer((HOST, port), make_handler(root))
        except OSError:
            continue
        url = "http://%s:%d/" % (HOST, port)
        print("Lobot dashboard for %s at %s (Ctrl+C to stop)" % (project_name(root), url))
        if not args.no_browser:
            webbrowser.open(url)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")
        return 0
    sys.exit("No free port between %d and %d. Pass --port." % (start, start + 19))


if __name__ == "__main__":
    sys.exit(main())
