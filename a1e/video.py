# Copyright (C) 2025 John Schember <john@nachtimwald.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import sys

from .constants import SCREEN_COLS

class Video():

    def __init__(self):
        self._col = 0

    def write_char(self, val: int) -> None:
        # Don't try to write anything to the screen is it's not a real character
        if val == 0:
            return

        # Strip off b7 which could have been was added from input
        # because Apple 1 key input would set this bit
        # Convert the value it to the equivelent printable character
        c = chr(val & 0x7F)

        if c in ('\r', '\n'):
            # Output a new line and reset the columns
            sys.stdout.write('\n')
            self._col = 0
        else:
            # Write the char and if we're at the end of a colum
            # print a new line so we can wrap
            sys.stdout.write(c)
            self._col += 1
            if self._col >= SCREEN_COLS:
                sys.stdout.write('\n')
                self._col = 0

        sys.stdout.flush()
