#!/usr/bin/env python3
"""gen_corpus.py <out.bin>: 4-byte slots (one decode window, <= 16384 slots so that slot n is at address 4n):
every opcode with 8 second bytes and 2 third bytes, then random slots."""
import random
import sys
rnd = random.Random(7)
second = (0x00, 0x01, 0x5a, 0x7f, 0x80, 0xa5, 0xfe, 0xff)
slots = []
for op in range(256):
    for b1 in second:
        for b2 in (0x00, 0x3c):
            slots.append(bytes((op, b1, b2, 0x00)))
while len(slots) < 16384:
    slots.append(bytes(rnd.getrandbits(8) for _ in range(4)))
open(sys.argv[1], 'wb').write(b''.join(slots))
