import signal
import logging
import asyncio

from .tree import Tree

_log = logging.getLogger(__name__)


class Router:
    def __init__(self, debug=False):
        self.channels = Tree()

        if debug:
            asyncio.get_event_loop().add_signal_handler(signal.SIGUSR1, self.debug)

    def get(self, channel):
        return self.channels.get_matches(channel)

    def subscribe(self, websocket, *channels):
        _log.debug("%s: subscribing to %r", websocket.name, channels)
        self.channels.add(websocket, *channels)

    def unsubscribe(self, websocket, *channels):
        _log.debug("%s: unsubscribing from %r", websocket.name, channels)
        self.channels.remove(websocket, *channels)

    def debug(self):
        _log.debug("subscriptions: \n%r", self.channels)
