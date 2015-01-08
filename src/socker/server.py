import logging
import asyncio

from collections import defaultdict
from functools import partial

import asyncio_redis
import websockets

from .transport import Message

_log = logging.getLogger(__name__)


@asyncio.coroutine
def websocket_handler(router, websocket, path):
    channels = set()
    _log.info('New websocket %r with path: %s', websocket, path)

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
                    _log.debug('%s: Unsubscribing to redis channels %r...',
                               id(websocket), old_channels)
                    router.unsubscribe(websocket, *old_channels)

                if new_channels:
                    _log.debug('%s: Subscribing to redis on channels %r...',
                               id(websocket), new_channels)
                    router.subscribe(websocket, *new_channels)

                channels = _channels

            else:
                _log.warning('No handler for %s', message)

        _log.debug('Closing')
    except Exception as e:
        _log.exception('Ouch! %r', e)
    finally:
        yield from websocket.close()


@asyncio.coroutine
def redis(router):
    connection = yield from asyncio_redis.Connection.create()
    subscriber = yield from connection.start_subscribe()
    yield from subscriber.subscribe(['socker'])

    while True:
        pub = yield from subscriber.next_published()
        _log.debug('From redis: %r', pub)

        message = Message.from_string(pub.value)

        clients = router.get(message.name)

        for websocket in clients:
            yield from websocket.send(pub.value)


class Router(object):

    def __init__(self):
        self.channels = defaultdict(list)

    def get(self, channel):
        return self.channels[channel]

    def subscribe(self, websocket, *channels):
        for channel in channels:
            self.channels[channel].append(websocket)

    def unsubscribe(self, websocket, *channels):
        for channel in channels:
            self.channels[channel].remove(websocket)


def main(interface=None, port=None):
    if port is None:
        port = 8765

    if interface is None:
        interface = 'localhost'

    _log.info('Starting socker on {}:{}'.format(interface, port))

    router = Router()

    asyncio.async(redis(router))

    start_server = websockets.serve(
        partial(websocket_handler, router),
        interface,
        port)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    main()
