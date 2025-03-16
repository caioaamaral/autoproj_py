from pathlib import Path
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

        def reload(self):
            if self.is_remote and self.is_imported:
                self.load_source_yml()
                self.rename_imported()

        def load_source_yml(self):
            source_file = self.import_path / 'source.yml'
            if source_file.exists():
                with open(source_file, 'r') as f:
                    data: dict = yaml.safe_load(f)
                    self._discovered_name = data.get('name')

        def rename_imported(self):
            if self._discovered_name:
                self.import_path.rename(Manifest.base_dir / 'package_sets' / self.name)

        @property
        def name(self):
            if self._explicit_name:
                return self._explicit_name
            
            if self._discovered_name:
                return self._discovered_name

            return Path(self.vcs.url).stem
        
        @property
        def import_path(self) -> Path:
            return Manifest.base_dir / 'package_sets' / self.name

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
    def init(cls, base_dir):
        cls.base_dir = base_dir
        cls.lookup_paths = [base_dir]
        cls.package_sets = cls.parse()

        return cls

    @classmethod
    def parse(cls):
        with open(cls.base_dir / 'manifest') as f:
            manifest = yaml.safe_load(f)

        package_sets: list[Manifest.PackageSet] = []
        if not manifest.get('package_sets'):
            return []

        for vcs in manifest['package_sets']:
            pkg_set = cls.PackageSet(VCSDefinition.from_dict(vcs))
            if pkg_set.is_remote and not pkg_set.is_imported:
                pkg_set.aquire()
                pkg_set.reload()

            cls.lookup_paths.append(cls.base_dir / 'package_sets' / pkg_set.name)
            package_sets.append(pkg_set)

        return package_sets
    
