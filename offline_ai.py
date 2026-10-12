#!/usr/bin/env python3
"""Run a real language model locally from a GGUF file. No API or network calls."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SYSTEM_PROMPT = (
    "You are Aajimin, a helpful offline AI coding assistant created by Aajimin (AJ-8A). "
    "Answer clearly and accurately. For coding tasks, provide working code and explain how to run it. "
    "If unsure, say so. Never claim you ran code unless you actually did."
)


def build_prompt(history: list[dict[str, str]], user_text: str) -> str:
    """Format chat history using a simple instruction-tuned chat template."""
    chunks = [f"<|system|>\n{SYSTEM_PROMPT}\n"]
    for message in history:
        role = "user" if message["role"] == "user" else "assistant"
        chunks.append(f"<|{role}|>\n{message['content']}\n")
    chunks.append(f"<|user|>\n{user_text}\n<|assistant|>\n")
    return "".join(chunks)


def load_model(model_path: Path, context: int, threads: int):
    """Load a local GGUF model using the optional llama-cpp-python runtime."""
    if not model_path.is_file():
        raise FileNotFoundError(
            f"Model file not found: {model_path}\n"
            "Download a GGUF model separately and pass its path with --model. "
            "This program never downloads models or contacts an API."
        )
    try:
        from llama_cpp import Llama
    except ImportError:
        raise RuntimeError(
            "The local model runtime is not installed. Install it with:\n"
            "  python3 -m pip install llama-cpp-python\n"
            "Then run again. Model inference remains on this computer."
        ) from None
    return Llama(
        model_path=str(model_path),
        n_ctx=context,
        n_threads=max(1, threads),
        verbose=False,
    )


def chat(model_path: Path, context: int = 4096, threads: int = 4) -> int:
    """Start a terminal conversation with the local model."""
    try:
        model = load_model(model_path, context, threads)
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"Setup error: {exc}", file=sys.stderr)
        return 2

    print("\nAajimin Offline AI")
    print(f"Model: {model_path}")
    print("Local inference only • type /exit to quit • /clear to reset chat\n")
    history: list[dict[str, str]] = []
    while True:
        try:
            user_text = input("You > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSession ended.")
            return 0
        if not user_text:
            continue
        if user_text.lower() in {"/exit", "/quit"}:
            print("Bye.")
            return 0
        if user_text.lower() == "/clear":
            history.clear()
            print("Conversation cleared.\n")
            continue

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(history[-12:])
        messages.append({"role": "user", "content": user_text})
        try:
            result = model.create_chat_completion(
                messages=messages,
                max_tokens=1024,
                temperature=0.7,
                top_p=0.9,
            )
            answer = result["choices"][0]["message"]["content"].strip()
        except Exception as exc:
            print(f"Generation error: {exc}", file=sys.stderr)
            continue
        if not answer:
            answer = "(The model returned an empty response. Try rephrasing.)"
        print(f"\nAajimin > {answer}\n")
        history.extend(({"role": "user", "content": user_text},
                        {"role": "assistant", "content": answer}))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Chat with a language model stored on your computer. No API, no cloud."
    )
    parser.add_argument("--model", type=Path, required=True, help="path to a local .gguf model file")
    parser.add_argument("--context", type=int, default=4096, help="context window (default: 4096)")
    parser.add_argument("--threads", type=int, default=4, help="CPU threads to use (default: 4)")
    args = parser.parse_args()
    if args.context < 512:
        parser.error("--context must be at least 512")
    if args.threads < 1:
        parser.error("--threads must be at least 1")
    return chat(args.model.expanduser(), args.context, args.threads)


if __name__ == "__main__":
    raise SystemExit(main())
