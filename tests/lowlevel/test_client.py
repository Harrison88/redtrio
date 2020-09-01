"""Tests for the lowlevel client."""

import pytest

from redtrio.lowlevel import connections
from redtrio.lowlevel import RedisClient


@pytest.fixture
def client():
    """A fresh client instance for every test."""
    client = RedisClient()
    return client


@pytest.fixture
def client2():
    """A second client instance to publish messages to channels."""
    client2 = RedisClient()
    return client2


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


async def test_push_callback(autojump_clock, client, client2):
    """It calls the correct callback when a push is received."""
    channel = b"test_channel"
    message = b"Hello, world!"
    subscribe_called = False
    message_called = False

    def assert_subscribe(resp_push):
        assert resp_push.push_type == b"subscribe"
        assert channel in resp_push.data

        nonlocal subscribe_called
        subscribe_called = True

    def assert_message(resp_push):
        assert resp_push.push_type == b"message"
        assert channel in resp_push.data
        assert message in resp_push.data

        nonlocal message_called
        message_called = True

    client.register_push_callback(b"subscribe", assert_subscribe)
    client.register_push_callback(b"message", assert_message)

    connection = await client.send_command(b"HELLO", b"3")
    await client.receive(connection)
    connection2 = await client2.send_command(b"HELLO", b"3")
    await client2.receive(connection2)

    await client.send_command(b"SUBSCRIBE", channel, connection=connection)
    result = await client.receive(connection, push_only=True)
    assert result is None
    await client2.send_command(b"PUBLISH", channel, message, connection=connection2)
    result = await client2.receive(connection2)
    assert result == 1
    result = await client.receive(connection, push_only=True)
    assert result is None

    client.connection_pool.put_connection(connection)
    client2.connection_pool.put_connection(connection2)

    assert subscribe_called
    assert message_called


async def test_push_received_with_command(autojump_clock, client, client2):
    """It calls the push callback even when it is received inbetween commands."""
    channel = b"test_channel2"
    message = b"42 is the answer"
    message_called = False

    def assert_message(resp_push):
        assert resp_push.push_type == b"message"
        assert channel in resp_push.data
        assert message in resp_push.data

        nonlocal message_called
        message_called = True

    client.register_push_callback(b"message", assert_message)

    connection = await client.send_command(b"HELLO", b"3")

    await client.send_command(b"SUBSCRIBE", channel, connection=connection)
    await client.send_command(b"PING", connection=connection)

    await client2.call(b"PUBLISH", channel, message)

    await client.send_command(b"PING", connection=connection)
    await client.send_command(b"PING", connection=connection)

    for _ in range(3):
        result = await client.receive(connection)
        assert result == b"PONG" or isinstance(result, dict)

    assert message_called
