import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_PRESET_DIR = Path(__file__).resolve().parent.parent / "data"


@lru_cache(maxsize=None)
def load_json_resource(filename: str) -> dict[str, Any]:
    """Load and cache a JSON resource from the packaged preset directory."""
    content = (_PRESET_DIR / filename).read_text()
    data: dict[str, Any] = json.loads(content)
    if not isinstance(data, dict):  # pyright: ignore
        raise TypeError(f"Resource {filename} must contain a JSON object")
    return data


def clear_data_cache() -> None:
    """Clear internal resource cache, useful for tests."""
    load_json_resource.cache_clear()
