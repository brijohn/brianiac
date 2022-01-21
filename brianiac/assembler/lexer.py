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

from rply import LexerGenerator


class Lexer():
    def __init__(self):
        self.lexer = LexerGenerator()
        self.__add_tokens()

    def __add_tokens(self):
        self.lexer.add("ADD", "add")
        self.lexer.add("SUB", "sub")
        self.lexer.add("AND", "and")
        self.lexer.add("OR", "or")
        self.lexer.add("XOR", "xor")
        self.lexer.add("CP", "cp")
        self.lexer.add("TEST", "test")
        self.lexer.add("NOT", "not")
        self.lexer.add("SHR", "shr")
        self.lexer.add("SHL", "shl")
        self.lexer.add("LDW", "ldw")
        self.lexer.add("LDB", "ldb")
        self.lexer.add("STW", "stw")
        self.lexer.add("STB", "stb")
        self.lexer.add("MOV", "mov")
        self.lexer.add("BRA", "bra")
        self.lexer.add("BZ", "bz")
        self.lexer.add("BNZ", "bnz")
        self.lexer.add("BC", "bc")
        self.lexer.add("BNC", "bnc")
        self.lexer.add("CALL", "call")
        self.lexer.add("RET", "ret")
        self.lexer.add("DEFB", "defb")
        self.lexer.add("DEFN", "defn")
        self.lexer.add("EQU", "equ")
        self.lexer.add("COMMA", ",")
        self.lexer.add("COLON", ":")
        self.lexer.add("NEWLINE", "\n")
        self.lexer.add("REGISTER", r"r1[0-5]|r[0-9]")
        self.lexer.add("INDIRECT", r"@r1[0-5]|@r[0-9]")
        self.lexer.add("BINARY", r"0b[01]+")
        self.lexer.add("OCTAL", r"0o[0-7]+")
        self.lexer.add("HEXIDECIMAL", r"0x[a-f0-9]+")
        self.lexer.add("DECIMAL", r"[0-9]+")
        self.lexer.add("IDENTIFIER", r"[a-z][a-z0-9]+")

        self.lexer.ignore("[ \t]+")

    def get_lexer(self):
        return self.lexer.build()
