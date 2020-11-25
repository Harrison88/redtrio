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


async def test_smembers(client):
    """It returns the proper responses for SMEMBERS."""
    key = "midlevel_smembers_test"

    # SMEMBERS returns the members of the set.
    expected = set()
    actual = await client.smembers(key)
    assert actual == expected

    await client.sadd(key, "a", "b")
    expected = set(["a".encode(), "b".encode()])
    actual = await client.smembers(key)
    assert actual == expected


async def test_sdiff(client):
    """It returns the proper responses for SDIFF."""
    key = "midlevel_sdiff_test"
    key2 = key + "2"
    key3 = key + "3"

    a, b, c = "a", "b", "c"
    await client.sadd(key, a, b, c)

    # SDIFF returns the result of subtracting the second and subsequent sets from
    # the first set.
    expected = set([a.encode(), b.encode(), c.encode()])
    actual = await client.sdiff(key, key2)
    assert actual == expected

    await client.sadd(key2, a, c)
    expected = set([b.encode()])
    actual = await client.sdiff(key, key2)
    assert actual == expected

    await client.sadd(key3, b)
    expected = set()
    actual = await client.sdiff(key, key2, key3)
    assert actual == expected


async def test_sdiffstore(client):
    """It returns the proper responses for SDIFFSTORE."""
    destination = "midlevel_sdiffstore_destination"
    key = "midlevel_sdiffstore_test"
    key2 = key + "2"
    key3 = key + "3"

    a, b, c = "a", "b", "c"
    await client.sadd(key, a, b, c)

    # SDIFFSTORE performs SDIFF, then stores the result in the destination key
    # and returns the number of elements in the result.
    expected = 3
    actual = await client.sdiffstore(destination, key, key2)
    assert actual == expected

    await client.sadd(key2, a, c)
    expected = 1
    actual = await client.sdiffstore(destination, key, key2)
    assert actual == expected
    expected = set([b.encode()])
    actual = await client.smembers(destination)
    assert actual == expected

    await client.sadd(key3, b)
    expected = 0
    actual = await client.sdiffstore(destination, key, key2, key3)
    assert actual == expected


async def test_sinter(client):
    """It returns the proper responses for SINTER."""
    key = "midlevel_sinter_test"
    key2 = key + "2"
    key3 = key + "3"

    a, b, c = "a", "b", "c"
    await client.sadd(key, a, b, c)

    # SINTER returns the intersection of all sets.
    expected = set()
    actual = await client.sinter(key, key2)
    assert actual == expected

    await client.sadd(key2, b, c)
    expected = set([b.encode(), c.encode()])
    actual = await client.sinter(key, key2)
    assert actual == expected

    await client.sadd(key3, a, b)
    expected = set([b.encode()])
    actual = await client.sinter(key, key2, key3)
    assert actual == expected


async def test_sinterstore(client):
    """It returns the proper responses for SINTERSTORE."""
    destination = "midlevel_sinterstore_destination"
    key = "midlevel_sinterstore_test"
    key2 = key + "2"
    key3 = key + "3"

    a, b, c = "a", "b", "c"
    await client.sadd(key, a, b, c)

    # SINTERSTORE takes the intersection of all given sets and stores the result
    # in the destination key, then returns the number of members in the result.

    expected = 0
    actual = await client.sinterstore(destination, key, key2)
    assert actual == expected

    await client.sadd(key2, b, c)
    expected = 2
    actual = await client.sinterstore(destination, key, key2)
    assert actual == expected
    expected = set([b.encode(), c.encode()])
    actual = await client.smembers(destination)
    assert actual == expected

    await client.sadd(key3, a, b)
    expected = 1
    actual = await client.sinterstore(destination, key, key2, key3)
    assert actual == expected
