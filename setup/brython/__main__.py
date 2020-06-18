"""This script creates the basic structure of a Brython project in the
current directory.
"""

import os
import shutil
import json
import argparse

from . import implementation


def install():
    """Put brython files on current directory."""
    print('Installing Brython {}'.format(implementation))

    data_path = os.path.join(os.path.dirname(__file__), 'data')
    current_path_files = os.listdir(os.getcwd())

    if current_path_files and 'brython.js' in current_path_files:
        override = input(
            'The brython.js is already present in this directory.'
            ' Override ? (Y/N)'
        )
        if override.lower() != 'y':
            import sys
            print('exiting')
            sys.exit()

    for path in os.listdir(data_path):
        try:
            shutil.copyfile(os.path.join(data_path, path), path)
        except SameFileError:
            print('{path} has not been moved. Are the same file.'.format(path))

    print('done')


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--add_package',
        help="Add a CPython package in Lib/site-packages")

    parser.add_argument('--install', help='Install Brython in an empty directory',
        action="store_true")

    parser.add_argument('--make_dist', help='Make a Python distribution',
        action="store_true")

    parser.add_argument('--make_package', help='Make a loadable Python package')

    parser.add_argument('--make_file_system', help='Make a virtual file system')

    parser.add_argument('--modules',
        help='Create brython_modules.js with all the modules used by the application',
        action="store_true")

    parser.add_argument('--reset', help='Reset brython_modules.js to stdlib',
        action="store_true")

    parser.add_argument('--update', help='Update Brython scripts',
        action="store_true")

    args = parser.parse_args()

    files = ['README.txt', 'demo.html', 'index.html',
        'brython.js', 'brython_stdlib.js', 'unicode.txt']

    if args.add_package:
        print('add package {}...'.format(args.add_package))
        package = __import__(args.add_package)
        package_file = package.__file__
        package_dir = os.path.dirname(package_file)
        lib_dir = os.path.join(os.getcwd(), 'Lib')
        if not os.path.exists(lib_dir):
            os.mkdir(lib_dir)
        dest_dir = os.path.join(lib_dir, 'site-packages')
        if not os.path.exists(dest_dir):
            os.mkdir(dest_dir)

        if os.path.splitext(package_dir)[1] == '.egg':
            import zipfile
            zf = zipfile.ZipFile(package_dir)
            for info in zf.infolist():
                if info.filename.startswith(('__pycache__', 'EGG-INFO')):
                    continue
                zf.extract(info, dest_dir)
                print('extract', info.filename)
            zf.close()
            print('done')
        elif not package_dir.split(os.sep)[-1] == "site-packages":
            print('copy folder', package_dir)
            dest_dir = os.path.join(dest_dir, args.add_package)
            if os.path.exists(dest_dir):
                shutil.rmtree(dest_dir)
            shutil.copytree(package_dir, dest_dir)
        else:
            print('copy single file', package_file)
            shutil.copyfile(package_file, os.path.join(dest_dir,
                os.path.basename(package_file)))

    if args.install:
        install()

    if args.update:
        print('Update Brython scripts to version {}'.format(implementation))

        data_path = os.path.join(os.path.dirname(__file__), 'data')

        for path in os.listdir(data_path):
            shutil.copyfile(os.path.join(data_path, path), path)

    if args.reset:
        print('Reset brython_modules.js to standard distribution')
        shutil.copyfile(os.path.join(os.getcwd(), 'brython_stdlib.js'),
            os.path.join(os.getcwd(), 'brython_modules.js'))

    if args.modules:
        print('Create brython_modules.js with all the modules used by the '
            'application')
        from . import list_modules

        finder = list_modules.ModulesFinder()
        finder.inspect()
        finder.make_brython_modules()

    if args.make_dist:
        print('Make a Python distribution for the application')
        from . import list_modules
        finder = list_modules.ModulesFinder()
        finder.inspect()
        finder.make_brython_modules()
        finder.make_setup()
        print('done')

    if args.make_file_system:
        print('Create a Javascript file for all the files in the directory')
        args_fs = args.make_file_system.split("#")
        if len(args_fs) > 2:
            raise ValueError("--make_file_systems expects at most 2 "
                "arguments, got " + str(len(args_fs)))
        vfs_name = args_fs[0]
        prefix = args_fs[1] if len(args_fs) > 1 else None
        from .make_file_system import make
        make(vfs_name, prefix)
        print('done')

    if args.make_package:
        package_name = args.make_package
        from . import make_package
        make_package.make(package_name, os.getcwd())
        print("done")

if __name__ == "__main__":
    main()
