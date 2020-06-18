import typing as t

import trio


class ConnectionPool:
    def __init__(
        self,
        host: str,
        port: int,
        max_connections: int = 50,
        spawn_connection: t.Callable = trio.open_tcp_stream,
    ):
        self.host = host
        self.port = port
        self.max_connections = max_connections
        self.spawn_connection = spawn_connection
        self.used_connections: t.Set[trio.abc.Stream] = set()
        self.pool: t.List[trio.abc.Stream] = []

    async def wait_for_connection(self):
        connection = None
        while not connection:
            if self.pool:
                connection = self.pool.pop()
                break
            if len(self.used_connections) + len(self.pool) < self.max_connections:
                connection = await self.spawn_connection(self.host, self.port)
                break

            await trio.sleep(1)

        self.used_connections.add(connection)
        return connection

    def put_connection(self, connection: trio.abc.Stream):
        self.used_connections.remove(connection)
        self.pool.append(connection)

    def remove_connection(self, connection: trio.abc.Stream):
        self.used_connections.discard(connection)
        if connection in self.pool:
            self.pool.remove(connection)
