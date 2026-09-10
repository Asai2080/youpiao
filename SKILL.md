---
name: youpiao
description: Turn one or more real reference images into a portrait or landscape vintage postage-stamp image by routing to one registered Style, using only verified place/building names, sending one immutable Style prompt byte-for-byte to image generation, and enforcing real transparency.
---

# Youpiao

Create a vintage city or destination stamp from user images without altering the selected source prompt or inventing factual or cultural content.

## Non-negotiable order

```text
USER INSTRUCTION
> FACTUAL ACCURACY
> INPUT CONTENT PRESERVATION
> CULTURAL ACCURACY
> STYLE DNA
> VISUAL COMPOSITION
> DECORATION
```

Treat every registered source prompt as byte-preserved `READ_ONLY` content. Never rewrite, summarize, shorten, polish, reorder, merge, auto-optimize, or replace it with a Style Card description. The image generator must receive exactly one thing as its text prompt: the complete selected Style source file, byte-for-byte.

## Workflow

1. Count the input images and initialize a session using [session.schema.json](schemas/session.schema.json).
   - If orientation is missing, ask only `横版还是竖版？` Never ask for a numeric ratio or custom dimensions.
   - Map portrait to `2:3`, `1024×1536 px`; map landscape to `3:2`, `1536×1024 px`. Do not repeat an orientation already supplied.
   - One image: never ask whether to add text.
   - Multiple images: also ask for fusion versus independent generation when that choice is missing. Do not repeat information already supplied.
   - For independent generation, process each image through the single-image route.
2. Analyze each image independently with [image-analysis.schema.json](schemas/image-analysis.schema.json) and [color-analysis.schema.json](schemas/color-analysis.schema.json). Build `verified_name_candidates` only from user-provided names, clearly readable image text/signage, verified metadata, or reliably verified image identity. Architectural style, cultural appearance, visual similarity, country, or general association must never become place-name evidence. Use analysis only for routing and QA; never append it to the generation prompt.
3. For fusion, build [fusion-plan.schema.json](schemas/fusion-plan.schema.json) before routing. Merge and deduplicate verified building, attraction, city, and place names from every image. The source prompt may select a primary title randomly only from this pool. Different destinations are allowed when the user asks for fusion, but the result must not claim they are one shared city. If the pool is empty, stop at `BLOCKED_UNVERIFIED_PRIMARY_TITLE`. Read [multi-image-fusion-policy.md](rules/multi-image-fusion-policy.md).
4. Produce normalized features with [router-features.schema.json](schemas/router-features.schema.json). Load the matching Style Registry, router config, and [tie-break-rules.md](router/tie-break-rules.md). Select exactly one eligible Style. Hard gates override scores. Border and Footer are never routed separately.
5. Resolve the selected Style through [prompt-version-registry.json](registry/prompt-version-registry.json).
   - Require a registered orientation mapping: portrait loads v3 and landscape loads v4. Require `verified_source` status, an existing path, and a matching SHA-256.
   - Load that one Style file verbatim. Do not mutate it in memory or on disk.
   - If the prompt is missing, placeholder-only, or hash-mismatched, stop with `blocked_missing_prompt`. Do not reconstruct it.
6. Let the selected immutable Style prompt control automatic text, typography, color, composition, Border, Footer, and multi-image fusion. Use [global-fact-policy.md](rules/global-fact-policy.md), [primary-title-policy.md](rules/primary-title-policy.md), [user-text-policy.md](rules/user-text-policy.md), [typography-policy.md](rules/typography-policy.md), and [dynamic-text-color-policy.md](rules/dynamic-text-color-policy.md) to validate the result; do not append them to the generation prompt. A primary title outside the verified pool, including a guessed city such as `XI'AN`, is an automatic failure.
7. Create and verify the exact generation prompt:

   ```bash
   python3 scripts/compose_generation_payload.py --style-id STYLE_ID --orientation portrait --output GENERATION_PAYLOAD.txt --manifest GENERATION_PAYLOAD.manifest.json
   python3 scripts/compose_generation_payload.py --verify-only --payload GENERATION_PAYLOAD.txt --manifest GENERATION_PAYLOAD.manifest.json
   ```

   `GENERATION_PAYLOAD.txt` must be byte-identical to the selected Style source file. Do not prepend or append the global negative prompt, Style Card data, analysis, Fusion Plan, user-request paraphrase, ratio, dimensions, transparency instructions, delimiters, or any assistant-authored text. A failed verification blocks generation.
8. Pass the input images separately as image references and use the entire verified payload as the image-generation prompt. Use native size or transparent-background controls outside the text prompt when available; never append those controls to the read-only payload. Capture the direct generator result to `INTERMEDIATE.png` without displaying or attaching it to the user response. A painted checkerboard, black matte, or white matte is an expected intermediate condition, not a reason to regenerate.
9. Immediately create the delivery asset with `python3 scripts/apply_transparency_mask.py --orientation ORIENTATION INTERMEDIATE.png FINAL.png`. This mandatory automatic post-process removes the border-connected outside background, preserves the stamp proportions, zeros hidden RGB beneath alpha 0, centers the complete stamp on the selected transparent canvas, and normalizes it to the orientation's exact RGBA dimensions without changing the generation prompt. The user must not be asked to remove the background manually.
10. Run `python3 scripts/apply_transparency_mask.py --verify-only --orientation ORIENTATION FINAL.png`, then run [final-qa-policy.md](rules/final-qa-policy.md). Display or attach only `FINAL.png`; never expose `INTERMEDIATE.png` as a candidate result. Do not deliver until dimensions, edge alpha, interior opacity, zero hidden RGB, title-pool membership, and all other checks pass. Repair only the failed layer whenever possible; do not regenerate preserved architecture to fix typography, Footer, border, or transparency alone.

## Required policies

Always read:

- [source-prompt-integrity-policy.md](rules/source-prompt-integrity-policy.md)
- [global-fact-policy.md](rules/global-fact-policy.md)
- [primary-title-policy.md](rules/primary-title-policy.md)
- [cultural-integrity-policy.md](rules/cultural-integrity-policy.md)
- [ratio-policy.md](rules/ratio-policy.md)
- [transparency-policy.md](rules/transparency-policy.md)
- [global-negative-rules.md](rules/global-negative-rules.md)
- [final-qa-policy.md](rules/final-qa-policy.md)

Read the single registry/router for one image or independent multi-image output. Read the multi registry/router and fusion policy only for fusion.
