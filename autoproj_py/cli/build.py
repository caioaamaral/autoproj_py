from autoproj_py.autoproj import Autoproj
import autoproj_py.ops.acquire as importer

def configure(subparser):
    build_parser = subparser.add_parser("build", help="build a package")
    build_parser.add_argument("PACKAGE_NAME", help="the package to build")
    build_parser.set_defaults(func=run)


def run(args):
    print(f"importing {args.PACKAGE_NAME}")
    pkg = Autoproj.registry.get(args.PACKAGE_NAME)

    def import_pkg(pkg):
        if is_imported(pkg.name):
            print(f"{pkg.name} already imported")
            return

        importer.import_package(pkg, Autoproj.root_dir / pkg.name)
    
    import_pkg(pkg)


def is_imported(package_name: str):
    return (Autoproj.root_dir / package_name).exists()

