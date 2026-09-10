#!/usr/bin/env python3
"""Verify that generation receives source prompts verbatim, never as summaries."""

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


class GenerationPayloadTests(unittest.TestCase):
    def run_script(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        self.assertTrue(SCRIPT.is_file(), "原文直传脚本尚未实现")
        return subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_selected_style_is_the_entire_payload_and_tampering_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temp = Path(temporary_directory)
            payload = temp / "generation-payload.txt"
            manifest_path = temp / "generation-payload.manifest.json"

            result = self.run_script(
                "--style-id",
                "MULTI_STYLE_03",
                "--orientation",
                "portrait",
                "--output",
                str(payload),
                "--manifest",
                str(manifest_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            payload_bytes = payload.read_bytes()
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["style_id"], "MULTI_STYLE_03")
            self.assertEqual(manifest["orientation"], "portrait")
            self.assertEqual(manifest["style_source_prompt"]["version"], "v3")
            self.assertEqual(
                hashlib.sha256(payload_bytes).hexdigest(), manifest["payload_sha256"]
            )
            self.assertEqual(
                manifest["generation_input_policy"],
                "STYLE_SOURCE_PROMPT_ONLY_VERBATIM",
            )
            section = manifest["style_source_prompt"]
            exact_source = (ROOT / section["path"]).read_bytes()
            self.assertEqual(payload_bytes, exact_source)
            self.assertEqual(hashlib.sha256(payload_bytes).hexdigest(), section["sha256"])
            self.assertNotIn("global_source_prompt", manifest)
            self.assertNotIn("runtime_input", manifest)

            verify = self.run_script(
                "--verify-only",
                "--payload",
                str(payload),
                "--manifest",
                str(manifest_path),
            )
            self.assertEqual(verify.returncode, 0, verify.stderr)

            payload.write_bytes(payload_bytes + b"\nSTYLE SUMMARY DRIFT")
            tampered = self.run_script(
                "--verify-only",
                "--payload",
                str(payload),
                "--manifest",
                str(manifest_path),
            )
            self.assertNotEqual(tampered.returncode, 0)
            self.assertIn("FAILED", tampered.stderr)

    def test_composition_requires_orientation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temp = Path(temporary_directory)
            result = self.run_script(
                "--style-id",
                "STYLE_03",
                "--output",
                str(temp / "prompt.txt"),
                "--manifest",
                str(temp / "manifest.json"),
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--orientation", result.stderr)


if __name__ == "__main__":
    unittest.main()
