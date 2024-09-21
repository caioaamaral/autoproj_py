import logging
from typing import Callable, Optional


def log(message: str, level: "logging._Level", setup:Optional[Callable[[str, "logging._Level"], logging.Logger]]=None):
    print(message)
    if setup:
        logger: logging.Logger = setup(level)
        logger.log(level, message)
    else:
        print(message)


def info(message: str, setup=None):
    log(message, logging.INFO, setup)


def warn(message: str, setup=None):
    log(message, logging.WARNING, setup)


def error(message: str, setup=None):
    log(message, logging.ERROR, setup)
