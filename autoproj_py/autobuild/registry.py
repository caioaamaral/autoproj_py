import importlib
from pathlib import Path
import sys

from autoproj_py.autobuild.package import Package


class PackageRegistry():
    _autobuild_registry = dict[str, Package]()
    _autobuild_collector = []
    
    @classmethod
    def init(cls, lookup_paths: list[Path], root_dir = None):
        Package.setup(root_dir)

        init_files = []
        autobuild_files = []
        for path in lookup_paths:
            init_files.append((path / "init.py", path.parent.as_posix()))
            autobuild_files.append((path.rglob("*.autobuild.py"), path.parent.as_posix()))

        for init, sys_path in init_files:
            sys.path.insert(0, sys_path)
            if init.exists():
                importlib.import_module(f'{path.name}.init')

            sys.path.pop()
        
        for autobuilds, sys_path in autobuild_files:
            sys.path.insert(0, sys_path)
            for autobuild in autobuilds:
                with open(autobuild, "r") as file:
                    exec(file.read(), {})
                cls.send(autobuild)

            sys.path.pop()

        return cls
    
    @classmethod
    def autobuild(cls):
        for autobuild in cls._autobuild_collector:
            print(f'- {autobuild}')

    @classmethod
    def collect(cls, package_name: str, package: Package):
        cls._autobuild_collector.append((package_name, package))

    @classmethod
    def send(cls, autobuild):
        for package_name, package in cls._autobuild_collector:
            package.declared_at = autobuild
            cls._autobuild_registry[package_name] = package

        cls._autobuild_collector = []

    @classmethod
    def get(cls, package_name: str):
        return cls._autobuild_registry[package_name]
    
    @classmethod
    def keys(cls):
        return cls._autobuild_registry.keys()

    @classmethod
    def list(cls):
        return list(cls._autobuild_registry.items())
