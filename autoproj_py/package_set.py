from dataclasses import dataclass, field
import os
from pathlib import Path
import subprocess

from autoproj_py.autobuild.registry import AutobuildRegistry
from autoproj_py.ops.acquire import git_import
from autoproj_py.python_env import PythonEnv
from autoproj_py.osdep import OSDepRegistry
from autoproj_py.vcs_definition import VCSDefinition
from autoproj_py.subprocess import Subprocess


class PackageSet:

    base_dir = None

    def __init__(self, vcs: VCSDefinition, name: str|None = None):
        self.is_main = False
        self._explicit_name = name
        self._discovered_name = None
        self.vcs = vcs
        self.source = None
        self.vcs_packages = None
        self.osdeps = None
        self.vcs_packages = AutobuildRegistry(self.name)
        self.osdeps = OSDepRegistry(self.name)
        self._env = None

        self._import_name = self.name

    @property
    def name(self):
        if self._explicit_name:
            return self._explicit_name

        return self.vcs.url.split('/')[-1].removesuffix('.git').removesuffix('-package_set')

    @property
    def import_path(self) -> Path:
        return self.base_dir / 'package_sets' / self._import_name

    @property
    def hidden_path(self) -> Path:
        return self.base_dir / 'package_sets' / '.hidden' / self._import_name.replace('.', '_')

    @property
    def is_name_changed(self):
        return self._import_name != self.name

    @property
    def is_remote(self):
        return not self.is_local

    @property
    def is_local(self):
        return self.vcs.type == 'local'

    @property
    def is_imported(self):
        return self.import_path.exists()

    @property
    def env(self) -> PythonEnv:
        if self._env is None:
            if self.is_main:
                env_path = self.base_dir / '.venv'
            else:
                env_path = self.import_path / '.venv'
            self._env = PythonEnv(env_path)
        return self._env

    def aquire(self):
        if self.is_remote and not self.is_imported:
            git_import(self.vcs.url, self.import_path)

    def install(self):
        """Install the package set and set up its virtualenv."""
        # Skip if virtualenv already exists
        if self.env.path.exists():
            return

        # Create the virtualenv
        self.env.create()

        # If there's a requirements.txt in the package set, install it
        requirements = self.import_path / 'requirements.txt'
        if requirements.exists():
            cmd = [
                str(self.env.python),
                '-m',
                'pip',
                'install',
                '-r',
                str(requirements)
            ]
            subprocess.run(cmd, check=True)

    def _hide_itself(self):
        if Path(self.hidden_path).exists():
            return

        os.symlink(self.base_dir / 'package_sets' / self.name.replace('_', '.'), self.hidden_path)


class MainPackageSet(PackageSet):
    def __init__(self):
        super().__init__(VCSDefinition('local', 'file://' + str(self.base_dir)), name='main')
        self.is_main = True
        self.vcs_packages = AutobuildRegistry('main')
        self.osdeps = OSDepRegistry('main')

    @property
    def is_remote(self):
        return False

    @property
    def is_imported(self):
        return True

    @property
    def is_local(self):
        return True

    @property
    def name(self):
        return 'main'

    @property
    def import_path(self):
        return self.base_dir


@dataclass
class PackageSetCollection:

    current: PackageSet | None = None
    collection: list[PackageSet] = field(default_factory=list)
