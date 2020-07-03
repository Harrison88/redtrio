"""Tests for the connection pool."""

import pytest
import trio

from redtrio.lowlevel import connections


@pytest.fixture
async def pool():
    """A ConnectionPool instance."""
    pool = connections.ConnectionPool("127.0.0.1", 6379)
    return pool


async def test_connection_creation(pool):
    """It creates a connection and puts it in used_connections."""
    assert len(pool.pool) == 0
    connection = await pool.wait_for_connection()
    assert connection in pool.used_connections
    pool.put_connection(connection)
    assert len(pool.pool) == 1


async def test_get_connection_from_pool(pool):
    """It reuses connections already in the pool."""
    connection = await pool.wait_for_connection()
    pool.put_connection(connection)
    connection_from_pool = await pool.wait_for_connection()
    assert connection is connection_from_pool


async def test_remove_connection(pool):
    """It removes connections from used_connections."""
    connection = await pool.wait_for_connection()
    assert len(pool.used_connections) == 1
    pool.remove_connection(connection)
    assert len(pool.pool) == 0 and len(pool.used_connections) == 0


async def test_remove_unused_connection(pool):
    """It removes connections from the pool."""
    connection = await pool.wait_for_connection()
    pool.put_connection(connection)
    pool.remove_connection(connection)
    assert len(pool.pool) == 0 and len(pool.used_connections) == 0


async def test_pool_limit(autojump_clock, pool):
    """It blocks when the max_connections is reached and nothing is in the pool."""
    for _ in range(pool.max_connections):
        await pool.wait_for_connection()
    assert len(pool.used_connections) == pool.max_connections

    with trio.move_on_after(2) as cancel_scope:
        await pool.wait_for_connection()

    assert cancel_scope.cancelled_caught
