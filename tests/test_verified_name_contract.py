#!/usr/bin/env python3
"""Contract tests for evidence-bound primary-title selection."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(relative_path: str) -> dict:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


class VerifiedNameContractTests(unittest.TestCase):
    def test_image_analysis_requires_verified_name_candidates(self) -> None:
        schema = load_json("schemas/image-analysis.schema.json")
        self.assertIn("verified_name_candidates", schema["required"])
        candidate = schema["properties"]["verified_name_candidates"]["items"]
        properties = candidate["properties"]
        self.assertEqual(properties["confidence"]["minimum"], 0.9)
        self.assertEqual(properties["country_only"], {"const": False})
        self.assertEqual(properties["primary_title_eligible"], {"const": True})
        self.assertNotIn("architectural_style_inference", properties["source_type"]["enum"])

    def test_fusion_randomizes_only_inside_verified_pool(self) -> None:
        schema = load_json("schemas/fusion-plan.schema.json")
        self.assertIn("verified_name_pool", schema["required"])
        self.assertIn("primary_title_selection", schema["required"])
        strategy = schema["properties"]["primary_title_selection"]["properties"]["strategy"]
        self.assertEqual(strategy, {"const": "RANDOM_FROM_VERIFIED_NAME_POOL"})

        router = load_json("router/multi-router.json")
        title = router["title_selection"]
        self.assertEqual(title["strategy"], "RANDOM_FROM_UNION_VERIFIED_NAME_POOL")
        self.assertEqual(title["randomization_scope"], "PRIMARY_TITLE_ONLY")
        self.assertFalse(title["allow_country_primary_title"])
        self.assertFalse(title["allow_outside_pool"])
        self.assertEqual(
            router["precheck"]["empty_verified_name_pool"]["result"],
            "BLOCKED_UNVERIFIED_PRIMARY_TITLE",
        )


if __name__ == "__main__":
    unittest.main()
