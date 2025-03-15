import importlib
from pathlib import Path
import sys

from autoproj_py.autobuild.package import Package


class AutobuildRegistry():
    _autobuild_registry = dict[str, Package]()
    _autobuild_collector = []

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
    def has(cls, package_name: str):
        return package_name in cls._autobuild_registry

    @classmethod
    def get(cls, package_name: str):
        return cls._autobuild_registry[package_name]
    
    @classmethod
    def keys(cls):
        return cls._autobuild_registry.keys()

    @classmethod
    def list(cls):
        return list(cls._autobuild_registry.items())
