import sys

from autoproj_py.autobuild.registry import AutobuildRegistry
from autoproj_py.autobuild.package import Package
from autoproj_py.autobuild.packages.cmake import CMake


def extension(func):
    setattr(sys.modules[__name__], func.__name__, func)
    return func


def import_package(name: str, source: str):
    pkg = Package(name, source)
    AutobuildRegistry.collect(pkg.name, pkg)

def cmake_package(name: str, source: str):
    pkg = CMake(name, source)
    pkg.dependencies = ["cmake"]
    AutobuildRegistry.collect(pkg.name, pkg)
