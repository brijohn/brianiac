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

class RAM(object):
    def __init__(self, size):
        self._memory = [0 for _ in range(size)]

    def readu8(self, offset):
        return self._memory[offset]

    def readu16(self, offset):
        return (self._memory[offset] << 8) | self._memory[offset+1]

    def writeu8(self, offset, value):
        self._memory[offset] = value & 0xff

    def writeu16(self, offset, value):
        self._memory[offset] = (value >> 8) & 0xff
        self._memory[offset+1] = value & 0xff
