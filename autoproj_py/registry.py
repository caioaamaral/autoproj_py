import sys
import runpy

from autoproj_py.autobuild.package import Package
from autoproj_py.autobuild.registry import AutobuildRegistry
from autoproj_py.osdep import OSDepRegistry, OSDep
from autoproj_py.package_set import PackageSetCollection
import autoproj_py.autobuild.dsl as dsl


class Registry():
    chain = dict()

    @classmethod
    def init(cls, pkg_sets: PackageSetCollection, root_dir = None, context: dict = {}):
        Package.setup(root_dir)

        package_sets = pkg_sets.collection
        cls.package_sets = package_sets

        init_files = []
        osdep_files = []
        autobuild_files = []
        for package_set in cls.package_sets:
            pkg_sets.current = package_set
            if package_set.is_main:
                path = package_set.import_path
            else:
                path = package_set.hidden_path
            init_files = (path / 'init.py', path.parent.as_posix())
            osdep_files = [
                p
                for p in path.rglob("*.osdep")

                # skip the file only if this is the "main" package_set AND path has "package_sets"
                if not (package_set.is_main and "package_sets" in p.parts)
            ]
            autobuild_files = ([
                p
                for p in path.rglob("*.autobuild")

                # skip the file only if this is the "main" package_set AND path has "package_sets"
                if not (package_set.is_main and "package_sets" in p.parts)
            ], path.parent.as_posix())

            init, sys_path = init_files
            sys.path.insert(0, sys_path)
            if init.exists():
                runpy.run_module(f'{path.name}.init', run_name='__main__', init_globals=context)

            sys.path.pop()

            for osdep in osdep_files:
                package_set.osdeps.send(osdep)

            autobuilds, sys_path = autobuild_files

            # make visible dsl functions
            exec_context = dict(vars(dsl))
            sys.path.insert(0, sys_path)
            for autobuild in autobuilds:
                with open(autobuild, 'r') as file:
                    try:
                        exec(file.read(), exec_context, exec_context)
                    except Exception as e:
                        print(f'Got exception while processing {autobuild}: {e}')
                        exit(-1)
                package_set.vcs_packages.send(package_set.import_path / autobuild.name)

            sys.path.pop()

        # find all selected packages
        selected_packages = set()
        for package_set in cls.package_sets:
            for package_name in package_set.vcs_packages._selected_packages:
                selected_packages.add(package_name)

        # hydrate dependencies and fill cls.chain
        for package_name in selected_packages:
            package = cls._find_first(package_name)
            package.hydrate_dependencies()
            for dependency_name in package.dependencies:
                if dependency_name not in cls.chain:
                    cls.chain[dependency_name] = [package_name]
                else:
                    cls.chain[dependency_name].append(package_name)

        # setup reverse dependencies
        for package_name, dependencies in cls.chain.items():
            package = cls._find_first(package_name)
            if not package:
                continue

            package.reverse_dependencies = dependencies

        return cls

    @classmethod
    def get(cls, package_name: str):
        return cls._find_first(package_name)

    @classmethod
    def _find_first(cls, package_name: str) -> OSDep|Package:
        return next(cls._find(package_name), None)

    @classmethod
    def _find_all(cls, package_name: str) -> list[OSDep|Package]:
        return list(cls._find(package_name))

    @classmethod
    def _find(cls, package_name: str):
        # attempt to find an osdep first
        for package_set in cls.package_sets:
            if package_set.osdeps.has(package_name):
                osdep = package_set.osdeps.get(package_name)
                yield osdep

        # fallback to a vcs package
        for package_set in cls.package_sets:
            if package_set.vcs_packages.has(package_name):
                pkg = package_set.vcs_packages.get(package_name)
                yield pkg

        return None

    @classmethod
    def show(cls, package_name: str):
        matches = cls._find_all(package_name)
        if not matches:
            return

        package = matches.pop(0)

        if package:
            declarations = [
                f'{str(pkg.declared_at)}'
                for pkg in matches
            ]
            package.matches = declarations
            print(package.details())

    @classmethod
    def keys(cls):
        return dict(
            {package_set.name: {'osdeps': list(package_set.osdeps.keys()), 'vcs': list(package_set.vcs_packages.keys())} for package_set in cls.package_sets}
        )

    @classmethod
    def list(cls):
        return list(OSDepRegistry.list()) + list(AutobuildRegistry.list())
