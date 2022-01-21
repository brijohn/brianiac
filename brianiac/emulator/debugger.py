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

from brianiac.emulator.rom import ROM
from brianiac.emulator.ram import RAM
from brianiac.emulator.serial import Serial
from brianiac.emulator.cpu import CPU
from brianiac.emulator.decoder import Opcode, DecodeError


class Debugger(object):
    def __init__(self, romfile):
        self.breakpoints = []
        self.cpu = CPU()
        self.cpu.map(0x0000, 0x1fff, ROM(0x2000, romfile))
        self.cpu.map(0x2000, 0xefff, RAM(0xD000))
        self.cpu.map(0xf000, 0xf001, Serial())

    def disassemble(self, pc=None):
        if pc is None:
            pc = self.cpu.registers.pc
        op = Opcode(self.cpu.readu16(pc))
        try:
            name = op.instruction
        except DecodeError:
            return f"DEFW 0x{op.word:04X}"
        imm = None
        if op.immediate:
            imm = self.cpu.readu16(pc + 2)
        if name in ("ADD", "SUB", "AND", "OR", "XOR", "CP", "TEST"):
            if imm is None:
                return f"{name} R{op.rn}, R{op.rm}"
            else:
                return f"{name} R{op.rn}, 0x{imm:04X}"
        elif name in ("NOT", "SHL", "SHR"):
            return f"{name} R{op.rn}"
        elif name in ("LDB", "LDW", "MOV"):
            at = "" if name == "MOV" else "@"
            if imm is None:
                return f"{name} R{op.rn}, {at}R{op.rm}"
            else:
                return f"{name} R{op.rn}, 0x{imm:04X}"
        elif name in ("STB", "STW"):
            if imm is None:
                return f"{name} @R{op.rn}, R{op.rm}"
            else:
                return f"{name} 0x{imm:04X}, R{op.rm}"
        elif name in ("BRA", "BZ", "BNZ", "BC", "BNC", "CALL"):
            if imm is None:
                return f"{name} @R{op.rm}"
            else:
                return f"{name} 0x{imm:04X}"
        else:
            return name

    def set_breakpoint(self, address):
        if address not in self.breakpoints:
            self.breakpoints.append(address)

    def del_breakpoint(self, address):
        if address in self.breakpoints:
            self.breakpoints.remove(address)

    def list_breakpoints(self):
        for idx, val in enumerate(self.breakpoints):
            print(f"{idx}: {val:04X}")

    def registers(self):
        print(f" PC: {self.cpu.registers.pc:04X}  {self.disassemble()}")
        print(f" ST: {self.cpu.registers.status:04X}")
        for index in range(0, 16):
            if index < 10:
                regstr = f" R{index}: {self.cpu.registers.get(index):04X}"
            else:
                regstr = f"R{index}: {self.cpu.registers.get(index):04X}"
            if index & 3 == 3:
                print(regstr)
            else:
                print(regstr, end=' ')

    def list(self, pc=None, count=None):
        if pc is None:
            pc = self.cpu.registers.pc
        if count is None:
            count = 16
        for _ in range(0, count):
            instruction = self.disassemble(pc)
            print(f"{pc:04X}: {instruction}")
            if "0x" in instruction and "DEFW" not in instruction:
                pc += 4
            else:
                pc += 2

    def step(self):
        self.cpu.step()
        self.registers()

    def next(self):
        def opcode_name():
            pc = self.cpu.registers.pc
            op = Opcode(self.cpu.readu16(pc))
            try:
                return op.instruction
            except DecodeError:
                return None

        if opcode_name() == "CALL":
            depth = 0
            self.cpu.step()
            while (name := opcode_name()) != "RET" or depth != 0:
                if (self.cpu.registers.pc in self.breakpoints):
                    break
                if name == "CALL":
                    depth += 1
                if name == "RET":
                    depth -= 1
                self.cpu.step()
            if self.cpu.registers.pc not in self.breakpoints:
                self.cpu.step()
        else:
            self.cpu.step()
        self.registers()

    def reset(self):
        self.cpu.reset()
        self.run()

    def run(self):
        self.cpu.step()
        while True:
            if (self.cpu.registers.pc in self.breakpoints):
                break
            self.cpu.step()
        self.registers()

    def memory_dump(self, start, end):
        def get_char(byte):
            return chr(byte) if byte >= 32 and byte < 127 else '.'

        for idx in range(0, end - start, 16):
            print(f"{start+idx:04X}:", end='')
            len = min(end-(start+idx), 16)
            ascii = ""
            for address in range(start+idx, start+idx+len):
                data = self.cpu.readu8(address)
                ascii = ascii + get_char(data)
                print(f" {data:02X}", end='')
            print(f"{'   '*(16-len)} {ascii}")
