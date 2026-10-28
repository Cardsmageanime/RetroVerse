# Nexus Relay Learning Lesson 010 — Inspect legacy U-Boot files without executing them

## What this milestone does

The GameBox's EmuELEC reference SD contains a legacy `aml_autoscript`. Our earlier text evidence suggests it invokes `defenv` and `saveenv`, which could change the device's persistent boot settings. **Do not execute it.** Instead, `inspect_uboot_binary.py` reads an **existing copy** as bytes, calculates its SHA-256 digest, checks the classic U-Boot `uImage` magic and header length, and looks for suspicious printable command fragments.

This is not a disassembler. **A report without matches does not make any script safe.** Hidden, compressed, encoded, segmented, or nested operations may not be visible.

## Try it safely
Only use an ordinary saved file, never a device path:

```bash
python3 boot/tools/inspect_uboot_binary.py --reference-file "$HOME/Downloads/RetroVerse-Boot-Reference/aml_autoscript"
python3 -m unittest discover -s boot/tests -p 'test_inspect_uboot_binary.py' -v
```

The tool rejects symlink paths, empty files and files over 16 MiB; it **does not flash, execute, mount, reboot, or write storage**. It reads existing file contents only and prints a report. No claims are made that the user's reference copy is available in this GitHub environment; it must be inspected locally before drawing conclusions.

## Code concepts
- `struct.unpack_from(">I", data)` interprets the big-endian 4-byte legacy image magic.
- A U-Boot legacy image header uses 64 bytes. The declared payload size is checked against the input length, not treated as trusted boot compatibility.
- `hashlib.sha256` fingerprints the exact bytes for later comparison without changing them.
- `re.findall` extracts printable byte runs; three regular-expression categories search for persistent environment changes, storage writes and indirect execution.
- The tool **always returns false** for safe execution, authorized boot and authorized writes.

## Verification and remaining blockers

11 isolated Python unit tests passed locally for binary header handling and hazards. This is **software-only testing**. Actual Vayava board revision, exact memory map, matching DTB, USB controller support and nonpersistent U-Boot route are still unverified. Do not run the reference script or alter Android/eMMC. Keep the EmuELEC SD preserved. Phases 1–5 only; Phase 6 remains reserved.
