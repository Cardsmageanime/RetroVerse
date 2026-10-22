# External boot staging (not flashing)

The script `boot/tools/stage_external_boot.py` combines an ARM64 Image, a user-supplied **kernel- and board-matched** DTB, and a gzip initramfs into an **extlinux directory** for examination. It does not write to any SD card, create a bootloader, modify eMMC, or prove that the Vayava GameBox can boot it.

Example:

```bash
python3 boot/tools/stage_external_boot.py \
 --kernel ./Image \
 --dtb ./meson-g12a-YOUR-VERIFIED-BOARD.dtb \
 --initramfs ./RetroVerse-ARM64-DIAGNOSTIC-initramfs.cpio.gz \
 --output ./retroverse-external-boot-staging
```

This early bring-up recipe assumes U-Boot already installed on the hardware supports extlinux, and `console=ttyAML0` is only an Amlogic candidate. No physical-test steps should be taken until exact hardware revision and external boot path are confirmed. A valid DTB header is not enough to prove compatibility.

The script always rejects existing destination directories and obviously invalid input formats. **No bootloader binary or flashable SD image is in this output.**
