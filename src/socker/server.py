import logging
import asyncio

from collections import defaultdict
from functools import partial
from array import array

import asyncio_redis
import websockets

from .transport import Message

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
                    _log.debug('%s: Unsubscribing to redis channels %r...',
                               websocket.name, old_channels)
                    router.unsubscribe(websocket, *old_channels)

                if new_channels:
                    _log.debug('%s: Subscribing to redis on channels %r...',
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

        for websocket in clients:
            yield from websocket.send(pub.value)


class Router(object):

    def __init__(self, debug=False, debug_interval=30):
        self.channels = defaultdict(list)

        self.debug_interval = debug_interval

        if debug:
            asyncio.get_event_loop()\
                .call_later(self.debug_interval, self.debug)

    def get(self, channel):
        return self.channels[channel]

    def subscribe(self, websocket, *channels):
        _log.debug('%s: subscribing to %r', websocket.name, channels)
        for channel in channels:
            self.channels[channel].append(websocket)

    def unsubscribe(self, websocket, *channels):
        _log.debug('%s: unsubscribing from %r', websocket.name, channels)
        for channel in channels:
            self.channels[channel].remove(websocket)

    def debug(self):
        _log.debug('subscriptions: \n%s', self.format_subscriptions())
        asyncio.get_event_loop().call_later(self.debug_interval, self.debug)

    def format_subscriptions(self):
        import pprint
        return pprint.pformat(dict(self.readable_channels()))

    def readable_channels(self):
        for channel, subscribers in self.channels.items():
            yield channel, len(subscribers)


def base_words(integer):
    """
    Convert a positive integer to a memorable string based on words from
    /usr/share/dict/words.

    :param integer: positive base 10 number
    :type integer: int
    :return: str containing capitalized words
    """
    if integer < 0:
        raise ValueError('base_words does not support negative integers')

    # Save the words in an in-memory cache attached to this method.
    if not hasattr(base_words, 'cache'):
        base_words.cache = words = []
        for word in open('/usr/share/dict/words', 'r'):
            # Filter out plurals, possessive form and conjugations.
            if '\'' not in word:
                words.append(word.strip().capitalize())

    words = base_words.cache

    new_base = len(words)

    result = ''

    current = integer

    while current != 0:
        current, remainder = divmod(current, new_base)
        result += words[remainder]

    return result


def main(interface=None, port=None, debug=False, **kw):
    if port is None:
        port = 8765

    if interface is None:
        interface = 'localhost'

    _log.info('Starting socker on {}:{}'.format(interface, port))

    router = Router(debug, debug_interval=10)

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
