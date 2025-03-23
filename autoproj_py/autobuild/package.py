import os
from typing import TYPE_CHECKING

from autoproj_py.autobuild.subprocess import Subprocess
from autoproj_py.vcs_definition import VCSDefinition
from autoproj_py.logger import setup_logger
import autoproj_py.ops.acquire as importer

if TYPE_CHECKING:
    from autoproj_py.osdep import OSDep


class Package:
    root_dir = None
    log_dir = None

    @staticmethod
    def setup(root_dir: str):
        Package.root_dir = root_dir
        Package.log_dir = root_dir / 'log'

    def __init__(self, name: str, url: str):
        self.name = name
        self.logger = setup_logger(name, filename=Package.log_dir / f'{name}.log', level='DEBUG')
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

    def info(self, message: str):
        self.logger.info(message)

    def warn(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)
