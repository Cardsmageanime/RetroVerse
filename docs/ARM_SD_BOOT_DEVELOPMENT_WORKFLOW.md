# ARM SD boot: planning, testing, and review workflow

**Status:** proposal; hardware boot is NOT verified. This document does not authorize writing media or changing eMMC.

## Goal and scope
Reach a **controlled, non-destructive first external-SD boot** on the observed Vayava/Franklin `g12a_u212_2g` board, then generalize validated knowledge into Versus Tree profiles. Keep the shared RetroVerse userspace separate from board-specific bootloader/kernel/DTB details. Do not postpone this boot milestone for frontend, online, or multiplayer features.

## Current verified repository baseline
- ARM64 kernel/DTB, diagnostic initramfs, Debian ARM64 rootfs tar, and ext4 partition artifacts have CI build records; **none proves the physical device boots RetroVerse**.
- Observed vendor bootloader: `U-Boot 2015.01-g51e6fd64e9-dirty`. Its environment, MMC numbering, script support, load addresses, and external boot selection are **not verified**.
- Android saw the SD controller and card, but kernel logs recorded CMD18 CRC errors. Windows readback success does not establish device-side reliability.
- The existing `boot/tools/check_external_boot_readiness.py` is evidence-only and always reports `can_flash: false`.

## Engineering operating rules (Superpowers-style)
1. **Plan before code:** document the problem, alternatives, exact board-specific evidence, acceptance criteria, and rollback procedure. Distinguish observed facts from inferences.
2. **Red-green-refactor:** add a failing regression test for each new parser/validator; run that test; make the smallest implementation change; rerun the focused tests and full `boot/tests` suite.
3. **Debug with evidence:** reproduce failures, capture sanitized logs, isolate root cause, and avoid speculative bootloader edits.
4. **Work in topic branches:** protect `main` in practice; submit a pull request with change summary, evidence, test output, known risks, and rollback notes. Do not auto-merge.
5. **Review twice:** technical review of assumptions/security and independent review of tests/readiness claims. Require human hardware owner approval before any device-side boot experiment.
6. **Verify honestly:** CI success establishes code/build checks only. Never label an image “bootable” without documented, repeatable physical boot evidence.

## Ordered gates and deliverables

### Gate A — reproduce the current software-only baseline
- [ ] Run `python -m unittest discover -s boot/tests -p 'test_*.py' -v`.
- [ ] Run `python boot/tools/plan_franklin_uboot.py`.
- [ ] Run `python boot/tools/check_external_boot_readiness.py`; capture a redacted report.
- [ ] Review `.github/workflows/check-gamebox-readiness.yml` and the kernel, initramfs, rootfs and external SD preflight workflows.
- **Exit:** tests and scripts produce reproducible reports; failures become issues with logs. No hardware claims.

### Gate B — identify the installed vendor external boot chain (current blocker)
- [ ] Acquire only passive UART logs if a documented, safe, non-invasive connector exists, **or** inspect exact matching vendor firmware offline.
- [ ] Record boot-source detection, supported observation commands, MMC numbering and storage-controller mapping; do not equate U-Boot `mmc 0` with Android `/dev/mmcblk0`.
- [ ] Investigate recovery triggers and `aml_autoscript` behavior using exact firmware evidence, not analogous source trees alone.
- [ ] Document bootloader command support, addresses, RAM overlap risk, SD controller reliability, and fallback route.
- **Exit:** reviewed evidence supports (or rejects) a specific read-only external boot path. Unknowns remain false, not assumed true.

### Gate C — match kernel, DTB, modules and initramfs to the board
- [ ] Validate mainline candidate DTB against actual board hardware and compiled kernel version; a DTB header is not sufficient.
- [ ] Validate kernel architecture, initramfs contents, module ABI and early console settings.
- [ ] Add offline tests for malformed/mismatched metadata before altering validators.
- **Exit:** versioned evidence packet and reproducible offline checks. Still no physical boot claim.

### Gate D — assess removable-media integrity and boot layout
- [ ] Resolve observed GameBox SD CMD18 CRC errors with device-side non-destructive diagnostics.
- [ ] Validate external-only partition plan, root filesystem UUID choices, read-only preflight and a non-flashing recovery procedure.
- [ ] Human-review every boot script command; never execute untrusted binary `aml_autoscript`, recovery, environment-write or erase instructions.
- **Exit:** owner-approved experiment plan with stop conditions and verified fallback, without any internal write.

### Gate E — supervised first boot (later, gated)
- [ ] Only after B–D succeed, assemble a board-specific external-SD candidate and independently review its contents.
- [ ] On physical hardware, record serial console, boot source, kernel start, rootfs mount, and health checks.
- [ ] Preserve original Android/eMMC and verify normal fallback on card removal.
- **Exit:** timestamped repeatable device-specific proof; do not extrapolate to other ARM products.

## Pull request checklist
- [ ] Linked gate and problem statement; observed evidence versus assumptions
- [ ] New failing test captured before implementation where code changes
- [ ] Focused tests plus entire `boot/tests` suite run; output linked
- [ ] Safe operations: no disk writes, firmware commands, secrets, or private identifiers in logs
- [ ] Source/DTB/kernel provenance and licenses documented
- [ ] Reviewer signs off on risks and remaining unverified hardware assumptions
- [ ] Main branch unchanged until review and manual merge

## Next concrete work item
**Gate B first:** create a redacted vendor boot-chain evidence packet for `franklin` identifying the actual external-SD boot decision path. Once available, add tests around offline evidence parsing and update the Versus Tree board profile only for directly observed facts.

This plan is intentionally **not** a boot script, flashable image, or declaration of boot success.
