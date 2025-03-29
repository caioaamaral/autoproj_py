import os
import shutil

from autoproj_py.autobuild.packages.package import Package

class CMake(Package):
    def __init__(self, name: str, source: str):
        super().__init__(name, source)
        self.build_dir = self.root_dir / "build" / self.name
        self.install_dir = self.root_dir / "install" / self.name
        self.use_manifest = True
        self.use_package_xml = False

    def build(self, registry, env=None, cwd=None, envsh=None):
        super().build(registry, env, cwd, envsh)
        self.configure()
        self.make()

        os.makedirs(self.install_dir, exist_ok=True)
        self.install()

    def configure(self):
        cmd = [shutil.which('cmake'), self.source_dir.as_posix(), '-DCMAKE_INSTALL_PREFIX=' + self.install_dir.as_posix()]
        self.run(cmd, cwd=self.build_dir, env=os.environ)

    def make(self):
        cmd = [shutil.which('make'), '-j']
        self.run('build', cmd, cwd=self.build_dir, env=os.environ)

    def install(self):
        cmd = [shutil.which('make'), 'install']
        self.run(cmd, cwd=self.install_dir, env=os.environ)
