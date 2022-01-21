# Copyright 2021,2022 Brian Johnson
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

import re
import struct
from enum import Enum


class Program:
    def __init__(self):
        self.pc = 0
        self.instructions = []
        self.labels = {}

    def add_statement(self, statement):
        if isinstance(statement, (Data, OpCode)):
            if isinstance(statement, OpCode) and (self.pc % 2) != 0:
                raise Exception(f"{statement} is not aligned, current addreess is {self.pc}")
            self.instructions.append(statement)
            self.pc += statement.size()
        elif isinstance(statement, Label):
            if statement.value in self.labels:
                raise ValueError(f"Duplicate symbol: {statement.value}")
            self.labels[statement.name] = self.pc if statement.value is None else statement.value
        else:
            if not (hasattr(statement, "gettokentype") and statement.gettokentype() == "NEWLINE"):
                raise ValueError(f"{statement} is an invalid statement")

    def eval(self):
        ret = []
        pc = 0
        for inst in self.instructions:
            bytecode = inst.eval(self.labels)
            packed = struct.pack(f"{len(bytecode)}B", *bytecode)
            print(f"{pc:04X}: {bytearray(bytecode).hex().upper():<8}  {inst}")
            ret.append(packed)
            pc += inst.size()
        if self.labels:
            print("\n----Symbol Table----")
            max_len = len(max(self.labels.keys(), key=len))
            for label in self.labels:
                print(f"{label + ' ' * (max_len- len(label))}  =  0x{self.labels[label]:04X}")
        return b"".join(ret)


class Number:
    class Base(Enum):
        BINARY = 1
        OCTAL = 2
        HEX = 3
        DEC = 4

    def __init__(self, value, max):
        self.name = value
        if (match := re.match(r"^0x([a-fA-F0-9]+)", self.name)):
            self.type = self.Base.HEX
            self.value = int(match.group(1), 16)
        elif (match := re.match(r"^0o([0-7]+)", self.name)):
            self.type = self.Base.OCTAL
            self.value = int(match.group(1), 8)
        elif (match := re.match(r"^0b([01]+)", self.name)):
            self.type = self.Base.BINARY
            self.value = int(match.group(1), 2)
        elif (match := re.match(r"^([0-9]+)", self.name)):
            self.type = self.Base.DEC
            self.value = int(match.group(1))
        else:
            raise ValueError(f"{self.name} is not a valid number")

        if self.value > max:
            raise ValueError(f"{self.name} out of range")

    def eval(self):
        return self.value

    def __repr__(self):
        if self.type == self.Base.HEX:
            return f"0x{self.value:>02x}"
        if self.type == self.Base.BINARY:
            return f"0b{self.value:>08b}"
        if self.type == self.Base.OCTAL:
            return f"0o{self.value:>03o}"
        return f"{self.value}"


class Byte(Number):
    def __init__(self, value):
        super().__init__(value, 0xff)


class Word(Number):
    def __init__(self, value):
        super().__init__(value, 0xffff)


class Identifier:
    def __init__(self, name):
        self.name = name


class Label(Identifier):
    def __init__(self, name, value=None):
        super().__init__(name)
        self.value = value


class Register:
    def __init__(self, register):
        self.name = register
        index = re.match(r"^@?r(\d{1,2})$", self.name)
        if index:
            self.index = int(index.group(1))
            if self.index > 15:
                raise ValueError(f"{self.name} is not a valid register")
        else:
            raise ValueError(f"{self.name} is not a valid register")

    def eval(self):
        return self.index


class Data:
    def __init__(self):
        self.data = []

    def size(self):
        return len(self.data)

    def eval(self, dummy=None):
        return [x.eval() for x in self.data]


class DataFill(Data):
    def __init__(self, value, len):
        super().__init__()
        self.value = value
        self.len = len
        self.data = [value] * len.value

    def __repr__(self):
        return f"defn {self.value}, {self.len}"


class DataBytes(Data):
    def add_byte(self, byte):
        self.data.append(byte)

    def __repr__(self):
        return f"defb {', '.join([str(x) for x in self.data])}"


class OpCode:
    def __init__(self, operand1=None, operand2=None):
        self.operand1 = operand1
        self.operand2 = operand2
        self.has_immediate = any(isinstance(x, (Word, Identifier)) for x in (operand1, operand2))

    def size(self):
        return 4 if self.has_immediate else 2

    def eval(self, labels):
        imm = None
        opcode = self.opcode()
        if isinstance(self.operand1, (Word, Identifier)):
            if isinstance(self.operand1, Identifier):
                if self.operand1.name in labels:
                    imm = labels[self.operand1.name]
                else:
                    raise ValueError(f"{self.operand1.name} is not defined")
            else:
                imm = self.operand1.eval()
        elif isinstance(self.operand2, (Word, Identifier)):
            if isinstance(self.operand2, Identifier):
                if self.operand2.name in labels:
                    imm = labels[self.operand2.name]
                else:
                    raise ValueError(f"{self.operand2.name} is not defined")
            else:
                imm = self.operand2.eval()
        operand = (self.operand1.eval() if isinstance(self.operand1, Register) else 0) << 4
        operand |= (self.operand2.eval() if isinstance(self.operand2, Register) else 0)
        return [opcode, operand] if imm is None else [opcode | 0x01, operand, (imm >> 8) & 0xff, (imm & 0xff)]


class Add(OpCode):
    def opcode(self):
        return 0x20

    def __repr__(self):
        return f"add {self.operand1.name}, {self.operand2.name}"


class Sub(OpCode):
    def opcode(self):
        return 0x22

    def __repr__(self):
        return f"sub {self.operand1.name}, {self.operand2.name}"


class And(OpCode):
    def opcode(self):
        return 0x24

    def __repr__(self):
        return f"and {self.operand1.name}, {self.operand2.name}"


class Or(OpCode):
    def opcode(self):
        return 0x26

    def __repr__(self):
        return f"or {self.operand1.name}, {self.operand2.name}"


class Xor(OpCode):
    def opcode(self):
        return 0x28

    def __repr__(self):
        return f"xor {self.operand1.name}, {self.operand2.name}"


class Not(OpCode):
    def opcode(self):
        return 0x2a

    def __repr__(self):
        return f"not {self.operand1.name}"


class Shr(OpCode):
    def opcode(self):
        return 0x2c

    def __repr__(self):
        return f"shr {self.operand1.name}"


class Shl(OpCode):
    def opcode(self):
        return 0x2e

    def __repr__(self):
        return f"shl {self.operand1.name}"


class Cp(OpCode):
    def opcode(self):
        return 0x30

    def __repr__(self):
        return f"cp {self.operand1.name}, {self.operand2.name}"


class Test(OpCode):
    def opcode(self):
        return 0x32

    def __repr__(self):
        return f"test {self.operand1.name}, {self.operand2.name}"


class Ldw(OpCode):
    def opcode(self):
        return 0x60

    def __repr__(self):
        return f"ldw {self.operand1.name}, {self.operand2.name}"


class Ldb(OpCode):
    def opcode(self):
        return 0x70

    def __repr__(self):
        return f"ldb {self.operand1.name}, {self.operand2.name}"


class Mov(OpCode):
    def opcode(self):
        return 0x62

    def __repr__(self):
        return f"mov {self.operand1.name}, {self.operand2.name}"


class Stw(OpCode):
    def opcode(self):
        return 0x64

    def __repr__(self):
        return f"stw {self.operand1.name}, {self.operand2.name}"


class Stb(OpCode):
    def opcode(self):
        return 0x74

    def __repr__(self):
        return f"stb {self.operand1.name}, {self.operand2.name}"


class Bra(OpCode):
    def opcode(self):
        return 0x40

    def __repr__(self):
        return f"bra {self.operand2.name}"


class Bz(OpCode):
    def opcode(self):
        return 0x42

    def __repr__(self):
        return f"bz {self.operand2.name}"


class Bnz(OpCode):
    def opcode(self):
        return 0x44

    def __repr__(self):
        return f"bnz {self.operand2.name}"


class Bc(OpCode):
    def opcode(self):
        return 0x46

    def __repr__(self):
        return f"bc {self.operand2.name}"


class Bnc(OpCode):
    def opcode(self):
        return 0x48

    def __repr__(self):
        return f"bnc {self.operand2.name}"


class Call(OpCode):
    def opcode(self):
        return 0x5c

    def __repr__(self):
        return f"call {self.operand2.name}"


class Ret(OpCode):
    def opcode(self):
        return 0x5e

    def __repr__(self):
        return "ret"
