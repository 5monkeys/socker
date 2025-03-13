"""
Start the socker websocket server

Usage:
  socker [options]
  socker -? | --help
  socker --version

Options:
  -i INTERFACE    Listening interface [default: localhost]
  -p PORT         Listening port [default: 8765]

  -v              Enable verbose output

  --auth-backend=PATH           Auth backend path
                                [default: socker.auth:default_backend]

  --redis-host=HOST             Redis host [default: localhost]
  --redis-port=PORT             Redis port [default: 6379]
  --redis-db=DB                 Redis database [default: 0]
  --redis-password=PASSWORD     Redis password

  --logto FILE    Log output to FILE instead of console

  --version       show version
  -? --help       Show this screen

"""

import asyncio
import logging
import signal

import pkg_resources
from docopt import docopt

from . import log
from .. import server

version = pkg_resources.require("socker")[0].version
logger = logging.getLogger(__name__)


class Interface(object):

    def __init__(self):
        self.opts = docopt(__doc__, version="socker v{}".format(version))
        self.setup_logging()
        self.register_signals()
        self.start()

    def setup_logging(self):
        filename = self.opts["--logto"]
        verbose = self.opts["-v"]
        log.configure(filename, verbose)

    def register_signals(self):
        # 1; Reload
        signal.signal(signal.SIGHUP, lambda *args: self.reload())
        # 2; Interrupt, ctrl-c
        signal.signal(signal.SIGINT, lambda *args: self.abort())
        # 15; Stop
        signal.signal(signal.SIGTERM, lambda *args: self.stop())

    def start(self):
        redis_opts = {
            k.replace("--", "").replace("-", "_"): v
            for k, v in self.opts.items()
            if "--redis-" in k
        }

        for key in ["redis_port", "redis_db"]:  # Integer arguments
            redis_opts[key] = int(redis_opts[key])

        asyncio.run(
            server.main(
                interface=self.opts["-i"],
                port=int(self.opts["-p"]),
                debug=self.opts["-v"],
                auth_backend=self.opts["--auth-backend"],
                **redis_opts
            )
        )

    def reload(self):
        logger.warn("--- SIGHUP ---")
        pass  # TODO: Implement

    def abort(self):
        logger.warn("--- SIGINT ---")
        self.safe_quit()

    def stop(self):
        logger.warn("--- SIGTERM ---")
        # Cold exit.
        self.quit()

    def safe_quit(self):
        # TODO: Implement safer way to exit
        logger.info("Closing event loop...")
        asyncio.get_event_loop().stop()

    @staticmethod
    def quit(exit_code=0):
        logger.debug(
            "Pending tasks at exit: %s",
            asyncio.Task.all_tasks(asyncio.get_event_loop()),
        )
        logger.info("Bye!")
        exit(exit_code)
