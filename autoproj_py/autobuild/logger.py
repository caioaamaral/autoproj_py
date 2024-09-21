import logging

import autoproj_py.logger as logger


def log(message, level, setup=None):
    logger.log(message, level, setup)


def setup(name: str, level: "logging._Level"):
    logger = logging.getLogger(name)
    fh = logging.FileHandler(name)
    fh.setLevel(level)
    logger.addHandler(fh)

    return logger

