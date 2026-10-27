# Nexus Relay Learning Lesson 003 — U-Boot text safety audit

**Milestone:** Phase 1, USB/SD bootloader investigation. This checks saved **plain-text** command listings, not devices or executable scripts.

## Why we need it
Our EmuELEC reference includes an `aml_autoscript` with `defenv`, `saveenv`, and `bootcmd` changes. Running it could modify persistent boot settings, contrary to the rule that Nexus Relay must leave internal Android/eMMC alone. **Never execute that script.**

## How the program works
1. `DANGEROUS` maps recognizable command patterns to warnings about persistent environment changes, flash/MMC writes, and boot control.
2. `UNKNOWN_EXECUTION` marks indirect calls (`run`, `source`), loaders and boot commands for human review.
3. `inspect()` reads only a Python string, attaches line numbers to findings, and always returns `safe_to_execute: false` and `boot_authorized: false`.
4. `main()` reads an ordinary UTF-8 file and prints JSON. It never writes a block device or invokes a shell.

## Try a harmless simulated input
```bash
printf 'defenv\nsaveenv\nrun bootcmd\n' > simulated-uboot.txt
python3 boot/tools/inspect_uboot_script.py --script-text simulated-uboot.txt
python3 -m unittest discover -s boot/tests -p 'test_inspect_uboot_script.py' -v
```

The example should report persistent-environment findings and require manual review. No script should be executed based on a clean result: variables, encoded operations, aliases, binaries and nested scripts may escape this heuristic. This tool deliberately does not claim to understand every U-Boot command or to authorize boot.

**Local development validation:** the corresponding 10 unit tests passed during this milestone. Hardware USB/SD boot remains unverified; board DTB, DDR, U-Boot capabilities and nonpersistent boot route still need direct verification. Phase 6 remains off-limits.
