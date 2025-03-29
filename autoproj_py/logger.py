import logging
import os
import sys
from typing import Callable, Optional


def setup_logger(
    name: str,
    level: "logging._Level",
    filename: str|None = None,
    stream_stdout: bool = True
) -> logging.Logger:
    if filename:
        os.makedirs(os.path.dirname(filename), exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter(
        fmt=f'[%(asctime)s] [{name}] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M'
    )

    if stream_stdout:
        console_handler = logging.StreamHandler(stream=sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if filename:
        file_handler = logging.FileHandler(filename, mode='w')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


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
