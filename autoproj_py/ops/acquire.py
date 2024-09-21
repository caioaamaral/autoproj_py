from git import Repo

def git_import(git_url, import_path):
    print(f"importing from {git_url} into {import_path}")
    Repo.clone_from(git_url, import_path)


def import_package(source, import_path):
    git_import(source, import_path)
