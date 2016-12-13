#!/usr/bin/env python
import sys

from os import path

from pkg_resources import parse_requirements

from setuptools import setup, find_packages


name = 'socker'  # PyPI name
package_name = name.replace('-', '_')  # Python module name
package_path = 'src'  # Where does the package live?
version_file = path.join(path.dirname(__file__), 'VERSION')

here = path.dirname(path.abspath(__file__))

# Add src dir to path
sys.path.append(package_path)


# Get the long description from the relevant file
long_description = None

try:
    with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
        long_description = f.read()
except Exception:
    pass


def get_version():
    """
    Get the version from version_file
    """
    return ''.join(
        line for line in open(version_file)
        if not line.startswith('#')).strip()


def get_requirements(filename):
    return [str(r) for r in parse_requirements(open(filename).read())]


setup(
    name=name,
    version=get_version(),
    author='Joar Wandborg',
    author_email='joar@5monkeys.se',
    url='https://github.com/5monkeys/socker',
    license='MIT',
    description='redis pubsub websocket proxy',
    long_description=long_description,
    package_dir={'': package_path},
    packages=find_packages(package_path),
    entry_points={
        'console_scripts': [
            'socker = socker.cli.command:Interface'
        ]
    },
    install_requires=get_requirements('requirements.txt')
)
