"""Global configuration for Rune CLI and library."""

from typing import Optional


class RuneConfig:
    """Holds runtime configuration values for Rune.

    Attributes
    -----------
    assetsPrefix: Optional[str]
        Prefix to prepend to emitted asset URLs. When None, no prefixing is applied.
    """

    def __init__(self) -> None:
        self.assetsPrefix: Optional[str] = None
        self.assetsDir: Optional[str] = None


# Singleton config used across the package
config = RuneConfig()
