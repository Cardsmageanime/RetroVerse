# Nexus Relay Learning Lesson 008 — Review actual Android board-survey evidence

## Why this is a better next step
The preceding milestones built conservative USB/SD safety checks. Their missing inputs cannot be resolved by further self-reported checklists. This lesson adds an **offline interpreter for real read-only Android/ADB survey output** from the existing `boot/tools/probe_android_board.py`.

The GameBox has not previously enumerated over ADB, so **no real board survey is available yet**. The new reviewer can run on a saved survey report when one becomes available. Neither tool can demonstrate that USB boot works.

## Code tour
1. `EXPECTED` is the list of fields produced by the existing Android probe: SoC platform, hardware, product board, bootloader version, device-tree model and compatibility, kernel release, MMC hosts.
2. `analyze()` checks the original survey's format, validates fields individually, and records unavailable fields rather than silently guessing.
3. When a supplied string contains G12A or S905X2, it reports a **clue**, not independently verified silicon or board revision.
4. The returned `boot_authorized`, `storage_write_authorized`, `dtb_matches_board`, and `nonpersistent_usb_boot_path_verified` always remain `false`.
5. The program reads only an existing text file and cannot run ADB, contact a device, flash storage or execute U-Boot.

## Try an offline example
Save this as `example-survey.json`:

```json
{"survey_type":"read-only-android-board-probe","results":{"soc_platform":{"ok":true,"value":"g12a"}}}
```

Then run:

```bash
python3 boot/tools/review_android_board_survey.py --survey example-survey.json
python3 -m unittest discover -s boot/tests -p 'test_review_android_board_survey.py' -v
```

The output identifies the G12A string as *unverified evidence* and records the missing fields. It cannot authorize a boot attempt. This illustrative JSON is not GameBox hardware evidence.

## Physical evidence gate
If and only if Android Debug Bridge is safely available on the GameBox, the existing optional probe can gather read-only properties. An unavailable ADB connection is a blocker, **not evidence of incompatible hardware**. Check command and output privacy before sharing reports.

The remaining blockers are board revision, bootloader external USB support, RAM/DDR handoff, board-matched DTB and nonpersistent boot sequence. Preserve the reference EmuELEC SD; never run its legacy `aml_autoscript` or write internal Android/eMMC. Phases 1–5 only.
