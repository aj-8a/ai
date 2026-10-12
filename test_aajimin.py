"""Tests for Aajimin Code Intelligence. Run: python3 -m unittest -v."""
import tempfile
import unittest
from pathlib import Path

from aajimin import analyze_source, explain_source, generate_code, knowledge_search, scan_project


class AnalyzerTests(unittest.TestCase):
    def test_syntax_error(self):
        findings = analyze_source("def broken(:\n    pass\n")
        self.assertTrue(any(item["rule"] == "PY001" for item in findings))

    def test_eval_warning(self):
        findings = analyze_source("result = eval(user_input)\n")
        self.assertTrue(any(item["rule"] == "SEC001" for item in findings))

    def test_none_comparison(self):
        findings = analyze_source("if value == None:\n    pass\n")
        self.assertTrue(any(item["rule"] == "PY101" for item in findings))

    def test_mutable_default(self):
        findings = analyze_source("def collect(items=[]):\n    return items\n")
        self.assertTrue(any(item["rule"] == "PY105" for item in findings))

    def test_explain_function(self):
        result = explain_source("def greet(name):\n    return name\n", "sample.py")
        self.assertIn("greet(name)", result)
        self.assertIn("Functions: 1", result)

    def test_generator_template(self):
        result = generate_code("calculator")
        self.assertIn("def main()", result)
        self.assertIn("division by zero", result)

    def test_knowledge_search(self):
        results = knowledge_search("how do I avoid eval security")
        self.assertTrue(results)
        self.assertEqual(results[0]["topic"], "security")

    def test_project_scan_and_skip_generated_folders(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "good.py").write_text("print('hello')\n", encoding="utf-8")
            (root / ".venv").mkdir()
            (root / ".venv" / "ignored.py").write_text("eval('1')\n", encoding="utf-8")
            result = scan_project(root)
            self.assertEqual(result["files_scanned"], 1)
            self.assertEqual(result["files"][0]["file"], str(root / "good.py"))

    def test_scan_single_file(self):
        with tempfile.TemporaryDirectory() as temp:
            file = Path(temp) / "sample.py"
            file.write_text("if x == None:\n    pass\n", encoding="utf-8")
            result = scan_project(file)
            self.assertEqual(result["files_scanned"], 1)
            self.assertGreater(result["findings_total"], 0)


if __name__ == "__main__":
    unittest.main()
