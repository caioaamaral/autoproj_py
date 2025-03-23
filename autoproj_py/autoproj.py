import os
from pathlib import Path
import shutil
import subprocess

from autoproj_py.config import Config
from autoproj_py.environment import Environment
from autoproj_py.logger import setup_logger
from autoproj_py.manifest import Manifest


class Autoproj:
    @staticmethod
    def autoproj_current_root_env():
        current_root_var = os.environ.get('AUTOPROJ_CURRENT_ROOT')
        if not current_root_var:
            raise ValueError('AUTOPROJ_CURRENT_ROOT is not set')
        
        return Path(current_root_var)
    
    root_dir = autoproj_current_root_env()
    autoproj_dir = root_dir / 'autoproj'
    import_dir = root_dir / 'src'
    src_dir = root_dir / 'src'
    install_dir = root_dir / 'install'
    log_dir = root_dir / 'log'

    config = Config(autoproj_dir / 'config.yaml')
    env = Environment(root_dir / 'env.sh')
    manifest = Manifest
    logger = setup_logger('autoproj', filename=log_dir / 'autoproj-last.log', level='DEBUG')

    @classmethod
    def debug(cls, message):
        cls.logger.debug(message)

    @classmethod
    def info(cls, message):
        cls.logger.info(message)

    @classmethod
    def warn(cls, message):
        cls.logger.warning(message)

    @classmethod
    def error(cls, message):
        cls.logger.error(message)

    @classmethod
    def execute_once(cls, name, fn):
        name = Autoproj.manifest.current_package_set().name + '.' + name
        cached_tasks: list = cls.config.get(f'__cache__.tasks')
        if name in cached_tasks:
            return

        fn()
        cached_tasks.append(name)
        cls.config.set('__cache__.tasks', cached_tasks)
        cls.config.save()

    @classmethod
    def run(cls, cmd: list[str], cwd: str=root_dir, env: dict = os.environ, capture_output: bool = True, shell='sh'):
        envsh = cls.root_dir / 'env.sh'
        cmd = [shutil.which(shell), '-c' , f'. "{envsh}" && ' + ' '.join(cmd)]
        cls.info(f"running: {' '.join(cmd)}")
        return subprocess.run(cmd, cwd=cwd, env=env, capture_output=capture_output, text=True)

Autoproj.manifest = Manifest.init(Autoproj.root_dir, autoproj=Autoproj)
Autoproj.env.save()

Autoproj.info('Running autoproj')
