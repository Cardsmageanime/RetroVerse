# Nexus Relay Coding Lesson 012 — Offline boot-reference inventory

This milestone identifies the exact bytes of *existing copied* GameBox reference files without executing the bootloader or accessing the original EmuELEC SD card.

## Why this matters
We have an Amlogic G12A/S905X2 candidate and several unverified USB boot blockers. A reference-file inventory makes it possible to compare specific `aml_autoscript`, `dtb.img`, `kernel.img` and `config.ini` copies using SHA-256 hashes. It does **not** determine whether a board DTB is compatible or the boot sequence is safe.

## How to run on your own Linux Mint computer
Only after confirming the *copied* files exist in `~/Downloads/RetroVerse-Boot-Reference`:

```bash
python3 boot/tools/reference_inventory.py --reference-dir "$HOME/Downloads/RetroVerse-Boot-Reference"
python3 -m unittest discover -s boot/tests -p "test_reference_inventory.py" -v
```

The tool never executes `aml_autoscript`, opens a hardware block device, or writes storage. It reads the four named regular files and refuses symlink inputs, empty files and files over 128 MiB. Do not point the tool at mounted SD content.

## Learn from the code
- `hashlib.sha256` produces a repeatable file fingerprint.
- `stat.S_ISREG` checks that a path refers to an ordinary file.
- `struct.unpack_from` reads the big-endian `0x27051956` magic and declared payload size in a legacy U-Boot header.
- `zlib.crc32` checks header and payload integrity on the `aml_autoscript` copy.
- Missing files are reported individually rather than hiding all findings.
- Even a valid hash or CRC does **not** prove authenticity, safety or boot compatibility.

## Status
Eleven synthetic fixture tests passed locally. The real GameBox reference files were not available in the current workspace and were not inspected. Real hardware boot is unverified; no USB boot authorization is given. Protect internal Android/eMMC and the original EmuELEC SD. Only Phases 1–5 are in scope.
