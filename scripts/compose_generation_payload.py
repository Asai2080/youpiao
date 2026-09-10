#!/usr/bin/env python3
"""Resolve one Style and copy its source prompt byte-for-byte for generation.

Routing, analysis, runtime settings, global policies, and QA deliberately remain
outside the prompt sent to the image model. The output file must be identical to
the selected immutable Style source prompt.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[1]
PROMPT_REGISTRY = ROOT / "registry" / "prompt-version-registry.json"
STYLE_REGISTRIES = (
    ROOT / "registry" / "single-style-registry.json",
    ROOT / "registry" / "multi-style-registry.json",
)
ORIENTATION_OUTPUTS = {
    "portrait": {"ratio": "2:3", "width": 1024, "height": 1536},
    "landscape": {"ratio": "3:2", "width": 1536, "height": 1024},
}


class PayloadError(RuntimeError):
    """Raised when an exact source-only payload cannot be produced or verified."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise PayloadError(f"invalid JSON at {path}: {error}") from error


def safe_source_path(relative_path: str) -> Path:
    candidate = (ROOT / relative_path).resolve()
    try:
        candidate.relative_to(ROOT.resolve())
    except ValueError as error:
        raise PayloadError(f"source path escapes the skill root: {relative_path}") from error
    return candidate


def style_prompt_id(style_id: str) -> str:
    matches: list[str] = []
    for registry_path in STYLE_REGISTRIES:
        registry = load_json(registry_path)
        for style in registry.get("styles", []):
            if style.get("style_id") == style_id:
                prompt_id = style.get("source_prompt", {}).get("prompt_id")
                if isinstance(prompt_id, str):
                    matches.append(prompt_id)
    if len(matches) != 1:
        raise PayloadError(f"style {style_id!r} must resolve to exactly one source prompt")
    return matches[0]


def verified_source(prompt_id: str, orientation: str) -> dict[str, Any]:
    registry = load_json(PROMPT_REGISTRY)
    records = {
        record.get("prompt_id"): record
        for record in registry.get("prompts", [])
        if isinstance(record, dict)
    }
    record = records.get(prompt_id)
    if not isinstance(record, dict):
        raise PayloadError(f"unregistered source prompt: {prompt_id}")
    active_by_orientation = record.get("active_versions_by_orientation")
    if not isinstance(active_by_orientation, dict):
        raise PayloadError(f"source prompt has no orientation variants: {prompt_id}")
    active_version = active_by_orientation.get(orientation)
    versions = record.get("versions", {})
    version = versions.get(active_version) if isinstance(versions, dict) else None
    if not isinstance(active_version, str) or not isinstance(version, dict):
        raise PayloadError(f"source prompt has no active verified version: {prompt_id}")
    if version.get("status") != "verified_source" or version.get("immutable") is not True:
        raise PayloadError(f"source prompt is not immutable verified_source: {prompt_id}")

    relative_path = version.get("path")
    expected_hash = version.get("sha256")
    if not isinstance(relative_path, str) or not isinstance(expected_hash, str):
        raise PayloadError(f"source prompt metadata is incomplete: {prompt_id}")
    path = safe_source_path(relative_path)
    try:
        content = path.read_bytes()
    except OSError as error:
        raise PayloadError(f"cannot read source prompt {relative_path}: {error}") from error
    actual_hash = sha256(content)
    if actual_hash != expected_hash:
        raise PayloadError(f"source prompt hash mismatch: {prompt_id}")
    return {
        "prompt_id": prompt_id,
        "version": active_version,
        "path": relative_path,
        "sha256": actual_hash,
        "content": content,
    }


def compose(
    style_id: str,
    orientation: str,
    output_path: Path,
    manifest_path: Path,
) -> dict[str, Any]:
    if orientation not in ORIENTATION_OUTPUTS:
        raise PayloadError("orientation must be portrait or landscape")
    source = verified_source(style_prompt_id(style_id), orientation)
    payload = source["content"]
    manifest: dict[str, Any] = {
        "source_prompt_policy": "READ_ONLY",
        "generation_input_policy": "STYLE_SOURCE_PROMPT_ONLY_VERBATIM",
        "excluded_from_generation_prompt": [
            "style_card_summary",
            "router_scores",
            "image_analysis",
            "fusion_plan",
            "global_policy_text",
            "runtime_json",
            "assistant_authored_instructions",
        ],
        "style_id": style_id,
        "orientation": orientation,
        "output_contract": ORIENTATION_OUTPUTS[orientation],
        "style_source_prompt": {
            key: source[key] for key in ("prompt_id", "version", "path", "sha256")
        },
        "payload_sha256": sha256(payload),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(payload)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    verify_payload(output_path, manifest_path)
    return manifest


def verify_payload(payload_path: Path, manifest_path: Path) -> dict[str, Any]:
    try:
        payload = payload_path.read_bytes()
    except OSError as error:
        raise PayloadError(f"cannot read payload: {error}") from error
    manifest = load_json(manifest_path)
    if manifest.get("source_prompt_policy") != "READ_ONLY":
        raise PayloadError("manifest source policy is not READ_ONLY")
    if manifest.get("generation_input_policy") != "STYLE_SOURCE_PROMPT_ONLY_VERBATIM":
        raise PayloadError("generation input policy is not source-only verbatim")
    if sha256(payload) != manifest.get("payload_sha256"):
        raise PayloadError("generation payload hash mismatch; mutation detected")

    section = manifest.get("style_source_prompt")
    if not isinstance(section, dict):
        raise PayloadError("style source manifest section is missing")
    orientation = manifest.get("orientation")
    if orientation not in ORIENTATION_OUTPUTS:
        raise PayloadError("manifest orientation is missing or invalid")
    if manifest.get("output_contract") != ORIENTATION_OUTPUTS[orientation]:
        raise PayloadError("manifest output contract does not match orientation")
    source = verified_source(section.get("prompt_id", ""), orientation)
    if section.get("version") != source["version"] or section.get("path") != source["path"]:
        raise PayloadError("manifest does not reference the active orientation source prompt")
    if payload != source["content"] or sha256(payload) != section.get("sha256"):
        raise PayloadError("payload is not byte-identical to the selected Style source prompt")
    return manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create or verify a Style-source-only image-generation prompt."
    )
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--style-id")
    parser.add_argument("--orientation", choices=sorted(ORIENTATION_OUTPUTS))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--payload", type=Path)
    parser.add_argument("--manifest", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    try:
        if arguments.verify_only:
            if arguments.payload is None:
                raise PayloadError("--verify-only requires --payload")
            manifest = verify_payload(arguments.payload, arguments.manifest)
            print(f"PASS: source-only generation prompt verified: {manifest['payload_sha256']}")
            return 0
        if arguments.style_id is None or arguments.orientation is None or arguments.output is None:
            raise PayloadError("composition requires --style-id, --orientation, and --output")
        manifest = compose(
            arguments.style_id,
            arguments.orientation,
            arguments.output,
            arguments.manifest,
        )
        print(f"PASS: source-only generation prompt created: {manifest['payload_sha256']}")
        return 0
    except PayloadError as error:
        print(f"FAILED: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
