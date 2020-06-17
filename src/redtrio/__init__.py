from importlib import metadata

try:
    __version__ = metadata.version(__name__)
except:  # pragma: no cover
    __version__ = "unknown"
