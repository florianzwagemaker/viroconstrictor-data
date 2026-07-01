from typing import Any, cast

from viroconstrictor_data.aliases import get_aliases, normalize_pathogen_name
from viroconstrictor_data.domain.load_json import load_json_resource
from viroconstrictor_data.domain.models import ValidationIssue

_PLATFORMS = ("illumina", "iontorrent", "nanopore")
_REQUIRED_STEP_KEYS = ("bin_by_platform", "flags_by_platform")
_MUST_BE_OBJECT = "must be an object"


def _add(issues: list[ValidationIssue], path: str, message: str) -> None:
    issues.append(ValidationIssue(path=path, message=message))


def _validate_default_step_shape(
    stage_name: str,
    step_name: str,
    step_data: Any,
    issues: list[ValidationIssue],
) -> None:
    if not isinstance(step_data, dict):
        _add(issues, f"{stage_name}.DEFAULT.{step_name}", _MUST_BE_OBJECT)
        return

    step_dict = cast(dict[str, Any], step_data)

    for required in _REQUIRED_STEP_KEYS:
        if required not in step_dict:
            _add(
                issues,
                f"{stage_name}.DEFAULT.{step_name}",
                f"missing required key: {required}",
            )

    for key in _REQUIRED_STEP_KEYS:
        value = step_dict.get(key)
        if not isinstance(value, dict):
            _add(
                issues,
                f"{stage_name}.DEFAULT.{step_name}.{key}",
                _MUST_BE_OBJECT,
            )
            continue

        value_dict = cast(dict[str, Any], value)

        for platform in _PLATFORMS:
            if platform not in value_dict:
                _add(
                    issues,
                    f"{stage_name}.DEFAULT.{step_name}.{key}",
                    f"missing platform key: {platform}",
                )


def _get_default_section(
    stage_name: str,
    raw: dict[str, Any],
    issues: list[ValidationIssue],
) -> dict[str, Any] | None:
    default = raw.get("DEFAULT")
    if not isinstance(default, dict):
        _add(issues, f"{stage_name}.DEFAULT", "must exist and be an object")
        return None

    return cast(dict[str, Any], default)


def _validate_override_key_platforms(
    stage_name: str,
    pathogen: str,
    step_name: str,
    key: str,
    step_data: dict[str, Any],
    issues: list[ValidationIssue],
) -> None:
    if key not in step_data:
        return

    value = step_data[key]
    if not isinstance(value, dict):
        _add(
            issues,
            f"{stage_name}.{pathogen}.{step_name}.{key}",
            _MUST_BE_OBJECT,
        )
        return

    value_dict = cast(dict[str, Any], value)

    for platform in value_dict:
        if platform not in _PLATFORMS:
            _add(
                issues,
                f"{stage_name}.{pathogen}.{step_name}.{key}.{platform}",
                "unknown platform",
            )


def _validate_override_step(
    stage_name: str,
    pathogen: str,
    step_name: str,
    step_data: Any,
    known_steps: set[str],
    issues: list[ValidationIssue],
) -> None:
    if step_name not in known_steps:
        _add(
            issues,
            f"{stage_name}.{pathogen}.{step_name}",
            "unknown step name",
        )
        return

    if not isinstance(step_data, dict):
        _add(
            issues,
            f"{stage_name}.{pathogen}.{step_name}",
            _MUST_BE_OBJECT,
        )
        return

    step_dict = cast(dict[str, Any], step_data)
    for key in _REQUIRED_STEP_KEYS:
        _validate_override_key_platforms(
            stage_name=stage_name,
            pathogen=pathogen,
            step_name=step_name,
            key=key,
            step_data=step_dict,
            issues=issues,
        )


def _validate_pathogen_overrides(
    stage_name: str,
    raw: dict[str, Any],
    known_steps: set[str],
    issues: list[ValidationIssue],
) -> None:
    for pathogen, overrides in raw.items():
        if pathogen == "DEFAULT":
            continue
        if not isinstance(overrides, dict):
            _add(issues, f"{stage_name}.{pathogen}", _MUST_BE_OBJECT)
            continue

        overrides_dict = cast(dict[str, Any], overrides)
        for step_name, step_data in overrides_dict.items():
            _validate_override_step(
                stage_name=stage_name,
                pathogen=pathogen,
                step_name=step_name,
                step_data=step_data,
                known_steps=known_steps,
                issues=issues,
            )


def _validate_stage_file(stage_name: str, filename: str) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    raw = load_json_resource(filename)

    default = _get_default_section(stage_name=stage_name, raw=raw, issues=issues)
    if default is None:
        return issues

    for step_name, step_data in default.items():
        _validate_default_step_shape(stage_name, step_name, step_data, issues)

    known_steps: set[str] = set(default.keys())

    _validate_pathogen_overrides(
        stage_name=stage_name,
        raw=raw,
        known_steps=known_steps,
        issues=issues,
    )

    return issues


def _validate_aliases() -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    aliases = get_aliases()
    normalized_to_canonical: dict[str, str] = {}

    for canonical, values in aliases.items():
        labels = [canonical, *values]
        for label in labels:
            normalized = normalize_pathogen_name(label)
            if not normalized:
                _add(
                    issues,
                    f"aliases.{canonical}",
                    "contains an empty alias after normalization",
                )
                continue
            mapped = normalized_to_canonical.get(normalized)
            if mapped and mapped != canonical:
                _add(
                    issues,
                    f"aliases.{canonical}",
                    f"alias collision for '{label}' with canonical '{mapped}'",
                )
            else:
                normalized_to_canonical[normalized] = canonical

    return issues


def validate_package() -> list[ValidationIssue]:
    """Validate all packaged preset and alias data."""
    issues: list[ValidationIssue] = []
    issues.extend(_validate_stage_file("main", "main_params.json"))
    issues.extend(_validate_stage_file("match_ref", "match_ref_params.json"))
    issues.extend(_validate_aliases())
    return issues


def assert_valid_package() -> None:
    """Raise a ValueError if packaged data validation finds any issue."""
    issues = validate_package()
    if issues:
        summary = "; ".join(f"{i.path}: {i.message}" for i in issues)
        raise ValueError(f"Preset package validation failed: {summary}")
