# Nexus Relay Lesson 007 — Controlled USB trial preparation

This is a **paper-only preflight**. It does not load a kernel, manipulate any device, or authorize a boot.

## Controlled verification checklist
Before a future hardware test, independent evidence is required for:
1. Exact Vayava GameBox model and board revision.
2. Board-matched DTB, GPIO/power configuration and correct RAM/reserved-memory layout.
3. A verified **nonpersistent** USB bootloader entry path.
4. Test-image hashes and USB-media integrity.
5. An understood rollback/recovery procedure returning to untouched Android.
6. Removal and protection of the existing EmuELEC reference SD.
7. An operator physically present to observe the boot and disconnect power if necessary.

**Stop immediately** if any proposed method invokes legacy `aml_autoscript`, `defenv`, `saveenv`, internal eMMC write operations, or an unverified DTB. Do not reuse example-board load addresses or claim the SD CRC issue resolved without real hardware evidence.

## Source walkthrough
- `REQUIRED`: eight required booleans, which must literally equal JSON `true`.
- `FORBIDDEN`: five disqualifying conditions, which must explicitly equal JSON `false`. Missing answers are **not** treated as safe.
- `evaluate()`: merges both sets into readable findings. It **always** returns `boot_authorized: false`, `flash_authorized: false`, `storage_write_authorized: false`, and `physical_boot_verified: false`.
- `main()`: loads a saved ordinary JSON file and prints the report. No block device is opened and no commands are executed.

## Run local simulated tests
```bash
printf '{}' > simulated-usb-trial.json
python3 boot/tools/check_controlled_usb_trial.py --checklist simulated-usb-trial.json
python3 -m unittest discover -s boot/tests -p 'test_check_controlled_usb_trial.py' -v
```

Expected result: **blocked**. The checker is intentionally not a device approval mechanism. Self-reported boolean flags are not independent hardware evidence.

## Milestone status
Ten tests ran locally and passed. No USB image was written and no boot test was performed. A tested, board-specific boot route remains the main blocker. Phases 1–5 only; Phase 6 off-limits.
