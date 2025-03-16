from pathlib import Path

from autoproj_py.autobuild.registry import AutobuildRegistry
from autoproj_py.ops.acquire import git_import
from autoproj_py.osdep import OSDepRegistry
from autoproj_py.vcs_definition import VCSDefinition

import yaml


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

        self._import_name = self.name

    def configure(self):
        self.load_source_yml()
        self.vcs_packages = AutobuildRegistry(self.name)
        self.osdeps = OSDepRegistry(self.name)
        if self.is_remote and self.is_imported  and self.is_name_changed:
            self.rename_imported()


    def load_source_yml(self):
        source_file = self.import_path / 'source.yaml'
        if source_file.exists():
            self.source = source_file
            with open(source_file, 'r') as f:
                data: dict = yaml.safe_load(f)
                self._discovered_name = data.get('name')

    def rename_imported(self):
        if self._discovered_name:
            self.import_path.rename(self.base_dir / 'package_sets' / self.name)
            self._import_name = self.name

    @property
    def name(self):
        if self._explicit_name:
            return self._explicit_name

        if self._discovered_name:
            return self._discovered_name

        return Path(self.vcs.url).stem

    @property
    def import_path(self) -> Path:
        return self.base_dir / 'package_sets' / self._import_name

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

    def aquire(self):
        if self.is_remote and not self.is_imported:
            git_import(self.vcs.url, self.import_path)


class MainPackageSet(PackageSet):
    def __init__(self):
        super().__init__(VCSDefinition('local', 'file://' + str(self.base_dir)), name='main')
        self.is_main = True
        self.vcs_packages = AutobuildRegistry('main')
        self.osdeps = OSDepRegistry('main')

    def configure(self):
        pass

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
