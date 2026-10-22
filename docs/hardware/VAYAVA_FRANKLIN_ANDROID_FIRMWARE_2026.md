# Vayava / TVBOX-GAME — Android firmware observations

Source: user-provided photograph of the device's Android About screen (October 2026).

## Observed
- Device name and model: `TVBOX-GAME`
- Android version: **9**
- Android security patch level: **2018-08-05** (reported by firmware)
- Installed Android Linux kernel release: **4.9.113**
- Kernel string build stamp: `#2 Wed Apr 5 12:42:54 CST 2023`
- Baseband: `Unknown`

## Development interpretation
- The factory firmware has a vendor Linux 4.9.113 kernel. The independently compiled RetroVerse **6.12.12** ARM64 kernel is **not** a drop-in replacement for its kernel modules, DTB, or boot chain.
- The vendor bootloader version and boot path are **not** identified from the screenshot.
- Historical security patch date is reported by the image; it does not establish the actual patch status of individual components.
- Keep `G12A/S905X2` as **candidate, unverified** until compatible/model properties or other hardware evidence confirm the SoC.
- Mainline Panfrost support for a Mali-G31 family GPU is not sufficient to verify HDMI/display operation on this board.

## Required before removable-media boot testing
1. Confirm actual board/SoC ID and compatible strings, ideally by non-destructive ADB read of `/proc/device-tree/compatible` and `/proc/device-tree/model`.
2. Confirm board's U-Boot external boot support and the correct board-matched kernel DTB.
3. Prepare kernel/rootfs boot arguments and external SD layout; do not write eMMC or internal Android.
4. Only then authorize a controlled physical removable-media test.

## Safety
Screenshot is **hardware information**, not proof of external SD boot compatibility. Current compiled artifacts remain **DO NOT FLASH**.
