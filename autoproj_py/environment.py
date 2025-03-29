from pathlib import Path
import shutil
import subprocess

from autoproj_py.subprocess import Subprocess


def _validate_file(file: Path):
    if not file.exists():
        raise FileNotFoundError(f'{file} does not exist')
    if not file.is_file():
        raise FileNotFoundError(f'{file} is not a file')

    return file


class Environment:

    def __init__(self, file: Path):
        self.file = _validate_file(file)
        self._envars = dict()
        self._source_after = list()

    def __repr__(self):
        return f'Environment(envars:{self._envars}, source_after:{self._source_after})'

    def set(self, key: str, value: str|int|float):
        self._envars[key] = value

    def remove(self, key: str):
        self._envars.pop(key, None)

    def source_after(self, file: str):
        self._source_after.append(file)

    def export_context(self):
        command = f'{shutil.which("bash")} -c ". {self.file} && env"'
        p = Subprocess.run(command, stdout=subprocess.PIPE)
        p.wait()

        _context = dict()
        for line in p.stdout:
            key, value = line.strip().split('=', 1)
            _context[key] = value

        return _context

    def save(self):
        with open(self.file, 'w') as f:
            for key, value in self._envars.items():
                f.write(f'export {key}={value}\n')
            for file in self._source_after:
                f.write(f'. {file}\n')
