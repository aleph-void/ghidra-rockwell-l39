#!/usr/bin/env python3
"""stream_test.py gen <slots-ghidra.txt> <slots-unidasm.txt> <corpus.bin> <out.bin> [n] | cmp <ghidra-dump.txt> <unidasm-dump.txt>

gen: a code stream of n random instructions, using only opcodes that both decoders know (random operand bytes).
cmp: compares the two linear disassemblies of that stream instruction by instruction (address, length, text)."""
import random
import re
import sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])


def norm(t):
    t = t.strip().lower()
    t = re.sub(r'(?:\$|0x)([0-9a-f]+)', lambda m: 'h%x' % int(m.group(1), 16), t)
    t = re.sub(r'\s+', '', t)
    t = re.sub(r'^(rmb|smb|bbr|bbs)h([0-7]),', r'\1\2', t)
    return t


if sys.argv[1] == 'gen':
    g = {int(l.split(' ', 2)[0]): l.split(' ', 2)[1:] for l in open(sys.argv[2]) if not l.startswith('    ')}
    u = {int(l.split(' ', 2)[0]): l.split(' ', 2)[1:] for l in open(sys.argv[3])}
    data = open(sys.argv[4], 'rb').read()
    ok = sorted({data[4 * i] for i in g if g[i][1] != 'BAD' and g[i][0] == u[i][0]})
    rnd = random.Random(3)
    n = int(sys.argv[6]) if len(sys.argv) > 6 else 20000
    out = bytearray()
    for _ in range(n):
        out.append(rnd.choice(ok))
        out += bytes(rnd.getrandbits(8) for _ in range(4))
        # operands are consumed by the decoders; the leftover random bytes become the next opcodes' operands only if
        # lengths differ, so every instruction is emitted whole: pad with the exact length from the slot table
        op = out[-5]
        ln = int(g[next(i for i in g if data[4 * i] == op)][0])
        del out[len(out) - 5 + ln:]
    open(sys.argv[5], 'wb').write(out)
    print(len(out), 'bytes', n, 'instructions')
else:
    gl = [l.rstrip('\n').split(' ', 2) for l in open(sys.argv[2])]
    ul = []
    for l in open(sys.argv[3]):
        m = re.match(r'([0-9a-f]+):\s+((?:[0-9a-f]{2} )+)\s*(.*)', l)
        if m:
            ul.append((int(m.group(1), 16), len(m.group(2).split()), m.group(3)))
    base = ul[0][0]
    bad = expl = 0
    n = min(len(gl), len(ul))
    for (go, gb, gt), (ua, ub, ut) in zip(gl, ul):
        if int(go, 16) + base != ua or len(gb) // 2 != ub or norm(gt) != norm(ut):
            if '--explained' in sys.argv and ((norm(gt).startswith(('rba', 'sba')) and norm(ut)[:3] == norm(gt)[:3]) or (gt == 'CLW' and ut == 'nop')):
                expl += 1
                continue
            bad += 1
            if bad <= 10:
                print('   DIFF', go, gb, gt, '|', hex(ua), ut)
    print(f'   {n - bad - expl}/{n} instructions identical (address, length, text) in a {n}-instruction linear sweep; {expl} explained differences (RBA/SBA operand order, CLW), {bad} unexplained')
    sys.exit(1 if bad or len(gl) != len(ul) else 0)
