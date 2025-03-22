from autoproj_py.autoproj import Autoproj


def configure(subparser):
    build_parser = subparser.add_parser("build", help="build a package")
    build_parser.add_argument("PACKAGE_NAME", help="the package to build")
    build_parser.set_defaults(func=run)


def run(args):
    pkg = Autoproj.manifest.get_package(args.PACKAGE_NAME)
    pkg.acquire()
    pkg.build(cwd=Autoproj.root_dir, envsh=Autoproj.root_dir / 'env.sh')


def is_imported(package_name: str):
    return (Autoproj.root_dir / package_name).exists()
