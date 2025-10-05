import unittest

from a1e.cpu.core import CPU6502
from a1e.memory import Memory

START  = 0x0200
FLAG_C = 0x01
FLAG_Z = 0x02
FLAG_I = 0x04
FLAG_D = 0x08
FLAG_B = 0x10
FLAG_U = 0x20
FLAG_V = 0x40
FLAG_N = 0x80

# Test cases for all official 6502 opcodes
# Each entry: (name, program bytes, expected cycles, setup lambda, expected lambda)
# Setup lambda modifies CPU/mem before execution
# Expected lambda asserts CPU/mem state and cycles after execution

OPCODE_TESTS = [
    # ADC (Add with Carry)
    ('ADC_IMM', [0x69, 0x10], 2,
     lambda cpu, mem: setattr(cpu, 'A', 0x20),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0x30)
    ),
    ('ADC_ZP', [0x65, 0x10], 3,
     lambda cpu, mem: mem.write(0x0010, 0x20),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0x20)
    ),
    ('ADC_ZPX', [0x75, 0x10], 4,
     lambda cpu, mem: (mem.write(0x0015, 0x20), setattr(cpu, 'X', 0x05)),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0x20)
    ),
    ('ADC_ABS', [0x6D, 0x00, 0x20], 4,
     lambda cpu, mem: mem.write(0x2000, 0x30),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0x30)
    ),
    ('ADC_ABX', [0x7D, 0x00, 0x20], 4,
     lambda cpu, mem: (mem.write(0x2005, 0x40), setattr(cpu, 'X', 5)),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0x40)
    ),
    ('ADC_ABY', [0x79, 0x00, 0x20], 4,
     lambda cpu, mem: (mem.write(0x2005, 0x50), setattr(cpu, 'Y', 5)),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0x50)
    ),
    ('ADC_INDX', [0x61, 0x10], 6,
     lambda cpu, mem: (mem.write(0x1234, 0x60), mem.write(0x20, 0x34), mem.write(0x21, 0x12), setattr(cpu, 'X', 0x10)),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0x60)
    ),
    ('ADC_INDY', [0x71, 0x10], 5,
     lambda cpu, mem: (mem.write(0x2010, 0x70), mem.write(0x10, 0x00), mem.write(0x11, 0x20), setattr(cpu, 'Y', 0x10)),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0x70)
    ),
    ('ADC_IMM_DEC', [0x69, 0x27], 3,
     lambda cpu, mem: setattr(cpu, 'A', 0x45) or setattr(cpu, 'P', cpu.P | FLAG_D),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0x72)
    ),
    ('ADC_ZP_DEC', [0x65, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0x45), setattr(cpu, 'P', cpu.P | FLAG_D), mem.write(0x0010, 0x27)),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0x72)
    ),
    ('ADC_ZPX_DEC', [0x75, 0x10], 5,
     lambda cpu, mem: (setattr(cpu, 'A', 0x12), setattr(cpu, 'X', 0x05), setattr(cpu, 'P', cpu.P | FLAG_D), mem.write(0x0015, 0x27)),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0x39)
    ),
    ('ADC_ABS_DEC', [0x6D, 0x00, 0x20], 5,
     lambda cpu, mem: (setattr(cpu, 'A', 0x33), setattr(cpu, 'P', cpu.P | FLAG_D), mem.write(0x2000, 0x45)),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0x78)
    ),
    ('ADC_ABX_DEC', [0x7D, 0x00, 0x20], 5,
     lambda cpu, mem: (setattr(cpu, 'A', 0x12), setattr(cpu, 'X', 0x05), setattr(cpu, 'P', cpu.P | FLAG_D), mem.write(0x2005, 0x27)),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0x39)
    ),
    ('ADC_ABY_DEC', [0x79, 0x00, 0x20], 5,
     lambda cpu, mem: (setattr(cpu, 'A', 0x12), setattr(cpu, 'Y', 0x05), setattr(cpu, 'P', cpu.P | FLAG_D), mem.write(0x2005, 0x27)),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0x39)
    ),
    ('ADC_INDX_DEC', [0x61, 0x10], 7,
     lambda cpu, mem: (setattr(cpu, 'A', 0x10), setattr(cpu, 'X', 0x04), setattr(cpu, 'P', cpu.P | FLAG_D), mem.write(0x0014, 0x00), mem.write(0x0015, 0x20), mem.write(0x2000, 0x27)),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0x37)
    ),
    ('ADC_INDY_DEC', [0x71, 0x10], 6,
     lambda cpu, mem: (setattr(cpu, 'A', 0x10), setattr(cpu, 'Y', 0x05), setattr(cpu, 'P', cpu.P | FLAG_D), mem.write(0x0010, 0x00), mem.write(0x0011, 0x20), mem.write(0x2005, 0x27)),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0x37)
    ),

    # AND
    ('AND_IMM', [0x29, 0x0F], 2,
     lambda cpu, mem: setattr(cpu, 'A', 0xF0),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0xF0 & 0x0F)
    ),
    ('AND_ZP', [0x25, 0x10], 3,
     lambda cpu, mem: (setattr(cpu, 'A', 0xFF), mem.write(0x0010, 0x0F)),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0xFF & 0x0F)
    ),
    ('AND_ZPX', [0x35, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0xAA), setattr(cpu, 'X', 0x05), mem.write(0x0015, 0x0F)),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0xAA & 0x0F)
    ),
    ('AND_ABS', [0x2D, 0x00, 0x20], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0xFF), mem.write(0x2000, 0x0F)),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0xFF & 0x0F)
    ),
    ('AND_ABX', [0x3D, 0x00, 0x20], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0xAA), setattr(cpu, 'X', 0x05), mem.write(0x2005, 0x0F)),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0xAA & 0x0F)
    ),
    ('AND_ABY', [0x39, 0x00, 0x20], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0xCC), setattr(cpu, 'Y', 0x05), mem.write(0x2005, 0x0F)),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0xCC & 0x0F)
    ),
    ('AND_INDX', [0x21, 0x10], 6,
     lambda cpu, mem: (setattr(cpu, 'A', 0xFF), setattr(cpu, 'X', 0x04), mem.write(0x0014, 0x00), mem.write(0x0015, 0x20), mem.write(0x2000, 0x0F)),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0xFF & 0x0F)
    ),
    ('AND_INDY', [0x31, 0x10], 5,
     lambda cpu, mem: (setattr(cpu, 'A', 0xFF), setattr(cpu, 'Y', 0x05), mem.write(0x0010, 0x00), mem.write(0x0011, 0x20), mem.write(0x2005, 0x0F)),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0xFF & 0x0F)
    ),

    # ASL (Shift Left One Bit)
    ('ASL_A', [0x0A], 2,
     lambda cpu, mem: setattr(cpu, 'A', 0x42),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x84), t.assertFalse(cpu.P & FLAG_C), t.assertFalse(cpu.P & FLAG_Z), t.assertTrue(cpu.P & FLAG_N))
    ),
    ('ASL_ZP', [0x06, 0x10], 5,
     lambda cpu, mem: mem.write(0x0010, 0x42),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x0010), 0x84), t.assertFalse(cpu.P & FLAG_C), t.assertFalse(cpu.P & FLAG_Z), t.assertTrue(cpu.P & FLAG_N))
    ),
    ('ASL_ZPX', [0x16, 0x10], 6,
     lambda cpu, mem: (setattr(cpu, 'X', 0x05), mem.write(0x0015, 0x42)),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x0015), 0x84), t.assertFalse(cpu.P & FLAG_C), t.assertFalse(cpu.P & FLAG_Z), t.assertTrue(cpu.P & FLAG_N))
    ),
    ('ASL_ABS', [0x0E, 0x00, 0x20], 6,
     lambda cpu, mem: mem.write(0x2000, 0x42),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x2000), 0x84), t.assertFalse(cpu.P & FLAG_C), t.assertFalse(cpu.P & FLAG_Z), t.assertTrue(cpu.P & FLAG_N))
    ),
    ('ASL_ABX', [0x1E, 0x00, 0x20], 7,
     lambda cpu, mem: (setattr(cpu, 'X', 0x05), mem.write(0x2005, 0x42)),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x2005), 0x84), t.assertFalse(cpu.P & FLAG_C), t.assertFalse(cpu.P & FLAG_Z), t.assertTrue(cpu.P & FLAG_N))
    ),

    #BCC
    # Branch not taken (C flag set)
    ('BCC_NOT_TAKEN', [0x90, 0x02], 2,
     lambda cpu, mem: setattr(cpu, 'P', FLAG_C),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.PC, 0x0202)
    ),
    # Branch taken, same page (C flag clear, offset +2)
    ('BCC_TAKEN_NO_PAGE_CROSS', [0x90, 0x02]*20, 3,
     lambda cpu, mem: None,
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.PC, 0x0204)
    ),
    # Branch taken, page crossed (C flag clear, offset crosses page)
    ('BCC_TAKEN_PAGE_CROSS', ([0xEA] * (0x02FD - START)) + [0x90, 0x05], 4,
      lambda cpu, mem: setattr(cpu, 'PC', 0x02FD),
      lambda t, cpu, mem, cycles: t.assertEqual(cpu.PC, 0x0304)
    ),

    #BCS
    ('BCS_NOT_TAKEN', [0xB0, 0x02], 2,
     lambda cpu, mem: None,
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.PC, 0x0202)
    ),
    ('BCS_TAKEN_NO_PAGE_CROSS', [0xB0, 0x02], 3,
     lambda cpu, mem: setattr(cpu, 'P', FLAG_C),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.PC, 0x0204)
    ),
    ('BCS_TAKEN_PAGE_CROSS', [0xB0, 0xFC], 4,
     lambda cpu, mem: setattr(cpu, 'P', FLAG_C),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.PC, 0x01FE)
    ),

    # BEQ
    ('BEQ_NOT_TAKEN', [0xF0, 0x02], 2,
     lambda cpu, mem: None,
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.PC, 0x0202)
    ),
    ('BEQ_TAKEN_NO_PAGE_CROSS', [0xF0, 0x02], 3,
     lambda cpu, mem: setattr(cpu, 'P', FLAG_Z),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.PC, 0x0204)
    ),
    ('BEQ_TAKEN_PAGE_CROSS', [0xF0, 0xFC], 4,
     lambda cpu, mem: setattr(cpu, 'P', FLAG_Z),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.PC, 0x01FE)
    ),

    # BIT
    ('BIT_ZP', [0x24, 0x10], 3,
     lambda cpu, mem: mem.write(0x10, 0x80),
     lambda t, cpu, mem, cycles: t.assertTrue(cpu.P & FLAG_N)
    ),
    ('BIT_ABS', [0x2C, 0x00, 0x20], 4,
     lambda cpu, mem: mem.write(0x2000, 0x40),
     lambda t, cpu, mem, cycles: t.assertFalse(cpu.P & FLAG_N)
    ),

    # BMI
    ('BMI_NOT_TAKEN', [0x30, 0x02], 2,
     lambda cpu, mem: None,
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.PC, 0x0202)
    ),
    ('BMI_TAKEN_NO_PAGE_CROSS', [0x30, 0x02], 3,
     lambda cpu, mem: setattr(cpu, 'P', FLAG_N),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.PC, 0x0204)
    ),
    ('BMI_TAKEN_PAGE_CROSS', [0x30, 0xFC], 4,
     lambda cpu, mem: setattr(cpu, 'P', FLAG_N),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.PC, 0x01FE)
    ),

    # BNE
    ('BME_NOT_TAKEN', [0xD0, 0x02], 2,
     lambda cpu, mem: setattr(cpu, 'P', FLAG_Z),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.PC, 0x0202)
    ),
    ('BME_TAKEN_NO_PAGE_CROSS', [0xD0, 0x02], 3,
     lambda cpu, mem: None,
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.PC, 0x0204)
    ),
    ('BME_TAKEN_PAGE_CROSS', [0xD0, 0xFC], 4,
     lambda cpu, mem: None,
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.PC, 0x01FE)
    ),

    # BPL
    ('BPL_NOT_TAKEN', [0x10, 0x02], 2,
     lambda cpu, mem: setattr(cpu, 'P', FLAG_N),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.PC, 0x0202)
    ),
    ('BPL_TAKEN_NO_PAGE_CROSS', [0x10, 0x02], 3,
     lambda cpu, mem: None,
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.PC, 0x0204)
    ),
    ('BPL_TAKEN_PAGE_CROSS', [0x10, 0xFC], 4,
     lambda cpu, mem: None,
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.PC, 0x01FE)
    ),

    # BRK
    ('BRK', [0x00], 7,
     lambda cpu, mem: mem.load_data([0x00, 0x10], 0xFFFE),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.PC, 0x1000), t.assertTrue((cpu.P & FLAG_I) != 0), t.assertEqual(mem.read(0x01FF), 0x02), t.assertEqual(mem.read(0x01FE), 0x02), t.assertTrue((mem.read(0x01FD) & FLAG_B) != 0))
    ),

    # BVC
    ('BVC_NOT_TAKEN', [0x50, 0x02], 2,
     lambda cpu, mem: setattr(cpu, 'P', FLAG_V),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.PC, 0x0202)
    ),
    ('BVC_TAKEN_NO_PAGE_CROSS', [0x50, 0x02], 3,
     lambda cpu, mem: None,
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.PC, 0x0204)
    ),
    ('BVC_TAKEN_PAGE_CROSS', [0x50, 0xFC], 4,
     lambda cpu, mem: None,
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.PC, 0x01FE)
    ),

    # BVS
    ('BVS_NOT_TAKEN', [0x70, 0x02], 2,
     lambda cpu, mem: None,
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.PC, 0x0202)
    ),
    ('BVS_TAKEN_NO_PAGE_CROSS', [0x70, 0x02], 3,
     lambda cpu, mem: setattr(cpu, 'P', FLAG_V),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.PC, 0x0204)
    ),
    ('BVS_TAKEN_PAGE_CROSS', [0x70, 0xFC], 4,
     lambda cpu, mem: setattr(cpu, 'P', FLAG_V),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.PC, 0x01FE)
    ),

    # CLC
    ('CLC_WHEN_CARRY_CLEAR', [0x18], 2,
     lambda cpu, mem: setattr(cpu, 'P', FLAG_Z),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, 0), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z))
    ),
    ('CLC_WHEN_CARRY_SET', [0x18], 2,
     lambda cpu, mem: setattr(cpu, 'P', FLAG_C | FLAG_N),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),

    # CLD
    ('CLD_WHEN_CARRY_CLEAR', [0xD8], 2,
     lambda cpu, mem: setattr(cpu, 'P', FLAG_Z),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_D, 0), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z))
    ),
    ('CLD_WHEN_CARRY_SET', [0xD8], 2,
     lambda cpu, mem: setattr(cpu, 'P', FLAG_D | FLAG_N),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_D, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),

    # CLI
    ('CLI_WHEN_CARRY_CLEAR', [0x58], 2,
     lambda cpu, mem: setattr(cpu, 'P', FLAG_Z),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_I, 0), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z))
    ),
    ('CLI_WHEN_CARRY_SET', [0x58], 2,
     lambda cpu, mem: setattr(cpu, 'P', FLAG_I | FLAG_N),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_I, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),

    # CLV
    ('CLV_WHEN_CARRY_CLEAR', [0xB8], 2,
     lambda cpu, mem: setattr(cpu, 'P', FLAG_Z),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_V, 0), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z))
    ),
    ('CLV_WHEN_CARRY_SET', [0xB8], 2,
     lambda cpu, mem: setattr(cpu, 'P', FLAG_V | FLAG_N),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_V, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),

    #CMP
    ('CMP_IMMEDIATE_LESS', [0xC9, 0x05], 2,
     lambda cpu, mem: setattr(cpu, 'A', 0x03),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, 0), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('CMP_IMMEDIATE_EQUAL', [0xC9, 0x05], 2,
     lambda cpu, mem: setattr(cpu, 'A', 0x05),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, FLAG_C), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('CMP_IMMEDIATE_GREATER', [0xC9, 0x05], 2,
     lambda cpu, mem: setattr(cpu, 'A', 0x08),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, FLAG_C), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('CMP_ZEROPAGE_LESS', [0xC5, 0x10], 3,
     lambda cpu, mem: (setattr(cpu, 'A', 0x03), mem.write(0x10, 0x05)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, 0), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('CMP_ZEROPAGE_EQUAL', [0xC5, 0x10], 3,
     lambda cpu, mem: (setattr(cpu, 'A', 0x05), mem.write(0x10, 0x05)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, FLAG_C), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('CMP_ZEROPAGE_GREATER', [0xC5, 0x10], 3,
     lambda cpu, mem: (setattr(cpu, 'A', 0x08), mem.write(0x10, 0x05)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, FLAG_C), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('CMP_ZEROPAGE_X_LESS', [0xD5, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0x03), setattr(cpu, 'X', 0x02), mem.write(0x12, 0x05)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, 0), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('CMP_ZEROPAGE_X_EQUAL', [0xD5, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0x05), setattr(cpu, 'X', 0x02), mem.write(0x12, 0x05)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, FLAG_C), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('CMP_ZEROPAGE_X_GREATER', [0xD5, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0x08), setattr(cpu, 'X', 0x02), mem.write(0x12, 0x05)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, FLAG_C), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('CMP_ABSOLUTE_LESS', [0xCD, 0x00, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0x03), mem.write(0x1000, 0x05)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, 0), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('CMP_ABSOLUTE_EQUAL', [0xCD, 0x00, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0x05), mem.write(0x1000, 0x05)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, FLAG_C), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('CMP_ABSOLUTE_GREATER', [0xCD, 0x00, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0x08), mem.write(0x1000, 0x05)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, FLAG_C), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('CMP_ABSOLUTE_X_LESS', [0xDD, 0x00, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0x03), setattr(cpu, 'X', 0x02), mem.write(0x1002, 0x05)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, 0), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('CMP_ABSOLUTE_X_EQUAL', [0xDD, 0x00, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0x05), setattr(cpu, 'X', 0x02), mem.write(0x1002, 0x05)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, FLAG_C), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('CMP_ABSOLUTE_X_GREATER', [0xDD, 0x00, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0x08), setattr(cpu, 'X', 0x02), mem.write(0x1002, 0x05)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, FLAG_C), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('CMP_ABSOLUTE_Y_LESS', [0xD9, 0x00, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0x03), setattr(cpu, 'Y', 0x02), mem.write(0x1002, 0x05)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, 0), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('CMP_ABSOLUTE_Y_EQUAL', [0xD9, 0x00, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0x05), setattr(cpu, 'Y', 0x02), mem.write(0x1002, 0x05)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, FLAG_C), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('CMP_ABSOLUTE_Y_GREATER', [0xD9, 0x00, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0x08), setattr(cpu, 'Y', 0x02), mem.write(0x1002, 0x05)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, FLAG_C), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('CMP_INDIRECT_X_LESS', [0xC1, 0x20], 6,
     lambda cpu, mem: (setattr(cpu, 'A', 0x03), setattr(cpu, 'X', 0x04), mem.write(0x24, 0x00), mem.write(0x25, 0x10), mem.write(0x1000, 0x05)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, 0), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('CMP_INDIRECT_X_EQUAL', [0xC1, 0x20], 6,
     lambda cpu, mem: (setattr(cpu, 'A', 0x05), setattr(cpu, 'X', 0x04), mem.write(0x24, 0x00), mem.write(0x25, 0x10), mem.write(0x1000, 0x05)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, FLAG_C), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('CMP_INDIRECT_X_GREATER', [0xC1, 0x20], 6,
     lambda cpu, mem: (setattr(cpu, 'A', 0x08), setattr(cpu, 'X', 0x04), mem.write(0x24, 0x00), mem.write(0x25, 0x10), mem.write(0x1000, 0x05)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, FLAG_C), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('CMP_INDIRECT_Y_LESS', [0xD1, 0x20], 5,
     lambda cpu, mem: (setattr(cpu, 'A', 0x03), setattr(cpu, 'Y', 0x02), mem.write(0x20, 0x00), mem.write(0x21, 0x10), mem.write(0x1002, 0x05)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, 0), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('CMP_INDIRECT_Y_EQUAL', [0xD1, 0x20], 5,
     lambda cpu, mem: (setattr(cpu, 'A', 0x05), setattr(cpu, 'Y', 0x02), mem.write(0x20, 0x00), mem.write(0x21, 0x10), mem.write(0x1002, 0x05)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, FLAG_C), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('CMP_INDIRECT_Y_GREATER', [0xD1, 0x20], 5,
     lambda cpu, mem: (setattr(cpu, 'A', 0x08), setattr(cpu, 'Y', 0x02), mem.write(0x20, 0x00), mem.write(0x21, 0x10), mem.write(0x1002, 0x05)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, FLAG_C), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),

    # CPX
    ('CPX_IMMEDIATE_LESS', [0xE0, 0x05], 2,
     lambda cpu, mem: setattr(cpu, 'X', 0x03),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, 0), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('CPX_IMMEDIATE_EQUAL', [0xE0, 0x05], 2,
     lambda cpu, mem: setattr(cpu, 'X', 0x05),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, FLAG_C), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('CPX_IMMEDIATE_GREATER', [0xE0, 0x05], 2,
     lambda cpu, mem: setattr(cpu, 'X', 0x08),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, FLAG_C), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('CPX_ZEROPAGE_LESS', [0xE4, 0x10], 3,
     lambda cpu, mem: (setattr(cpu, 'X', 0x03), mem.write(0x10, 0x05)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, 0), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('CPX_ZEROPAGE_EQUAL', [0xE4, 0x10], 3,
     lambda cpu, mem: (setattr(cpu, 'X', 0x05), mem.write(0x10, 0x05)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, FLAG_C), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('CPX_ZEROPAGE_GREATER', [0xE4, 0x10], 3,
     lambda cpu, mem: (setattr(cpu, 'X', 0x08), mem.write(0x10, 0x05)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, FLAG_C), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('CPX_ABSOLUTE_LESS', [0xEC, 0x00, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'X', 0x03), mem.write(0x1000, 0x05)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, 0), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('CPX_ABSOLUTE_EQUAL', [0xEC, 0x00, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'X', 0x05), mem.write(0x1000, 0x05)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, FLAG_C), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('CPX_ABSOLUTE_GREATER', [0xEC, 0x00, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'X', 0x08), mem.write(0x1000, 0x05)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, FLAG_C), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),

    # CPY
    ('CPY_IMMEDIATE_LESS', [0xC0, 0x05], 2,
     lambda cpu, mem: setattr(cpu, 'Y', 0x03),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, 0), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('CPY_IMMEDIATE_EQUAL', [0xC0, 0x05], 2,
     lambda cpu, mem: setattr(cpu, 'Y', 0x05),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, FLAG_C), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('CPY_IMMEDIATE_GREATER', [0xC0, 0x05], 2,
     lambda cpu, mem: setattr(cpu, 'Y', 0x08),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, FLAG_C), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('CPY_ZEROPAGE_LESS', [0xC4, 0x10], 3,
     lambda cpu, mem: (setattr(cpu, 'Y', 0x03), mem.write(0x10, 0x05)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, 0), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('CPY_ZEROPAGE_EQUAL', [0xC4, 0x10], 3,
     lambda cpu, mem: (setattr(cpu, 'Y', 0x05), mem.write(0x10, 0x05)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, FLAG_C), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('CPY_ZEROPAGE_GREATER', [0xC4, 0x10], 3,
     lambda cpu, mem: (setattr(cpu, 'Y', 0x08), mem.write(0x10, 0x05)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, FLAG_C), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('CPY_ABSOLUTE_LESS', [0xCC, 0x00, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'Y', 0x03), mem.write(0x1000, 0x05)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, 0), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('CPY_ABSOLUTE_EQUAL', [0xCC, 0x00, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'Y', 0x05), mem.write(0x1000, 0x05)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, FLAG_C), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('CPY_ABSOLUTE_GREATER', [0xCC, 0x00, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'Y', 0x08), mem.write(0x1000, 0x05)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & FLAG_C, FLAG_C), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),

    # DEC
    ('DEC_ZEROPAGE_NORMAL', [0xC6, 0x10], 5,
     lambda cpu, mem: mem.write(0x10, 0x05),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x10), 0x04), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('DEC_ZEROPAGE_ZERO', [0xC6, 0x10], 5,
     lambda cpu, mem: mem.write(0x10, 0x01),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x10), 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('DEC_ZEROPAGE_NEGATIVE', [0xC6, 0x10], 5,
     lambda cpu, mem: mem.write(0x10, 0x80),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x10), 0x7F), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('DEC_ZEROPAGE_X_NORMAL', [0xD6, 0x10], 6,
     lambda cpu, mem: (setattr(cpu, 'X', 0x02), mem.write(0x12, 0x05)),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x12), 0x04), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('DEC_ZEROPAGE_X_ZERO', [0xD6, 0x10], 6,
     lambda cpu, mem: (setattr(cpu, 'X', 0x02), mem.write(0x12, 0x01)),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x12), 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('DEC_ZEROPAGE_X_NEGATIVE', [0xD6, 0x10], 6,
     lambda cpu, mem: (setattr(cpu, 'X', 0x02), mem.write(0x12, 0x80)),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x12), 0x7F), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('DEC_ABSOLUTE_NORMAL', [0xCE, 0x00, 0x10], 6,
     lambda cpu, mem: mem.write(0x1000, 0x05),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x1000), 0x04), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('DEC_ABSOLUTE_ZERO', [0xCE, 0x00, 0x10], 6,
     lambda cpu, mem: mem.write(0x1000, 0x01),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x1000), 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('DEC_ABSOLUTE_NEGATIVE', [0xCE, 0x00, 0x10], 6,
     lambda cpu, mem: mem.write(0x1000, 0x80),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x1000), 0x7F), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('DEC_ABSOLUTE_X_NORMAL', [0xDE, 0x00, 0x10], 7,
     lambda cpu, mem: (setattr(cpu, 'X', 0x02), mem.write(0x1002, 0x05)),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x1002), 0x04), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('DEC_ABSOLUTE_X_ZERO', [0xDE, 0x00, 0x10], 7,
     lambda cpu, mem: (setattr(cpu, 'X', 0x02), mem.write(0x1002, 0x01)),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x1002), 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('DEC_ABSOLUTE_X_NEGATIVE', [0xDE, 0x00, 0x10], 7,
     lambda cpu, mem: (setattr(cpu, 'X', 0x02), mem.write(0x1002, 0x80)),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x1002), 0x7F), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('DEX_NORMAL', [0xCA], 2,
     lambda cpu, mem: setattr(cpu, 'X', 0x05),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.X, 0x04), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('DEX_ZERO', [0xCA], 2,
     lambda cpu, mem: setattr(cpu, 'X', 0x01),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.X, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('DEX_NEGATIVE', [0xCA], 2,
     lambda cpu, mem: setattr(cpu, 'X', 0x80),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.X, 0x7F), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('DEY_NORMAL', [0x88], 2,
     lambda cpu, mem: setattr(cpu, 'Y', 0x05),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.Y, 0x04), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('DEY_ZERO', [0x88], 2,
     lambda cpu, mem: setattr(cpu, 'Y', 0x01),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.Y, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('DEY_NEGATIVE', [0x88], 2,
     lambda cpu, mem: setattr(cpu, 'Y', 0x80),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.Y, 0x7F), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),

    # EOR
    ('EOR_IMMEDIATE_NORMAL', [0x49, 0x0F], 2,
     lambda cpu, mem: setattr(cpu, 'A', 0xF0),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0xFF), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('EOR_IMMEDIATE_ZERO', [0x49, 0x0F], 2,
     lambda cpu, mem: setattr(cpu, 'A', 0x0F),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('EOR_IMMEDIATE_NEGATIVE', [0x49, 0x80], 2,
     lambda cpu, mem: setattr(cpu, 'A', 0x7F),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0xFF), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('EOR_ZEROPAGE_NORMAL', [0x45, 0x10], 3,
     lambda cpu, mem: (setattr(cpu, 'A', 0xF0), mem.write(0x10, 0x0F)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0xFF), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('EOR_ZEROPAGE_ZERO', [0x45, 0x10], 3,
     lambda cpu, mem: (setattr(cpu, 'A', 0x0F), mem.write(0x10, 0x0F)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('EOR_ZEROPAGE_NEGATIVE', [0x45, 0x10], 3,
     lambda cpu, mem: (setattr(cpu, 'A', 0x7F), mem.write(0x10, 0x80)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0xFF), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('EOR_ZEROPAGE_X_NORMAL', [0x55, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0xF0), setattr(cpu, 'X', 0x02), mem.write(0x12, 0x0F)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0xFF), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('EOR_ZEROPAGE_X_ZERO', [0x55, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0x0F), setattr(cpu, 'X', 0x02), mem.write(0x12, 0x0F)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('EOR_ZEROPAGE_X_NEGATIVE', [0x55, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0x7F), setattr(cpu, 'X', 0x02), mem.write(0x12, 0x80)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0xFF), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('EOR_ABSOLUTE_NORMAL', [0x4D, 0x00, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0xF0), mem.write(0x1000, 0x0F)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0xFF), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('EOR_ABSOLUTE_ZERO', [0x4D, 0x00, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0x0F), mem.write(0x1000, 0x0F)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('EOR_ABSOLUTE_NEGATIVE', [0x4D, 0x00, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0x7F), mem.write(0x1000, 0x80)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0xFF), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('EOR_ABSOLUTE_X_NORMAL', [0x5D, 0x00, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0xF0), setattr(cpu, 'X', 0x02), mem.write(0x1002, 0x0F)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0xFF), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('EOR_ABSOLUTE_X_ZERO', [0x5D, 0x00, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0x0F), setattr(cpu, 'X', 0x02), mem.write(0x1002, 0x0F)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('EOR_ABSOLUTE_X_NEGATIVE', [0x5D, 0x00, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0x7F), setattr(cpu, 'X', 0x02), mem.write(0x1002, 0x80)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0xFF), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('EOR_ABSOLUTE_Y_NORMAL', [0x59, 0x00, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0xF0), setattr(cpu, 'Y', 0x02), mem.write(0x1002, 0x0F)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0xFF), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('EOR_ABSOLUTE_Y_ZERO', [0x59, 0x00, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0x0F), setattr(cpu, 'Y', 0x02), mem.write(0x1002, 0x0F)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('EOR_ABSOLUTE_Y_NEGATIVE', [0x59, 0x00, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0x7F), setattr(cpu, 'Y', 0x02), mem.write(0x1002, 0x80)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0xFF), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('EOR_INDIRECT_X_NORMAL', [0x41, 0x20], 6,
     lambda cpu, mem: (setattr(cpu, 'A', 0xF0), setattr(cpu, 'X', 0x04), mem.write(0x24, 0x00), mem.write(0x25, 0x10), mem.write(0x1000, 0x0F)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0xFF), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('EOR_INDIRECT_X_ZERO', [0x41, 0x20], 6,
     lambda cpu, mem: (setattr(cpu, 'A', 0x0F), setattr(cpu, 'X', 0x04), mem.write(0x24, 0x00), mem.write(0x25, 0x10), mem.write(0x1000, 0x0F)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('EOR_INDIRECT_X_NEGATIVE', [0x41, 0x20], 6,
     lambda cpu, mem: (setattr(cpu, 'A', 0x7F), setattr(cpu, 'X', 0x04), mem.write(0x24, 0x00), mem.write(0x25, 0x10), mem.write(0x1000, 0x80)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0xFF), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('EOR_INDIRECT_Y_NORMAL', [0x51, 0x20], 5,
     lambda cpu, mem: (setattr(cpu, 'A', 0xF0), setattr(cpu, 'Y', 0x04), mem.write(0x20, 0x00), mem.write(0x21, 0x10), mem.write(0x1004, 0x0F)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0xFF), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('EOR_INDIRECT_Y_ZERO', [0x51, 0x20], 5,
     lambda cpu, mem: (setattr(cpu, 'A', 0x0F), setattr(cpu, 'Y', 0x04), mem.write(0x20, 0x00), mem.write(0x21, 0x10), mem.write(0x1004, 0x0F)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('EOR_INDIRECT_Y_NEGATIVE', [0x51, 0x20], 5,
     lambda cpu, mem: (setattr(cpu, 'A', 0x7F), setattr(cpu, 'Y', 0x04), mem.write(0x20, 0x00), mem.write(0x21, 0x10), mem.write(0x1004, 0x80)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0xFF), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),

    # INC
    ('INC_ZEROPAGE_NORMAL', [0xE6, 0x10], 5,
     lambda cpu, mem: mem.write(0x0010, 0x05),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x0010), 0x06), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('INC_ZEROPAGE_ZERO', [0xE6, 0x10], 5,
     lambda cpu, mem: mem.write(0x0010, 0xFF),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x0010), 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('INC_ZEROPAGE_NEGATIVE', [0xE6, 0x10], 5,
     lambda cpu, mem: mem.write(0x0010, 0x7F),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x0010), 0x80), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('INC_ZEROPAGE_X_NORMAL', [0xF6, 0x10], 6,
     lambda cpu, mem: (setattr(cpu, 'X', 0x02), mem.write(0x0012, 0x03)),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x0012), 0x04), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('INC_ZEROPAGE_X_ZERO', [0xF6, 0x10], 6,
     lambda cpu, mem: (setattr(cpu, 'X', 0x02), mem.write(0x0012, 0xFF)),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x0012), 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('INC_ZEROPAGE_X_NEGATIVE', [0xF6, 0x10], 6,
     lambda cpu, mem: (setattr(cpu, 'X', 0x02), mem.write(0x0012, 0x7F)),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x0012), 0x80), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('INC_ABSOLUTE_NORMAL', [0xEE, 0x00, 0x20], 6,
     lambda cpu, mem: mem.write(0x2000, 0x05),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x2000), 0x06), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('INC_ABSOLUTE_ZERO', [0xEE, 0x00, 0x20], 6,
     lambda cpu, mem: mem.write(0x2000, 0xFF),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x2000), 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('INC_ABSOLUTE_NEGATIVE', [0xEE, 0x00, 0x20], 6,
     lambda cpu, mem: mem.write(0x2000, 0x7F),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x2000), 0x80), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('INC_ABSOLUTE_X_NORMAL', [0xFE, 0x00, 0x20], 7,
     lambda cpu, mem: (setattr(cpu, 'X', 0x03), mem.write(0x2003, 0x04)),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x2003), 0x05), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('INC_ABSOLUTE_X_ZERO', [0xFE, 0x00, 0x20], 7,
     lambda cpu, mem: (setattr(cpu, 'X', 0x03), mem.write(0x2003, 0xFF)),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x2003), 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('INC_ABSOLUTE_X_NEGATIVE', [0xFE, 0x00, 0x20], 7,
     lambda cpu, mem: (setattr(cpu, 'X', 0x03), mem.write(0x2003, 0x7F)),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x2003), 0x80), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),

    # INX
    ('INX_NORMAL', [0xE8], 2,
     lambda cpu, mem: setattr(cpu, 'X', 0x05),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.X, 0x06), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('INX_ZERO', [0xE8], 2,
     lambda cpu, mem: setattr(cpu, 'X', 0xFF),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.X, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('INX_NEGATIVE', [0xE8], 2,
     lambda cpu, mem: setattr(cpu, 'X', 0x7F),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.X, 0x80), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),

    # INY
    ('INY_NORMAL', [0xC8], 2,
     lambda cpu, mem: setattr(cpu, 'Y', 0x05),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.Y, 0x06), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('INY_ZERO', [0xC8], 2,
     lambda cpu, mem: setattr(cpu, 'Y', 0xFF),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.Y, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('INY_NEGATIVE', [0xC8], 2,
     lambda cpu, mem: setattr(cpu, 'Y', 0x7F),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.Y, 0x80), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),

    # JMP
    ('JMP_INDIRECT_NORMAL', [0x6C, 0x00, 0x30], 5,
     lambda cpu, mem: (mem.write(0x3000, 0x00), mem.write(0x3001, 0x40)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.PC, 0x4000))
    ),
    ('JMP_INDIRECT_NORMAL', [0x6C, 0x00, 0x30], 5,
     lambda cpu, mem: (mem.write(0x3000, 0x00), mem.write(0x3001, 0x40)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.PC, 0x4000))
    ),
    ('JMP_INDIRECT_PAGE_WRAP', [0x6C, 0xFF, 0x30], 5,
     lambda cpu, mem: (mem.write(0x30FF, 0x10), mem.write(0x3000, 0x50)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.PC, 0x5010))
    ),

    # JSR
    ('JSR_ABSOLUTE', [0x20, 0x00, 0x40], 6,
     lambda cpu, mem: (setattr(cpu, 'SP', 0xFD)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.SP, 0xFB), t.assertEqual(mem.read(0x01FD), 0x02), t.assertEqual(mem.read(0x01FC), 0x02), t.assertEqual(cpu.PC, 0x4000))
    ),
    ('JSR_ABSOLUTE_ALT', [0x20, 0x34, 0x12], 6,
     lambda cpu, mem: (setattr(cpu, 'SP', 0xF9)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.SP, 0xF7), t.assertEqual(mem.read(0x01F9), 0x02), t.assertEqual(mem.read(0x01F8), 0x02), t.assertEqual(cpu.PC, 0x1234))
    ),
    ('JSR_STACK_WRAP', [0x20, 0x00, 0x30], 6,
     lambda cpu, mem: setattr(cpu, 'SP', 0x00),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.SP, 0xFE), t.assertEqual(cpu.PC, 0x3000))
    ),

    # LDA
    ('LDA_IMMEDIATE_NORMAL', [0xA9, 0x42], 2,
     lambda cpu, mem: None,
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x42), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LDA_IMMEDIATE_ZERO', [0xA9, 0x00], 2,
     lambda cpu, mem: None,
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LDA_IMMEDIATE_NEGATIVE', [0xA9, 0x80], 2,
     lambda cpu, mem: None,
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x80), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('LDA_ZEROPAGE_NORMAL', [0xA5, 0x10], 3,
     lambda cpu, mem: mem.write(0x0010, 0x42),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x42), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LDA_ZEROPAGE_ZERO', [0xA5, 0x10], 3,
     lambda cpu, mem: mem.write(0x0010, 0x00),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LDA_ZEROPAGE_NEGATIVE', [0xA5, 0x10], 3,
     lambda cpu, mem: mem.write(0x0010, 0x80),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x80), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('LDA_ZEROPAGE_X_NORMAL', [0xB5, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'X', 0x02), mem.write(0x0012, 0x42)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x42), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LDA_ZEROPAGE_X_ZERO', [0xB5, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'X', 0x02), mem.write(0x0012, 0x00)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LDA_ZEROPAGE_X_NEGATIVE', [0xB5, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'X', 0x02), mem.write(0x0012, 0x80)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x80), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('LDA_ABSOLUTE_NORMAL', [0xAD, 0x00, 0x20], 4,
     lambda cpu, mem: mem.write(0x2000, 0x42),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x42), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LDA_ABSOLUTE_ZERO', [0xAD, 0x00, 0x20], 4,
     lambda cpu, mem: mem.write(0x2000, 0x00),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LDA_ABSOLUTE_NEGATIVE', [0xAD, 0x00, 0x20], 4,
     lambda cpu, mem: mem.write(0x2000, 0x80),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x80), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('LDA_ABSOLUTE_X_NORMAL', [0xBD, 0x00, 0x20], 4,
     lambda cpu, mem: (setattr(cpu, 'X', 0x02), mem.write(0x2002, 0x42)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x42), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LDA_ABSOLUTE_X_ZERO', [0xBD, 0x00, 0x20], 4,
     lambda cpu, mem: (setattr(cpu, 'X', 0x02), mem.write(0x2002, 0x00)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LDA_ABSOLUTE_X_NEGATIVE', [0xBD, 0x00, 0x20], 4,
     lambda cpu, mem: (setattr(cpu, 'X', 0x02), mem.write(0x2002, 0x80)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x80), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('LDA_ABSOLUTE_Y_NORMAL', [0xB9, 0x00, 0x20], 4,
     lambda cpu, mem: (setattr(cpu, 'Y', 0x02), mem.write(0x2002, 0x42)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x42), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LDA_ABSOLUTE_Y_ZERO', [0xB9, 0x00, 0x20], 4,
     lambda cpu, mem: (setattr(cpu, 'Y', 0x02), mem.write(0x2002, 0x00)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LDA_ABSOLUTE_Y_NEGATIVE', [0xB9, 0x00, 0x20], 4,
     lambda cpu, mem: (setattr(cpu, 'Y', 0x02), mem.write(0x2002, 0x80)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x80), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('LDA_INDIRECT_X_NORMAL', [0xA1, 0x20], 6,
     lambda cpu, mem: (setattr(cpu, 'X', 0x04), mem.write(0x24, 0x00), mem.write(0x25, 0x30), mem.write(0x3000, 0x42)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x42), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LDA_INDIRECT_X_ZERO', [0xA1, 0x20], 6,
     lambda cpu, mem: (setattr(cpu, 'X', 0x04), mem.write(0x24, 0x00), mem.write(0x25, 0x30), mem.write(0x3000, 0x00)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LDA_INDIRECT_X_NEGATIVE', [0xA1, 0x20], 6,
     lambda cpu, mem: (setattr(cpu, 'X', 0x04), mem.write(0x24, 0x00), mem.write(0x25, 0x30), mem.write(0x3000, 0x80)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x80), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('LDA_INDIRECT_Y_NORMAL', [0xB1, 0x20], 5,
     lambda cpu, mem: (setattr(cpu, 'Y', 0x04), mem.write(0x20, 0x00), mem.write(0x21, 0x30), mem.write(0x3004, 0x42)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x42), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LDA_INDIRECT_Y_ZERO', [0xB1, 0x20], 5,
     lambda cpu, mem: (setattr(cpu, 'Y', 0x04), mem.write(0x20, 0x00), mem.write(0x21, 0x30), mem.write(0x3004, 0x00)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LDA_INDIRECT_Y_NEGATIVE', [0xB1, 0x20], 5,
     lambda cpu, mem: (setattr(cpu, 'Y', 0x04), mem.write(0x20, 0x00), mem.write(0x21, 0x30), mem.write(0x3004, 0x80)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x80), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),

    # LDX
    ('LDX_IMMEDIATE_NORMAL', [0xA2, 0x42], 2,
     lambda cpu, mem: None,
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.X, 0x42), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LDX_IMMEDIATE_ZERO', [0xA2, 0x00], 2,
     lambda cpu, mem: None,
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.X, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LDX_IMMEDIATE_NEGATIVE', [0xA2, 0x80], 2,
     lambda cpu, mem: None,
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.X, 0x80), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('LDX_ZEROPAGE_NORMAL', [0xA6, 0x10], 3,
     lambda cpu, mem: mem.write(0x0010, 0x42),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.X, 0x42), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LDX_ZEROPAGE_ZERO', [0xA6, 0x10], 3,
     lambda cpu, mem: mem.write(0x0010, 0x00),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.X, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LDX_ZEROPAGE_NEGATIVE', [0xA6, 0x10], 3,
     lambda cpu, mem: mem.write(0x0010, 0x80),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.X, 0x80), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('LDX_ZEROPAGE_Y_NORMAL', [0xB6, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'Y', 0x02), mem.write(0x0012, 0x42)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.X, 0x42), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LDX_ZEROPAGE_Y_ZERO', [0xB6, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'Y', 0x02), mem.write(0x0012, 0x00)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.X, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LDX_ZEROPAGE_Y_NEGATIVE', [0xB6, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'Y', 0x02), mem.write(0x0012, 0x80)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.X, 0x80), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('LDX_ABSOLUTE_NORMAL', [0xAE, 0x00, 0x20], 4,
     lambda cpu, mem: mem.write(0x2000, 0x42),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.X, 0x42), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LDX_ABSOLUTE_ZERO', [0xAE, 0x00, 0x20], 4,
     lambda cpu, mem: mem.write(0x2000, 0x00),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.X, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LDX_ABSOLUTE_NEGATIVE', [0xAE, 0x00, 0x20], 4,
     lambda cpu, mem: mem.write(0x2000, 0x80),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.X, 0x80), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('LDX_ABSOLUTE_Y_NORMAL', [0xBE, 0x00, 0x20], 4,
     lambda cpu, mem: (setattr(cpu, 'Y', 0x02), mem.write(0x2002, 0x42)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.X, 0x42), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LDX_ABSOLUTE_Y_ZERO', [0xBE, 0x00, 0x20], 4,
     lambda cpu, mem: (setattr(cpu, 'Y', 0x02), mem.write(0x2002, 0x00)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.X, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LDX_ABSOLUTE_Y_NEGATIVE', [0xBE, 0x00, 0x20], 4,
     lambda cpu, mem: (setattr(cpu, 'Y', 0x02), mem.write(0x2002, 0x80)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.X, 0x80), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),

    # LDY
    ('LDY_IMMEDIATE_NORMAL', [0xA0, 0x42], 2,
     lambda cpu, mem: None,
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.Y, 0x42), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LDY_IMMEDIATE_ZERO', [0xA0, 0x00], 2,
     lambda cpu, mem: None,
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.Y, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LDY_IMMEDIATE_NEGATIVE', [0xA0, 0x80], 2,
     lambda cpu, mem: None,
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.Y, 0x80), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('LDY_ZEROPAGE_NORMAL', [0xA4, 0x10], 3,
     lambda cpu, mem: mem.write(0x0010, 0x42),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.Y, 0x42), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LDY_ZEROPAGE_ZERO', [0xA4, 0x10], 3,
     lambda cpu, mem: mem.write(0x0010, 0x00),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.Y, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LDY_ZEROPAGE_NEGATIVE', [0xA4, 0x10], 3,
     lambda cpu, mem: mem.write(0x0010, 0x80),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.Y, 0x80), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('LDY_ZEROPAGE_X_NORMAL', [0xB4, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'X', 0x02), mem.write(0x0012, 0x42)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.Y, 0x42), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LDY_ZEROPAGE_X_ZERO', [0xB4, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'X', 0x02), mem.write(0x0012, 0x00)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.Y, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LDY_ZEROPAGE_X_NEGATIVE', [0xB4, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'X', 0x02), mem.write(0x0012, 0x80)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.Y, 0x80), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('LDY_ABSOLUTE_NORMAL', [0xAC, 0x00, 0x20], 4,
     lambda cpu, mem: mem.write(0x2000, 0x42),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.Y, 0x42), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LDY_ABSOLUTE_ZERO', [0xAC, 0x00, 0x20], 4,
     lambda cpu, mem: mem.write(0x2000, 0x00),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.Y, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LDY_ABSOLUTE_NEGATIVE', [0xAC, 0x00, 0x20], 4,
     lambda cpu, mem: mem.write(0x2000, 0x80),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.Y, 0x80), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('LDY_ABSOLUTE_X_NORMAL', [0xBC, 0x00, 0x20], 4,
     lambda cpu, mem: (setattr(cpu, 'X', 0x02), mem.write(0x2002, 0x42)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.Y, 0x42), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LDY_ABSOLUTE_X_ZERO', [0xBC, 0x00, 0x20], 4,
     lambda cpu, mem: (setattr(cpu, 'X', 0x02), mem.write(0x2002, 0x00)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.Y, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LDY_ABSOLUTE_X_NEGATIVE', [0xBC, 0x00, 0x20], 4,
     lambda cpu, mem: (setattr(cpu, 'X', 0x02), mem.write(0x2002, 0x80)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.Y, 0x80), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),

    # LSR
    ('LSR_ACC_C0', [0x4A], 2,
     lambda cpu, mem: setattr(cpu, 'A', 0x02),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x01), t.assertEqual(cpu.P & FLAG_C, 0), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LSR_ACC_C1', [0x4A], 2,
     lambda cpu, mem: setattr(cpu, 'A', 0x03),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x01), t.assertEqual(cpu.P & FLAG_C, FLAG_C), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LSR_ACC_ZERO', [0x4A], 2,
     lambda cpu, mem: setattr(cpu, 'A', 0x01),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x00), t.assertEqual(cpu.P & FLAG_C, FLAG_C), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LSR_ZP_C0', [0x46, 0x10], 5,
     lambda cpu, mem: mem.write(0x0010, 0x02),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x0010), 0x01), t.assertEqual(cpu.P & FLAG_C, 0), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LSR_ZP_C1', [0x46, 0x10], 5,
     lambda cpu, mem: mem.write(0x0010, 0x03),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x0010), 0x01), t.assertEqual(cpu.P & FLAG_C, FLAG_C), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LSR_ZP_ZERO', [0x46, 0x10], 5,
     lambda cpu, mem: mem.write(0x0010, 0x01),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x0010), 0x00), t.assertEqual(cpu.P & FLAG_C, FLAG_C), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LSR_ZP_X_C0', [0x56, 0x10], 6,
     lambda cpu, mem: (setattr(cpu, 'X', 0x02), mem.write(0x0012, 0x02)),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x0012), 0x01), t.assertEqual(cpu.P & FLAG_C, 0), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LSR_ZP_X_C1', [0x56, 0x10], 6,
     lambda cpu, mem: (setattr(cpu, 'X', 0x02), mem.write(0x0012, 0x03)),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x0012), 0x01), t.assertEqual(cpu.P & FLAG_C, FLAG_C), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LSR_ZP_X_ZERO', [0x56, 0x10], 6,
     lambda cpu, mem: (setattr(cpu, 'X', 0x02), mem.write(0x0012, 0x01)),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x0012), 0x00), t.assertEqual(cpu.P & FLAG_C, FLAG_C), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LSR_ABSOLUTE_C0', [0x4E, 0x00, 0x20], 6,
     lambda cpu, mem: mem.write(0x2000, 0x02),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x2000), 0x01), t.assertEqual(cpu.P & FLAG_C, 0), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LSR_ABSOLUTE_C1', [0x4E, 0x00, 0x20], 6,
     lambda cpu, mem: mem.write(0x2000, 0x03),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x2000), 0x01), t.assertEqual(cpu.P & FLAG_C, FLAG_C), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LSR_ABSOLUTE_ZERO', [0x4E, 0x00, 0x20], 6,
     lambda cpu, mem: mem.write(0x2000, 0x01),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x2000), 0x00), t.assertEqual(cpu.P & FLAG_C, FLAG_C), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LSR_ABSOLUTE_X_C0', [0x5E, 0x00, 0x20], 7,
     lambda cpu, mem: (setattr(cpu, 'X', 0x02), mem.write(0x2002, 0x02)),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x2002), 0x01), t.assertEqual(cpu.P & FLAG_C, 0), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LSR_ABSOLUTE_X_C1', [0x5E, 0x00, 0x20], 7,
     lambda cpu, mem: (setattr(cpu, 'X', 0x02), mem.write(0x2002, 0x03)),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x2002), 0x01), t.assertEqual(cpu.P & FLAG_C, FLAG_C), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('LSR_ABSOLUTE_X_ZERO', [0x5E, 0x00, 0x20], 7,
     lambda cpu, mem: (setattr(cpu, 'X', 0x02), mem.write(0x2002, 0x01)),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x2002), 0x00), t.assertEqual(cpu.P & FLAG_C, FLAG_C), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),

    # NOP
    ('NOP_STANDARD', [0xEA], 2,
     lambda cpu, mem: None,
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.PC, 0x0201), t.assertEqual(cpu.A, 0), t.assertEqual(cpu.X, 0), t.assertEqual(cpu.Y, 0))
    ),

    # ORA
    ('ORA_IMMEDIATE_NORMAL', [0x09, 0x42], 2,
     lambda cpu, mem: setattr(cpu, 'A', 0x10),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x52), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('ORA_IMMEDIATE_ZERO', [0x09, 0x00], 2,
     lambda cpu, mem: setattr(cpu, 'A', 0x00),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('ORA_IMMEDIATE_NEGATIVE', [0x09, 0x80], 2,
     lambda cpu, mem: setattr(cpu, 'A', 0x01),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x81), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('ORA_ZEROPAGE_NORMAL', [0x05, 0x10], 3,
     lambda cpu, mem: (setattr(cpu, 'A', 0x10), mem.write(0x0010, 0x42)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x52), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('ORA_ZEROPAGE_ZERO', [0x05, 0x10], 3,
     lambda cpu, mem: (setattr(cpu, 'A', 0x00), mem.write(0x0010, 0x00)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('ORA_ZEROPAGE_NEGATIVE', [0x05, 0x10], 3,
     lambda cpu, mem: (setattr(cpu, 'A', 0x01), mem.write(0x0010, 0x80)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x81), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('ORA_ZEROPAGE_X_NORMAL', [0x15, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0x10), setattr(cpu, 'X', 0x02), mem.write(0x0012, 0x42)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x52), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('ORA_ZEROPAGE_X_ZERO', [0x15, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0x00), setattr(cpu, 'X', 0x02), mem.write(0x0012, 0x00)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('ORA_ZEROPAGE_X_NEGATIVE', [0x15, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0x01), setattr(cpu, 'X', 0x02), mem.write(0x0012, 0x80)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x81), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('ORA_ABSOLUTE_NORMAL', [0x0D, 0x00, 0x20], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0x10), mem.write(0x2000, 0x42)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x52), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('ORA_ABSOLUTE_ZERO', [0x0D, 0x00, 0x20], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0x00), mem.write(0x2000, 0x00)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('ORA_ABSOLUTE_NEGATIVE', [0x0D, 0x00, 0x20], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0x01), mem.write(0x2000, 0x80)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x81), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('ORA_ABSOLUTE_X_NORMAL', [0x1D, 0x00, 0x20], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0x10), setattr(cpu, 'X', 0x02), mem.write(0x2002, 0x42)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x52), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('ORA_ABSOLUTE_X_ZERO', [0x1D, 0x00, 0x20], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0x00), setattr(cpu, 'X', 0x02), mem.write(0x2002, 0x00)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('ORA_ABSOLUTE_X_NEGATIVE', [0x1D, 0x00, 0x20], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0x01), setattr(cpu, 'X', 0x02), mem.write(0x2002, 0x80)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x81), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('ORA_ABSOLUTE_Y_NORMAL', [0x19, 0x00, 0x20], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0x10), setattr(cpu, 'Y', 0x02), mem.write(0x2002, 0x42)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x52), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('ORA_ABSOLUTE_Y_ZERO', [0x19, 0x00, 0x20], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0x00), setattr(cpu, 'Y', 0x02), mem.write(0x2002, 0x00)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('ORA_ABSOLUTE_Y_NEGATIVE', [0x19, 0x00, 0x20], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0x01), setattr(cpu, 'Y', 0x02), mem.write(0x2002, 0x80)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x81), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('ORA_INDIRECT_X_NORMAL', [0x01, 0x10], 6,
     lambda cpu, mem: (setattr(cpu, 'A', 0x10), setattr(cpu, 'X', 0x04), mem.write(0x0014, 0x00), mem.write(0x0015, 0x20), mem.write(0x2000, 0x42)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x52), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('ORA_INDIRECT_X_ZERO', [0x01, 0x10], 6,
     lambda cpu, mem: (setattr(cpu, 'A', 0x00), setattr(cpu, 'X', 0x04), mem.write(0x0014, 0x00), mem.write(0x0015, 0x20), mem.write(0x2000, 0x00)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('ORA_INDIRECT_X_NEGATIVE', [0x01, 0x10], 6,
     lambda cpu, mem: (setattr(cpu, 'A', 0x01), setattr(cpu, 'X', 0x04), mem.write(0x0014, 0x00), mem.write(0x0015, 0x20), mem.write(0x2000, 0x80)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x81), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),
    ('ORA_INDIRECT_Y_NORMAL', [0x11, 0x10], 5,
     lambda cpu, mem: (setattr(cpu, 'A', 0x10), setattr(cpu, 'Y', 0x02), mem.write(0x0010, 0x00), mem.write(0x0011, 0x20), mem.write(0x2002, 0x42)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x52), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('ORA_INDIRECT_Y_ZERO', [0x11, 0x10], 5,
     lambda cpu, mem: (setattr(cpu, 'A', 0x00), setattr(cpu, 'Y', 0x02), mem.write(0x0010, 0x00), mem.write(0x0011, 0x20), mem.write(0x2002, 0x00)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
    ('ORA_INDIRECT_Y_NEGATIVE', [0x11, 0x10], 5,
     lambda cpu, mem: (setattr(cpu, 'A', 0x01), setattr(cpu, 'Y', 0x02), mem.write(0x0010, 0x00), mem.write(0x0011, 0x20), mem.write(0x2002, 0x80)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x81), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),

    # PHA
    ('PHA', [0x48], 3,
     lambda cpu, mem: setattr(cpu, 'A', 0x42),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x0100 + cpu.SP + 1), 0x42), t.assertEqual(cpu.SP, 0xFE))
    ),

    # PHP
    ('PHP', [0x08], 3,
     lambda cpu, mem: setattr(cpu, 'P', FLAG_N | FLAG_Z),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x0100 + cpu.SP + 1) & (FLAG_N | FLAG_Z), FLAG_N | FLAG_Z), t.assertEqual(cpu.SP, 0xFE))
    ),

    # PLA
    ('PLA', [0x68], 4,
     lambda cpu, mem: (setattr(cpu, 'SP', 0xFE), mem.write(0x01FF, 0x42)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x42), t.assertEqual(cpu.SP, 0xFF))
    ),

    # PLP
    ('PLP', [0x28], 4,
     lambda cpu, mem: (setattr(cpu, 'SP', 0xFE), mem.write(0x01FF, FLAG_N | FLAG_Z)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.P & (FLAG_N | FLAG_Z), FLAG_N | FLAG_Z), t.assertEqual(cpu.SP, 0xFF))
    ),

    # ROL
    ('ROL_ACC_C0', [0x2A], 2,
     lambda cpu, mem: setattr(cpu, 'A', 0x40) or setattr(cpu, 'P', cpu.P & ~FLAG_C),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x80), t.assertEqual(cpu.P & FLAG_C, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N), t.assertEqual(cpu.P & FLAG_Z, 0))
    ),
    ('ROL_ACC_C1', [0x2A], 2,
     lambda cpu, mem: setattr(cpu, 'A', 0x40) or setattr(cpu, 'P', cpu.P | FLAG_C),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x81), t.assertEqual(cpu.P & FLAG_C, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N), t.assertEqual(cpu.P & FLAG_Z, 0))
    ),
    ('ROL_ACC_ZERO', [0x2A], 2,
     lambda cpu, mem: setattr(cpu, 'A', 0x00) or setattr(cpu, 'P', cpu.P | FLAG_C),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x01), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0), t.assertEqual(cpu.P & FLAG_C, 0))
    ),
    ('ROL_ZP_C0', [0x26, 0x10], 5,
     lambda cpu, mem: mem.write(0x0010, 0x40) or setattr(cpu, 'P', cpu.P & ~FLAG_C),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x0010), 0x80), t.assertEqual(cpu.P & FLAG_C, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N), t.assertEqual(cpu.P & FLAG_Z, 0))
    ),
    ('ROL_ZP_C1', [0x26, 0x10], 5,
     lambda cpu, mem: mem.write(0x0010, 0x40) or setattr(cpu, 'P', cpu.P | FLAG_C),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x0010), 0x81), t.assertEqual(cpu.P & FLAG_C, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N), t.assertEqual(cpu.P & FLAG_Z, 0))
    ),
    ('ROL_ZP_ZERO', [0x26, 0x10], 5,
     lambda cpu, mem: mem.write(0x0010, 0x00) or setattr(cpu, 'P', cpu.P | FLAG_C),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x0010), 0x01), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0), t.assertEqual(cpu.P & FLAG_C, 0))
    ),
    ('ROL_ZP_X_C0', [0x36, 0x10], 6,
     lambda cpu, mem: setattr(cpu, 'X', 0x02) or mem.write(0x0012, 0x40) or setattr(cpu, 'P', cpu.P & ~FLAG_C),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x0012), 0x80), t.assertEqual(cpu.P & FLAG_C, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N), t.assertEqual(cpu.P & FLAG_Z, 0))
    ),
    ('ROL_ZP_X_C1', [0x36, 0x10], 6,
     lambda cpu, mem: setattr(cpu, 'X', 0x02) or mem.write(0x0012, 0x40) or setattr(cpu, 'P', cpu.P | FLAG_C),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x0012), 0x81), t.assertEqual(cpu.P & FLAG_C, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N), t.assertEqual(cpu.P & FLAG_Z, 0))
    ),
    ('ROL_ZP_X_ZERO', [0x36, 0x10], 6,
     lambda cpu, mem: setattr(cpu, 'X', 0x02) or mem.write(0x0012, 0x00) or setattr(cpu, 'P', cpu.P | FLAG_C),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x0012), 0x01), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0), t.assertEqual(cpu.P & FLAG_C, 0))
    ),

    # ROR
    ('ROR_ACC_C0', [0x6A], 2,
     lambda cpu, mem: setattr(cpu, 'A', 0x02) or setattr(cpu, 'P', cpu.P & ~FLAG_C),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x01), t.assertEqual(cpu.P & FLAG_C, 0), t.assertEqual(cpu.P & FLAG_N, 0), t.assertEqual(cpu.P & FLAG_Z, 0))
    ),
    ('ROR_ACC_C1', [0x6A], 2,
     lambda cpu, mem: setattr(cpu, 'A', 0x02) or setattr(cpu, 'P', cpu.P | FLAG_C),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x81), t.assertEqual(cpu.P & FLAG_C, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N), t.assertEqual(cpu.P & FLAG_Z, 0))
    ),
    ('ROR_ACC_ZERO', [0x6A], 2,
     lambda cpu, mem: setattr(cpu, 'A', 0x00) or setattr(cpu, 'P', cpu.P & ~FLAG_C),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0), t.assertEqual(cpu.P & FLAG_C, 0))
    ),
    ('ROR_ZP_C0', [0x66, 0x10], 5,
     lambda cpu, mem: mem.write(0x0010, 0x02) or setattr(cpu, 'P', cpu.P & ~FLAG_C),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x0010), 0x01), t.assertEqual(cpu.P & FLAG_C, 0), t.assertEqual(cpu.P & FLAG_N, 0), t.assertEqual(cpu.P & FLAG_Z, 0))
    ),
    ('ROR_ZP_C1', [0x66, 0x10], 5,
     lambda cpu, mem: mem.write(0x0010, 0x02) or setattr(cpu, 'P', cpu.P | FLAG_C),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x0010), 0x81), t.assertEqual(cpu.P & FLAG_C, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N), t.assertEqual(cpu.P & FLAG_Z, 0))
    ),
    ('ROR_ZP_ZERO', [0x66, 0x10], 5,
     lambda cpu, mem: mem.write(0x0010, 0x00) or setattr(cpu, 'P', cpu.P & ~FLAG_C),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x0010), 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0), t.assertEqual(cpu.P & FLAG_C, 0))
    ),
    ('ROR_ZP_X_C0', [0x76, 0x10], 6,
     lambda cpu, mem: setattr(cpu, 'X', 0x02) or mem.write(0x0012, 0x02) or setattr(cpu, 'P', cpu.P & ~FLAG_C),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x0012), 0x01), t.assertEqual(cpu.P & FLAG_C, 0), t.assertEqual(cpu.P & FLAG_N, 0), t.assertEqual(cpu.P & FLAG_Z, 0))
    ),
    ('ROR_ZP_X_C1', [0x76, 0x10], 6,
     lambda cpu, mem: setattr(cpu, 'X', 0x02) or mem.write(0x0012, 0x02) or setattr(cpu, 'P', cpu.P | FLAG_C),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x0012), 0x81), t.assertEqual(cpu.P & FLAG_C, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N), t.assertEqual(cpu.P & FLAG_Z, 0))
    ),
    ('ROR_ZP_X_ZERO', [0x76, 0x10], 6,
     lambda cpu, mem: setattr(cpu, 'X', 0x02) or mem.write(0x0012, 0x00) or setattr(cpu, 'P', cpu.P & ~FLAG_C),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x0012), 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0), t.assertEqual(cpu.P & FLAG_C, 0))
    ),
    ('ROR_ABSOLUTE_C0', [0x6E, 0x00, 0x20], 6,
     lambda cpu, mem: mem.write(0x2000, 0x02) or setattr(cpu, 'P', cpu.P & ~FLAG_C),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x2000), 0x01), t.assertEqual(cpu.P & FLAG_C, 0), t.assertEqual(cpu.P & FLAG_N, 0), t.assertEqual(cpu.P & FLAG_Z, 0))
    ),
    ('ROR_ABSOLUTE_C1', [0x6E, 0x00, 0x20], 6,
     lambda cpu, mem: mem.write(0x2000, 0x02) or setattr(cpu, 'P', cpu.P | FLAG_C),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x2000), 0x81), t.assertEqual(cpu.P & FLAG_C, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N), t.assertEqual(cpu.P & FLAG_Z, 0))
    ),
    ('ROR_ABSOLUTE_ZERO', [0x6E, 0x00, 0x20], 6,
     lambda cpu, mem: mem.write(0x2000, 0x00) or setattr(cpu, 'P', cpu.P & ~FLAG_C),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x2000), 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0), t.assertEqual(cpu.P & FLAG_C, 0))
    ),
    ('ROR_ABSOLUTE_X_C0', [0x7E, 0x00, 0x20], 7,
     lambda cpu, mem: setattr(cpu, 'X', 0x02) or mem.write(0x2002, 0x02) or setattr(cpu, 'P', cpu.P & ~FLAG_C),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x2002), 0x01), t.assertEqual(cpu.P & FLAG_C, 0), t.assertEqual(cpu.P & FLAG_N, 0), t.assertEqual(cpu.P & FLAG_Z, 0))
    ),
    ('ROR_ABSOLUTE_X_C1', [0x7E, 0x00, 0x20], 7,
     lambda cpu, mem: setattr(cpu, 'X', 0x02) or mem.write(0x2002, 0x02) or setattr(cpu, 'P', cpu.P | FLAG_C),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x2002), 0x81), t.assertEqual(cpu.P & FLAG_C, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N), t.assertEqual(cpu.P & FLAG_Z, 0))
    ),
    ('ROR_ABSOLUTE_X_ZERO', [0x7E, 0x00, 0x20], 7,
     lambda cpu, mem: setattr(cpu, 'X', 0x02) or mem.write(0x2002, 0x00) or setattr(cpu, 'P', cpu.P & ~FLAG_C),
     lambda t, cpu, mem, cycles: (t.assertEqual(mem.read(0x2002), 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0), t.assertEqual(cpu.P & FLAG_C, 0))
    ),

    # RTI
    ('RTI', [0x40], 6,
     lambda cpu, mem: (setattr(cpu, 'SP', 0xFC), mem.write(0x01FE, 0x34), mem.write(0x01FF, 0x12), mem.write(0x01FD, FLAG_N | FLAG_Z)),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.PC, 0x1234), t.assertEqual(cpu.P & (FLAG_N | FLAG_Z), FLAG_N | FLAG_Z))
    ),

    # RTS
    ('RTS', [0x60], 6,
     lambda cpu, mem: (setattr(cpu, 'SP', 0xFD), mem.write(0x01FE, 0x05), mem.write(0x01FF, 0x02)),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.PC, 0x0206)
    ),

    # SBC (Subtract with Carry)
    ('SBC_IMM', [0xE9, 0x10], 2,
     lambda cpu, mem: (setattr(cpu, 'A', 0x30), setattr(cpu, 'P', cpu.P | FLAG_C)),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0x20)
    ),
    ('SBC_ZP', [0xE5, 0x10], 3,
     lambda cpu, mem: (setattr(cpu, 'A', 0x30), setattr(cpu, 'P', cpu.P | FLAG_C), mem.write(0x0010, 0x10)),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0x20)
    ),
    ('SBC_ZPX', [0xF5, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0x50), setattr(cpu, 'X', 0x05), setattr(cpu, 'P', cpu.P | FLAG_C), mem.write(0x0015, 0x10)),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0x40)
    ),
    ('SBC_ABS', [0xED, 0x00, 0x20], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0x50), setattr(cpu, 'P', cpu.P | FLAG_C), mem.write(0x2000, 0x20)),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0x30)
    ),
    ('SBC_ABX', [0xFD, 0x00, 0x20], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0x60), setattr(cpu, 'X', 0x05), setattr(cpu, 'P', cpu.P | FLAG_C), mem.write(0x2005, 0x20)),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0x40)
    ),
    ('SBC_ABY', [0xF9, 0x00, 0x20], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0x60), setattr(cpu, 'Y', 0x05), setattr(cpu, 'P', cpu.P | FLAG_C), mem.write(0x2005, 0x20)),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0x40)
    ),
    ('SBC_INDX', [0xE1, 0x10], 6,
     lambda cpu, mem: (setattr(cpu, 'A', 0x60), setattr(cpu, 'X', 0x04), setattr(cpu, 'P', cpu.P | FLAG_C), mem.write(0x0014, 0x00), mem.write(0x0015, 0x20), mem.write(0x2000, 0x20)),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0x40)
    ),
    ('SBC_INDY', [0xF1, 0x10], 5,
     lambda cpu, mem: (setattr(cpu, 'A', 0x60), setattr(cpu, 'Y', 0x05), setattr(cpu, 'P', cpu.P | FLAG_C), mem.write(0x0010, 0x00), mem.write(0x0011, 0x20), mem.write(0x2005, 0x20)),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0x40)
    ),
    ('SBC_IMM_DEC', [0xE9, 0x20], 3,
     lambda cpu, mem: (setattr(cpu, 'A', 0x50), setattr(cpu, 'P', cpu.P | FLAG_C | FLAG_D)),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0x30)
    ),
    ('SBC_ZP_DEC', [0xE5, 0x10], 4,
     lambda cpu, mem: (setattr(cpu, 'A', 0x50), setattr(cpu, 'P', cpu.P | FLAG_C | FLAG_D), mem.write(0x0010, 0x20)),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0x30)
    ),
    ('SBC_ZPX_DEC', [0xF5, 0x10], 5,
     lambda cpu, mem: (setattr(cpu, 'A', 0x60), setattr(cpu, 'X', 0x05), setattr(cpu, 'P', cpu.P | FLAG_C | FLAG_D), mem.write(0x0015, 0x20)),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0x40)
    ),
    ('SBC_ABS_DEC', [0xED, 0x00, 0x20], 5,
     lambda cpu, mem: (setattr(cpu, 'A', 0x50), setattr(cpu, 'P', cpu.P | FLAG_C | FLAG_D), mem.write(0x2000, 0x20)),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0x30)
    ),
    ('SBC_ABX_DEC', [0xFD, 0x00, 0x20], 5,
     lambda cpu, mem: (setattr(cpu, 'A', 0x60), setattr(cpu, 'X', 0x05), setattr(cpu, 'P', cpu.P | FLAG_C | FLAG_D), mem.write(0x2005, 0x20)),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0x40)
    ),
    ('SBC_ABY_DEC', [0xF9, 0x00, 0x20], 5,
     lambda cpu, mem: (setattr(cpu, 'A', 0x60), setattr(cpu, 'Y', 0x05), setattr(cpu, 'P', cpu.P | FLAG_C | FLAG_D), mem.write(0x2005, 0x20)),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0x40)
    ),
    ('SBC_INDX_DEC', [0xE1, 0x10], 7,
     lambda cpu, mem: (setattr(cpu, 'A', 0x60), setattr(cpu, 'X', 0x04), setattr(cpu, 'P', cpu.P | FLAG_C | FLAG_D), mem.write(0x0014, 0x00), mem.write(0x0015, 0x20), mem.write(0x2000, 0x20)),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0x40)
    ),
    ('SBC_INDY_DEC', [0xF1, 0x10], 6,
     lambda cpu, mem: (setattr(cpu, 'A', 0x60), setattr(cpu, 'Y', 0x05), setattr(cpu, 'P', cpu.P | FLAG_C | FLAG_D), mem.write(0x0010, 0x00), mem.write(0x0011, 0x20), mem.write(0x2005, 0x20)),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.A, 0x40)
    ),

    # SEC
    ('SEC', [0x38], 2,
     lambda cpu, mem: setattr(cpu, 'P', cpu.P & ~FLAG_C),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.P & FLAG_C, FLAG_C)
    ),

    # SED
    ('SED', [0xF8], 2,
     lambda cpu, mem: setattr(cpu, 'P', cpu.P & ~FLAG_D),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.P & FLAG_D, FLAG_D)
    ),

    # SEI
    ('SEI', [0x78], 2,
     lambda cpu, mem: setattr(cpu, 'P', cpu.P & ~FLAG_I),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.P & FLAG_I, FLAG_I)
    ),

    # STA
    ('STA_ZP', [0x85, 0x10], 3,
     lambda cpu, mem: setattr(cpu, 'A', 0x42),
     lambda t, cpu, mem, cycles: t.assertEqual(mem.read(0x0010), 0x42)
    ),
    ('STA_ZP_X', [0x95, 0x10], 4,
     lambda cpu, mem: setattr(cpu, 'A', 0x42) or setattr(cpu, 'X', 0x02),
     lambda t, cpu, mem, cycles: t.assertEqual(mem.read(0x0012), 0x42)
    ),
    ('STA_ABS', [0x8D, 0x00, 0x20], 4,
     lambda cpu, mem: setattr(cpu, 'A', 0x42),
     lambda t, cpu, mem, cycles: t.assertEqual(mem.read(0x2000), 0x42)
    ),
    ('STA_ABS_X', [0x9D, 0x00, 0x20], 5,
     lambda cpu, mem: setattr(cpu, 'A', 0x42) or setattr(cpu, 'X', 0x02),
     lambda t, cpu, mem, cycles: t.assertEqual(mem.read(0x2002), 0x42)
    ),
    ('STA_ABS_Y', [0x99, 0x00, 0x20], 5,
     lambda cpu, mem: setattr(cpu, 'A', 0x42) or setattr(cpu, 'Y', 0x02),
     lambda t, cpu, mem, cycles: t.assertEqual(mem.read(0x2002), 0x42)
    ),
    ('STA_IND_X', [0x81, 0x10], 6,
     lambda cpu, mem: setattr(cpu, 'A', 0x42) or setattr(cpu, 'X', 0x04) or mem.write(0x0014, 0x00) or mem.write(0x0015, 0x20),
     lambda t, cpu, mem, cycles: t.assertEqual(mem.read(0x2000), 0x42)
    ),
    ('STA_IND_Y', [0x91, 0x10], 6,
     lambda cpu, mem: setattr(cpu, 'A', 0x42) or setattr(cpu, 'Y', 0x03) or mem.write(0x0010, 0x00) or mem.write(0x0011, 0x20),
     lambda t, cpu, mem, cycles: t.assertEqual(mem.read(0x2003), 0x42)
    ),

    # STX
    ('STX_ZP', [0x86, 0x10], 3,
     lambda cpu, mem: setattr(cpu, 'X', 0x55),
     lambda t, cpu, mem, cycles: t.assertEqual(mem.read(0x0010), 0x55)
    ),
    ('STX_ZP_Y', [0x96, 0x10], 4,
     lambda cpu, mem: setattr(cpu, 'X', 0x55) or setattr(cpu, 'Y', 0x03),
     lambda t, cpu, mem, cycles: t.assertEqual(mem.read(0x0013), 0x55)
    ),
    ('STX_ABS', [0x8E, 0x00, 0x20], 4,
     lambda cpu, mem: setattr(cpu, 'X', 0x55),
     lambda t, cpu, mem, cycles: t.assertEqual(mem.read(0x2000), 0x55)
    ),

    # STY
    ('STY_ZP', [0x84, 0x10], 3,
     lambda cpu, mem: setattr(cpu, 'Y', 0xAA),
     lambda t, cpu, mem, cycles: t.assertEqual(mem.read(0x0010), 0xAA)
    ),
    ('STY_ZP_X', [0x94, 0x10], 4,
     lambda cpu, mem: setattr(cpu, 'Y', 0xAA) or setattr(cpu, 'X', 0x02),
     lambda t, cpu, mem, cycles: t.assertEqual(mem.read(0x0012), 0xAA)
    ),
    ('STY_ABS', [0x8C, 0x00, 0x20], 4,
     lambda cpu, mem: setattr(cpu, 'Y', 0xAA),
     lambda t, cpu, mem, cycles: t.assertEqual(mem.read(0x2000), 0xAA)
    ),

    # TAX
    ('TAX', [0xAA], 2,
     lambda cpu, mem: setattr(cpu, 'A', 0x42) or setattr(cpu, 'X', 0x00),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.X, 0x42), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),

    # TAY
    ('TAY', [0xA8], 2,
     lambda cpu, mem: setattr(cpu, 'A', 0x80) or setattr(cpu, 'Y', 0x00),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.Y, 0x80), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),

    # TSX
    ('TSX', [0xBA], 2,
     lambda cpu, mem: setattr(cpu, 'SP', 0x10) or setattr(cpu, 'X', 0x00),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.X, 0x10), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, 0))
    ),

    # TXA
    ('TXA', [0x8A], 2,
     lambda cpu, mem: setattr(cpu, 'X', 0xFF) or setattr(cpu, 'A', 0x00),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0xFF), t.assertEqual(cpu.P & FLAG_Z, 0), t.assertEqual(cpu.P & FLAG_N, FLAG_N))
    ),

    # TXS
    ('TXS', [0x9A], 2,
     lambda cpu, mem: setattr(cpu, 'X', 0x55) or setattr(cpu, 'SP', 0x00),
     lambda t, cpu, mem, cycles: t.assertEqual(cpu.SP, 0x55)
    ),

    # TYA
    ('TYA', [0x98], 2,
     lambda cpu, mem: setattr(cpu, 'Y', 0x00) or setattr(cpu, 'A', 0x00),
     lambda t, cpu, mem, cycles: (t.assertEqual(cpu.A, 0x00), t.assertEqual(cpu.P & FLAG_Z, FLAG_Z), t.assertEqual(cpu.P & FLAG_N, 0))
    ),
]

class Test6502IllegalOpcode(unittest.TestCase):

    def test_raises_with_message(self):
        mem = Memory()
        cpu = CPU6502(mem)
        mem.write(START, 0xFB)
        cpu.PC = START

        with self.assertRaises(NotImplementedError) as context:
            cpu.step()
        self.assertIn('Illegal opcode', str(context.exception))

class Test6502Opcodes(unittest.TestCase):

    def setUp(self):
        self.mem = Memory()
        self.cpu = CPU6502(self.mem)

    def reset_cpu(self):
        self.mem.data[:] = b'\x00' * 0x10000
        self.cpu.reset()

    def write_program(self, program):
        for i, byte in enumerate(program):
            addr = START + i
            self.mem.write(addr, byte)
        self.cpu.PC = START

# Dynamically generate a test function for each opcode
def generate_opcode_test(name, program, cycles, setup_fn, expected_fn):
    def test(self):
        self.reset_cpu()
        self.write_program(program)
        if setup_fn:
            setup_fn(self.cpu, self.mem)
        actual_cycles = self.cpu.step()
        # Verify cycles returned
        if cycles is not None:
            self.assertEqual(actual_cycles, cycles)
        if expected_fn:
            expected_fn(self, self.cpu, self.mem, actual_cycles)
    test.__name__ = f'test_{name}'
    return test

# Attach dynamically to the Test6502Opcodes class
for opcode_test in OPCODE_TESTS:
    name, program, cycles, setup_fn, expected_fn = opcode_test
    func = generate_opcode_test(name, program, cycles, setup_fn, expected_fn)
    setattr(Test6502Opcodes, func.__name__, func)


if __name__ == '__main__':
    unittest.main()

