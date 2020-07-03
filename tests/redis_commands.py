# flake8: noqa
from redtrio.lowlevel.protocol import RedisError

redis_commands = {
    b"HELLO 3": {
        "encoded": b"*2\r\n$5\r\nHELLO\r\n$1\r\n3\r\n",
        "response": b"%7\r\n$6\r\nserver\r\n$5\r\nredis\r\n$7\r\nversion\r\n$5\r\n6.0.5\r\n$5\r\nproto\r\n:3\r\n$2\r\nid\r\n:628\r\n$4\r\nmode\r\n$10\r\nstandalone\r\n$4\r\nrole\r\n$6\r\nmaster\r\n$7\r\nmodules\r\n*0\r\n",
        "response_value": {
            b"server": b"redis",
            b"version": b"6.0.5",
            b"proto": 3,
            b"id": 628,
            b"mode": b"standalone",
            b"role": b"master",
            b"modules": [],
        },
    },
    b"PING": {
        "encoded": b"*1\r\n$4\r\nPING\r\n",
        "response": b"+PONG\r\n",
        "response_value": b"PONG",
    },
    b"SET foo bar": {
        "encoded": b"*3\r\n$3\r\nSET\r\n$3\r\nfoo\r\n$3\r\nbar\r\n",
        "response": b"+OK\r\n",
        "response_value": b"OK",
    },
    b"GET foo": {
        "encoded": b"*2\r\n$3\r\nGET\r\n$3\r\nfoo\r\n",
        "response": b"$3\r\nbar\r\n",
        "response_value": b"bar",
    },
    b"MSET language Python version 3": {
        "encoded": b"*5\r\n$4\r\nMSET\r\n$8\r\nlanguage\r\n$6\r\nPython\r\n$7\r\nversion\r\n$1\r\n3\r\n",
        "response": b"+OK\r\n",
        "response_value": b"OK",
    },
    b"MGET language version": {
        "encoded": b"*3\r\n$4\r\nMGET\r\n$8\r\nlanguage\r\n$7\r\nversion\r\n",
        "response": b"*2\r\n$6\r\nPython\r\n$1\r\n3\r\n",
        "response_value": [b"Python", b"3"],
    },
    b"NOT A COMMAND": {
        "encoded": b"*3\r\n$3\r\nNOT\r\n$1\r\nA\r\n$7\r\nCOMMAND\r\n",
        "response": b"-ERR unknown command `NOT`, with args beginning with: `A`, `COMMAND`, \r\n",
        "response_value": RedisError(
            b"ERR", b"unknown command `NOT`, with args beginning with: `A`, `COMMAND`, "
        ),
    },
    b"GET nonexistent": {
        "encoded": b"*2\r\n$3\r\nGET\r\n$11\r\nnonexistant\r\n",
        "response": b"_\r\n",
        "response_value": None,
    },
}
