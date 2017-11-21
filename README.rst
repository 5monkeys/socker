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

.. code-block:: bash

    pip install socker

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

-------------------------------
Releasing a new version to PyPi
-------------------------------

1. Bump the version in ``VERSION``.
2. Commit the change and tag it with the new version identifier.
3. Build a source distribution: ``python setup.py sdist``.
4. Build a wheel: ``python setup.py bdist_wheel``.
5. Upload the built distribution using Twine_: ``twine upload dist/*``.

.. _Twine: https://github.com/pypa/twine

------
Thanks
------

Thanks to

- https://github.com/aaugustin/websockets
- https://github.com/jonathanslenders/asyncio-redis

for their brilliant asyncio packages.
