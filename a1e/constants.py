# Copyright (C) 2025 John Schember <john@nachtimwald.com>
# SPDX-License-Identifier: GPL-3.0-or-later

ROM_SIZE  = 0x0100
RAM_SIZE  = 0x10000

KBD_DATA = 0xD010  # Memory address accessed when reading the keyboard
KBD_CTRL = 0xD011  # Control register, b7 set if key pressed

VIDEO_ADDR = 0xD012  # Memory address written to for writing a character to the screen
SCREEN_COLS = 40

CPU_HZ = 1_000_000  # Apple 1 1 MHz CPU
FPS = 60
CYCLES_PER_FRAME = CPU_HZ // FPS
FRAME_TIME = 1.0 / FPS
