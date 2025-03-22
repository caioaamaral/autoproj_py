import importlib
from pathlib import Path
import sys

from autoproj_py.autobuild.package import Package


class AutobuildCollector:
    _packages = []

    @classmethod
    def collect(cls, package_name: str, package: Package):
        cls._packages.append((package_name, package))

    @classmethod
    def flush(cls):
        packages = cls._packages
        cls._packages = []
        return packages


class AutobuildRegistry:

    def __init__(self, name: str):
        self.name = name
        self._registry = dict[str, Package]()
        self._selected_packages = []

    def send(self, autobuild_file):
        for package_name, package in AutobuildCollector.flush():
            package.declared_at = f'{self.name}: {autobuild_file}'
            self._registry[package_name] = package
            if package.is_aquired:
                self._selected_packages.append(package_name)

    def has(self, package_name: str):
        return package_name in self._registry

    def get(self, package_name: str):
        return self._registry[package_name]

    def keys(self):
        return self._registry.keys()

    def list(self):
        return list(self._registry.items())

    def __repr__(self):
        items = [
            ': '.join([name, str(pkg.declared_at)])
            for name, pkg in self._registry.items()
        ]
        return f"{self.name}: {[': '.join([name, str(pkg.declared_at)]) for name, pkg in self._registry.items()]}"
