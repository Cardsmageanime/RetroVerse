# Milestone 8: Compile-only Franklin DTB gate

The prototype `hardware/dts/meson-g12a-vayava-franklin-experimental.dts` is **not a board-matched or bootable DTB**.

On the Linux Mint development machine, from the RetroVerse clone:

```bash
git pull --ff-only
python3 boot/tools/check_franklin_dtb.py \
  --kernel "$HOME/src/linux" \
  --output "$HOME/retroverse-build/franklin-dtb"
```

Requires `cpp`, `dtc`, `fdtget`, and the exact Linux source previously used for the kernel build. The script preprocesses and compiles the DTS and checks that the experimental board identity is present and that both SD/MMC B and internal eMMC C are disabled. It does not connect to the GameBox, write removable media, modify Android, or validate physical boot.

**Do not flash / do not boot** this artifact. Passing this gate is only a structural/software check.

Next milestones:
- Identify board-specific regulator, GPIO card detect/polarity, DRAM size, bootloader behavior and SD signal reliability using non-destructive evidence.
- Add a minimal root filesystem build/inspection workflow, reproducible offline before any removable-media deployment.
- Verify a board-matched DTB and safe external boot chain before approving physical tests.
