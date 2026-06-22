import json
from pathlib import Path
from typing import Any

from viroconstrictor_data.aliases import resolve_pathogen_alias
from viroconstrictor_data.domain.models import PresetRequest
from viroconstrictor_data.presets import resolve_preset
from viroconstrictor_data.stdout import (
    print_resolved_preset,
    print_resolved_preset_request,
    print_validation_report,
)
from viroconstrictor_data.validation import validate_package

__version__ = "0.0.1"
__prog__ = "viroconstrictor-data"
_PACKAGE_DIR = Path(__file__).resolve().parent
_MANIFEST_PATH = _PACKAGE_DIR / "data" / "manifest.json"

# Load schema version from manifest at import time
_manifest = json.loads(_MANIFEST_PATH.read_text())
SCHEMA_VERSION: str = _manifest["schema_version"]


def get_manifest() -> dict[str, Any]:
    """Load and return manifest.json via package-local filesystem path."""
    return json.loads(_MANIFEST_PATH.read_text())


def preset_data_path() -> Path:
    """Return the filesystem root of the package for downstream consumers."""
    return _PACKAGE_DIR


__all__ = [
    "PresetRequest",
    "SCHEMA_VERSION",
    "get_manifest",
    "preset_data_path",
    "print_resolved_preset",
    "print_resolved_preset_request",
    "print_validation_report",
    "resolve_pathogen_alias",
    "resolve_preset",
    "validate_package",
]
