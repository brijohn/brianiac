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

from rply import ParserGenerator
from brianiac.assembler.ast import (Program, Label, Identifier, Register, Byte, Word, DataFill,
                                    DataBytes, Add, Sub, And, Or, Xor, Cp, Test, Not, Shr, Shl,
                                    Ldw, Ldb, Stw, Stb, Mov, Bra, Bz, Bnz, Bc, Bnc, Call, Ret)


class Parser:
    def __init__(self):
        self.pg = ParserGenerator(["COLON", "COMMA", "NEWLINE", "REGISTER",
                                   "INDIRECT", "BINARY", "OCTAL", "HEXIDECIMAL", "DECIMAL", "IDENTIFIER", "EQU",
                                   "ADD", "SUB", "AND", "OR", "XOR", "CP", "TEST",
                                   "NOT", "SHR", "SHL", "LDW", "LDB", "STW",
                                   "STB", "MOV", "BRA", "BZ", "BNZ", "BC",
                                   "BNC", "CALL", "RET", "DEFB", "DEFN", "$end"])

    def bnf(self):
        @self.pg.production('program : program statement')
        @self.pg.production('program : statement')
        def program(p):
            if len(p) == 1:
                prog = Program()
                prog.add_statement(p[0])
                return prog
            p[0].add_statement(p[1])
            return p[0]

        @self.pg.production('statement : instruction eol')
        @self.pg.production('statement : label eol')
        @self.pg.production('statement : equ eol')
        @self.pg.production('statement : NEWLINE')
        def statement(p):
            return p[0]

        @self.pg.production('instruction : ADD register COMMA register')
        @self.pg.production('instruction : ADD register COMMA word')
        @self.pg.production('instruction : ADD register COMMA identifier')
        def add_op(p):
            return Add(p[1], p[3])

        @self.pg.production('instruction : SUB register COMMA register')
        @self.pg.production('instruction : SUB register COMMA word')
        @self.pg.production('instruction : SUB register COMMA identifier')
        def sub_op(p):
            return Sub(p[1], p[3])

        @self.pg.production('instruction : AND register COMMA register')
        @self.pg.production('instruction : AND register COMMA word')
        @self.pg.production('instruction : AND register COMMA identifier')
        def and_op(p):
            return And(p[1], p[3])

        @self.pg.production('instruction : OR register COMMA register')
        @self.pg.production('instruction : OR register COMMA word')
        @self.pg.production('instruction : OR register COMMA identifier')
        def or_op(p):
            return Or(p[1], p[3])

        @self.pg.production('instruction : XOR register COMMA register')
        @self.pg.production('instruction : XOR register COMMA word')
        @self.pg.production('instruction : XOR register COMMA identifier')
        def xor_op(p):
            return Xor(p[1], p[3])

        @self.pg.production('instruction : CP register COMMA register')
        @self.pg.production('instruction : CP register COMMA word')
        @self.pg.production('instruction : CP register COMMA identifier')
        def cp_op(p):
            return Cp(p[1], p[3])

        @self.pg.production('instruction : TEST register COMMA register')
        @self.pg.production('instruction : TEST register COMMA word')
        @self.pg.production('instruction : TEST register COMMA identifier')
        def test_op(p):
            return Test(p[1], p[3])

        @self.pg.production('instruction : NOT register')
        def not_op(p):
            return Not(p[1])

        @self.pg.production('instruction : SHR register')
        def shr_op(p):
            return Shr(p[1])

        @self.pg.production('instruction : SHL register')
        def shl_op(p):
            return Shl(p[1])

        @self.pg.production('instruction : LDW register COMMA word')
        @self.pg.production('instruction : LDW register COMMA identifier')
        @self.pg.production('instruction : LDW register COMMA indirect')
        def ldw_op(p):
            return Ldw(p[1], p[3])

        @self.pg.production('instruction : LDB register COMMA word')
        @self.pg.production('instruction : LDB register COMMA identifier')
        @self.pg.production('instruction : LDB register COMMA indirect')
        def ldb_op(p):
            return Ldb(p[1], p[3])

        @self.pg.production('instruction : STW word COMMA register')
        @self.pg.production('instruction : STW identifier COMMA register')
        @self.pg.production('instruction : STW indirect COMMA register')
        def stw_op(p):
            return Stw(p[1], p[3])

        @self.pg.production('instruction : STB word COMMA register')
        @self.pg.production('instruction : STB identifier COMMA register')
        @self.pg.production('instruction : STB indirect COMMA register')
        def stb_op(p):
            return Stb(p[1], p[3])

        @self.pg.production('instruction : MOV register COMMA register')
        @self.pg.production('instruction : MOV register COMMA word')
        @self.pg.production('instruction : MOV register COMMA identifier')
        def mov_op(p):
            return Mov(p[1], p[3])

        @self.pg.production('instruction : BRA word')
        @self.pg.production('instruction : BRA identifier')
        @self.pg.production('instruction : BRA indirect')
        def bra_op(p):
            return Bra(None, p[1])

        @self.pg.production('instruction : BZ word')
        @self.pg.production('instruction : BZ identifier')
        @self.pg.production('instruction : BZ indirect')
        def bz_op(p):
            return Bz(None, p[1])

        @self.pg.production('instruction : BNZ word')
        @self.pg.production('instruction : BNZ identifier')
        @self.pg.production('instruction : BNZ indirect')
        def bnz_op(p):
            return Bnz(None, p[1])

        @self.pg.production('instruction : BC word')
        @self.pg.production('instruction : BC identifier')
        @self.pg.production('instruction : BC indirect')
        def bc_op(p):
            return Bc(None, p[1])

        @self.pg.production('instruction : BNC word')
        @self.pg.production('instruction : BNC identifier')
        @self.pg.production('instruction : BNC indirect')
        def bnc_op(p):
            return Bnc(None, p[1])

        @self.pg.production('instruction : CALL word')
        @self.pg.production('instruction : CALL identifier')
        @self.pg.production('instruction : CALL indirect')
        def call_op(p):
            return Call(Register('r15'), p[1])

        @self.pg.production('instruction : RET')
        def ret_op(p):
            return Ret(None, Register('r15'))

        @self.pg.production('instruction : DEFN byte COMMA word')
        def defn(p):
            return DataFill(p[1], p[3])

        @self.pg.production('instruction : DEFB bytelist')
        def defb(p):
            return p[1]

        @self.pg.production('equ : identifier EQU word')
        def equ(p):
            return Label(p[0].name, p[2].eval())

        @self.pg.production('register : REGISTER')
        def register(p):
            return Register(p[0].value)

        @self.pg.production('indirect : INDIRECT')
        def indirect(p):
            return Register(p[0].value)

        @self.pg.production('bytelist : bytelist COMMA byte')
        @self.pg.production('bytelist : byte')
        def bytelist(p):
            if len(p) == 1:
                defb = DataBytes()
                defb.add_byte(p[0])
                return defb
            p[0].add_byte(p[2])
            return p[0]

        @self.pg.production('byte : BINARY')
        @self.pg.production('byte : OCTAL')
        @self.pg.production('byte : HEXIDECIMAL')
        @self.pg.production('byte : DECIMAL')
        def databyte(p):
            return Byte(p[0].value)

        @self.pg.production('word : BINARY')
        @self.pg.production('word : OCTAL')
        @self.pg.production('word : HEXIDECIMAL')
        @self.pg.production('word : DECIMAL')
        def dataword(p):
            return Word(p[0].value)

        @self.pg.production('label : IDENTIFIER COLON')
        def label(p):
            return Label(p[0].value)

        @self.pg.production('identifier : IDENTIFIER')
        def identifer(p):
            return Identifier(p[0].value)

        @self.pg.production('eol : NEWLINE')
        @self.pg.production('eol : $end')
        def eol(self):
            pass

        @self.pg.error
        def error_handler(token):
            raise ValueError(token)

    def get_parser(self):
        return self.pg.build()
