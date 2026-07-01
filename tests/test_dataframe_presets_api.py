from pathlib import Path

import pytest

from viroconstrictor_data.presets import resolve_presets_for_dataframe

pd = pytest.importorskip("pandas")


def test_resolve_presets_for_rows_with_fixed_platform() -> None:
    df = pd.DataFrame(
        [
            {"SAMPLE": "s1", "VIRUS": "INFLUENZA"},
            {"SAMPLE": "s2", "VIRUS": "SARSCOV2"},
        ]
    )

    result = resolve_presets_for_dataframe(
        df,
        stage="main",
        platform="nanopore",
    )

    assert "PRESET" in result.columns
    assert "--splice" in result.loc[0, "PRESET"]["raw_alignment"]["flags"]
    assert "--splice" not in result.loc[1, "PRESET"]["raw_alignment"]["flags"]


def test_resolve_presets_uses_per_row_disable_presets_column() -> None:
    df = pd.DataFrame(
        [
            {"SAMPLE": "s1", "VIRUS": "INFLUENZA", "DISABLE_PRESETS": True},
            {"SAMPLE": "s2", "VIRUS": "INFLUENZA", "DISABLE_PRESETS": False},
        ]
    )

    result = resolve_presets_for_dataframe(
        df,
        stage="main",
        platform="nanopore",
        defaults_only_col="DISABLE_PRESETS",
    )

    assert "--splice" not in result.loc[0, "PRESET"]["raw_alignment"]["flags"]
    assert "--splice" in result.loc[1, "PRESET"]["raw_alignment"]["flags"]


def test_resolve_presets_can_read_platform_from_dataframe() -> None:
    df = pd.DataFrame(
        [
            {"SAMPLE": "s1", "VIRUS": "ENTEROVIRUS", "PLATFORM": "illumina"},
            {"SAMPLE": "s2", "VIRUS": "ENTEROVIRUS", "PLATFORM": "nanopore"},
        ]
    )

    result = resolve_presets_for_dataframe(
        df,
        stage="match_ref",
    )

    assert "-q 20" in result.loc[0, "PRESET"]["alignment_filtering"]["flags"]
    assert "-q 20" in result.loc[1, "PRESET"]["alignment_filtering"]["flags"]


def test_resolve_presets_from_example_samplesheet_tsv() -> None:
    samplesheet_path = Path(__file__).parent / "example_samplesheet.tsv"
    df = pd.read_csv(samplesheet_path, sep="\t")

    result = resolve_presets_for_dataframe(
        df,
        stage="main",
        pathogen_col="Virus",
        platform="nanopore",
    )

    assert "PRESET" in result.columns
    assert "--splice" not in result.loc[0, "PRESET"]["raw_alignment"]["flags"]
    assert "--splice" in result.loc[1, "PRESET"]["raw_alignment"]["flags"]
    assert "--splice" in result.loc[2, "PRESET"]["raw_alignment"]["flags"]
    assert result.loc[3, "PRESET"]["raw_alignment"]["bin"] == "minimap2"
