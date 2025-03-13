import asyncio
import logging
import importlib

from functools import partial
from urllib.parse import urlsplit, parse_qsl

from werkzeug.datastructures import ImmutableMultiDict

_log = logging.getLogger(__name__)


def example_backend(channel, path, params):
    _log.debug("channel: %s, path: %s, params: %s", channel, path, params)
    if params.get("secret") == "42":
        return True

    return False


def default_backend(*args):
    """
    Default auth backend, allows everything.

    :param args:
    :return:
    """
    _log.debug("default backend called with %s", args)
    return True


def get_backend(module_path):
    module_path, attr = module_path.rsplit(":", 1)

    module = importlib.import_module(module_path)

    return getattr(module, attr)


def get_auth_coro(module_path):
    if module_path is not None:
        auth_backend = get_backend(module_path)
    else:
        auth_backend = default_backend

    return partial(check_auth, auth_backend)


async def check_auth(backend, channel, path):
    url = urlsplit(path)
    params = ImmutableMultiDict(parse_qsl(url.query))

    _log.debug(
        "Checking auth to channel %s for path: %s, params: %s",
        channel,
        url.path,
        params,
    )

    return backend(channel, url.path, params)
