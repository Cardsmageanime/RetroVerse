# ARM SD boot: planning, testing, and review workflow

**Status:** a compatible external EmuELEC reference system booted successfully on the Vayava/Franklin hardware on 2026-10-23. A RetroVerse-built image has not yet booted. This document does not authorize writing internal eMMC.

## Goal and scope
Reach a **controlled, non-destructive RetroVerse external-media boot** on the observed Vayava/Franklin `g12a_u212_2g` board, then generalize validated knowledge into Versus Tree profiles. Keep the shared RetroVerse userspace separate from board-specific bootloader, kernel, DTB, and driver details. Do not postpone this boot milestone for frontend, online, or multiplayer features.

## Current verified baseline
- The box physically booted an existing EmuELEC system from external removable media after the recovery/reset trigger.
- `dtb.img` exactly matched `device_trees/g12a_s905x2_2g.dtb` by SHA-256: `66f024a72e9e9c6efcf2e1e61ea6338afb29be12ff2b0da41d1b792b38d17966`.
- EmuELEC's `kernel.img` and `SYSTEM` matched their recorded MD5 values.
- HDMI video, the EmuELEC splash, EmulationStation collection loading, and the frontend were observed.
- Controller input, HDMI audio, networking, repeat boot, and Android fallback after removing the media remain unverified.
- This reference boot proves that the installed vendor firmware can start a compatible external ARM system. It does not prove that RetroVerse's kernel, DTB, initramfs, modules, or root filesystem boot.
- ARM64 kernel/DTB, diagnostic initramfs, Debian ARM64 rootfs tar, and ext4 partition artifacts have CI build records; those records alone do not prove physical RetroVerse boot.
- Observed vendor bootloader: `U-Boot 2015.01-g51e6fd64e9-dirty`. Exact MMC numbering, commands, load addresses, and boot-script execution remain unobserved.
- Earlier Android logs included CMD18 CRC errors. One completed boot is useful evidence but does not establish capacity-wide or long-duration media reliability.
- `boot/tools/check_external_boot_readiness.py` is evidence-only and always reports `can_flash: false`.

## Engineering operating rules (Superpowers-style)
1. **Plan before code:** document the problem, alternatives, exact board-specific evidence, acceptance criteria, and rollback procedure. Distinguish observed facts from inferences.
2. **Red-green-refactor:** add a failing regression test for each new parser or validator; run that test; make the smallest implementation change; rerun the focused tests and full `boot/tests` suite.
3. **Debug with evidence:** reproduce failures, capture sanitized logs, isolate root cause, and avoid speculative bootloader edits.
4. **Work in topic branches:** protect `main` in practice; submit a pull request with change summary, evidence, test output, known risks, and rollback notes. Do not auto-merge.
5. **Review twice:** technical review of assumptions and independent review of tests and readiness claims. Require the hardware owner's supervision for device-side experiments.
6. **Verify honestly:** CI establishes code and build checks. Record a physical boot only for the exact image, board, and observed functions.

## Ordered gates and deliverables

### Gate A — reproduce the software-only baseline
- [ ] Run `python -m unittest discover -s boot/tests -p 'test_*.py' -v`.
- [ ] Run `python boot/tools/plan_franklin_uboot.py`.
- [ ] Run `python boot/tools/check_external_boot_readiness.py`; capture a redacted report.
- [ ] Review `.github/workflows/check-gamebox-readiness.yml` and the kernel, initramfs, rootfs, and external-media preflight workflows.
- **Exit:** tests and scripts produce reproducible reports; failures become issues with logs.

### Gate B — identify the installed vendor external boot chain
- [x] Demonstrate that the installed vendor firmware can start a compatible external system using the recovery/reset trigger.
- [x] Record the active reference DTB and verify the reference kernel and system checksums.
- [ ] Identify exact U-Boot MMC numbering, supported commands, boot-script path, and load addresses from passive logs or exact matching firmware evidence.
- [ ] Confirm whether later boots work without holding Reset.
- **Exit:** the high-level external boot route is physically demonstrated; low-level details needed for a RetroVerse image remain documented as unknown.

### Gate C — match RetroVerse kernel, DTB, modules, and initramfs
- [ ] Treat the working EmuELEC `g12a_s905x2_2g.dtb` as compatibility evidence only; do not copy it into a differently built kernel without validation.
- [ ] Validate a kernel-built G12A/S905X2 candidate DTB against the actual board hardware.
- [ ] Validate kernel architecture, initramfs contents, module ABI, storage drivers, HDMI, and early console settings.
- [ ] Add offline tests for malformed or mismatched metadata before altering validators.
- **Exit:** versioned RetroVerse evidence packet and reproducible offline checks.

### Gate D — assess removable-media integrity and fallback
- [ ] Reboot the reference system and confirm external boot repeatability.
- [ ] Remove the external media and verify normal Android startup, establishing fallback without an internal-storage change.
- [ ] Test controller input, HDMI audio, shutdown, and at least one game launch/exit.
- [ ] Resolve or bound the earlier GameBox SD CMD18 CRC errors with device-side diagnostics.
- [ ] Validate the external-only partition plan, root filesystem UUIDs, and non-flashing recovery procedure.
- **Exit:** repeatable reference boot and fallback evidence with explicit remaining hardware limitations.

### Gate E — supervised first RetroVerse boot
- [ ] Assemble a board-specific external-media diagnostic candidate from the repository-built kernel, DTB, initramfs, modules, and rootfs.
- [ ] Independently inspect its partition table, checksums, boot files, and absence of internal-storage write commands.
- [ ] On physical hardware, record boot source, kernel start, rootfs mount, HDMI output, input, and health checks.
- [ ] Preserve Android/eMMC and re-verify fallback with the media removed.
- **Exit:** timestamped, repeatable device-specific RetroVerse proof. Do not extrapolate it to other ARM products.

## Pull request checklist
- [x] Linked gate and problem statement; observed evidence separated from assumptions
- [ ] Focused tests plus the entire `boot/tests` suite run; output linked
- [x] Safe operations: no internal disk writes, firmware commands, secrets, or private identifiers committed
- [ ] Source, DTB, kernel provenance, and licenses documented
- [ ] Reviewer signs off on risks and remaining hardware assumptions
- [ ] Main branch unchanged until review and manual merge

## Next concrete work item
Complete Gate D's repeat-boot and Android-fallback checks, capture the running EmuELEC kernel and hardware identifiers, and then prepare the smallest external-only RetroVerse diagnostic boot candidate for Gate E.

The successful EmuELEC run is an important board-compatibility result. It is not a declaration that RetroVerse itself is bootable.
