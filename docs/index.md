# k3daemonize

[![Action-CI](https://github.com/pykit3/k3daemonize/actions/workflows/python-package.yml/badge.svg)](https://github.com/pykit3/k3daemonize/actions/workflows/python-package.yml)
[![Documentation Status](https://readthedocs.org/projects/k3daemonize/badge/?version=stable)](https://k3daemonize.readthedocs.io/en/stable/?badge=stable)
[![Package](https://img.shields.io/pypi/pyversions/k3daemonize)](https://pypi.org/project/k3daemonize)

Create daemon processes with CLI for start/stop/restart. Identifies daemons by PID file to prevent duplicate processes.

k3daemonize is a component of [pykit3](https://github.com/pykit3) project: a python3 toolkit set.

## Installation

```bash
pip install k3daemonize
```

## Quick Start

```python
import time
import k3daemonize

def run():
    for i in range(100):
        print(i)
        time.sleep(1)

# python foo.py start
# python foo.py stop
# python foo.py restart
if __name__ == '__main__':
    k3daemonize.daemonize_cli(run, '/var/run/pid')
```

## API Reference

::: k3daemonize

## License

The MIT License (MIT) - Copyright (c) 2015 Zhang Yanpo (张炎泼)
