# L39 in Ghidra-Rare: verification notes

Module `ghidra/RockwellL39` of https://github.com/honx/rockwell_l39_ghidra (Apache-2.0); language `RockwellL39:LE:16:default` (unchanged). See [CREDITS.md](CREDITS.md). Builds for Ghidra 12.1.3, 12.1.4, 12.2 (`tools/build-module.sh --standard --name L39`).
CPU: Rockwell R65C19 enhanced 6502 (65C02-like plus W/I registers, multiply, threaded-code and bit-memory instructions; `(zp,X)` and `(zp),Y` redefined as `(zp)` and `(zp),X`).

## How to test
`GHIDRA_INSTALL_DIR=<Ghidra> PROJ_DIR=<dir without dot components> ghidra/RockwellL39/test/run-tests.sh <workdir> [--loader]`. Needs MAME's `unidasm` (used as a black box). `--loader` needs the built extension installed.
The upstream `tests/` need the ELSA modem firmware, which is not in the repository (vendor firmware, gitignored) and was not available.

## Results
| Area | Result |
|---|---|
| Decode | 16,384 four-byte slots (every opcode x 8 second bytes x 2 third bytes, plus random) against `unidasm -arch r65c19`: 14,444 exact, 1,767 where the module has no instruction and MAME shows a NOP/CLW for a reserved opcode (27 opcodes), 115 RBA/SBA operand-order differences, 16 CLW-vs-NOP at $43; **0 unexplained**. 20,000-instruction linear sweep (random operands, opcodes both decoders know): 19,738 identical, 262 the explained RBA/SBA/CLW differences, 0 unexplained |
| Reached | 132/132 constructors reached |
| Semantics | 88 hand-computed emulator cases (all ALU addressing modes incl. the R65C19 indirect modes, ADC/SBC flags in binary and decimal mode, compares, shifts, stack, all branch kinds, JSR/RTS, BRK, JMP forms, ADD/ASR/NEG, STI, RBA/SBA, SMB/RMB/BBS/BBR, BAR/BAS, EXC, PSH/PUL, TAW/TWA, PHW/PLW, JSB, JPI, NXT/LAN/LAI), 2 deliberately wrong expectations detected. Found and fixed: ADC V flag, ADC carry-in, SBC carry, missing BCD, JSR/RTS return address convention |
| Real code | No firmware available (the repository's ELSA modem image is not published). Synthetic 128 KiB banked image: loader maps ROM, creates the bank overlay and the `_reset` entry (tested). Upstream's banking scripts could not be exercised |
| Doesn't work | `MPY`, `MPA`, `RND` and the W multiplier are pcodeops (register effects not documented in the available text); `STOP`/idle and the CRC peripheral are not modelled; `CLW` opcode and `RBA`/`SBA` operand order are unresolved (below); the banking scripts' limitations in docs/open-points.md remain |
| Unverified | Everything not shared with MAME: encodings of `RBA`/`SBA`/`BAR`/`BAS`/`STI`, W/I-register semantics, decimal-mode V flag, the vector slots used by `JSB`, bank-switch behaviour, cycle counts, and all behaviour on real silicon |

## Differences from MAME's r65c19 disassembler (left as is, unresolved)
- `RBA` / `SBA` ($C2 / $D2): MAME decodes `op, mask, addr16`; the module `op, addr16, mask` (like `BAR` / `BAS`, which MAME also decodes as `addr16, mask`). The upstream analysis of real firmware found these accesses hitting control registers with the module's order, and the sibling instructions agree with it; the data sheet could not be checked. Possible MAME inconsistency.
- `CLW`: module $43 (the upstream author saw it in real firmware), MAME $52 (module: undefined) and a NOP at $43.
- 27 reserved opcodes: MAME shows NOPs of various lengths, the module shows no instruction (real firmware had none).

## Confirmed reference-tool bugs
None confirmed (no data sheet to settle the differences above).
