"""The client module handles the Redis Client interface.

Classes:
    RedisClient
"""
from collections import defaultdict
import typing as t

from respy3 import protocol

from . import connections


PUSH_COMMANDS = {b"SUBSCRIBE", b"PSUBSCRIBE", b"UNSUBSCRIBE", b"PUNSUBSCRIBE"}


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
        self.push_callbacks: defaultdict = defaultdict(list)

    async def receive(self, connection, push_only: bool = False):
        """Read the connection and return an object, calling any push callbacks.

        It is not recommended to call this directly. Use the :meth:`call` method,
        instead.

        Args:
            connection (trio.abc.Stream): The connection to read from.
            push_only (bool): If a push is received, return None
                and don't try to read anything else (default: False).

        Returns:
            The response from Redis, as parsed by the Reader class (or None, if
                push_only is True and a push is received).
        """
        while True:
            output = self.reader.get_object()
            if output is self.reader.sentinel:
                pass
            elif isinstance(output, protocol.RespPush):
                callbacks = self.push_callbacks[output.push_type]
                for callback in callbacks:
                    callback(output)
                if push_only:
                    return None
                continue  # pragma: nocover
            else:
                return output

            data = await connection.receive_some()
            self.reader.feed(data)

    async def send_command(self, command: bytes, *args: bytes, connection=None):
        """Send the given command to Redis and return the connection used.

        It is not recommended to call this directly. Use the :meth:`call` method,
        instead.

        Args:
            command (bytes): The command to send, such as b"PING" or b"SET".
            *args (bytes): The args to send with the command.
            connection (trio.abc.Stream): the connection to use, or None
                to get a connection from the pool.

        Returns:
            The connection used to send the command.

        """
        buffer = self.write_command(command, *args)
        if connection is None:
            connection = await self.connection_pool.wait_for_connection()
        await connection.send_all(buffer)
        return connection

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
        connection = await self.send_command(command, *args)
        response = await self.receive(
            connection, push_only=command.upper() in PUSH_COMMANDS
        )
        self.connection_pool.put_connection(connection)
        return response

    def register_push_callback(self, push_type: bytes, callback: t.Callable) -> None:
        """Register a function to be called when a push is received."""
        self.push_callbacks[push_type].append(callback)
