# Milestone 9 — minimal ARM64 userspace (offline)

Host checks confirmed GCC 13.3 cross compiler, `make`, `cpio`, `gzip`, `file`, 760 GB free, and Linux config `CONFIG_BLK_DEV_INITRD=y`, `CONFIG_DEVTMPFS=y`. The host BusyBox is **not** an ARM64 target binary.

## Preparation

Install cross-build support if missing:

```bash
sudo apt update
sudo apt install -y git make gcc-aarch64-linux-gnu binutils-aarch64-linux-gnu cpio gzip bc bison flex libncurses-dev
```

Get a trusted BusyBox release from its official source and verify its upstream published checksum/signature before unpacking; do not use a random mirror. Extract it outside the repo, e.g. `~/src/busybox-1.37.0` (version/path example only; use the actual extracted source directory).

## Build locally

```bash
cd ~/Downloads/RetroVerse-Development
git pull --ff-only
JOBS=4 bash boot/tools/build_arm64_initramfs.sh "$HOME/src/busybox-1.37.0" "$HOME/retroverse-build/initramfs-001"
```

The script builds a static AArch64 BusyBox, checks ELF architecture and absence of a dynamic interpreter, creates an initramfs with `/init`, and validates gzip integrity. If a host/toolchain BusyBox build error occurs, stop and report the output. It does not connect to the GameBox, write SD cards, or install anything to Android.

Inspect the result with `ls -lh ~/retroverse-build/initramfs-001/retroverse-arm64-initramfs.cpio.gz`.

## Safety gate

An initramfs build is separate from verification of DDR layout, regulator wiring, SD card detection, external U-Boot handoff, appropriate DTB and non-destructive hardware boot. Do not flash or try a boot with the research-only Franklin DTB.
