import lsb_release
import yaml


DISTRO = lsb_release.get_distro_information()['CODENAME']


class OSDepRegistry:
    _packages = dict[str, "APT_OSDep"]()

    @classmethod
    def send(cls, osdep: 'Path'):
        with open(osdep, 'r') as file:
            data: dict = yaml.safe_load(file)
            for name, definition in data.items():
                cls._packages[name] = APT_OSDep(name, definition, declared_at=osdep)

    @classmethod
    def has(cls, package_name: str):
        return package_name in cls._packages

    @classmethod
    def get(cls, package_name: str):
        return cls._packages[package_name]

    @classmethod
    def keys(cls):
        return cls._packages.keys()

    @classmethod
    def list(cls):
        return list(cls._packages.items())


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
            f"  {bold}apt-dpkg:{reset} {self.apt_dpkg}\n"
            f'  {bold}first match:{reset} {self.declared_at}\n'
            f"      {bold}selector:{reset} '{self.rule}'\n"
            f"  {bold}osdep:{reset} {self.definition['osdep']}\n" if 'osdep' in self.definition else ''
        )

    def install(self):
        name = self.osdep.get(DISTRO, None)
        
        if name is None:
            return
        
        self._install(name)
    
    def _install(self, name: str):
        pass
        # subprocess.run(["sudo", "apt", "install", "-y", name])