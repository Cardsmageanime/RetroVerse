# Nexus Relay Coding Lesson 013 — Inspect copied DTB binary headers

**Phase 1; USB/SD boot investigation, read-only.**

A DTB (Flattened Device Tree Blob) describes a board's hardware. The GameBox's actual compatible DTB remains **unverified**, despite G12A/S905X2 references. This milestone adds a file-only checker of the DTB's *binary envelope*, not a compatibility determination.

## What the source teaches

- `struct.unpack_from('>10I', data)` reads the 40-byte standard DTB header as ten **big-endian** 32-bit integers.
- The standard magic is `0xD00DFEED`; the header declares the total size and the structure/strings/reserve-map offsets.
- The tool checks length, range bounds, version consistency and overlapping structure/string regions; SHA-256 fingerprints the exact copied bytes.
- `board_matched`, `boot_authorized` and `write_authorized` **always remain false**. Passing a structural check cannot prove correct GPIO polarity, SD power rails, bootloader support, reserved memory or actual GameBox compatibility.

## Optional local read-only review

Run only on an ordinary, offline *copy* of the reference DTB:

```bash
python3 boot/tools/inspect_dtb_header.py --dtb-copy "$HOME/Downloads/RetroVerse-Boot-Reference/dtb.img"
python3 -m unittest discover -s boot/tests -p 'test_inspect_dtb_header.py' -v
```

No DTB file from the actual user's computer was supplied to this milestone, so its contents were **not** inspected here. The tool doesn't execute commands, format storage or contact the device.

## Validation

**11 synthetic unit tests passed locally** for valid header structure, corrupted magic, malformed sizes, overlap, version errors and boot-authorization safeguards. This is not a physical USB boot test.

**Hardware blockers remain:** verified board revision, suitable DTB, DDR map, nonpersistent USB boot route. Never execute legacy EmuELEC `aml_autoscript`, alter Android/eMMC, or overwrite the EmuELEC reference SD. Continue only Phases 1–5.
