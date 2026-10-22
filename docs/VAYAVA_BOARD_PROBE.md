# Vayava GameBox board-identification milestone

The kernel, initramfs, ext4 root filesystem and external-SD structural preflight have built successfully. **External SD boot is NOT verified**. A commercial label and an old EmuELEC DTB do not establish the board's U-Boot capabilities.

To gather board information without flashing, run the optional `boot/tools/probe_android_board.py` on a computer with Android platform-tools installed, and only after you explicitly enable/authorize Android Debug Bridge (ADB) on your own GameBox.

```bash
python3 boot/tools/probe_android_board.py --output vayava-board-survey.json
```

The script only runs Android read-only shell commands: non-unique hardware properties, kernel release, device tree model/compatible information and MMC host names. It does not run `adb root`, flash, repartition, change Android settings, reboot, unlock anything, or query serial numbers/accounts/MAC addresses. The local JSON may still contain model or device-specific information; review before sharing.

ADB availability varies; absence of ADB does not prove incompatibility. Do not execute this on an untrusted device. The report cannot tell us whether SD boot works; for that we still need vendor U-Boot behavior, board revision, bootloader/DRAM initialization and actual hardware evidence.

Do **not** flash the existing ext4 file or diagnostic ZIP. They are *not* bootable SD images.

Next engineering gate: corroborate the exact hardware revision and external boot path, select board-matched upstream DTB, then prepare a controlled removable-media boot test.
