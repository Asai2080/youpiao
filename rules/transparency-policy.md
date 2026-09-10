# Transparency and Perforation Policy

The final asset is a freestanding stamp with complete perforations.

```text
INSIDE STAMP = OPAQUE
OUTSIDE OUTER PERFORATION = ALPHA 0
```

The alpha boundary follows the outermost perforation silhouette, including corner teeth. No pixel outside it may contain a white or black background, table, wall, display board, second sheet of paper, halo, matte, or shadow backing.

## Mandatory delivery pipeline

The image generator's direct result is always an intermediate render. Even when the generation request asks for transparency, never infer transparency from a visible checkerboard: the model may have painted that pattern into an opaque RGB image. Capture this intermediate without displaying or attaching it to the user response.

Create the final asset with:

```bash
python3 scripts/apply_transparency_mask.py INTERMEDIATE.png FINAL.png
python3 scripts/apply_transparency_mask.py --verify-only FINAL.png
```

Run both commands automatically in the same generation turn. Only `FINAL.png` may be displayed or delivered; the user must never be asked to remove the background manually. The processor must fail closed when the outer backdrop is not safely separable. Do not rename an RGB file, add transparency metadata without a pixel mask, or report a painted checkerboard as transparent.

## Pass conditions

- File format is PNG and pixel mode is RGBA.
- Alpha contains both `0` and `255`.
- Every pixel on the outer canvas edge has alpha `0`.
- Every fully transparent pixel stores RGBA `(0, 0, 0, 0)`; no hidden checkerboard or matte RGB remains.
- The stamp body retains opaque pixels.
- The central half of the printed stamp remains opaque; interior alpha leakage is an automatic failure.
- Portrait delivery is exactly 1024×1536 px at 2:3. Landscape delivery is exactly 1536×1024 px at 3:2. When the intermediate render differs, post-processing fits the complete stamp proportionally on the selected transparent canvas without stretching it.
- Visual inspection confirms that the alpha silhouette follows all four perforated sides and corners.

QA must inspect actual alpha values as well as the composited preview. A viewer's checkerboard is acceptable only after the pixel-level gate passes; it is viewer chrome, never image content. Do not show the raw generator preview before this gate.
