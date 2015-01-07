from asyncio.tasks import FIRST_COMPLETED
import json
import logging
import asyncio
import websockets
import asyncio_redis

_log = logging.getLogger(__name__)


class SockMessage:
    def __init__(self, name, data):
        self.name = name
        self.data = data

    @classmethod
    def from_redis(cls, reply):
        return cls(reply.channel, json.loads(reply.value))

    @classmethod
    def from_string(cls, string):
        name, json_str = string.split('|', 1)
        data = json.loads(json_str)

        return cls(name, data)

    def __str__(self):
        return self.name + '|' + json.dumps(self.data)


@asyncio.coroutine
def redis_listener(queue, connection):
    subscriber = yield from connection.start_subscribe()

    channels = ['hello']
    channels_last = []

    while True:
        if channels != channels_last:
            _log.debug('Subscribing to redis on channels %r...', channels)
            yield from subscriber.subscribe(channels)
            channels_last = channels
            _log.debug('... subscribed to redis')

            _log.debug('Waiting for redis pub')

        pub = yield from subscriber.next_published()

        _log.debug('From redis: %r', pub)
        yield from queue.put(('redis', pub))


@asyncio.coroutine
def websocket_listener(queue, websocket):
    while True:
        recv = yield from websocket.recv()

        _log.debug('from websocket: %r', recv)
        yield from queue.put(('websocket', recv))


@asyncio.coroutine
def hello(websocket, path):
    _log.info('Hello %r with path: %s', websocket, path)
    try:
        connection = yield from asyncio_redis.Connection.create()
        queue = asyncio.Queue()

        asyncio.async(redis_listener(queue, connection))
        asyncio.async(websocket_listener(queue, websocket))

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
                    _log.warning('Refactor!')
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