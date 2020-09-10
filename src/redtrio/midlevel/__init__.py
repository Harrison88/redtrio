"""The Midlevel client is a layer of abstraction above the lowlevel client.

In particular, this means:

1. Each command has its own function with type hints.

2. Where possible, arguments supplied to a command will be converted
   automatically from their type to the bytes that Redis expects to receive.

3. HELLO 3 is called automatically.

4. Some return types are changed, where it makes sense. For example, INCRBYFLOAT
   returns a float instead of the bytes that Redis returns.
"""
from .client import MidlevelClient
