=======================================================
socker - pubsub websocket proxy server built on asyncio
=======================================================

socker runs as a single-process service, using asyncio for non-blocking I/O.

socker uses a single redis pubsub channel, and has its own channel
subscription logic, this means that you may share redis database with other
applications.

socker runs as a single-process service. socker opens up a websocket
server port and establishes a redis connection. The redis connection creates
a subscription on the socker channel.


------------
Installation
------------


socker is not on PyPI, so you'll have to run

.. code-block:: bash

    pip install -e 'git+http://github.com/5monkeys/socker.git#egg=socker'

in order to use it.

-----
Usage
-----

.. code-block:: bash

    $ socker -h
    Start the socker websocket server

    Usage:
      socker [options]
      socker -? | --help
      socker --version

    Options:
      -i INTERFACE    Listening interface [default: localhost]
      -p PORT         Listening port [default: 8765]

      -v              Enable verbose output

      --redis-host=HOST             Redis host [default: localhost]
      --redis-port=PORT             Redis port [default: 6379]
      --redis-db=DB                 Redis database [default: 0]
      --redis-password=PASSWORD     Redis password

      --logto FILE    Log output to FILE instead of console

      --version       show version
      -? --help       Show this screen


To publish a message to socker from another application:

.. code-block:: python

    from socker import Message


    channel = 'foo.bar.42'
    data = {
        'yes': [
            'yes',
            'no',
            'baz'
        ]
    }

    redis_client.publish('socker', Message(channel, data))

Any websocket clients subscribed to

-   ``foo.*``
-   ``foo.bar.*``
-   ``foo.bar.42``

will receive that message.

------
Thanks
------

Thanks to

- https://github.com/aaugustin/websockets
- https://github.com/jonathanslenders/asyncio-redis

for their brilliant asyncio packages.
