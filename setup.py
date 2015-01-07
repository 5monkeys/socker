import sys
from os import path
from setuptools import setup, find_packages

src = path.join(path.dirname(path.abspath(__file__)), 'src')
sys.path.append(src)

name = 'socker'
version = __import__(name).__version__

import os
os.chdir(src)

setup(
    name=name,
    version=version,
    author='Joar Wandborg',
    author_email='joar@5monkeys.se',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'socker = socker.cli.command:Interface'
        ]
    },
    install_requires=[
        'asyncio-redis>=0.13.4',
        'websockets>=2.3',
        'docopt>=0.6.2',
    ]
)