from dataclasses import dataclass
from typing import Any, Literal, cast

from viroconstrictor_data.domain.exceptions import (
    InvalidPlatformError,
    InvalidPresetDataError,
    InvalidStageError,
)

Platform = Literal["illumina", "iontorrent", "nanopore"]
Stage = Literal["main", "match_ref"]
_ALLOWED_STAGES = {"main", "match_ref"}
_ALLOWED_PLATFORMS = {"illumina", "iontorrent", "nanopore"}


@dataclass(frozen=True)
class PresetRequest:
    """Stage/platform request for resolving a pathogen-specific preset."""

    pathogen: str
    stage: Stage
    platform: Platform
    defaults_only: bool = False

    def __post_init__(self) -> None:
        raw_pathogen: Any = self.pathogen
        if not isinstance(raw_pathogen, str):
            raise InvalidPresetDataError("pathogen must be a non-empty string")

        normalized_pathogen = raw_pathogen.strip().lower()
        if not normalized_pathogen:
            raise InvalidPresetDataError("pathogen must be a non-empty string")

        raw_stage: Any = self.stage
        if not isinstance(raw_stage, str):
            raise InvalidStageError(f"Unknown stage: {raw_stage}")
        normalized_stage = raw_stage.strip().lower()
        if normalized_stage not in _ALLOWED_STAGES:
            raise InvalidStageError(f"Unknown stage: {raw_stage}")

        raw_platform: Any = self.platform
        if not isinstance(raw_platform, str):
            raise InvalidPlatformError(f"Unknown platform: {raw_platform}")
        normalized_platform = raw_platform.strip().lower()
        if normalized_platform not in _ALLOWED_PLATFORMS:
            raise InvalidPlatformError(f"Unknown platform: {raw_platform}")

        raw_defaults_only: Any = self.defaults_only
        if not isinstance(raw_defaults_only, bool):
            raise InvalidPresetDataError("defaults_only must be a boolean")

        object.__setattr__(self, "pathogen", normalized_pathogen)
        object.__setattr__(self, "stage", cast(Stage, normalized_stage))
        object.__setattr__(self, "platform", cast(Platform, normalized_platform))


@dataclass(frozen=True)
class ValidationIssue:
    path: str
    message: str
