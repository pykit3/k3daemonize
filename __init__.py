"""
Help to create daemon process.
It supplies a command line interface API to start/stop/restart a daemon.

`daemonize` identifies a daemon by the `pid` file.
Thus two processes those are set up with the same `pid` file
can not run at the same time.

"""

from .daemonize import (
    Daemon,
    daemonize_cli,
)

__all__ = [
    "Daemon",
    "daemonize_cli",
]


def __getattr__(name: str) -> str:
    # importlib.metadata takes about 20 ms to import, so it is loaded only
    # when __version__ is read
    if name != "__version__":
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    from importlib.metadata import version

    return version("k3daemonize")
