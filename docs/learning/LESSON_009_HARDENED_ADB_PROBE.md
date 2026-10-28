# Nexus Relay Learning Lesson 009 — Hardened read-only ADB hardware probe

**Scope:** Phase 1, hardware evidence collection. The code does not boot, flash, root, reboot, or write to Android.

## What changed
The existing `boot/tools/probe_android_board.py` was updated rather than replaced with another checklist. Its eight fixed, read-only Android commands gather board and SoC strings, bootloader version, device-tree identifiers, kernel release and MMC host names.

- `authorized_device_count()` parses `adb devices` but only counts exact authorized `device` rows; it does not put serial numbers in the survey or error messages.
- `survey()` runs only hard-coded commands, each with a 15-second timeout. Failed or timed-out fields become `{"ok": false, "value": ""}`, while other fields remain available.
- Values are limited to 1,024 characters. Reports can still contain board-specific strings: **review reports before sharing**.
- `make_report()` uses the Nexus Relay project name and explicitly sets `board_boot_verified` and `boot_authorized` to false.
- `main()` requires exactly one authorized ADB device; output files use exclusive creation, so existing files are never overwritten.

## Offline tests
```bash
python3 -m unittest discover -s boot/tests -p 'test_probe_android_board.py' -v
```
Ten isolated unit tests passed locally using mocked subprocess calls; no real ADB connection was made.

## Optional hardware usage, only when authorized ADB is available
```bash
python3 boot/tools/probe_android_board.py --output nexus-relay-gamebox-survey.json
python3 boot/tools/review_android_board_survey.py --survey nexus-relay-gamebox-survey.json
```
If the GameBox does not enumerate over ADB, the safe outcome is a clear error without a boot attempt. ADB output alone cannot prove exact board revision, RAM reservations, nonpersistent USB boot or electrical DTB compatibility.

**Remaining gate:** independently verify the GameBox hardware and bootloader, then plan a controlled removable-media test without using the legacy EmuELEC `aml_autoscript` or changing internal Android/eMMC. The reference SD remains untouched. Phases 1–5 only.
