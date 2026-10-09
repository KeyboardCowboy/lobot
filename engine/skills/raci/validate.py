#!/usr/bin/env python3
"""Validate a Project Brain RACI matrix (raci.yaml) and report on it.

Usage:
  python3 validate.py [path/to/raci.yaml] [--people path/to/people.yaml]
  python3 validate.py [path/to/raci.yaml] --table [--scope SCOPE]   # Markdown matrix to share
  python3 validate.py [path/to/raci.yaml] --person KEY              # everything one person holds

The file has three parts: `scopes` (the sites or programs, optional), `roles`
(each role's side and who fills it in each scope), and `rows` (who is R, A, C,
and I for each responsibility). Rows name roles; roles name people. A row key
ending in `@<scope>` replaces the row with the same base key for that scope only.

The people directory (default: people.yaml next to the matrix) is loaded so
role holders can be checked and shown by name.
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

STATUSES = ["draft", "agreed", "needs-review"]
ORGS = ["agency", "client"]
TOP_ALLOWED = {"status", "agreed", "review_reason", "scopes", "roles", "rows"}
ROLE_ALLOWED = {"org", "title", "people", "source"}
ROW_REQUIRED = ["area", "responsibility", "R", "A"]
ROW_ALLOWED = set(ROW_REQUIRED) | {"C", "I", "backup", "response_window", "sow_ref", "dependency", "source", "notes"}
LETTERS = ["R", "A", "C", "I"]
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
# A row key is a slug, optionally followed by @scope for a scope-specific override.
ROW_KEY_RE = re.compile(r"^([a-z0-9]+(?:-[a-z0-9]+)*)(?:@([a-z0-9]+(?:-[a-z0-9]+)*))?$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ALL = "all"      # the scope that applies everywhere; the only scope when none are declared
TBD = "tbd"      # a role holder who hasn't been named yet: allowed, but reported
MAX_ROWS = 25    # beyond this the matrix stops being something people read
MAX_C = 3        # more consulted roles than this slows every decision on the row
MIN_ROWS_FOR_LOAD_CHECK = 6


class UniqueKeyLoader(yaml.SafeLoader):
    """SafeLoader that errors on duplicate mapping keys instead of overwriting.

    Duplicate row keys matter here: two `scope-change@site-a` rows would mean
    two answers to "who is accountable", and plain YAML keeps only the last.
    """


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


# ---------------------------------------------------------------------------
# Resolving rows and roles to people, per scope
# ---------------------------------------------------------------------------

def scope_names(data):
    """The scopes every general row must cover: the declared ones, or just 'all'."""
    scopes = data.get("scopes")
    return list(scopes) if isinstance(scopes, dict) and scopes else [ALL]


def row_scopes(key, rows, scopes):
    """The scopes a row applies to.

    `x@s` applies to s only. A general row `x` applies to every scope that
    has no `x@s` override.
    """
    m = ROW_KEY_RE.match(key)
    if not m:
        return []
    base, scope = m.groups()
    if scope:
        return [scope]
    return [s for s in scopes if f"{base}@{s}" not in rows]


def holders(role, scope):
    """Who fills a role in a scope, as a list of people keys, ['tbd'], or None.

    A scope's own entry wins over 'all', so `{all: a, site-c: b}` means
    "a everywhere except site-c".
    """
    people = role.get("people") if isinstance(role, dict) else None
    if not isinstance(people, dict):
        return None
    value = people.get(scope, people.get(ALL))
    if value is None:
        return None
    return value if isinstance(value, list) else [value]


def as_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate(data, people, people_path):
    errors, warnings = [], []
    for field in data:
        if field not in TOP_ALLOWED:
            warnings.append(f"unknown top-level field '{field}'")
    _check_status(data, people, people_path, errors, warnings)
    scopes = _check_scopes(data, errors)
    roles = data.get("roles") or {}
    if not isinstance(roles, dict):
        errors.append("roles must be a mapping of role-key: {org, title, people}")
        roles = {}
    _check_roles(roles, scopes, people, people_path, errors, warnings)
    rows = data.get("rows") or {}
    if not isinstance(rows, dict):
        errors.append("rows must be a mapping of row-key: {area, responsibility, R, A, ...}")
        rows = {}
    _check_rows(rows, roles, scopes, errors, warnings)
    _check_load(rows, roles, scopes, warnings)
    return errors, warnings


def _check_status(data, people, people_path, errors, warnings):
    status = data.get("status")
    if status is None:
        if data.get("rows"):
            errors.append(f"missing 'status' ({' | '.join(STATUSES)})")
        return
    if status not in STATUSES:
        errors.append(f"status must be one of: {', '.join(STATUSES)}")
        return
    agreed = data.get("agreed")
    if status == "agreed":
        if not isinstance(agreed, dict):
            errors.append("status 'agreed' needs an 'agreed' block (date, by, source)")
        else:
            when = as_date(agreed.get("date"))
            if when is None:
                errors.append("agreed.date must be a date (YYYY-MM-DD)")
            elif when > datetime.date.today():
                warnings.append("agreed.date is in the future")
            by = agreed.get("by")
            if not isinstance(by, list) or not by:
                errors.append("agreed.by must list who agreed (people directory keys), at least one per side")
            elif people is not None:
                for key in by:
                    if key not in people:
                        errors.append(f"agreed.by '{key}' is not a key in {people_path}")
            if not agreed.get("source"):
                warnings.append("agreed.source should say where the agreement is recorded")
    if status == "needs-review" and not data.get("review_reason"):
        errors.append("status 'needs-review' needs a 'review_reason'")


def _check_scopes(data, errors):
    scopes = data.get("scopes")
    if scopes is None:
        return [ALL]
    if not isinstance(scopes, dict):
        errors.append("scopes must be a mapping of scope-key: \"Display name\"")
        return [ALL]
    for key in scopes:
        if not isinstance(key, str) or not SLUG_RE.match(key) or key in (ALL, TBD):
            errors.append(f"scope key '{key}' must be lowercase and hyphenated, and not 'all' or 'tbd'")
    if len(scopes) == 1:
        errors.append("declare scopes only when there are two or more; a single site or program uses 'all'")
    return scope_names(data)


def _check_roles(roles, scopes, people, people_path, errors, warnings):
    valid_scope_keys = set(scopes) | {ALL}
    for key, role in roles.items():
        where = f"[role {key}]"
        if not isinstance(key, str) or not SLUG_RE.match(key):
            errors.append(f"{where} key must be lowercase and hyphenated")
        if not isinstance(role, dict):
            errors.append(f"{where} must be a mapping")
            continue
        for field in role:
            if field not in ROLE_ALLOWED:
                warnings.append(f"{where} unknown field '{field}'")
        if role.get("org") not in ORGS:
            errors.append(f"{where} org must be one of: {', '.join(ORGS)}")
        if not role.get("title"):
            errors.append(f"{where} missing 'title'")
        assigned = role.get("people")
        if not isinstance(assigned, dict) or not assigned:
            errors.append(f"{where} people must be a mapping of scope: person, e.g. {{all: lastname-firstname}}")
            continue
        for scope, value in assigned.items():
            if scope not in valid_scope_keys:
                errors.append(f"{where} people has scope '{scope}', which is not 'all' or a declared scope")
            keys = as_list(value)
            if not keys:
                errors.append(f"{where} people.{scope} is empty; use tbd if nobody is named yet")
            for person in keys:
                if person == TBD:
                    continue
                if not isinstance(person, str):
                    errors.append(f"{where} people.{scope} must hold people directory keys")
                elif people is not None:
                    if person not in people:
                        errors.append(f"{where} '{person}' is not a key in {people_path}")
                    elif not str((people[person] or {}).get("status", "")).startswith("active"):
                        warnings.append(f"{where} '{person}' is not active in the people directory")


def _check_rows(rows, roles, scopes, errors, warnings):
    if len(rows) > MAX_ROWS:
        warnings.append(f"{len(rows)} rows; keep the matrix to about {MAX_ROWS} so people read it")
    used = set()
    for key, row in rows.items():
        where = f"[row {key}]"
        m = ROW_KEY_RE.match(key) if isinstance(key, str) else None
        if not m:
            errors.append(f"{where} key must be lowercase and hyphenated, optionally ending in @scope")
            continue
        if m.group(2) and m.group(2) not in scopes:
            errors.append(f"{where} @{m.group(2)} is not a declared scope")
            continue
        if not isinstance(row, dict):
            errors.append(f"{where} must be a mapping")
            continue
        for field in ROW_REQUIRED:
            if not row.get(field):
                errors.append(f"{where} missing required field '{field}'")
        for field in row:
            if field not in ROW_ALLOWED:
                warnings.append(f"{where} unknown field '{field}'")
        if row.get("area") and not SLUG_RE.match(str(row["area"])):
            errors.append(f"{where} area must be lowercase and hyphenated")
        if "dependency" in row and not isinstance(row["dependency"], bool):
            errors.append(f"{where} dependency must be true or false")
        if not row.get("source"):
            warnings.append(f"{where} no 'source'; say where this assignment came from")

        # Exactly one A. A list is a mistake even when it holds one role,
        # because it invites a second to be added later.
        accountable = row.get("A")
        if isinstance(accountable, list):
            errors.append(f"{where} A must be exactly one role, not a list")
            accountable = None
        elif accountable is not None and not isinstance(accountable, str):
            errors.append(f"{where} A must be one role key")
            accountable = None
        for letter in ("R", "C", "I"):
            if letter in row and not isinstance(row[letter], list):
                errors.append(f"{where} {letter} must be a list of roles")
        if len(as_list(row.get("C"))) > MAX_C:
            warnings.append(f"{where} {len(row['C'])} consulted roles; more than {MAX_C} slows every decision")

        letters = {}
        for letter in LETTERS:
            refs = as_list(row.get(letter))
            if not all(isinstance(ref, str) for ref in refs):
                errors.append(f"{where} {letter} must hold role keys only")
                refs = [ref for ref in refs if isinstance(ref, str)]
            letters[letter] = refs
        for letter, refs in letters.items():
            if len(refs) != len(set(refs)):
                errors.append(f"{where} {letter} lists the same role twice")
            for ref in refs:
                used.add(ref)
                if ref not in roles:
                    errors.append(f"{where} {letter} '{ref}' is not a defined role")
        # A and R may be the same role (common on small teams). Anything else
        # held twice on one row is a contradiction: you can't do the work and
        # also only be told about it.
        doers = set(letters["R"]) | set(letters["A"])
        for ref in set(letters["C"]) & doers:
            errors.append(f"{where} '{ref}' is both C and R/A")
        for ref in set(letters["I"]) & (doers | set(letters["C"])):
            errors.append(f"{where} '{ref}' is I and also R, A, or C")

        backup = row.get("backup")
        if backup is not None and not isinstance(backup, str):
            errors.append(f"{where} backup must be one role key")
            backup = None
        if backup is not None:
            used.add(backup)
            if backup not in roles:
                errors.append(f"{where} backup '{backup}' is not a defined role")
            elif backup == accountable:
                errors.append(f"{where} backup must be a different role from A")
        if accountable in roles and roles[accountable].get("org") == "client":
            if not backup:
                warnings.append(f"{where} client A has no 'backup'; work stalls when they're away")
            if not row.get("response_window"):
                warnings.append(f"{where} client A has no 'response_window' (e.g. \"5 business days\")")

        _check_row_people(where, key, rows, letters, backup, roles, scopes, errors, warnings)

    for key in roles:
        if key not in used:
            warnings.append(f"[role {key}] not used by any row")


def _check_row_people(where, key, rows, letters, backup, roles, scopes, errors, warnings):
    """Every role on the row must resolve to someone in every scope the row covers."""
    covered = row_scopes(key, rows, scopes)
    refs = [(letter, ref) for letter in LETTERS for ref in letters[letter]]
    if backup:
        refs.append(("backup", backup))
    for scope in covered:
        label = "" if scope == ALL else f" in {scope}"
        for letter, ref in refs:
            if ref not in roles:
                continue  # already reported
            who = holders(roles[ref], scope)
            if who is None:
                errors.append(f"{where} {letter} role '{ref}' has nobody assigned{label}")
            elif TBD in who:
                warnings.append(f"{where} {letter} role '{ref}' is tbd{label}: open question")
            elif letter == "A" and len(who) != 1:
                errors.append(f"{where} A role '{ref}' resolves to {len(who)} people{label}; A must be one person")


def _check_load(rows, roles, scopes, warnings):
    """Warn when one person is accountable for most rows in a scope: a bottleneck."""
    for scope in scopes:
        counts, total = {}, 0
        for key, row in rows.items():
            if not isinstance(row, dict) or scope not in row_scopes(key, rows, scopes):
                continue
            total += 1
            role = roles.get(row.get("A")) if isinstance(row.get("A"), str) else None
            for person in holders(role, scope) or []:
                if person != TBD:
                    counts[person] = counts.get(person, 0) + 1
        if total < MIN_ROWS_FOR_LOAD_CHECK:
            continue
        label = "" if scope == ALL else f" in {scope}"
        for person, n in counts.items():
            if n > total / 2:
                warnings.append(f"'{person}' is A on {n} of {total} rows{label}: likely a bottleneck")


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

def person_name(key, people):
    entry = (people or {}).get(key) or {}
    return entry.get("name") or key


def person_email(key, people):
    entry = (people or {}).get(key) or {}
    return (entry.get("ids") or {}).get("email", "")


def report_table(data, people, only_scope):
    """Print the matrix as Markdown, one section per scope.

    Columns are the roles used in that scope, headed by title. A "Who's who"
    table under each matrix says who fills each role and how to reach them,
    so the client can find the right person without asking the PM.
    """
    rows, roles = data.get("rows") or {}, data.get("roles") or {}
    scopes = scope_names(data)
    names = data.get("scopes") or {}
    if only_scope:
        if only_scope not in scopes:
            print(f"ERROR: '{only_scope}' is not a declared scope ({', '.join(scopes)})")
            return 1
        scopes = [only_scope]
    for scope in scopes:
        if scope != ALL:
            print(f"## {names.get(scope, scope)}\n")
        in_scope = [(k, r) for k, r in rows.items() if scope in row_scopes(k, rows, scope_names(data))]
        # Group by area, keeping the order areas first appear in the file.
        areas = list(dict.fromkeys(r.get("area") for _, r in in_scope))
        in_scope.sort(key=lambda kr: areas.index(kr[1].get("area")))
        used = {ref for _, r in in_scope for letter in LETTERS for ref in as_list(r.get(letter))}
        cols = [k for k in roles if k in used]
        print("| Area | Responsibility | " + " | ".join(roles[c].get("title", c) for c in cols) + " |")
        print("|---|---|" + "---|" * len(cols))
        for _, r in in_scope:
            cells = []
            for c in cols:
                marks = [letter for letter in LETTERS if c in as_list(r.get(letter))]
                cells.append("/".join(marks))
            print(f"| {r.get('area')} | {r.get('responsibility')} | " + " | ".join(cells) + " |")
        print("\n**Who's who**\n")
        print("| Role | Side | Person | Email |")
        print("|---|---|---|---|")
        for c in cols:
            for person in holders(roles[c], scope) or ["(nobody assigned)"]:
                name = "TBD" if person == TBD else person_name(person, people)
                email = "" if person == TBD else person_email(person, people)
                print(f"| {roles[c].get('title', c)} | {roles[c].get('org')} | {name} | {email} |")
        print()
    return 0


def report_person(data, people, key):
    """List every role a person fills and every row they appear on, by scope."""
    rows, roles = data.get("rows") or {}, data.get("roles") or {}
    scopes = scope_names(data)
    print(f"{person_name(key, people)} ({key})")
    found = False
    for scope in scopes:
        mine = {r for r, role in roles.items() if key in (holders(role, scope) or [])}
        if not mine:
            continue
        found = True
        label = "" if scope == ALL else f" in {scope}"
        print(f"\nRoles{label}: {', '.join(sorted(mine))}")
        for row_key, row in rows.items():
            if scope not in row_scopes(row_key, rows, scopes):
                continue
            marks = [letter for letter in LETTERS if set(as_list(row.get(letter))) & mine]
            if row.get("backup") in mine:
                marks.append("backup")
            if marks:
                print(f"- {'/'.join(marks)} | {row_key} | {row.get('responsibility')}")
    if not found:
        print("Fills no role in the matrix.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(path, people_path, mode, arg):
    try:
        data = load(path)
    except yaml.YAMLError as e:
        print(f"ERROR: YAML does not parse:\n{e}")
        return 1
    if data is None:
        print("OK: file is empty (no matrix yet).")
        return 0
    if not isinstance(data, dict):
        print("ERROR: top level must be a mapping with status, roles, and rows")
        return 1

    people, extra = None, []
    if os.path.exists(people_path):
        try:
            people = load(people_path) or {}
        except yaml.YAMLError as e:
            print(f"ERROR: people directory {people_path} does not parse:\n{e}")
            return 1
    else:
        extra.append(f"people directory not found at {people_path}; role holders were not checked")

    if mode == "table":
        return report_table(data, people, arg)
    if mode == "person":
        report_person(data, people, arg)
        return 0

    errors, warnings = validate(data, people, people_path)
    for w in extra + warnings:
        print(f"WARN:  {w}")
    for e in errors:
        print(f"ERROR: {e}")
    if errors:
        print(f"{len(errors)} error(s) in {path}")
        return 1
    rows, roles = data.get("rows") or {}, data.get("roles") or {}
    print(f"OK: {data.get('status', 'no status')}, {len(rows)} rows, {len(roles)} roles, "
          f"{len(scope_names(data))} scope(s), {len(extra) + len(warnings)} warning(s).")
    return 0


def _take_option(args, flag):
    """Remove `flag VALUE` from args and return VALUE, or None if absent."""
    if flag not in args:
        return None
    i = args.index(flag)
    if i + 1 >= len(args):
        sys.exit(f"{flag} needs a value")
    value = args[i + 1]
    del args[i:i + 2]
    return value


if __name__ == "__main__":
    args = sys.argv[1:]
    mode, arg = "validate", None
    people_path = _take_option(args, "--people")
    scope = _take_option(args, "--scope")
    person = _take_option(args, "--person")
    if "--table" in args:
        mode, arg = "table", scope
        args.remove("--table")
    elif person:
        mode, arg = "person", person
    path = args[0] if args else "docs/raci.yaml"
    if people_path is None:
        people_path = os.path.join(os.path.dirname(path) or ".", "people.yaml")
    sys.exit(main(path, people_path, mode, arg))
