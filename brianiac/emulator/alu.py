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

from brianiac.emulator.decoder import Opcode, DecodeError


class ALU(object):
    def __init__(self):
        self.reset()

    def reset(self):
        self.status = 0

    def execute(self, func, rn, rm):
        status = 0
        op = Opcode.instruction_map[0b001].get(func, None)
        if op is None:
            raise DecodeError("Invalid ALU operation")
        function = getattr(self, op)
        r = function(rn & 0xffff, rm & 0xffff)
        if r == 0:
            status |= 2
        if r & 0x8000:
            status |= 4
        if func in (0, 1, 8):
            if r > 0xffff or r < 0:
                status |= 1
            if rn & 0x8000 == rm & 0x8000 and r & 0x8000 != rn & 0x8000:
                status |= 8
        self.status = status
        return r & 0xffff, status

    def ADD(self, rn, rm):
        r = rn + rm + (self.status & 1)
        return r

    def SUB(self, rn, rm):
        r = rn - rm - (self.status & 1)
        return r

    def AND(self, rn, rm):
        r = rn & rm
        return r

    def OR(self, rn, rm):
        r = rn | rm
        return r

    def XOR(self, rn, rm):
        r = rn ^ rm
        return r

    def NOT(self, rn, rm):
        r = ~rn
        return r

    def SHR(self, rn, rm):
        r = rn >> 1
        return r

    def SHL(self, rn, rm):
        r = rn << 1
        return r

    def CP(self, rn, rm):
        r = rn - rm
        return r

    def TEST(self, rn, rm):
        r = rn & rm
        return r
