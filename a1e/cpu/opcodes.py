# Copyright (C) 2025 John Schember <john@nachtimwald.com>
# SPDX-License-Identifier: GPL-3.0-or-later

# Supports the official 6502 opcodes

# Access table of opcode to tuple.
# The tuple is (opcode length, handler function)
# E.g: opcode_table[0xB8] = (1, CLV)
#
# This is the only part of the file that should be accessed directly.
# Everyting else supports this table.
opcode_table = [None] * 256

# The decorator registers (length_in_bytes, func) in opcode_table.
# Each opcode handler signature: func(cpu, operands) -> cycles (int)
# operands is a list of bytes.
def register_opcode(opcode: int, length: int):
    def decorator(func):
        opcode_table[opcode] = (length, func)
        return func
    return decorator


# Flags used by cpu.P register
FLAG_C = 0x01  # Carry
FLAG_Z = 0x02  # Zero
FLAG_I = 0x04  # Interrupt Disable
FLAG_D = 0x08  # Decimal Mode
FLAG_B = 0x10  # Break
FLAG_U = 0x20  # Unused, always 1 in pushes
FLAG_V = 0x40  # Overflow
FLAG_N = 0x80  # Negative


# Helpers
def _set_zn(cpu, val: int) -> None:
    val &= 0xFF
    cpu.P &= ~(FLAG_Z | FLAG_N)
    if val == 0:
        cpu.P |= FLAG_Z
    if val & 0x80:
        cpu.P |= FLAG_N

def _page_crossed(addr1: int, addr2: int) -> None:
    return (addr1 & 0xFF00) != (addr2 & 0xFF00)

def _stack_push(cpu, val: int) -> None:
    cpu.mem.write(0x0100 + cpu.SP, val & 0xFF)
    cpu.SP = (cpu.SP - 1) & 0xFF

def _stack_pop(cpu) -> int:
    cpu.SP = (cpu.SP + 1) & 0xFF
    return cpu.mem.read(0x0100 + cpu.SP)

def _branch_common(cpu, offset: int, condition: bool):
    cycles = 2
    if condition:
        old_pc = cpu.PC
        if offset & 0x80:
            offset -= 0x100
        cpu.PC = (cpu.PC + offset) & 0xFFFF
        cycles += 1
        if _page_crossed(old_pc, cpu.PC):
            cycles += 1
    return cycles

def _cmp_helper(cpu, reg_val: int, operand: int):
    operand &= 0xFF
    result = (reg_val - operand) & 0x1FF
    cpu.P = (cpu.P & ~FLAG_C) | (FLAG_C if reg_val >= operand else 0)
    _set_zn(cpu, result & 0xFF)

def _parse_operands_abs(operands: list[int]) -> int:
    lo = operands[0]
    hi = operands[1]
    return (hi << 8) | lo

def _parse_operands_abs_x(cpu, operands: list[int]) -> (int, int):
    base = _parse_operands_abs(operands)
    addr = (base + cpu.X) & 0xFFFF
    extra = 1 if _page_crossed(base, addr) else 0
    return addr, extra

def _parse_operands_abs_y(cpu, operands: list[int]) -> (int, int):
    base = _parse_operands_abs(operands)
    addr = (base + cpu.Y) & 0xFFFF
    extra = 1 if _page_crossed(base, addr) else 0
    return addr, extra

def _parse_operands_imm(operands: list[int]) -> int:
    return operands[0]

def _parse_operands_zp(operands: list[int]) -> int:
    return operands[0] & 0xFF

def _parse_operands_zp_x(cpu, operands: list[int]) -> int:
    return (operands[0] + cpu.X) & 0xFF

def _parse_operands_zp_y(cpu, operands: list[int]) -> int:
    return (operands[0] + cpu.Y) & 0xFF

def _parse_operands_ind_x(cpu, operands: list[int]) -> int:
    zp = (operands[0] + cpu.X) & 0xFF
    lo = cpu.mem.read(zp)
    hi = cpu.mem.read((zp + 1) & 0xFF)
    return (hi << 8) | lo

def _parse_operands_ind_y(cpu, operands: list[int]) -> (int, int):
    zp = operands[0] & 0xFF
    lo = cpu.mem.read(zp)
    hi = cpu.mem.read((zp + 1) & 0xFF)
    base = (hi << 8) | lo
    addr = (base + cpu.Y) & 0xFFFF
    extra = 1 if _page_crossed(base, addr) else 0
    return addr, extra


# ALU Helpers (ADC/SBC)

def _adc_decimal(cpu, a, m, carry_in):
    lo = (a & 0x0F) + (m & 0x0F) + carry_in
    hi = (a >> 4) + (m >> 4)
    if lo > 9:
        lo -= 10
        hi += 1
    if hi > 9:
        cpu.P |= FLAG_C
        hi -= 10
    else:
        cpu.P &= ~FLAG_C
    cpu.A = ((hi << 4) | (lo & 0x0F)) & 0xFF
    # Overflow flag has no meaning in BCD. Apply the same rule as binary for consistency.
    cpu.P = (cpu.P & ~(FLAG_N | FLAG_Z | FLAG_V)) | (FLAG_N if cpu.A & 0x80 else 0) | (FLAG_Z if cpu.A == 0 else 0)

def _adc_binary(cpu, a, m, carry_in):
    result = a + m + carry_in
    carry = 1 if result > 0xFF else 0
    cpu.A = result & 0xFF
    overflow = ((~(a ^ m) & (a ^ cpu.A)) & 0x80) != 0
    cpu.P = (cpu.P & ~(FLAG_C | FLAG_V)) | (FLAG_C if carry else 0) | (FLAG_V if overflow else 0)
    _set_zn(cpu, cpu.A)

def _adc(cpu, operand):
    carry_in = 1 if (cpu.P & FLAG_C) else 0
    a = cpu.A
    m = operand & 0xFF

    if cpu.P & FLAG_D:  # Decimal mode
        _adc_decimal(cpu, a, m, carry_in)
        return 1
    else:
        _adc_binary(cpu, a, m, carry_in)
    return 0

def _sbc_decimal(cpu, a, m, carry_in):
    lo = (a & 0x0F) - (m & 0x0F) - (1 - carry_in)
    hi = (a >> 4) - (m >> 4)
    if lo < 0:
        lo += 10
        hi -= 1
    if hi < 0:
        cpu.P &= ~FLAG_C
        hi += 10
    else:
        cpu.P |= FLAG_C
    cpu.A = ((hi << 4) | (lo & 0x0F)) & 0xFF
    # Overflow flag has no meaning in BCD. Apply the same rule as binary for consistency.
    cpu.P = (cpu.P & ~(FLAG_N | FLAG_Z | FLAG_V)) | (FLAG_N if cpu.A & 0x80 else 0) | (FLAG_Z if cpu.A == 0 else 0)

def _sbc_binary(cpu, a, m, carry_in):
    # Binary subtraction via two's complement
    inv_m = m ^ 0xFF
    result = a + inv_m + carry_in
    carry = 1 if result > 0xFF else 0
    cpu.A = result & 0xFF
    overflow = ((~(a ^ inv_m) & (a ^ cpu.A)) & 0x80) != 0
    cpu.P = (cpu.P & ~(FLAG_C | FLAG_V)) | (FLAG_C if carry else 0) | (FLAG_V if overflow else 0)
    _set_zn(cpu, cpu.A)

def _sbc(cpu, operand):
    carry_in = 1 if (cpu.P & FLAG_C) else 0
    a = cpu.A
    m = operand & 0xFF

    if cpu.P & FLAG_D:  # Decimal mode
        _sbc_decimal(cpu, a, m, carry_in)
        return 1
    else:
        _sbc_binary(cpu, a, m, carry_in)
    return 0


# opcodes
# convention for naming
# <INSTR>_<addressing>
# addressing
# - imm   = immediate
# - zp    = zeropage
# - zp_x  = zeropage,x
# - abs   = absolute
# - abs_x = absolute,x
# - abs_y = absolute,y
# - ind   = indirect
# - ind_x = (indirect,x)
# - ind_y = (indirect,y)
# - acc   = accumulator
# -       = relative / implied

@register_opcode(0x69, 2)
def ADC_imm(cpu, operands):
    m = _parse_operands_imm(operands)
    extra = _adc(cpu, m)
    return 2 + extra

@register_opcode(0x65, 2)
def ADC_zp(cpu, operands):
    addr = _parse_operands_zp(operands)
    m = cpu.mem.read(addr)
    extra = _adc(cpu, m)
    return 3 + extra

@register_opcode(0x75, 2)
def ADC_zp_x(cpu, operands):
    addr = _parse_operands_zp_x(cpu, operands)
    m = cpu.mem.read(addr)
    extra = _adc(cpu, m)
    return 4 + extra

@register_opcode(0x6D, 3)
def ADC_abs(cpu, operands):
    addr = _parse_operands_abs(operands)
    m = cpu.mem.read(addr)
    extra = _adc(cpu, m)
    return 4 + extra

@register_opcode(0x7D, 3)
def ADC_abs_x(cpu, operands):
    addr, extra = _parse_operands_abs_x(cpu, operands)
    m = cpu.mem.read(addr)
    extra += _adc(cpu, m)
    return 4 + extra

@register_opcode(0x79, 3)
def ADC_abs_y(cpu, operands):
    addr, extra = _parse_operands_abs_y(cpu, operands)
    m = cpu.mem.read(addr)
    extra += _adc(cpu, m)
    return 4 + extra

@register_opcode(0x61, 2)
def ADC_ind_x(cpu, operands):
    addr = _parse_operands_ind_x(cpu, operands)
    m = cpu.mem.read(addr)
    extra =_adc(cpu, m)
    return 6 + extra

@register_opcode(0x71, 2)
def ADC_ind_y(cpu, operands):
    addr, extra = _parse_operands_ind_y(cpu, operands)
    m = cpu.mem.read(addr)
    extra += _adc(cpu, m)
    return 5 + extra

@register_opcode(0x29, 2)
def AND_imm(cpu, operands):
    cpu.A &= _parse_operands_imm(operands)
    _set_zn(cpu, cpu.A)
    return 2

@register_opcode(0x25, 2)
def AND_zp(cpu, operands):
    cpu.A &= cpu.mem.read(_parse_operands_zp(operands))
    _set_zn(cpu, cpu.A)
    return 3

@register_opcode(0x35, 2)
def AND_zp_x(cpu, operands):
    cpu.A &= cpu.mem.read(_parse_operands_zp_x(cpu, operands))
    _set_zn(cpu, cpu.A)
    return 4

@register_opcode(0x2D, 3)
def AND_abs(cpu, operands):
    cpu.A &= cpu.mem.read(_parse_operands_abs(operands))
    _set_zn(cpu, cpu.A)
    return 4

@register_opcode(0x3D, 3)
def AND_abs_x(cpu, operands):
    addr, extra = _parse_operands_abs_x(cpu, operands)
    cpu.A &= cpu.mem.read(addr)
    _set_zn(cpu, cpu.A)
    return 4 + extra

@register_opcode(0x39, 3)
def AND_abs_y(cpu, operands):
    addr, extra = _parse_operands_abs_y(cpu, operands)
    cpu.A &= cpu.mem.read(addr)
    _set_zn(cpu, cpu.A)
    return 4 + extra

@register_opcode(0x21, 2)
def AND_ind_x(cpu, operands):
    addr = _parse_operands_ind_x(cpu, operands)
    cpu.A &= cpu.mem.read(addr)
    _set_zn(cpu, cpu.A)
    return 6

@register_opcode(0x31, 2)
def AND_ind_y(cpu, operands):
    addr, extra = _parse_operands_ind_y(cpu, operands)
    cpu.A &= cpu.mem.read(addr)
    _set_zn(cpu, cpu.A)
    return 5 + extra

@register_opcode(0x0A, 1)
def ASL_acc(cpu, operands):
    v = cpu.A
    carry = (v >> 7) & 1
    cpu.A = (v << 1) & 0xFF
    cpu.P = (cpu.P & ~FLAG_C) | (FLAG_C if carry else 0)
    _set_zn(cpu, cpu.A)
    return 2

@register_opcode(0x06, 2)
def ASL_zp(cpu, operands):
    addr = _parse_operands_zp(operands)
    v = cpu.mem.read(addr)
    carry = (v >> 7) & 1
    res = (v << 1) & 0xFF
    cpu.mem.write(addr, res)
    cpu.P = (cpu.P & ~FLAG_C) | (FLAG_C if carry else 0)
    _set_zn(cpu, res)
    return 5

@register_opcode(0x16, 2)
def ASL_zp_x(cpu, operands):
    addr = _parse_operands_zp_x(cpu, operands)
    v = cpu.mem.read(addr)
    carry = (v >> 7) & 1
    res = (v << 1) & 0xFF
    cpu.mem.write(addr, res)
    cpu.P = (cpu.P & ~FLAG_C) | (FLAG_C if carry else 0)
    _set_zn(cpu, res)
    return 6

@register_opcode(0x0E, 3)
def ASL_abs(cpu, operands):
    addr = _parse_operands_abs(operands)
    v = cpu.mem.read(addr)
    carry = (v >> 7) & 1
    res = (v << 1) & 0xFF
    cpu.mem.write(addr, res)
    cpu.P = (cpu.P & ~FLAG_C) | (FLAG_C if carry else 0)
    _set_zn(cpu, res)
    return 6

@register_opcode(0x1E, 3)
def ASL_abs_x(cpu, operands):
    addr = (_parse_operands_abs(operands) + cpu.X) & 0xFFFF
    v = cpu.mem.read(addr)
    carry = (v >> 7) & 1
    res = (v << 1) & 0xFF
    cpu.mem.write(addr, res)
    cpu.P = (cpu.P & ~FLAG_C) | (FLAG_C if carry else 0)
    _set_zn(cpu, res)
    return 7

@register_opcode(0x90, 2)
def BCC(cpu, operands):
    offset = operands[0]
    return _branch_common(cpu, offset, (cpu.P & FLAG_C) == 0)

@register_opcode(0xB0, 2)
def BCS(cpu, operands):
    offset = operands[0]
    return _branch_common(cpu, offset, (cpu.P & FLAG_C) != 0)

@register_opcode(0xF0, 2)
def BEQ(cpu, operands):
    offset = operands[0]
    return _branch_common(cpu, offset, (cpu.P & FLAG_Z) != 0)

@register_opcode(0x24, 2)
def BIT_zp(cpu, operands):
    val = cpu.mem.read(_parse_operands_zp(operands))
    res = cpu.A & val
    cpu.P = (cpu.P & ~(FLAG_Z | FLAG_V | FLAG_N)) | (FLAG_Z if res == 0 else 0) | (FLAG_V if (val & 0x40) else 0) | (FLAG_N if (val & 0x80) else 0)
    return 3

@register_opcode(0x2C, 3)
def BIT_abs(cpu, operands):
    addr = _parse_operands_abs(operands)
    val = cpu.mem.read(addr)
    res = cpu.A & val
    cpu.P = (cpu.P & ~(FLAG_Z | FLAG_V | FLAG_N)) | (FLAG_Z if res == 0 else 0) | (FLAG_V if (val & 0x40) else 0) | (FLAG_N if (val & 0x80) else 0)
    return 4

@register_opcode(0x30, 2)
def BMI(cpu, operands):
    offset = operands[0]
    return _branch_common(cpu, offset, (cpu.P & FLAG_N) != 0)

@register_opcode(0xD0, 2)
def BNE(cpu, operands):
    offset = operands[0]
    return _branch_common(cpu, offset, (cpu.P & FLAG_Z) == 0)

@register_opcode(0x10, 2)
def BPL(cpu, operands):
    offset = operands[0]
    return _branch_common(cpu, offset, (cpu.P & FLAG_N) == 0)

@register_opcode(0x00, 1)
def BRK(cpu, operands):
    ret = cpu.PC + 1
    _stack_push(cpu, (ret >> 8) & 0xFF)
    _stack_push(cpu, ret & 0xFF)
    _stack_push(cpu, cpu.P | FLAG_B | FLAG_U)
    cpu.P |= FLAG_I
    lo = cpu.mem.read(0xFFFE)
    hi = cpu.mem.read(0xFFFF)
    cpu.PC = (hi << 8) | lo
    return 7

@register_opcode(0x50, 2)
def BVC(cpu, operands):
    offset = operands[0]
    return _branch_common(cpu, offset, (cpu.P & FLAG_V) == 0)

@register_opcode(0x70, 2)
def BVS(cpu, operands):
    offset = operands[0]
    return _branch_common(cpu, offset, (cpu.P & FLAG_V) != 0)

@register_opcode(0x18, 1)
def CLC(cpu, operands):
    cpu.P &= ~FLAG_C
    return 2

@register_opcode(0xD8, 1)
def CLD(cpu, operands):
    cpu.P &= ~FLAG_D
    return 2

@register_opcode(0x58, 1)
def CLI(cpu, operands):
    cpu.P &= ~FLAG_I
    return 2

@register_opcode(0xB8, 1)
def CLV(cpu, operands):
    cpu.P &= ~FLAG_V
    return 2

@register_opcode(0xC9, 2)
def CMP_imm(cpu, operands):
    _cmp_helper(cpu, cpu.A, _parse_operands_imm(operands))
    return 2

@register_opcode(0xC5, 2)
def CMP_zp(cpu, operands):
    _cmp_helper(cpu, cpu.A, cpu.mem.read(_parse_operands_zp(operands)))
    return 3

@register_opcode(0xD5, 2)
def CMP_zp_x(cpu, operands):
    _cmp_helper(cpu, cpu.A, cpu.mem.read(_parse_operands_zp_x(cpu, operands)))
    return 4

@register_opcode(0xCD, 3)
def CMP_abs(cpu, operands):
    _cmp_helper(cpu, cpu.A, cpu.mem.read(_parse_operands_abs(operands)))
    return 4

@register_opcode(0xDD, 3)
def CMP_abs_x(cpu, operands):
    addr, extra = _parse_operands_abs_x(cpu, operands)
    _cmp_helper(cpu, cpu.A, cpu.mem.read(addr))
    return 4 + extra

@register_opcode(0xD9, 3)
def CMP_abs_y(cpu, operands):
    addr, extra = _parse_operands_abs_y(cpu, operands)
    _cmp_helper(cpu, cpu.A, cpu.mem.read(addr))
    return 4 + extra

@register_opcode(0xC1, 2)
def CMP_ind_x(cpu, operands):
    addr = _parse_operands_ind_x(cpu, operands)
    _cmp_helper(cpu, cpu.A, cpu.mem.read(addr))
    return 6

@register_opcode(0xD1, 2)
def CMP_ind_y(cpu, operands):
    addr, extra = _parse_operands_ind_y(cpu, operands)
    _cmp_helper(cpu, cpu.A, cpu.mem.read(addr))
    return 5 + extra

@register_opcode(0xE0, 2)
def CPX_imm(cpu, operands):
    _cmp_helper(cpu, cpu.X, _parse_operands_imm(operands))
    return 2

@register_opcode(0xE4, 2)
def CPX_zp(cpu, operands):
    _cmp_helper(cpu, cpu.X, cpu.mem.read(_parse_operands_zp(operands)))
    return 3

@register_opcode(0xEC, 3)
def CPX_abs(cpu, operands):
    _cmp_helper(cpu, cpu.X, cpu.mem.read(_parse_operands_abs(operands)))
    return 4

@register_opcode(0xC0, 2)
def CPY_imm(cpu, operands):
    _cmp_helper(cpu, cpu.Y, _parse_operands_imm(operands))
    return 2

@register_opcode(0xC4, 2)
def CPY_zp(cpu, operands):
    _cmp_helper(cpu, cpu.Y, cpu.mem.read(_parse_operands_zp(operands)))
    return 3

@register_opcode(0xCC, 3)
def CPY_abs(cpu, operands):
    _cmp_helper(cpu, cpu.Y, cpu.mem.read(_parse_operands_abs(operands)))
    return 4

@register_opcode(0xC6, 2)
def DEC_zp(cpu, operands):
    addr = _parse_operands_zp(operands)
    v = (cpu.mem.read(addr) - 1) & 0xFF
    cpu.mem.write(addr, v)
    _set_zn(cpu, v)
    return 5

@register_opcode(0xD6, 2)
def DEC_zp_x(cpu, operands):
    addr = _parse_operands_zp_x(cpu, operands)
    v = (cpu.mem.read(addr) - 1) & 0xFF
    cpu.mem.write(addr, v)
    _set_zn(cpu, v)
    return 6

@register_opcode(0xCE, 3)
def DEC_abs(cpu, operands):
    addr = _parse_operands_abs(operands)
    v = (cpu.mem.read(addr) - 1) & 0xFF
    cpu.mem.write(addr, v)
    _set_zn(cpu, v)
    return 6

@register_opcode(0xDE, 3)
def DEC_abs_x(cpu, operands):
    addr = (_parse_operands_abs(operands) + cpu.X) & 0xFFFF
    v = (cpu.mem.read(addr) - 1) & 0xFF
    cpu.mem.write(addr, v)
    _set_zn(cpu, v)
    return 7

@register_opcode(0xCA, 1)
def DEX(cpu, operands):
    cpu.X = (cpu.X - 1) & 0xFF
    _set_zn(cpu, cpu.X)
    return 2

@register_opcode(0x88, 1)
def DEY(cpu, operands):
    cpu.Y = (cpu.Y - 1) & 0xFF
    _set_zn(cpu, cpu.Y)
    return 2

@register_opcode(0x49, 2)
def EOR_imm(cpu, operands):
    cpu.A ^= _parse_operands_imm(operands)
    _set_zn(cpu, cpu.A)
    return 2

@register_opcode(0x45, 2)
def EOR_zp(cpu, operands):
    cpu.A ^= cpu.mem.read(_parse_operands_zp(operands))
    _set_zn(cpu, cpu.A)
    return 3

@register_opcode(0x55, 2)
def EOR_zp_x(cpu, operands):
    cpu.A ^= cpu.mem.read(_parse_operands_zp_x(cpu, operands))
    _set_zn(cpu, cpu.A)
    return 4

@register_opcode(0x4D, 3)
def EOR_abs(cpu, operands):
    cpu.A ^= cpu.mem.read(_parse_operands_abs(operands))
    _set_zn(cpu, cpu.A)
    return 4

@register_opcode(0x5D, 3)
def EOR_abs_x(cpu, operands):
    addr, extra = _parse_operands_abs_x(cpu, operands)
    cpu.A ^= cpu.mem.read(addr)
    _set_zn(cpu, cpu.A)
    return 4 + extra

@register_opcode(0x59, 3)
def EOR_abs_y(cpu, operands):
    addr, extra = _parse_operands_abs_y(cpu, operands)
    cpu.A ^= cpu.mem.read(addr)
    _set_zn(cpu, cpu.A)
    return 4 + extra

@register_opcode(0x41, 2)
def EOR_ind_x(cpu, operands):
    addr = _parse_operands_ind_x(cpu, operands)
    cpu.A ^= cpu.mem.read(addr)
    _set_zn(cpu, cpu.A)
    return 6

@register_opcode(0x51, 2)
def EOR_ind_y(cpu, operands):
    addr, extra = _parse_operands_ind_y(cpu, operands)
    cpu.A ^= cpu.mem.read(addr)
    _set_zn(cpu, cpu.A)
    return 5 + extra

@register_opcode(0xE6, 2)
def INC_zp(cpu, operands):
    addr = _parse_operands_zp(operands)
    v = (cpu.mem.read(addr) + 1) & 0xFF
    cpu.mem.write(addr, v)
    _set_zn(cpu, v)
    return 5

@register_opcode(0xF6, 2)
def INC_zp_x(cpu, operands):
    addr = _parse_operands_zp_x(cpu, operands)
    v = (cpu.mem.read(addr) + 1) & 0xFF
    cpu.mem.write(addr, v)
    _set_zn(cpu, v)
    return 6

@register_opcode(0xEE, 3)
def INC_abs(cpu, operands):
    addr = _parse_operands_abs(operands)
    v = (cpu.mem.read(addr) + 1) & 0xFF
    cpu.mem.write(addr, v)
    _set_zn(cpu, v)
    return 6

@register_opcode(0xFE, 3)  # INC abs,X
def INC_abs_x(cpu, operands):
    addr = (_parse_operands_abs(operands) + cpu.X) & 0xFFFF
    v = (cpu.mem.read(addr) + 1) & 0xFF
    cpu.mem.write(addr, v)
    _set_zn(cpu, v)
    return 7

@register_opcode(0xE8, 1)
def INX(cpu, operands):
    cpu.X = (cpu.X + 1) & 0xFF
    _set_zn(cpu, cpu.X)
    return 2

@register_opcode(0xC8, 1)
def INY(cpu, operands):
    cpu.Y = (cpu.Y + 1) & 0xFF
    _set_zn(cpu, cpu.Y)
    return 2

@register_opcode(0x4C, 3)
def JMP_abs(cpu, operands):
    cpu.PC = _parse_operands_abs(operands)
    return 3

@register_opcode(0x6C, 3)
def JMP_ind(cpu, operands):
    ptr = _parse_operands_abs(operands)
    lo = cpu.mem.read(ptr)
    hi_addr = (ptr & 0xFF00) | ((ptr + 1) & 0xFF)
    hi = cpu.mem.read(hi_addr)
    cpu.PC = (hi << 8) | lo
    return 5

@register_opcode(0x20, 3)
def JSR_abs(cpu, operands):
    addr = _parse_operands_abs(operands)
    ret = (cpu.PC - 1) & 0xFFFF
    _stack_push(cpu, (ret >> 8) & 0xFF)
    _stack_push(cpu, ret & 0xFF)
    cpu.PC = addr
    return 6

@register_opcode(0xA9, 2)
def LDA_imm(cpu, operands):
    cpu.A = _parse_operands_imm(operands) & 0xFF
    _set_zn(cpu, cpu.A)
    return 2

@register_opcode(0xA5, 2)
def LDA_zp(cpu, operands):
    addr = _parse_operands_zp(operands)
    cpu.A = cpu.mem.read(addr)
    _set_zn(cpu, cpu.A)
    return 3

@register_opcode(0xB5, 2)
def LDA_zp_x(cpu, operands):
    addr = _parse_operands_zp_x(cpu, operands)
    cpu.A = cpu.mem.read(addr)
    _set_zn(cpu, cpu.A)
    return 4

@register_opcode(0xAD, 3)
def LDA_abs(cpu, operands):
    addr = _parse_operands_abs(operands)
    cpu.A = cpu.mem.read(addr)
    _set_zn(cpu, cpu.A)
    return 4

@register_opcode(0xBD, 3)
def LDA_abs_x(cpu, operands):
    addr, extra = _parse_operands_abs_x(cpu, operands)
    cpu.A = cpu.mem.read(addr)
    _set_zn(cpu, cpu.A)
    return 4 + extra

@register_opcode(0xB9, 3)
def LDA_abs_y(cpu, operands):
    addr, extra = _parse_operands_abs_y(cpu, operands)
    cpu.A = cpu.mem.read(addr)
    _set_zn(cpu, cpu.A)
    return 4 + extra

@register_opcode(0xA1, 2)
def LDA_ind_x(cpu, operands):
    addr = _parse_operands_ind_x(cpu, operands)
    cpu.A = cpu.mem.read(addr)
    _set_zn(cpu, cpu.A)
    return 6

@register_opcode(0xB1, 2)
def LDA_ind_y(cpu, operands):
    addr, extra = _parse_operands_ind_y(cpu, operands)
    cpu.A = cpu.mem.read(addr)
    _set_zn(cpu, cpu.A)
    return 5 + extra

@register_opcode(0xA2, 2)
def LDX_imm(cpu, operands):
    cpu.X = _parse_operands_imm(operands) & 0xFF
    _set_zn(cpu, cpu.X)
    return 2

@register_opcode(0xA6, 2)
def LDX_zp(cpu, operands):
    addr = _parse_operands_zp(operands)
    cpu.X = cpu.mem.read(addr)
    _set_zn(cpu, cpu.X)
    return 3

@register_opcode(0xB6, 2)
def LDX_zp_y(cpu, operands):
    addr = _parse_operands_zp_y(cpu, operands)
    cpu.X = cpu.mem.read(addr)
    _set_zn(cpu, cpu.X)
    return 4

@register_opcode(0xAE, 3)
def LDX_abs(cpu, operands):
    addr = _parse_operands_abs(operands)
    cpu.X = cpu.mem.read(addr)
    _set_zn(cpu, cpu.X)
    return 4

@register_opcode(0xBE, 3)
def LDX_abs_y(cpu, operands):
    addr, extra = _parse_operands_abs_y(cpu, operands)
    cpu.X = cpu.mem.read(addr)
    _set_zn(cpu, cpu.X)
    return 4 + extra

@register_opcode(0xA0, 2)
def LDY_imm(cpu, operands):
    cpu.Y = _parse_operands_imm(operands) & 0xFF
    _set_zn(cpu, cpu.Y)
    return 2

@register_opcode(0xA4, 2)
def LDY_zp(cpu, operands):
    addr = _parse_operands_zp(operands)
    cpu.Y = cpu.mem.read(addr)
    _set_zn(cpu, cpu.Y)
    return 3

@register_opcode(0xB4, 2)
def LDY_zp_x(cpu, operands):
    addr = _parse_operands_zp_x(cpu, operands)
    cpu.Y = cpu.mem.read(addr)
    _set_zn(cpu, cpu.Y)
    return 4

@register_opcode(0xAC, 3)
def LDY_abs(cpu, operands):
    addr = _parse_operands_abs(operands)
    cpu.Y = cpu.mem.read(addr)
    _set_zn(cpu, cpu.Y)
    return 4

@register_opcode(0xBC, 3)
def LDY_abs_x(cpu, operands):
    addr, extra = _parse_operands_abs_x(cpu, operands)
    cpu.Y = cpu.mem.read(addr)
    _set_zn(cpu, cpu.Y)
    return 4 + extra

@register_opcode(0x4A, 1)
def LSR_acc(cpu, operands):
    v = cpu.A
    carry = v & 1
    res = (v >> 1) & 0xFF
    cpu.A = res
    cpu.P = (cpu.P & ~FLAG_C) | (FLAG_C if carry else 0)
    _set_zn(cpu, cpu.A)
    return 2

@register_opcode(0x46, 2)
def LSR_zp(cpu, operands):
    addr = _parse_operands_zp(operands)
    v = cpu.mem.read(addr)
    carry = v & 1
    res = (v >> 1) & 0xFF
    cpu.mem.write(addr, res)
    cpu.P = (cpu.P & ~FLAG_C) | (FLAG_C if carry else 0)
    _set_zn(cpu, res)
    return 5

@register_opcode(0x56, 2)
def LSR_zp_x(cpu, operands):
    addr = _parse_operands_zp_x(cpu, operands)
    v = cpu.mem.read(addr)
    carry = v & 1
    res = (v >> 1) & 0xFF
    cpu.mem.write(addr, res)
    cpu.P = (cpu.P & ~FLAG_C) | (FLAG_C if carry else 0)
    _set_zn(cpu, res)
    return 6

@register_opcode(0x4E, 3)
def LSR_abs(cpu, operands):
    addr = _parse_operands_abs(operands)
    v = cpu.mem.read(addr)
    carry = v & 1
    res = (v >> 1) & 0xFF
    cpu.mem.write(addr, res)
    cpu.P = (cpu.P & ~FLAG_C) | (FLAG_C if carry else 0)
    _set_zn(cpu, res)
    return 6

@register_opcode(0x5E, 3)
def LSR_abs_x(cpu, operands):
    addr = (_parse_operands_abs(operands) + cpu.X) & 0xFFFF
    v = cpu.mem.read(addr)
    carry = v & 1
    res = (v >> 1) & 0xFF
    cpu.mem.write(addr, res)
    cpu.P = (cpu.P & ~FLAG_C) | (FLAG_C if carry else 0)
    _set_zn(cpu, res)
    return 7

@register_opcode(0xEA, 1)
def NOP(cpu, operands):
    return 2

@register_opcode(0x09, 2)
def ORA_imm(cpu, operands):
    cpu.A |= _parse_operands_imm(operands)
    _set_zn(cpu, cpu.A)
    return 2

@register_opcode(0x05, 2)
def ORA_zp(cpu, operands):
    cpu.A |= cpu.mem.read(_parse_operands_zp(operands))
    _set_zn(cpu, cpu.A)
    return 3

@register_opcode(0x15, 2)
def ORA_zp_x(cpu, operands):
    cpu.A |= cpu.mem.read(_parse_operands_zp_x(cpu, operands))
    _set_zn(cpu, cpu.A)
    return 4

@register_opcode(0x0D, 3)
def ORA_abs(cpu, operands):
    cpu.A |= cpu.mem.read(_parse_operands_abs(operands))
    _set_zn(cpu, cpu.A)
    return 4

@register_opcode(0x1D, 3)
def ORA_abs_x(cpu, operands):
    addr, extra = _parse_operands_abs_x(cpu, operands)
    cpu.A |= cpu.mem.read(addr)
    _set_zn(cpu, cpu.A)
    return 4 + extra

@register_opcode(0x19, 3)
def ORA_abs_y(cpu, operands):
    addr, extra = _parse_operands_abs_y(cpu, operands)
    cpu.A |= cpu.mem.read(addr)
    _set_zn(cpu, cpu.A)
    return 4 + extra

@register_opcode(0x01, 2)
def ORA_ind_x(cpu, operands):
    addr = _parse_operands_ind_x(cpu, operands)
    cpu.A |= cpu.mem.read(addr)
    _set_zn(cpu, cpu.A)
    return 6

@register_opcode(0x11, 2)
def ORA_ind_y(cpu, operands):
    addr, extra = _parse_operands_ind_y(cpu, operands)
    cpu.A |= cpu.mem.read(addr)
    _set_zn(cpu, cpu.A)
    return 5 + extra

@register_opcode(0x48, 1)
def PHA(cpu, operands):
    _stack_push(cpu, cpu.A)
    return 3

@register_opcode(0x68, 1)
def PLA(cpu, operands):
    val = _stack_pop(cpu)
    cpu.A = val
    _set_zn(cpu, cpu.A)
    return 4

@register_opcode(0x08, 1)
def PHP(cpu, operands):
    _stack_push(cpu, cpu.P | FLAG_B | FLAG_U)
    return 3

@register_opcode(0x28, 1)
def PLP(cpu, operands):
    val = _stack_pop(cpu)
    cpu.P = (val & ~FLAG_B) | FLAG_U
    return 4

@register_opcode(0x2A, 1)
def ROL_acc(cpu, operands):
    carry_in = 1 if (cpu.P & FLAG_C) else 0
    v = cpu.A
    carry_out = (v >> 7) & 1
    res = ((v << 1) | carry_in) & 0xFF
    cpu.A = res
    cpu.P = (cpu.P & ~FLAG_C) | (FLAG_C if carry_out else 0)
    _set_zn(cpu, cpu.A)
    return 2

@register_opcode(0x26, 2)
def ROL_zp(cpu, operands):
    addr = _parse_operands_zp(operands)
    v = cpu.mem.read(addr)
    carry_in = 1 if (cpu.P & FLAG_C) else 0
    carry_out = (v >> 7) & 1
    res = ((v << 1) | carry_in) & 0xFF
    cpu.mem.write(addr, res)
    cpu.P = (cpu.P & ~FLAG_C) | (FLAG_C if carry_out else 0)
    _set_zn(cpu, res)
    return 5

@register_opcode(0x36, 2)
def ROL_zp_x(cpu, operands):
    addr = _parse_operands_zp_x(cpu, operands)
    v = cpu.mem.read(addr)
    carry_in = 1 if (cpu.P & FLAG_C) else 0
    carry_out = (v >> 7) & 1
    res = ((v << 1) | carry_in) & 0xFF
    cpu.mem.write(addr, res)
    cpu.P = (cpu.P & ~FLAG_C) | (FLAG_C if carry_out else 0)
    _set_zn(cpu, res)
    return 6

@register_opcode(0x2E, 3)
def ROL_abs(cpu, operands):
    addr = _parse_operands_abs(operands)
    v = cpu.mem.read(addr)
    carry_in = 1 if (cpu.P & FLAG_C) else 0
    carry_out = (v >> 7) & 1
    res = ((v << 1) | carry_in) & 0xFF
    cpu.mem.write(addr, res)
    cpu.P = (cpu.P & ~FLAG_C) | (FLAG_C if carry_out else 0)
    _set_zn(cpu, res)
    return 6

@register_opcode(0x3E, 3)
def ROL_abs_x(cpu, operands):
    addr = (_parse_operands_abs(operands) + cpu.X) & 0xFFFF
    v = cpu.mem.read(addr)
    carry_in = 1 if (cpu.P & FLAG_C) else 0
    carry_out = (v >> 7) & 1
    res = ((v << 1) | carry_in) & 0xFF
    cpu.mem.write(addr, res)
    cpu.P = (cpu.P & ~FLAG_C) | (FLAG_C if carry_out else 0)
    _set_zn(cpu, res)
    return 7

@register_opcode(0x6A, 1)
def ROR_acc(cpu, operands):
    carry_in = 1 if (cpu.P & FLAG_C) else 0
    v = cpu.A
    carry_out = v & 1
    res = ((carry_in << 7) | (v >> 1)) & 0xFF
    cpu.A = res
    cpu.P = (cpu.P & ~FLAG_C) | (FLAG_C if carry_out else 0)
    _set_zn(cpu, cpu.A)
    return 2

@register_opcode(0x66, 2)
def ROR_zp(cpu, operands):
    addr = _parse_operands_zp(operands)
    v = cpu.mem.read(addr)
    carry_in = 1 if (cpu.P & FLAG_C) else 0
    carry_out = v & 1
    res = ((carry_in << 7) | (v >> 1)) & 0xFF
    cpu.mem.write(addr, res)
    cpu.P = (cpu.P & ~FLAG_C) | (FLAG_C if carry_out else 0)
    _set_zn(cpu, res)
    return 5

@register_opcode(0x76, 2)
def ROR_zp_x(cpu, operands):
    addr = _parse_operands_zp_x(cpu, operands)
    v = cpu.mem.read(addr)
    carry_in = 1 if (cpu.P & FLAG_C) else 0
    carry_out = v & 1
    res = ((carry_in << 7) | (v >> 1)) & 0xFF
    cpu.mem.write(addr, res)
    cpu.P = (cpu.P & ~FLAG_C) | (FLAG_C if carry_out else 0)
    _set_zn(cpu, res)
    return 6

@register_opcode(0x6E, 3)
def ROR_abs(cpu, operands):
    addr = _parse_operands_abs(operands)
    v = cpu.mem.read(addr)
    carry_in = 1 if (cpu.P & FLAG_C) else 0
    carry_out = v & 1
    res = ((carry_in << 7) | (v >> 1)) & 0xFF
    cpu.mem.write(addr, res)
    cpu.P = (cpu.P & ~FLAG_C) | (FLAG_C if carry_out else 0)
    _set_zn(cpu, res)
    return 6

@register_opcode(0x7E, 3)
def ROR_abs_x(cpu, operands):
    addr = (_parse_operands_abs(operands) + cpu.X) & 0xFFFF
    v = cpu.mem.read(addr)
    carry_in = 1 if (cpu.P & FLAG_C) else 0
    carry_out = v & 1
    res = ((carry_in << 7) | (v >> 1)) & 0xFF
    cpu.mem.write(addr, res)
    cpu.P = (cpu.P & ~FLAG_C) | (FLAG_C if carry_out else 0)
    _set_zn(cpu, res)
    return 7

@register_opcode(0x40, 1)
def RTI(cpu, operands):
    p = _stack_pop(cpu)
    cpu.P = (p & ~FLAG_B) | FLAG_U
    lo = _stack_pop(cpu)
    hi = _stack_pop(cpu)
    cpu.PC = (hi << 8) | lo
    return 6

@register_opcode(0x60, 1)
def RTS(cpu, operands):
    lo = _stack_pop(cpu)
    hi = _stack_pop(cpu)
    ret = (hi << 8) | lo
    cpu.PC = (ret + 1) & 0xFFFF
    return 6

@register_opcode(0xE9, 2)
def SBC_imm(cpu, operands):
    m = _parse_operands_imm(operands)
    extra = _sbc(cpu, m)
    return 2 + extra

@register_opcode(0xE5, 2)
def SBC_zp(cpu, operands):
    addr = _parse_operands_zp(operands)
    m = cpu.mem.read(addr)
    extra = _sbc(cpu, m)
    return 3 + extra

@register_opcode(0xF5, 2)
def SBC_zp_x(cpu, operands):
    addr = _parse_operands_zp_x(cpu, operands)
    m = cpu.mem.read(addr)
    extra = _sbc(cpu, m)
    return 4 + extra

@register_opcode(0xED, 3)
def SBC_abs(cpu, operands):
    addr = _parse_operands_abs(operands)
    m = cpu.mem.read(addr)
    extra = _sbc(cpu, m)
    return 4 + extra

@register_opcode(0xFD, 3)
def SBC_abs_x(cpu, operands):
    addr, extra = _parse_operands_abs_x(cpu, operands)
    m = cpu.mem.read(addr)
    extra += _sbc(cpu, m)
    return 4 + extra

@register_opcode(0xF9, 3)
def SBC_abs_y(cpu, operands):
    addr, extra = _parse_operands_abs_y(cpu, operands)
    m = cpu.mem.read(addr)
    extra += _sbc(cpu, m)
    return 4 + extra

@register_opcode(0xE1, 2)
def SBC_ind_x(cpu, operands):
    addr = _parse_operands_ind_x(cpu, operands)
    m = cpu.mem.read(addr)
    extra = _sbc(cpu, m)
    return 6 + extra

@register_opcode(0xF1, 2)
def SBC_ind_y(cpu, operands):
    addr, extra = _parse_operands_ind_y(cpu, operands)
    m = cpu.mem.read(addr)
    extra += _sbc(cpu, m)
    return 5 + extra

@register_opcode(0x38, 1)
def SEC(cpu, operands):
    cpu.P |= FLAG_C
    return 2

@register_opcode(0xF8, 1)
def SED(cpu, operands):
    cpu.P |= FLAG_D
    return 2

@register_opcode(0x78, 1)
def SEI(cpu, operands):
    cpu.P |= FLAG_I
    return 2

@register_opcode(0x85, 2)
def STA_zp(cpu, operands):
    addr = _parse_operands_zp(operands)
    cpu.mem.write(addr, cpu.A)
    return 3

@register_opcode(0x95, 2)
def STA_zp_x(cpu, operands):
    addr = _parse_operands_zp_x(cpu, operands)
    cpu.mem.write(addr, cpu.A)
    return 4

@register_opcode(0x8D, 3)
def STA_abs(cpu, operands):
    addr = _parse_operands_abs(operands)
    cpu.mem.write(addr, cpu.A)
    return 4

@register_opcode(0x9D, 3)
def STA_abs_x(cpu, operands):
    addr = (_parse_operands_abs(operands) + cpu.X) & 0xFFFF
    cpu.mem.write(addr, cpu.A)
    return 5

@register_opcode(0x99, 3)
def STA_abs_y(cpu, operands):
    addr = (_parse_operands_abs(operands) + cpu.Y) & 0xFFFF
    cpu.mem.write(addr, cpu.A)
    return 5

@register_opcode(0x81, 2)
def STA_ind_x(cpu, operands):
    zp = (operands[0] + cpu.X) & 0xFF
    lo = cpu.mem.read(zp)
    hi = cpu.mem.read((zp + 1) & 0xFF)
    addr = (hi << 8) | lo
    cpu.mem.write(addr, cpu.A)
    return 6

@register_opcode(0x91, 2)
def STA_ind_y(cpu, operands):
    zp = operands[0] & 0xFF
    lo = cpu.mem.read(zp)
    hi = cpu.mem.read((zp + 1) & 0xFF)
    addr = ((hi << 8) | lo) + cpu.Y
    addr &= 0xFFFF
    cpu.mem.write(addr, cpu.A)
    return 6

@register_opcode(0x86, 2)
def STX_zp(cpu, operands):
    cpu.mem.write(_parse_operands_zp(operands), cpu.X)
    return 3

@register_opcode(0x96, 2)
def STX_zp_y(cpu, operands):
    cpu.mem.write(_parse_operands_zp_y(cpu, operands), cpu.X)
    return 4

@register_opcode(0x8E, 3)
def STX_abs(cpu, operands):
    cpu.mem.write(_parse_operands_abs(operands), cpu.X)
    return 4

@register_opcode(0x84, 2)
def STY_zp(cpu, operands):
    cpu.mem.write(_parse_operands_zp(operands), cpu.Y)
    return 3

@register_opcode(0x94, 2)
def STY_zp_x(cpu, operands):
    cpu.mem.write(_parse_operands_zp_x(cpu, operands), cpu.Y)
    return 4

@register_opcode(0x8C, 3)
def STY_abs(cpu, operands):
    cpu.mem.write(_parse_operands_abs(operands), cpu.Y)
    return 4

@register_opcode(0xAA, 1)
def TAX(cpu, operands):
    cpu.X = cpu.A & 0xFF
    _set_zn(cpu, cpu.X)
    return 2

@register_opcode(0xA8, 1)
def TAY(cpu, operands):
    cpu.Y = cpu.A & 0xFF
    _set_zn(cpu, cpu.Y)
    return 2

@register_opcode(0xBA, 1)
def TSX(cpu, operands):
    cpu.X = cpu.SP & 0xFF
    _set_zn(cpu, cpu.X)
    return 2

@register_opcode(0x8A, 1)
def TXA(cpu, operands):
    cpu.A = cpu.X & 0xFF
    _set_zn(cpu, cpu.A)
    return 2

@register_opcode(0x9A, 1)
def TXS(cpu, operands):
    cpu.SP = cpu.X & 0xFF
    return 2

@register_opcode(0x98, 1)
def TYA(cpu, operands):
    cpu.A = cpu.Y & 0xFF
    _set_zn(cpu, cpu.A)
    return 2


def illegal(cpu, operands):
    opcode = cpu.mem.data[cpu.PC - 1]
    raise NotImplementedError(f'Illegal opcode (0x{opcode:04X}) executed at PC=0x{cpu.PC:04X}')

# Fill remaining None slots with illegal handler
for i in range(256):
    if opcode_table[i] is None:
        opcode_table[i] = (1, illegal)
