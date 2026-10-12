#!/usr/bin/env python3
"""Aajimin Code Intelligence — offline, rule-based Python coding assistant.

Uses only the Python standard library. No API keys, network calls, or cloud AI.
"""
from __future__ import annotations

import argparse
import ast
import re
import sys
import textwrap
from pathlib import Path

VERSION = "0.1.0"
BANNER = r"""
    _       _ _imin
   / \     (_) |           CODE INTELLIGENCE
  / _ \    | | |__   Offline Python assistant
 / ___ \   | | '_ \  No API • No cloud • Pure Python
/_/   \_\  |_|_.__/
"""


def read_source(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise ValueError(f"{path}: file is not valid UTF-8 text") from None
    except OSError as exc:
        raise ValueError(f"Cannot read {path}: {exc}") from None


def analyze_source(source: str, filename: str = "<input>") -> list[dict[str, object]]:
    """Return deterministic syntax, style, and common-bug findings."""
    findings: list[dict[str, object]] = []
    lines = source.splitlines()

    try:
        tree = ast.parse(source, filename=filename)
    except SyntaxError as exc:
        findings.append({
            "severity": "ERROR", "line": exc.lineno or 1,
            "rule": "PY001", "message": exc.msg,
            "suggestion": "Check indentation, brackets, colons, and quotes near this line.",
        })
        return findings

    def add(severity: str, line: int, rule: str, message: str, suggestion: str) -> None:
        findings.append({"severity": severity, "line": line, "rule": rule,
                         "message": message, "suggestion": suggestion})

    for number, line in enumerate(lines, 1):
        if line.rstrip(" \t") != line:
            add("INFO", number, "STYLE001", "Trailing whitespace.",
                "Remove spaces or tabs at the end of the line.")
        if len(line) > 100:
            add("INFO", number, "STYLE002", f"Long line ({len(line)} characters).",
                "Consider splitting the expression for readability.")
        if "\t" in line[:len(line) - len(line.lstrip())]:
            add("WARNING", number, "STYLE003", "Tab used for indentation.",
                "Use consistent spaces for indentation.")

    parents: dict[ast.AST, ast.AST] = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parents[child] = parent

    for node in ast.walk(tree):
        line = getattr(node, "lineno", 1)
        if isinstance(node, ast.Compare):
            if any(isinstance(op, ast.Eq) for op in node.ops) and any(
                isinstance(c, ast.Constant) and c.value is None for c in node.comparators
            ):
                add("WARNING", line, "PY101", "Comparison with None using ==.",
                    "Prefer 'value is None' for an explicit None check.")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "eval":
                add("WARNING", line, "SEC001", "Use of eval() can execute untrusted input.",
                    "Avoid eval(); parse input explicitly or use a safe data format.")
            if isinstance(node.func, ast.Name) and node.func.id == "exec":
                add("WARNING", line, "SEC002", "Use of exec() executes dynamic code.",
                    "Avoid exec() on untrusted or externally supplied content.")
            if isinstance(node.func, ast.Name) and node.func.id == "print":
                pass
        elif isinstance(node, ast.ExceptHandler) and node.type is None:
            add("WARNING", line, "PY102", "Bare except catches almost every exception.",
                "Catch a specific exception type, such as ValueError or OSError.")
        elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            if not node.name.startswith("_") and ast.get_docstring(node) is None:
                add("INFO", line, "DOC001", f"Function '{node.name}' has no docstring.",
                    "Add a short docstring describing its purpose and arguments.")
            args = [arg.arg for arg in node.args.args]
            if len(args) != len(set(args)):
                add("ERROR", line, "PY103", f"Function '{node.name}' has duplicate argument names.",
                    "Give every parameter a unique name.")
        elif isinstance(node, ast.Assign):
            if any(isinstance(t, (ast.List, ast.Dict, ast.Set)) for t in node.targets):
                add("INFO", line, "PY104", "Assignment target is a collection literal.",
                    "Check that you intended to assign into a subscript or attribute.")
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "os" and "system" in source:
                    pass

    # Avoid duplicate findings from overlapping checks.
    unique: dict[tuple[object, ...], dict[str, object]] = {}
    for item in findings:
        key = (item["severity"], item["line"], item["rule"], item["message"])
        unique[key] = item
    return sorted(unique.values(), key=lambda f: (int(f["line"]), str(f["severity"]), str(f["rule"])))


def explain_source(source: str, filename: str = "<input>") -> str:
    """Produce a compact structural explanation using Python's AST."""
    try:
        tree = ast.parse(source, filename=filename)
    except SyntaxError as exc:
        return f"Cannot explain code until its syntax error is fixed: line {exc.lineno}: {exc.msg}"

    output = [f"File overview: {filename}", ""]
    imports = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
    functions = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
    assignments = [n for n in tree.body if isinstance(n, (ast.Assign, ast.AnnAssign))]
    output.append(f"Top-level imports: {len(imports)}")
    for node in imports:
        output.append(f"  • {ast.unparse(node)}")
    output.append(f"\nTop-level variables/assignments: {len(assignments)}")
    for node in assignments:
        try:
            output.append(f"  • {ast.unparse(node)[:140]}")
        except Exception:
            output.append("  • assignment")
    output.append(f"\nFunctions: {len(functions)}")
    for node in functions:
        args = [a.arg for a in node.args.args]
        doc = ast.get_docstring(node)
        output.append(f"  • {node.name}({', '.join(args)}) — {doc.splitlines()[0] if doc else 'No docstring'}")
    output.append(f"\nClasses: {len(classes)}")
    for node in classes:
        output.append(f"  • {node.name}")
        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                output.append(f"      - {child.name}()")
    output.append(f"\nTotal lines: {len(source.splitlines())}")
    return "\n".join(output)


def generate_code(request: str) -> str:
    """Generate starter code from explicit offline templates, not a language model."""
    text = request.lower().strip()
    if any(word in text for word in ("calculator", "add two numbers", "addition")):
        return '''"""A simple command-line calculator."""\n\ndef main():\n    first = float(input("First number: "))\n    operator = input("Operator (+, -, *, /): ").strip()\n    second = float(input("Second number: "))\n\n    if operator == "+":\n        result = first + second\n    elif operator == "-":\n        result = first - second\n    elif operator == "*":\n        result = first * second\n    elif operator == "/":\n        if second == 0:\n            print("Error: division by zero.")\n            return\n        result = first / second\n    else:\n        print("Unknown operator.")\n        return\n\n    print(f"Result: {result}")\n\nif __name__ == "__main__":\n    main()\n'''
    if any(word in text for word in ("todo", "task list", "to-do")):
        return '''"""A tiny in-memory task list."""\n\ndef main():\n    tasks = []\n    while True:\n        print("\\n1. Add task  2. List tasks  3. Quit")\n        choice = input("Choose: ").strip()\n        if choice == "1":\n            task = input("Task: ").strip()\n            if task:\n                tasks.append(task)\n                print("Task added.")\n        elif choice == "2":\n            if not tasks:\n                print("No tasks yet.")\n            for index, task in enumerate(tasks, 1):\n                print(f"{index}. {task}")\n        elif choice == "3":\n            break\n        else:\n            print("Choose 1, 2, or 3.")\n\nif __name__ == "__main__":\n    main()\n'''
    if any(word in text for word in ("hello", "greeting", "say hi")):
        return '''"""A friendly greeting program."""\n\ndef greet(name: str) -> str:\n    """Return a greeting for name."""\n    clean_name = name.strip() or "developer"\n    return f"Hello, {clean_name}! Welcome to Aajimin Code Intelligence."\n\nif __name__ == "__main__":\n    print(greet(input("Your name: ")))\n'''
    return ("I don't have an offline template for that request yet. Try asking for a calculator, "
            "task list, or greeting program. This generator uses local templates, not a cloud model.")


def print_findings(findings: list[dict[str, object]]) -> None:
    if not findings:
        print("✓ No findings from the current rule set.")
        print("  Note: a clean scan does not prove the program is bug-free.")
        return
    counts = {"ERROR": 0, "WARNING": 0, "INFO": 0}
    for item in findings:
        severity = str(item["severity"])
        counts[severity] = counts.get(severity, 0) + 1
        print(f"[{severity}] line {item['line']} · {item['rule']} — {item['message']}")
        print(f"         Suggestion: {item['suggestion']}")
    print(f"\nSummary: {counts['ERROR']} error(s), {counts['WARNING']} warning(s), {counts['INFO']} info item(s).")


def interactive() -> None:
    print(BANNER)
    print("Welcome to Aajimin Code Intelligence — offline edition.")
    print("Type help for commands, exit to quit. No code is uploaded anywhere.\n")
    while True:
        try:
            command = input("aajimin> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye, developer.")
            return
        if not command:
            continue
        if command.lower() in {"exit", "quit"}:
            print("Goodbye, developer.")
            return
        if command.lower() == "help":
            print("Commands:\n  analyze <file.py>  Scan a Python file\n  explain <file.py>  Summarize its structure\n  generate <request> Generate from built-in templates\n  version            Show version\n  exit               Quit")
            continue
        if command.lower() == "version":
            print(f"Aajimin Code Intelligence v{VERSION} · Python {sys.version.split()[0]}")
            continue
        match = re.match(r"^(analyze|explain)\s+(.+)$", command, re.I)
        if match:
            path = Path(match.group(2).strip().strip('"').strip("'"))
            try:
                source = read_source(path)
                if match.group(1).lower() == "analyze":
                    print_findings(analyze_source(source, str(path)))
                else:
                    print(explain_source(source, str(path)))
            except ValueError as exc:
                print(f"Error: {exc}")
            continue
        if command.lower().startswith("generate "):
            print(generate_code(command[9:]))
            continue
        print("Unknown command. Type help to see available commands.")


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="aajimin",
        description="Aajimin Code Intelligence — offline Python analysis with no API.",
        epilog="Examples: python aajimin.py analyze app.py | python aajimin.py explain app.py",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    sub = parser.add_subparsers(dest="command")
    analyze = sub.add_parser("analyze", help="analyze a Python file")
    analyze.add_argument("file", type=Path)
    explain = sub.add_parser("explain", help="explain a Python file's structure")
    explain.add_argument("file", type=Path)
    generate = sub.add_parser("generate", help="generate code from offline templates")
    generate.add_argument("request", nargs="+")
    args = parser.parse_args()

    if args.command is None:
        interactive()
        return 0
    if args.command in {"analyze", "explain"}:
        try:
            source = read_source(args.file)
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 2
        if args.command == "analyze":
            findings = analyze_source(source, str(args.file))
            print_findings(findings)
            return 1 if any(item["severity"] == "ERROR" for item in findings) else 0
        print(explain_source(source, str(args.file)))
        return 0
    if args.command == "generate":
        print(generate_code(" ".join(args.request)), end="" if generate_code(" ".join(args.request)).endswith("\n") else "\n")
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
