import importlib
from pathlib import Path
import sys

from autoproj_py.autobuild.package import Package


class PackageRegistry():
    _registry = dict[str, Package]()
    
    @classmethod
    def __init__(cls, lookup_paths: list[Path], root_dir = None):
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

            sys.path.pop()

        return cls
            
    @classmethod
    def send(cls, package_name: str, package: Package):
        cls._registry[package_name] = package
    
    @classmethod
    def get(cls, package_name: str):
        return cls._registry[package_name]
    
    @classmethod
    def keys(cls):
        return cls._registry.keys()

    @classmethod
    def list(cls):
        return list(cls._registry.keys())
