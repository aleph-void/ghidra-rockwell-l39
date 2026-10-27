#!/usr/bin/env bash
# Rockwell L39 / R65C19 module test suite.
#
#   GHIDRA_INSTALL_DIR=<Ghidra 12.1.x/12.2> PROJ_DIR=<dir, no path component starting with '.'> test/run-tests.sh [workdir] [--loader]
#
# Needs MAME's `unidasm` (black box, `-arch r65c19`) on PATH or in UNIDASM.
# 1. the spec compiles   2. decode: 16,384 four-byte slots against unidasm   3. every constructor reached
# 4. 20,000-instruction linear sweep against unidasm   5. hand-computed emulator cases + wrong expectations that must be reported
# --loader: firmware loader (needs the built extension installed in $GHIDRA_INSTALL_DIR/Ghidra/Extensions)
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
MOD=$(cd "$HERE/.." && pwd)
: "${GHIDRA_INSTALL_DIR:?set GHIDRA_INSTALL_DIR}"
LOADER=0
ARGS=()
for a in "$@"; do if [[ $a == --loader ]]; then LOADER=1; else ARGS+=("$a"); fi; done
W=$(readlink -m "${ARGS[0]:-${TMPDIR:-/tmp}/l39-tests}")
mkdir -p "$W"
export TMPDIR=$W PROJ_DIR=${PROJ_DIR:-$W} JOBS=${JOBS:-4}
UNIDASM=${UNIDASM:-$(command -v unidasm)}
shopt -s expand_aliases
L=RockwellL39:LE:16:default
fail=0
P="$GHIDRA_INSTALL_DIR/Ghidra/Processors/L39"
if [[ ! -e $P && ! -e $GHIDRA_INSTALL_DIR/Ghidra/Extensions/L39 ]]; then
	ln -s "$MOD" "$P"
	trap 'rm -f "$P"' EXIT      # a leftover link would collide with the installed extension
fi

echo "== 1. SLEIGH compiles"
"$GHIDRA_INSTALL_DIR/support/sleigh" "$MOD/data/languages/RockwellL39.slaspec" 2>&1 | grep -E "^ERROR" && exit 1 || true
sz=$(stat -c %s "$MOD/data/languages/RockwellL39.sla"); echo "   RockwellL39.sla: $sz bytes"; ((sz < 16 * 1024 * 1024))

echo "== 2. decode against unidasm (r65c19)"
python3 -I "$HERE/gen_corpus.py" "$W/all.bin"
"$HERE/decode-corpus.sh" $L "$W/all.bin" "$W/gh.txt" 4
PATH=$(dirname "$UNIDASM"):$PATH python3 -I "$HERE/unidasm_stream.py" "$W/all.bin" "$W/uni.txt" 12
python3 -I "$HERE/compare.py" "$W/gh.txt" "$W/uni.txt" "$W/all.bin" --detail | tee "$W/compare.txt" | head -60
# the only differences allowed: opcodes the data sheet leaves empty, which unidasm shows as NOP
python3 -I "$HERE/check_explained.py" "$W/gh.txt" "$W/uni.txt" "$W/all.bin" || fail=1

echo "== 3. every constructor is reached"
"$HERE/decode-corpus.sh" $L "$W/all.bin" "$W/reach.txt" 4 Reach.java
python3 -I "$HERE/reach_check.py" "$MOD/data/languages/RockwellL39.slaspec" "$W/reach.txt" || fail=1

echo "== 4. linear sweep of a 20,000-instruction stream"
python3 -I "$HERE/stream_test.py" gen "$W/gh.txt" "$W/uni.txt" "$W/all.bin" "$W/stream.bin" 20000
"$UNIDASM" "$W/stream.bin" -arch r65c19 -basepc 0x1000 > "$W/stream.uni"
BASE_ADDR=0x1000 "$HERE/ghidra-script.sh" raw $L "$W/stream.bin" DumpDisasm.java 4 "$W/stream.gh"
python3 -I "$HERE/stream_test.py" cmp "$W/stream.gh" "$W/stream.uni" || fail=1

echo "== 5. p-code: hand-computed emulator tests"
mkdir -p "$W/emu"
python3 -I "$HERE/emu_tests.py" "$W/emu"
"$HERE/ghidra-script.sh" raw $L "$W/emu/emu.bin" EmuCheck.java "$W/emu/tests.txt" "$W/emu/out.txt"
echo "   $(tail -1 "$W/emu/out.txt")"
grep -q " 0 failed" "$W/emu/out.txt" || { grep ^FAIL "$W/emu/out.txt" | head -20; fail=1; }
grep -q "[1-9][0-9]* broken expectations detected" "$W/emu/out.txt" || { echo "   the deliberately wrong expectations were not detected"; fail=1; }

if ((LOADER)); then
	echo "== 6. firmware loader (banked image, explicit loader choice)"
	python3 -I "$HERE/make_image.py" "$W/fw.bin"
	P2=$(mktemp -d "$PROJ_DIR/l39.XXXXXX")
	"$GHIDRA_INSTALL_DIR/support/analyzeHeadless" "$P2" p -import "$W/fw.bin" -loader RockwellL39Loader -processor $L -noanalysis \
		-scriptPath "$HERE" -postScript LoaderCheck.java "$W/loader.out" -deleteProject >"$W/loader.log" 2>&1 || { tail -20 "$W/loader.log"; fail=1; }
	rm -rf "$P2"
	cat "$W/loader.out"; grep -q '^PASS' "$W/loader.out" || fail=1
fi
if ((fail)); then echo "FAILED"; exit 1; fi
echo "all tests passed"
