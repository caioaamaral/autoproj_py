import subprocess
import shlex


class Subprocess:

    @staticmethod
    def run(
        command: str,
        cwd: str = None,
        env: dict = None,
        stdout = None,
        stderr = None
    ):
        args = shlex.split(command)

        return subprocess.Popen(
            args, 
            cwd=cwd, 
            env=env, 
            stdout=stdout,
            stderr=stderr,
            text=True
        )
            
