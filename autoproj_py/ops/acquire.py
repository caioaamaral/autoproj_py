from git import Repo

from autoproj_py.package.definition import PackageDefinition

def git_import(git_url, local_path):
    print(f"importing from {git_url} into {local_path}")
    Repo.clone_from(git_url, local_path)


def import_package(package: PackageDefinition, local_path):
    git_import(package.source, local_path)
