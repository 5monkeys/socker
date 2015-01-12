import logging
import asyncio

_log = logging.getLogger(__name__)

from collections import defaultdict


class Tree(defaultdict, dict):
    def __init__(self):
        defaultdict.__init__(self, self.__class__)
        self.subscribers = set()

    def __repr__(self):
        repr_ = dict(self)
        repr_.update(self.__dict__)
        return repr(repr_)

    def subscribe(self, channel, subscriber):
        parts = channel.split('.')
        cursor = self

        for part in parts:
            cursor = cursor[part]

        cursor.subscribers.add(subscriber)

    def unsubscribe(self, channel, subscriber):
        parts = channel.split('.')

        cursor = self

        for part in parts:
            cursor = cursor[part]

        cursor.subscribers.remove(subscriber)

    def get_subscribers(self, channel):
        parts = channel.split('.')

        cursor = self

        for part in parts:
            yield from cursor['*'].subscribers
            cursor = cursor[part]

        yield from cursor.subscribers


class Router:
    def __init__(self, debug=False, debug_interval=30):
        self.channels = Tree()

        self.debug_interval = debug_interval

        if debug:
            asyncio.get_event_loop()\
                .call_later(self.debug_interval, self.debug)

    def get(self, channel):
        return self.channels.get_subscribers(channel)

    def subscribe(self, websocket, *channels):
        _log.debug('%s: subscribing to %r', websocket.name, channels)
        for channel in channels:
            self.channels.subscribe(channel, websocket)

    def unsubscribe(self, websocket, *channels):
        _log.debug('%s: unsubscribing from %r', websocket.name, channels)
        for channel in channels:
            self.channels.unsubscribe(channel, websocket)

    def debug(self):
        _log.debug('subscriptions: \n%s', self.format_subscriptions())
        asyncio.get_event_loop().call_later(self.debug_interval, self.debug)

    def format_subscriptions(self):
        import pprint
        return pprint.pformat(dict(self.readable_channels()))

    def readable_channels(self):
        for channel, subscribers in self.channels.items():
            yield channel, len(subscribers)