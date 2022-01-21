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

import pty
import os
import select


class Serial(object):
    def __init__(self):
        (master, slave) = pty.openpty()
        self.poll = select.poll()
        self.poll.register(master, select.POLLIN | select.POLLHUP)
        slavename = os.ttyname(slave)
        os.close(slave)
        self.fd = master
        print(f"Slave PTY: {slavename}")

    def readu8(self, offset):
        if offset == 0:
            for event in self.poll.poll(1):
                if event[0] == self.fd and (event[1] & select.POLLIN):
                    return 1
            return 0
        elif offset == 1:
            data = os.read(self.fd, 1)
            return ord(data)
        return 0xff

    def writeu8(self, offset, value):
        if offset == 1:
            os.write(self.fd, (value & 0xff).to_bytes(1, 'big'))
