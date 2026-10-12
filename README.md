# ⚡ Aajimin AI — Offline Local Assistant

**This repository contains runnable AI code, not just documentation.** Aajimin AI can load a language model stored on your computer and chat with it locally. It does not need an API key, a cloud account, or an internet connection during inference.

<p align="center">
  <img src="https://img.shields.io/badge/AI-Local%20Inference-7C3AED?style=for-the-badge" alt="Local inference">
  <img src="https://img.shields.io/badge/API-None-16A34A?style=for-the-badge" alt="No API">
  <img src="https://img.shields.io/badge/Model-GGUF-0EA5E9?style=for-the-badge" alt="GGUF model">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+">
</p>

## What it actually does

- **Local AI chat:** runs a GGUF language model on your own CPU (and supported acceleration where your runtime is built for it).
- **Conversation memory:** keeps recent turns in the current terminal session; `/clear` resets them.
- **Code intelligence:** analyzes Python source using the Python AST and checks for selected bugs and risky patterns.
- **Project scan:** recursively scans a Python project and can export a JSON report.
- **Offline developer tools:** explain code structure and search bundled programming notes.
- **Privacy:** prompts and inspected source are passed to the local model/process only; this code makes no API calls and does not download a model.

> **Important:** Python code alone is not a trained language model. For real generative AI, you must provide a compatible local `.gguf` model file and install the optional inference runtime once. After setup, chatting can work offline. The model file is not included in this repository because model files are large and each model has its own license.

## Start the actual offline AI

### 1. Get the code

```bash
git clone https://github.com/AJ-8A/ai.git
cd ai
```

### 2. Install the local inference runtime

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install llama-cpp-python
```

This installs a local inference library, **not an API client**. The first installation needs internet access unless you already have the package available. Some systems may need build tools; GPU acceleration depends on how the library is built.

### 3. Get a GGUF model

Choose an instruction/chat-tuned **GGUF** model from a reputable model publisher, read its license, and download the model file yourself. Start with a smaller quantized model if your computer has limited RAM. The model is separate from this repository and can be kept on your computer.

### 4. Run it

Replace the example path with the actual path to your downloaded model:

```bash
python3 offline_ai.py --model ~/models/your-instruct-model.gguf
```

Inside the chat:
- Type a question or ask it to write/debug code.
- Type `/clear` to reset the conversation.
- Type `/exit` to quit.

Optional settings:

```bash
python3 offline_ai.py --model ~/models/your-instruct-model.gguf --context 2048 --threads 4
```

If you see “model file not found”, check the path. If you see “runtime is not installed”, install `llama-cpp-python` in the same Python environment. If the model is too large for available memory, choose a smaller quantized model or lower the context size.

## Python code scanner (no extra packages)

The scanner works independently from the language model:

```bash
python3 aajimin.py analyze your_file.py
python3 aajimin.py scan .
python3 aajimin.py scan . --output report.json
python3 aajimin.py explain your_file.py
python3 aajimin.py knowledge security
python3 -m unittest -v
```

The scanner does not execute inspected files. Its findings are rule-based checks, not a guarantee that code is safe or bug-free.

## Project files

| File | Purpose |
| --- | --- |
| `offline_ai.py` | Actual local LLM chat using a GGUF model |
| `aajimin.py` | Offline Python analyzer, scanner, and developer CLI |
| `test_aajimin.py` | Unit tests for the scanner and code tools |
| `.github/workflows/python.yml` | Automated Python checks |

## Privacy and limitations

- No OpenAI, Gemini, or other hosted AI API is used.
- No model is downloaded automatically.
- The inference process runs on your computer; network access is not needed once the model and runtime are installed.
- Response quality and speed depend on the chosen model and hardware.
- This project does not claim to train a new foundation model; it runs an existing local model.

Made by **Aajimin (AJ-8A)**.
