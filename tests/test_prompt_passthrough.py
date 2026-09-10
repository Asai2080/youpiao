#!/usr/bin/env python3
"""Regression test: image generation receives only the selected source prompt."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "compose_generation_payload.py"


class PromptPassthroughTests(unittest.TestCase):
    def test_payload_equals_selected_style_source_byte_for_byte(self) -> None:
        self.assertTrue(SCRIPT.is_file(), "当前运行 Skill 尚未安装原文直传器")
        with tempfile.TemporaryDirectory() as temporary_directory:
            temp = Path(temporary_directory)
            payload = temp / "prompt.txt"
            manifest_path = temp / "prompt.manifest.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--style-id",
                    "MULTI_STYLE_03",
                    "--orientation",
                    "landscape",
                    "--output",
                    str(payload),
                    "--manifest",
                    str(manifest_path),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            expected = (ROOT / "prompts/multi/multi_style_03/prompt_v4.md").read_bytes()
            actual = payload.read_bytes()
            self.assertEqual(actual, expected)

            global_prompt = (ROOT / "prompts/global/global_negative/prompt_v1.md").read_bytes()
            self.assertNotIn(global_prompt, actual)

            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(
                manifest["generation_input_policy"],
                "STYLE_SOURCE_PROMPT_ONLY_VERBATIM",
            )
            self.assertEqual(manifest["payload_sha256"], hashlib.sha256(expected).hexdigest())
            self.assertEqual(manifest["orientation"], "landscape")
            self.assertEqual(
                manifest["output_contract"],
                {"ratio": "3:2", "width": 1536, "height": 1024},
            )
            self.assertEqual(manifest["style_source_prompt"]["version"], "v4")


if __name__ == "__main__":
    unittest.main()
