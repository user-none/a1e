# Copyright (C) 2025 John Schember <john@nachtimwald.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from ..memory import Memory
from .opcodes import opcode_table

class CPU6502():

    def __init__(self, mem: Memory):
        self.mem = mem
        self._opcode_table = opcode_table
        self.reset()

    def reset(self) -> None:
        # Apple 1 reset vector is usually at FFFC/FFFD
        self.mem.reset_vector()
        lo = self.mem.read(0xFFFC)
        hi = self.mem.read(0xFFFD)
        self.PC = (hi << 8) | lo

        # 6502 Registers
        self.A = 0 # accumulator
        self.X = 0 # X register
        self.Y = 0 # Y register
        self.SP = 0xFF # stack pointer
        self.P = 0x20  # status register

    def step(self) -> int:
        opcode = self.mem.data[self.PC]
        oplen, func = self._opcode_table[opcode]

        operands = [self.mem.data[(self.PC + i) & 0xFFFF] for i in range(1, oplen)]

        #print(f'PC = {self.PC:04X}, opcode = {opcode:02X}, operands = {operands}')

        self.PC = (self.PC + oplen) & 0xFFFF

        # returns the number of cycles the operation used
        return func(self, operands)
