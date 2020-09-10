"""The connections module handles connecting to the server.

Classes:
    ConnectionPool
"""

import typing as t

import trio


class ConnectionPool:
    """This class implements a default connection pool.

    Attributes:
        host (str): The address to connect to.
        port (int): The port to connect to.
        max_connections (int): The maximum number of connections to keep.
        spawn_connection: The function used to spawn a new connection.
        used_connections (set): A set containing connections currently in use.
        pool: The pool of unused connections.
    """

    def __init__(
        self,
        host: str,
        port: int,
        max_connections: int = 50,
        spawn_connection: t.Callable = trio.open_tcp_stream,
    ):
        """Initialize the ConnectionPool.

        Arguments:
            host (str): The address to connect to.
            port (int): The port to connect to.
            max_connections (int): The maximum number of connections (default: 50).
            spawn_connection: Spawn a connection (default: trio.open_tcp_stream).
        """
        self.host = host
        self.port = port
        self.max_connections = max_connections
        self.spawn_connection = spawn_connection
        self.used_connections: t.Set[trio.abc.Stream] = set()
        self.pool: t.List[trio.abc.Stream] = []

    async def wait_for_connection(self):
        """Wait for a connection to become available.

        Returns immediately if *pool* has a connection available.
        Otherwise, if *max_connections* has not been reached, spawns a new connection.
        If *max_connections* has been reached, wait for one to become available.

        Returns:
            A connection to the Redis server.
        """
        connection = None
        while not connection:  # pragma: nobranch
            if self.pool:
                connection = self.pool.pop()
                break
            elif len(self.used_connections) + len(self.pool) < self.max_connections:
                connection = await self.spawn_connection(self.host, self.port)
                break

            await trio.sleep(5)

        self.used_connections.add(connection)
        return connection

    def put_connection(self, connection: trio.abc.Stream):
        """Put a connection back in the pool, removing it from used_connections.

        Arguments:
            connection: The connection to put back.
        """
        self.used_connections.remove(connection)
        self.pool.append(connection)

    def remove_connection(self, connection: trio.abc.Stream):
        """Remove a connection entirely, whether it is in used_connections or the pool.

        Arguments:
            connection: The connection to remove.
        """
        self.used_connections.discard(connection)
        if connection in self.pool:
            self.pool.remove(connection)
