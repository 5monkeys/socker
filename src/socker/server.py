import logging
import asyncio

from functools import partial

import asyncio_redis
import websockets

from .tools import base_words
from .transport import Message
from .router import Router

_log = logging.getLogger(__name__)


@asyncio.coroutine
def websocket_handler(router, websocket, path):
    websocket.name = base_words(id(websocket))

    channels = set()

    _log.info('New websocket %s with path: %s', websocket.name, path)

    try:
        while True:
            data = yield from websocket.recv()

            if data is None:
                _log.debug('Client closed websocket')
                break

            message = Message.from_string(data)
            _log.debug('got message: %s', message)

            if message.name == 'subscribe':
                _channels = set(message.data)
                old_channels = channels - _channels
                new_channels = _channels - channels

                if old_channels:
                    _log.debug('%s: Unsubscribing from channels %r...',
                               websocket.name, old_channels)
                    router.unsubscribe(websocket, *old_channels)

                if new_channels:
                    _log.debug('%s: Subscribing to channels %r...',
                               websocket.name, new_channels)
                    router.subscribe(websocket, *new_channels)

                channels = _channels
            else:
                _log.warning('No handler for %s', message)

        _log.debug('Closing')
    except Exception as e:
        _log.exception('Ouch! %r', e)
    finally:
        router.unsubscribe(websocket, *channels)

    yield from websocket.close()


@asyncio.coroutine
def redis(router, **kw):
    connection = yield from asyncio_redis.Connection.create(**kw)
    subscriber = yield from connection.start_subscribe()
    yield from subscriber.subscribe(['socker'])

    while True:
        pub = yield from subscriber.next_published()
        _log.debug('From redis: %r', pub)

        message = Message.from_string(pub.value)

        clients = router.get(message.name)

        for channel, websocket in clients:
            # Create a new channel with the channel name that the Socker
            # client used to subscribe. We do this in order to not have
            # the wildcard matching in more than one place.
            channel_message = Message(channel, message.data)
            yield from websocket.send(str(channel_message))


def main(interface='localhost', port=8765, debug=False, **kw):
    _log.info('Starting socker on {}:{}'.format(interface, port))

    router = Router(debug, debug_interval=10)

    # Transform {'redis_host': 'redis.example'} into {'host': 'redis.example'}
    redis_opts = {k.replace('redis_', ''): v
                  for k, v in kw.items()
                  if 'redis_' in k}

    asyncio.async(redis(router, **redis_opts))

    start_server = websockets.serve(
        partial(websocket_handler, router),
        interface,
        port)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    main()
