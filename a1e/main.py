# Copyright (C) 2025 John Schember <john@nachtimwald.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import sys

from a1e.emulator import A1E

def parse_args():
    parser = argparse.ArgumentParser(prog='Apple 1 Emulator', description='A simple Apple 1 emulator')
    parser.register('type', 'hex_int', lambda s: int(s, 16))
    parser.add_argument('-m', '--monitor_rom', help='Monitor ROM to load and run')
    parser.add_argument('-s', '--monitor_start', default=0xF000, type='hex_int', help='Start offset for the Monitor ROM as a hex int. The reset vector will be initialized to this value')
    parser.add_argument('-p', '--program_data', help='Program data to load')
    parser.add_argument('-d', '--program_start', default=0x2000, type='hex_int', help='Start offset for the program data as a hex int')
    return parser.parse_args()

def load_data(emu: A1E, path: str, start: int) -> None:
    with open(path, 'rb') as f:
        data = f.read()
    emu.load_data(data, start)

def main() -> None:
    args = parse_args()
    emu = A1E(args.monitor_start)

    if args.monitor_rom:
        load_data(emu, args.monitor_rom, args.monitor_start)

    if args.program_data:
        load_data(emu, args.program_data, args.program_start)

    try:
        emu.run()
    except KeyboardInterrupt:
        print('\n[EXIT]')
    except Exception as e:
        print(f'Error: {e}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
