"""Smoke tests for Aajimin Code Intelligence. Run: python3 -m unittest."""
import unittest

from aajimin import analyze_source, explain_source, generate_code


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

    def test_explain_function(self):
        result = explain_source("def greet(name):\n    return name\n", "sample.py")
        self.assertIn("greet(name)", result)
        self.assertIn("Functions: 1", result)

    def test_generator_template(self):
        result = generate_code("calculator")
        self.assertIn("def main()", result)
        self.assertIn("division by zero", result)


if __name__ == "__main__":
    unittest.main()
