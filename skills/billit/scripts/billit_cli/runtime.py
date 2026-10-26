import os
import sys
from dataclasses import dataclass
from typing import Any, Callable, TextIO

from .transport import Transport, Urllib


@dataclass
class Runtime:
    env: dict
    cwd: str
    home: str
    transport: Transport
    stdout: TextIO
    stderr: TextIO
    stdin: TextIO
    execvp: Callable[[str, list], Any]
    entry: str

    @classmethod
    def live(cls, entry):
        return cls(env=dict(os.environ), cwd=os.getcwd(), home=os.path.expanduser("~"), transport=Urllib(),
                   stdout=sys.stdout, stderr=sys.stderr, stdin=sys.stdin, execvp=os.execvp,
                   entry=os.path.realpath(entry))
