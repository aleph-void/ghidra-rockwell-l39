# L39 in Ghidra-Rare: verification notes

Source: `ghidra/RockwellL39` of https://github.com/honx/rockwell_l39_ghidra (Apache-2.0); see [CREDITS.md](CREDITS.md).
Language `RockwellL39:LE:16:default` (unchanged). Builds for Ghidra 12.1.3, 12.1.4, 12.2 (`tools/build-module.sh --standard --name L39`).
CPU: Rockwell R65C19 enhanced 6502 (65C02-like plus W and I registers, multiply, threaded-code and bit-in-memory instructions;
`(zp,X)` and `(zp),Y` are redefined as `(zp)` and `(zp),X`). Used in the C40 / L39 / L3902 modem MCUs.

## How to test
```
GHIDRA_INSTALL_DIR=<Ghidra> PROJ_DIR=<dir whose path has no component starting with '.'> test/run-tests.sh <workdir> [--loader]
```
Needs MAME's `unidasm` (black box; `UNIDASM=<path>` if it is not on PATH). `--loader` needs the built extension installed in the Ghidra install.
No firmware is needed or fetched; the upstream repository's own end-to-end tests need the ELSA modem firmware, which is not published.

## Results
| Area | Result |
|---|---|
| Decode | 16,384 four-byte slots (every opcode x 8 second bytes x 2 third bytes, plus random) against `unidasm -arch r65c19`: 14,637 identical, 1,747 where the module has no instruction and unidasm shows a NOP: exactly the 27 opcodes the data sheet's opcode matrix leaves empty. **0 unexplained.** 20,000-instruction linear sweep (random operands): **20,000 / 20,000 identical** (address, length, text) |
| Opcode map | The R65C19-specific cells of the data sheet's Table A-1 (page A-2) were checked by eye against the module (all match), and its 27 empty cells are exactly the opcodes the module leaves undefined; the 65C02 cells are covered by the unidasm comparison |
| Reached | 132/132 constructors reached |
| Semantics | 89 hand-computed emulator cases: every ALU addressing mode including the R65C19 indirect modes, ADC/SBC flags in binary and decimal mode, compares, shifts, stack, every branch kind, JSR/RTS, BRK, JMP forms, ADD/ASR/NEG/CLW, STI, RBA/SBA, SMB/RMB/BBS/BBR, BAR/BAS, EXC, PSH/PUL, TAW/TWA, PHW/PLW, JSB, JPI, NXT/LAN/LAI. 2 deliberately wrong expectations are detected |
| Real code | No firmware is available (the ELSA image the upstream analysis used is not published). Loader tested on a synthetic 128 KiB banked image: ROM block, bank overlay, `_reset` entry |
| Doesn't work | `MPY`, `MPA`, `RND` (the W multiplier) are pcodeops: the data sheet's one-line descriptions do not define the register results precisely enough; `STOP`/idle modes and the CRC peripheral are not modelled; the banking scripts (`ghidra_scripts/`) are untested here and keep the limitations their author lists |
| Unverified | Behaviour on silicon; decimal-mode V flag (65C02 rule assumed); the `JSB` vector slots ($FFE0..$FFEE); W and I register details beyond the data sheet tables; cycle counts. **RBA / SBA byte order** (see below) |

## Settled against the data sheet
- `CLW` is $52 (Table A-1, page A-2); $43 is an empty cell. Upstream had `CLW` at $43; MAME agrees with the data sheet.
- `JPI` $0C, `ADD zp` $64, `ADD zp,X` $74 are in Table A-1; upstream lacked them.

## RBA / SBA operand order
The data sheet lists `RBA` / `SBA` as 4-byte ABS instructions ("Seven Controller Instructions", page A-4) without a byte layout. The module
follows MAME's r65c19 disassembler and the 2015 ca65 C39 patch, which both encode op, mask, address (while BAR/BAS are op, address, mask,
offset). **Unverified alternative:** the upstream author decoded them as op, address, mask (like BAR/BAS) and reports that, read that way,
the ELSA firmware's RBA/SBA operations hit control registers. That firmware is not available to check either reading.

## Confirmed reference-tool bugs
None. MAME shows the 27 opcodes left empty in the data sheet as NOPs of various lengths; the module leaves them undefined.
