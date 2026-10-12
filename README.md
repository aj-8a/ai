# ⚡ Aajimin Code Intelligence

> **Offline Python developer assistant. No API keys. No cloud AI. No external dependencies.**

**Aajimin Code Intelligence** is a local-first coding utility by **Aajimin (AJ-8A)**. It combines Python's syntax tree, deterministic rules, and small built-in templates to help developers inspect code and catch common issues.

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
| **Code analysis** | Parses Python source and reports syntax errors and selected code-quality/security patterns. |
| **Code explanation** | Summarizes imports, assignments, functions, classes, methods, and line count. |
| **Offline code templates** | Generates starter programs for common requests such as a calculator, task list, and greeting. |
| **Interactive shell** | Explore commands from a simple terminal prompt. |
| **Privacy-first design** | Source files are read locally; the tool does not upload code or call external services. |
| **Zero dependencies** | Built with the Python standard library. |

## 🚀 Quick start

### Requirements

- Python 3.10 or newer
- A terminal (Linux, ChromeOS Linux, macOS, or Windows)
- No package installation required

### Run the assistant

```bash
git clone https://github.com/AJ-8A/ai.git
cd ai
python3 aajimin.py
```

### Analyze a file

```bash
python3 aajimin.py analyze path/to/program.py
```

### Explain a file

```bash
python3 aajimin.py explain path/to/program.py
```

### Generate a starter program

```bash
python3 aajimin.py generate calculator
python3 aajimin.py generate todo-list
python3 aajimin.py generate greeting
```

### Check the version

```bash
python3 aajimin.py --version
```

## 🧭 Interactive commands

Start with `python3 aajimin.py`, then type:

| Command | Purpose |
| --- | --- |
| `help` | Show available commands |
| `analyze app.py` | Inspect a Python file |
| `explain app.py` | Summarize the code structure |
| `generate calculator` | Print a starter calculator |
| `version` | Show version details |
| `exit` | Close the tool |

## 🔍 Rule IDs

The analyzer reports findings with stable rule IDs to make future testing and documentation easier.

| Rule | Meaning |
| --- | --- |
| `PY001` | Python syntax error |
| `PY101` | Comparison with `None` using `==` |
| `PY102` | Bare `except` clause |
| `SEC001` | Use of `eval()` |
| `SEC002` | Use of `exec()` |
| `STYLE001` | Trailing whitespace |
| `STYLE002` | Line longer than 100 characters |
| `STYLE003` | Tabs used for indentation |
| `DOC001` | Public function without a docstring |

The rules are intentionally conservative. A finding is a prompt to review code, not proof of a defect; a clean report does not guarantee that code is correct or secure.

## 🧠 How the offline engine works

1. **Parse:** Python's built-in `ast` module builds a syntax tree.
2. **Inspect:** deterministic rules inspect selected syntax and source formatting.
3. **Explain:** syntax-tree nodes are summarized into a readable outline.
4. **Generate:** small, explicit templates return starter programs for supported requests.
5. **Report:** findings include severity, line, rule ID, explanation, and a suggested next step.

### An honest note about “AI”

This first version is an **offline, rule-based coding assistant**, not a large language model. It does not have ChatGPT-level open-ended reasoning, and its code generator only supports the templates documented above. That limitation is deliberate: the project stays transparent, reproducible, and completely API-free.

## 🔐 Privacy and safety

- No API keys or account credentials are needed.
- No network requests are made by the application.
- Files are read from your local machine.
- The analyzer does not execute the code it scans.
- Review generated code before running it.
- Static analysis cannot guarantee security or correctness.

## 🗺️ Roadmap

- [x] Offline command-line interface
- [x] Python syntax error reporting
- [x] Rule-based code-quality checks
- [x] Structural code explanation
- [x] Starter-code templates
- [ ] Unit tests and continuous integration
- [ ] More Python lint and security rules
- [ ] Project-wide scan with exclusions
- [ ] JSON report output
- [ ] Local searchable documentation and examples
- [ ] Optional desktop interface

## 🧑‍💻 Development

The project intentionally avoids third-party packages. Run the built-in help to see the supported commands:

```bash
python3 aajimin.py --help
```

Contributions and bug reports are welcome. Please include a minimal example, the command you ran, and the expected versus actual result.

## 👑 Author

**Aajimin (AJ-8A)**

- GitHub: [@AJ-8A](https://github.com/AJ-8A)
- Project: [Aajimin Code Intelligence](https://github.com/AJ-8A/ai)

---

<p align="center">
  <strong>Built by Aajimin · Offline by design · Powered by Python</strong><br>
  <sub>No API. No cloud dependency. Just code.</sub>
</p>
