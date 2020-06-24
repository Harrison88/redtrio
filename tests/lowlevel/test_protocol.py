import pytest

from redtrio.lowlevel import protocol
from ..redis_commands import redis_commands


@pytest.fixture
def reader():
    return protocol.Resp3Reader()


@pytest.mark.parametrize("command_data", redis_commands.values())
def test_command_responses(reader, command_data):
    print("About to test", command_data["response_value"])
    reader.feed(command_data["response"])
    result = reader.get_object()
    assert result == command_data["response_value"]


@pytest.mark.parametrize("command_data", redis_commands.values())
def test_command_responses_one_byte(reader, command_data):
    print("About to test", command_data["response_value"], "one byte at a time")
    for b in (i.to_bytes(1, "little") for i in command_data["response"]):
        print("Getting object")
        result = reader.get_object()
        print("Got result:", result)
        print(reader.state_stack)
        assert result is reader.sentinel
        print("Feeding", b)
        reader.feed(b)

    print(reader.state_stack)
    result = reader.get_object()
    print("Got result:", result)
    assert result == command_data["response_value"]


@pytest.mark.parametrize("command_data", redis_commands.values())
def test_command_responses_two_bytes(reader, command_data):
    second = False
    for b in (i.to_bytes(1, "little") for i in command_data["response"]):
        if not second:
            reader.feed(b)
            second = True
        else:
            result = reader.get_object()
            assert result is reader.sentinel
            second = False
            reader.feed(b)

    result = reader.get_object()
    assert result == command_data["response_value"]
