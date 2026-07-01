from viroconstrictor_data.domain.models import Platform
from viroconstrictor_data.presets.resolver import (
    resolve_by_values,
    resolve_default_preset,
)


def get(pathogen: str, platform: Platform) -> dict[str, dict[str, str]]:
    """Resolve the effective stage-main command set for a pathogen and platform."""
    return resolve_by_values(pathogen=pathogen, stage="main", platform=platform)


def get_defaults(platform: Platform) -> dict[str, dict[str, str]]:
    """Resolve stage-main defaults only, without pathogen-specific overrides."""
    return resolve_default_preset(stage="main", platform=platform)
