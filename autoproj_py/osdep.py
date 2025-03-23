from pathlib import Path
import re
import shutil
import subprocess

import lsb_release
import yaml


DISTRO = lsb_release.get_distro_information()['CODENAME']


class APT_OSDep:

    KEYRINGS_DIR = Path('/usr/share/keyrings')
    SOURCES_LIST_DIR = Path('/etc/apt/sources.list.d')

    @classmethod
    def add_repo(cls, name: str, rule: str, key=None):
        if key:
            p = subprocess.run(
                [shutil.which('sh'), '-c', f"sudo tee {(cls.KEYRINGS_DIR / f'{name}-archive-keyring.gpg').as_posix()}"],
                input=key,
                capture_output=True,
            )

            if p.returncode != 0:
                raise Exception('Failed to add key')

        p = subprocess.run(
            [shutil.which('sh'), '-c', f"echo '{rule}' | sudo tee {(cls.SOURCES_LIST_DIR / f'{name}.list').as_posix()}"],
            capture_output=True,
        )

        if p.returncode != 0:
                raise Exception('Failed to add repo')


    @staticmethod
    def install(name: str):
        subprocess.run(['sudo', shutil.which('apt'), 'install', '-y', name])

    @staticmethod
    def is_installed(name: str):
        output = subprocess.run([shutil.which('dpkg'), '-s', name], capture_output=True, text=True)
        return False if output.stderr else True

class PIP_OSDep:

    @staticmethod
    def install(name: str):
        subprocess.run([shutil.which('pip'), 'install', name])

    @staticmethod
    def is_installed(name: str):
        output = subprocess.run([shutil.which('pip'), 'show', name], capture_output=True, text=True)
        return False if output.stderr else True


OSDepHandlers = {
    re.compile(r'.'): (0, APT_OSDep),
    re.compile(r'^pip$'): (10, PIP_OSDep),
}

class OSDepManifest:

    @classmethod
    def from_dict(cls, definition: dict[str, dict]):
        for name, defs in definition.items():
            osdeps = defs.pop('osdep', None)
            rules = defs

            return cls(name, rules, osdeps)

    def __init__(self, name: str, rules: list[dict], osdeps: list[str]|None):
        self.name = name
        self.rules = rules
        self.osdeps = osdeps

    def to_dict(self):
        if self.osdeps:
            self.rules.append(self.osdeps)

        return {
            self.name: self.rules
        }


class OSDep:

    @classmethod
    def from_manifest(cls, manifest: OSDepManifest, declared_at=None):
        if DISTRO in manifest.rules:
            rule = f'{DISTRO}: {manifest.rules[DISTRO]}'
            return cls(manifest.name, rule, manifest.osdeps, declared_at=declared_at)

        if 'default' in manifest.rules:
            rule = f"default: {manifest.rules['default']}"
            return cls(manifest.name, rule, manifest.osdeps, declared_at=declared_at)

    @classmethod
    def from_dict(cls, definition: dict, declared_at=None):
        manifest = OSDepManifest.from_dict(definition)
        return cls.from_manifest(manifest, declared_at=declared_at)


    def __init__(self, name: str, rule: str, osdep: list[str]|None, declared_at=None):
        self.name = name
        self.rule = rule
        self.osdep = osdep
        self.declared_at = declared_at
        self.reverse_dependencies = []

    @property
    def apt_dpkg(self):
        if not self.osdep:
            pkgs = [self.name]

        elif type(self.osdep) is list:
            pkgs = [self.name, *self.osdep]

        else:
            pkgs = [self.name, self.osdep]

        return f"{', '.join(pkgs)}"

    def details(self):
        bold = "\033[1m"
        reset = "\033[0m"
        return (
            f"{bold}APT OSDep '{self.name}'{reset} \n"
            f'  {bold}first match:{reset}\n'
            f'      {self.declared_at}\n'
            f"  {bold}apt-dpkg:{reset}\n"
            f"      {self.apt_dpkg} [selector: '{self.rule}]'\n"
            f"  {bold}reverse dependencies:{reset}\n"
            f"      {self.reverse_dependencies}\n"
        ) + (
            f"  {bold}osdep:{reset}\n"
            f"      {self.osdep}\n" if self.osdep else ''
        )

    def acquire(self):
        self.install()

    def install(self):
        name = self.apt_dpkg
        
        if name is None:
            return
        
        self._install(name)
    
    def _install(self, name: str):
        distro, name = self.rule.split(':')
        name = name.strip()
        best_score = -1
        selected_handler = None
        for hook in OSDepHandlers.keys():
            score, handler = OSDepHandlers[hook]
            if hook.match(distro) and score > best_score:
                best_score = score
                selected_handler = handler

        if not selected_handler.is_installed(name):
            selected_handler.install(name)


class OSDepRegistry:

    def __init__(self, name: str):
        self.name = name
        self._packages = dict[str, OSDep]()

    def send(self, osdep: Path|OSDep):
        if isinstance(osdep, Path):
            with open(osdep, 'r') as file:
                data: dict = yaml.safe_load(file)
                for name, definition in data.items():
                    pkg = OSDep.from_dict({name: definition}, declared_at=f'{self.name}: {osdep}')
                    self._packages[name] = pkg

        elif isinstance(osdep, OSDep):
            osdep.declared_at=f"{self.name}: 'dynamically declared'"
            self._packages[osdep.name] = osdep

    def has(self, package_name: str):
        return package_name in self._packages

    def get(self, package_name: str):
        return self._packages[package_name]

    def keys(self):
        return self._packages.keys()

    def list(self):
        return list(self._packages.items())
