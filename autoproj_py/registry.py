import importlib
from pathlib import Path
import sys

from autoproj_py.autobuild.package import Package
from autoproj_py.autobuild.registry import AutobuildRegistry
from autoproj_py.osdep import APT_OSDep, OSDepRegistry


class Registry():
    
    @classmethod
    def init(cls, lookup_paths: list[Path], root_dir = None):
        Package.setup(root_dir)

        init_files = []
        osdep_files = []
        autobuild_files = []
        for path in lookup_paths:
            init_files.append((path / "init.py", path.parent.as_posix()))
            osdep_files.append(path.rglob("*.osdep"))
            autobuild_files.append((path.rglob("*.autobuild"), path.parent.as_posix()))

        for init, sys_path in init_files:
            sys.path.insert(0, sys_path)
            if init.exists():
                importlib.import_module(f'{path.name}.init')

            sys.path.pop()
        
        for osdeps in osdep_files:
            for osdep in osdeps:
                OSDepRegistry.send(osdep)
        
        for autobuilds, sys_path in autobuild_files:
            sys.path.insert(0, sys_path)
            for autobuild in autobuilds:
                with open(autobuild, "r") as file:
                    exec(file.read(), {})
                AutobuildRegistry.send(autobuild)

            sys.path.pop()

        return cls

    @classmethod
    def get(cls, package_name: str):
        if OSDepRegistry.has(package_name):
            return OSDepRegistry.get(package_name)

        if AutobuildRegistry.has(package_name):
            return AutobuildRegistry.get(package_name)

    @classmethod
    def show(cls, package_name: str):
        package = cls.get(package_name)
        if package:
            print(package.details())

    @classmethod
    def keys(cls):
        return dict(
            osdep=OSDepRegistry.keys(),
            autobuild=AutobuildRegistry.keys()
        )

    @classmethod
    def list(cls):
        return list(OSDepRegistry.list()) + list(AutobuildRegistry.list())
