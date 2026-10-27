# Credits and provenance: L39 module

| | |
|---|---|
| Source | https://github.com/honx/rockwell_l39_ghidra, HEAD `d1e76d5` (this directory is `ghidra/RockwellL39` there; 11 commits, all 2026-05-05) |
| License | Apache-2.0 (`LICENSE`) |
| Original author | honx (GitHub @honx): SLEIGH module, loader, banking scripts, documentation |
| Based on | Rockwell R65C19 Microcomputer data sheet (Order No. 410, January 1992) and the C40/L39 technical reference manual, as cited in the slaspec |

Other implementations: `gh search repos` for "ghidra r65c19", "rockwell l39 ghidra", "r65c19 sleigh", "rockwell c40 modem ghidra" found none.

## Ghidra-Rare changes
1. New opcodes `JPI` ($0C), `ADD zp` ($64), `ADD zp,X` ($74); `CLW` moved from $43 to $52. All four are in the data sheet's opcode
   matrix (Table A-1, page A-2), and MAME's r65c19 disassembler agrees.
2. `RBA` / `SBA` operand bytes are now op, mask, address. The data sheet gives only "ABS, 4 bytes" (Seven Controller Instructions table,
   page A-4); MAME's r65c19 disassembler and the C39 support patch for ca65 posted to the cc65 mailing list (2015) both use this order.
3. `ADC` / `SBC` rewritten: V was set to C, carry-in was ignored when detecting carry, SBC's carry flag was wrong; decimal mode added.
4. `JSR`, `JSB0..7` push the address of their last byte and `RTS` adds one (6502 convention). `LAB` sets N/Z on both paths.
5. Loader ported to the Ghidra 12 loader API (it targeted a removed signature and had never been built); overlapping I/O / RAM blocks
   dropped (the pspec labels the registers); no longer the preferred loader for any file whose size is a multiple of 8 KiB.
6. Build files (`build.gradle`, `extension.properties`, extension name `L39`), `LICENSE` copy, `test/`, `GHIDRA-RARE.md`, this file.

## Sources and tools
- Rockwell R65C19 Microcomputer data sheet, January 1992, from the 6502.org document archive
  (http://www.6502.org/documents/datasheets/rockwell/rockwell_r65c19_microcomputer.pdf): Table A-1 (opcode matrix, page A-2) and
  the new-instruction tables (page A-4). Not redistributed.
- MAME's `unidasm -arch r65c19`, used as a black box (MAME source not read).
- The C39 ca65 patch (`cc65-git.diff`, cc65-devel mailing list, May 2015; cc65 is zlib-licensed): read for the RBA/SBA/BAR/BAS byte order only.
