# RetroVerse ARM removable SD card compatibility policy

Status: **design requirement**, not a claim of tested hardware support.

## Scope
RetroVerse Systems Edition should accept **any SD/microSD brand**, including generic and off-brand media, if the card and the target ARM device meet technical compatibility and reliability checks. No vendor whitelist or preferred brand may be used as an eligibility gate. Device/reader electrical and bootloader compatibility still determine whether a particular card can boot.

- **Capacity ceiling: 1 TB (1,000,000,000,000 bytes).** Above this maximum is unsupported and must not be offered as an install target. A reported size of 1 TiB is *larger* than 1 TB and is outside this cap.
- Media classes: SD/SDHC/SDXC where supported by the board's SD host and firmware. Do not promise all cards or devices work; validate them.
- The installer should support boot from SD and separately USB where the device's boot chain permits. Both require hardware verification.
- Prefer usable devices with stable read/write behavior. Never assume genuine capacity from the printed label or manufacturer ID.

## Proposed installer gates (not yet implemented or tested)
1. **Identify destination unambiguously:** explicit user confirmation of correct removable physical drive, path, model, size and transport; detect/reject internal Android eMMC and mounted system disks. If removable-ness cannot be established, block rather than guess.
2. **Capacity checks:** device capacity must be sufficient for the boot image plus a reserved margin and at most 1,000,000,000,000 bytes. Check actual block-device size in bytes, not marketing labels or partition size.
3. **Non-destructive preflight:** check SD reader availability, write protection, detected health warnings, partition tables, existing data warning; do not silently erase or automatically select a target.
4. **Consent:** clear warning that installing a disk image erases the chosen external card, plus a separate explicit destructive-action confirmation before any writes.
5. **Integrity:** validate signed/trusted image provenance if available and always verify download checksums; perform post-write block readback integrity verification.
6. **False-capacity and I/O failure screening:** recommend full-capacity test on expendable blank media; never run destructive capacity testing on a card containing valuable data. Reject suspect/counterfeit-capacity behavior and repeated SD CRC/I/O errors.
7. **Boot compatibility:** select board-specific device tree and bootloader profile only when independently verified. File-system support, SDXC/exFAT, GPT/MBR firmware expectations and >32 GB/128 GB/1 TB boot limits vary by device; do not conflate Linux card reading with U-Boot boot ability.
8. **Preserve internals:** never write/flash Android/eMMC. The current Franklin candidate is research-only; do not enable physical boot or image flashing from this policy.

## Acceptance criteria for future implementation
- Unit tests at 32 GB, 64 GB, 128 GB, 256 GB, 512 GB, exactly 1 TB, over 1 TB and exactly 1 TiB.
- Same behavior for brand-name and generic cards with otherwise identical characteristics.
- Fail-closed handling for unknown capacity, no removable transport evidence, ambiguous target, unreadable medium, write protection, CRC faults and unreliable readback.
- No write operation performed by inventory, compatibility or diagnostic tools.
- A separate hardware test matrix for each ARM board, boot ROM/U-Boot path, capacity and card family.
