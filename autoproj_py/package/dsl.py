from autoproj_py.package.registry import PackageRegistry
from autoproj_py.package.definition import PackageDefinition


def package(name: str, source: str):
    pkg = PackageDefinition(name, source)
    PackageRegistry.send(pkg.name, pkg)
