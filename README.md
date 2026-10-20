# env-audit

Catch missing configuration before starting an app or deploying it.

A small Python CLI that compares `.env` with `.env.example`. No runtime dependencies, no network requests, no configuration writes. Reports key names and line numbers without logging assignment values.

## Quick start

Requires Python 3.10 or newer. Run from this repository:

```sh
python env_audit.py --template examples/.env.example --env-file examples/valid.env
python env_audit.py --template examples/.env.example --env-file examples/invalid.env
```

The second command intentionally exits with status 1:

```text
missing_key: key=API_TOKEN file=actual
empty_value: key=LOG_LEVEL file=actual
```

To check your own project, copy `env_audit.py` into it and run:

```sh
python env_audit.py
python env_audit.py --strict --allow-empty OPTIONAL_KEY
python env_audit.py --format json
```

Alternatively, install from this local checkout with `python -m pip install .`, then use `env-audit`. Installation needs setuptools; direct script execution needs only Python. This project has not been published to PyPI.

## What it checks

| Check | Default behavior |
| --- | --- |
| Key present in template but absent in actual file | Fail |
| Required key assigned an empty value | Fail; allow with repeatable `--allow-empty KEY` |
| Duplicate keys in either file | Fail |
| Malformed assignments in either file | Fail |
| Extra keys in actual file | Allowed; fail with `--strict` |

Every template key is required, even when its example value is empty. Template values are not defaults. Empty extra keys are ignored unless `--strict` rejects the key itself. Comments cannot mark a key optional; omit optional keys from the template or permit their empty values explicitly. `--allow-empty` does not permit a missing key.

Exit codes: **0** clean, **1** configuration findings, **2** unreadable/non-UTF-8 input or command usage error. `--format json` emits an object with `ok` and `findings` for audit results and input errors. Argument usage errors follow argparse's normal stderr output.

## Supported file syntax

- UTF-8, optionally with BOM; LF and CRLF.
- Blank lines, full-line `#` comments, `KEY=value`, optional `export` prefix.
- Keys match `[A-Za-z_][A-Za-z0-9_]*`.
- Single-line quoted values, including escaped quote characters.
- Unquoted `#` starts a comment only at the start of the value or after whitespace. `URL=https://host/#section` remains a nonempty value.

This is a configuration **presence check**, with a deliberately small dotenv subset. It does not load environment variables, expand `$VARIABLES`, decode escapes, execute shell code, support multiline values, check types, validate credentials, or detect placeholder values such as `changeme`. Quoted spaces count as nonempty. Use your runtime's dotenv loader for application loading semantics.

## CI usage

After creating your deployment configuration within a job, run:

```sh
python env_audit.py --template .env.example --env-file .env --strict
```

Keep real `.env` files out of source control. The included test workflow uses dummy fixtures only. Values are never included in findings, including malformed lines; key names and line numbers are visible. This is not a secret scanner or a guarantee that your configuration is safe to publish.

## Development

```sh
python -m unittest discover -s tests -v
```

Tests cover parsing, duplicate keys, malformed input, missing and empty keys, strict mode, value redaction, UTF-8 BOM, input failures, and process exit behavior. GitHub Actions is configured for Linux, Windows, and macOS with Python 3.10, 3.13, and 3.14.

See [한국어 설명](README.ko.md) and [contribution guidelines](CONTRIBUTING.md). MIT licensed.
