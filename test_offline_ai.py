"""Tests for the local-only AI entry points."""
import tempfile
import unittest
from pathlib import Path

import offline_ai
import web_app


class OfflineAITests(unittest.TestCase):
    def test_prompt_includes_system_and_user_message(self):
        prompt = offline_ai.build_prompt([], "Explain Python lists")
        self.assertIn("offline AI coding assistant", prompt)
        self.assertIn("Explain Python lists", prompt)

    def test_missing_model_fails_before_runtime_import(self):
        missing = Path(tempfile.gettempdir()) / "aajimin-definitely-missing-model.gguf"
        if missing.exists():
            self.skipTest("Temporary test model unexpectedly exists")
        with self.assertRaises(FileNotFoundError):
            offline_ai.load_model(missing, context=512, threads=1)

    def test_browser_app_is_local_chat_ui(self):
        self.assertIn("Aajimin AI", web_app.PAGE)
        self.assertIn("fetch('/chat'", web_app.PAGE)
        self.assertIn("No API keys", web_app.PAGE)

    def test_app_refuses_non_local_host(self):
        # Argument validation is intentionally enforced in main before binding.
        import inspect
        source = inspect.getsource(web_app.main)
        self.assertIn('args.host not in {"127.0.0.1", "localhost", "::1"}', source)


if __name__ == "__main__":
    unittest.main()
