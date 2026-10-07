#!/usr/bin/env python3
"""Validate a Project Brain people directory (people.yaml).

Usage: python3 validate.py [path/to/people.yaml]
Exit code 0 = valid (warnings may print), 1 = errors found.
"""
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml")

REQUIRED = ["name", "org", "role", "status"]
ALLOWED = set(REQUIRED) | {"aka", "tz", "ids", "owns", "notes"}
KEY_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
STATUS_RE = re.compile(r"^(active|unknown|former \(\d{4}-\d{2}-\d{2}\))$")


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


def valid_tz(tz):
    try:
        from zoneinfo import ZoneInfo
        ZoneInfo(tz)
        return True
    except Exception:
        return False


def main(path):
    errors, warnings = [], []
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.load(f, Loader=UniqueKeyLoader)
    except yaml.YAMLError as e:
        print(f"ERROR: YAML does not parse:\n{e}")
        return 1

    if data is None:
        print("OK: file is empty (no entries yet).")
        return 0
    if not isinstance(data, dict):
        print("ERROR: top level must be a mapping of lastname-firstname: {entry}")
        return 1

    keys = list(data.keys())
    if keys != sorted(keys):
        for a, b in zip(keys, keys[1:]):
            if a > b:
                errors.append(f"not alphabetized: '{b}' should come before '{a}'")

    for key, p in data.items():
        where = f"[{key}]"
        if not isinstance(key, str) or not KEY_RE.match(key):
            errors.append(f"{where} key must be lowercase lastname-firstname")
        if not isinstance(p, dict):
            errors.append(f"{where} entry must be a mapping")
            continue
        for field in REQUIRED:
            if not p.get(field):
                errors.append(f"{where} missing required field '{field}'")
        for field in p:
            if field not in ALLOWED:
                warnings.append(f"{where} unknown field '{field}'")
        status = p.get("status")
        if status and not STATUS_RE.match(str(status)):
            errors.append(f"{where} status '{status}' must be active | unknown | former (YYYY-MM-DD)")
        name = str(p.get("name", ""))
        if name:
            first = re.sub(r"[^a-z0-9]+", "-", name.split()[0].lower()).strip("-")
            if first and not key.endswith(first):
                warnings.append(f"{where} key doesn't end with first name '{first}' from '{name}'")
        tz = p.get("tz")
        if tz and not valid_tz(str(tz)):
            errors.append(f"{where} tz '{tz}' is not a valid IANA timezone")
        ids = p.get("ids")
        if ids is not None:
            if not isinstance(ids, dict):
                errors.append(f"{where} ids must be a mapping of service: \"value\"")
            else:
                for svc, val in ids.items():
                    if not isinstance(val, str):
                        errors.append(f"{where} ids.{svc} must be a quoted string (got {type(val).__name__})")
        for field in ("aka", "owns", "notes"):
            if field in p and not isinstance(p[field], list):
                errors.append(f"{where} {field} must be a list")
        for note in p.get("notes") or []:
            if not isinstance(note, str):
                errors.append(f"{where} notes entries must be quoted strings")

    for w in warnings:
        print(f"WARN:  {w}")
    for e in errors:
        print(f"ERROR: {e}")
    if errors:
        print(f"{len(errors)} error(s) in {path}")
        return 1
    print(f"OK: {len(data)} people, {len(warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "docs/people.yaml"))
