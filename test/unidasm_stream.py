#!/usr/bin/env python3
"""unidasm_stream.py <corpus.bin> <out.txt> [jobs] [arch]: MAME's unidasm (a black box) on each 4-byte slot at address 4n.
Output "<slot> <length> <text>" (first instruction of the slot)."""
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

data = open(sys.argv[1], 'rb').read()
jobs = int(sys.argv[3]) if len(sys.argv) > 3 else 8
arch = sys.argv[4] if len(sys.argv) > 4 else 'r65c19'
tmp = tempfile.mkdtemp(prefix='unidasm.', dir=os.environ.get('TMPDIR'))


def one(n):
    p = os.path.join(tmp, f'{n}.bin')
    open(p, 'wb').write(data[4 * n:4 * n + 4])
    r = subprocess.run(['unidasm', p, '-arch', arch, '-basepc', hex(4 * n)], capture_output=True, text=True)
    os.unlink(p)
    line = r.stdout.splitlines()[0] if r.stdout.strip() else ''
    try:
        addr, rest = line.split(':', 1)
        toks = rest.split()
        nb = 0
        while nb < len(toks) and len(toks[nb]) == 2 and all(c in '0123456789abcdef' for c in toks[nb]):
            nb += 1
        # the instruction text starts after the raw bytes (mnemonic is never two hex digits)
        text = rest.strip()
        text = ' '.join(text.split()[nb:])
        return n, nb, text
    except ValueError:
        return n, 0, 'ERR ' + (r.stdout + r.stderr)[:60]


with ThreadPoolExecutor(jobs) as ex, open(sys.argv[2], 'w') as f:
    for n, ln, text in ex.map(one, range(len(data) // 4)):
        f.write(f'{n} {ln} {text}\n')
os.rmdir(tmp)
