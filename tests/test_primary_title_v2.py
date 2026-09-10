#!/usr/bin/env python3
"""Verify append-only title and orientation prompt versions."""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RULE = """━━━━━━━━━━━━━━━━━━
【V2｜主标题对象硬性规则】
━━━━━━━━━━━━━━━━━━

主标题优先级：

景点名 / 建筑名 > 城市名。

国家名禁止作为主标题。

国家名只能放在
小型副标题、邮戳或 Footer。

无法可靠识别具体城市、
建筑或景点时，
停止生成事实标题，
不能退化为国家名。
""".encode("utf-8")


class PrimaryTitleVersionTests(unittest.TestCase):
    def test_every_style_preserves_v2_and_uses_orientation_variants(self) -> None:
        registry = json.loads(
            (ROOT / "registry/prompt-version-registry.json").read_text(encoding="utf-8")
        )
        for record in registry["prompts"]:
            with self.subTest(prompt_id=record["prompt_id"]):
                if record["mode"] == "global":
                    self.assertEqual(record["active_version"], "v1")
                    self.assertNotIn("v2", record["versions"])
                    continue

                self.assertEqual(record["active_version"], "v3")
                self.assertEqual(
                    record["active_versions_by_orientation"],
                    {"portrait": "v3", "landscape": "v4"},
                )
                v1 = (ROOT / record["versions"]["v1"]["path"]).read_bytes()
                v2_info = record["versions"]["v2"]
                v2 = (ROOT / v2_info["path"]).read_bytes()
                self.assertEqual(v2, v1.rstrip(b"\n") + b"\n\n" + RULE)
                self.assertEqual(hashlib.sha256(v2).hexdigest(), v2_info["sha256"])
                self.assertTrue(v2_info["immutable"])
                self.assertEqual(v2_info["status"], "verified_source")

                for version_id, orientation, dimensions in (
                    ("v3", "竖版", "1024 × 1536 px"),
                    ("v4", "横版", "1536 × 1024 px"),
                ):
                    info = record["versions"][version_id]
                    content = (ROOT / info["path"]).read_bytes()
                    self.assertTrue(content.startswith(v2.rstrip(b"\n") + b"\n\n"))
                    decoded = content.decode("utf-8")
                    self.assertIn("禁止仅凭建筑风格", decoded)
                    self.assertIn("整体候选池内随机选取", decoded)
                    self.assertIn(orientation, decoded)
                    self.assertIn(dimensions, decoded)
                    self.assertEqual(hashlib.sha256(content).hexdigest(), info["sha256"])
                    self.assertTrue(info["immutable"])
                    self.assertEqual(info["status"], "verified_source")


if __name__ == "__main__":
    unittest.main()
