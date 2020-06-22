import typing as t

from . import connections
from . import protocol


class RedisClient:
    """Documentation for RedisClient is here
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 6379,
        *,
        connection_pool=None,
        Reader: type = protocol.Resp3Reader,
        write_command: t.Callable = protocol.write_command,
    ):
        self.host = host
        self.port = port

        if connection_pool is None:
            self.connection_pool = connections.ConnectionPool(host, port)
        else:
            self.connection_pool = connection_pool

        self.reader = Reader()
        self.write_command = write_command

    async def call(self, command: bytes, *args: bytes):
        """Documentation for *call*
        """
        buffer = self.write_command(command, *args)
        connection = await self.connection_pool.wait_for_connection()
        await connection.send_all(buffer)
        async for data in connection:
            self.reader.feed(data)
            if output := self.reader.get_object():
                self.connection_pool.put_connection(connection)
                return output
