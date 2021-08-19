"""
Help to create daemon process.
It supplies a command line interface API to start/stop/restart a daemon.

`daemonize` identifies a daemon by the `pid` file.
Thus two processes those are set up with the same `pid` file
can not run at the same time.

"""

__version__ = "0.1.0"
__name__ = "k3daemonize"

from .daemonize import (
    Daemon,
    daemonize_cli,
)

__all__ = [
    'Daemon',
    'daemonize_cli',
]
