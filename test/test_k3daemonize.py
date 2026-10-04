import os
import time
import unittest

import k3proc
import k3ut

import k3daemonize

dd = k3ut.dd

this_base = os.path.dirname(__file__)


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
