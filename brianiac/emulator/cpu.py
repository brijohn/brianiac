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

from brianiac.emulator.alu import ALU
from brianiac.emulator.registers import Registers
from brianiac.emulator.decoder import Opcode
import signal


class MemoryAccessError(Exception):
    pass


class CPU(object):
    def __init__(self):
        self.registers = Registers()
        self.alu = ALU()
        self.memory_map = {}

    def reset(self):
        self.registers.reset()
        self.ALU.reset()

#   Memory Map Functions
    def map(self, start, end, device):
        def overlap(start1, end1, start2, end2):
            return end1 >= start2 and end2 >= start1

        for r in self.memory_map:
            if overlap(start, end, r.start, r.stop-1):
                raise ValueError("Overlapping memory ranges")

        r = range(start, end+1)
        self.memory_map[r] = device

    def _lookup_memory_handler(self, address):
        for r in self.memory_map:
            if address in r:
                return (self.memory_map[r], address - r.start)
        return (None, 0)

    def readu8(self, address):
        handler, offset = self._lookup_memory_handler(address)
        if handler and hasattr(handler, "readu8"):
            return handler.readu8(offset)
        return 0xff

    def readu16(self, address):
        handler, offset = self._lookup_memory_handler(address)
        if offset % 2 != 0:
            raise MemoryAccessError(f"offset 0x{offset:02x} is not word aligned")
        if handler and hasattr(handler, "readu16"):
            return handler.readu16(offset)
        return 0xffff

    def writeu8(self, address, value):
        handler, offset = self._lookup_memory_handler(address)
        if handler and hasattr(handler, "writeu8"):
            handler.writeu8(offset, value)

    def writeu16(self, address, value):
        handler, offset = self._lookup_memory_handler(address)
        if offset % 2 != 0:
            raise MemoryAccessError(f"offset 0x{offset:02x} is not word aligned")
        if handler and hasattr(handler, "writeu16"):
            handler.writeu16(offset, value)

#   CPU Cycle Functions
    def fetch(self):
        data = self.readu16(self.registers.pc)
        self.registers.pc += 2
        return data

    def decode(self, inst):
        op = Opcode(inst)
        if op.immediate:
            self.registers.immediate = self.readu16(self.registers.pc)
            self.registers.pc += 2
        return op

    def execute(self, opcode):
        if opcode._grp == 0b001:
            self.ALU(opcode)
        else:
            func = getattr(self, opcode.instruction)
            func(opcode)

    def step(self):
        try:
            signal.pthread_sigmask(signal.SIG_BLOCK, [signal.SIGINT])
            inst = self.fetch()
            opcode = self.decode(inst)
            self.execute(opcode)
        finally:
            signal.pthread_sigmask(signal.SIG_UNBLOCK, [signal.SIGINT])

#   Instructions
    def NOP(self, opcode):
        pass

    def ALU(self, opcode):
        if opcode.immediate:
            src = self.registers.immediate
        else:
            src = self.registers.get(opcode.rm)
        rn = self.registers.get(opcode.rn)
        val, status = self.alu.execute(opcode._func, rn, src)
        self.registers.status = status
        if opcode._func not in (0b1000, 0b1001):
            self.registers.set(opcode.rn, val)

    def MOV(self, opcode):
        if opcode.immediate:
            src = self.registers.immediate
        else:
            src = self.registers.get(opcode.rm)
        self.registers.set(opcode.rn, src)

    def LDW(self, opcode):
        if opcode.immediate:
            src = self.registers.immediate
        else:
            src = self.registers.get(opcode.rm)
        data = self.readu16(src)
        self.registers.set(opcode.rn, data)

    def LDB(self, opcode):
        if opcode.immediate:
            src = self.registers.immediate
        else:
            src = self.registers.get(opcode.rm)
        data = self.readu8(src)
        self.registers.set(opcode.rn, data)

    def STW(self, opcode):
        if opcode.immediate:
            dst = self.registers.immediate
        else:
            dst = self.registers.get(opcode.rn)
        data = self.registers.get(opcode.rm)
        self.writeu16(dst, data & 0xffff)

    def STB(self, opcode):
        if opcode.immediate:
            dst = self.registers.immediate
        else:
            dst = self.registers.get(opcode.rn)
        data = self.registers.get(opcode.rm)
        self.writeu8(dst, data & 0xff)

    def BRA(self, opcode):
        if opcode.immediate:
            dst = self.registers.immediate
        else:
            dst = self.registers.get(opcode.rm)
        self.registers.pc = dst

    def BZ(self, opcode):
        if self.registers.status & 2:
            if opcode.immediate:
                dst = self.registers.immediate
            else:
                dst = self.registers.get(opcode.rm)
            self.registers.pc = dst

    def BNZ(self, opcode):
        if not (self.registers.status & 2):
            if opcode.immediate:
                dst = self.registers.immediate
            else:
                dst = self.registers.get(opcode.rm)
            self.registers.pc = dst

    def BC(self, opcode):
        if self.registers.status & 1:
            if opcode.immediate:
                dst = self.registers.immediate
            else:
                dst = self.registers.get(opcode.rm)
            self.registers.pc = dst

    def BNC(self, opcode):
        if not (self.registers.status & 1):
            if opcode.immediate:
                dst = self.registers.immediate
            else:
                dst = self.registers.get(opcode.rm)
            self.registers.pc = dst

    def CALL(self, opcode):
        if opcode.immediate:
            dst = self.registers.immediate
        else:
            dst = self.registers.get(opcode.rm)
        self.registers.set(15, self.registers.pc)
        self.registers.pc = dst

    def RET(self, opcode):
        self.registers.pc = self.registers.get(15)
