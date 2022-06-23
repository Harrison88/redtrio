"""This module contains the MidlevelClient implementation.

All commands are divided by comments into sections based on https://redis.io/commands
"""
import typing as t

from redtrio.lowlevel import RedisClient


class MidlevelClient:
    """MidlevelClient is an abstraction on top of the lowlevel client.

    Args:
        **client_args: any arg accepted by :class:`lowlevel.RedisClient`.
    """

    def __init__(self, **client_args):
        """Initialize MidlevelClient."""
        self.client = RedisClient(**client_args)
        self.said_hello = False

    async def call(self, command: str, *args: str):
        """Send a command to Redis and return the response.

        Strings passed to this function will be converted to bytes.

        Args:
            command (str): The command to be sent, like "HELLO".
            *args (str): Arguments to be sent with the command.

        Returns:
            The response from Redis.
        """
        if not self.said_hello:
            self.said_hello = True
            await self.hello(3)
        encoded_args = [s.encode() for s in args]
        return await self.client.call(command.encode(), *encoded_args)

    async def hello(self, protocol: int) -> dict:
        """Say hello to Redis and let it know what protocol we're using.

        It's good to be friendly.

        Args:
            protocol (int): The protocol number. Currently 3 is the only option.

        Returns:
            A dict containing the response from Redis.
        """
        return await self.call("HELLO", str(protocol))

    ### Hash commands: https://redis.io/commands#hash ###
    async def hdel(self, key: str, *fields: str) -> int:
        """Implement the HDEL command (https://redis.io/commands/hdel)."""
        return await self.call("HDEL", key, *fields)

    async def hexists(self, key: str, field: str) -> int:
        """Implement the HEXISTS command (https://redis.io/commands/hexists)."""
        return await self.call("HEXISTS", key, field)

    async def hget(self, key: str, field: str) -> bytes:
        """Implement the HGET command (https://redis.io/commands/hget)."""
        return await self.call("HGET", key, field)

    async def hgetall(self, key: str) -> dict:
        """Implement the HGETALL command (https://redis.io/commands/hgetall)."""
        return await self.call("HGETALL", key)

    async def hincrby(self, key: str, field: str, increment: int) -> int:
        """Implement the HINCRBY command (https://redis.io/commands/hincrby)."""
        return await self.call("HINCRBY", key, field, str(increment))

    async def hincrbyfloat(self, key: str, field: str, increment: float) -> float:
        """Implement HINCRBYFLOAT command (https://redis.io/commands/hincrbyfloat).

        This command modifies the return response from `bytes` to `float`.

        Args:
            key (str): the key to increment.
            field (str): the field of the key to increment.
            increment (float): the amount to increment the field.

        Returns:
            The new value of the field (float).
        """
        return float(await self.call("HINCRBYFLOAT", key, field, str(increment)))

    async def hkeys(self, key: str) -> list:
        """Implement the HKEYS command (https://redis.io/commands/hkeys)."""
        return await self.call("HKEYS", key)

    async def hlen(self, key: str) -> int:
        """Implement the HLEN command (https://redis.io/commands/hlen)."""
        return await self.call("HLEN", key)

    async def hmget(self, key: str, *fields: str) -> list:
        """Implement the HMGET command (https://redis.io/commands/hmget)."""
        return await self.call("HMGET", key, *fields)

    async def hset(self, key: str, *args: str) -> str:
        """Implement the HSET command (https://redis.io/commands/hset)."""
        return await self.call("HSET", key, *args)

    async def hsetnx(self, key: str, field: str, value: str) -> int:
        """Implement the HSETNX command (https://redis.io/commands/hsetnx)."""
        return await self.call("HSETNX", key, field, value)

    async def hstrlen(self, key: str, field: str) -> int:
        """Implement the HSTRLEN command (https://redis.io/commands/hstrlen)."""
        return await self.call("HSTRLEN", key, field)

    async def hvals(self, key: str) -> list:
        """Implement the HVALS command (https://redis.io/commands/hvals)."""
        return await self.call("HVALS", key)

    ### Sets commands: https://redis.io/commands#set ###
    async def sadd(self, key: str, *values: str) -> int:
        """Implement the SADD command (https://redis.io/commands/sadd)."""
        return await self.call("SADD", key, *values)

    async def scard(self, key: str) -> int:
        """Implement the SCARD command (https://redis.io/commands/scard)."""
        return await self.call("SCARD", key)

    async def sdiff(self, key: str, *keys: str) -> set:
        """Implement the SDIFF command (https://redis.io/commands/sdiff)."""
        return await self.call("SDIFF", key, *keys)

    async def sdiffstore(self, destination: str, key: str, *keys: str) -> int:
        """Implement the SDIFFSTORE command (https://redis.io/commands/sdiffstore)."""
        return await self.call("SDIFFSTORE", destination, key, *keys)

    async def sinter(self, key: str, *keys: str) -> set:
        """Implement the SINTER command (https://redis.io/commands/sinter)."""
        return await self.call("SINTER", key, *keys)

    async def sinterstore(self, destination: str, key: str, *keys: str):
        """Implement the SINTERSTORE command (https://redis.io/commands/sinterstore)."""
        return await self.call("SINTERSTORE", destination, key, *keys)

    async def sismember(self, key: str, member: str) -> bool:
        """Implement the SISMEMBER command (https://redis.io/commands/sismember)."""
        return await self.call("SISMEMBER", key, member)

    async def smembers(self, key: str) -> set:
        """Implement the SMEMBERS command (https://redis.io/commands/smember)."""
        return await self.call("SMEMBERS", key)

    async def smismember(self, key: str, member: str, *members: str) -> list:
        """Implement the SMISMEMBER command (https://redis.io/commands/smismember)."""
        return await self.call("SMISMEMBER", key, member, *members)

    async def smove(self, source: str, destination: str, member: str) -> int:
        """Implement the SMOVE command (https://redis.io/commands/smove)."""
        return await self.call("SMOVE", source, destination, member)

    async def spop(
        self, key: str, count: t.Optional[int] = None
    ) -> t.Union[bytes, set]:
        """Implement the SPOP command (https://redis.io/commands/spop)."""
        command = ["SPOP", key]
        if count is not None:
            command.append(str(count))
        return await self.call(*command)

    ### String commands: https://redis.io/commands/#string ###
    async def append(self, key: str, value: str) -> bytes:
        """Implement the APPEND command (https://redis.io/commands/append)."""
        return await self.call("APPEND", key, value)

    async def bitcount(
        self, key: str, start: t.Optional[int] = None, end: t.Optional[int] = None
    ):
        """Implement the BITCOUNT command (https://redis.io/commands/bitcount)."""
        command = ["BITCOUNT", key]
        if start is not None and end is not None:
            command.extend([str(start), str(end)])

        return await self.call(*command)

    async def bitop(
        self,
        command: t.Literal["AND", "OR", "XOR", "NOT"],
        destination_key: str,
        *source_keys: str,
    ) -> int:
        """Implement the BITOP command (https://redis.io/commands/bitop)."""
        return await self.call("BITOP", command, destination_key, *source_keys)

    async def bitpos(
        self,
        key: str,
        bit: t.Literal[0, 1],
        start: t.Optional[int] = None,
        end: t.Optional[int] = None,
    ):
        """Implement the BITPOS command (https://redis.io/commands/bitpos)."""
        command = ["BITPOS", key, str(bit)]
        if start:
            command.append(str(start))
        if end:
            command.append(str(end))

        return await self.call(*command)

    async def decr(self, key: str) -> int:
        """Implement the DECR command (https://redis.io/commands/decr)."""
        return await self.call("DECR", key)

    async def decrby(self, key: str, decrement: int) -> int:
        """Implement the DECRBY command (https://redis.io/commands/decrby)."""
        return await self.call("DECRBY", key, str(decrement))

    async def get(self, key: str) -> bytes:
        """Implement the GET command (https://redis.io/commands/get)."""
        return await self.call("GET", key)

    async def getbit(self, key: str, index: int) -> int:
        """Implement the GETBIT command (https://redis.io/commands/getbit)."""
        return await self.call("GETBIT", key, str(index))

    async def getrange(self, key: str, start: int, end: int) -> bytes:
        """Implement the GETRANGE command (https://redis.io/commands/getrange)."""
        return await self.call("GETRANGE", key, str(start), str(end))

    async def getset(self, key: str, value: str) -> t.Optional[bytes]:
        """Implement the GETSET command (https://redis.io/commands/getset)."""
        return await self.call("GETSET", key, value)

    async def incr(self, key: str) -> int:
        """Implement the INCR command (https://redis.io/commands/incr)."""
        return await self.call("INCR", key)

    async def incrby(self, key: str, increment: int) -> int:
        """Implement the INCRBY command (https://redis.io/commands/incrby)."""
        return await self.call("INCRBY", key, str(increment))

    async def incrbyfloat(self, key: str, increment: float) -> float:
        """Implement the INCRBYFLOAT command (https://redis.io/commands/incrbyfloat)."""
        return float(await self.call("INCRBYFLOAT", key, str(increment)))

    async def mget(self, key: str, *keys: str) -> list:
        """Implement the MGET command (https://redis.io/commands/mget)."""
        return await self.call("MGET", key, *keys)

    async def mset(self, key: str, value: str, *more: str) -> bytes:
        """Implement the MSET command (https://redis.io/commands/mset)."""
        return await self.call("MSET", key, value, *more)

    async def msetnx(self, key: str, value: str, *more: str) -> int:
        """Implement the MSETNX command (https://redis.io/commands/msetnx)."""
        return await self.call("MSETNX", key, value, *more)

    async def set(
        self,
        key: str,
        value: str,
        *,
        ex: int = 0,
        px: int = 0,
        keepttl: bool = False,
        nx: bool = False,
        xx: bool = False,
    ):
        """Implement the SET command (https://redis.io/commands/set)."""
        command = ["SET", key, value]
        if bool(ex) + bool(px) + keepttl > 1:
            raise ValueError(
                f"More than one of {ex=}, {px=}, and {keepttl=} were specified"
            )
        if ex:
            command.extend(["EX", str(ex)])
        elif px:
            command.extend(["PX", str(px)])
        elif keepttl:
            command.append("KEEPTTL")

        if nx and xx:
            raise ValueError("Both nx and xx were specified")
        if nx:
            command.append("NX")
        elif xx:
            command.append("XX")

        return await self.call(*command)

    async def setbit(self, key: str, offset: int, value: t.Literal[0, 1]) -> int:
        """Implement the SETBIT command (https://redis.io/commands/setbit)."""
        return await self.call("SETBIT", key, str(offset), str(value))

    async def setrange(self, key: str, offset: int, value: str) -> int:
        """Implement the SETRANGE command (https://redis.io/commands/setrange)."""
        return await self.call("SETRANGE", key, str(offset), value)

    async def strlen(self, key: str) -> int:
        """Implement the STRLEN command (https://redis.io/commands/strlen)."""
        return await self.call("STRLEN", key)
