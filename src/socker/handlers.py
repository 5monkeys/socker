import asyncio
import logging
import json

from websockets.exceptions import InvalidState

_log = logging.getLogger(__name__)


async def keep_alive(websocket, ping_period=30):
    while True:
        await asyncio.sleep(ping_period)

        try:
            await websocket.ping()
        except InvalidState:
            _log.exception(
                "%s: Got exception when trying to keep connection alive, " "giving up.",
                websocket.name,
            )
            return


def set_subscriptions(websocket, router, subscriptions, message, check_auth, **kwargs):
    _subscriptions = set(message.data)
    old_subscriptions = subscriptions - _subscriptions
    requested_subscriptions = _subscriptions - subscriptions

    new_subscriptions = set()

    # Check that the client has access to the requested subscriptions.
    for channel in requested_subscriptions:
        if check_auth(channel):
            new_subscriptions.add(channel)

    if old_subscriptions:
        _log.debug(
            "%s: Unsubscribing from subscriptions %r...",
            websocket.name,
            old_subscriptions,
        )
        router.unsubscribe(websocket, *old_subscriptions)

    if requested_subscriptions:
        _log.debug(
            "%s: Subscribing to subscriptions %r...",
            websocket.name,
            requested_subscriptions,
        )
        router.subscribe(websocket, *requested_subscriptions)

    # Update the state variable with the result of the checking.
    subscriptions = _subscriptions

    return subscriptions


def subscribe(websocket, router, subscriptions, message, check_auth, **kwargs):
    channels = _get_channels_from_message(message, websocket)

    for channel in channels:
        if channel is not None and check_auth(channel):
            _log.debug("%s: Subscribing to %s", websocket.name, channel)
            router.subscribe(websocket, channel)
            subscriptions.add(channel)
        else:
            _log.warn(
                "%s: Invalid channel or failed auth for %r", websocket.name, channel
            )


def unsubscribe(websocket, message, router, check_auth, subscriptions, **kwargs):
    channels = _get_channels_from_message(message, websocket)

    for channel in channels:
        if channel is not None and check_auth(channel):
            _log.debug("%s: Unsubscribing from %s", websocket.name, channel)
            router.unsubscribe(websocket, channel)
            subscriptions.remove(channel)
        else:
            _log.warn(
                "%s: Invalid channel or failed auth for %r", websocket.name, channel
            )


def get_subscriptions(websocket, router, subscriptions, **kwargs):
    _log.debug("get_subscriptions, %r", subscriptions)
    return "#{}".format(json.dumps(list(subscriptions)))


def _get_channels_from_message(message, websocket):
    channels = message.data

    if not isinstance(channels, (str, list)):
        raise ChannelTypeError("Channel {0!r} is not a string or list".format(channels))

    if isinstance(channels, str):
        channels = [channels]

    return channels


class ChannelTypeError(TypeError):
    pass
