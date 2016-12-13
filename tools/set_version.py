import os
import re
import semver

from os import path

VERSION_FILE = path.abspath(
    path.join(path.dirname(__file__),
              '..',
              'VERSION'))


def get_version():
    return ''.join(
        line for line in open(VERSION_FILE)
        if not line.startswith('#')).strip()


def set_version_interactive():
    current_version = get_version()

    print('Current version: {}'.format(current_version))

    print('Note: New version must be a valid SemVer string. '
          'See http://semver.org')

    while True:
        new_version_str = input('New SemVer string: ')
        try:
            new_version = semver.parse_version_info(new_version_str)
        except Exception as exc:
            print('Could not parse version: {}'.format(exc))
        else:
            break

    print('New version: {}'.format(new_version))

    write_package_json(new_version)
    write_version_file(new_version)


def write_package_json(version_tuple):
    package_json_file = path.abspath(
        path.join(
            path.dirname(__file__),
            '..',
            'socker.js',
            'package.json'
        )
    )

    version = semver.format_version(*version_tuple)

    lines = [i for i in open(package_json_file, 'r')]

    edited_lines = []

    version_re = re.compile(r'("version":\s?")([^"]*)(")')

    for line in lines:
        match = version_re.search(line)
        if match:
            print('Match groups {0!r}'.format(match.groups()))
            line = version_re.sub(r'\g<1>{}\g<3>'.format(version), line)
        edited_lines.append(line)

    print('Writing version to {}'.format(package_json_file))

    open(package_json_file, 'w').writelines(edited_lines)


def write_version_file(version_tuple, version_file=VERSION_FILE):
    print('Writing version to {}'.format(version_file))

    vf_lines = [i for i in open(version_file, 'r')]

    vf_lines[0] = '{}\n'.format(semver.format_version(*version_tuple))

    open(version_file, 'w').writelines(vf_lines)


if __name__ == '__main__':
    set_version_interactive()
