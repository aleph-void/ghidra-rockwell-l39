#!/usr/bin/env python3
"""emu_tests.py <workdir>: write emu.bin (cases of emu_cases.py, 0x40 bytes apart from 0x1000) and tests.txt for EmuCheck.java."""
import os
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import emu_cases  # noqa: E402

STRIDE, BASE = 0x40, 0x1000
work = sys.argv[1]
os.makedirs(work, exist_ok=True)
img = bytearray(BASE + STRIDE * len(emu_cases.CASES) + 16)
tests = []
for n, (name, code, init, expect, stop) in enumerate(emu_cases.CASES):
    a = BASE + n * STRIDE
    raw = bytes.fromhex(re.sub(r'@(\w\w)', lambda m: '%02x%02x' % ((a + int(m.group(1), 16)) & 0xff, (a + int(m.group(1), 16)) >> 8),
                               code.replace(' ', '')))
    expect = re.sub(r'\$(\d+)', lambda m: '%04x' % (a + int(m.group(1))), expect)
    assert len(raw) < STRIDE - 8
    img[a:a + len(raw)] = raw
    start = a
    stopaddr = stop if stop >= 0x100 else a + stop
    if name == 'brk_pushes_pc_plus_2_and_flags':
        stopaddr = 0x2000
    tests.append(f'{name} {start:x} {stopaddr:x} {init} {expect}')
open(os.path.join(work, 'emu.bin'), 'wb').write(img)
open(os.path.join(work, 'tests.txt'), 'w').write('\n'.join(tests) + '\n')
print(len(tests), 'cases')
