import difflib
import re

from viroconstrictor_data.domain.exceptions import UnknownPathogenError
from viroconstrictor_data.domain.load_json import load_json_resource

_NORMALIZE_PATTERN = re.compile(r"[^A-Z0-9]+")


def normalize_pathogen_name(value: str) -> str:
    """Normalize pathogen labels so aliases resolve consistently."""
    normalized = _NORMALIZE_PATTERN.sub("_", value.strip().upper()).strip("_")
    return normalized


def get_aliases() -> dict[str, list[str]]:
    """Return alias definitions keyed by canonical pathogen IDs."""
    raw = load_json_resource("preset_aliases.json")
    aliases: dict[str, list[str]] = {}
    for canonical, values in raw.items():
        if not isinstance(values, list):
            raise TypeError(f"Aliases for {canonical} must be a list")
        aliases[canonical] = [str(v) for v in values]
    return aliases


def match_preset_name(
    targetname: str, aliases: dict[str, list[str]], use_presets: bool
) -> tuple[str, float]:
    """
    The function takes a target name and a boolean flag as input, and returns a tuple containing the
    best matching preset name and a score based on string similarity, or a default value if the flag is
    False or no match is found with a high enough similarity score.
    """
    if not use_presets:
        return "DEFAULT", 0.0

    query = re.sub(r"[^_a-zA-Z0-9/-]+", "", targetname).upper()
    if query == "DEFAULT":
        return "DEFAULT", 1.0

    aliases_list = [item for group in aliases.values() for item in group]
    if not aliases_list:
        return "DEFAULT", 0.0

    best = difflib.get_close_matches(query, aliases_list, cutoff=0.0, n=1)
    if not best:
        return "DEFAULT", 0.0

    best_match = best[0]
    score = difflib.SequenceMatcher(None, a=query, b=best_match).ratio()
    if score < 0.40:
        return "DEFAULT", 0.0

    for preset, values in aliases.items():
        if best_match in values:
            return preset, score
    return "DEFAULT", 0.0


def resolve_pathogen_alias(value: str) -> str:
    """Resolve any known alias to a canonical pathogen preset key."""
    normalized = normalize_pathogen_name(value)
    aliases = get_aliases()
    canonical, _ = match_preset_name(normalized, aliases, use_presets=True)
    if canonical is None:
        raise UnknownPathogenError(f"Unknown pathogen preset alias: {value}")
    return canonical
