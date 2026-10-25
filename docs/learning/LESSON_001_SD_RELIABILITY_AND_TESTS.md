# RetroVerse coding lesson 001 — SD reliability and Python testing

**Milestone:** 15, Phase 1. **Language:** Python 3. **Status:** offline test; physical GameBox verification not performed.

## Why this code exists
The Windows reader successfully checked 256 MiB of the EmuELEC card. However, GameBox Android previously reported SD CMD18 CRC errors. A partial computer-side readback must **not** erase the hardware-side failure from the record.

This component reviews *already collected JSON evidence*, not a device. It never opens a block device or writes anything.

## Read the source in this order
1. [Implementation](../../boot/tools/check_sd_reliability.py) — the function `evaluate(evidence)` takes a Python dictionary containing facts such as `gamebox_sd_crc_errors_observed`.
2. `CHECKS` is a dictionary of positive facts that must be exactly `True`; absent, false, or unknown values keep the report blocked.
3. `PROBLEMS` identifies known bad conditions; an explicit `True` blocks verification even if all positive checks are present.
4. `blockers` is a Python list of human-readable reasons. A list with any items means research cannot progress to a physical boot.
5. `can_write: False` and `boot_verified: False` are hard-coded safety boundaries. Even a clean report does not authorize an installation.
6. `argparse` accepts the JSON file path; `json.loads` converts file text to a Python dictionary.

## Example input, based on current evidence
Create a local JSON file *with a text editor* containing:

```json
{
  "full_capacity_verified": false,
  "gamebox_sd_link_reliability_verified": false,
  "reader_readback_verified": false,
  "bootloader_card_detection_verified": false,
  "gamebox_sd_crc_errors_observed": true,
  "windows_hash_readback_passed": true
}
```

Then run from the repository root:

```bash
python3 boot/tools/check_sd_reliability.py --evidence hardware/evidence/vayava-franklin-external-boot.json
```

This existing repository evidence intentionally lacks several positive keys. The expected outcome is **verification-blocked**.

## Understanding the tests
See [test_check_sd_reliability.py](../../boot/tests/test_check_sd_reliability.py). `unittest.TestCase` groups independent tests. `assertEqual` checks exact results; `assertFalse` checks safety defaults. A test that passes establishes **software behavior**, not reliability of an SD card.

```bash
python3 -m unittest discover -s boot/tests -p 'test_check_sd_reliability.py' -v
```

## Programming exercises
- Add a test where the bootloader detection field is missing; check that it blocks verification.
- Identify why `evidence.get(key) is True` is stricter than a generic truthy check.
- Explain why an SD-card brand should never influence the reliability report.

## GitHub learning workflow
1. View a commit's **Files changed** tab to compare the added lines.
2. Read the implementation before the tests, and predict the outcome of each fixture.
3. Run the tests locally, then read error messages if they fail.
4. Keep comments, instructions, and release-status claims separate: a documented plan is not working hardware.

**Do not attempt to boot the Franklin research DTB or execute EmuELEC `aml_autoscript`. Phase 6 remains reserved and untouched.**
