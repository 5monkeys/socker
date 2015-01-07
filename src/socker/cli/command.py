"""
Start the socker websocket server

Usage:
    socker [-p PORT] [-l INTERFACE]

Options:
  -p            listening port [default: 8765].
  -i            listening interface [default: localhost].
"""
import logging

from docopt import docopt
from .. import __version__, server


class Interface(object):
    def __init__(self):
        self.opts = docopt(__doc__, 'socker v{}'.format(__version__))

        self.setup_logging()

        self.run()

    def run(self):
        server.main(
            interface=self.opts.get('i'),
            port=int(self.opts.get('-p')) or None)

    def setup_logging(self):
        logging.basicConfig(level=logging.DEBUG)
