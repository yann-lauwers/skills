import os
import sys
from dataclasses import dataclass
from typing import TextIO

from .transport import Transport, Urllib


@dataclass
class Runtime:
    env: dict
    transport: Transport
    stdout: TextIO
    stderr: TextIO
    stdin: TextIO

    @classmethod
    def live(cls):
        return cls(env=dict(os.environ), transport=Urllib(), stdout=sys.stdout, stderr=sys.stderr, stdin=sys.stdin)
