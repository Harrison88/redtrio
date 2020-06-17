import pytest
import trio

from redtrio.lowlevel import RedisClient


@pytest.fixture
def client():
    client = RedisClient()
    return client


async def test_call_hello(client):
    result = await client.call(b"HELLO", b"3")
    assert result[b"proto"] == 3
    assert len(result) == 7
