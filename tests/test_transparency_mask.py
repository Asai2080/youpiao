#!/usr/bin/env python3
"""Regression tests for deterministic transparent-background delivery."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "apply_transparency_mask.py"


class TransparencyMaskTests(unittest.TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        self.assertTrue(SCRIPT.is_file(), "透明背景处理脚本尚未实现")
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_checkerboard_is_removed_and_perforations_stay_transparent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temp = Path(temporary_directory)
            source = temp / "checkerboard.png"
            output = temp / "transparent.png"

            image = Image.new("RGB", (96, 72))
            draw = ImageDraw.Draw(image)
            for y in range(0, 72, 8):
                for x in range(0, 96, 8):
                    shade = 176 if (x // 8 + y // 8) % 2 == 0 else 214
                    draw.rectangle((x, y, x + 7, y + 7), fill=(shade, shade, shade))

            draw.rounded_rectangle((12, 10, 83, 61), radius=4, fill=(236, 218, 171))
            draw.rectangle((18, 16, 77, 55), fill=(31, 90, 96))
            draw.ellipse((43, 4, 53, 14), fill=(176, 176, 176))
            image.save(source)

            result = self.run_script("--expected-size", "96x72", str(source), str(output))
            self.assertEqual(result.returncode, 0, result.stderr)

            with Image.open(output) as processed:
                self.assertEqual(processed.mode, "RGBA")
                self.assertEqual(processed.size, image.size)
                alpha = processed.getchannel("A")
                self.assertEqual(alpha.getpixel((0, 0)), 0)
                self.assertEqual(alpha.getpixel((95, 71)), 0)
                self.assertEqual(alpha.getpixel((48, 9)), 0)
                self.assertEqual(alpha.getpixel((48, 36)), 255)
                self.assertEqual(alpha.getextrema(), (0, 255))

            verify = self.run_script("--verify-only", "--expected-size", "96x72", str(output))
            self.assertEqual(verify.returncode, 0, verify.stderr)

    def test_dark_textured_matte_is_removed_even_when_teeth_touch_edges(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temp = Path(temporary_directory)
            source = temp / "dark-matte.png"
            output = temp / "transparent.png"

            image = Image.new("RGB", (96, 144))
            pixels = image.load()
            for y in range(144):
                for x in range(96):
                    texture = (x * 3 + y * 5) % 17
                    pixels[x, y] = (44 + texture, 42 + texture, 36 + texture)

            draw = ImageDraw.Draw(image)
            paper = (232, 199, 126)
            draw.rectangle((6, 6, 89, 137), fill=paper)
            # A few perforation peaks touch the source canvas and deliberately
            # contaminate the wider border sample with saturated paper color.
            draw.rectangle((20, 0, 24, 8), fill=paper)
            draw.rectangle((70, 0, 74, 8), fill=paper)
            draw.rectangle((20, 135, 24, 143), fill=paper)
            draw.rectangle((70, 135, 74, 143), fill=paper)
            draw.rectangle((15, 14, 80, 128), fill=(31, 90, 96))
            image.save(source)

            result = self.run_script(
                "--expected-size", "96x144", str(source), str(output)
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            with Image.open(output) as processed:
                self.assertEqual(processed.mode, "RGBA")
                self.assertEqual(processed.size, image.size)
                alpha = processed.getchannel("A")
                self.assertEqual(alpha.getpixel((0, 0)), 0)
                self.assertEqual(alpha.getpixel((95, 143)), 0)
                self.assertEqual(alpha.getpixel((48, 72)), 255)
                self.assertEqual(alpha.getextrema(), (0, 255))

    def test_verify_only_rejects_fully_opaque_png(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            source = Path(temporary_directory) / "opaque.png"
            Image.new("RGB", (32, 24), (20, 80, 90)).save(source)

            result = self.run_script("--verify-only", str(source))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("FAILED", result.stderr)

    def test_valid_rgba_input_is_preserved_without_relearning_background(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temp = Path(temporary_directory)
            source = temp / "already-transparent.png"
            output = temp / "copied-transparent.png"
            image = Image.new("RGBA", (40, 30), (255, 0, 255, 0))
            ImageDraw.Draw(image).rectangle((5, 5, 34, 24), fill=(220, 180, 80, 255))
            image.save(source)

            result = self.run_script("--expected-size", "40x30", str(source), str(output))
            self.assertEqual(result.returncode, 0, result.stderr)
            with Image.open(output) as processed:
                self.assertEqual(processed.mode, "RGBA")
                self.assertEqual(processed.getpixel((0, 0)), (0, 0, 0, 0))
                self.assertEqual(processed.getpixel((20, 15)), (220, 180, 80, 255))

    def test_dark_matte_does_not_leak_into_neutral_stamp_paper(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temp = Path(temporary_directory)
            source = temp / "dark-matte-neutral-paper.png"
            output = temp / "transparent.png"

            image = Image.new("RGB", (120, 80), (43, 43, 43))
            draw = ImageDraw.Draw(image)
            draw.rounded_rectangle((8, 7, 111, 72), radius=5, fill=(226, 222, 211))
            draw.rectangle((18, 16, 101, 63), fill=(32, 72, 70))
            image.save(source)

            result = self.run_script(
                "--expected-size", "120x80", str(source), str(output)
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            with Image.open(output) as processed:
                alpha = processed.getchannel("A")
                self.assertEqual(alpha.getpixel((0, 0)), 0)
                self.assertEqual(alpha.getpixel((60, 40)), 255)
                center = alpha.crop((30, 20, 90, 60))
                self.assertNotIn(0, center.tobytes())

    def test_verify_only_rejects_hidden_checker_rgb_under_alpha_zero(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            source = Path(temporary_directory) / "hidden-checker.png"
            image = Image.new("RGBA", (40, 30), (176, 176, 176, 0))
            ImageDraw.Draw(image).rectangle((5, 5, 34, 24), fill=(220, 180, 80, 255))
            image.save(source)

            result = self.run_script(
                "--verify-only", "--expected-size", "40x30", str(source)
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("hidden RGB", result.stderr)

    def test_verify_only_rejects_alpha_leak_inside_stamp(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            source = Path(temporary_directory) / "interior-leak.png"
            image = Image.new("RGBA", (40, 30), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            draw.rectangle((3, 3, 36, 26), fill=(220, 180, 80, 255))
            draw.rectangle((16, 11, 23, 18), fill=(0, 0, 0, 0))
            image.save(source)

            result = self.run_script(
                "--verify-only", "--expected-size", "40x30", str(source)
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("stamp interior", result.stderr)

    def test_default_delivery_gate_rejects_any_size_other_than_1024x1536(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            source = Path(temporary_directory) / "wrong-size.png"
            image = Image.new("RGBA", (40, 30), (0, 0, 0, 0))
            ImageDraw.Draw(image).rectangle((5, 5, 34, 24), fill=(220, 180, 80, 255))
            image.save(source)

            result = self.run_script("--verify-only", str(source))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("1024x1536", result.stderr)

    def test_conversion_normalizes_to_delivery_size_without_stretching_content(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temp = Path(temporary_directory)
            source = temp / "small-transparent.png"
            output = temp / "normalized.png"
            image = Image.new("RGBA", (80, 40), (255, 0, 255, 0))
            ImageDraw.Draw(image).rectangle((10, 10, 69, 29), fill=(220, 180, 80, 255))
            image.save(source)

            result = self.run_script(
                "--expected-size", "100x150", str(source), str(output)
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            with Image.open(output) as processed:
                self.assertEqual(processed.size, (100, 150))
                bbox = processed.getchannel("A").getbbox()
                self.assertIsNotNone(bbox)
                left, top, right, bottom = bbox or (0, 0, 0, 0)
                content_ratio = (right - left) / (bottom - top)
                self.assertAlmostEqual(content_ratio, 3.0, delta=0.15)
                self.assertGreater(top, 0)
                self.assertLess(bottom, 150)

    def test_landscape_orientation_normalizes_and_verifies_1536x1024(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temp = Path(temporary_directory)
            source = temp / "landscape-source.png"
            output = temp / "landscape-final.png"
            image = Image.new("RGBA", (120, 80), (0, 0, 0, 0))
            ImageDraw.Draw(image).rectangle((10, 10, 109, 69), fill=(220, 180, 80, 255))
            image.save(source)

            result = self.run_script(
                "--orientation", "landscape", str(source), str(output)
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            with Image.open(output) as processed:
                self.assertEqual(processed.mode, "RGBA")
                self.assertEqual(processed.size, (1536, 1024))
                self.assertEqual(processed.getchannel("A").getextrema(), (0, 255))

            verify = self.run_script(
                "--verify-only", "--orientation", "landscape", str(output)
            )
            self.assertEqual(verify.returncode, 0, verify.stderr)


if __name__ == "__main__":
    unittest.main()
