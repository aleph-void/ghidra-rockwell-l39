#!/usr/bin/env python3
"""check_explained.py <ghidra.txt> <unidasm.txt> <corpus.bin>: every module/unidasm difference must be in an explained class:
 (a) module undefined, unidasm shows 'nop ...' or 'clw' for a reserved opcode (MAME's choice; see GHIDRA-RARE.md),
 (b) RBA / SBA: MAME puts the mask before the 16-bit address, the module (like BAR / BAS) the address first,
 (c) opcode 0x43: module CLW, MAME nop.
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
        if ut.startswith(('nop', 'clw')):
            continue
    elif gl == ul and gk == uk:
        continue
    elif gl == ul and gk[0] == uk[0] and gk[0] in ('rba', 'sba'):
        continue
    elif data[4 * i] == 0x43 and gt == 'CLW' and ut == 'nop':
        continue
    bad += 1
    if bad <= 10:
        print('   UNEXPLAINED', i, data[4 * i:4 * i + 4].hex(), gt, '|', ut)
print(f'   {bad} unexplained differences')
sys.exit(1 if bad else 0)
