#!/usr/bin/env python3
# coding: utf-8

# Copyright 2020 Francisco Pina Martins <f.pinamartins@gmail.com>
# This file is part of hpc-bot.
# hpc-bot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# hpc-bot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with hpc-bot. If not, see <http://www.gnu.org/licenses/>.

"""
hpc-bot setup
"""

import sys
from hpc_bot import hpc_bot
try:
    from setuptools import setup
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup


class NotSupportedException(BaseException):
    """Python version not supported"""


if float(f'{sys.version_info.major}.{sys.version_info.minor}') < 3.8:
    raise NotSupportedException('Only Python 3.8 or higher is supported')


def dynamic_datafiles():
    """
    Detect the platform and set systemd service file for installation if
    required.
    """

    data_files = []

    if sys.platform == 'linux':
        service_file = 'hpc_bot/systemd/hpc-bot.service'
        data_files.append(('share/systemd/user', [service_file]))

    return data_files


with open('README.md', encoding='utf-8') as readme_md,\
        open('requirements.txt', encoding='utf-8') as requirements_txt:
    readme = readme_md.read()
    requirements = [req[:req.find('#')].rstrip() for req in requirements_txt.readlines()]

setup(
    name='hpc-bot',
    version=hpc_bot.__version__,
    description=hpc_bot.__description__,
    long_description=readme,
    long_description_content_type='text/markdown',
    license=hpc_bot.__license__,
    author=hpc_bot.__author__,
    url=hpc_bot.__url__,
    # project_urls={'Documentation': '<documentation_url>'},
    packages=['hpc_bot',
              'hpc_bot.cogs',
              'hpc_bot.checks'],
    install_requires=requirements,
    keywords='discord-bot discord-py hpc-bot',
    download_url='{0}/-/archive/{1}/hpc_bot-{1}.tar.gz'.format(hpc_bot.__url__,
                                                               hpc_bot.__version__),
    classifiers=['Development Status :: 3 - Alpha',
                 'Intended Audience :: Science/Research',
                 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                 'Natural Language :: English',
                 'Operating System :: POSIX :: Linux',
                 'Programming Language :: Python :: 3 :: Only',
                 'Programming Language :: Python :: 3.8'],
    data_files=dynamic_datafiles(),
    entry_points={
        'console_scripts': [
            'hpc-bot = hpc_bot.hpc_bot:main',
        ]
    },
)
