from pathlib import Path

from autoproj_py.autobuild.package import Package


class PackageRegistry():
    _registry = dict[str, Package]()
    
    @classmethod
    def __init__(cls, lookup_paths: list[Path], root_dir = None):
        Package.setup(root_dir)

        for path in lookup_paths:
            for autobuild_path in path.rglob("*.autobuild.py"):
                with open(autobuild_path, "r") as file:
                    exec(file.read(), {})
        
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
