# Credits and provenance: L39 module

| | |
|---|---|
| Source | https://github.com/honx/rockwell_l39_ghidra, HEAD `d1e76d5` (module directory `ghidra/RockwellL39`, 11 commits, all 2026-05-05) |
| License | Apache-2.0 (`LICENSE`) |
| Original author | honx (GitHub @honx): SLEIGH module, loader, banking scripts, documentation, talk |
| Based on | the Rockwell R65C19 data sheet (order no. 410, 1992) and C40/L39 technical reference manual as cited in the slaspec; contributor diagram `binary/banking-configurations.png` |

Other implementations: `gh search repos` for "ghidra r65c19", "rockwell l39 ghidra", "r65c19 sleigh", "rockwell c40 modem ghidra" found none.

## Ghidra-Rare changes
1. New opcodes `JPI` ($0C), `ADD zp` ($64), `ADD zp,X` ($74) (upstream "ISA gaps"): opcodes read from MAME's `unidasm -arch r65c19` run as a black box (MAME source not read); semantics from the data-sheet descriptions quoted in `docs/open-points.md`.
2. `ADC` / `SBC` rewritten: V was set to C, carry-in was ignored when detecting carry, SBC's carry/no-borrow flag was wrong; decimal mode (BCD, 65C02 behaviour) added (upstream "BCD math is binary-only").
3. `JSR`, `JSB0..7` push the address of their last byte and `RTS` adds one, as the 6502 does (the module pushed the next-instruction address and returned to it unchanged).
4. `LAB` sets N/Z on both paths.
5. Loader ported to the Ghidra 12 loader API (it targeted a removed signature and was never built); the I/O / RAM blocks that overlapped the ROM block (impossible in a Ghidra memory map) were dropped (the pspec labels them); it is no longer the preferred loader for any file whose size is a multiple of 8 KiB.
6. Build files (`build.gradle`, `extension.properties`, extension name `L39`), `LICENSE` copy in the module, `test/`, `GHIDRA-RARE.md`, this file, README and `docs/open-points.md` updates.

Tools used as black boxes: MAME `unidasm` (r65c19) for the opcode comparison. No firmware or datasheet was available.
