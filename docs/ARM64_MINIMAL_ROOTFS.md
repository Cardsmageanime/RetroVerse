# Minimal ARM64 root filesystem — bring-up stage

This workflow uses Debian 12 (bookworm) ARM64 packages and `debootstrap` to create an **ARM64 filesystem tree**, packaged as a tarball. It is **not** a completed RetroVerse OS and **not** an SD image.

This is a minimal Linux/service foundation only. No RetroArch, gaming interface, ROMs or online services are installed. SSH is disabled; root password is locked. Do not publish credentialed images or private firmware blobs. Configuration intentionally avoids touching Android/eMMC.

The build is designed for GitHub Actions Ubuntu 24.04 x86_64 runners with `qemu-user-static`. It needs verification against runner packages and Debian mirror availability. Structural tests are not proof of bootability.

Next: mountable ext4 image, kernel modules integration (version-matched), fstab and cmdline for specific partition UUIDs, bootloader/board DTB investigation, then hardware testing on **external** SD media.
