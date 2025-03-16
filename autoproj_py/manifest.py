from pathlib import Path
from autoproj_py.registry import Registry
from autoproj_py.vcs_definition import VCSDefinition
from autoproj_py.ops.acquire import git_import

import yaml


class Manifest:

    base_dir = None
    package_sets = []
    lookup_paths = []


    class PackageSet:
        def __init__(self, vcs: VCSDefinition, name: str|None = None):
            self._explicit_name = name
            self._discovered_name = None
            self.vcs = vcs
            self.source = None

            self._import_name = self.name

        def hydrate(self):
            self.load_source_yml()
            if self.is_name_changed:
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
                self.import_path.rename(Manifest.base_dir / 'package_sets' / self.name)
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
            return Manifest.base_dir / 'package_sets' / self._import_name

        @property
        def is_name_changed(self):
            return self._import_name != self.name

        @property
        def is_remote(self):
            return self.vcs.type != 'local'

        @property
        def is_imported(self):
            return self.import_path.exists()

        def aquire(self):
            if self.is_remote and not self.is_imported:
                git_import(self.vcs.url, self.import_path)


    @classmethod
    def init(cls, root_dir):
        cls.base_dir = root_dir / 'autoproj'
        cls.lookup_paths = [cls.base_dir]
        cls.package_sets = cls.hydrate()

        cls.registry = Registry.init(lookup_paths=cls.lookup_paths, root_dir=root_dir)

        return cls

    @classmethod
    def hydrate(cls):
        with open(cls.base_dir / 'manifest') as f:
            manifest = yaml.safe_load(f)

        package_sets: list[Manifest.PackageSet] = []
        if not manifest.get('package_sets'):
            return []

        for vcs in manifest['package_sets']:
            pkg_set = cls.PackageSet(VCSDefinition.from_dict(vcs))

            if pkg_set.is_remote and not pkg_set.is_imported:
                pkg_set.aquire()

            pkg_set.hydrate()

            cls.lookup_paths.append(cls.base_dir / 'package_sets' / pkg_set.name)
            package_sets.append(pkg_set)

        return package_sets

    @classmethod
    def show(cls, package_name: str):
        cls.registry.show(package_name)

    @classmethod
    def get(cls, package_name: str):
        return cls.registry.get(package_name)
