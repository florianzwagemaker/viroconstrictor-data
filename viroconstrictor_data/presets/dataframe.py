from typing import Any

from viroconstrictor_data.domain.models import Platform, PresetRequest, Stage
from viroconstrictor_data.presets.resolver import resolve_preset


def resolve_presets_for_dataframe(
    dataframe: Any,
    *,
    stage: Stage,
    pathogen_col: str = "VIRUS",
    platform: Platform | None = None,
    platform_col: str = "PLATFORM",
    defaults_only: bool = False,
    defaults_only_col: str | None = None,
    output_col: str = "PRESET",
) -> Any:
    """Return a copy of a samplesheet dataframe with resolved presets per row.

    The caller can provide a fixed platform for all rows, or a platform column.
    If defaults_only_col is provided, that column controls whether each row should
    ignore pathogen-specific overrides (equivalent to disable-presets behavior).
    """
    if platform is None and platform_col not in dataframe.columns:
        raise ValueError(
            f"Missing platform source: provide 'platform' or include '{platform_col}' column"
        )

    if pathogen_col not in dataframe.columns:
        raise ValueError(f"Missing required pathogen column: '{pathogen_col}'")

    if defaults_only_col and defaults_only_col not in dataframe.columns:
        raise ValueError(f"Missing defaults-only column: '{defaults_only_col}'")

    resolved_values: list[dict[str, dict[str, str]]] = []
    for _, row in dataframe.iterrows():
        row_platform = platform if platform is not None else row[platform_col]
        row_defaults_only = (
            bool(row[defaults_only_col]) if defaults_only_col else defaults_only
        )

        request = PresetRequest(
            pathogen=str(row[pathogen_col]),
            stage=stage,
            platform=row_platform,
            defaults_only=row_defaults_only,
        )
        resolved_values.append(resolve_preset(request))

    result = dataframe.copy()
    result[output_col] = resolved_values
    return result
