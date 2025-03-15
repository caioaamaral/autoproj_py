from autoproj_py.autoproj import Autoproj


def configure(subparser):
    build_parser = subparser.add_parser('list', help='list all packages')
    build_parser.set_defaults(func=run)


def run(args):
    packages = Autoproj.registry.list()
    for package in packages:
        print(f'- {package}')
