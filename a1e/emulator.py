# Copyright (C) 2025 John Schember <john@nachtimwald.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import time

from .cpu.core import CPU6502
from .memory import Memory
from .video import Video
from .keyboard import Keyboard
from .constants import KBD_DATA, KBD_CTRL, VIDEO_ADDR, CYCLES_PER_FRAME, FRAME_TIME 

class A1E():

    def __init__(self, monitor_addr: int):
        self.mem = Memory(monitor_addr)

    def load_data(self, data, start):
        self.mem.load_data(data, start)

    def run(self) -> None:
        video = Video()
        keyboard = Keyboard()

        self.mem.map_io(VIDEO_ADDR, None, video.write_char)
        self.mem.map_io(KBD_DATA, keyboard.read_char, None)
        self.mem.map_io(KBD_CTRL, keyboard.read_status, None)

        cpu = CPU6502(self.mem)
        cpu.reset()

        try:
            emu_time = time.perf_counter()
            while True:
                cycles = 0
                while cycles < CYCLES_PER_FRAME:
                    keyboard.poll()
                    cycles += cpu.step()

                emu_time += FRAME_TIME
                now = time.perf_counter()
                if emu_time > now:
                    time.sleep(emu_time - now)
        finally:
            keyboard.cleanup()
