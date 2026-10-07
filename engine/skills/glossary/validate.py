#!/usr/bin/env python3
"""Validate a Project Brain glossary (glossary.yaml).

Usage: python3 validate.py [path/to/glossary.yaml] [--shared path/to/shared.yaml]

When validating a project glossary, the shared glossary (default:
.ai/general/glossary.yaml, if it exists and isn't the file being validated)
is loaded so `related` can point at shared keys and overrides are flagged.
Exit code 0 = valid (warnings may print), 1 = errors found.
"""
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml")

REQUIRED = ["term", "means"]
ALLOWED = set(REQUIRED) | {"expands", "aka", "related", "notes"}
KEY_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


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


def main(path, shared_path=None):
    errors, warnings = [], []
    try:
        data = load(path)
    except yaml.YAMLError as e:
        print(f"ERROR: YAML does not parse:\n{e}")
        return 1
    shared = {}
    if shared_path and os.path.abspath(shared_path) != os.path.abspath(path) and os.path.exists(shared_path):
        try:
            shared = load(shared_path) or {}
        except yaml.YAMLError as e:
            print(f"ERROR: shared glossary {shared_path} does not parse:\n{e}")
            return 1

    if data is None:
        print("OK: file is empty (no entries yet).")
        return 0
    if not isinstance(data, dict):
        print("ERROR: top level must be a mapping of term-key: {entry}")
        return 1

    keys = list(data.keys())
    for a, b in zip(keys, keys[1:]):
        if str(a) > str(b):
            errors.append(f"not alphabetized: '{b}' should come before '{a}'")

    names = {}  # lowercase term/aka -> key, to catch collisions
    for key, t in data.items():
        where = f"[{key}]"
        if not isinstance(key, str) or not KEY_RE.match(key):
            errors.append(f"{where} key must be lowercase and hyphenated")
        if not isinstance(t, dict):
            errors.append(f"{where} entry must be a mapping")
            continue
        if key in shared:
            warnings.append(f"{where} overrides the shared glossary entry; make sure that's intended")
        for field in REQUIRED:
            if not t.get(field):
                errors.append(f"{where} missing required field '{field}'")
        for field in t:
            if field not in ALLOWED:
                warnings.append(f"{where} unknown field '{field}'")
        if "means" in t and not isinstance(t["means"], str):
            errors.append(f"{where} means must be a quoted string")
        elif isinstance(t.get("means"), str):
            sentences = len(re.findall(r"[.!?](\s|$)", t["means"]))
            if sentences > 4:
                warnings.append(f"{where} means has ~{sentences} sentences; keep it to 1-3 and move history to notes")
        for field in ("aka", "related", "notes"):
            if field in t and not isinstance(t[field], list):
                errors.append(f"{where} {field} must be a list")
        for note in t.get("notes") or []:
            if not isinstance(note, str):
                errors.append(f"{where} notes entries must be quoted strings")
        for ref in t.get("related") or []:
            if ref not in data and ref not in shared:
                errors.append(f"{where} related '{ref}' is not a glossary key")
            elif ref == key:
                warnings.append(f"{where} relates to itself")
        for label in [t.get("term"), t.get("expands")] + list(t.get("aka") or []):
            if not label:
                continue
            low = str(label).lower()
            if low in names and names[low] != key:
                warnings.append(f"{where} '{label}' also names [{names[low]}]; disambiguate")
            names.setdefault(low, key)

    for w in warnings:
        print(f"WARN:  {w}")
    for e in errors:
        print(f"ERROR: {e}")
    if errors:
        print(f"{len(errors)} error(s) in {path}")
        return 1
    print(f"OK: {len(data)} terms, {len(warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    shared_path = ".ai/general/glossary.yaml"
    if "--shared" in args:
        i = args.index("--shared")
        shared_path = args[i + 1]
        del args[i:i + 2]
    sys.exit(main(args[0] if args else "docs/glossary.yaml", shared_path))
