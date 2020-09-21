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
