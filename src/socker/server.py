import logging
import asyncio

import websockets
import asyncio_redis

from .transport import SockMessage

_log = logging.getLogger(__name__)


@asyncio.coroutine
def redis_listener(queue, subscriber):

    while True:
        pub = yield from subscriber.next_published()

        _log.debug('From redis: %r', pub)
        yield from queue.put(('redis', pub))


@asyncio.coroutine
def websocket_listener(queue, websocket):
    while True:
        recv = yield from websocket.recv()

        _log.debug('from websocket: %r', recv)

        if recv is None:
            _log.info('Client closed connection, returning')
            return

        yield from queue.put(('websocket', recv))


@asyncio.coroutine
def hello(websocket, path):
    _log.info('Hello %r with path: %s', websocket, path)

    channels = set()

    try:
        connection = yield from asyncio_redis.Connection.create()
        subscriber = yield from connection.start_subscribe()
        queue = asyncio.Queue()

        asyncio.Task(redis_listener(queue, subscriber))
        asyncio.Task(websocket_listener(queue, websocket))

        while True:
            producer, data = yield from queue.get()

            _log.debug('Fresh produce! %r', (producer, data))

            if producer is 'redis':
                yield from websocket.send(
                        str(SockMessage.from_redis(data)))

            elif producer is 'websocket':
                message = data

                if message is None:
                    _log.debug('Client closed websocket')
                    break

                message = SockMessage.from_string(message)
                _log.debug('got message: %s', message)

                if message.name == 'subscribe':
                    _channels = set(message.data)
                    old_channels = list(channels - _channels)
                    new_channels = list(_channels - channels)

                    if old_channels:
                        _log.debug('Unsubscribing to redis channels %r...', old_channels)
                        yield from subscriber.unsubscribe(old_channels)
                        _log.debug('... unsubscribed')

                    if new_channels:
                        _log.debug('Subscribing to redis on channels %r...', new_channels)
                        yield from subscriber.subscribe(new_channels)
                        _log.debug('... subscribed')

                    channels = _channels

                else:
                    _log.warning('No handler for %s', message)

        _log.debug('Closing')
    except Exception as e:
        _log.exception('Ouch! %r', e)
    finally:
        yield from websocket.close()


def main(interface=None, port=None):
    if port is None:
        port = 8765

    if interface is None:
        interface = 'localhost'

    _log.info('Starting socker on {}:{}'.format(interface, port))

    start_server = websockets.serve(hello, interface, port)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    main()
