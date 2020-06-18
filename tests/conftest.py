import pytest
import trio
from pytest_trio.enable_trio_mode import *


async def fake_server(stream, *, task_status=trio.TASK_STATUS_IGNORED):
    task_status.started()
    while True:
        data = await stream.receive_some()
        if data == b"*1\r\n$4\r\nPING\r\n":
            await stream.send_all(b"+PONG\r\n")


@pytest.fixture
async def trickle_connection(nursery):
    server_socket, client_socket = trio.testing.memory_stream_pair()
    await nursery.start(fake_server, server_socket)

    async def trickle():
        while trio.testing.memory_stream_pump(
            server_socket.send_stream, client_socket.receive_stream, max_bytes=1
        ):
            await trio.sleep(1)

    server_socket.send_stream.send_all_hook = trickle

    return client_socket
