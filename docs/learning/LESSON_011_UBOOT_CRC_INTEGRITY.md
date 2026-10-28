# Nexus Relay Lesson 011 — U-Boot Legacy Image CRC Integrity

**Phase 1; offline-only milestone.** The prior binary inspector searched printable strings for dangerous commands. This milestone adds actual **CRC32 integrity checking** for the 64-byte *legacy U-Boot uImage header* and declared payload. It does **not** parse U-Boot script semantics or prove bootloader safety.

## How the code works
- A classic legacy uImage header begins with big-endian magic `0x27051956`.
- Header CRC32 is stored at byte offsets 4–7. To validate, zero those four bytes in a copy of the first 64 bytes, then use `zlib.crc32` on that header copy.
- Payload size is read at byte offsets 12–15 and payload CRC32 at 24–27.
- The checker verifies payload fits the file, computes CRC32 only for the declared payload, and reports trailing bytes separately.
- CRC32 is an **error-detection checksum, not a signature**. A valid CRC is not evidence of authenticity, board compatibility, a nonpersistent USB boot route, or permission to execute.
- `safe_to_execute`, `boot_authorized`, and `write_authorized` remain false in every result.

## Usage on an existing *copy* of the EmuELEC reference
```bash
python3 boot/tools/verify_uboot_legacy_crc.py --reference-file "$HOME/Downloads/RetroVerse-Boot-Reference/aml_autoscript"
python3 -m unittest discover -s boot/tests -p 'test_verify_uboot_legacy_crc.py' -v
```
The tool reads only existing regular files (not symlinks). Never execute the reference `aml_autoscript`, flash internal Android/eMMC, or write the existing SD reference card.

## Testing and limitations
**11 tests passed locally** using synthetic image bytes, including bad header CRC, bad payload CRC, truncated header, oversized input, trailing bytes and checks against falsely authorizing boot.

This check cannot verify FIT images, encrypted/proprietary containers, image signatures, load addresses or hardware handoff. Real Vayava USB boot remains unverified. The next blocker is still independently validating bootloader behavior, RAM map and a board-matched DTB. Phase 6 remains out of scope.
