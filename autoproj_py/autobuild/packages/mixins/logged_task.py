from logging import Logger
import subprocess
import sys
from textwrap import dedent, indent

from autoproj_py.logger import setup_logger
from autoproj_py.subprocess import Subprocess

class LoggedTaskMixin:

    def __init__(self, name: str, log_dir: str):
        self.name = name
        self.log_dir = log_dir
        self.loggers: dict[str, Logger] = {
            'import': self.make_logger('import'),
            'update': self.make_logger('update'),
            'build': self.make_logger('build'),
            'install': self.make_logger('install')
        }

    def make_logger(self, task_name: str) -> Logger:
        filename = self.log_dir / f'{self.name}-{task_name}.log'
        logger = setup_logger(f'{self.name}-{task_name}', filename=filename, level='DEBUG', stream_stdout=False)
        return logger

    def add_task(self, task_name: str):
        self.loggers[task_name] = self.make_logger(task_name)

    def run(self, task_name: str, cmd: list[str] | str, cwd: str, env: dict):
        log_msg = dedent("""
            running:
                {cmd}

            in directory:
                {cwd}

            with environment:
                {env}

            [OUT_BEGIN]
            {output}
            [OUT_END]

            Exit: {{code={retcode}}}
        """)

        buffer = ''
        p = Subprocess.run(cmd, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        for line in p.stdout:
            print(line, file=sys.stdout, end='')
            buffer += line

        retcode = p.wait()

        # if retcode != 0:
        stderr_lines = []
        for line in p.stderr:
            stderr_lines.append(line)
            buffer += line

        for line in stderr_lines[-10:]:
            print(line, file=sys.stdout, end='')

        print(f'\nComplete log at {self.loggers[task_name].handlers[0].baseFilename}')

        cmd = ' '.join(cmd) if isinstance(cmd, list) else cmd
        env_list = [f'{key}={value}' for key, value in env.items()]
        env = env_list[0] + '\n' + indent('\n'.join(env_list[1:]), prefix='    ')
        output = buffer

        log_msg = log_msg.format(cmd=cmd, cwd=cwd, env=env, output=output, retcode=retcode)

        self.loggers[task_name].info(log_msg)
