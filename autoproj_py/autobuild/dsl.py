from autoproj_py.autobuild.registry import PackageRegistry
from autoproj_py.autobuild.package import Package
from autoproj_py.autobuild.packages.cmake import CMake


def package(name: str, source: str):
    pkg = Package(name, source)
    PackageRegistry.send(pkg.name, pkg)

def cmake_package(name: str, source: str):
    pkg = CMake(name, source)
    pkg.dependencies = ["cmake"]
    PackageRegistry.send(pkg.name, pkg)
