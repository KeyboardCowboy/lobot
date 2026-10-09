#!/usr/bin/env python3
"""Validate a Project Brain source map (docs/sources.yaml).

Usage: python3 validate.py [path/to/sources.yaml]

Checks the `shared_drive` link, the `sources` map (Google Drive folders and
files the project uses), the `not_used` list (standard layout items the project
doesn't have), and the `processed` list (files already handled). Standard keys
are checked against layout.yaml in this script's folder.
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

KEY_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
KINDS = {"folder", "file"}
PURPOSES = {"transcripts", "reference", "deliverable"}
SOURCE_FIELDS = {"kind", "url", "purpose", "handler", "copy_to", "since", "subfolders",
                 "record", "shared_with_client", "added", "notes"}
PROCESSED_REQUIRED = ["id", "title", "source", "modified", "processed", "result"]
FOLDER_URL = re.compile(r"^https://drive\.google\.com/drive/(?:u/\d+/)?folders/([A-Za-z0-9_-]{10,})")
FILE_URL = re.compile(
    r"^https://(?:docs\.google\.com/(?:document|spreadsheets|presentation|forms)/(?:u/\d+/)?d/"
    r"|drive\.google\.com/(?:file/d/|open\?id=))([A-Za-z0-9_-]{10,})")
DRIVE_ID = re.compile(r"^[A-Za-z0-9_-]{10,}$")
TOP_LEVEL = ("shared_drive", "sources", "not_used", "processed")
LAYOUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "layout.yaml")


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


def is_date(value):
    if isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
        return True
    if isinstance(value, str):
        try:
            datetime.date.fromisoformat(value)
            return True
        except ValueError:
            return False
    return False


def is_timestamp(value):
    if isinstance(value, datetime.datetime):
        return True
    if isinstance(value, str):
        try:
            datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
            return True
        except ValueError:
            return False
    return False


def drive_id(url, kind):
    pattern = FOLDER_URL if kind == "folder" else FILE_URL
    m = pattern.match(url or "")
    return m.group(1) if m else None


def load_layout(errors):
    try:
        with open(LAYOUT_PATH, encoding="utf-8") as f:
            return (yaml.load(f, Loader=UniqueKeyLoader) or {}).get("items") or {}
    except (OSError, yaml.YAMLError) as e:
        errors.append(f"standard layout could not be read ({LAYOUT_PATH}): {e}")
        return {}


def check_shared_drive(drive, errors):
    if not isinstance(drive, dict):
        errors.append("shared_drive must be a mapping with url and added")
        return
    if not drive_id(str(drive.get("url") or ""), "folder"):
        errors.append("[shared_drive] url is not a Google Drive folder link")
    if not is_date(drive.get("added")):
        errors.append("[shared_drive] added must be a date (YYYY-MM-DD)")


def check_layout_match(key, s, layout, where, errors):
    item = layout.get(key)
    if not item:
        return
    for field in ("kind", "purpose"):
        if s.get(field) != item.get(field):
            errors.append(f"{where} is a standard layout item: {field} must be '{item.get(field)}'")


def check_not_used(not_used, sources, layout, errors):
    if not isinstance(not_used, dict):
        errors.append("not_used must be a mapping of layout-key: \"reason\"")
        return
    for key, reason in not_used.items():
        where = f"[not_used.{key}]"
        if key not in layout:
            errors.append(f"{where} is not a standard layout item")
        if key in sources:
            errors.append(f"{where} is also in sources")
        if not isinstance(reason, str) or not reason.strip():
            errors.append(f"{where} needs a quoted reason")


def check_sources(sources, layout, errors, warnings):
    if not isinstance(sources, dict):
        errors.append("sources must be a mapping of source-key: {entry}")
        return {}
    keys = list(sources.keys())
    for a, b in zip(keys, keys[1:]):
        if str(a) > str(b):
            errors.append(f"sources not alphabetized: '{b}' should come before '{a}'")
    ids = {}
    for key, s in sources.items():
        where = f"[sources.{key}]"
        if not isinstance(key, str) or not KEY_RE.match(key):
            errors.append(f"{where} key must be lowercase and hyphenated")
        if not isinstance(s, dict):
            errors.append(f"{where} entry must be a mapping")
            continue
        for field in s:
            if field not in SOURCE_FIELDS:
                warnings.append(f"{where} unknown field '{field}'")
        kind, purpose = s.get("kind"), s.get("purpose")
        if kind not in KINDS:
            errors.append(f"{where} kind must be one of: {', '.join(sorted(KINDS))}")
        if purpose not in PURPOSES:
            errors.append(f"{where} purpose must be one of: {', '.join(sorted(PURPOSES))}")
        if not s.get("url"):
            errors.append(f"{where} missing required field 'url'")
        elif kind in KINDS:
            found = drive_id(str(s["url"]), kind)
            if not found:
                errors.append(f"{where} url is not a Google Drive {kind} link")
            elif found in ids:
                errors.append(f"{where} same Drive {kind} as [sources.{ids[found]}]")
            else:
                ids[found] = key
        if not is_date(s.get("added")):
            errors.append(f"{where} added must be a date (YYYY-MM-DD)")
        if "since" in s and not is_date(s["since"]):
            errors.append(f"{where} since must be a date (YYYY-MM-DD)")
        for flag in ("subfolders", "shared_with_client"):
            if flag in s and not isinstance(s[flag], bool):
                errors.append(f"{where} {flag} must be true or false")
        if "copy_to" in s and not str(s["copy_to"]).startswith("docs/"):
            errors.append(f"{where} copy_to must be a folder under docs/")
        if "notes" in s and not isinstance(s["notes"], str):
            errors.append(f"{where} notes must be a quoted string")
        check_layout_match(key, s, layout, where, errors)
        if purpose == "transcripts":
            if kind != "folder":
                errors.append(f"{where} a transcripts source must be a folder")
            if not s.get("handler"):
                errors.append(f"{where} a transcripts source needs a handler (meeting-notes)")
            if not s.get("copy_to"):
                warnings.append(f"{where} no copy_to: transcripts won't be kept in the Project Brain")
        if kind == "folder" and "since" not in s:
            warnings.append(f"{where} no since date: the first check will list every file in the folder")
        if kind != "folder" and ("since" in s or "subfolders" in s):
            warnings.append(f"{where} since and subfolders only apply to folders")
        if purpose == "deliverable" and not s.get("record"):
            errors.append(f"{where} a deliverable needs record: the Project Brain file it corresponds to")
        if purpose != "deliverable" and ("record" in s or "shared_with_client" in s):
            warnings.append(f"{where} record and shared_with_client only apply to deliverables")
    return sources


def check_processed(processed, sources, errors, warnings):
    if not isinstance(processed, list):
        errors.append("processed must be a list of entries")
        return 0
    seen = set()
    for i, p in enumerate(processed, 1):
        where = f"[processed #{i}]"
        if not isinstance(p, dict):
            errors.append(f"{where} entry must be a mapping")
            continue
        where = f"[processed #{i} {p.get('id', '?')}]"
        for field in PROCESSED_REQUIRED:
            if not p.get(field):
                errors.append(f"{where} missing required field '{field}'")
        for field in p:
            if field not in PROCESSED_REQUIRED:
                warnings.append(f"{where} unknown field '{field}'")
        if p.get("id") and not DRIVE_ID.match(str(p["id"])):
            errors.append(f"{where} id is not a Drive file ID")
        if p.get("source") and p["source"] not in sources:
            warnings.append(f"{where} source '{p['source']}' is no longer in sources (kept as history)")
        if p.get("modified") and not is_timestamp(p["modified"]):
            errors.append(f"{where} modified must be a quoted timestamp like \"2026-10-08T21:14:49Z\"")
        if p.get("processed") and not is_date(p["processed"]):
            errors.append(f"{where} processed must be a date (YYYY-MM-DD)")
        result = p.get("result")
        if result and not (str(result).startswith("docs/") or str(result).startswith("skipped:")):
            errors.append(f"{where} result must be a docs/ path or 'skipped: <reason>'")
        pair = (p.get("id"), str(p.get("modified")))
        if pair in seen:
            errors.append(f"{where} already recorded with the same modified time")
        seen.add(pair)
    return len(processed)


def main(path):
    errors, warnings = [], []
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.load(f, Loader=UniqueKeyLoader)
    except yaml.YAMLError as e:
        print(f"ERROR: YAML does not parse:\n{e}")
        return 1
    if data is None:
        print("OK: file is empty (no sources yet).")
        return 0
    if not isinstance(data, dict):
        print("ERROR: top level must be a mapping (shared_drive, sources, not_used, processed)")
        return 1
    for key in data:
        if key not in TOP_LEVEL:
            errors.append(f"unknown top-level key '{key}'")
    layout = load_layout(errors)
    if data.get("shared_drive") is not None:
        check_shared_drive(data["shared_drive"], errors)
    sources = check_sources(data.get("sources") or {}, layout, errors, warnings)
    not_used = data.get("not_used") or {}
    check_not_used(not_used, sources if isinstance(sources, dict) else {}, layout, errors)
    count = check_processed(data.get("processed") or [], sources, errors, warnings)

    for w in warnings:
        print(f"WARN:  {w}")
    for e in errors:
        print(f"ERROR: {e}")
    if errors:
        print(f"{len(errors)} error(s) in {path}")
        return 1
    if isinstance(not_used, dict):
        accounted = set(sources) | set(not_used)
        open_items = [k for k in layout if k not in accounted]
        if open_items:
            print(f"NOTE:  standard items not yet mapped or marked not used: {', '.join(open_items)}")
    print(f"OK: {len(sources)} sources, {count} processed, {len(warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "docs/sources.yaml"))
