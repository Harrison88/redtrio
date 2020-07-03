"""Redtrio is a modern async client for Redis, supporting the new RESP3 protocol."""

from importlib import metadata

try:
    __version__ = metadata.version(__name__)
except Exception:  # pragma: no cover
    __version__ = "unknown"
