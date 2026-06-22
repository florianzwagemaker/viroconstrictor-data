import json
from dataclasses import asdict

from viroconstrictor_data.domain.models import Platform, PresetRequest, Stage
from viroconstrictor_data.presets.resolver import resolve_by_values, resolve_preset
from viroconstrictor_data.validation import validate_package


def print_resolved_preset(
    *,
    pathogen: str,
    stage: Stage,
    platform: Platform,
    defaults_only: bool = False,
    indent: int = 2,
) -> None:
    """Resolve and print preset commands as JSON to stdout."""
    resolved = resolve_by_values(
        pathogen=pathogen,
        stage=stage,
        platform=platform,
        defaults_only=defaults_only,
    )
    print(json.dumps(resolved, indent=indent, sort_keys=True))


def print_resolved_preset_request(request: PresetRequest, *, indent: int = 2) -> None:
    """Resolve and print preset commands from a PresetRequest as JSON to stdout."""
    resolved = resolve_preset(request)
    print(json.dumps(resolved, indent=indent, sort_keys=True))


def print_validation_report(*, indent: int = 2) -> None:
    """Print validation issues as JSON to stdout."""
    issues = [asdict(issue) for issue in validate_package()]
    print(json.dumps(issues, indent=indent, sort_keys=True))
