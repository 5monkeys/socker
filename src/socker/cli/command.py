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
  --logto FILE    Log output to FILE instead of console
  --version       show version
  -? --help       Show this screen

"""
import logging
import signal
from docopt import docopt

from . import log
from .. import __version__, server

logger = logging.getLogger(__name__)


class Interface(object):

    def __init__(self):
        self.opts = docopt(__doc__, version='socker v{}'.format(__version__))
        self.setup_logging()
        self.register_signals()
        self.start()

    def setup_logging(self):
        filename = self.opts['--logto']
        verbose = self.opts['-v']
        log.configure(filename, verbose)

    def register_signals(self):
        signal.signal(signal.SIGHUP, lambda *args: self.reload())  # 1; Reload
        signal.signal(signal.SIGINT, lambda *args: self.abort())   # 2; Interrupt, ctrl-c
        signal.signal(signal.SIGTERM, lambda *args: self.stop())   # 15; Stop

    def start(self):
        server.main(
            interface=self.opts['-i'],
            port=int(self.opts['-p']))

    def reload(self):
        logger.warn('--- SIGHUP ---')

    def abort(self):
        logger.warn('--- SIGINT ---')
        self.safe_quit()

    def stop(self):
        logger.warn('--- SIGTERM ---')
        self.safe_quit()

    def safe_quit(self):
        # TODO: Implement safer way to exit
        # TODO: Break inner loops with something like "while not quit:" or custom exceptions
        # self._quit = True
        self.quit()

    def quit(self):
        logger.info('Bye!')
        exit()
