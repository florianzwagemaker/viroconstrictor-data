import json
from importlib import resources

__version__ = "0.0.1"
__prog__ = "viroconstrictor-data"

# Load schema version from manifest at import time
_manifest = json.loads(
    resources.files("viroconstrictor_data").joinpath("manifest.json").read_text()
)
SCHEMA_VERSION: str = _manifest["schema_version"]

def get_manifest() -> dict:
    """Load and return manifest.json via importlib.resources."""
    return json.loads(
        resources.files("viroconstrictor_data").joinpath("manifest.json").read_text()
    )


def preset_data_path() -> resources.abc.Traversable:
    """Return the traversable root of the package for downstream consumers."""
    return resources.files("viroconstrictor_data")