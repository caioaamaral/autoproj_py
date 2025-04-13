import venv
import subprocess
from pathlib import Path


class PythonEnv:
    def __init__(self, path: Path):
        self.path = path
        self._python = None

    @property
    def python(self) -> Path:
        """Get the path to the virtualenv's Python interpreter."""
        if self._python is None:
            if not self.path.exists():
                self.create()
            self._python = self.path / 'bin' / 'python'
        return self._python

    def create(self):
        """Create the virtualenv and install autoproj_py.

        This method:
        1. Creates a new virtualenv in self.path with system site packages
        2. Installs autoproj_py in editable mode (-e) to make all system dependencies
           (like gitpython) available in the virtualenv
        3. This ensures that init files can run with access to all required dependencies
           while maintaining isolation between package sets
        """
        self.path.mkdir(parents=True, exist_ok=True)
        venv.create(self.path, with_pip=True, system_site_packages=True)
        
        # Get the Python path directly to avoid recursion
        python = self.path / 'bin' / 'python'
        
        # Get the workspace root directory (where setup.py is located)
        workspace_root = Path(__file__).parent.parent.parent
        
        # Install autoproj_py in editable mode to make system dependencies available
        cmd = [str(python), '-m', 'pip', 'install', '-e', str(workspace_root)]
        subprocess.run(cmd, check=True)
        
        # Set the Python path after installation
        self._python = python

    def run_module(self, module_path: Path, context: dict = None):
        """Run a Python module in this virtualenv."""
        import sys
        import runpy

        module_name = f'{module_path.parent.name}.{module_path.name.removesuffix(".py")}'

        # Store original sys.path
        original_path = sys.path.copy()

        try:
            # Add virtualenv's site-packages to sys.path
            site_packages = self.path / 'lib' / f'python{sys.version_info.major}.{sys.version_info.minor}' / 'site-packages'
            if site_packages.exists():
                sys.path.insert(0, str(site_packages))

            # Add the module's parent directory to sys.path
            sys.path.insert(0, str(module_path.parent.parent))

            # Run the module directly with the provided context
            runpy.run_module(f'{module_name}', run_name='__main__', init_globals=context or {})
        finally:
            # Restore original sys.path
            sys.path = original_path
