import typing as t


class NotEnoughDataError(Exception):
    pass


class Resp3Reader:
    def __init__(self):
        self._buffer = bytearray()
        self.sentinel = object()
        self.current_object = self.sentinel
        self._state = None
        self.state_stack = []
        self.object_stack = []

        self.types = {
            ord("%"): self.parse_map,
            ord("+"): self.parse_simple_string,
            ord("$"): self.parse_blob,
            ord(":"): self.parse_number,
            ord("*"): self.parse_array,
        }

    def feed(self, data):
        self._buffer.extend(data)

    def eat(self, num_bytes: int, state=None) -> t.Optional[bytearray]:
        if state:
            self.state_stack.append(state)
        if len(self._buffer) < num_bytes:
            raise NotEnoughDataError
        if state:
            self.state_stack.pop()
        data = self._buffer[:num_bytes]
        del self._buffer[:num_bytes]
        return data

    def eat_linebreak(self, state=None):
        linebreak = b"\r\n"

        if state:
            self.state_stack.append(state)
        if linebreak not in self._buffer:
            raise NotEnoughDataError
        if state:
            self.state_stack.pop()

        index = self._buffer.index(linebreak)
        data = self.eat(index + 2)
        return data[:-2]

    def get_object(self):
        try:
            return self.parse(check_state=True)
        except NotEnoughDataError:
            return False

    def parse(self, check_state=False, state=None):
        if check_state and self.state_stack:
            state = self.state_stack.pop()
            return state["function"](state=state)

        object_type = self.eat(1, state=state)
        object_parser = self.types[ord(object_type)]
        return object_parser()

    def parse_map(self, state=None):
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

            if state["action"] is READ_VALUE:
                name = state["next_key_name"]
                state["object"][name] = self.parse(state=state)
                state["action"] = READ_KEY_NAME

        return state["object"]

    def parse_simple_string(self, state=None):
        state = {"function": self.parse_simple_string}
        line = self.eat_linebreak(state=state)
        return line.decode()

    def parse_blob(self, state=None):
        if state is None:
            state = {"function": self.parse_blob}

        if "length" not in state:
            state["length"] = int(self.eat_linebreak(state=state))

        state["object"] = self.eat(state["length"], state=state)
        self.eat(2, state=state)  # Discard the line break after the data
        return bytes(state["object"])

    def parse_number(self, state=None):
        state = {"function": self.parse_number}
        line = self.eat_linebreak(state=state)
        return int(line)

    def parse_array(self, state=None):
        if state is None:
            state = {"function": self.parse_array, "object": []}

        if "length" not in state:
            state["length"] = int(self.eat_linebreak(state=state))

        while len(state["object"]) < state["length"]:
            state["object"].append(self.parse(state=state))

        return state["object"]


def write_command(command, *args):
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