#!/usr/bin/env python3
"""Validate the youpiao skill skeleton without generating images."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas"
REGISTRY_DIR = ROOT / "registry"
ROUTER_DIR = ROOT / "router"
TRANSPARENCY_SCRIPT = ROOT / "scripts" / "apply_transparency_mask.py"
TRANSPARENCY_TEST = ROOT / "tests" / "test_transparency_mask.py"
PAYLOAD_SCRIPT = ROOT / "scripts" / "compose_generation_payload.py"
PAYLOAD_TEST = ROOT / "tests" / "test_generation_payload.py"
SOURCE_TEST = ROOT / "tests" / "test_authoritative_prompt_sources.py"

errors: list[str] = []
warnings: list[str] = []


def load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception as exc:
        errors.append(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")
        return None


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_path(relative: str) -> Path | None:
    candidate = (ROOT / relative).resolve()
    try:
        candidate.relative_to(ROOT.resolve())
    except ValueError:
        errors.append(f"Prompt path escapes project root: {relative}")
        return None
    return candidate


def validate_schemas() -> dict[str, Any]:
    schemas: dict[str, Any] = {}
    schema_files = sorted(SCHEMA_DIR.glob("*.schema.json"))
    expected = {
        "session.schema.json",
        "image-analysis.schema.json",
        "color-analysis.schema.json",
        "fusion-plan.schema.json",
        "router-features.schema.json",
        "style-decision.schema.json",
        "generation-spec.schema.json",
    }
    missing = expected - {path.name for path in schema_files}
    for name in sorted(missing):
        errors.append(f"Missing schema: schemas/{name}")

    try:
        from jsonschema import Draft202012Validator  # type: ignore
    except ImportError:
        Draft202012Validator = None
        warnings.append("jsonschema is not installed; performed structural schema checks only.")

    for path in schema_files:
        data = load_json(path)
        if data is None:
            continue
        schemas[path.name] = data
        if data.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            errors.append(f"{path.relative_to(ROOT)}: expected JSON Schema draft 2020-12")
        if data.get("type") != "object":
            errors.append(f"{path.relative_to(ROOT)}: root type must be object")
        if not isinstance(data.get("properties"), dict):
            errors.append(f"{path.relative_to(ROOT)}: missing properties object")
        if Draft202012Validator is not None:
            try:
                Draft202012Validator.check_schema(data)
            except Exception as exc:
                errors.append(f"{path.relative_to(ROOT)}: invalid schema: {exc}")

    if Draft202012Validator is not None:
        example_map = {
            "examples/single/session.json": "session.schema.json",
            "examples/single/image-analysis.json": "image-analysis.schema.json",
            "examples/single/color-analysis.json": "color-analysis.schema.json",
            "examples/single/generation-spec.json": "generation-spec.schema.json",
            "examples/multi-independent/session.json": "session.schema.json",
            "examples/multi-fusion/session.json": "session.schema.json",
            "examples/multi-fusion/fusion-plan.json": "fusion-plan.schema.json",
        }
        for relative, schema_name in example_map.items():
            path = ROOT / relative
            if not path.exists():
                errors.append(f"Missing example: {relative}")
                continue
            instance = load_json(path)
            schema = schemas.get(schema_name)
            if instance is None or schema is None:
                continue
            validator = Draft202012Validator(schema)
            for issue in sorted(validator.iter_errors(instance), key=lambda item: list(item.path)):
                location = ".".join(str(part) for part in issue.path) or "<root>"
                errors.append(f"{relative}:{location}: {issue.message}")
    return schemas


def validate_style_registry(path: Path, expected_mode: str) -> tuple[set[str], set[str]]:
    data = load_json(path)
    style_ids: set[str] = set()
    prompt_ids: set[str] = set()
    if not isinstance(data, dict):
        return style_ids, prompt_ids
    if data.get("source_prompt_policy") != "READ_ONLY":
        errors.append(f"{path.relative_to(ROOT)}: source_prompt_policy must be READ_ONLY")
    if data.get("border_router") != "NONE" or data.get("footer_router") != "NONE":
        errors.append(f"{path.relative_to(ROOT)}: Border/Footer routers must be NONE")
    styles = data.get("styles")
    if not isinstance(styles, list) or not styles:
        errors.append(f"{path.relative_to(ROOT)}: styles must be a non-empty list")
        return style_ids, prompt_ids
    for index, style in enumerate(styles):
        where = f"{path.relative_to(ROOT)} styles[{index}]"
        if not isinstance(style, dict):
            errors.append(f"{where}: must be an object")
            continue
        style_id = style.get("style_id")
        if not isinstance(style_id, str) or style_id in style_ids:
            errors.append(f"{where}: missing or duplicate style_id")
        else:
            style_ids.add(style_id)
        if style.get("mode") != expected_mode:
            errors.append(f"{where}: mode must be {expected_mode}")
        source = style.get("source_prompt", {})
        if source.get("policy") != "READ_ONLY":
            errors.append(f"{where}: source prompt policy must be READ_ONLY")
        prompt_id = source.get("prompt_id")
        if not isinstance(prompt_id, str) or prompt_id in prompt_ids:
            errors.append(f"{where}: missing or duplicate prompt_id")
        else:
            prompt_ids.add(prompt_id)
        if style.get("border", {}).get("embedded_in_style") is not True:
            errors.append(f"{where}: Border must be embedded in Style")
        if style.get("footer", {}).get("embedded_in_style") is not True:
            errors.append(f"{where}: Footer must be embedded in Style")
    return style_ids, prompt_ids


def validate_router(path: Path, registry_styles: set[str]) -> None:
    data = load_json(path)
    if not isinstance(data, dict):
        return
    algorithm = data.get("algorithm", {})
    if algorithm.get("one_style_only") is not True:
        errors.append(f"{path.relative_to(ROOT)}: one_style_only must be true")
    if algorithm.get("randomization") is not False:
        errors.append(f"{path.relative_to(ROOT)}: randomization must be false")
    if algorithm.get("ratio_compatibility_weight_cap") != 5:
        errors.append(f"{path.relative_to(ROOT)}: ratio compatibility cap must be 5")
    router_styles = set(data.get("styles", {}))
    if router_styles != registry_styles:
        errors.append(
            f"{path.relative_to(ROOT)}: router/registry style mismatch; "
            f"missing={sorted(registry_styles - router_styles)}, extra={sorted(router_styles - registry_styles)}"
        )
    for style_id, config in data.get("styles", {}).items():
        if not isinstance(config.get("hard_gates"), list):
            errors.append(f"{path.relative_to(ROOT)} {style_id}: hard_gates must be a list")
        rules = config.get("score_rules")
        if not isinstance(rules, list):
            errors.append(f"{path.relative_to(ROOT)} {style_id}: score_rules must be a list")
            continue
        for index, rule in enumerate(rules):
            if not isinstance(rule.get("weight"), (int, float)):
                errors.append(f"{path.relative_to(ROOT)} {style_id} rule[{index}]: weight must be numeric")


def validate_prompts(expected_prompt_ids: set[str], require_all: bool) -> None:
    path = REGISTRY_DIR / "prompt-version-registry.json"
    data = load_json(path)
    if not isinstance(data, dict):
        return
    if data.get("source_prompt_policy") != "READ_ONLY":
        errors.append("registry/prompt-version-registry.json: policy must be READ_ONLY")
    records = data.get("prompts")
    if not isinstance(records, list):
        errors.append("registry/prompt-version-registry.json: prompts must be a list")
        return
    seen: set[str] = set()
    placeholder_count = 0
    for record in records:
        prompt_id = record.get("prompt_id")
        if not isinstance(prompt_id, str) or prompt_id in seen:
            errors.append("registry/prompt-version-registry.json: missing or duplicate prompt_id")
            continue
        seen.add(prompt_id)
        active = record.get("active_version")
        versions = record.get("versions")
        if not isinstance(versions, dict) or not versions:
            errors.append(f"{prompt_id}: versions must be a non-empty object")
            continue
        if active is None:
            placeholder_count += 1
            statuses = {value.get("status") for value in versions.values() if isinstance(value, dict)}
            if statuses != {"placeholder_missing_source"}:
                errors.append(f"{prompt_id}: null active_version is allowed only for a placeholder")
            for version, entry in versions.items():
                prompt_path = safe_path(entry.get("path", ""))
                if prompt_path is None or not prompt_path.exists():
                    errors.append(f"{prompt_id} {version}: placeholder path missing")
                    continue
                text = prompt_path.read_text(encoding="utf-8", errors="replace")
                if "SOURCE_PROMPT_PLACEHOLDER" not in text:
                    errors.append(f"{prompt_id} {version}: guarded placeholder marker missing")
            message = f"{prompt_id}: complete source prompt is unavailable; generation is blocked for this Style"
            if require_all:
                errors.append(message)
            else:
                warnings.append(message)
            continue
        if active not in versions:
            errors.append(f"{prompt_id}: active_version {active!r} is not registered")
            continue
        if record.get("mode") != "global":
            orientation_versions = record.get("active_versions_by_orientation")
            if orientation_versions != {"portrait": "v3", "landscape": "v4"}:
                errors.append(
                    f"{prompt_id}: active_versions_by_orientation must map portrait=v3 and landscape=v4"
                )
            else:
                for orientation, version_id in orientation_versions.items():
                    if version_id not in versions:
                        errors.append(
                            f"{prompt_id}: {orientation} active version {version_id!r} is not registered"
                        )
        for version, entry in versions.items():
            if entry.get("immutable") is not True:
                errors.append(f"{prompt_id} {version}: immutable must be true")
            if entry.get("status") != "verified_source":
                errors.append(f"{prompt_id} {version}: registered versions must be verified_source")
            relative = entry.get("path")
            if not isinstance(relative, str):
                errors.append(f"{prompt_id} {version}: path is required")
                continue
            prompt_path = safe_path(relative)
            if prompt_path is None or not prompt_path.is_file():
                errors.append(f"{prompt_id} {version}: prompt path missing: {relative}")
                continue
            expected_hash = entry.get("sha256")
            actual_hash = sha256(prompt_path)
            if expected_hash != actual_hash:
                errors.append(f"{prompt_id} {version}: SHA-256 mismatch")
            first_bytes = prompt_path.read_bytes()[:256]
            if b"SOURCE_PROMPT_PLACEHOLDER" in first_bytes:
                errors.append(f"{prompt_id} {version}: verified source contains placeholder marker")
            if os.stat(prompt_path).st_mode & 0o222:
                warnings.append(f"{prompt_id} {version}: source prompt is writable; hash still protects integrity")
    if seen != expected_prompt_ids:
        errors.append(
            "Prompt registry coverage mismatch; "
            f"missing={sorted(expected_prompt_ids - seen)}, extra={sorted(seen - expected_prompt_ids)}"
        )
    if placeholder_count > 1:
        errors.append(f"Expected at most one known placeholder, found {placeholder_count}")


def validate_transparency_pipeline() -> None:
    for path, label in (
        (TRANSPARENCY_SCRIPT, "transparency processor"),
        (TRANSPARENCY_TEST, "transparency regression test"),
    ):
        if not path.is_file():
            errors.append(f"Missing {label}: {path.relative_to(ROOT)}")

    policy_path = ROOT / "rules" / "transparency-policy.md"
    if not policy_path.is_file():
        errors.append("Missing transparency policy: rules/transparency-policy.md")
    else:
        policy = policy_path.read_text(encoding="utf-8")
        required_terms = (
            "RGBA",
            "--verify-only",
            "apply_transparency_mask.py",
            "1536×1024",
        )
        for term in required_terms:
            if term not in policy:
                errors.append(f"rules/transparency-policy.md: missing mandatory term {term!r}")

    try:
        from PIL import Image  # noqa: F401
    except ImportError:
        errors.append("Pillow is required by scripts/apply_transparency_mask.py")


def validate_prompt_payload_pipeline() -> None:
    for path, label in (
        (PAYLOAD_SCRIPT, "byte-exact payload composer"),
        (PAYLOAD_TEST, "payload regression test"),
        (SOURCE_TEST, "authoritative source regression test"),
    ):
        if not path.is_file():
            errors.append(f"Missing {label}: {path.relative_to(ROOT)}")

    if PAYLOAD_SCRIPT.is_file():
        payload_script = PAYLOAD_SCRIPT.read_text(encoding="utf-8")
        required_terms = (
            "STYLE_SOURCE_PROMPT_ONLY_VERBATIM",
            "orientation",
            "style_card_summary",
            "runtime_json",
            "global_policy_text",
        )
        for term in required_terms:
            if term not in payload_script:
                errors.append(f"scripts/compose_generation_payload.py: missing isolation term {term!r}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--require-all-prompts",
        action="store_true",
        help="Fail when any source prompt is represented by a guarded placeholder.",
    )
    parser.add_argument("--json", action="store_true", help="Emit a machine-readable report.")
    args = parser.parse_args()

    validate_schemas()
    single_styles, single_prompts = validate_style_registry(
        REGISTRY_DIR / "single-style-registry.json", "single"
    )
    multi_styles, multi_prompts = validate_style_registry(
        REGISTRY_DIR / "multi-style-registry.json", "multi_fusion"
    )
    validate_router(ROUTER_DIR / "single-router.json", single_styles)
    validate_router(ROUTER_DIR / "multi-router.json", multi_styles)
    registered_prompts = single_prompts | multi_prompts | {"global.negative"}
    validate_prompts(registered_prompts, args.require_all_prompts)
    validate_transparency_pipeline()
    validate_prompt_payload_pipeline()

    forbidden_router_files = [
        path for path in ROUTER_DIR.iterdir()
        if path.name.lower().startswith(("border", "footer"))
    ]
    for path in forbidden_router_files:
        errors.append(f"Forbidden separate router file: {path.relative_to(ROOT)}")

    report = {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "counts": {
            "schemas": len(list(SCHEMA_DIR.glob("*.schema.json"))),
            "single_styles": len(single_styles),
            "multi_styles": len(multi_styles),
            "registered_prompts": len(registered_prompts),
        },
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("youpiao validation:", "PASS" if report["ok"] else "FAIL")
        for item in warnings:
            print(f"WARNING: {item}")
        for item in errors:
            print(f"ERROR: {item}")
        print(
            "Checked "
            f"{report['counts']['schemas']} schemas, "
            f"{report['counts']['single_styles']} single styles, "
            f"{report['counts']['multi_styles']} multi styles, "
            f"{report['counts']['registered_prompts']} prompt mappings."
        )
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
