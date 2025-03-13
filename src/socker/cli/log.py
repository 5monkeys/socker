import logging
import logging.config
from . import colors


class ColorizedFormatter(logging.Formatter):

    color = {
        logging.INFO: colors.green,
        logging.DEBUG: colors.blue,
        logging.WARN: colors.yellow,
        logging.ERROR: colors.red,
        logging.CRITICAL: colors.magenta,
    }

    def format(self, record):
        level = record.levelno
        if isinstance(record.msg, str) and level in self.color:
            record.msg = self.color.get(level)(record.msg)
        return super(ColorizedFormatter, self).format(record)


def configure(filename, verbose):
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s [%(process)d] %(name) 20s"
                    " %(levelname) 8s >> %(message)s"
                },
                "colorized": {
                    "()": "socker.cli.log.ColorizedFormatter",
                    "fmt": "%(asctime)s [%(process)d] %(name) 20s"
                    " %(levelname) 8s >> %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "colorized",
                    "stream": "ext://sys.stdout",
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "default",
                    "filename": filename or "/tmp/socker.log",
                    "maxBytes": 10485760,
                    "backupCount": 20,
                    "encoding": "utf8",
                },
            },
            "root": {
                "level": "DEBUG" if verbose else "INFO",
                "handlers": ["file" if filename else "console"],
            },
        }
    )
