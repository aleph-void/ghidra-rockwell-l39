#!/usr/bin/env python3
"""compare.py <ghidra.txt> <unidasm.txt> <corpus.bin> [--show N]: module vs MAME unidasm (r65c19).
Buckets: exact (same length, mnemonic and operands after normalisation), operand-order, length, mnemonic, ..."""
import collections
import re
import sys


def norm(t):
    t = t.strip().lower()
    t = re.sub(r'(?:\$|0x)([0-9a-f]+)', lambda m: 'h%x' % int(m.group(1), 16), t)
    t = re.sub(r'\s+', ' ', t)
    return t


def split(t):
    t = norm(t)
    mn, _, ops = t.partition(' ')
    m = re.match(r'(rmb|smb|bbr|bbs)(\d)$', mn)
    ol = [o.strip() for o in ops.split(',')] if ops else []
    return mn, ol, m


def key(t):
    """canonical (mnemonic, operands) with the bit number folded into RMB/SMB/BBR/BBS mnemonics"""
    mn, ol, m = split(t)
    if mn in ('rmb', 'smb', 'bbr', 'bbs') and ol:
        b = int(ol[0][1:], 16)
        return (mn + str(b), tuple(ol[1:]))
    return (mn, tuple(ol))


def main():
    global g
    g = {}
    for l in open(sys.argv[1]):
        if l.startswith('    '):
            continue
        i, ln, t = (l.rstrip('\n').split(' ', 2) + [''])[:3]
        g[int(i)] = (int(ln), t)
    u = {}
    for l in open(sys.argv[2]):
        i, ln, t = (l.rstrip('\n').split(' ', 2) + [''])[:3]
        u[int(i)] = (int(ln), t)
    data = open(sys.argv[3], 'rb').read()
    show = int(sys.argv[sys.argv.index('--show') + 1]) if '--show' in sys.argv else 2
    b = collections.Counter()
    ex = collections.defaultdict(list)
    for i in sorted(g):
        gl, gt = g[i]
        ul, ut = u[i]
        gk, uk = key(gt), key(ut)
        if gl == 5 and ul == 5:      # the fifth byte belongs to the next slot of the corpus (unidasm saw it as 0): ignore the branch target
            gk, uk = (gk[0], gk[1][:-1]), (uk[0], uk[1][:-1])
        if gt == 'BAD' or gl == 0:
            c = 'module undefined, unidasm decodes' if ul and not ut.startswith(('db ', '.byte')) else 'both undefined'
        elif gl == ul and gk == uk:
            c = 'exact'
        elif gl == ul and gk[0] == uk[0] and sorted(gk[1]) == sorted(uk[1]):
            c = 'operand order'
        elif gl == ul and gk[0] == uk[0]:
            c = 'same mnemonic and length, operands differ'
        elif gl != ul:
            c = 'length differs'
        else:
            c = 'mnemonic differs'
        b[c] += 1
        if len(ex[c]) < 400:
            ex[c].append((i, data[4 * i:4 * i + 4].hex(), gt, gl, ut, ul))
    n = len(g)
    for c, k in b.most_common():
        print(f'   {k:6d} {c}')
    print(f'   {n} slots')
    if '--detail' in sys.argv:
        for c in b:
            if c in ('exact', 'both undefined'):
                continue
            seen = collections.Counter()
            print('==', c)
            for i, h, gt, gl, ut, ul in ex[c]:
                kk = (h[:2], gt.split(' ')[0], ut.split(' ')[0])
                seen[kk] += 1
                if seen[kk] <= 1:
                    print(f'   {h}  module: {gt} ({gl})   unidasm: {ut} ({ul})')


if __name__ == '__main__':
    main()
