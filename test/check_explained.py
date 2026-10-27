#!/usr/bin/env python3
"""check_explained.py <ghidra.txt> <unidasm.txt> <corpus.bin>: every module/unidasm difference must be in an explained class:
 the module has no instruction where unidasm shows 'nop ...': opcodes the R65C19 data sheet's opcode matrix
 (Table A-1) leaves empty.
Anything else is a failure."""
import re
import sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from compare import key  # noqa: E402  (compare.py runs on import only when given arguments)

g = {}
for l in open(sys.argv[1]):
    if not l.startswith('    '):
        i, ln, t = (l.rstrip('\n').split(' ', 2) + [''])[:3]
        g[int(i)] = (int(ln), t)
u = {}
for l in open(sys.argv[2]):
    i, ln, t = (l.rstrip('\n').split(' ', 2) + [''])[:3]
    u[int(i)] = (int(ln), t)
data = open(sys.argv[3], 'rb').read()
bad = n = 0
for i in sorted(g):
    gl, gt = g[i]
    ul, ut = u[i]
    gk, uk = key(gt), key(ut)
    if gl == 5 and ul == 5:
        gk, uk = (gk[0], gk[1][:-1]), (uk[0], uk[1][:-1])
    if gt == 'BAD':
        if ut.startswith('nop'):
            continue
    elif gl == ul and gk == uk:
        continue
    bad += 1
    if bad <= 10:
        print('   UNEXPLAINED', i, data[4 * i:4 * i + 4].hex(), gt, '|', ut)
print(f'   {bad} unexplained differences')
sys.exit(1 if bad else 0)
