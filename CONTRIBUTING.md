# Contributing

Small, focused fixes are welcome. Describe the failing input using dummy values and explain the expected behavior. Never include real credentials in issues, pull requests, logs, or fixtures.

Run `python -m unittest discover -s tests -v` before submitting a change. Add regression coverage for parsing changes and preserve the rule that diagnostics must not contain assignment values. Keep runtime dependencies at zero and maintain Python 3.10 compatibility.

The parser intentionally handles a small single-line subset. Discuss broader syntax changes before adding them; document any changes in README.md and README.ko.md.
