from autoproj_py.registry import Registry
from autoproj_py.vcs_definition import VCSDefinition
from autoproj_py.package_set import PackageSet, MainPackageSet

import yaml


class Manifest:

    base_dir = None
    package_sets = []

    @classmethod
    def init(cls, root_dir):
        cls.base_dir = root_dir / 'autoproj'
        PackageSet.base_dir = cls.base_dir

        cls.package_sets = cls.load_package_sets()

        cls.registry = Registry.init(package_sets=cls.package_sets, root_dir=root_dir)

        return cls

    @classmethod
    def load_package_sets(cls):
        with open(cls.base_dir / 'manifest') as f:
            manifest = yaml.safe_load(f)

        package_sets: list[PackageSet] = [MainPackageSet()]

        if not manifest.get('package_sets'):
            return []

        for vcs in manifest['package_sets']:
            pkg_set = PackageSet(VCSDefinition.from_dict(vcs))

            if pkg_set.is_remote and not pkg_set.is_imported:
                pkg_set.aquire()

            pkg_set.configure()

            package_sets.append(pkg_set)

        return package_sets

    @classmethod
    def show(cls, package_name: str):
        cls.registry.show(package_name)

    @classmethod
    def get(cls, package_name: str):
        return cls.registry.get(package_name)

    @classmethod
    def keys(cls):
        return cls.registry.keys()
