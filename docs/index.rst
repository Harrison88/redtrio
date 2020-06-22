Redtrio
=======

.. toctree::
   :hidden:
   :maxdepth: 1

Redtrio is an async (Trio) client supporting Redis 6+, using the RESP3 protocol.


Installation
------------

To install redtrio,
run this command in your terminal:

.. code-block:: console

   $ pip install redtrio


Usage
-----

Redtrio's usage looks like:

.. code-block:: python

   >>>from redtrio.lowlevel import RedisClient
   >>>client = RedisClient()
   >>>await client.call(b"PING")
   b"PONG"