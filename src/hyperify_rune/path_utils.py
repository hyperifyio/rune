"""Utilities for constructing public asset URLs.

This module provides helpers to construct deterministic, platform-independent
URLs for assets that have been extracted to an assets directory. It supports
two modes:

- Using a configured URL prefix (e.g., "/static")
- Falling back to a relative URL from the output JSON location to the
  assets directory when no prefix is configured

All returned paths use forward slashes regardless of the operating system.
"""

import os
from typing import Optional


def _ensure_forward_slashes(path: str) -> str:
    """Normalize path separators to forward slashes for URL usage."""
    return path.replace("\\", "/")


def build_asset_url(
    filename: str,
    output_json_path: str,
    assets_dir: str,
    assets_prefix: Optional[str] = None,
) -> str:
    """Build the public URL for an extracted asset.

    - If ``assets_prefix`` is provided, returns ``{assets_prefix}/{filename}``
      with no duplicate slashes.
    - Otherwise, computes a relative URL from the directory containing
      ``output_json_path`` to the file at ``assets_dir/filename``.

    Returned URLs always use forward slashes.
    """
    if not filename:
        raise ValueError("filename must be a non-empty string")

    if assets_prefix:
        # Avoid duplicate slashes when joining
        prefix = assets_prefix.rstrip("/")
        return f"{prefix}/{filename}"

    # Relative fallback from the output JSON's directory to the asset path
    output_dir_abs = os.path.dirname(os.path.abspath(output_json_path))
    asset_path_abs = os.path.abspath(os.path.join(assets_dir, filename))
    rel_path = os.path.relpath(asset_path_abs, start=output_dir_abs)
    return _ensure_forward_slashes(rel_path)


__all__ = ["build_asset_url"]
