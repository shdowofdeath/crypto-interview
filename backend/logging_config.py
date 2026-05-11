"""Developer-friendly logging for the interview backend.

Configures a single root logger with a coloured, single-line format that
prints to stdout. Mounted in main.py at startup so that every request,
every upstream call, and every exception is visible in the uvicorn terminal.
"""

import logging
import sys


_GREY = "\x1b[38;20m"
_YELLOW = "\x1b[33;20m"
_RED = "\x1b[31;20m"
_BOLD_RED = "\x1b[31;1m"
_CYAN = "\x1b[36;20m"
_RESET = "\x1b[0m"


class _ColourFormatter(logging.Formatter):
    LEVEL_COLOURS = {
        logging.DEBUG: _GREY,
        logging.INFO: _CYAN,
        logging.WARNING: _YELLOW,
        logging.ERROR: _RED,
        logging.CRITICAL: _BOLD_RED,
    }

    def format(self, record: logging.LogRecord) -> str:
        colour = self.LEVEL_COLOURS.get(record.levelno, _GREY)
        record.levelname = f"{colour}{record.levelname:<7}{_RESET}"
        record.name = f"{_GREY}{record.name}{_RESET}"
        base = "%(asctime)s %(levelname)s %(name)s :: %(message)s"
        return logging.Formatter(base, "%H:%M:%S").format(record)


def configure_logging(level: int = logging.INFO) -> None:
    root = logging.getLogger()
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_ColourFormatter())
    root.addHandler(handler)
    root.setLevel(level)

    for noisy in ("httpx", "httpcore", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
