# RetroVerse opt-in automatic game library

On an **already-running graphical Linux installation**, point the kiosk launcher at a specifically mounted removable ROM directory:

```sh
RETROVERSE_ROM_ROOT="/media/user/GAMES/roms" sh boot/tools/launch_neon_arm.sh
```

If Chromium and Python 3 are installed, the launcher starts a **loopback-only** local service on port 8769 and opens the RetroVerse title screen. Press **Offline Mode** or **Start**, then select **Game Library**. It automatically displays game names indexed from that configured directory, with no JSON-import step. This is read-only discovery; no ROMs or saves are modified, uploaded, or launched. It doesn't mount media, detect disks automatically, or touch the Android partition. No Wi-Fi or RetroVerse Online login is needed. Without `RETROVERSE_ROM_ROOT`, the existing file-based title screen remains the default and manual JSON import remains available.

The UI's index currently lists titles and system labels; an emulator launcher, artwork, richer metadata, native drive selection, and a full bootable ARM image are future milestones.

Do not use the server on untrusted networks or expose its port. The local server listens on 127.0.0.1, not 0.0.0.0.
