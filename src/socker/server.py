import logging
import asyncio

from functools import partial

import asyncio_redis
import websockets
from websockets.exceptions import InvalidState

from .tools import base_words
from .transport import Message
from .router import Router
from .auth import get_auth_coro

_log = logging.getLogger(__name__)


@asyncio.coroutine
def keep_alive(websocket, ping_period=30):
    while True:
        yield from asyncio.sleep(ping_period)

        try:
            yield from websocket.ping()
        except InvalidState:
            _log.debug('Got exception when trying to keep connection alive, '
                       'giving up.')
            return


@asyncio.coroutine
def websocket_handler(router, check_auth, websocket, path):
    websocket.name = base_words(id(websocket))

    channels = set()

    _log.info('New websocket %s with path: %s', websocket.name, path)

    # Launch keep-alive coroutine
    asyncio.async(keep_alive(websocket))

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
                requested_channels = _channels - channels

                new_channels = set()

                for channel in requested_channels:
                    auth_passed = yield from check_auth(channel, path)

                    if not auth_passed:
                        _log.info('Authentication failed for %s (path: %s) '
                                  'with channel %s',
                                  websocket.name,
                                  path,
                                  channel)
                    else:
                        new_channels.add(channel)

                if old_channels:
                    _log.debug('%s: Unsubscribing from channels %r...',
                               websocket.name, old_channels)
                    router.unsubscribe(websocket, *old_channels)

                if requested_channels:
                    _log.debug('%s: Subscribing to channels %r...',
                               websocket.name, requested_channels)
                    router.subscribe(websocket, *requested_channels)

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
def redis_subscriber(router, **kw):
    connection = yield from asyncio_redis.Connection.create(**kw)
    subscriber = yield from connection.start_subscribe()
    yield from subscriber.subscribe(['socker'])

    while True:
        pub = yield from subscriber.next_published()
        _log.debug('From redis: %r', pub)

        message = Message.from_string(pub.value)

        clients = router.get(message.name)

        for channel, websocket in clients:
            # Send the message with the same channel the client used to
            # subscribe.
            channel_message = Message(channel, message.data)
            yield from websocket.send(str(channel_message))


def main(interface='localhost', port=8765, debug=False, auth_backend=None,
         **kw):
    _log.info('Starting socker on {}:{}'.format(interface, port))

    router = Router(debug)

    # Transform {'redis_host': 'redis.example'} into {'host': 'redis.example'}
    redis_opts = {k.replace('redis_', ''): v
                  for k, v in kw.items()
                  if 'redis_' in k}

    check_auth = get_auth_coro(auth_backend)

    asyncio.async(redis_subscriber(router, **redis_opts))

    start_server = websockets.serve(
        partial(websocket_handler, router, check_auth),
        interface,
        port)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    main()
