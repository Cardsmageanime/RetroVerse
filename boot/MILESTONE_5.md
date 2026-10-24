# Milestone 5: ARM64 kernel artifact validation

**Status:** inspection tooling committed; build and physical hardware boot not yet verified.

## On Linux Mint

From the repository root, install the host packages:

```sh
sudo apt update
sudo apt install -y git build-essential bc bison flex libssl-dev libelf-dev \
    gcc-aarch64-linux-gnu device-tree-compiler python3
```

Obtain and independently verify a complete upstream Linux kernel source tree.
The kernel version and correct device-tree **must be selected against the physical board**;
a same-SoC DTB is not automatically compatible. This milestone deliberately does
not choose a bootloader or overwrite Android/eMMC.

With verified kernel source at `$HOME/src/linux`:

```sh
sh boot/tools/build_arm64_kernel.sh "$HOME/src/linux" "$HOME/retroverse-build/kernel-001"
python3 -m unittest discover -s boot/tests -p 'test_arm64_artifacts.py' -v
```

Select a compiled DTB from the **same kernel build output** only after reviewing
the board's model, PCB revision, and device-tree compatibility. Inspect artifacts:

```sh
python3 boot/tools/inspect_arm64_artifacts.py \
    --image "$HOME/retroverse-build/kernel-001/arch/arm64/boot/Image" \
    --dtb "/absolute/path/to/compiled-and-reviewed-board.dtb"
```

A passing header inspection is **not** evidence that the DTB matches hardware,
that the bootloader can load the files, or that the OS boots.

## Hardware acceptance gates (currently incomplete)

- [ ] Kernel source version recorded, toolchain recorded
- [ ] ARM64 Image, modules, and matching compiled DTB exist
- [ ] Exact PCB/board profile and DTB compatibility reviewed
- [ ] Root filesystem and kernel command line validated
- [ ] External SD-card layout and boot chain validated without eMMC writes
- [ ] Serial console boot observed on the real board
- [ ] Android boots normally after SD removal

**Do not flash any image yet.** Prior EmuELEC external boot observations
inform the hardware investigation, but cannot validate a new kernel.
