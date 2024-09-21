import importlib
from pathlib import Path
import sys

from autoproj_py.autobuild.package import Package


class PackageRegistry():
    _registry = dict[str, Package]()
    
    @classmethod
    def __init__(cls, lookup_paths: list[Path], root_dir = None):
        Package.setup(root_dir)

        for path in lookup_paths:
            sys.path.insert(0, path.parent.as_posix())
            for autobuild_path in path.rglob("*.autobuild.py"):
                init_file_path = path / "init.py"
                if init_file_path.exists():
                    init_module = importlib.import_module(f'{path.name}.init')
                with open(autobuild_path, "r") as file:
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
