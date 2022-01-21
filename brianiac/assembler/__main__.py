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

import click
from brianiac.assembler.lexer import Lexer
from brianiac.assembler.parser import Parser
import os
import re


def split_bytecode(bytecode):
    return bytecode[0::2], bytecode[1::2]


@click.command()
@click.argument("source", type=str)
@click.argument("destination", type=str)
@click.option("--split", is_flag=True, help="Splits file into high and low byte banks")
def main(source, destination, split):
    """
    Brianiac 16bit Assembler
    """

    filename, ext = os.path.splitext(destination)

    lexer = Lexer().get_lexer()
    with open(source) as f:
        lines = []
        for line in f:
            lines.append(re.sub(r"^([^;]*);.*(\n?)$", r"\1\2", line))
        tokens = lexer.lex("".join(lines))
        pg = Parser()
        pg.bnf()
        parser = pg.get_parser()
        result = parser.parse(tokens)
        if split:
            hi, lo = split_bytecode(result.eval())
            with open(f"{filename}_hi{ext}", "wb") as w:
                w.write(hi)
            with open(f"{filename}_lo{ext}", "wb") as w:
                w.write(lo)
        else:
            with open(f"{filename}{ext}", "wb") as w:
                w.write(result.eval())


if __name__ == "__main__":
    main()
