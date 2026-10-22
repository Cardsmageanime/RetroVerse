# RetroVerse Steam Deck support — planned

Status: **planned, not implemented or hardware-tested**.

Steam Deck uses AMD x86-64 hardware and runs SteamOS. It cannot boot the current RetroVerse ARM64 kernel or use Amlogic device trees. Steam Deck must have an independent x86-64 distribution build or a SteamOS application package.

## Development decision

1. **Phase 1, after ARM GameBox first boot:** provide a RetroVerse **SteamOS frontend application** (ideally Flatpak), preserving the existing SteamOS installation. Bring the game library, controller navigation and RetroArch launcher to Steam Deck's 1280×800 display.
2. **Phase 2, optional:** evaluate a separate **x86-64 RetroVerse bootable image** on external media. This needs EFI boot, AMD GPU drivers, audio, Wi-Fi, gamepad inputs, power management, suspend/resume, and dedicated hardware validation; do not repurpose ARM artifacts.

## Shared and separate components

**Shared:** game library model, emulator launch configuration, themes, profiles and offline feature design, eventual netplay protocol.

**Steam Deck-specific:** x86-64 binaries, SteamOS packaging, gamepad/back-button/trackpad input, screen scaling, battery and suspend-resume testing.

## Safety rules

- No replacement of SteamOS or modifications to the internal NVMe drive as a default setup path.
- No claim of Steam Deck support until actual application builds and hardware tests pass.
- Steam Deck is a **separate target** from the ARM Versus Tree DTB catalog.

## Current priority

Finish the Vayava GameBox external ARM boot chain first. Steam Deck implementation begins after the ARM first-boot milestone.
