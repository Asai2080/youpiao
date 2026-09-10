#!/usr/bin/env python3
"""Lock every user-authored source prompt to its authoritative byte hash."""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_SOURCES = {
    "global.negative": ("prompts/global/global_negative/prompt_v1.md", "bba96a464f766129549a684efc85c286a9bd857c67d4fc3fb5621aff4fb610ff"),
    "single.style_01": ("prompts/single/style_01/prompt_v1.md", "66ada858878e4ae99463b757c0228932565ebe22d09a5a209da838ace4af2732"),
    "single.style_02": ("prompts/single/style_02/prompt_v1.md", "57b24bc43e9daec6a5293596f3f2d133e8ba3e2364cc88bf2ff1888d5325056c"),
    "single.style_03": ("prompts/single/style_03/prompt_v1.md", "ffb93ff697d4e80f0df5adca1b93bab30083d0f91c1b5b1327f3421b4c7b1a6f"),
    "single.style_04": ("prompts/single/style_04/prompt_v1.md", "8317252acd102e7687a85fe205cf62412ad921e1756a46890eb75d42aa3d5da2"),
    "single.style_05": ("prompts/single/style_05/prompt_v1.md", "bec5b89c7b52f0b0936d7dd311c99dfa7b59a4f858509b5a0a85af6e552e4bd4"),
    "single.style_06": ("prompts/single/style_06/prompt_v1.md", "05a8fafff18c67c474b73329fd9eae6887435e65d95836dab7366901801b2963"),
    "single.style_07": ("prompts/single/style_07/prompt_v1.md", "68d708949ca1496498925dd5132807fc4382e877d9a299587a1fb69ba3fc644e"),
    "multi.multi_style_01": ("prompts/multi/multi_style_01/prompt_v1.md", "8e5c186be6f79434333ada473b3cadd7b51fcab756b15a5378da011d3d816b07"),
    "multi.multi_style_02": ("prompts/multi/multi_style_02/prompt_v1.md", "98aca20154963357806cdc28a7153c53f08e2f10124334342bfb3e676f604974"),
    "multi.multi_style_03": ("prompts/multi/multi_style_03/prompt_v1.md", "831070ab07bd9b694e620b373fe298d041051c63b610f324706caa82b8a49970"),
    "multi.multi_style_04": ("prompts/multi/multi_style_04/prompt_v1.md", "b7880f6f3e0459e3b95a4956f2cfcaad252b454f326056b652d423f725385d54"),
    "multi.multi_style_05": ("prompts/multi/multi_style_05/prompt_v1.md", "9c9bdeaff555b6829022df307461330cdedb3e359e8f1a3a2ca107d543a268db"),
    "multi.multi_style_06": ("prompts/multi/multi_style_06/prompt_v1.md", "cef96f2aa0091924ee3ca0a11d3dfc7fb523e4b7dcbf5f19a032597878d99e64"),
}


class AuthoritativePromptSourceTests(unittest.TestCase):
    def test_registry_and_files_match_all_authoritative_sources(self) -> None:
        registry = json.loads(
            (ROOT / "registry/prompt-version-registry.json").read_text(encoding="utf-8")
        )
        records = {record["prompt_id"]: record for record in registry["prompts"]}
        self.assertEqual(set(records), set(EXPECTED_SOURCES))

        for prompt_id, (relative_path, expected_hash) in EXPECTED_SOURCES.items():
            with self.subTest(prompt_id=prompt_id):
                record = records[prompt_id]
                version = record["versions"]["v1"]
                self.assertEqual(version["path"], relative_path)
                self.assertEqual(version["status"], "verified_source")
                self.assertTrue(version["immutable"])
                self.assertEqual(version["sha256"], expected_hash)
                actual_hash = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
                self.assertEqual(actual_hash, expected_hash)

                expected_active = "v1" if prompt_id == "global.negative" else "v3"
                self.assertEqual(record["active_version"], expected_active)
                if prompt_id != "global.negative":
                    self.assertEqual(
                        record["active_versions_by_orientation"],
                        {"portrait": "v3", "landscape": "v4"},
                    )


if __name__ == "__main__":
    unittest.main()
