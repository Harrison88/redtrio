"""The client module handles the Redis Client interface.

Classes:
    RedisClient
"""
import typing as t

from . import connections
from . import protocol


class RedisClient:
    """RedisClient communicates with the Redis server via its *call* method.

    Attributes:
        host (str): The address to connect to (default: "127.0.0.1").
        port (int): The port to connect to (default: 6379).
        connection_pool (instance of a connection pool): The pool to use for
            connections. Leave as None to use the default ConnectionPool.
        Reader (protocol class): The class to use for interpreting responses from Redis.
        write_command (function): The function to use to format commands to send
            to Redis.
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
        """Initialize the RedisClient.

        Arguments:
            host (str): The address to connect to (default: "127.0.0.1").
            port (int): The port to connect to (default: 6379).
            connection_pool: A connection pool to use. Overrides host and port.
                Leave as None to use the default ConnectionPool.
            Reader: the class to use for parsing replies from the server.
            write_command: the function used to prepare commands sent to the server.
        """
        self.host = host
        self.port = port

        if connection_pool is None:
            self.connection_pool = connections.ConnectionPool(host, port)
        else:
            self.connection_pool = connection_pool

        self.reader = Reader()
        self.write_command = write_command

    async def call(self, command: bytes, *args: bytes):
        """Send the given command to Redis and return the response.

        Args:
            command (bytes): The command to send, such as b"PING" or b"SET".
            *args (bytes): The args to send with the command.

        Returns:
            The response from Redis, as parsed by the Reader class.

        Example:
            call(b"SET", b"key_name", b"value") -> b"OK"
        """
        buffer = self.write_command(command, *args)
        connection = await self.connection_pool.wait_for_connection()
        await connection.send_all(buffer)
        async for data in connection:
            self.reader.feed(data)
            output = self.reader.get_object()
            if output is not self.reader.sentinel:
                self.connection_pool.put_connection(connection)
                return output
