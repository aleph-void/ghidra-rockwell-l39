#!/usr/bin/env python3
"""make_image.py <out.bin>: synthetic 128 KiB banked image for the loader test: bank pattern bytes, reset vector -> 0xE000."""
import sys
img = bytearray(0x20000)
for i in range(len(img)):
    img[i] = (i // 0x2000 * 16 + 1) & 0xff
img[0xE000] = 0xEA            # NOP
img[0xFFFE], img[0xFFFF] = 0x00, 0xE0
open(sys.argv[1], 'wb').write(img)
