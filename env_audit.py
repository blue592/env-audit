"""Audit dotenv configuration without displaying values. Python 3.10+."""

import argparse
import json
from pathlib import Path
import re
import sys

__version__ = "0.1.0"
KEY = re.compile(r"(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)")


def parse(text):
    """Parse a deliberately small, single-line dotenv subset.

    Values are used only to identify empty assignments, never evaluated.
    Return (key -> is_empty, issues). Issues never contain source values.
    """
    entries, issues = {}, []
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = KEY.fullmatch(line)
        if not match:
            issues.append({"code": "invalid_syntax", "line": number})
            continue
        key, value = match.groups()
        if value.startswith(("'", '"')):
            quote = value[0]
            end = None
            escaped = False
            for index in range(1, len(value)):
                char = value[index]
                if char == quote and not escaped:
                    end = index
                    break
                escaped = not escaped if char == "\\" else False
            if end is None or (value[end + 1:].strip() and not value[end + 1:].lstrip().startswith("#")):
                issues.append({"code": "invalid_syntax", "line": number})
                continue
            empty = end == 1
        else:
            # A comment begins at # only at the start or after whitespace.
            value = re.split(r"(?:^|\s)#", value, maxsplit=1)[0].strip()
            empty = not value
        if key in entries:
            issues.append({"code": "duplicate_key", "line": number, "key": key})
        entries[key] = empty
    return entries, issues


def audit(template, actual, strict=False, allow_empty=()):
    expected, template_issues = parse(template)
    present, actual_issues = parse(actual)
    findings = [dict(issue, file="template") for issue in template_issues]
    findings += [dict(issue, file="actual") for issue in actual_issues]
    for key in sorted(expected.keys() - present.keys()):
        findings.append({"code": "missing_key", "key": key, "file": "actual"})
    for key in sorted(expected.keys() & present.keys()):
        if present[key] and key not in allow_empty:
            findings.append({"code": "empty_value", "key": key, "file": "actual"})
    if strict:
        for key in sorted(present.keys() - expected.keys()):
            findings.append({"code": "unexpected_key", "key": key, "file": "actual"})
    return findings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template", default=".env.example", help="Required-key template")
    parser.add_argument("--env-file", default=".env", help="Configuration to check")
    parser.add_argument("--strict", action="store_true", help="Also reject extra keys")
    parser.add_argument("--allow-empty", action="append", default=[], metavar="KEY", help="Permit an empty required key (repeatable)")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--version", action="version", version=__version__)
    args = parser.parse_args(argv)
    try:
        template = Path(args.template).read_text(encoding="utf-8-sig")
        actual = Path(args.env_file).read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError):
        # Do not echo paths or exception details: they may contain private data.
        result = {"ok": False, "findings": [{"code": "input_error"}]}
        status = 2
    else:
        findings = audit(template, actual, args.strict, args.allow_empty)
        result = {"ok": not findings, "findings": findings}
        status = 1 if findings else 0
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=True))
    elif result["ok"]:
        print("OK: configuration matches the template.")
    else:
        for finding in result["findings"]:
            details = " ".join(f"{key}={value}" for key, value in finding.items() if key != "code")
            print(f"{finding['code']}: {details}".rstrip())
        if status == 2:
            print("Could not read both inputs as UTF-8. Check file paths and permissions.", file=sys.stderr)
    return status


if __name__ == "__main__":
    sys.exit(main())
