# ⚡ Aajimin Code Intelligence

> **Offline Python developer assistant — no API keys, no cloud AI, no external dependencies.**

Aajimin Code Intelligence is a local-first coding utility by **Aajimin (AJ-8A)**. It combines Python's syntax tree, deterministic analysis rules, and a small built-in knowledge base to help developers inspect code and catch common issues.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/API-None-22C55E?style=for-the-badge" alt="No API">
  <img src="https://img.shields.io/badge/Dependencies-Standard%20Library-8B5CF6?style=for-the-badge" alt="Standard library only">
  <img src="https://img.shields.io/badge/Mode-Offline-0EA5E9?style=for-the-badge" alt="Offline">
</p>

---

## ✨ Features

| Feature | What it does |
| --- | --- |
| **Single-file analysis** | Detects syntax errors and selected security, style, and maintainability patterns. |
| **Project scanner** | Recursively scans Python files and skips common generated folders such as `.git`, `.venv`, `build`, and `dist`. |
| **JSON reports** | Print machine-readable reports or save project scan output to a JSON file. |
| **Code explanation** | Summarizes imports, assignments, functions, classes, methods, and line count. |
| **Offline knowledge search** | Searches built-in notes about syntax errors, testing, exceptions, security, paths, and performance. |
| **Starter-code generator** | Generates template programs for a calculator, task list, and greeting. |
| **Interactive shell** | Explore commands from a terminal prompt. |
| **Privacy-first** | Source files are read locally; the tool makes no network requests. |

## 🚀 Quick start

Requirements: Python 3.10+ and a terminal. No package installation is needed.

```bash
git clone https://github.com/AJ-8A/ai.git
cd ai
python3 aajimin.py
```

## 🧰 Commands

### Scan a complete project

```bash
python3 aajimin.py scan .
python3 aajimin.py scan ~/my-project
``

By default, the scanner skips common generated directories and hidden paths. It does not execute the files it inspects.

### Export a JSON report

```bash
# Print JSON to the terminal
python3 aajimin.py scan . --format json

# Save the report
python3 aajimin.py scan . --output report.json
``

The report contains the tool version, scan root, number of files, finding totals, severity counts, and findings grouped by file.

### Analyze one file

```bash
python3 aajimin.py analyze aajimin.py
python3 aajimin.py analyze aajimin.py --format json
``

### Explain code structure

```bash
python3 aajimin.py explain aajimin.py
``

### Search offline developer notes

```bash
python3 aajimin.py knowledge syntax error
python3 aajimin.py knowledge security eval
python3 aajimin.py knowledge unit tests
python3 aajimin.py knowledge performance
``

### Generate a starter program

```bash
python3 aajimin.py generate calculator
python3 aajimin.py generate todo-list
python3 aajimin.py generate greeting
``

### Run tests

```bash
python3 -m unittest -v
``

GitHub Actions also runs compilation and unit tests on pushes and pull requests across Python 3.10–3.13.

## 🔍 Current analysis rules

| Rule | Meaning |
| --- | --- |
| `PY001` | Python syntax error |
| `PY101` | Comparison with `None` using equality operators |
| `PY102` | Bare `except` clause |
| `PY105` | Mutable list, dict, or set default argument |
| `PY106` | Unconditional `assert False` |
| `SEC001` | Use of `eval()` |
| `SEC002` | Use of `exec()` |
| `STYLE001` | Trailing whitespace |
| `STYLE002` | Line longer than 100 characters |
| `STYLE003` | Tabs used for indentation |
| `DOC001` | Public function without a docstring |

Rules are intentionally conservative. A finding is a prompt to review code, not proof of a defect. A clean scan does not guarantee that code is correct or secure.

## 🧠 How the offline engine works

1. **Parse:** Python's built-in `ast` module creates a syntax tree.
2. **Inspect:** deterministic rules examine selected syntax and source formatting.
3. **Explain:** syntax-tree nodes are summarized into a readable outline.
4. **Search:** a local knowledge base ranks notes by matching query terms.
5. **Generate:** explicit code templates provide starter programs for supported requests.
6. **Report:** findings include severity, line, rule ID, message, and suggestion.

### An honest note about “AI”

This version is an **offline, rule-based coding assistant**, not a large language model. It does not have ChatGPT-level open-ended reasoning. Its knowledge search and code generator work only with bundled notes and documented templates. That is how the core stays API-free, reproducible, and private.

## 🔐 Privacy and safety

- No API keys or account credentials are needed.
- The application makes no network requests.
- Source files are not uploaded.
- The analyzer does not execute inspected code.
- Review generated code before running it.
- Static analysis cannot guarantee security or correctness.
- Scan only folders you have permission to inspect.

## 🗺️ Roadmap

- [x] Offline command-line interface
- [x] Python syntax and selected code-quality checks
- [x] Project-wide recursive scan
- [x] JSON output and report files
- [x] Local developer knowledge search
- [x] Starter-code templates
- [x] Unit tests and GitHub Actions
- [ ] More analysis rules and configurable exclusions
- [ ] Better cross-file project insights
- [ ] Optional graphical interface
- [ ] Optional local-model integration (never required)

## 👑 Author

**Aajimin (AJ-8A)**

- GitHub profile: [@AJ-8A](https://github.com/AJ-8A)
- Repository: [Aajimin Code Intelligence](https://github.com/AJ-8A/ai)

---

<p align="center">
  <strong>Built by Aajimin · Offline by design · Powered by Python</strong><br>
  <sub>No API. No cloud dependency. Just code.</sub>
</p>
