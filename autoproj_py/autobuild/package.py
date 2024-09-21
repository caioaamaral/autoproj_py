import logging
import os

import autoproj_py.autobuild.logger as logger
import autoproj_py.ops.acquire as importer
from autoproj_py.autobuild.subprocess import Subprocess


def __setup(name: str, level: "logging._Level"):
    return logger.setup(name, level)


def __setup_build(level: "logging._Level"):
    return __setup("build.log", level)


def __setup_import(level: "logging._Level"):
    return __setup("import.log", level)


_SETUPS = {
    "build": __setup_build,
    "import": __setup_import
}

class Package:
    root_dir = None

    @staticmethod
    def setup(root_dir: str):
        Package.root_dir = root_dir

    def __init__(self, name: str, source: str):
        self.name = name
        self.source = source
        self.import_dir = self.root_dir / self.name
        self.source_dir = self.import_dir
        self.dependencies = []

    def is_aquired(self):
        return self.import_dir.exists()
    
    def acquire(self):
        self.info(f"importing {self.name}", "import")
        if self.is_aquired():
            self.info(f"{self.name} already imported", "import")
            return

        importer.import_package(self.source, self.import_dir)
    
    def run(self, cmd: list[str], cwd: str, env: dict = os.environ):
        Subprocess.run(cmd, cwd=cwd, env=env)

    def log(self, message: str, level: "logging._Level", step:str):
        logger.log(message, level, _SETUPS[step])

    def info(self, message: str, step:str):
        self.log(message, logging.INFO, step)

    def warn(self, message: str, step:str):
        self.log(message, logging.WARNING, step)
    
    def error(self, message: str, step:str):
        self.log(message, logging.ERROR, step)
