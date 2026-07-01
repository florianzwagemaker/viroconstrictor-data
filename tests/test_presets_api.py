from typing import cast

import pytest

from viroconstrictor_data.domain.exceptions import (
    InvalidPlatformError,
    InvalidPresetDataError,
    InvalidStageError,
)
from viroconstrictor_data.domain.models import Platform, PresetRequest, Stage
from viroconstrictor_data.presets import (
    main,
    main_defaults,
    match_ref,
    resolve_preset,
)


def test_main_preset_resolves_platform_specific_values() -> None:
    resolved = main("INFLUENZA", "nanopore")
    assert "raw_alignment" in resolved
    assert resolved["raw_alignment"]["bin"] == "minimap2"
    assert "--splice" in resolved["raw_alignment"]["flags"]


def test_match_ref_preset_uses_default_then_override() -> None:
    resolved = match_ref("ENTEROVIRUS", "illumina")
    assert resolved["alignment_filtering"]["bin"] == "samtools"
    assert "-q 20" in resolved["alignment_filtering"]["flags"]


def test_resolve_request_with_alias() -> None:
    request = PresetRequest(
        pathogen="flu",
        stage="main",
        platform="illumina",
    )
    resolved = resolve_preset(request)
    assert resolved["alignment"]["bin"] == "minimap2"


def test_defaults_only_request_ignores_pathogen_override() -> None:
    request = PresetRequest(
        pathogen="flu",
        stage="main",
        platform="nanopore",
        defaults_only=True,
    )
    resolved = resolve_preset(request)
    assert "--cut_front" in resolved["qc"]["flags"]
    assert "--splice" not in resolved["raw_alignment"]["flags"]


def test_main_defaults_helper_returns_default_values() -> None:
    resolved = main_defaults("nanopore")
    assert "--cut_front" in resolved["qc"]["flags"]
    assert "--splice" not in resolved["raw_alignment"]["flags"]


def test_preset_request_normalizes_string_values() -> None:
    request = PresetRequest(
        pathogen="  Flu  ",
        stage=cast(Stage, " Main "),
        platform=cast(Platform, " Illumina "),
    )
    assert request.pathogen == "flu"
    assert request.stage == "main"
    assert request.platform == "illumina"


def test_preset_request_rejects_empty_pathogen() -> None:
    with pytest.raises(InvalidPresetDataError):
        PresetRequest(pathogen="   ", stage="main", platform="illumina")


def test_preset_request_rejects_invalid_stage() -> None:
    with pytest.raises(InvalidStageError):
        PresetRequest(
            pathogen="flu",
            stage=cast(Stage, "unknown"),
            platform="illumina",
        )


def test_preset_request_rejects_invalid_platform() -> None:
    with pytest.raises(InvalidPlatformError):
        PresetRequest(
            pathogen="flu",
            stage="main",
            platform=cast(Platform, "pacbio"),
        )
