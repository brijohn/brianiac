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

import click
from click_shell import shell
from brianiac.emulator.debugger import Debugger


class BasedIntParamType(click.ParamType):
    name = "integer"

    def convert(self, value, param, ctx):
        if isinstance(value, int):
            return value

        try:
            if value[:2].lower() == "0x":
                return int(value[2:], 16)
            elif value[:1] == "0":
                return int(value, 8)
            return int(value, 10)
        except ValueError:
            self.fail(f"{value!r} is not a valid integer", param, ctx)


BASED_INT = BasedIntParamType()


@shell(prompt=">>")
@click.pass_context
def cli(ctx):
    print("Brianiac CPU emulator/debugger")
    ctx.obj.registers()


@cli.command()
@click.pass_context
def reset(ctx):
    """Resets CPU and starts running loaded ROM."""
    if click.confirm("Do you wish to restart the machine?"):
        ctx.obj.reset()


@cli.command()
@click.pass_context
def run(ctx):
    """Starts the CPU running or continues running after a breakpoint."""
    ctx.obj.run()


@cli.command()
@click.pass_context
def registers(ctx):
    """Shows the current content of CPU registers."""
    ctx.obj.registers()


@cli.command()
@click.pass_context
def step(ctx):
    """Executes the next instruction."""
    ctx.obj.step()


@cli.command()
@click.pass_context
def next(ctx):
    """Executes next instruction, but proceeds thouugh subroutines (CALL)."""
    ctx.obj.next()


@cli.command()
@click.argument("start", required=False, type=BASED_INT)
@click.argument("count", required=False, type=BASED_INT)
@click.pass_context
def list(ctx, **kwargs):
    """Dissassembles the next COUNT instructions starting at the address START"""
    ctx.obj.list(kwargs['start'], kwargs['count'])


@cli.command()
@click.argument("start", type=BASED_INT)
@click.argument("end", required=False, type=BASED_INT)
@click.pass_context
def memory(ctx, **kwargs):
    """Dumps the memory range given by START, END"""
    if kwargs['end'] is None:
        kwargs['end'] = kwargs['start'] + 256
    ctx.obj.memory_dump(kwargs['start'], kwargs['end'])


@cli.command(name="break")
@click.argument("address", required=False, type=BASED_INT)
@click.option("--delete", is_flag=True, help="Delete breakpoint")
@click.pass_context
def breakpoint(ctx, **kwargs):
    """Set, Delete, and List breakpoints."""
    if kwargs['address'] is None:
        ctx.obj.list_breakpoints()
    else:
        if kwargs['delete']:
            ctx.obj.del_breakpoint(kwargs['address'])
        else:
            ctx.obj.set_breakpoint(kwargs['address'])


@click.command()
@click.argument('rom')
def main(rom):
    """Brianiac CPU emulator/debugger"""
    debugger = Debugger(rom)
    cli.invoke(click.Context(cli, info_name=cli.name, obj=debugger))


if __name__ == "__main__":
    main()
