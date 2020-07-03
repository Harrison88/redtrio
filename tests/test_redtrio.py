from importlib import metadata

from redtrio import __version__


def test_version():
    """It has the correct __version__"""
    assert __version__ == metadata.version("redtrio")
