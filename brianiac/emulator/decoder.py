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

class DecodeError(Exception):
    pass


class Opcode(object):
    instruction_map = {
            0b000: "NOP",
            0b001: {
                0b0000: "ADD",
                0b0001: "SUB",
                0b0010: "AND",
                0b0011: "OR",
                0b0100: "XOR",
                0b0101: "NOT",
                0b0110: "SHR",
                0b0111: "SHL",
                0b1000: "CP",
                0b1001: "TEST"
            },
            0b010: {
                0b0000: "BRA",
                0b0001: "BZ",
                0b0010: "BNZ",
                0b0011: "BC",
                0b0100: "BNC",
                0b1110: "CALL",
                0b1111: "RET"
            },
            0b011: {
                0b0000: "LDW",
                0b1000: "LDB",
                0b0001: "MOV",
                0b0010: "STW",
                0b1010: "STB"
            }
    }

    def __init__(self, instruction):
        instruction = instruction & 0xffff
        self.word = instruction
        self._grp = instruction >> 13
        self.immediate = True if instruction & 0x100 else False
        self._func = (instruction >> 9) & 0x0f
        self.rn = (instruction >> 4) & 0x0f
        self.rm = instruction & 0x0f

    @property
    def instruction(self):
        grp = Opcode.instruction_map.get(self._grp, None)
        if grp is None:
            raise DecodeError("Invalid instruction")
        if isinstance(grp, dict):
            inst = grp.get(self._func, None)
            if inst is None:
                raise DecodeError("Invalid instruction")
            return inst
        return grp
