# Nexus Relay Learning Lesson 015 — Validate and harden the DTB node parser

The previous milestone introduced a read-only DTB node parser but did not run its tests. This milestone focuses on checking and repairing the parser rather than adding another readiness checklist.

## What was improved
- Minimum accepted input length is now 56 bytes (40-byte header plus a minimal 16-byte reserve map); DTB format versions below 17 are rejected by this limited parser.
- Header region bounds now include a check that the reserve map does not overlap the structure or string sections.
- Padding after a node name must remain inside the structure section.
- The FDT_END token must terminate the declared structure section, preventing silent acceptance of trailing structure data.
- A root/node must exist. The old brittle end-marker test offset is corrected, and additional negative cases cover malformed sections and version boundaries.

## Learn from the code
`struct.unpack_from(">10I", data)` reads ten big-endian DTB header fields. The structure block holds tokens (begin node, end node, property, no-op, end). Parsing requires strict file-size and offset checks because an untrusted DTB can claim sizes outside the actual bytes supplied.

Use a **copied** DTB only:
```bash
python3 -m unittest discover -s boot/tests -p 'test_inspect_dtb_nodes.py' -v
python3 boot/tools/inspect_dtb_nodes.py --dtb-copy "$HOME/Downloads/RetroVerse-Boot-Reference/dtb.img"
```

## Validation boundary
A locally reconstructed standalone parser and synthetic fixture suite passed 11 tests during this milestone. The repository parser and regression test were updated with the corresponding fixes, but GitHub CI was **not** independently run in this turn. Run the committed tests before using its output for research.

This remains a **read-only structural inspector**: it does not verify GPIO, voltage rails, DRAM layout, USB boot behavior or board-specific DTB suitability. No boot is authorized. Do not execute legacy `aml_autoscript`, change Android/eMMC or overwrite the EmuELEC reference SD. Phases 1–5 only.
