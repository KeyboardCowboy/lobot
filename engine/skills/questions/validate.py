#!/usr/bin/env python3
"""Validate a Project Brain questions log (docs/questions.md).

Usage: python3 validate.py [path/to/questions.md]

Checks the frontmatter and the questions table: IDs (Q-###, unique), scope,
raised date, status (open | answered), and that answered questions have an
answer. Open questions should come before answered ones.
Exit code 0 = valid (warnings may print), 1 = errors found.
"""
import datetime
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml")

HEADER = ["ID", "Question", "Scope", "Raised", "Source", "Status", "Answer"]
ID_RE = re.compile(r"^Q-\d{3,}$")
SCOPE_RE = re.compile(r"^(all|[a-z0-9]+(-[a-z0-9]+)*)$")
STATUSES = ("open", "answered")


def cells(line):
    line = line.strip()
    if not (line.startswith("|") and line.endswith("|")):
        return None
    return [c.strip() for c in line[1:-1].split("|")]


def is_date(value):
    try:
        datetime.date.fromisoformat(value)
        return True
    except ValueError:
        return False


def main(path):
    errors, warnings = [], []
    try:
        text = open(path, encoding="utf-8").read()
    except OSError as e:
        print(f"ERROR: {e}")
        return 1
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        errors.append("missing frontmatter (title, status, updated)")
        body = text
    else:
        body = text[m.end():]
        try:
            fm = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError as e:
            fm = {}
            errors.append(f"frontmatter does not parse: {e}")
        for field in ("title", "status", "updated"):
            if field not in fm:
                errors.append(f"frontmatter missing '{field}'")
        if "updated" in fm and not is_date(str(fm["updated"])):
            errors.append("frontmatter 'updated' must be a date (YYYY-MM-DD)")

    lines = body.splitlines()
    start = next((i for i, l in enumerate(lines) if cells(l) == HEADER), None)
    if start is None:
        errors.append("no questions table with header: | " + " | ".join(HEADER) + " |")
        rows = []
    else:
        rows = []
        for n, line in enumerate(lines[start + 2:], start + 3):
            c = cells(line)
            if c is None:
                break
            rows.append((n, c))

    seen, answered_seen, open_count = set(), False, 0
    for n, c in rows:
        where = f"[row {c[0] if c else '?'}]"
        if len(c) != len(HEADER):
            errors.append(f"{where} has {len(c)} cells, expected {len(HEADER)} (a '|' inside a cell breaks the table)")
            continue
        qid, question, scope, raised, source, status, answer = c
        if not ID_RE.match(qid):
            errors.append(f"{where} ID must look like Q-001")
        elif qid in seen:
            errors.append(f"{where} duplicate ID")
        seen.add(qid)
        if not question:
            errors.append(f"{where} question is empty")
        if not SCOPE_RE.match(scope):
            errors.append(f"{where} scope must be 'all' or a lowercase scope key")
        if not is_date(raised):
            errors.append(f"{where} raised must be a date (YYYY-MM-DD)")
        if not source:
            warnings.append(f"{where} no source: say where the question came from")
        if status not in STATUSES:
            errors.append(f"{where} status must be one of: {', '.join(STATUSES)}")
        elif status == "answered":
            answered_seen = True
            if not answer:
                errors.append(f"{where} answered but the answer is empty")
        else:
            open_count += 1
            if answered_seen:
                warnings.append(f"{where} open question listed after an answered one (open first)")

    for w in warnings:
        print(f"WARN:  {w}")
    for e in errors:
        print(f"ERROR: {e}")
    if errors:
        print(f"{len(errors)} error(s) in {path}")
        return 1
    print(f"OK: {len(rows)} questions, {open_count} open, {len(warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "docs/questions.md"))
