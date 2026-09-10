# youpiao

A deliverable Skill skeleton for routing real reference images into one fact-safe vintage postage-stamp Style while preserving the user's tuned source prompts verbatim.

Every generation uses one of two fixed delivery formats: portrait `2:3` at `1024×1536 px`, or landscape `3:2` at `1536×1024 px`. When orientation is missing, the Skill asks only `横版还是竖版？` For multiple images it also asks for fusion versus independent generation when that choice is missing.

## Generation examples

All eight single-image tests and four multi-image fusion tests are displayed directly below. Each comparison uses the requested columns: original image, portrait result, and landscape result.

### Single-image generation

#### Single 01

| 原图 | 竖版（2:3） | 横版（3:2） |
|---|---|---|
| <img src="examples/showcase/single/single-01/original.webp" width="280" alt="Single 01 original"> | <img src="examples/showcase/single/single-01/portrait.webp" width="280" alt="Single 01 portrait result"> | 暂缺 |

#### Single 02

| 原图 | 竖版（2:3） | 横版（3:2） |
|---|---|---|
| <img src="examples/showcase/single/single-02/original.webp" width="280" alt="Single 02 original"> | <img src="examples/showcase/single/single-02/portrait.webp" width="280" alt="Single 02 portrait result"> | <img src="examples/showcase/single/single-02/landscape.webp" width="280" alt="Single 02 landscape result"> |

#### Single 03

| 原图 | 竖版（2:3） | 横版（3:2） |
|---|---|---|
| <img src="examples/showcase/single/single-03/original.webp" width="280" alt="Single 03 original"> | <img src="examples/showcase/single/single-03/portrait.webp" width="280" alt="Single 03 portrait result"> | <img src="examples/showcase/single/single-03/landscape.webp" width="280" alt="Single 03 landscape result"> |

#### Single 04

| 原图 | 竖版（2:3） | 横版（3:2） |
|---|---|---|
| <img src="examples/showcase/single/single-04/original.webp" width="280" alt="Single 04 original"> | <img src="examples/showcase/single/single-04/portrait.webp" width="280" alt="Single 04 portrait result"> | <img src="examples/showcase/single/single-04/landscape.webp" width="280" alt="Single 04 landscape result"> |

#### Single 05

| 原图 | 竖版（2:3） | 横版（3:2） |
|---|---|---|
| <img src="examples/showcase/single/single-05/original.webp" width="280" alt="Single 05 original"> | <img src="examples/showcase/single/single-05/portrait.webp" width="280" alt="Single 05 portrait result"> | <img src="examples/showcase/single/single-05/landscape.webp" width="280" alt="Single 05 landscape result"> |

#### Single 06

| 原图 | 竖版（2:3） | 横版（3:2） |
|---|---|---|
| <img src="examples/showcase/single/single-06/original.webp" width="280" alt="Single 06 original"> | <img src="examples/showcase/single/single-06/portrait.webp" width="280" alt="Single 06 portrait result"> | <img src="examples/showcase/single/single-06/landscape.webp" width="280" alt="Single 06 landscape result"> |

#### Single 07

| 原图 | 竖版（2:3） | 横版（3:2） |
|---|---|---|
| <img src="examples/showcase/single/single-07/original.webp" width="280" alt="Single 07 original"> | <img src="examples/showcase/single/single-07/portrait.webp" width="280" alt="Single 07 portrait result"> | <img src="examples/showcase/single/single-07/landscape.webp" width="280" alt="Single 07 landscape result"> |

#### Single 08

| 原图 | 竖版（2:3） | 横版（3:2） |
|---|---|---|
| <img src="examples/showcase/single/single-08/original.webp" width="280" alt="Single 08 original"> | <img src="examples/showcase/single/single-08/portrait.webp" width="280" alt="Single 08 portrait result"> | <img src="examples/showcase/single/single-08/landscape.webp" width="280" alt="Single 08 landscape result"> |

### Multi-image fusion

The first column contains every source image used by that fusion test.

#### Multi 01

| 原图 | 竖版（2:3） | 横版（3:2） |
|---|---|---|
| <img src="examples/showcase/multi/multi-01/source-01.webp" width="100" alt="Multi 01 source 1"> <img src="examples/showcase/multi/multi-01/source-02.webp" width="100" alt="Multi 01 source 2"><br><img src="examples/showcase/multi/multi-01/source-03.webp" width="100" alt="Multi 01 source 3"> <img src="examples/showcase/multi/multi-01/source-04.webp" width="100" alt="Multi 01 source 4"><br><img src="examples/showcase/multi/multi-01/source-05.webp" width="100" alt="Multi 01 source 5"> | <img src="examples/showcase/multi/multi-01/portrait.webp" width="280" alt="Multi 01 portrait result"> | 暂缺 |

#### Multi 02

| 原图 | 竖版（2:3） | 横版（3:2） |
|---|---|---|
| <img src="examples/showcase/multi/multi-02/source-01.webp" width="100" alt="Multi 02 source 1"> <img src="examples/showcase/multi/multi-02/source-02.webp" width="100" alt="Multi 02 source 2"><br><img src="examples/showcase/multi/multi-02/source-03.webp" width="100" alt="Multi 02 source 3"> <img src="examples/showcase/multi/multi-02/source-04.webp" width="100" alt="Multi 02 source 4"><br><img src="examples/showcase/multi/multi-02/source-05.webp" width="100" alt="Multi 02 source 5"> | <img src="examples/showcase/multi/multi-02/portrait.webp" width="280" alt="Multi 02 portrait result"> | 暂缺 |

#### Multi 03

| 原图 | 竖版（2:3） | 横版（3:2） |
|---|---|---|
| <img src="examples/showcase/multi/multi-03/source-01.webp" width="100" alt="Multi 03 source 1"> <img src="examples/showcase/multi/multi-03/source-02.webp" width="100" alt="Multi 03 source 2"><br><img src="examples/showcase/multi/multi-03/source-03.webp" width="100" alt="Multi 03 source 3"> <img src="examples/showcase/multi/multi-03/source-04.webp" width="100" alt="Multi 03 source 4"> | <img src="examples/showcase/multi/multi-03/portrait-slot-alternate.webp" width="280" alt="Multi 03 retained alternate result"><br><sub>按用户确认保留；当前文件实际为 1536×1024 横版备选稿。</sub> | <img src="examples/showcase/multi/multi-03/landscape.webp" width="280" alt="Multi 03 landscape result"> |

Multi 03 preserves the two approved historical outputs even though both are landscape and opaque. The label makes that limitation explicit rather than presenting either file as a transparent portrait asset.

#### Multi 04

| 原图 | 竖版（2:3） | 横版（3:2） |
|---|---|---|
| <img src="examples/showcase/multi/multi-04/source-01.webp" width="100" alt="Multi 04 source 1"> <img src="examples/showcase/multi/multi-04/source-02.webp" width="100" alt="Multi 04 source 2"><br><img src="examples/showcase/multi/multi-04/source-03.webp" width="100" alt="Multi 04 source 3"> <img src="examples/showcase/multi/multi-04/source-04.webp" width="100" alt="Multi 04 source 4"> | <img src="examples/showcase/multi/multi-04/portrait.webp" width="280" alt="Multi 04 portrait result"> | <img src="examples/showcase/multi/multi-04/landscape.webp" width="280" alt="Multi 04 landscape result"> |

## Install from the shared ZIP

This package is intended for a Codex environment that has built-in image generation available.

1. Unzip the archive. Keep the top-level folder name as `youpiao`.
2. Copy that complete folder to the Codex Skill directory:
   - default: `~/.codex/skills/youpiao`
   - custom Codex home: `$CODEX_HOME/skills/youpiao`
3. Install the two lightweight Python dependencies from the copied folder:

   ```bash
   python3 -m pip install -r requirements.txt
   ```

4. Start a new Codex task, attach one or more reference images, and invoke `$youpiao` or ask for a vintage postage-stamp image.

The ZIP includes the complete registered source prompts. Share it only with people who are allowed to receive and use those prompt texts. A recipient does not need the original authoring document or any path from the creator's computer.

## Install from the private Git repository

Clone the repository into the Codex Skill directory, keep the folder name as `youpiao`, and install the lightweight Python dependencies:

```bash
git clone https://github.com/Asai2080/youpiao.git ~/.codex/skills/youpiao
cd ~/.codex/skills/youpiao
python3 -m pip install -r requirements.txt
python3 scripts/validate_skill.py --require-all-prompts
```

The existing style-coverage gallery keeps only the intended `before.png`, `portrait-after.png`, and `landscape-after.png` files. The user-facing showcase under `examples/showcase/` keeps only optimized WebP previews. Runtime output, direct generator renders, QA intermediates, caches, duplicate transparent copies, and gallery ZIP bundles remain local and are excluded by `.gitignore`.

## Known QA limitation

`MULTI_STYLE_03` / original `STYLE_09` contains both a required denomination slot and a rule forbidding unsupported real-looking denominations. Some image-generation runs still render a plausible value such as `80¢`. The Skill flags that as a factual QA failure; it does not silently rewrite the read-only source prompt to fix it.

## Current source-prompt state

- The user-provided `stamp_prompts_original_verbatim.md` is the authoritative import source.
- All 14 v1 source blocks remain installed and hash-locked: one global negative prompt, seven single-image Style prompts, and six multi-image Style prompts.
- The 13 Style prompts now have append-only `prompt_v2.md` versions. Each v2 keeps its complete v1 source text byte-for-byte and appends only the user-approved rule requiring a specific attraction/building or city as the primary title and forbidding a country name as the primary title.
- All 13 Style prompts retain v1 and v2 unchanged. Portrait now resolves to immutable v3 and landscape resolves to immutable v4; both append the approved verified-name rule, while their orientation-specific composition contracts remain separate.
- Automatic titles may come only from verified candidates: single images use the most specific verified building/attraction/city/place name; fusion images randomly choose only from the deduplicated union of verified names across all inputs. A guessed name or any name outside that pool is rejected.
- The independent global negative prompt remains on v1 and is still never appended to generation payloads.
- No prompt placeholder remains. Historical v1 files are unchanged and remain available for rollback.

Run:

```bash
python3 scripts/validate_skill.py
```

This validates JSON files, schema structure, registry coverage, router/registry agreement, prompt paths, and hashes. Add `--require-all-prompts` to explicitly reject any future guarded placeholder.

## Project map

```text
youpiao/
├── SKILL.md
├── README.md
├── schemas/
├── registry/
├── rules/
├── router/
├── prompts/
│   ├── global/global_negative/
│   ├── single/style_01..style_07/
│   └── multi/multi_style_01..multi_style_06/
├── examples/
├── scripts/
│   ├── validate_skill.py
│   ├── compose_generation_payload.py
│   └── apply_transparency_mask.py
└── tests/
```

The Style Card registries hold routing, composition, typography, color-role, Border, Footer, printing, and QA metadata. They are indexes, not replacements for source prompts. Border and Footer remain embedded in Style DNA; there is no Border Router or Footer Router.

## Add a new Prompt version

Never overwrite a verified prompt.

1. Put the exact new user text in the same Style directory as `prompt_v2.md`, `prompt_v3.md`, and so on.
2. Add that version under the same `prompt_id` in `prompt-version-registry.json`, including path, `verified_source` status, immutable flag, SHA-256, and provenance.
3. Change `active_versions_by_orientation.portrait` and/or `.landscape` to the confirmed complete version. Keep `active_version` aligned with the portrait version for backward registry compatibility.
4. Make the source file read-only and run validation.

Historical versions stay registered and unchanged. Switching an orientation mapping changes which complete source prompt is loaded without modifying that prompt at runtime.

## Exact generation payload

Do not manually compose, summarize, or augment the prompt sent to image generation. Create and verify it deterministically:

```bash
python3 scripts/compose_generation_payload.py --style-id MULTI_STYLE_03 --orientation landscape --output generation-payload.txt --manifest generation-payload.manifest.json
python3 scripts/compose_generation_payload.py --verify-only --payload generation-payload.txt --manifest generation-payload.manifest.json
```

The payload is not a wrapper or combined prompt: its complete byte content equals the selected Style source file. It contains no global prompt, Style Card, Router score, analysis, Fusion Plan, runtime JSON, output setting, delimiter, or assistant-authored text. Pass that file to the image generator unchanged and pass the images separately as references. Any addition, summary, truncation, mutation, or Style substitution invalidates the payload hash and blocks generation.

## Runtime boundary

This project intentionally does not implement image generation. It defines analysis contracts, deterministic routing, byte-exact Style prompt resolution, deterministic size/transparency post-processing, and final QA. Routing and QA data are never mixed into the image-generation prompt.

## Mandatory transparent delivery

Never deliver the image generator's direct result. Some generators paint a gray checkerboard into a fully opaque RGB PNG even when asked for transparency.

The runtime should capture that direct result silently as `intermediate.png`, run the conversion and verification immediately, and show only `final.png`. This makes transparency automatic for the user; a fake checkerboard is handled as an internal intermediate state instead of a second manual task.

After generation, create and verify the delivery asset:

```bash
python3 scripts/apply_transparency_mask.py --orientation portrait intermediate.png final.png
python3 scripts/apply_transparency_mask.py --verify-only --orientation portrait final.png
```

The first command learns the outside backdrop from the canvas edge, removes only the connected outside region, clears hidden RGB under fully transparent pixels, preserves the stamp's proportions, and fits it onto the selected transparent RGBA canvas. Use `portrait` for 1024×1536 or `landscape` for 1536×1024. The second command is the delivery gate and also rejects interior alpha leakage. If either command fails, do not deliver the file; correct only the post-processing layer, never the source prompt.

Run the regression tests with:

```bash
python3 -m unittest discover -s tests -v
```

The transparency processor requires Pillow. It does not modify source prompts or implement image generation.
