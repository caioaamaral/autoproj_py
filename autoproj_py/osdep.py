from pathlib import Path

import lsb_release
import yaml


DISTRO = lsb_release.get_distro_information()['CODENAME']


class OSDepRegistry:

    def __init__(self, name: str):
        self.name = name
        self._packages = dict[str, 'APT_OSDep']()

    def send(self, osdep: Path):
        with open(osdep, 'r') as file:
            data: dict = yaml.safe_load(file)
            for name, definition in data.items():
                pkg = APT_OSDep(name, definition, declared_at=f'{self.name}: {osdep}')
                self._packages[name] = pkg

    def has(self, package_name: str):
        return package_name in self._packages

    def get(self, package_name: str):
        return self._packages[package_name]

    def keys(self):
        return self._packages.keys()

    def list(self):
        return list(self._packages.items())


class APT_OSDep:

    def __init__(self, name: str, definition: dict, declared_at=None):
        self.name = name
        self.definition = definition
        self.declared_at = declared_at

    @property
    def apt_dpkg(self):
        if DISTRO in self.definition:
            pkgs = [self.definition[DISTRO]]
            if (osdep := self.definition.get('osdep', '')):
                pkgs.append(osdep)

            return f"{','.join(pkgs)}"

        if 'default' in self.definition:
            pkgs = [self.definition['default']]
            if (osdep := self.definition.get('osdep', '')):
                pkgs.append(osdep)

            return f"{', '.join(pkgs)}"
    
    @property
    def rule(self):
        if DISTRO in self.definition:
            return f'{DISTRO}: {self.definition[DISTRO]}'

        if 'default' in self.definition:
            return f'default: {self.definition["default"]}'

    def details(self):
        bold = "\033[1m"
        reset = "\033[0m"
        return (
            f"{bold}APT OSDep '{self.name}'{reset} \n"
            f'  {bold}first match:{reset}\n'
            f'      {self.declared_at}\n'
            f"  {bold}apt-dpkg:{reset}\n"
            f"      {self.apt_dpkg} [selector: '{self.rule}]'\n"
            f"  {bold}osdep:{reset}\n"
            f"      {self.definition['osdep']}\n" if 'osdep' in self.definition else ''
        )

    def install(self):
        name = self.osdep.get(DISTRO, None)
        
        if name is None:
            return
        
        self._install(name)
    
    def _install(self, name: str):
        pass
        # subprocess.run(["sudo", "apt", "install", "-y", name])