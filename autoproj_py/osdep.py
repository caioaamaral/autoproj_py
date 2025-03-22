from pathlib import Path

import lsb_release
import yaml


DISTRO = lsb_release.get_distro_information()['CODENAME']


class APT_OSDepManifest:

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


class APT_OSDep:

    @classmethod
    def from_manifest(cls, manifest: APT_OSDepManifest, declared_at=None):
        if DISTRO in manifest.rules:
            rule = f'{DISTRO}: {manifest.rules[DISTRO]}'
            return cls(manifest.name, rule, manifest.osdeps, declared_at=declared_at)

        if 'default' in manifest.rules:
            rule = f"default: {manifest.rules['default']}"
            return cls(manifest.name, rule, manifest.osdeps, declared_at=declared_at)

    @classmethod
    def from_dict(cls, definition: dict, declared_at=None):
        manifest = APT_OSDepManifest.from_dict(definition)
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

    def install(self):
        name = self.osdep.get(DISTRO, None)
        
        if name is None:
            return
        
        self._install(name)
    
    def _install(self, name: str):
        pass
        # subprocess.run(["sudo", "apt", "install", "-y", name])


class OSDepRegistry:

    def __init__(self, name: str):
        self.name = name
        self._packages = dict[str, APT_OSDep]()

    def send(self, osdep: Path|APT_OSDep):
        if isinstance(osdep, Path):
            with open(osdep, 'r') as file:
                data: dict = yaml.safe_load(file)
                for name, definition in data.items():
                    pkg = APT_OSDep.from_dict({name: definition}, declared_at=f'{self.name}: {osdep}')
                    self._packages[name] = pkg

        elif isinstance(osdep, APT_OSDep):
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
