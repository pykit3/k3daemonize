# DO NOT EDIT!!! built with `python _building/build_setup.py`
import setuptools
setuptools.setup(
    name="k3daemonize",
    packages=["k3daemonize"],
    version="0.1.0",
    license='MIT',
    description='It supplies a command line interface API to start/stop/restart a daemon.',
    long_description="# k3daemonize\n\n[![Action-CI](https://github.com/pykit3/k3daemonize/actions/workflows/python-package.yml/badge.svg)](https://github.com/pykit3/k3daemonize/actions/workflows/python-package.yml)\n[![Build Status](https://travis-ci.com/pykit3/k3daemonize.svg?branch=master)](https://travis-ci.com/pykit3/k3daemonize)\n[![Documentation Status](https://readthedocs.org/projects/k3daemonize/badge/?version=stable)](https://k3daemonize.readthedocs.io/en/stable/?badge=stable)\n[![Package](https://img.shields.io/pypi/pyversions/k3daemonize)](https://pypi.org/project/k3daemonize)\n\nIt supplies a command line interface API to start/stop/restart a daemon.\n\nk3daemonize is a component of [pykit3] project: a python3 toolkit set.\n\n\nHelp to create daemon process.\nIt supplies a command line interface API to start/stop/restart a daemon.\n\n`daemonize` identifies a daemon by the `pid` file.\nThus two processes those are set up with the same `pid` file\ncan not run at the same time.\n\n\n\n\n# Install\n\n```\npip install k3daemonize\n```\n\n# Synopsis\n\n```python\n\nimport time\nimport k3daemonize\n\n\ndef run():\n    for i in range(100):\n        print(i)\n        time.sleep(1)\n\n\n# python foo.py start\n# python foo.py stop\n# python foo.py restart\n\nif __name__ == '__main__':\n    # there is at most only one of several processes with the same pid path\n    # that can run.\n    k3daemonize.daemonize_cli(run, '/var/run/pid')\n\n```\n\n#   Author\n\nZhang Yanpo (张炎泼) <drdr.xp@gmail.com>\n\n#   Copyright and License\n\nThe MIT License (MIT)\n\nCopyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>\n\n\n[pykit3]: https://github.com/pykit3",
    long_description_content_type="text/markdown",
    author='Zhang Yanpo',
    author_email='drdr.xp@gmail.com',
    url='https://github.com/pykit3/k3daemonize',
    keywords=['python', 'daemon'],
    python_requires='>=3.0',

    install_requires=['k3ut>=0.1.15,<0.2', 'k3proc>=0.2.13,<0.3.0'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
    ] + ['Programming Language :: Python :: 3'],
)
