from autoproj_py.registry import Registry
from autoproj_py.vcs_definition import VCSDefinition
from autoproj_py.package_set import MainPackageSet, PackageSet, PackageSetCollection

import yaml


class Manifest:

    base_dir = None
    package_sets_collection = PackageSetCollection()

    @classmethod
    def init(cls, root_dir, autoproj):
        cls.base_dir = root_dir / 'autoproj'
        PackageSet.base_dir = cls.base_dir
        autoproj.manifest = cls

        cls.package_sets_collection.collection = cls._load_package_sets_config()

        cls.registry = Registry.init(pkg_sets=cls.package_sets_collection, root_dir=root_dir, context={'Autoproj': autoproj})

        return cls

    @classmethod
    def _load_package_sets_config(cls):
        with open(cls.base_dir / 'manifest') as f:
            manifest = yaml.safe_load(f)

        package_sets: list[PackageSet] = [MainPackageSet()]

        if not manifest.get('package_sets'):
            return package_sets

        for vcs in manifest['package_sets']:
            pkg_set = PackageSet(VCSDefinition.from_dict(vcs))

            if pkg_set.is_remote and not pkg_set.is_imported:
                pkg_set.aquire()

            if not pkg_set.is_main:
                pkg_set._hide_itself()

            package_sets.append(pkg_set)

        return package_sets

    @classmethod
    def show_package(cls, name: str):
        cls.registry.show(name)

    @classmethod
    def get_package(cls, name: str):
        return cls.registry.get(name)

    @classmethod
    def get_package_set(cls, name: str):
        for pkg_set in cls.package_sets_collection:
            if pkg_set.name == name:
                return pkg_set

        raise ValueError(f"'{name}' not in package_sets. Valids are: {cls.each_package_set(lambda p: p.name)}")

    @classmethod
    def current_package_set(cls):
        return cls.package_sets_collection.current

    @classmethod
    def each_package_set(cls, fn):
        return list(map(fn, cls.package_sets_collection))

    @classmethod
    def keys(cls):
        return cls.registry.keys()
