# Vayava GameBox — ARM boot reference preflight

**Status:** read-only inspection tool committed. No RetroVerse ARM kernel, boot image, or boot test has been produced.

The first ARM target is provisionally Amlogic G12A/S905X2 (~2 GB RAM). A previously booting EmuELEC installation is a useful *reference*, not a proof that a different kernel/device tree or RetroVerse USB image will boot.

On your computer, copy these **four files from the known-working EmuELEC boot medium** to a separate directory (for example `RetroVerse-Boot-Reference`): `aml_autoscript`, `cfgload`, `config.ini`, and `dtb.img`. Do not modify or overwrite the working boot medium.

From the repository root:

```sh
python3 boot/tools/inspect_boot_reference.py --reference-dir "/path/to/RetroVerse-Boot-Reference"
```

The command prints a JSON manifest with presence, byte sizes, SHA-256 checksums and the DTB/FDT header signature. It **does not** mount a disk, follow symlinks, change any file, infer board compatibility, generate an SD/USB image, or touch internal Android/eMMC. A valid DTB magic signature alone is insufficient to match the board.

Next engineering gates: inspect actual reference content with the owner's permission, identify the exact board/device-tree and supported external boot sequence, obtain kernel sources, compile ARM64 kernel + matched DTB + modules, package rootfs, and then assemble a removable-media image for supervised testing. Do not flash any internal storage.
