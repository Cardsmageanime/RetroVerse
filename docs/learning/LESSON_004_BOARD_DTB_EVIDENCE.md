# Nexus Relay Learning Lesson 004 — Board/DTB evidence and safe USB preparation

## What we know
The EmuELEC reference identifies a G12A-family SD controller at `sd2@ffe05000`. Its `gpio_cd = <0x27 0x30 0x00>` refers to vendor GPIO index 48. Mainline example boards often use `GPIOC_6` (47) and the upstream G12A header lists `GPIOC_7` as 48. **These numbers do not establish vendor-to-mainline GPIO equivalence.** SD polarity, SD power rail and board revision remain unverified. The GameBox previously showed SD CMD18 CRC errors.

## Code lesson
- `REQUIRED` lists seven independently verified facts needed before considering board-specific configuration.
- `HAZARDS` lists five disqualifying dangers. Each must be explicitly recorded as JSON `false`; a missing value means unknown and **blocks** approval.
- `evaluate()` accepts only a JSON object. Required values must literally be `true`; negative hazards must literally be `false`. Strings such as `"true"` do not count.
- Even complete *reported* evidence never authorizes boot, flash or a device tree. Independent physical review is indispensable.

## Local example (pure simulation)
Save `{}` in a regular file `board-evidence.json` and run:

```bash
python3 boot/tools/check_board_dtb_evidence.py --evidence board-evidence.json
python3 -m unittest discover -s boot/tests -p 'test_check_board_dtb_evidence.py' -v
```

The report should be `verification-blocked`. Do not point it to a device or treat hand-entered booleans as real board evidence.

## Next evidence-gathering gate
Compare Vayava board model/revision, real peripheral GPIO bank offsets and SD card-detect signals, SD regulator wiring, RAM/DDR boot handoff, and *nonpersistent* U-Boot USB boot capability. **Do not run the EmuELEC `aml_autoscript`, write eMMC, swap in a reference-board DTB, or boot until independently validated.**

**Validation:** 10 unit tests of this checker ran locally and passed on October 27, 2026. No GameBox boot has been performed. Phases 1–5 only; Phase 6 is reserved.
