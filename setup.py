# Copyright 2022 Brian Johnson
#
# This file is part of brianiac
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

from setuptools import setup

setup(name='brianiac',
      version='0.4',
      description='Python CPU emulator and assembler for custom CPU',
      classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: POSIX :: Linux',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python :: 3 :: Only',
      ],
      keywords='cpu emulator assembler',
      url='http://github.com/brijohn/brianiac',
      author='Brian Johnson',
      author_email='brijohn@gmail.com',
      license='GPLv2',
      packages=['brianiac.assembler', 'brianiac.emulator'],
      install_requires=[
          'rply',
          'click',
          'click_shell',
      ],
      entry_points={
          'console_scripts': ['brianiac-emu=brianiac.emulator.__main__:main',
                              'brianiac-asm=brianiac.assembler.__main__:main'],
      },
      zip_safe=False)
