"""Utilities for handling embedded attachments and asset extraction.

This module provides helpers to decode data URLs, compute content hashes,
derive file extensions, and write extracted attachments to a designated
assets directory using deterministic, content-addressed filenames.

The primary entry point is `extract_data_url_to_assets_dir` which accepts a
data URL string, an output directory, and an optional suggested original
filename to preserve the extension when available.
"""

from __future__ import annotations

import base64
import hashlib
import os
from pathlib import Path
from typing import Tuple, Optional
from urllib.parse import unquote_to_bytes


def _parse_data_url(data_url: str) -> Tuple[str, bytes]:
    """Parse a data URL and return a tuple of (mime_type, bytes).

    Raises ValueError when the input is not a valid data URL.
    """
    if not isinstance(data_url, str) or not data_url.startswith("data:"):
        raise ValueError("Input is not a valid data URL: missing 'data:' prefix")

    try:
        header, payload = data_url.split(",", 1)
    except ValueError as exc:
        raise ValueError("Invalid data URL: missing comma separator") from exc

    header_meta = header[5:]  # drop 'data:'
    is_base64 = False
    mime_type = ""

    if ";" in header_meta:
        parts = header_meta.split(";")
        mime_type = parts[0] or ""
        is_base64 = any(p.lower() == "base64" for p in parts[1:])
    else:
        mime_type = header_meta or ""

    if is_base64:
        try:
            data_bytes = base64.b64decode(payload, validate=True)
        except Exception as exc:
            raise ValueError("Invalid base64 payload in data URL") from exc
    else:
        # Percent-decoded raw payload
        try:
            data_bytes = unquote_to_bytes(payload)
        except Exception as exc:
            raise ValueError("Invalid percent-encoded payload in data URL") from exc

    return mime_type, data_bytes


_MIME_TO_EXT = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/gif": ".gif",
    "image/svg+xml": ".svg",
    "image/webp": ".webp",
    "text/plain": ".txt",
    "text/css": ".css",
    "text/html": ".html",
    "application/json": ".json",
    "application/pdf": ".pdf",
}


def _derive_extension(mime_type: str, suggested_name: Optional[str]) -> str:
    """Return an extension beginning with '.'

    Prefers the extension from suggested_name when provided; otherwise maps
    from MIME type. Returns an empty string when neither yields a result.
    """
    if suggested_name:
        ext = Path(suggested_name).suffix
        if ext:
            return ext
    return _MIME_TO_EXT.get(mime_type.lower(), "")


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_data_url_to_assets_dir(
    data_url: str,
    assets_dir: str | os.PathLike[str],
    suggested_name: Optional[str] = None,
) -> str:
    """Extract a data URL payload to `assets_dir` using a hashed filename.

    - File name is <sha256(content)> + <extension>
    - Extension is preserved from `suggested_name` when available; otherwise
      derived from the data URL MIME type where possible
    - Idempotent: repeated calls with identical content yield the same path
      and do not rewrite the file when it already exists

    Returns the absolute file system path of the written (or existing) file.
    """
    mime_type, data_bytes = _parse_data_url(data_url)
    file_hash = _sha256_hex(data_bytes)
    ext = _derive_extension(mime_type, suggested_name)

    target_dir = Path(assets_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{file_hash}{ext}"
    target_path = target_dir / filename

    if target_path.exists():
        return str(target_path)

    # Write atomically; avoid partial files on crashes
    tmp_path = target_path.with_suffix(target_path.suffix + ".tmp")
    try:
        with open(tmp_path, "xb") as f:
            f.write(data_bytes)
        os.replace(tmp_path, target_path)
    finally:
        # Best-effort cleanup of tmp in case of exceptions before replace
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass

    return str(target_path)


__all__ = [
    "extract_data_url_to_assets_dir",
]
