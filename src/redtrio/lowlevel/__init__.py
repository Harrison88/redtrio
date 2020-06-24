"""The lowlevel package contains the bare minimum required for a Redis client.

Example:
    from redtrio.lowlevel import RedisClient
    client = RedisClient()
    result = await client.call(b"PING")
    print(result)
    b'PONG'

Modules:
    protocol - An implementation of Redis' RESP3 protocol
    connections - The default connection pool
    client - The Redis client, exported at the package level

Exports:
    RedisClient
"""

from .client import RedisClient
