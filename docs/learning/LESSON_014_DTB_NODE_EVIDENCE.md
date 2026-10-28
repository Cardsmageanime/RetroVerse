# Nexus Relay Learning Lesson 014 — Inspect real DTB hardware labels

**Phase 1, research-only.** This tool parses *copied* Flattened Device Tree (DTB) structure sections for the root `model`, `compatible`, and nearby SD/MMC, USB and RAM node labels. These are **clues**, never proof of actual electrical wiring or USB bootability.

## Code concepts
- `struct.unpack_from(">10I", ...)` reads the DTB's big-endian header.
- A DTB uses numbered tokens: 1 begins a node, 2 ends it, 3 declares a property, 4 is padding/no-op and 9 closes the structure.
- The parser checks section ranges, string terminators, property bounds and nesting depth. It shows only selected identifying properties rather than exposing all device-tree content.
- `boot_authorized`, `write_authorized`, `board_match_verified` and `usb_boot_verified` always remain **false**.

## Offline use
Run on a **copied** `dtb.img` file, never on the live reference SD:
```bash
python3 boot/tools/inspect_dtb_nodes.py --dtb-copy "$HOME/Downloads/RetroVerse-Boot-Reference/dtb.img"
python3 -m unittest discover -s boot/tests -p 'test_inspect_dtb_nodes.py' -v
```

Review `observed_nodes` for Vayava board-identity clues and controller names. The GameBox reference file wasn't available during this commit, so its specific nodes were **not inspected**.

**Still blocked:** board-specific electrical GPIO and regulator mapping, genuine revision, DRAM reservations, safe nonpersistent USB handoff and physical tests. No Android/eMMC or removable-media writes. Phases 1–5 only.
