import logging
import asyncio

from .tree import Tree

_log = logging.getLogger(__name__)


class Router:
    def __init__(self, debug=False, debug_interval=30):
        self.channels = Tree()

        self.debug_interval = debug_interval

        if debug:
            asyncio.get_event_loop()\
                .call_later(self.debug_interval, self.debug)

    def get(self, channel):
        return self.channels.get_matches(channel)

    def subscribe(self, websocket, *channels):
        _log.debug('%s: subscribing to %r', websocket.name, channels)
        self.channels.add(websocket, *channels)

    def unsubscribe(self, websocket, *channels):
        _log.debug('%s: unsubscribing from %r', websocket.name, channels)
        self.channels.remove(websocket, *channels)

    def debug(self):
        _log.debug('subscriptions: \n%r', self.channels)
        asyncio.get_event_loop().call_later(self.debug_interval, self.debug)
