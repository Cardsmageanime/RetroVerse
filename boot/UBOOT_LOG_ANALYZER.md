# Passive U-Boot log analyzer

`boot/tools/analyze_uboot_log.py` summarizes a saved, text-format U-Boot log. It
does not connect to UART, run U-Boot commands, inspect disks, or change device
state. It extracts only normalized version/model fields, MMC index tokens, and
boolean text markers; it never copies log lines into its JSON report.

Run from the repository root:

```sh
python3 boot/tools/analyze_uboot_log.py --log /path/to/redacted-uboot.log
```

To save a report, give a path that does not exist yet:

```sh
python3 boot/tools/analyze_uboot_log.py \
  --log /path/to/redacted-uboot.log \
  --output ./uboot-observations.json
```

The input is limited to 4 MiB. Reports include the input SHA-256 and line
count, observed text markers, and a manual-review flag for environment-write
or flash/erase text. Treat logs and reports as potentially sensitive anyway.

**A marker is not proof of execution or hardware behavior.** MMC numbers are
only tokens printed in the log; they are not mapped to physical devices. The
report always leaves `external_uboot_boot_path_verified`,
`external_sd_boot_verified`, and `can_flash` false. Review the original log
locally and redact secrets before sharing it. Do not use this tool as approval
to execute a boot script or write to internal storage.

Tests:

```sh
python3 -m unittest discover -s boot/tools -p 'test_analyze_uboot_log.py' -v
```
