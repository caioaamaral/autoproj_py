import logging
import os
import sys
from typing import Callable, Optional


def setup_logger(name: str, filename: str, level: "logging._Level") -> logging.Logger:
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    _logger = logging.getLogger(name)
    _logger.setLevel(level)

    formatter = logging.Formatter(
        fmt=f'[%(asctime)s] [{name}] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M'
    )

    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    _logger.addHandler(console_handler)

    file_handler = logging.FileHandler(filename, mode='w')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    _logger.addHandler(file_handler)

    return _logger


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
