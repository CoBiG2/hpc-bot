#!/usr/bin/python3

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
try:
    from setuptools import setup
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup


class NotSupportedException(BaseException):
    pass


if float("{}.{}".format(sys.version_info.major, sys.version_info.minor)) < 3.8:
    raise NotSupportedException("Only Python 3.8 or higher is supported")


# Set some variables (PKGBUILD inspired)
VERSION = "0.1.1a"
URL = "https://github.com/CoBiG2/hpc-bot"


setup(
    name="hpc-bot",
    version=VERSION,
    packages=["hpc_bot",
              "hpc_bot.cogs",
              "hpc_bot.checks"],
    install_requires=["discord.py==1.3.*"],
    description="A discord bot to relay CoBiG2 HPC information.",
    url=URL,
    download_url="{0}/-/archive/{1}/hpc_bot-{1}.tar.gz".format(URL, VERSION),
    author="Kronopt",
    license="GPL3",
    classifiers=["Intended Audience :: Science/Research",
                 "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
                 "Natural Language :: English",
                 "Operating System :: POSIX :: Linux",
                 "Programming Language :: Python :: 3 :: Only",
                 "Programming Language :: Python :: 3.8"],
    entry_points={
        "console_scripts": [
            "hpc-bot = hpc_bot.hpc_bot:main",
        ]
    },
)
