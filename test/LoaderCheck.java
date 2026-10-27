// Checks the firmware loader on test/make_image.py's 128 KiB image: ROM block = first 64 KiB, one overlay for the
// second 64 KiB, reset vector entry function.  Script args: <outfile>
//@category Testing

import java.io.PrintStream;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.mem.MemoryBlock;

public class LoaderCheck extends GhidraScript {
	@Override
	protected void run() throws Exception {
		PrintStream out = new PrintStream(getScriptArgs()[0]);
		StringBuilder sb = new StringBuilder();
		MemoryBlock rom = currentProgram.getMemory().getBlock("ROM");
		MemoryBlock ov = currentProgram.getMemory().getBlock("BANK_HIGH_1");
		boolean ok = rom != null && rom.getSize() == 0x10000 && ov != null && ov.isOverlay() && ov.getSize() == 0x10000;
		var f = getFunctionAt(toAddr(0xE000));
		ok = ok && f != null && f.getName().equals("_reset");
		byte b = ov == null ? 0 : ov.getByte(ov.getStart());
		ok = ok && (b & 0xff) == 0x81;       // bank 8 of the pattern: 8 * 16 + 1
		out.printf("loader: ROM %s, overlay %s, reset function %s, first overlay byte %02x%n", rom, ov, f, b & 0xff);
		out.println(ok ? "PASS" : "FAIL");
		out.close();
	}
}
