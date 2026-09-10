# Source Prompt Integrity Policy

`SOURCE_PROMPT_POLICY = READ_ONLY`.

A source prompt is the exact user-authored text stored at a versioned path. It is not a template to improve.

Forbidden operations include rewriting, shortening, summarizing, polishing, translating, merging, reordering, deleting, normalizing wording, silently correcting, or replacing a source prompt with Style Card metadata. Runtime policies, analysis JSON, Fusion Plans, ratios, and user requests remain separate outer blocks.

Resolution is deterministic:

```text
selected_style_id
→ Style Registry prompt_id
→ Prompt Version Registry active_versions_by_orientation[orientation]
→ version path
→ status = verified_source
→ SHA-256 matches
→ load exact bytes
```

If any check fails, stop with `blocked_missing_prompt`. Never continue with a placeholder, partial prompt, registry summary, Style Card, or reconstructed approximation.

Before image generation, use `scripts/compose_generation_payload.py` to copy the selected Style source prompt byte-for-byte. The resulting payload must equal that source file in its entirety. Do not add `global.negative`, Style Card metadata, analysis, Fusion Plans, runtime settings, delimiters, or assistant-authored text. Verify the sidecar manifest, then pass the complete payload to the image generator unchanged. Payload verification failure is a hard stop.

Version updates are append-only. Add `prompt_vN.md`, register its hash and provenance, then change the appropriate orientation mapping. Portrait and landscape resolve to separate complete immutable source files; never create the selected orientation by appending runtime text. Never overwrite a verified historical version.
