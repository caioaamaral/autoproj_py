import subprocess
from pathlib import Path


class Subprocess:
    @staticmethod
    def run(command: list[str], cwd: Path, env: dict = {}):
        command = ' '.join(command)
        print(subprocess.run(command, shell=True, cwd=cwd, env=env))
