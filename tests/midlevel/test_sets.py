"""This module contains the tests for Redis' sets commands."""

import pytest

from redtrio.midlevel import MidlevelClient


@pytest.fixture
async def client():
    """A fresh client for every test.

    Also flushes the database to prevent conflicts.

    Returns:
        An instance of :class:`midlevel.MidlevelClient`.
    """
    client = MidlevelClient()
    await client.call("FLUSHALL")
    return client


async def test_sadd(client):
    """It returns the proper responses for SADD."""
    key = "midlevel_sadd_test"
    value = "Hello, Sets!"

    # SADD returns the number of elements added to the set, not including any
    # elements which were already in the set.
    expected = 1
    actual = await client.sadd(key, value)
    assert actual == expected

    # Adding the same value again should return 0, since it's already in the set.
    expected = 0
    actual = await client.sadd(key, value)
    assert actual == expected

    # Adding two new values should return 2.
    expected = 2
    actual = await client.sadd(key, "new", "also new")
    assert actual == expected


async def test_scard(client):
    """It returns the proper responses for SCARD."""
    key = "midlevel_scard_test"

    # SCARD returns the number of elements in a set, or 0 if it doesn't exist.
    expected = 0
    actual = await client.scard(key)
    assert actual == expected

    await client.sadd(key, "value")
    expected = 1
    actual = await client.scard(key)
    assert actual == expected
