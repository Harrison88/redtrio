"""This module contains the tests for Redis' string commands."""

import time

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


async def test_get(client):
    """It returns the proper responses for GET."""
    key = "midlevel_get_test"
    value = "hello, world!"

    # When the key does not exist, None is returned.
    expected = None
    actual = await client.get(key)
    assert actual == expected

    # When the key does exist, the value (as bytes) is returned.
    await client.set(key, value)
    expected = value.encode()
    actual = await client.get(key)
    assert actual == expected


async def test_set(client):
    """It returns the proper responses for SET."""
    key = "midlevel_set_test"
    value = "Redis is cool"

    # When the value is successfully set, b"OK" is returned.
    expected = b"OK"
    actual = await client.set(key, value)
    assert actual == expected

    # When NX is specified and the key already exists, None is returned.
    expected = None
    actual = await client.set(key, value, nx=True)
    assert actual == expected

    # When XX is specified and the key does not exist, None is returned.
    expected = None
    actual = await client.set(key + "nope", value, xx=True)
    assert actual == expected

    # When EX is specified, the key should expire.
    # To make sure EX is sent correctly, we set the key, sleep, then try to get the key.
    expected = b"OK"
    actual = await client.set(key, value, ex=1)
    assert actual == expected
    time.sleep(1)
    expected = None
    actual = await client.get(key)
    assert actual == expected

    # When PX is specified, the key should expire.
    expected = b"OK"
    actual = await client.set(key, value, px=100)
    assert actual == expected
    time.sleep(0.1)
    expected = None
    actual = await client.get(key)
    assert actual == expected


async def test_set_bad_arguments(client):
    """It raises an error when bad combinations of arguments are passed."""
    with pytest.raises(ValueError):
        await client.set("random key", "random value", ex=3, keepttl=True)

    with pytest.raises(ValueError):
        await client.set("random key", "random value", ex=3, px=1000)

    with pytest.raises(ValueError):
        await client.set("random key", "random value", nx=True, xx=True)


async def test_set_keepttl(client):
    """It properly passes the keepttl argument to Redis."""
    key = "midlevel_set_keepttl_test"

    # When keepttl is set, changing the value won't reset the ttl.
    # We can check this by setting a value with a ttl, then changing the value
    # with keepttl=True, then checking to make sure the ttl is still the same.

    await client.set(key, "something random", ex=100)
    await client.set(key, "something else", keepttl=True)
    result = await client.call("TTL", key)
    assert result > 1
