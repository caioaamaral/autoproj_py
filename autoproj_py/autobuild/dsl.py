import sys

from autoproj_py.autobuild.packages.cmake import CMake
from autoproj_py.autobuild.packages.package import Package
from autoproj_py.autobuild.registry import AutobuildCollector
from autoproj_py.vcs_definition import VCSDefinition


def extension(func):
    setattr(sys.modules[__name__], func.__name__, func)
    return func


def common_package(cls: type[Package], name: str, source: str|dict):
    if isinstance(source, dict):
        vcs = VCSDefinition.from_dict(source)
    elif isinstance(source, str):
        vcs = VCSDefinition.from_url(source)
    else:
        raise ValueError(f'Invalid source type: {type(source)}')

    pkg = cls(name, vcs.url)
    AutobuildCollector.collect(pkg.name, pkg)
    return pkg


def import_package(name: str, source: str):
    return common_package(Package, name, source)


def cmake_package(name: str, source: str):
    pkg = common_package(CMake, name, source)
    pkg.dependencies = ['cmake']
    return pkg
