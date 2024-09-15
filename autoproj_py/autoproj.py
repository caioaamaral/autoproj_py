import os
from pathlib import Path

from config import Config


class Autoproj:
    @staticmethod
    def autoproj_current_root_env():
        current_root_var = os.environ.get("AUTOPROJ_CURRENT_ROOT")
        if not current_root_var:
            raise ValueError("AUTOPROJ_CURRENT_ROOT is not set")
        
        return Path(current_root_var)
    
    root_dir = autoproj_current_root_env()
    autoproj_dir = root_dir / "autoproj"

    config = Config(autoproj_dir / "config.yaml")
    