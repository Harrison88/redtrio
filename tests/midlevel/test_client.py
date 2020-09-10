import pytest

from redtrio.midlevel import MidlevelClient


def test_arguments_passed_through():
    """It passes arguments to the lowlevel client."""

    class TestReader:
        pass

    host = "Nothing"
    port = -1
    connection_pool = True
    write_command = lambda x: x

    client = MidlevelClient(
        host=host,
        port=port,
        connection_pool=connection_pool,
        Reader=TestReader,
        write_command=write_command,
    )

    assert client.client.host == host
    assert client.client.port == port
    assert client.client.connection_pool == connection_pool
    assert isinstance(client.client.reader, TestReader)
    assert client.client.write_command is write_command
