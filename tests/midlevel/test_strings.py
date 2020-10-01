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
    actual = await client.set(key, value, px=50)
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


async def test_append(client):
    """It returns the proper responses for APPEND."""
    key = "midlevel_append_test"
    value = "something random"

    # When the key doesn't exist, it creates the key and returns the length.
    expected = len(value)
    actual = await client.append(key, value)
    assert actual == expected

    # When the key does exist, it appends the value and returns the new length.
    expected = len(value) * 2
    actual = await client.append(key, value)
    assert actual == expected

    expected = value.encode() * 2
    actual = await client.get(key)
    assert actual == expected


async def test_bitcount(client):
    """It returns the proper responses for BITCOUNT."""
    key = "midlevel_bitcount_test"
    value = "value"

    # When the key does not exist, 0 is returned.
    expected = 0
    actual = await client.bitcount(key)
    assert actual == expected

    # When the key does exist, an int is returned.
    await client.set(key, value)
    expected = 21
    actual = await client.bitcount(key)
    assert actual == expected

    expected = 8
    actual = await client.bitcount(key, 0, 1)
    assert actual == expected


async def test_bitop(client):
    """It returns the proper responses for BITOP."""
    destination_key = "midlevel_bitop_test"
    source_key = "midlevel_bitop_source"
    source_key2 = "midlevel_bitop_source2"
    value = "foobar"
    value2 = "abcdef"

    await client.set(source_key, value)
    await client.set(source_key2, value2)

    # BITOP AND performs the AND operation between the source keys, stores the
    # result in the destination_key, and returns the integer length of the result.
    expected = 6
    actual = await client.bitop("AND", destination_key, source_key, source_key2)
    assert actual == expected
    expected = b"`bc`ab"
    actual = await client.get(destination_key)
    assert actual == expected

    # BITOP OR performs the OR operation between the source keys, stores the
    # result in the destination_key, and returns the integer length of the result.
    expected = 6
    actual = await client.bitop("OR", destination_key, source_key, source_key2)
    assert actual == expected
    expected = b"goofev"
    actual = await client.get(destination_key)
    assert actual == expected

    # BITOP XOR performs the XOR operation between the source keys, stores the
    # result in the destination_key, and returns the integer length of the result.
    expected = 6
    actual = await client.bitop("XOR", destination_key, source_key, source_key2)
    assert actual == expected
    expected = b"\a\r\x0c\x06\x04\x14"
    actual = await client.get(destination_key)
    assert actual == expected

    # BITOP NOT performs the NOT operation on the source key, stores the result
    # in the destination_key, and returns the integer length of the result.
    # Note that BITOP NOT is an unary operation, accepting only one source key,
    # as opposed to the other operations which can take any number of source keys.
    expected = 6
    actual = await client.bitop("NOT", destination_key, source_key)
    assert actual == expected
    expected = b"\x99\x90\x90\x9d\x9e\x8d"
    actual = await client.get(destination_key)
    assert actual == expected


async def test_bitpos(client):
    """It returns the proper responses for BITPOS."""
    key = "midlevel_bitpos_test"

    # Note that "\x00\xff", when encoded to UTF-8, becomes b"\x00\xc3\xbf".
    await client.set(key, "\x00\xff")

    # The first bit is 0, so BITPOS returns 0 in this case.
    expected = 0
    actual = await client.bitpos(key, 0)
    assert actual == expected

    # The first set bit is the first bit of the second bytes, so BITPOS returns
    # 8 in this case.
    expected = 8
    actual = await client.bitpos(key, 1)
    assert actual == expected

    # Start is specified
    expected = 17
    actual = await client.bitpos(key, 0, start=2)
    assert actual == expected

    # Start is specified after the last 1, so BITPOS returns -1.
    expected = -1
    actual = await client.bitpos(key, 1, start=3)
    assert actual == expected

    # Start and end are specified, containing no 0's, so BITPOS returns -1.
    expected = -1
    actual = await client.bitpos(key, 0, start=3, end=4)
    assert actual == expected


async def test_decr(client):
    """It returns the proper responses for DECR."""
    key = "midlevel_decr_test"

    # When the key doesn't exist, it is initialized to 0, then decremented.
    expected = -1
    actual = await client.decr(key)
    assert actual == expected

    # When the key does exist, the value is decremented and returned as an int.
    expected = -2
    actual = await client.decr(key)
    assert actual == expected


async def test_decrby(client):
    """It returns the proper responses for DECRBY."""
    key = "midlevel_decrby_test"

    # When the key doesn't exist, it is initialized to 0, then decremented.
    expected = -7
    actual = await client.decrby(key, 7)
    assert actual == expected

    # When the key does exist, the value is decremented and returned as an int.
    expected = -12
    actual = await client.decrby(key, 5)
    assert actual == expected


async def test_getbit(client):
    """It returns the proper responses for GETBIT."""
    key = "midlevel_getbit_test"

    # When the key doesn't exist, all zeroes are assumed.
    expected = 0
    actual = await client.getbit(key, 5)
    assert actual == expected

    # When the key does exist, the requested bit is returned.
    await client.set(key, "v")
    expected = 1
    actual = await client.getbit(key, 1)
    assert actual == expected


async def test_getrange(client):
    """It returns the proper responses for GETRANGE."""
    key = "midlevel_getrange_test"
    value = "Hello!"

    # When the key doesn't exist, empty bytes are returned.
    expected = b""
    actual = await client.getrange(key, 0, 5)
    assert actual == expected

    # When the key does exist, the range (inclusive) is returned.
    await client.set(key, value)
    expected = value.encode()
    actual = await client.getrange(key, 0, -1)
    assert actual == expected


async def test_getset(client):
    """It returns the proper responses for GETSET."""
    key = "midlevel_getset_test"
    value = "Hello"
    value2 = "World!"

    # When the key does not exist, None is returned.
    expected = None
    actual = await client.getset(key, value)
    assert actual == expected

    # When the key does exist, bytes are returned.
    expected = value.encode()
    actual = await client.getset(key, value2)
    assert actual == expected


async def test_incr(client):
    """It returns the proper responses for INCR."""
    key = "midlevel_incr_test"

    # When the key does not exist, it is initialized to zero then incremented.
    expected = 1
    actual = await client.incr(key)
    assert actual == expected

    # When the key does exist, it is incremented and the new value is returned.
    expected = 2
    actual = await client.incr(key)
    assert actual == expected


async def test_incrby(client):
    """It returns the proper responses for INCRBY."""
    key = "midlevel_incrby_test"
    value = 42

    # When the key does not exist, it is initialized to zero then incremented.
    expected = value
    actual = await client.incrby(key, value)
    assert actual == expected

    # When the key does exist, it is incremented and the new value is returned.
    expected = value * 2
    actual = await client.incrby(key, value)
    assert actual == expected


async def test_incrbyfloat(client):
    """It returns the proper responses for INCRBYFLOAT."""
    key = "midlevel_incrbyfloat_test"
    value = 1.2

    # When the key does not exist, it is initialized to zero then incremented.
    expected = value
    actual = await client.incrbyfloat(key, value)
    assert actual == expected

    # When the key does exist, it is incremented and the new value is returned.
    expected = value * 2
    actual = await client.incrbyfloat(key, value)
    assert actual == expected
