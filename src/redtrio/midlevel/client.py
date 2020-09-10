import typing as t

from redtrio.lowlevel import RedisClient


class MidlevelClient:
    def __init__(self, **client_args):
        self.client = RedisClient(**client_args)
        self.said_hello = False

    async def call(self, command: str, *args: str):
        if not self.said_hello:
            self.said_hello = True
            await self.hello(3)
        encoded_args = [s.encode() for s in args]
        return await self.client.call(command.encode(), *encoded_args)

    async def hello(self, protocol: int):
        return await self.call("HELLO", str(protocol))

    ### Hash commands: https://redis.io/commands#hash ###
    async def hdel(self, key: str, *fields: str) -> int:
        return await self.call("HDEL", key, *fields)

    async def hexists(self, key: str, field: str) -> int:
        return await self.call("HEXISTS", key, field)

    async def hget(self, key: str, field: str) -> bytes:
        return await self.call("HGET", key, field)

    async def hgetall(self, key: str) -> dict:
        return await self.call("HGETALL", key)

    async def hincrby(self, key: str, field: str, increment: int) -> int:
        return await self.call("HINCRBY", key, field, str(increment))

    async def hincrbyfloat(self, key: str, field: str, increment: float) -> float:
        return float(await self.call("HINCRBYFLOAT", key, field, str(increment)))

    async def hkeys(self, key: str) -> list:
        return await self.call("HKEYS", key)

    async def hlen(self, key: str) -> int:
        return await self.call("HLEN", key)

    async def hmget(self, key: str, *fields: str) -> list:
        return await self.call("HMGET", key, *fields)

    async def hset(self, key: str, *args: str) -> str:
        return await self.call("HSET", key, *args)

    async def hsetnx(self, key: str, field: str, value: str) -> int:
        return await self.call("HSETNX", key, field, value)

    async def hstrlen(self, key: str, field: str) -> int:
        return await self.call("HSTRLEN", key, field)

    async def hvals(self, key: str) -> list:
        return await self.call("HVALS", key)
