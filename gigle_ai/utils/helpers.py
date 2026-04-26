"""Shared utility helpers for Gigle-AI."""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Any


def encode_image(source: bytes | str | Path) -> str:
    """
    Return a base64-encoded string for *source*.

    Parameters
    ----------
    source:
        Raw image bytes, a file path (``str`` or :class:`pathlib.Path`),
        or a string that is already base64-encoded.

    Returns
    -------
    str:
        Base64-encoded image data.
    """
    if isinstance(source, (str, Path)):
        path = Path(source)
        if path.exists():
            source = path.read_bytes()
        else:
            # Assume the string is already base64-encoded
            return str(source)
    return base64.b64encode(source).decode()


def decode_image(encoded: str) -> bytes:
    """
    Decode a base64-encoded image string back to raw bytes.

    Parameters
    ----------
    encoded:
        Base64-encoded image data.

    Returns
    -------
    bytes:
        Raw image bytes.

    Raises
    ------
    ValueError:
        If *encoded* is not valid base64.
    """
    try:
        return base64.b64decode(encoded, validate=True)
    except Exception as exc:
        raise ValueError("Invalid base64 data") from exc


def build_response(response_type: str, result: Any) -> dict:
    """
    Wrap an AI result in a standard response envelope.

    Parameters
    ----------
    response_type:
        One of ``"text"``, ``"image"``, or ``"chat"``.
    result:
        The raw result from the AI engine.

    Returns
    -------
    dict:
        ``{"type": response_type, "result": result}``
    """
    return {"type": response_type, "result": result}
