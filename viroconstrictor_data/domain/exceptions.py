class PresetError(ValueError):
    """Base class for preset resolution errors."""


class UnknownPathogenError(PresetError):
    """Raised when a pathogen alias or canonical ID is unknown."""


class InvalidStageError(PresetError):
    """Raised when an unknown stage is requested."""


class InvalidPlatformError(PresetError):
    """Raised when an unknown platform is requested."""


class InvalidPresetDataError(PresetError):
    """Raised when preset data does not match expected shape."""
