#!/usr/bin/env python3
"""Contract tests for selectable portrait and landscape output policies."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(relative_path: str) -> dict:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


class OrientationOutputContractTests(unittest.TestCase):
    def test_session_schema_offers_only_two_orientation_contracts(self) -> None:
        schema = load_json("schemas/session.schema.json")
        properties = schema["properties"]
        self.assertEqual(
            properties["orientation"]["enum"], ["portrait", "landscape", None]
        )
        self.assertEqual(properties["output_ratio"]["enum"], ["2:3", "3:2", None])
        pending = properties["pending_questions"]["items"]["enum"]
        self.assertIn("output_orientation", pending)
        self.assertNotIn("output_ratio", pending)

    def test_generation_schema_requires_exact_dimensions_for_each_orientation(self) -> None:
        schema = load_json("schemas/generation-spec.schema.json")
        output = schema["properties"]["output"]
        self.assertIn("orientation", output["required"])
        self.assertIn("width", output["required"])
        self.assertIn("height", output["required"])
        contracts = output["allOf"]
        portrait = contracts[0]["then"]["properties"]
        landscape = contracts[1]["then"]["properties"]
        self.assertEqual(
            portrait,
            {
                "ratio": {"const": "2:3"},
                "width": {"const": 1024},
                "height": {"const": 1536},
            },
        )
        self.assertEqual(
            landscape,
            {
                "ratio": {"const": "3:2"},
                "width": {"const": 1536},
                "height": {"const": 1024},
            },
        )

    def test_examples_cover_portrait_and_landscape(self) -> None:
        portrait = load_json("examples/single/session.json")
        self.assertEqual(
            (
                portrait["orientation"],
                portrait["output_ratio"],
                portrait["output_width"],
                portrait["output_height"],
            ),
            ("portrait", "2:3", 1024, 1536),
        )
        landscape = load_json("examples/multi-independent/session.json")
        self.assertEqual(
            (
                landscape["orientation"],
                landscape["output_ratio"],
                landscape["output_width"],
                landscape["output_height"],
            ),
            ("landscape", "3:2", 1536, 1024),
        )


if __name__ == "__main__":
    unittest.main()
