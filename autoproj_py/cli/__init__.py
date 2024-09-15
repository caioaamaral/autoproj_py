import argparse
from . import bootstrap
from . import build

def main():
    parser = argparse.ArgumentParser(prog="autoproj", description="Autoproj command line tool")
    
    subparser = parser.add_subparsers(title="Commands", dest="command")
    bootstrap.configure(subparser)
    build.configure(subparser)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
