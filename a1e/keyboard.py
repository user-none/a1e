# Copyright (C) 2025 John Schember <john@nachtimwald.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import select
import termios
import tty

from .constants import *

class Keyboard():

    def __init__(self):
        # Save original terminal settings
        self._old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())

        self._key_pressed = 0
        self._kbdcr = 0

    def poll(self) -> None:
        if select.select([sys.stdin], [], [], 0)[0]:
            c = sys.stdin.read(1)
            self._key_pressed = ord(c) & 0x7F

            # Apple 1 keyboards usesd CR instead of LF for return press.
            # Convert to be compaitible.
            if self._key_pressed == 0x0A:
                self._key_pressed = 0x0D

            # Set the flag that a key was pressed
            self._kbdcr |= 0x80

    # Registered as an io handler for the KBD_DATA address
    def read_char(self) -> int:
        val = self._key_pressed
        self._key_pressed = 0

        # Clear the flag that a key was pressed
        self._kbdcr &= 0x7F

        # Apple 1 keyboards set b7 on input keys.
        # Add it to be compatible.
        return val | 0x80

    # Registered as teh io handler for the KBD_CTRL address
    def read_status(self) -> int:
        return self._kbdcr

    def cleanup(self) -> None:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self._old_settings)
