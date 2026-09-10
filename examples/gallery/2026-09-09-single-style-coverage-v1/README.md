# Single Style Coverage Gallery V1

This gallery is a single-image regression set for `youpiao`.

## Coverage

- Seven uploaded source images are assigned globally to the best-fitting style.
- `STYLE_01` through `STYLE_07` are each covered exactly once.
- The assignment is not based on upload order.
- Every style includes one portrait result at 1024 × 1536 and one landscape result at 1536 × 1024.
- All final `*-after.png` files are RGBA PNGs with transparent pixels outside the perforated stamp contour.
- No Router, Registry, rule, or source Prompt was changed for this gallery run.

## Files in each style folder

- `before.png`: original source image used for the style.
- `portrait-after.png`: final portrait sample.
- `landscape-after.png`: final landscape sample.
- `*-generation-payload.txt`: exact read-only active source Prompt passed to generation.
- `*-generation-payload.manifest.json`: source Prompt version, path, hash, and output contract.
- `*-intermediate.png` and `*-qa-intermediate.png`: generation audit artifacts; these are not gallery delivery files.

## Selected pairing

| Style | Source subject | Reason for fit |
| --- | --- | --- |
| STYLE_01 | The Wave | Strong single natural landmark and travel-poster composition |
| STYLE_02 | Giant Wild Goose Pagoda | Formal Buddhist heritage subject and vertical monumentality |
| STYLE_03 | Colosseum | Repeating arcades and curved architectural perspective |
| STYLE_04 | Li River / Guilin landscape | Waterfront culture, local life, and botanical foreground |
| STYLE_05 | Leaning Tower of Pisa | Monumental public architecture with a stable horizontal base |
| STYLE_06 | Lauterbrunnen | Deep settlement layers, waterfall, river, and local rail context |
| STYLE_07 | User-approved alpine visual reference | Wide landscape with open compositional corridors |

## Factual-text note

`STYLE_07` is retained exactly as the user-approved visual sample. Its rendered place-name text is not treated as a verified naming example and must not be copied into Router or naming behavior. The global rule remains: do not guess a city, building, attraction, or scenic-area name.

See `mapping.json` for the machine-readable assignment and `QA.md` for delivery checks.

## True-transparent delivery set

The `transparent/` directory contains the 14 public delivery PNGs. Every fully
transparent pixel is stored as literal RGBA `(0, 0, 0, 0)`, so no painted
checkerboard or hidden matte color remains underneath the alpha channel.
