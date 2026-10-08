import os
import subprocess
import sys
import time
import unittest

import k3proc
import k3ut

import k3daemonize

dd = k3ut.dd

this_base = os.path.dirname(__file__)

# Holds an exclusive lock on argv[1] until killed.
HOLD_LOCK_SCRIPT = """
import fcntl
import sys
import time

f = open(sys.argv[1], "w")
fcntl.lockf(f, fcntl.LOCK_EX)
print("locked", flush=True)
time.sleep(60)
"""

# Writes the pid file argv[1] under a file size limit of 0, so writing the pid fails.
WRITE_PID_OVER_SIZE_LIMIT_SCRIPT = """
import resource
import signal
import sys

import k3daemonize

signal.signal(signal.SIGXFSZ, signal.SIG_IGN)
resource.setrlimit(resource.RLIMIT_FSIZE, (0, 0))
k3daemonize.Daemon(pidfile=sys.argv[1]).write_pid_or_exit()
"""

# Runs daemonize_cli() in the foreground with the pid file argv[1].
RUN_CLI_SCRIPT = """
import sys

import k3daemonize

pidfn = sys.argv.pop(1)
k3daemonize.daemonize_cli(lambda: None, pidfn)
"""

# Lets the scripts above import k3daemonize from this checkout.
SCRIPT_ENV = dict(os.environ, PYTHONPATH=this_base + "/../..")


def subproc(script, env=None):
    if env is None:
        env = {
            "PYTHONPATH": this_base + "/../..",
        }

    return k3proc.shell_script(script, env=env)


def read_file(fn):
    try:
        with open(fn, "r") as f:
            cont = f.read()
            return cont
    except OSError:
        return None


class TestDaemonize(unittest.TestCase):
    foo_fn = "/tmp/foo"
    bar_fn = "/tmp/bar"
    pidfn = "/tmp/test_daemonize.pid"

    def _clean(self):
        # kill foo.py and kill bar.py
        # bar.py might be waiting for foo.py to release lock-file.
        try:
            subproc(f"python {this_base}/foo.py stop")
        except OSError as e:
            dd(repr(e))

        time.sleep(0.1)

        try:
            subproc(f"python {this_base}/bar.py stop")
        except OSError as e:
            dd(repr(e))

        # remove written file

        try:
            os.unlink(self.foo_fn)
        except OSError:
            pass

        try:
            os.unlink(self.bar_fn)
        except OSError:
            pass

    def setUp(self):
        self._clean()

    def tearDown(self):
        self._clean()

    def test_start(self):
        subproc(f"python {this_base}/foo.py start")
        time.sleep(0.2)

        self.assertEqual("foo-before", read_file(self.foo_fn))
        time.sleep(1)
        self.assertEqual("foo-after", read_file(self.foo_fn))

    def test_stop(self):
        subproc(f"python {this_base}/foo.py start")
        time.sleep(0.2)

        self.assertEqual("foo-before", read_file(self.foo_fn), "foo started")

        subproc(f"python {this_base}/foo.py stop")
        time.sleep(0.2)

        self.assertEqual("foo-before", read_file(self.foo_fn), "process has been kill thus no content is updated")

    def test_restart(self):
        subproc(f"python {this_base}/foo.py start")
        time.sleep(0.2)

        self.assertEqual("foo-before", read_file(self.foo_fn))

        os.unlink(self.foo_fn)
        self.assertEqual(None, read_file(self.foo_fn))

        subproc(f"python {this_base}/foo.py restart")
        time.sleep(0.2)

        self.assertEqual("foo-before", read_file(self.foo_fn), "restarted and rewritten to the file")

    def test_exclusive_pid(self):
        subproc(f"python {this_base}/foo.py start")
        time.sleep(0.1)
        subproc(f"python {this_base}/bar.py start")
        time.sleep(0.1)

        self.assertEqual(None, read_file(self.bar_fn), "bar.py not started or run")

    def test_default_pid_file(self):
        d = k3daemonize.Daemon()
        # pid file is based on __main__.__file__ which varies by invocation method
        self.assertTrue(d.pidfile.startswith("/var/run/"))

    def test_close_fds(self):
        env = {"PYTHONPATH": this_base + "/../.."}

        code, out, err = subproc(f"python {this_base}/close_fds.py close", env=env)

        dd("close_fds.py close result:")
        dd(code)
        dd("out:")
        for line in out.split("\n"):
            dd("  ", line)
        dd("err:")
        for line in err.split("\n"):
            dd("  ", line)

        time.sleep(1)

        fds = read_file(self.foo_fn)
        dd("fds:", fds)

        self.assertNotIn(self.bar_fn, fds)

        self._clean()

        code, out, err = subproc(f"python {this_base}/close_fds.py open", env=env)

        dd("close_fds.py open result:")
        dd(code)
        dd("out:")
        for line in out.split("\n"):
            dd("  ", line)
        dd("err:")
        for line in err.split("\n"):
            dd("  ", line)

        time.sleep(1)

        fds = read_file(self.foo_fn)
        dd("fds:", fds)

        self.assertIn(self.bar_fn, fds)


class TestTrylock(unittest.TestCase):
    def test_exit_when_lock_is_held_by_another_process(self):
        d = k3daemonize.Daemon(pidfile="/tmp/test_daemonize_trylock.pid")
        holder = subprocess.Popen(
            [sys.executable, "-c", HOLD_LOCK_SCRIPT, d.lockfile],
            stdout=subprocess.PIPE,
            text=True,
        )
        try:
            self.assertEqual("locked\n", holder.stdout.readline())

            with self.assertRaises(SystemExit) as ctx:
                d.trylock_or_exit(timeout=0.3)
        finally:
            holder.kill()
            holder.wait()
            holder.stdout.close()

        self.assertEqual(1, ctx.exception.code)
        self.assertIsNone(d.lockfp)
        os.unlink(d.lockfile)


class TestExitStatus(unittest.TestCase):
    # Python also exits with 1 on an uncaught error, so each test checks the log too.

    def test_exit_1_when_pid_write_fails(self):
        pidfn = "/tmp/test_daemonize_write_pid.pid"

        proc = subprocess.run(
            [sys.executable, "-c", WRITE_PID_OVER_SIZE_LIMIT_SCRIPT, pidfn],
            env=SCRIPT_ENV,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(1, proc.returncode, proc.stderr)
        self.assertIn("write pid failed.", proc.stderr)
        os.unlink(pidfn)

    def test_cli_exit_1_when_pid_file_is_dir(self):
        # Even root can not open a directory as the pid file.
        pidfn = "/tmp/test_daemonize_pid_dir"
        os.makedirs(pidfn, exist_ok=True)

        proc = subprocess.run(
            [sys.executable, "-c", RUN_CLI_SCRIPT, pidfn],
            env=SCRIPT_ENV,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(1, proc.returncode, proc.stderr)
        self.assertIn("daemonize_cli failed", proc.stderr)
        os.rmdir(pidfn)
        os.unlink(pidfn + ".lock")
