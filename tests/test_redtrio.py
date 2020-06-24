from redtrio import __version__
from importlib import metadata


def test_version():
    assert __version__ == metadata.version("redtrio")
