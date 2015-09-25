import os
import sys
import subprocess

from distutils.version import StrictVersion


def make_release():
    # Add /src to path
    src_dir = os.path.join(
        os.path.dirname(__file__),
        '..',
        'src')

    sys.path.append(src_dir)

    from socker.version import get_version
    current_version = get_version()

    print('Current version {}'.format(current_version))

    new_version_str = input('New version: ')

    new = StrictVersion(new_version_str)

    print('New version: {}, {}'.format(
        new.version, new.prerelease))


if __name__ == '__main__':
    make_release()
