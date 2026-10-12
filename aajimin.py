#!/usr/bin/env python3
"""Aajimin Code Intelligence: local-first Python analysis with no API or dependencies."""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

VERSION = "0.2.0"
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules", "dist", "build", ".mypy_cache", ".pytest_cache"}
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
    """Return deterministic syntax, security, and maintainability findings."""
    findings: list[dict[str, object]] = []
    lines = source.splitlines()

    def add(severity: str, line: int, rule: str, message: str, suggestion: str) -> None:
        findings.append({"severity": severity, "line": line, "rule": rule,
                         "message": message, "suggestion": suggestion, "file": filename})

    try:
        tree = ast.parse(source, filename=filename)
    except SyntaxError as exc:
        add("ERROR", exc.lineno or 1, "PY001", exc.msg,
            "Check indentation, brackets, colons, and quotes near this line.")
        return findings

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

    for node in ast.walk(tree):
        line = getattr(node, "lineno", 1)
        if isinstance(node, ast.Compare):
            for left, op, right in zip([node.left, *node.comparators[:-1]], node.ops, node.comparators):
                if isinstance(op, (ast.Eq, ast.NotEq)) and (
                    isinstance(left, ast.Constant) and left.value is None or
                    isinstance(right, ast.Constant) and right.value is None
                ):
                    add("WARNING", line, "PY101", "Comparison with None using == or !=.",
                        "Prefer 'value is None' or 'value is not None'.")
                    break
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "eval":
                add("WARNING", line, "SEC001", "Use of eval() can execute untrusted input.",
                    "Avoid eval(); parse input explicitly or use a safe data format.")
            elif node.func.id == "exec":
                add("WARNING", line, "SEC002", "Use of exec() executes dynamic code.",
                    "Avoid exec() on untrusted or externally supplied content.")
        elif isinstance(node, ast.ExceptHandler) and node.type is None:
            add("WARNING", line, "PY102", "Bare except catches almost every exception.",
                "Catch a specific exception type, such as ValueError or OSError.")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_") and ast.get_docstring(node) is None:
                add("INFO", line, "DOC001", f"Public function '{node.name}' has no docstring.",
                    "Add a short docstring describing its purpose and arguments.")
            positional_defaults = node.args.defaults
            for arg, default in zip(node.args.args[-len(positional_defaults):] if positional_defaults else [],
                                    positional_defaults):
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    add("WARNING", getattr(default, "lineno", line), "PY105",
                        f"Mutable default argument for '{arg.arg}'.",
                        "Use None as the default and create a new collection inside the function.")
        elif isinstance(node, ast.Assert) and isinstance(node.test, ast.Constant) and node.test.value is False:
            add("WARNING", line, "PY106", "Unconditional assert False.",
                "Remove this assertion or replace it with an intentional exception.")

    unique = {}
    for item in findings:
        key = (item["severity"], item["line"], item["rule"], item["message"])
        unique[key] = item
    return sorted(unique.values(), key=lambda f: (int(f["line"]), str(f["severity"]), str(f["rule"])))


def explain_source(source: str, filename: str = "<input>") -> str:
    """Summarize top-level structure without executing the inspected code."""
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
    output.extend(f"  • {ast.unparse(node)}" for node in imports)
    output.append(f"\nTop-level assignments: {len(assignments)}")
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


def scan_project(root: Path, include_hidden: bool = False) -> dict[str, object]:
    """Analyze Python files beneath a folder, skipping common generated directories."""
    if not root.exists():
        raise ValueError(f"Path does not exist: {root}")
    if root.is_file():
        paths = [root] if root.suffix == ".py" else []
    elif root.is_dir():
        paths = []
        for path in root.rglob("*.py"):
            relative = path.relative_to(root)
            if any(part in SKIP_DIRS for part in relative.parts):
                continue
            if not include_hidden and any(part.startswith(".") for part in relative.parts):
                continue
            paths.append(path)
    else:
        paths = []
    files = []
    for path in sorted(paths):
        try:
            findings = analyze_source(read_source(path), str(path))
            files.append({"file": str(path), "findings": findings, "finding_count": len(findings)})
        except ValueError as exc:
            files.append({"file": str(path), "error": str(exc), "findings": [], "finding_count": 0})
    all_findings = [finding for item in files for finding in item["findings"]]
    return {
        "tool": "Aajimin Code Intelligence",
        "version": VERSION,
        "root": str(root),
        "files_scanned": len(files),
        "findings_total": len(all_findings),
        "summary": {level: sum(f["severity"] == level for f in all_findings)
                    for level in ("ERROR", "WARNING", "INFO")},
        "files": files,
    }


def generate_code(request: str) -> str:
    """Generate starter code from local templates, not a language model."""
    text = request.lower().strip()
    if any(word in text for word in ("calculator", "add two numbers", "addition")):
        return '''"""A simple command-line calculator."""

def main():
    first = float(input("First number: "))
    operator = input("Operator (+, -, *, /): ").strip()
    second = float(input("Second number: "))

    if operator == "+":
        result = first + second
    elif operator == "-":
        result = first - second
    elif operator == "*":
        result = first * second
    elif operator == "/":
        if second == 0:
            print("Error: division by zero.")
            return
        result = first / second
    else:
        print("Unknown operator.")
        return

    print(f"Result: {result}")

if __name__ == "__main__":
    main()
'''
    if any(word in text for word in ("todo", "task list", "to-do")):
        return '''"""A tiny in-memory task list."""

def main():
    tasks = []
    while True:
        print("\\n1. Add task  2. List tasks  3. Quit")
        choice = input("Choose: ").strip()
        if choice == "1":
            task = input("Task: ").strip()
            if task:
                tasks.append(task)
                print("Task added.")
        elif choice == "2":
            if not tasks:
                print("No tasks yet.")
            for index, task in enumerate(tasks, 1):
                print(f"{index}. {task}")
        elif choice == "3":
            break
        else:
            print("Choose 1, 2, or 3.")

if __name__ == "__main__":
    main()
'''
    if any(word in text for word in ("hello", "greeting", "say hi")):
        return '''"""A friendly greeting program."""

def greet(name: str) -> str:
    """Return a greeting for name."""
    clean_name = name.strip() or "developer"
    return f"Hello, {clean_name}! Welcome to Aajimin Code Intelligence."

if __name__ == "__main__":
    print(greet(input("Your name: ")))
'''
    return ("I don't have an offline template for that request yet. Try calculator, task list, "
            "or greeting. The generator uses local templates, not a cloud model.")


def knowledge_search(query: str) -> list[dict[str, str]]:
    """Search the small built-in offline knowledge base."""
    entries = [
        {"topic": "syntax error", "keywords": "syntax indentation colon bracket quote parser",
         "answer": "Read the exact line and nearby lines. Check indentation, matching brackets, quotes, and colons. Run: python3 -m py_compile file.py"},
        {"topic": "virtual environment", "keywords": "venv virtual environment dependencies pip install",
         "answer": "Create one with: python3 -m venv .venv. Activate on Linux: source .venv/bin/activate. Install only trusted packages."},
        {"topic": "exceptions", "keywords": "try except error exception traceback",
         "answer": "Catch the narrowest exception you can handle. Avoid bare except; log useful context and preserve the original traceback when debugging."},
        {"topic": "file paths", "keywords": "path file folder pathlib directory",
         "answer": "Use pathlib.Path for cross-platform paths. Check existence and handle OSError when reading or writing files."},
        {"topic": "security", "keywords": "security eval exec input injection untrusted",
         "answer": "Do not pass untrusted strings to eval() or exec(). Validate input and prefer structured formats such as JSON for data."},
        {"topic": "unit tests", "keywords": "test unittest assert regression",
         "answer": "Use unittest from the standard library. Keep tests small, deterministic, and independent. Run: python3 -m unittest -v"},
        {"topic": "performance", "keywords": "slow performance profile optimize speed",
         "answer": "Measure before optimizing. Use cProfile for CPU profiling: python3 -m cProfile -s cumulative program.py. Prefer clear algorithms and suitable data structures."},
    ]
    terms = set(re.findall(r"[a-z0-9_]+", query.lower()))
    scored = []
    for item in entries:
        words = set(re.findall(r"[a-z0-9_]+", " ".join(item.values()).lower()))
        score = len(terms & words)
        if score:
            scored.append((score, item))
    return [item for _, item in sorted(scored, key=lambda pair: pair[0], reverse=True)]


def print_findings(findings: list[dict[str, object]]) -> None:
    if not findings:
        print("✓ No findings from the current rule set.")
        print("  A clean scan does not prove that code is bug-free.")
        return
    counts = {"ERROR": 0, "WARNING": 0, "INFO": 0}
    for item in findings:
        severity = str(item["severity"])
        counts[severity] = counts.get(severity, 0) + 1
        print(f"[{severity}] {item.get('file', '')}:{item['line']} · {item['rule']} — {item['message']}")
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
        elif command.lower() == "help":
            print("Commands:\n  analyze <file.py>  Analyze a Python file\n  scan <folder>      Scan a project\n  explain <file.py>  Explain file structure\n  generate <request> Generate from offline templates\n  knowledge <query>  Search offline Python notes\n  version            Show version\n  exit               Quit")
        elif command.lower() == "version":
            print(f"Aajimin Code Intelligence v{VERSION} · Python {sys.version.split()[0]}")
        elif command.lower().startswith("scan "):
            try:
                result = scan_project(Path(command[5:].strip().strip('"').strip("'")))
                print(json.dumps(result, indent=2))
            except ValueError as exc:
                print(f"Error: {exc}")
        elif command.lower().startswith("knowledge "):
            matches = knowledge_search(command[10:])
            for item in matches[:3]:
                print(f"\n{item['topic'].upper()}\n{item['answer']}")
            if not matches:
                print("No matching note. Try: syntax error, security, tests, performance.")
        elif command.lower().startswith("generate "):
            print(generate_code(command[9:]))
        else:
            match = re.match(r"^(analyze|explain)\s+(.+)$", command, re.I)
            if match:
                path = Path(match.group(2).strip().strip('"').strip("'"))
                try:
                    source = read_source(path)
                    print_findings(analyze_source(source, str(path))) if match.group(1).lower() == "analyze" else print(explain_source(source, str(path)))
                except ValueError as exc:
                    print(f"Error: {exc}")
            else:
                print("Unknown command. Type help to see available commands.")
        if command.lower() in {"exit", "quit"}:
            return


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="aajimin",
        description="Aajimin Code Intelligence — offline Python analysis with no API.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    sub = parser.add_subparsers(dest="command")
    analyze = sub.add_parser("analyze", help="analyze one Python file")
    analyze.add_argument("file", type=Path)
    analyze.add_argument("--format", choices=("text", "json"), default="text", help="report format")
    explain = sub.add_parser("explain", help="explain a Python file's structure")
    explain.add_argument("file", type=Path)
    scan = sub.add_parser("scan", help="scan a project folder recursively")
    scan.add_argument("path", type=Path, nargs="?", default=Path("."))
    scan.add_argument("--format", choices=("text", "json"), default="text", help="report format")
    scan.add_argument("--output", type=Path, help="write JSON report to a file")
    scan.add_argument("--include-hidden", action="store_true", help="include hidden folders (generated folders are always skipped)")
    generate = sub.add_parser("generate", help="generate code from offline templates")
    generate.add_argument("request", nargs="+")
    knowledge = sub.add_parser("knowledge", help="search the built-in offline knowledge base")
    knowledge.add_argument("query", nargs="+")
    args = parser.parse_args()

    if args.command is None:
        interactive()
        return 0
    if args.command == "analyze":
        try:
            source = read_source(args.file)
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 2
        findings = analyze_source(source, str(args.file))
        if args.format == "json":
            print(json.dumps({"file": str(args.file), "findings": findings,
                              "finding_count": len(findings)}, indent=2))
        else:
            print_findings(findings)
        return 1 if any(item["severity"] == "ERROR" for item in findings) else 0
    if args.command == "explain":
        try:
            print(explain_source(read_source(args.file), str(args.file)))
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 2
        return 0
    if args.command == "scan":
        try:
            result = scan_project(args.path, include_hidden=args.include_hidden)
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 2
        if args.output:
            args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
            print(f"JSON report written to {args.output}")
        elif args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            print(f"Aajimin Code Intelligence v{VERSION}")
            print(f"Scanned {result['files_scanned']} Python file(s) in {result['root']}")
            print(f"Findings: {result['summary']}")
            for item in result["files"]:
                if item["finding_count"]:
                    print(f"\n{item['file']}")
                    print_findings(item["findings"])
            if not result["findings_total"]:
                print("✓ No findings from the current rule set.")
        return 1 if result["summary"]["ERROR"] else 0
    if args.command == "generate":
        print(generate_code(" ".join(args.request)), end="")
        if not generate_code(" ".join(args.request)).endswith("\n"):
            print()
        return 0
    if args.command == "knowledge":
        matches = knowledge_search(" ".join(args.query))
        for item in matches[:5]:
            print(f"\n{item['topic'].upper()}\n{item['answer']}")
        if not matches:
            print("No matching note. Try syntax error, security, tests, paths, or performance.")
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
