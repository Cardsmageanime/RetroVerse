# RetroVerse first-boot engineering checkpoint

The first ARM64 G12A Linux kernel GitHub build succeeded and published Image, modules and DTBs in a **compiled-not-boot-verified** artifact.

This separate diagnostic initramfs is intentionally **not** the RetroVerse frontend, a complete root filesystem or a flashable SD card. It consists of static ARM64 BusyBox and a console init script. It only mounts ephemeral kernel filesystems, prints the kernel version, and opens a shell. There is no Android/eMMC write operation.

**Do not flash this initramfs**; it needs a matching compiled Image, appropriate board-specific DTB and an existing externally bootable U-Boot boot chain. The downloaded historical DTB references from EmuELEC may not match the compiled upstream kernel.

Open Actions → RetroVerse ARM64 Diagnostic Initramfs → Run workflow. A successful run uploads an artifact. Physical SD boot remains blocked pending confirmed Vayava board boot chain, hardware revision, storage connectivity and boot test plan.

The kernel build run artifact is https://github.com/Cardsmageanime/RetroVerse/actions/runs/39717680785/artifacts/12400194665 .
