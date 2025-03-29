import logging
import os
import sys

import autoproj_py.logger as logger


def setup_logger(name: str, filename: str, level: "logging._Level") -> logging.Logger:
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter(
        fmt=f'[%(asctime)s] [{name}] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M'
    )

    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(filename, mode='w')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def log(message, level, setup=None):
    logger.log(message, level, setup)


def setup(name: str, level: "logging._Level"):
    logger = logging.getLogger(name)
    fh = logging.FileHandler(name)
    fh.setLevel(level)
    logger.addHandler(fh)

    return logger

