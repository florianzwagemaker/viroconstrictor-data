# viroconstrictor-data

Data package for ViroConstrictor preset configuration.

## Installation

```bash
pip install viroconstrictor-data
```

For development:

```bash
pip install -e .
pip install -e .[test]
```

## Scope

This repository is responsible for:

- Canonical preset data for `main` and `match_ref` stages
- Pathogen alias mapping
- Preset parsing, merge, and resolution logic
- Data validation logic

This repository does **not** include pipeline CLI parsing or runtime orchestration.

## Public Python API

This section covers the recommended starting flow for most users:

1. Resolve a user-provided virus label to a canonical preset alias.
2. Resolve the effective preset for one sample.
3. Apply that logic to a full samplesheet dataframe.

### 1) Resolve Pathogen Alias

```python
from viroconstrictor_data import resolve_pathogen_alias

canonical = resolve_pathogen_alias("covid")
# canonical == "SARSCOV2"
```

### 2) Resolve Preset For One Sample

```python
from viroconstrictor_data import PresetRequest, resolve_preset

resolved = resolve_preset(
    PresetRequest(pathogen="flu", stage="main", platform="illumina", defaults_only=False) # defaults_only is optional, used with --disable-presets flag
)
```

`resolve_preset(...)` return per-step command config in this shape:

```python
{
	"alignment": {
		"bin": "minimap2",
		"flags": "--secondary=no -ax sr"
	},
	...
}
```

### 3) Resolve Presets For A Samplesheet

When your pipeline has a per-sample dataframe (for example columns like `SAMPLE`, `VIRUS`, `REFERENCE`, ...), resolve presets row-by-row and attach them as a new column.

```python
import pandas as pd

from viroconstrictor_data.presets import resolve_presets_for_dataframe

df = pd.DataFrame(
    [
        {"SAMPLE": "s1", "VIRUS": "INFLUENZA", "REFERENCE": "...", "DISABLE_PRESETS": False},
        {"SAMPLE": "s2", "VIRUS": "INFLUENZA", "REFERENCE": "...", "DISABLE_PRESETS": True},
    ]
)

resolved = resolve_presets_for_dataframe(
    df,
    stage="main",
    platform="nanopore",                  # or provide per-row PLATFORM column
    defaults_only_col="DISABLE_PRESETS",  # optional per-row disable-presets behavior
    output_col="PRESET",
)

# resolved.loc[i, "PRESET"] now contains the effective per-step {bin, flags}
```

## Specialized API (Advanced)

Use these helpers when you need more control than the default flow above.

### Stage-Specific Helpers

```python
from viroconstrictor_data.presets import (
    main,
    main_defaults,
    match_ref,
    match_ref_defaults,
    resolve_default_preset,
)

main_cfg = main("INFLUENZA", "nanopore")
match_ref_cfg = match_ref("ENTEROVIRUS", "illumina")

# Equivalent to --disable-presets behavior
defaults_main = main_defaults("nanopore")
defaults_match_ref = resolve_default_preset(stage="match_ref", platform="illumina")
```

### Validation And Stdout Reporting

```python
from viroconstrictor_data import print_resolved_preset, print_validation_report
from viroconstrictor_data.validation import validate_package

issues = validate_package()
assert not issues

print_resolved_preset(pathogen="INFLUENZA", stage="main", platform="nanopore")
print_validation_report()
```


## Package Layout

- `viroconstrictor_data/presets/`: preset resolution and dataframe helper code
- `viroconstrictor_data/domain/`: shared models, exceptions, and JSON loading utilities
- `viroconstrictor_data/data/`: packaged JSON data files (`manifest.json`, preset params, aliases)
