import trio


class RedisConnection:
    def __init__(self, host, port, *, pool=None):
        self.socket = None
        self.host = host
        self.port = port
        self.pool = pool

    async def connect(self):
        if self.socket:
            return True

        self.socket = await trio.open_tcp_stream(self.host, self.port)
        return True

    async def send(self, data):
        await self.socket.send_all(data)
        return True

    async def receive(self):
        pass

    def close(self):
        if self.pool:
            self.pool.remove_connection(self)
        self.socket = None


class ConnectionPool:
    def __init__(
        self, host, port, max_connections=50, spawn_connection=trio.open_tcp_stream
    ):
        self.host = host
        self.port = port
        self.max_connections = max_connections
        self.spawn_connection = spawn_connection
        self.used_connections = set()
        self.pool = []

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

    def put_connection(self, connection):
        self.used_connections.remove(connection)
        self.pool.append(connection)

    def remove_connection(self, connection):
        self.used_connections.discard(connection)
        if connection in self.pool:
            self.pool.remove(connection)
