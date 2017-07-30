#!env python3
"""
    habitica-planner -- plan multiple recusive tasks with checklists
    Copyright 2017 Pavel Pletenev <cpp.create@gmail.com>
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
# pylint: disable=invalid-name
import sys
import setuptools


def make_version(version: str):
    """format a .devN if current installation isn't in upstream master"""
    try:
        from plumbum import local, CommandNotFound, ProcessExecutionError
    except ImportError:
        return version
    try:
        git = local['git']
        git('status')
    except (CommandNotFound, ProcessExecutionError):
        return version
    nc = git(*'rev-list --left-right --count master...{}'.format(version).split(' '))
    nc = int(nc.split('\t')[0])
    if nc == 0:
        return version  # just cloned or pushed - maybe a stable version
    return version + '.dev{}'.format(nc)  # local dev version, different from upstream

with open('README') as f:
    long_description = f.read()

install_requires = [
    'PyYAML',
    'plumbum',
    'habitica'  # this will be git until PR philadams/habitica#51 will be resolved
]
if sys.version_info < (3, 5):
    install_requires.append('typing')
# =====
if __name__ == '__main__':
    setuptools.setup(
        name='habitica_planner',
        version=make_version('0.1.5'),
        url='https://github.com/ASMfreaK/habitica_planner',
        license='GPLv3',
        author='Pavel Pletenev',
        author_email='cpp.create@gmail.com',
        description='habitica_planner -- plan multiple recusive tasks with checklists',
        long_description="""
        habitica_planner
        ================
        Simple Python script to upload multiple tasks to Habitica.
        """,
        platforms='any',

        packages=[
            'habitica_planner'
        ],

        entry_points={
            'console_scripts': [
                'habitica_planner = habitica_planner:main',
            ],
        },

        install_requires=install_requires,

        package_data={
            '': ['README'],
            'habitica_planner': [
                'i18n/*/LC_MESSAGES/*.mo'
            ]
        },

        classifiers=[
            'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
            'Development Status :: 4 - Beta',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Utilities',
            'Operating System :: POSIX :: Linux'
        ],

    )
