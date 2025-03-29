import os


class ConfigureMixin:

    def configure_directories(self):
        self.build_dir = self.root_dir / 'build' / self.name
        self.install_dir = self.root_dir / 'install' / self.name
        self.log_dir = self.root_dir / 'log' / self.name
        os.makedirs(self.build_dir, exist_ok=True)
        os.makedirs(self.install_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
