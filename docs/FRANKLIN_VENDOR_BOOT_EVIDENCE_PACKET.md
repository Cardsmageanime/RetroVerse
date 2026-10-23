# Franklin vendor U-Boot external-SD evidence packet

**Milestone:** B — establish an evidence-based external boot path before building an SD image.
**Status (2026-10-23): BLOCKED / evidence incomplete.**
**Scope:** Vayava GameBox, Android board `franklin`, firmware DT selector `g12a_u212_2g`, observed U-Boot `2015.01-g51e6fd64e9-dirty`.

This is a *review template*, not an instruction to enter a bootloader console, execute `aml_autoscript`, enable firmware updates, or flash anything. The current repository contains no proof that this exact U-Boot loads Linux from SD.

## Evidence ledger
| Fact or gate | Current observation | Confidence and next evidence |
| --- | --- | --- |
| Android board name | `franklin` | Observed in prior device evidence |
| Android DT selector | `g12a_u212_2g` | Observed in prior device evidence, not a mainline DTB compatibility proof |
| Vendor U-Boot | `2015.01-g51e6fd64e9-dirty` | Version observed; build config/environment unknown |
| SD controller | `ffe05000.sd2` mapped by Android to `mmcblk1` | Android observation only; U-Boot MMC numbering unknown |
| SD read quality | CMD18 CRC errors observed in Android | GameBox-side SD link reliability unverified |
| Windows card test | 256 MiB write/read SHA-256 matched | Does not verify capacity-wide integrity or GameBox link |
| DTB/kernel match | Unverified | Need board-matched DTB and kernel evidence |
| Boot script format and commands | Unverified | Need exact firmware's U-Boot build config or passive boot log |
| Recovery/boot selection | Unverified | Never infer recovery behavior from another G12A board |
| Boot image | Not approved | Keep artifacts labeled diagnostic/non-deployable |

## Safe evidence acquisition sequence
1. **First choice: offline, exact-match firmware examination.** Obtain publicly documented or owner-provided *exact firmware matching this board revision/build*, record provenance, hashes and version strings. Extract only configuration/logs with ordinary host-side read-only tools. Do not install firmware or run vendor update files.
2. **Alternative: passive serial observation**, only if the exact board has a documented non-invasive connector and safe electrical parameters. Capture existing startup text without transmitting commands, shorting test pads, soldering or changing firmware. If the board lacks documented safe access, **stop** rather than attempting speculative pinout work.
3. Redact serial numbers, MAC addresses, device IDs, account tokens and any unique identifiers. Preserve the remaining timestamps/command names/diagnostics.
4. Record whether the *installed* firmware actually checks removable SD, the boot priority, MMC index mapping, recognized files, script interpreter support, and proven fallback to normal Android.
5. Have a second reviewer compare every conclusion against exact evidence; leave unknown fields explicitly **UNKNOWN**.

## Required reviewer questions
- Does this installed U-Boot scan SD at startup, and under which documented, non-destructive conditions?
- Does it support `fatload`, `ext4load`, `autoscr`, `booti`, and the necessary ARM64 initramfs/FDT path? A command in a related source tree does *not* count.
- Which U-Boot MMC controller is external SD? Never substitute Android `mmcblk1` or `mmcblk0` numbers.
- Does a candidate kernel/DTB/initramfs load layout avoid overlap and stay within the observed DRAM map?
- Are observed Android SD CMD18 CRC failures resolved with reproducible **device-side** evidence?
- Is normal Android startup preserved with the SD removed, without modifying eMMC or U-Boot environment?

## Stop conditions
Do not progress to an external boot candidate if firmware provenance, board revision, U-Boot external SD behavior, MMC mapping, memory layout, compatible DTB or GameBox SD reliability is unknown. Do not use a generic `aml_autoscript`, vendor recovery package or internal-storage command.

## Artifact checklist for review
- [ ] Provenance and SHA-256 of exact firmware or redacted passive boot log, with acquisition method
- [ ] Board revision and installed firmware correlation
- [ ] Boot decision path and SD enumeration demonstrated with primary evidence
- [ ] U-Boot command capabilities and MMC index supported by primary evidence
- [ ] SD CRC/reliability diagnosis recorded
- [ ] Known-good Android fallback documented
- [ ] Independent review completed

**Acceptance:** Update `hardware/evidence/vayava-franklin-external-boot.json` only with verified facts, add failing-first tests for any changed evidence parser, and run `python -m unittest discover -s boot/tests -p 'test_*.py' -v`. Until then, `external_uboot_boot_path_verified=false` and `can_flash=false` remain unchanged.
