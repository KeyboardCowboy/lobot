#!/usr/bin/env python3
"""Validate a Project Brain decision log (decisions.yaml) and report on it.

Usage:
  python3 validate.py [path/to/decisions.yaml] [--people path/to/people.yaml]
  python3 validate.py [path/to/decisions.yaml] --pending   # what's waiting on approval
  python3 validate.py [path/to/decisions.yaml] --tags      # tags in use, with counts

The people directory (default: people.yaml next to the decision log) is loaded
so `driver` and `approver` can be checked against its keys.
Exit code 0 = valid (warnings may print), 1 = errors found.
"""
import datetime
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml")

STATUSES = ["pending", "approved", "denied", "superseded", "deprecated"]
REQUIRED = ["decision", "justification", "driver", "created", "status"]
ALLOWED = set(REQUIRED) | {"approver", "date", "tags", "needed_by", "superseded_by"}
KEY_RE = re.compile(r"^D-(\d{3,})$")
TAG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MAX_DECISION_CHARS = 100


class UniqueKeyLoader(yaml.SafeLoader):
    """SafeLoader that errors on duplicate mapping keys instead of overwriting."""


def _construct_mapping(loader, node, deep=False):
    seen = set()
    for key_node, _ in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in seen:
            raise yaml.constructor.ConstructorError(
                None, None, f"duplicate key: {key!r}", key_node.start_mark)
        seen.add(key)
    return loader.construct_mapping(node, deep)


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)


def load(path):
    with open(path, encoding="utf-8") as f:
        return yaml.load(f, Loader=UniqueKeyLoader)


def as_date(value):
    """Return a date for a YAML date or a YYYY-MM-DD string, else None."""
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, str) and DATE_RE.match(value):
        try:
            return datetime.date.fromisoformat(value)
        except ValueError:
            return None
    return None


def validate(data, people, people_path):
    errors, warnings = [], []
    today = datetime.date.today()

    prev = 0
    for key in data:
        m = KEY_RE.match(key) if isinstance(key, str) else None
        if not m:
            errors.append(f"[{key}] key must look like D-001 (D- plus a zero-padded number)")
            continue
        num = int(m.group(1))
        if num <= prev:
            errors.append(f"[{key}] out of order: IDs must ascend through the file")
        elif num != prev + 1:
            warnings.append(f"[{key}] gap in IDs after D-{prev:03d}; entries are never deleted")
        prev = max(prev, num)

    for key, d in data.items():
        where = f"[{key}]"
        if not isinstance(d, dict):
            errors.append(f"{where} entry must be a mapping")
            continue
        for field in REQUIRED:
            if not d.get(field):
                errors.append(f"{where} missing required field '{field}'")
        for field in d:
            if field not in ALLOWED:
                warnings.append(f"{where} unknown field '{field}'")

        for field in ("decision", "justification"):
            if field in d and not isinstance(d[field], str):
                errors.append(f"{where} {field} must be a quoted string")
        just = d.get("justification")
        if isinstance(just, str) and "Source:" not in just:
            warnings.append(f"{where} justification should end with where the decision came from (Source: ...)")
        dec = d.get("decision")
        if isinstance(dec, str):
            if "\n" in dec.strip():
                errors.append(f"{where} decision must be a single line")
            elif len(dec) > MAX_DECISION_CHARS:
                warnings.append(f"{where} decision is {len(dec)} characters; keep it to one short line and move the reasoning to justification")

        status = d.get("status")
        if status and status not in STATUSES:
            errors.append(f"{where} status must be one of: {', '.join(STATUSES)}")
            status = None

        for field in ("driver", "approver"):
            person = d.get(field)
            if person is None:
                continue
            if not isinstance(person, str):
                errors.append(f"{where} {field} must be one people directory key")
            elif people is not None and person not in people:
                errors.append(f"{where} {field} '{person}' is not a key in {people_path}")

        for field in ("date", "created", "needed_by"):
            if field in d and d[field] is not None and as_date(d[field]) is None:
                errors.append(f"{where} {field} must be a date (YYYY-MM-DD)")
        for field in ("date", "created"):
            when = as_date(d.get(field))
            if when and when > today:
                warnings.append(f"{where} {field} is in the future")

        if status == "pending":
            if d.get("date"):
                errors.append(f"{where} pending entries have no date; date is when the decision was approved or denied")
        elif status in ("approved", "denied", "superseded"):
            for field in ("approver", "date"):
                if not d.get(field):
                    errors.append(f"{where} {status} entries need '{field}'")
        if status and status != "pending" and d.get("needed_by"):
            warnings.append(f"{where} needed_by is for pending entries; remove it now the decision is {status}")

        target = d.get("superseded_by")
        if status == "superseded" and not target:
            errors.append(f"{where} superseded entries need 'superseded_by'")
        if target:
            if status and status != "superseded":
                errors.append(f"{where} has superseded_by but status is '{status}'")
            if target == key:
                errors.append(f"{where} cannot supersede itself")
            elif target not in data:
                errors.append(f"{where} superseded_by '{target}' is not an entry in this log")

        tags = d.get("tags")
        if tags is not None:
            if not isinstance(tags, list):
                errors.append(f"{where} tags must be a list")
            else:
                for tag in tags:
                    if not isinstance(tag, str) or not TAG_RE.match(tag):
                        errors.append(f"{where} tag '{tag}' must be lowercase and hyphenated")
    return errors, warnings


def report_pending(data):
    today = datetime.date.today()
    rows = []
    for key, d in data.items():
        if isinstance(d, dict) and d.get("status") == "pending":
            rows.append((as_date(d.get("needed_by")), key, d))
    if not rows:
        print("No pending decisions.")
        return
    rows.sort(key=lambda r: (r[0] is None, r[0] or today, r[1]))
    print(f"{len(rows)} pending decision(s), most urgent first:")
    for needed, key, d in rows:
        if needed is None:
            when = "no needed_by"
        elif needed < today:
            when = f"needed by {needed} OVERDUE"
        else:
            when = f"needed by {needed}"
        waiting_on = d.get("approver") or "no approver named"
        print(f"- {key} | {when} | waiting on: {waiting_on} | driver: {d.get('driver')} | {d.get('decision')}")


def report_tags(data):
    counts = {}
    for d in data.values():
        if isinstance(d, dict):
            for tag in d.get("tags") or []:
                counts[tag] = counts.get(tag, 0) + 1
    if not counts:
        print("No tags in use.")
        return
    for tag in sorted(counts):
        print(f"{tag}: {counts[tag]}")


def main(path, people_path, mode):
    try:
        data = load(path)
    except yaml.YAMLError as e:
        print(f"ERROR: YAML does not parse:\n{e}")
        return 1
    if data is None:
        print("OK: file is empty (no entries yet).")
        return 0
    if not isinstance(data, dict):
        print("ERROR: top level must be a mapping of D-001: {entry}")
        return 1

    if mode == "pending":
        report_pending(data)
        return 0
    if mode == "tags":
        report_tags(data)
        return 0

    people, extra = None, []
    if os.path.exists(people_path):
        try:
            people = load(people_path) or {}
        except yaml.YAMLError as e:
            print(f"ERROR: people directory {people_path} does not parse:\n{e}")
            return 1
    else:
        extra.append(f"people directory not found at {people_path}; driver and approver were not checked")

    errors, warnings = validate(data, people, people_path)
    for w in extra + warnings:
        print(f"WARN:  {w}")
    for e in errors:
        print(f"ERROR: {e}")
    if errors:
        print(f"{len(errors)} error(s) in {path}")
        return 1
    counts = {s: 0 for s in STATUSES}
    for d in data.values():
        counts[d["status"]] += 1
    summary = ", ".join(f"{n} {s}" for s, n in counts.items() if n)
    print(f"OK: {len(data)} decisions ({summary}), {len(extra) + len(warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    mode = "validate"
    for flag in ("--pending", "--tags"):
        if flag in args:
            mode = flag[2:]
            args.remove(flag)
    people_path = None
    if "--people" in args:
        i = args.index("--people")
        people_path = args[i + 1]
        del args[i:i + 2]
    path = args[0] if args else "docs/decisions.yaml"
    if people_path is None:
        people_path = os.path.join(os.path.dirname(path) or ".", "people.yaml")
    sys.exit(main(path, people_path, mode))
