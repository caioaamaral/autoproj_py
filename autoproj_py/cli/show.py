from autoproj_py.autoproj import Autoproj


def configure(subparser):
    build_parser = subparser.add_parser('show', help='show package information')
    build_parser.add_argument('PACKAGE_NAME', help='the package to show')
    build_parser.set_defaults(func=run)


def run(args):
    if (pkg := Autoproj.registry.get(args.PACKAGE_NAME)):
        print(pkg.details())
    else:
        print(f'package {args.PACKAGE_NAME} not found')
