# Rockwell C40 / L39 / L3902 (R65C19) processor module

Ghidra processor module (extension name `L39`, language `RockwellL39:LE:16:default`) for the Rockwell R65C19 enhanced-6502 core of
the C40 / L39 / L3902 modem MCUs, with a firmware loader for banked images and banking-analysis scripts (`ghidra_scripts/`).
Original work by honx (https://github.com/honx/rockwell_l39_ghidra). Verification notes: [GHIDRA-RARE.md](GHIDRA-RARE.md);
provenance and changes: [CREDITS.md](CREDITS.md); tests: `test/run-tests.sh`.

Install the zip for your Ghidra version (12.1.3, 12.1.4, 12.2) from the Releases page with *File > Install Extensions*. Import a
firmware image with the format "Rockwell C40/L39/L3902 firmware" (or `-loader RockwellL39Loader` headless).
