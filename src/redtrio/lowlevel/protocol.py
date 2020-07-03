"""The protocol module contains the RESP3 implementation.

Classes:
    NotEnoughDataError - an internal error used by Resp3Reader
    Resp3Reader - used for parsing responses from the server into Python objects

Functions:
    write_command - used to encode commands + args in RESP3 to send to the server
"""

import typing as t


class NotEnoughDataError(Exception):
    """Raised to indicate that not enough data has been fed to parse the object."""


class RedisError(Exception):
    """Represents an error returned from the Redis server."""

    def __eq__(self, other):
        """It is equal to another RedisError if it has the same arguments."""
        return self.args == other.args


class ProtocolError(Exception):
    """An error occurred while parsing."""


class Resp3Reader:
    """This class parses RESP3 responses from the Redis server.

    Attributes:
        _buffer (bytearray): Data gets fed into this buffer and removed by the parser.
        sentinel (object): A sentinel object, returned by *get_object* when no object
            has been parsed yet.
        state_stack (list): A stack that keeps track of the state, allowing
            restarting after more data has been fed.
        types (dict): A mapping of parser functions related to a particular byte.
    """

    def __init__(self):
        """Initialize the Resp3Reader."""
        self._buffer = bytearray()
        self.sentinel = object()
        self.state_stack: t.List[dict] = []

        self.types = {
            ord("%"): self.parse_map,
            ord("+"): self.parse_simple_string,
            ord("$"): self.parse_blob,
            ord(":"): self.parse_number,
            ord("*"): self.parse_array,
            ord("-"): self.parse_simple_error,
            ord("_"): self.parse_null,
            ord(","): self.parse_double,
            ord("#"): self.parse_boolean,
            ord("!"): self.parse_blob_error,
            ord("="): self.parse_verbatim_string,
            ord("("): self.parse_big_number,
        }

    def feed(self, data: bytes):
        """Extend the buffer with data.

        Arguments:
            data (bytes): Bytes received from the server.
        """
        self._buffer.extend(data)

    def eat(self, num_bytes: int, state: t.Optional[dict] = None) -> bytes:
        """Remove the specified number of bytes from _buffer and return them.

        If there aren't enough bytes, raises NotEnoughDataError. If state was passed,
        then it first saves the state.

        Arguments:
            num_bytes (int): The number of bytes to attempt to remove from the buffer.
            state (dict): A dictionary containing the state, to be saved in the
                event there isn't enough data.

        Returns:
            A bytes object containing the requested number of bytes from _buffer.

        Raises:
            NotEnoughDataError: Not enough data is in the buffer.
        """
        if state:
            self.state_stack.append(state)
        if len(self._buffer) < num_bytes:
            raise NotEnoughDataError
        if state:
            self.state_stack.pop()
        data = self._buffer[:num_bytes]
        del self._buffer[:num_bytes]
        return bytes(data)

    def eat_linebreak(self, state: dict) -> bytes:
        """A convenience function to call *eat* up to the next CRLF.

        If there isn't enough data in the buffer, the state is saved on the stack
        and NotEnoughDataError is raised.
        The linebreak is discarded, while all the data up to the linebreak is returned.

        Arguments:
            state (dict): A dictionary containing the state, to be saved in the
                event there isn't enough data.

        Returns:
            A bytearray containing the data up to, and excluding, the linebreak.

        Raises:
            NotEnoughDataError: Not enough data is in the buffer.
        """
        linebreak = b"\r\n"

        self.state_stack.append(state)
        if linebreak not in self._buffer:
            raise NotEnoughDataError
        self.state_stack.pop()

        index = self._buffer.index(linebreak)
        data = self.eat(index + 2)
        return bytes(data[:-2])

    def get_object(self) -> t.Any:
        """Get an object using the data from *feed*.

        If NotEnoughDataError is raised while parsing, *sentinel* is returned, instead.
        If *sentinel* is returned, more data must be fed, and this method called again.

        Returns:
            The object parsed from the RESP3 data.
        """
        try:
            return self.parse(check_state=True)
        except NotEnoughDataError:
            return self.sentinel

    def parse(self, check_state: bool = True, state: t.Optional[dict] = None):
        """Parse data and call an object parser based on the byte defined in self.types.

        If check_state and the state stack is not empty,
        then run through the state stack to return to the previous state.
        Otherwise, eat a byte and use it to determine which specific object
            parser to call.

        Arguments:
            check_state (bool): Whether to check the state stack or not
                (default: True).
            state (dict): State to be saved while checking the state stack
                (default: None).

        Returns:
            The parsed object.
        """
        if check_state and self.state_stack:
            checked_state = self.state_stack.pop(0)
            if state:
                self.state_stack.append(state)
            result = checked_state["function"](state=checked_state)
            if state:
                self.state_stack.pop()
            return result

        object_type = self.eat(1, state=state)

        if state:
            self.state_stack.append(state)
        object_parser = self.types[ord(object_type)]
        result = object_parser()
        if state:
            self.state_stack.pop()
        return result

    def parse_map(self, state: t.Optional[dict] = None):
        """Parse a RESP3 map object (byte: %) into a Python dictionary.

        Arguments:
            state (dict): If this is passed, parsing will resume from where it
                left off.

        Returns:
            The parsed dictionary.
        """
        READ_KEY_NAME = "read_key"
        READ_VALUE = "read_value"

        if state is None:
            state = {"function": self.parse_map, "object": {}}

        if "length" not in state:
            state["length"] = int(self.eat_linebreak(state=state))
            state["action"] = READ_KEY_NAME

        while len(state["object"]) < state["length"]:
            if state["action"] is READ_KEY_NAME:
                key_name = self.parse(state=state)
                state["next_key_name"] = key_name
                state["action"] = READ_VALUE

            else:
                name = state["next_key_name"]
                state["object"][name] = self.parse(state=state)
                state["action"] = READ_KEY_NAME

        return state["object"]

    def parse_simple_string(self, state: t.Optional[dict] = None):
        """Parse a RESP3 simple string (byte: +) into a bytes object.

        Arguments:
            state (dict): Simple strings don't require state, but this argument
                is still present to keep the signature the same as other object
                parsers.

        Returns:
            A bytes object representing the parsed simple string.
        """
        state = {"function": self.parse_simple_string}
        line = self.eat_linebreak(state=state)
        return line

    def parse_blob(self, state: t.Optional[dict] = None):
        """Parse a RESP3 blob (byte: $) into a bytes object.

        Arguments:
            state (dict): If this is passed, parsing will resume from where it
                left off.

        Returns:
            A bytes object representing the parsed blob string.
        """
        if state is None:
            state = {"function": self.parse_blob}

        if "length" not in state:
            state["length"] = int(self.eat_linebreak(state=state))

        if "object" not in state:
            state["object"] = self.eat(state["length"], state=state)

        self.eat(2, state=state)  # Discard the line break after the data
        return bytes(state["object"])

    def parse_number(self, state: t.Optional[dict] = None):
        """Parse a RESP3 number (byte: :) into a Python int.

        Arguments:
            state (dict): Numbers don't require state, but this argument is still
                present to keep the function signature the same as other object
                parsers.

        Returns:
            An int representing the parsed number.
        """
        state = {"function": self.parse_number}
        line = self.eat_linebreak(state=state)
        return int(line)

    def parse_array(self, state: t.Optional[dict] = None):
        """Parse a RESP3 array (byte: *) into a Python list.

        Arguments:
            state (dict): If this is passed, parsing will resume from where it
                left off.

        Returns:
            A list representing the parsed array.
        """
        if state is None:
            state = {"function": self.parse_array, "object": []}

        if "length" not in state:
            state["length"] = int(self.eat_linebreak(state=state))

        while len(state["object"]) < state["length"]:
            state["object"].append(self.parse(state=state))

        return state["object"]

    def parse_simple_error(self, state: t.Optional[dict] = None) -> RedisError:
        """Parse a simple error (byte: -) into a RedisError.

        Arguments:
            state (dict): Simple errors don't require state, but this argument is still
                present to keep the function signature the same as other object
                parsers.

        Returns:
            A RedisError representing the parsed error.
        """
        state = {"function": self.parse_simple_error}
        line = self.eat_linebreak(state=state)
        error, _, message = line.partition(b" ")
        return RedisError(error, message)

    def parse_null(self, state: t.Optional[dict] = None) -> None:
        """Parse null (byte: _) into None.

        Arguments:
            state (dict): null doesn't require state, but this argument is still
                present to keep the function signature the same as other object
                parsers.

        Returns:
            None
        """
        state = {"function": self.parse_null}
        self.eat_linebreak(state=state)
        return None

    def parse_double(self, state: t.Optional[dict] = None) -> float:
        """Parse a double (byte: ,) into a float.

        Arguments:
            state (dict): doubles don't require state, but this argument is still
                present to keep the function signature the same as other object
                parsers.

        Returns:
            The parsed float.
        """
        state = {"function": self.parse_double}
        line = self.eat_linebreak(state=state)
        return float(line)

    def parse_boolean(self, state: t.Optional[dict] = None) -> bool:
        """Parse a boolean (byte: #) into a bool.

        Arguments:
            state (dict): boolens don't require state, but this argument is still
                present to keep the function signature the same as other object
                parsers.

        Returns:
            The parsed bool.

        Raises:
            ProtocolError: an incorrect value was passed (not t or f).
        """
        state = {"function": self.parse_boolean}
        line = self.eat_linebreak(state=state)
        if line == b"t":
            return True
        if line == b"f":
            return False

        raise ProtocolError(
            "A boolean was supposed to be parsed, but the value was neither t nor f"
        )

    def parse_blob_error(self, state: t.Optional[dict] = None) -> RedisError:
        """Parse a blob error (byte: !) into a RedisError.

        Has the same basic implementation as a blob string.

        Arguments:
            state (dict): If this is passed, parsing will resume from where it
                left off.

        Returns:
            The parsed RedisError.
        """
        if state is None:
            state = {"function": self.parse_blob_error}

        if "length" not in state:
            state["length"] = int(self.eat_linebreak(state=state))

        if "object" not in state:
            state["object"] = self.eat(state["length"], state=state)

        self.eat(2, state=state)  # Discard the line break after the data
        error, _, message = state["object"].partition(b" ")
        return RedisError(error, message)

    def parse_verbatim_string(self, state: t.Optional[dict] = None) -> bytes:
        """Parse a verbatim string (byte: =) into bytes.

        Has the same basic implementation as a blob string.

        Arguments:
            state (dict): If this is passed, parsing will resume from where it
                left off.

        Returns:
            The parsed bytes.
        """
        if state is None:
            state = {"function": self.parse_verbatim_string}

        if "length" not in state:
            state["length"] = int(self.eat_linebreak(state=state))

        if "object" not in state:
            state["object"] = self.eat(state["length"], state=state)

        self.eat(2, state=state)  # Discard the line break after the data
        return state["object"][4:]  # Return the string after the format marker.

    def parse_big_number(self, state: t.Optional[dict] = None) -> int:
        """Parse a big number (byte: () into an int.

        Arguments:
            state (dict): big numbers don't require state, but this argument is still
                present to keep the function signature the same as other object
                parsers.

        Returns:
            The parsed int.
        """
        state = {"function": self.parse_big_number}
        line = self.eat_linebreak(state=state)
        return int(line)


def write_command(command: bytes, *args: bytes) -> bytes:
    r"""Encode the given command and args into a RESP3 array to be sent to the server.

    Note that no spaces are allowed in the command. Redis commands that contain a space
    (for example, "MODULE LOAD")
    are actually encoded as a command + an argument. Higher level interfaces will
    take care of this for you.

    Arguments:
        command (bytes): The command to be sent.
        *args (bytes): The args to send with the command.

    Returns:
        The encoded RESP3 array as a bytes object.

    Example:
        >>>write_command(b"SET", b"key", b"value")

        b'*3\r\n$3\r\nSET\r\n$3\r\nkey\r\n$5\r\nvalue\r\n'
    """
    length = len(args) + 1

    packed_command = b"*%(num_args)d\r\n$%(command_length)d\r\n%(command)b\r\n" % {
        b"num_args": length,
        b"command_length": len(command),
        b"command": command,
    }
    packed_args = b""
    for arg in args:
        packed_args += b"$%(arg_length)d\r\n%(arg)b\r\n" % {
            b"arg_length": len(arg),
            b"arg": arg,
        }

    return packed_command + packed_args
