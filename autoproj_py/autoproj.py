import os
from pathlib import Path

from autoproj_py.config import Config
from autoproj_py.autobuild.registry import PackageRegistry

class Autoproj:
    @staticmethod
    def autoproj_current_root_env():
        current_root_var = os.environ.get("AUTOPROJ_CURRENT_ROOT")
        if not current_root_var:
            raise ValueError("AUTOPROJ_CURRENT_ROOT is not set")
        
        return Path(current_root_var)
    
    root_dir = autoproj_current_root_env()
    autoproj_dir = root_dir / "autoproj"
    import_dir = root_dir / "src"
    src_dir = root_dir / "src"
    install_dir = root_dir / "install"

    config = Config(autoproj_dir / "config.yaml")
    registry = PackageRegistry.__init__(lookup_paths=[autoproj_dir], root_dir=root_dir)
