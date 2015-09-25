import os
import re
import sys
import subprocess
import json

from distutils.version import StrictVersion


def make_release():
    # Add /src to path
    src_dir = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '..',
            'src')
        )

    sys.path.append(src_dir)

    from socker.version import get_version

    current_version = get_version()
    print('Current version {}'.format(current_version))

    new_version_str = input('New version: ')

    new = StrictVersion(new_version_str)

    print('New version: {}, {}'.format(
        new.version, new.prerelease))

    prerelease_type_map = {
        'a': 'alpha',
        'b': 'beta',
        'c': 'rc'
    }

    new_version = list(new.version)
    if new.prerelease is None:
        new_version.extend(['final', 9])
    else:
        p = new.prerelease
        new_version.extend([
            prerelease_type_map[p[0]],
            p[1]
        ])

    new_version = tuple(new_version)

    print('New version tuple: {}'.format(new_version))

    write_package_json(new_version)
    write_version_file(new_version)


def write_package_json(version_tuple):
    from socker.version import get_version

    package_json_fn = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '..',
            'socker.js',
            'package.json'
        )
    )

    version = get_version(version_tuple)

    ls = [i for i in open(package_json_fn, 'r')]

    new_ls = []

    version_re = re.compile(r'("version":\s?")([^"]*)(")')

    for line in ls:
        match = version_re.search(line)
        if match:
            print('Match groups {0!r}'.format(match.groups()))
            line = version_re.sub(r'\g<1>{}\g<3>'.format(version), line)
        new_ls.append(line)

    print('Writing version to {}'.format(package_json_fn))

    open(package_json_fn, 'w').writelines(new_ls)


def write_version_file(version_tuple):
    from socker import version as socker_version_module
    version_file = socker_version_module.__file__

    print('Writing version to {}'.format(version_file))

    vf_lines = [i for i in open(version_file, 'r')]

    vf_lines[0] = 'VERSION = {0!r}\n'.format(version_tuple)

    open(version_file, 'w').writelines(vf_lines)


if __name__ == '__main__':
    make_release()
