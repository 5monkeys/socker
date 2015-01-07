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
from docopt import docopt

from . import log
from .. import __version__, server

logger = logging.getLogger(__name__)


class Interface(object):
    def __init__(self):
        self.opts = docopt(__doc__, version='socker v{}'.format(__version__))

        self.setup_logging()

        try:
            self.run()
        except KeyboardInterrupt:
            self.quit()

    def run(self):
        server.main(
            interface=self.opts['-i'],
            port=int(self.opts['-p']))

    def setup_logging(self):
        filename = self.opts['--logto']
        verbose = self.opts['-v']
        log.configure(filename, verbose)

    def quit(self):
        logger.info('Bye!')
        exit()
