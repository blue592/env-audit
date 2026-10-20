import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from env_audit import audit, main, parse


class AuditTests(unittest.TestCase):
    def test_supported_syntax(self):
        entries, issues = parse('# comment\nexport HOST = localhost\nURL=https://host/#part\nTOKEN="a # b" # comment\nEMPTY= # comment\nBLANK=\'\'\n')
        self.assertEqual(issues, [])
        self.assertEqual(entries, {"HOST": False, "URL": False, "TOKEN": False, "EMPTY": True, "BLANK": True})

    def test_required_empty_and_extra(self):
        result = audit("A=\nB=\nC=\n", "A=ok\nB=\nD=extra\n", strict=True)
        self.assertEqual([item["code"] for item in result], ["missing_key", "empty_value", "unexpected_key"])
        self.assertEqual(audit("A=", "A=", allow_empty=["A"]), [])

    def test_duplicate_and_bad_syntax_in_both_inputs(self):
        result = audit("A=\nA=\nbroken", "A=ok\nA=ok\nX=\"unterminated")
        self.assertEqual([item["code"] for item in result], ["duplicate_key", "invalid_syntax", "duplicate_key", "invalid_syntax"])

    def test_quoted_values_and_escapes(self):
        self.assertEqual(parse('A="a\\\"b"\nB="" # empty')[0], {"A": False, "B": True})
        self.assertEqual(parse('A="value" garbage')[1][0]["code"], "invalid_syntax")

    def test_values_never_appear_in_findings(self):
        secret = "super-private-password"
        result = audit("A=", f'A={secret}\nA={secret}\nmalformed {secret}\nB="{secret}')
        self.assertNotIn(secret, json.dumps(result))

    def test_cli_json_bom_and_exit_codes(self):
        with tempfile.TemporaryDirectory() as directory:
            template = Path(directory) / "example"
            actual = Path(directory) / "actual"
            template.write_text("A=", encoding="utf-8-sig")
            actual.write_text("A=value", encoding="utf-8-sig")
            args = ["--template", str(template), "--env-file", str(actual), "--format", "json"]
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(main(args), 0)
            self.assertTrue(json.loads(output.getvalue())["ok"])
            actual.write_text("B=value", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(args), 1)
            actual.write_bytes(b"\xff")
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(main(args), 2)
            self.assertEqual(json.loads(output.getvalue())["findings"], [{"code": "input_error"}])
            actual.unlink()
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(args), 2)

    def test_process_exit_code(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run([sys.executable, str(root / "env_audit.py"), "--template", str(root / "examples/.env.example"), "--env-file", str(root / "examples/valid.env")], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
