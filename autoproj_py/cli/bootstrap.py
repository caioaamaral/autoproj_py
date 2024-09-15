from pathlib import Path
import os


def configure(subparser):
    bootstrap_parser = subparser.add_parser("bootstrap", help="bootstrap a new project")
    bootstrap_parser.add_argument("ROOT_DIR", help="bootstrap in a directory")
    bootstrap_parser.add_argument("--git", type=str, help="bootstrap from a git repository")
    bootstrap_parser.set_defaults(func=run)


def bootstrap_from_git(git_url, root_dir):
    print(f"bootstrapping from {git_url} to {root_dir}")


def run(args):
    if args.path:
        root_dir = Path(args.path).resolve()
        if not root_dir.is_dir():
            print(f"{root_dir} is not a directory or does not exist")
            return

        if any(root_dir.iterdir()):
            print(f"bootstrap directory must be empty")
            return
        
        print("bootstraping a new project at", root_dir)
        
        if not args.git:
            os.makedirs(root_dir / "autoproj")

            with open(root_dir / "autoproj" / "config.yaml", "w") as f:
                f.write(f"root_dir: {root_dir}\n")

        os.environ["AUTOPROJ_CURRENT_ROOT"] = str(root_dir)