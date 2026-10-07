#!/usr/bin/env python3
"""Generate a markdown inventory of a Drupal site from its config sync directory.

Usage:
  python3 drupal_config_inventory.py <config_dir> <output.md> [--repo <repo_dir>]

Output is a Level-3 reference file (full detail) for a Project Brain. It is
derived data: regenerate it rather than editing it by hand. Never prints
secret values (keys, passwords, tokens).
Requires PyYAML (pip install pyyaml).
"""
import collections
import datetime
import glob
import os
import subprocess
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml")

args = sys.argv[1:]
repo = None
if "--repo" in args:
    i = args.index("--repo"); repo = args[i + 1]; del args[i:i + 2]
if len(args) != 2:
    sys.exit(__doc__)
CFG, OUT = args


def load(name):
    p = os.path.join(CFG, name + ".yml")
    return yaml.safe_load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def each(prefix):
    for p in sorted(glob.glob(os.path.join(CFG, prefix + "*.yml"))):
        yield yaml.safe_load(open(p, encoding="utf-8"))


def clean(s, n=200):
    s = " ".join(str(s or "").split())
    return (s[: n - 1] + "…") if len(s) > n else s


out = []
w = out.append

commit = ""
if repo:
    try:
        commit = subprocess.check_output(
            ["git", "-C", repo, "log", "-1", "--format=%h %ad", "--date=short"], text=True).strip()
    except Exception:
        pass

w("# Drupal config inventory\n")
w(f"Generated {datetime.date.today()} from `{CFG}`" + (f" at commit {commit}" if commit else "") + ".")
w("Derived file: regenerate with `.ai/general/scripts/drupal_config_inventory.py`; don't edit by hand.")
w("Fields: `Label (machine_name: type -> targets)`, `*` = required. `field_` prefixes omitted.\n")

# Site + modules
site = load("system.site") or {}
ext = load("core.extension") or {}
theme = load("system.theme") or {}
w("## Site\n")
w(f"- Name: {site.get('name', '')}")
w(f"- Default theme: {theme.get('default', '')}; admin theme: {theme.get('admin', '')}")
w(f"- Installed themes: {', '.join(sorted((ext.get('theme') or {}).keys()))}")
mods = sorted((ext.get("module") or {}).keys())
w(f"- Enabled modules ({len(mods)}): {', '.join(mods)}\n")
ci = load("config_ignore.settings")
if ci:
    w("Config ignored (managed per environment, may differ in production): " +
      ", ".join(f"`{x}`" for x in ci.get("ignored_config_entities", [])) + "\n")

# Fields by bundle
fields = collections.defaultdict(list)
for d in each("field.field."):
    s = d.get("settings") or {}
    tgt = ""
    if d["field_type"] in ("entity_reference", "entity_reference_revisions"):
        tb = ((s.get("handler_settings") or {}).get("target_bundles") or {})
        tgt = " -> " + (", ".join(tb.keys()) if tb else str(s.get("handler", "")))
    req = "*" if d.get("required") else ""
    fields[(d["entity_type"], d["bundle"])].append(
        f"{d['label']} ({d['field_name'].replace('field_', '')}: {d['field_type']}{tgt}){req}")

BUNDLES = [
    ("Content types (node)", "node", "node.type.", "type", "name"),
    ("Paragraph types", "paragraph", "paragraphs.paragraphs_type.", "id", "label"),
    ("Microcontent types", "microcontent", "microcontent.type.", "id", "label"),
    ("Media types", "media", "media.type.", "id", "label"),
    ("Taxonomy vocabularies", "taxonomy_term", "taxonomy.vocabulary.", "vid", "name"),
    ("Block content types", "block_content", "block_content.type.", "id", "label"),
]
for title, et, prefix, idk, labk in BUNDLES:
    items = list(each(prefix))
    if not items:
        continue
    w(f"## {title} ({len(items)})\n")
    for d in items:
        b = d.get(idk)
        desc = clean(d.get("description"))
        w(f"### {d.get(labk) or b} (`{b}`)")
        if desc:
            w(desc)
        fl = fields.get((et, b), [])
        w("- " + "\n- ".join(fl) if fl else "- (no fields)")
        w("")

# Views
w("## Views\n")
w("| id | label | base | enabled | displays (type:id @path) |")
w("|---|---|---|---|---|")
for d in each("views.view."):
    ds = []
    for k, v in d["display"].items():
        o = v.get("display_options") or {}
        ds.append(f"{v['display_plugin']}:{k}" + (f" @/{o['path']}" if o.get("path") else ""))
    w(f"| {d['id']} | {d['label']} | {d.get('base_table')} | {d.get('status')} | {'; '.join(ds)} |")
w("")

# Webforms
w("## Webforms (exported)\n")
for d in each("webform.webform."):
    hs = [h.get("id") for h in (d.get("handlers") or {}).values()]
    w(f"- `{d['id']}` {d['title']} ({d.get('status')}); handlers: {', '.join(hs) or 'none'}")
w("")

# Roles
w("## Roles\n")
for d in each("user.role."):
    extra = " (admin)" if d.get("is_admin") else ""
    w(f"- `{d['id']}` {d['label']}: {len(d.get('permissions') or [])} permissions{extra}")
w("")

# Menus, path patterns, blocks, formats, image styles
w("## Menus\n")
w(", ".join(f"{d['label']} (`{d['id']}`)" for d in each("system.menu.")) + "\n")
w("## URL alias patterns (Pathauto)\n")
for d in each("pathauto.pattern."):
    w(f"- `{d['id']}`: {d['pattern']}")
w("")
w("## Block placement (default theme)\n")
by_region = collections.defaultdict(list)
for d in each("block.block."):
    if d.get("theme") == theme.get("default"):
        by_region[d.get("region")].append(f"{d['id']} ({d['plugin']}{'' if d.get('status') else ', disabled'})")
for r, bl in sorted(by_region.items()):
    w(f"- **{r}**: {'; '.join(bl)}")
w("")
w("## Text formats\n")
w(", ".join(f"{d['name']} (`{d['format']}`)" for d in each("filter.format.")) + "\n")
w("## Image styles\n")
w(", ".join(f"`{d['name']}`" for d in each("image.style.")) + "\n")
w("## Keys (names only)\n")
for d in each("key.key."):
    w(f"- `{d['id']}` {d.get('label', '')} (provider: {d.get('key_provider')})")
w("")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
print(f"Wrote {OUT} ({len(out)} lines)")
