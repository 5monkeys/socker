import pkg_resources


def get_version():
    return pkg_resources.require('socker')[0].version
