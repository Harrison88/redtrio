from functools import partial

import pytest
import trio

from redtrio.lowlevel import RedisClient
from redtrio.lowlevel import connections


@pytest.fixture
def client():
    client = RedisClient()
    return client


async def test_call_hello(client):
    result = await client.call(b"HELLO", b"3")
    assert result[b"proto"] == 3
    assert len(result) == 7


def test_use_connection_pool():
    pool = connections.ConnectionPool(host="127.0.0.1", port=6379)
    client = RedisClient(connection_pool=pool)
    assert client.connection_pool is pool


async def test_parse_streamed_data(autojump_clock, nursery, client, trickle_connection):
    client.connection_pool.pool.append(trickle_connection)
    result = await client.call(b"PING")
    assert result == b"PONG"
