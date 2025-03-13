import logging
import asyncio

from functools import partial

import asyncio_redis
import websockets

from .tools import base_words
from .transport import Message
from .router import Router
from .auth import get_auth_coro
from . import handlers

_log = logging.getLogger(__name__)


def check_auth(auth_function, websocket, uri_path, channel):
    """
    Helper method for handlers to check channel access.

    :param auth_function: Auth backend method.
    :param websocket: websocket instance.
    :param uri_path:
    :param channel: channel string.
    :return: boolean "is allowed" value.
    """
    auth_passed = yield from auth_function(channel, uri_path)

    if not auth_passed:
        _log.info(
            "Authentication failed for %s (uri_path: %s) " "with channel %s",
            websocket.name,
            uri_path,
            channel,
        )
        return False
    else:
        return True


async def websocket_handler(router, auth_function, websocket, uri_path):
    websocket.name = base_words(id(websocket))

    subscriptions = set()

    _log.info("%s: New websocket with path: %s", websocket.name, uri_path)

    # Launch keep-alive coroutine
    await handlers.keep_alive(websocket)

    try:
        while True:
            data = await websocket.recv()

            if data is None:
                _log.debug("%s: Client closed websocket", websocket.name)
                break

            message = Message.from_string(data)
            _log.debug("%s: got message: %s", websocket.name, message)

            context = {
                "websocket": websocket,
                "router": router,
                "subscriptions": subscriptions,
                "message": message,
                "uri_path": uri_path,
                "check_auth": partial(check_auth, auth_function, websocket, uri_path),
            }

            try:
                if message.name == "set-subscriptions":
                    subscriptions = handlers.set_subscriptions(**context)
                elif message.name == "get-subscriptions":
                    await websocket.send(handlers.get_subscriptions(**context))
                elif message.name == "subscribe":
                    handlers.subscribe(**context)
                elif message.name == "unsubscribe":
                    handlers.unsubscribe(**context)
                else:
                    _log.warning("%s: No handler for %s", websocket.name, message)

            except handlers.ChannelTypeError as exc:
                _log.exception("%s: Got ChannelTypeError", websocket.name)
                await websocket.send("#{}".format(str(exc)))

    except Exception:
        _log.exception("%s: Ouch", websocket.name)
    finally:
        router.unsubscribe(websocket, *subscriptions)

    await websocket.close()


async def redis_subscriber(router, **kw):
    connection = await asyncio_redis.Connection.create(**kw)
    subscriber = await connection.start_subscribe()
    await subscriber.subscribe(["socker"])

    while True:
        pub = await subscriber.next_published()
        _log.debug("From redis: %r", pub)

        message = Message.from_string(pub.value)

        clients = router.get(message.name)

        for channel, websocket in clients:
            # Send the message with the same channel the client used to
            # subscribe.
            channel_message = Message(channel, message.data)
            await websocket.send(str(channel_message))


async def main(interface="localhost", port=8765, debug=False, auth_backend=None, **kw):
    _log.info("Starting socker on {}:{}".format(interface, port))

    router = Router(debug)

    # Transform {'redis_host': 'redis.example'} into {'host': 'redis.example'}
    redis_opts = {k.replace("redis_", ""): v for k, v in kw.items() if "redis_" in k}

    auth_function = get_auth_coro(auth_backend)

    await redis_subscriber(router, **redis_opts)

    start_server = websockets.serve(
        partial(websocket_handler, router, auth_function), interface, port
    )

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    asyncio.run(main())
