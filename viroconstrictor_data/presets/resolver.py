from copy import deepcopy
from typing import Any

from viroconstrictor_data.aliases import resolve_pathogen_alias
from viroconstrictor_data.domain.exceptions import (
    InvalidPlatformError,
    InvalidPresetDataError,
    InvalidStageError,
)
from viroconstrictor_data.domain.load_json import load_json_resource
from viroconstrictor_data.domain.models import Platform, PresetRequest, Stage

_PLATFORMS: tuple[Platform, ...] = ("illumina", "iontorrent", "nanopore")
_STAGES: tuple[Stage, ...] = ("main", "match_ref")
_STAGE_FILE_MAP = {
    "main": "main_params.json",
    "match_ref": "match_ref_params.json",
}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged


def _load_stage(stage: Stage) -> dict[str, Any]:
    if stage not in _STAGES:
        raise InvalidStageError(f"Unknown stage: {stage}")
    return load_json_resource(_STAGE_FILE_MAP[stage])


def _resolve_stage_config(pathogen: str, stage: Stage) -> dict[str, Any]:
    stage_data = _load_stage(stage)
    default = stage_data.get("DEFAULT")
    if not isinstance(default, dict):
        raise InvalidPresetDataError(f"Stage '{stage}' is missing DEFAULT object")

    overrides = stage_data.get(pathogen, {})
    if not isinstance(overrides, dict):
        raise InvalidPresetDataError(
            f"Pathogen '{pathogen}' in stage '{stage}' is not an object"
        )

    return _deep_merge(default, overrides)


def _resolve_stage_default_config(stage: Stage) -> dict[str, Any]:
    stage_data = _load_stage(stage)
    default = stage_data.get("DEFAULT")
    if not isinstance(default, dict):
        raise InvalidPresetDataError(f"Stage '{stage}' is missing DEFAULT object")
    return deepcopy(default)


def _resolve_platform_commands(
    merged: dict[str, Any],
    platform: Platform,
) -> dict[str, dict[str, str]]:
    if platform not in _PLATFORMS:
        raise InvalidPlatformError(f"Unknown platform: {platform}")

    resolved: dict[str, dict[str, str]] = {}
    for step, step_data in merged.items():
        if not isinstance(step_data, dict):
            raise InvalidPresetDataError(f"Step '{step}' must be an object")

        bin_map = step_data.get("bin_by_platform")
        flags_map = step_data.get("flags_by_platform")
        if not isinstance(bin_map, dict) or not isinstance(flags_map, dict):
            raise InvalidPresetDataError(
                f"Step '{step}' must contain bin_by_platform and flags_by_platform objects"
            )

        resolved[step] = {
            "bin": str(bin_map.get(platform, "")),
            "flags": str(flags_map.get(platform, "")),
        }

    return resolved


def resolve_preset(request: PresetRequest) -> dict[str, dict[str, str]]:
    """Resolve merged step parameters for a pathogen/stage/platform request."""
    if request.defaults_only:
        merged = _resolve_stage_default_config(stage=request.stage)
    else:
        canonical = resolve_pathogen_alias(request.pathogen)
        merged = _resolve_stage_config(pathogen=canonical, stage=request.stage)
    return _resolve_platform_commands(merged=merged, platform=request.platform)


def resolve_by_values(
    pathogen: str,
    stage: Stage,
    platform: Platform,
    defaults_only: bool = False,
) -> dict[str, dict[str, str]]:
    """Convenience API for callers that do not build PresetRequest objects."""
    return resolve_preset(
        PresetRequest(
            pathogen=pathogen,
            stage=stage,
            platform=platform,
            defaults_only=defaults_only,
        )
    )


def resolve_default_preset(
    stage: Stage,
    platform: Platform,
) -> dict[str, dict[str, str]]:
    """Resolve stage defaults only, without pathogen-specific overrides."""
    return _resolve_platform_commands(
        merged=_resolve_stage_default_config(stage=stage),
        platform=platform,
    )
