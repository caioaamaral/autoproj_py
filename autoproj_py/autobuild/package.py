import logging
import os
from typing import TYPE_CHECKING

from autoproj_py.autobuild.subprocess import Subprocess
from autoproj_py.vcs_definition import VCSDefinition
import autoproj_py.autobuild.logger as logger
import autoproj_py.ops.acquire as importer

if TYPE_CHECKING:
    from autoproj_py.osdep import OSDep


def __setup(name: str, level: "logging._Level"):
    return logger.setup(name, level)


def __setup_build(level: "logging._Level"):
    return __setup("build.log", level)


def __setup_import(level: "logging._Level"):
    return __setup("import.log", level)


def __setup_update(level: "logging._Level"):
    return __setup('update.log', level)


_SETUPS = {
    'build': __setup_build,
    'import': __setup_import,
    'update': __setup_update,
}


class Package:
    root_dir = None

    @staticmethod
    def setup(root_dir: str):
        Package.root_dir = root_dir

    def __init__(self, name: str, url: str):
        self.name = name
        self.source = VCSDefinition.from_url(url)
        self.import_dir = self.root_dir / self.name
        self.source_dir = self.import_dir
        self.dependencies = []
        self.reverse_dependencies = []
        self.declared_at = None
        self.matches = []

    def details(self):
        bold = "\033[1m"
        reset = "\033[0m"

        return (
            f"{bold}VS Package:{reset} {self.name}\n"
            f"  {bold}first match:{reset}\n"
            f"      {self.declared_at}\n"
            f"  {bold}source definition:{reset}\n"
            f"      type: {self.source.type}\n"
            f"      url: {self.source.url}\n"
            f"      options: {self.source.options}\n"
            f"  {bold}depends on:{reset}\n"
            f"      {self.dependencies}\n"
            f"  {bold}reverse dependencies:{reset}\n"
            f"      {self.reverse_dependencies}\n"
            f"  {bold}others matches:{reset}\n"
            + "".join([f"      - {match}\n" for match in self.matches])
        )

    @property
    def is_aquired(self):
        return self.import_dir.exists()

    def update(self, registry):
        for dependency_name in self.dependencies:
            dependency = registry.get(dependency_name)
            if not dependency:
                self.error(f'missing dependency {dependency_name}', 'update')
                exit(-1)

            if isinstance(dependency, Package):
                dependency.acquire()
            elif isinstance(dependency, OSDep):
                dependency.install()

    def acquire(self, registry):
        self.info(f'importing {self.name}', 'import')
        if self.is_aquired:
            self.info(f'{self.name} already imported', 'import')
            return

        self.update(registry)

        importer.import_package(self.source.url, self.import_dir)

    def build(self, registry, env=None, cwd=None, envsh=None):
        os.makedirs(self.build_dir, exist_ok=True)
        os.makedirs(self.install_dir, exist_ok=True)
        for dependency_name in self.dependencies:
            dependency = registry.get(dependency_name)
            if not dependency:
                self.error(f'missing dependency {dependency_name}', 'build')
                exit(-1)

            if isinstance(dependency, Package):
                dependency.build(registry, env=env, cwd=cwd, envsh=envsh)

    def hydrate_dependencies(self):
        pass

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
