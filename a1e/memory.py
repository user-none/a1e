# Copyright (C) 2025 John Schember <john@nachtimwald.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from collections.abc import Callable

from .constants import RAM_SIZE, ROM_SIZE

class Memory():

    def __init__(self, rom_start: int = 0xF000):
        self.data = bytearray(RAM_SIZE)
        self._io_handlers = {}
        self._rom_start = rom_start

    def reset_vector(self):
        self.data[0xFFFC] = self._rom_start & 0xFF
        self.data[0xFFFD] = (self._rom_start >> 8) & 0xFF

    def map_io(self, addr: int, read: Callable[[], None] | None = None , write: Callable[[], None] | None = None):
        self._io_handlers[addr] = (read, write)

    def load_data(self, data: bytes, start: int = 0x2000):
        dlen = len(data)
        if dlen > (RAM_SIZE - start):
            raise Exception('Data too large')
        self.data[start:start + dlen] = bytes(data)

    def read(self, addr: int) -> int:
        addr &= 0xFFFF
        if addr in self._io_handlers:
            read, _ = self._io_handlers[addr]
            if read:
                return read()
        return self.data[addr]

    def write(self, addr: int, val: int) -> None:
        addr &= 0xFFFF

        # ROM is read only
        if self._rom_start <= addr <= 0xFFFF:
            return

        val &= 0xFF
        if addr in self._io_handlers:
            _, write = self._io_handlers[addr]
            if write:
                write(val)
                return
        self.data[addr] = val
