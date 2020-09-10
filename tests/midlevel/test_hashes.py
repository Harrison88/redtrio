import pytest

from redtrio.midlevel import MidlevelClient


@pytest.fixture
async def client():
    client = MidlevelClient()
    await client.call("FLUSHALL")
    return client


async def test_hdel(client):
    key = "midlevel_hdel_test"

    # When the field doesn't exist, HDEL returns 0.
    expected = 0
    actual = await client.hdel(key, "nonexistent")
    assert actual == expected

    # Set one value then delete the field, resulting in 1 deletion.
    await client.hset(key, "test", "value")
    expected = 1
    actual = await client.hdel(key, "test")
    assert actual == expected

    # Set two values then delete both fields, resulting in 2 deletions.
    await client.hset(key, "test", "value", "test2", "value2")
    expected = 2
    actual = await client.hdel(key, "test", "test2")
    assert actual == expected


async def test_hexists(client):
    key = "midlevel_hexists_test"

    # When the key doesn't exist, 0 is returned.
    expected = 0
    actual = await client.hexists(key, "nonexistent")
    assert actual == expected

    # When the key does exist, 1 is returned.
    await client.hset(key, "test", "value")
    expected = 1
    actual = await client.hexists(key, "test")
    assert actual == expected


async def test_hget(client):
    key = "midlevel_hget_test"
    field = "test"

    # When the key doesn't exist, None is returned.
    expected = None
    actual = await client.hget(key, field)
    assert actual == expected

    # When the key and the field both exist, return the value.
    # The value will be returned as bytes.
    value = "42"
    await client.hset(key, field, value)
    expected = value.encode()
    actual = await client.hget(key, field)
    assert actual == expected


async def test_hgetall(client):
    key = "midlevel_hgetall_test"
    field = "hello, world!"
    value = "Yes, it is I."

    # When the key does not exist, an empty dict is returned.
    expected = {}
    actual = await client.hgetall(key)
    assert actual == expected

    # When the key does exist, a dict with the field:value mapping is returned.
    # The strings will be bytes now.
    await client.hset(key, field, value)
    expected = {field.encode(): value.encode()}
    actual = await client.hgetall(key)
    assert actual == expected


async def test_hincrby(client):
    key = "midlevel_hincrby_test"
    field = "test_increment"
    increment = 42

    # When the key doesn't exist, it is initialized as a hash.
    # The field is initialized to 0, then incremented.
    expected = increment
    actual = await client.hincrby(key, field, increment)
    assert actual == expected

    # When the key and field both exist, the value is incremented.
    expected = increment * 2
    actual = await client.hincrby(key, field, increment)
    assert actual == expected


async def test_hincrbyfloat(client):
    key = "midlevel_hincrbyfloat_test"
    field = "test_increment"
    increment = 3.14

    expected = increment
    actual = await client.hincrbyfloat(key, field, increment)
    assert actual == expected

    expected = increment * 2
    actual = await client.hincrbyfloat(key, field, increment)
    assert actual == expected


async def test_hkeys(client):
    key = "midlevel_hkeys_test"
    field = "test_hkeys"

    # When the key does not exist, an empty list is returned.
    expected = []
    actual = await client.hkeys(key)
    assert actual == expected

    # When the key does exist, a list of bytes is returned.
    await client.hset(key, field, "value")
    expected = [field.encode()]
    actual = await client.hkeys(key)
    assert actual == expected


async def test_hlen(client):
    key = "midlevel_hlen_test"

    # When the key does not exist, 0 is returned.
    expected = 0
    actual = await client.hlen(key)
    assert actual == expected

    # When the key does exist, the number of fields it contains is returned.
    await client.hset(key, "field", "value")
    expected = 1
    actual = await client.hlen(key)
    assert actual == expected


async def test_hmget(client):
    key = "midlevel_hmget_test"
    field = "hello"
    value = "yes"
    field2 = "also a field"

    # When the key does not exist, [None] is returned.
    expected = [None]
    actual = await client.hmget(key, "nope")
    assert actual == expected

    # When the key and field both exist, a [value] list is returned.
    await client.hset(key, field, value, field2, value)
    expected = [value.encode(), value.encode()]
    actual = await client.hmget(key, field, field2)
    assert actual == expected

    # When only some fields exist, a [value, None] list is returned.
    expected = [value.encode(), None]
    actual = await client.hmget(key, field, "nope")
    assert actual == expected


async def test_hset(client):
    key = "midlevel_hset_test"
    field = "something"
    value = "valuable"
    field2 = "something else"
    value2 = "also valuable"

    # When one value is set, a 1 int is returned.
    expected = 1
    actual = await client.hset(key, field, value)
    assert actual == expected

    # When one value is modified, a 0 int is returned
    expected = 0
    actual = await client.hset(key, field, value2)
    assert actual == expected
    assert await client.hget(key, field) == value2.encode()

    # When one value is modified and one new field is set, a 1 int is returned.
    expected = 1
    actual = await client.hset(key, field, value, field2, value2)
    assert actual == expected


async def test_hsetnx(client):
    key = "midlevel_hsetnx_test"
    field = "something"

    # When the field does not already exist, a 1 int is returned.
    expected = 1
    actual = await client.hsetnx(key, field, "a thing")
    assert actual == expected

    # When the field does already exist, a 0 int is returned.
    expected = 0
    actual = await client.hsetnx(key, field, "another thing")
    assert actual == expected


async def test_hstrlen(client):
    key = "midlevel_hstrlen_test"
    field = "field"
    value = "This is 22 chars long."

    # When the key or field do not exist, a 0 int is returned.
    expected = 0
    actual = await client.hstrlen(key, field)
    assert actual == expected

    # When the key and field exist, an int of the length of the value is returned.
    await client.hset(key, field, value)
    expected = len(value)
    actual = await client.hstrlen(key, field)
    assert actual == expected


async def test_hvals(client):
    key = "midlevel_hvals_test"
    field = "field"
    value = "value"

    # When the key does not exist, an empty list is returned.
    expected = []
    actual = await client.hvals(key)
    assert actual == expected

    # When the key does exist, a list of bytes is returned.
    await client.hset(key, field, value)
    expected = [value.encode()]
    actual = await client.hvals(key)
    assert actual == expected
