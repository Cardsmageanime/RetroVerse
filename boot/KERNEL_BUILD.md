# ARM64 kernel build preparation

**Not a bootable release.** This milestone provides a cross-compilation script for a user-supplied Linux kernel source tree. It does not download or patch a kernel, assert compatibility with the Vayava GameBox, select a DTB, flash media, or install to Android/eMMC.

On a Linux build machine, install `make`, `gcc-aarch64-linux-gnu`, `binutils-aarch64-linux-gnu`, and the standard kernel build prerequisites for your selected source version (typically bc, bison, flex, libssl-dev, libelf-dev, and device-tree-compiler). Use a trusted complete Linux source checkout compatible with your intended bootloader and hardware.

```sh
JOBS=2 CROSS_COMPILE=aarch64-linux-gnu- sh boot/tools/build_arm64_kernel.sh /path/to/linux /path/to/output
```

The script builds an ARM64 `Image`, in-tree DTBs, and modules in the separate output directory. The **generic defconfig is only an initial build check**, not proof of appropriate driver support. Review kernel configuration, match the DTB to the exact board, review serial output and existing working EmuELEC boot parameters before any boot attempt.

Next gate: obtain and inspect actual copies of `aml_autoscript`, `cfgload`, `config.ini`, and `dtb.img` from the known-working EmuELEC installation, then choose and validate a device-specific boot configuration. Never overwrite internal Android storage.


## Real ARM64 cross-build GitHub Action (experimental)

A new manually triggered workflow, **Build ARM64 Linux Kernel (Experimental)**, downloads upstream Linux 6.6 source from kernel.org and runs the cross-compiler to build the ARM64 `Image`, in-tree DTBs and modules. It is deliberately *not* part of every commit's quick syntax-test workflow.

In GitHub Actions, select **Build ARM64 Linux Kernel (Experimental)** → **Run workflow**. If compilation succeeds, the workflow uploads a short-lived artifact bundle with the `Image`, DTBs archive, and SHA-256 manifest. Results have **not yet been run or confirmed**.

The artifact is **not a bootable image**. Linux 6.6 generic `defconfig` does not prove any Vayava GameBox drivers, kernel command line, DTB, display, Wi-Fi, storage or bootloader compatibility. This workflow does not touch Android/eMMC, produce an SD/USB image, or install a kernel on hardware. Do not flash these artifacts to your device.

For the actual first hardware attempt, the separate gate remains inspection of the known-working EmuELEC boot-reference copies, followed by a board-specific kernel/DTB and removable-media boot design.
