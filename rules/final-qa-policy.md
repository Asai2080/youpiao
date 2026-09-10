# Final QA Policy

A result passes only when every category passes.

## FACT

- Every factual text item has recorded support.
- No invented year, denomination, authority, emblem, event, coordinate, place, or landmark name appears.
- The primary title exactly matches a recorded verified-name candidate or its recorded verified standard translation/romanization.
- No place name was inferred from architectural style, cultural appearance, resemblance, country, or general association.
- For fusion, the rendered title belongs to the deduplicated union candidate pool and was selected using the registered random-title strategy.
- A country name does not appear as the primary title. Country-only primary titling is an automatic failure.

## STYLE

- Exactly one Style is used.
- The generation payload manifest passes verification and proves that the entire payload is byte-identical to the selected Style source prompt.
- No global prompt, Style Card summary, analysis, Fusion Plan, runtime setting, or assistant-authored text was added to the generation prompt.
- Typography, color-role mapping, print medium, aging, Border, and Footer match its Style Card and untouched source prompt.
- Border and Footer were not independently routed.

## CONTENT

- Key identity is at least 95% preserved.
- No incorrect, duplicated, fused-together, or culturally contaminated landmark appears.

## FUSION

- Roles follow the Fusion Plan.
- Perspective, scale, lighting, color temperature, depth, and print medium are coherent.
- Unused images are recorded rather than forced into the composition.

## OUTPUT

- Portrait output is 2:3 at exactly 1024×1536 px; landscape output is 3:2 at exactly 1536×1024 px. It must match the user's selected orientation.
- Typography is readable.
- Perforations are complete on all sides and corners.
- The delivered file is the post-processed final PNG, never the direct generator render.
- Pixel mode is RGBA, alpha includes both 0 and 255, and every outer-canvas pixel has alpha 0.
- Every pixel outside the outer perforation has alpha 0; a checkerboard painted into RGB is an automatic failure.
- Every alpha-0 pixel has RGB `(0,0,0)`, and the central half of the stamp contains no erased background leak.
- `python3 scripts/apply_transparency_mask.py --verify-only FINAL.png` exits successfully.

Repair only the failed layer when possible. Typography, Border, Footer, perforation, or alpha failures do not justify regenerating correct preserved architecture.
