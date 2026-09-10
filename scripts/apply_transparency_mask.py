#!/usr/bin/env python3
"""Convert a rendered stamp's border-connected backdrop into real PNG alpha.

Image models sometimes paint a checkerboard instead of returning transparency.
This script learns the neutral backdrop from the outer canvas border, removes only
the matching border-connected region, writes RGBA PNG, and then applies a strict
delivery gate.
"""

from __future__ import annotations

import argparse
import sys
from collections import deque
from pathlib import Path
from typing import Iterable, Sequence

from PIL import Image


ORIENTATION_SIZES = {
    "portrait": (1024, 1536),
    "landscape": (1536, 1024),
}
DEFAULT_ORIENTATION = "portrait"
DEFAULT_EXPECTED_SIZE = ORIENTATION_SIZES[DEFAULT_ORIENTATION]


class TransparencyError(RuntimeError):
    """Raised when real transparency cannot be produced or verified safely."""


def percentile(values: Sequence[float], fraction: float) -> float:
    if not values:
        raise TransparencyError("cannot learn a background from an empty sample")
    ordered = sorted(values)
    index = round((len(ordered) - 1) * fraction)
    return float(ordered[index])


def outer_band_pixels(image: Image.Image, band: int) -> Iterable[tuple[int, int, int]]:
    pixels = image.load()
    width, height = image.size
    for y in range(band):
        for x in range(width):
            yield pixels[x, y]
    for y in range(height - band, height):
        for x in range(width):
            yield pixels[x, y]
    for y in range(band, height - band):
        for x in range(band):
            yield pixels[x, y]
        for x in range(width - band, width):
            yield pixels[x, y]


def learn_neutral_background(image: Image.Image) -> tuple[float, float, float]:
    width, height = image.size

    # Prefer the one-pixel canvas edge.  It is the strongest evidence for the
    # outside matte and avoids learning light stamp paper that enters a wider
    # border band through perforation peaks.  A deliberately narrow chroma
    # envelope keeps a gray checkerboard or dark matte from leaking into
    # neutral paper, snow, clouds, or typography inside the stamp.
    edge_sample = list(outer_band_pixels(image, 1))
    edge_neutral = [pixel for pixel in edge_sample if max(pixel) - min(pixel) <= 38]
    if len(edge_neutral) >= max(32, round(len(edge_sample) * 0.55)):
        edge_chroma = [max(pixel) - min(pixel) for pixel in edge_neutral]
        edge_luminance = [sum(pixel) / 3.0 for pixel in edge_neutral]
        chroma_limit = min(38.0, max(8.0, percentile(edge_chroma, 0.99) + 7.0))
        luminance_10 = percentile(edge_luminance, 0.10)
        luminance_90 = percentile(edge_luminance, 0.90)

        if luminance_90 <= 115:
            # Dark black/charcoal/brown matte.  Do not let light paper in the
            # wider sample broaden this range.
            return chroma_limit, 0.0, min(135.0, luminance_90 + 24.0)
        if luminance_10 >= 215:
            # White or near-white matte.
            return chroma_limit, max(190.0, luminance_10 - 24.0), 255.0

        # Mid-tone neutral checkerboard.  The two checker levels are captured
        # by the edge percentiles while the tight chroma limit excludes paper.
        return (
            chroma_limit,
            max(0.0, percentile(edge_luminance, 0.02) - 18.0),
            min(255.0, percentile(edge_luminance, 0.98) + 18.0),
        )

    band = max(2, min(width, height) // 100)
    sample = list(outer_band_pixels(image, band))
    neutral_sample = [
        pixel for pixel in sample if max(pixel) - min(pixel) <= 45
    ]

    # Perforation peaks can enter the sampling band and are intentionally
    # chromatic.  Learn from the neutral majority/minority backdrop instead of
    # letting a small amount of tan paper force the dark-matte fallback.  This
    # also handles a generated gray checkerboard whose two luminance levels
    # remain connected around the complete stamp silhouette.
    if len(neutral_sample) >= max(32, round(len(sample) * 0.20)):
        neutral_chroma = [max(pixel) - min(pixel) for pixel in neutral_sample]
        neutral_luminance = [sum(pixel) / 3.0 for pixel in neutral_sample]
        chroma_limit = min(50.0, max(12.0, percentile(neutral_chroma, 0.995) + 8.0))
        luminance_low = max(0.0, percentile(neutral_luminance, 0.002) - 24.0)
        luminance_high = min(255.0, percentile(neutral_luminance, 0.998) + 24.0)
        return chroma_limit, luminance_low, luminance_high

    chroma = [max(pixel) - min(pixel) for pixel in sample]

    border_chroma_99 = percentile(chroma, 0.99)
    if border_chroma_99 > 40:
        # A generated stamp can sit on a dark, slightly textured matte.  The
        # perforation peaks may enter the wider sampling band, so learn this
        # fallback from the one-pixel canvas edge instead.  It remains
        # deliberately conservative: only a predominantly dark, low-chroma
        # edge is accepted, and flood filling still limits removal to pixels
        # connected to that edge.
        edge_chroma = [max(pixel) - min(pixel) for pixel in edge_sample]
        edge_luminance = [sum(pixel) / 3.0 for pixel in edge_sample]
        edge_chroma_75 = percentile(edge_chroma, 0.75)
        edge_luminance_75 = percentile(edge_luminance, 0.75)
        if edge_chroma_75 > 35 or edge_luminance_75 > 110:
            raise TransparencyError(
                "outer border is not a separable neutral or dark backdrop; "
                "refusing an unsafe mask"
            )
        chroma_limit = min(55.0, percentile(edge_chroma, 0.90) + 15.0)
        luminance_high = min(125.0, percentile(edge_luminance, 0.90) + 30.0)
        return chroma_limit, 0.0, luminance_high

    chroma_limit = min(36.0, max(12.0, border_chroma_99 + 14.0))
    luminance = [sum(pixel) / 3.0 for pixel in sample]
    luminance_low = max(0.0, percentile(luminance, 0.005) - 24.0)
    luminance_high = min(255.0, percentile(luminance, 0.995) + 24.0)
    return chroma_limit, luminance_low, luminance_high


def make_background_mask(image: Image.Image) -> bytearray:
    width, height = image.size
    pixels = image.load()
    chroma_limit, luminance_low, luminance_high = learn_neutral_background(image)
    mask = bytearray(width * height)
    queue: deque[int] = deque()

    def is_background(x: int, y: int) -> bool:
        red, green, blue = pixels[x, y]
        chroma = max(red, green, blue) - min(red, green, blue)
        luminance = (red + green + blue) / 3.0
        return chroma <= chroma_limit and luminance_low <= luminance <= luminance_high

    def seed(x: int, y: int) -> None:
        index = y * width + x
        if not mask[index] and is_background(x, y):
            mask[index] = 1
            queue.append(index)

    for x in range(width):
        seed(x, 0)
        seed(x, height - 1)
    for y in range(1, height - 1):
        seed(0, y)
        seed(width - 1, y)

    while queue:
        index = queue.popleft()
        x = index % width
        y = index // width
        if x > 0:
            seed(x - 1, y)
        if x + 1 < width:
            seed(x + 1, y)
        if y > 0:
            seed(x, y - 1)
        if y + 1 < height:
            seed(x, y + 1)

    return mask


def verify_rgba(
    image: Image.Image,
    expected_size: tuple[int, int] | None = DEFAULT_EXPECTED_SIZE,
    require_transparent_edges: bool = True,
) -> dict[str, float | int]:
    if image.mode != "RGBA":
        raise TransparencyError(f"output mode is {image.mode}, expected RGBA")

    width, height = image.size
    if expected_size is not None and (width, height) != expected_size:
        expected_width, expected_height = expected_size
        raise TransparencyError(
            f"output size is {width}x{height}, expected {expected_width}x{expected_height}"
        )
    if width < 2 or height < 2:
        raise TransparencyError("output dimensions are too small")

    alpha = image.getchannel("A")
    minimum, maximum = alpha.getextrema()
    if minimum != 0 or maximum != 255:
        raise TransparencyError(
            f"alpha range is {(minimum, maximum)}, expected both fully transparent and opaque pixels"
        )

    alpha_pixels = alpha.load()
    edge_coordinates = (
        [(x, 0) for x in range(width)]
        + [(x, height - 1) for x in range(width)]
        + [(0, y) for y in range(1, height - 1)]
        + [(width - 1, y) for y in range(1, height - 1)]
    )
    if require_transparent_edges and any(
        alpha_pixels[x, y] != 0 for x, y in edge_coordinates
    ):
        raise TransparencyError("one or more outer-canvas pixels are not fully transparent")

    histogram = alpha.histogram()
    transparent_pixels = histogram[0]
    opaque_pixels = histogram[255]
    total_pixels = width * height
    transparent_fraction = transparent_pixels / total_pixels
    if transparent_fraction < 0.01:
        raise TransparencyError("transparent area is too small to represent an outside background")
    if opaque_pixels == 0:
        raise TransparencyError("no opaque stamp content remains")

    # A stamp is an opaque printed object.  Transparency in the central half
    # indicates that background classification leaked through the border and
    # erased valid art.  Fail closed instead of delivering a plausible-looking
    # but damaged alpha mask.
    content_bbox = alpha.getbbox()
    if content_bbox is None:
        raise TransparencyError("no visible stamp content remains")
    left, top, right, bottom = content_bbox
    content_width = right - left
    content_height = bottom - top
    center = alpha.crop(
        (
            left + content_width // 4,
            top + content_height // 4,
            left + content_width * 3 // 4,
            top + content_height * 3 // 4,
        )
    )
    center_histogram = center.histogram()
    center_transparent_fraction = center_histogram[0] / (center.width * center.height)
    if center_transparent_fraction > 0.002:
        raise TransparencyError(
            "transparent mask leaked into the stamp interior "
            f"({center_transparent_fraction:.4%} of central pixels are alpha 0)"
        )

    # True transparent delivery also clears the hidden color channels.  This
    # prevents a painted checkerboard or matte from reappearing in software
    # that mishandles straight alpha.
    raw = image.tobytes()
    hidden_rgb_pixels = 0
    for index in range(0, len(raw), 4):
        if raw[index + 3] == 0 and (raw[index] or raw[index + 1] or raw[index + 2]):
            hidden_rgb_pixels += 1
    if hidden_rgb_pixels:
        raise TransparencyError(
            f"{hidden_rgb_pixels} fully transparent pixels retain hidden RGB data"
        )

    return {
        "width": width,
        "height": height,
        "transparent_pixels": transparent_pixels,
        "opaque_pixels": opaque_pixels,
        "transparent_fraction": round(transparent_fraction, 6),
        "center_transparent_fraction": round(center_transparent_fraction, 6),
        "hidden_rgb_pixels": hidden_rgb_pixels,
    }


def clear_fully_transparent_rgb(image: Image.Image) -> Image.Image:
    """Return RGBA with every alpha-0 pixel normalized to (0, 0, 0, 0)."""
    rgba = image.convert("RGBA")
    raw = bytearray(rgba.tobytes())
    for index in range(0, len(raw), 4):
        if raw[index + 3] == 0:
            raw[index] = 0
            raw[index + 1] = 0
            raw[index + 2] = 0
    return Image.frombytes("RGBA", rgba.size, bytes(raw))


def normalize_canvas(
    image: Image.Image,
    expected_size: tuple[int, int],
) -> Image.Image:
    """Fit the complete stamp onto the fixed canvas without changing its proportions."""
    alpha_bbox = image.getchannel("A").getbbox()
    if alpha_bbox is None:
        raise TransparencyError("cannot normalize an image with no visible stamp content")
    if image.size == expected_size:
        width, height = image.size
        left, top, right, bottom = alpha_bbox
        if left > 0 and top > 0 and right < width and bottom < height:
            return image
    stamp = image.crop(alpha_bbox)
    expected_width, expected_height = expected_size
    margin = max(1, round(min(expected_size) * 0.02))
    available_width = expected_width - margin * 2
    available_height = expected_height - margin * 2
    scale = min(available_width / stamp.width, available_height / stamp.height)
    resized_size = (
        max(1, round(stamp.width * scale)),
        max(1, round(stamp.height * scale)),
    )
    stamp = stamp.resize(resized_size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", expected_size, (0, 0, 0, 0))
    position = (
        (expected_width - stamp.width) // 2,
        (expected_height - stamp.height) // 2,
    )
    canvas.alpha_composite(stamp, position)
    return canvas


def convert_to_transparent(
    source: Path,
    destination: Path,
    expected_size: tuple[int, int] = DEFAULT_EXPECTED_SIZE,
) -> dict[str, float | int]:
    if destination.suffix.lower() != ".png":
        raise TransparencyError("destination must use the .png extension")

    already_transparent: Image.Image | None = None
    with Image.open(source) as opened:
        if opened.mode == "RGBA":
            candidate = clear_fully_transparent_rgb(opened)
            try:
                verify_rgba(candidate, opened.size)
            except TransparencyError:
                pass
            else:
                already_transparent = candidate
        rgb = opened.convert("RGB")
        existing_alpha = opened.getchannel("A") if opened.mode == "RGBA" else None

    if already_transparent is not None:
        rgba = already_transparent
    else:
        background = make_background_mask(rgb)
        rgba = rgb.convert("RGBA")
        alpha_values = bytearray(existing_alpha.tobytes()) if existing_alpha else bytearray([255]) * len(background)
        for index, is_background in enumerate(background):
            if is_background:
                alpha_values[index] = 0
        rgba.putalpha(Image.frombytes("L", rgba.size, bytes(alpha_values)))
        rgba = clear_fully_transparent_rgb(rgba)

    # Generated perforation peaks can touch the intermediate canvas edge.
    # Preserve them here, then create a guaranteed transparent delivery margin
    # in normalize_canvas before applying the strict final edge gate.
    verify_rgba(rgba, rgba.size, require_transparent_edges=False)
    rgba = normalize_canvas(rgba, expected_size)
    rgba = clear_fully_transparent_rgb(rgba)
    report = verify_rgba(rgba, expected_size)
    destination.parent.mkdir(parents=True, exist_ok=True)
    rgba.save(destination, format="PNG")

    with Image.open(destination) as saved:
        saved_report = verify_rgba(saved, expected_size)
    if saved_report != report:
        raise TransparencyError("saved PNG does not match the verified in-memory alpha result")
    return report


def verify_file(
    path: Path,
    expected_size: tuple[int, int] = DEFAULT_EXPECTED_SIZE,
) -> dict[str, float | int]:
    with Image.open(path) as image:
        return verify_rgba(image, expected_size)


def parse_size(value: str) -> tuple[int, int]:
    normalized = value.lower().replace("×", "x")
    try:
        width_text, height_text = normalized.split("x", 1)
        width, height = int(width_text), int(height_text)
    except (TypeError, ValueError) as error:
        raise argparse.ArgumentTypeError("size must use WIDTHxHEIGHT, for example 1024x1536") from error
    if width < 2 or height < 2:
        raise argparse.ArgumentTypeError("width and height must both be at least 2")
    return width, height


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create and verify a true RGBA transparent background for youpiao outputs."
    )
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument(
        "--orientation",
        choices=sorted(ORIENTATION_SIZES),
        default=DEFAULT_ORIENTATION,
        help="delivery orientation; portrait=1024x1536, landscape=1536x1024",
    )
    parser.add_argument(
        "--expected-size",
        type=parse_size,
        default=None,
        metavar="WIDTHxHEIGHT",
        help="explicit test/legacy override; normal delivery should use --orientation",
    )
    parser.add_argument("paths", nargs="+")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    expected_size = arguments.expected_size or ORIENTATION_SIZES[arguments.orientation]
    try:
        if arguments.verify_only:
            if len(arguments.paths) != 1:
                raise TransparencyError("--verify-only expects exactly one PNG path")
            report = verify_file(Path(arguments.paths[0]), expected_size)
            print(f"PASS: true RGBA transparency verified: {report}")
            return 0

        if len(arguments.paths) != 2:
            raise TransparencyError("conversion expects SOURCE and DESTINATION paths")
        report = convert_to_transparent(
            Path(arguments.paths[0]), Path(arguments.paths[1]), expected_size
        )
        print(f"PASS: transparent PNG created and verified: {report}")
        return 0
    except (OSError, TransparencyError) as error:
        print(f"FAILED: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
