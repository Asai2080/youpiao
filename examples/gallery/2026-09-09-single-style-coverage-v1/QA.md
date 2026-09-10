# Gallery QA

## Passed delivery gates

- 7/7 single styles covered exactly once.
- 14/14 final images present.
- 7/7 portrait images are exactly 1024 × 1536.
- 7/7 landscape images are exactly 1536 × 1024.
- 14/14 final images are RGBA PNGs.
- 14/14 final images contain both fully transparent and fully opaque pixels.
- 14/14 final images have fully transparent outer-canvas edges.
- All source generation payloads match the active read-only Prompt files recorded in their manifests.
- Style routing order was not forced by upload sequence.
- Existing skill logic was not changed.

## Sample-specific handling

- `STYLE_02/landscape-after.png` received a final text QA pass so the primary label is the attraction name `GIANT WILD GOOSE PAGODA` with `XI'AN` secondary.
- `STYLE_06` received transparency-only QA passes; the visual content and naming remain Lauterbrunnen.
- `STYLE_07` keeps the exact user-approved visual result. Its rendered geographic wording is not a verified factual example and is excluded from naming-rule evidence.

## Delivery files

Only `before.png`, `portrait-after.png`, and `landscape-after.png` are intended for the public before/after gallery. Intermediate files are retained only for local audit.
