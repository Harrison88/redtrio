"""Tests for the lowlevel client."""

import pytest

from redtrio.lowlevel import connections
from redtrio.lowlevel import RedisClient


@pytest.fixture
def client():
    """A fresh client instance for every test."""
    client = RedisClient()
    return client


async def test_call_hello(client):
    """It returns the expected mapping for the HELLO 3 command."""
    result = await client.call(b"HELLO", b"3")
    assert result[b"proto"] == 3
    assert len(result) == 7


def test_use_connection_pool():
    """It uses the connection pool that was passed in."""
    pool = connections.ConnectionPool(host="127.0.0.1", port=6379)
    client = RedisClient(connection_pool=pool)
    assert client.connection_pool is pool


async def test_parse_streamed_data(autojump_clock, nursery, client, trickle_connection):
    """It returns the correct response to the PING command, over a slow connection."""
    client.connection_pool.pool.append(trickle_connection)
    result = await client.call(b"PING")
    assert result == b"PONG"
