import os
import sys

import k3proc

import k3daemonize

foo_fn = "/tmp/foo"
bar_fn = "/tmp/bar"
pidfn = "/tmp/test_daemonize.pid"


def write_file(fn, cont):
    try:
        with open(fn, "w") as f:
            f.write(cont)
    except Exception as e:
        print(repr(e) + " while write_file:" + fn)
        raise


def run():
    try:
        _code, out, _err = k3proc.shell_script("lsof -p " + str(os.getpid()))
    except OSError as e:
        print(repr(e))
    write_file(foo_fn, repr(out))


if __name__ == "__main__":
    # The daemon inherits this open file unless close_fds=True; test_close_fds checks for it.
    fd = open(bar_fn, "w")  # noqa: SIM115
    op = sys.argv[1]
    # daemonize.daemonize_cli neede sys.argv[1] to decide what to do.
    sys.argv[1] = "start"
    if op == "close":
        k3daemonize.daemonize_cli(run, pidfn, close_fds=True)
    else:
        k3daemonize.daemonize_cli(run, pidfn, close_fds=False)
