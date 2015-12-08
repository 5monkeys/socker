#!/usr/bin/env bash
# Utility script for socker python package release
#set -o xtrace

function get_package_version {
    python -c 'import socker.version; print(socker.version.__version__)'
}

function info {
    echo 'info:' $@
}

function fatal {
    echo 'Fatal:' $@
    exit 1
}

function update_version {
    echo 'Current socker version:' $(get_package_version)
    echo -n 'Do you want to update the version? [y/n]: '
    read choice
    case $choice in
        y | Y)
        python 'tools/update_version.py'
        if test ! $? -eq 0; then
            fatal 'tools/update_version.py encountered an error'
        fi
        ;;
        n | N)
        # Do nothing
        ;;
        *)
        fatal 'Unknown choise' $choice
        ;;
    esac
}

function build_python_package_distribution_files {
    python setup.py sdist bdist_wheel || fatal 'Could not build python package'
    return
}

function upload_package {
    package_files=dist/socker-$(get_package_version)*
    info 'Uploading package_files:' $package_files
    twine upload $package_files || fatal 'Could not upload package files'
}

function release_main {
    # Version
    update_version
    build_python_package_distribution_files
    upload_package
}


# Run main method
release_main
