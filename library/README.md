# RetroVerse opt-in automatic game library

On an **already-running graphical Linux installation**, point the kiosk launcher at a specifically mounted removable ROM directory:

```sh
RETROVERSE_ROM_ROOT="/media/user/GAMES/roms" sh boot/tools/launch_neon_arm.sh
```

If Chromium and Python 3 are installed, the launcher starts a **loopback-only** local service on port 8769 and opens the RetroVerse title screen. Press **Offline Mode** or **Start**, then select **Game Library**. It automatically displays game names indexed from that configured directory, with no JSON-import step. This is read-only discovery; no ROMs or saves are modified, uploaded, or launched. It doesn't mount media, detect disks automatically, or touch the Android partition. No Wi-Fi or RetroVerse Online login is needed. Without `RETROVERSE_ROM_ROOT`, the existing file-based title screen remains the default and manual JSON import remains available.

The UI's index currently lists titles and system labels; an emulator launcher, artwork, richer metadata, native drive selection, and a full bootable ARM image are future milestones.

Do not use the server on untrusted networks or expose its port. The local server listens on 127.0.0.1, not 0.0.0.0.


## Removable drive discovery (Linux preview)

The new optional `library/removable_discovery.py` utility lists candidate `roms` / `ROMS` / `games` / `GAMES` folders on **already-mounted removable drives** under `/media`, `/run/media`, or `/mnt`:

```sh
python3 library/removable_discovery.py
```

This is discovery only: it does not mount, scan, index, or select a drive. It reads Linux `lsblk` metadata. Review a candidate and **explicitly select it** before launching RetroVerse:

```sh
RETROVERSE_ROM_ROOT="/media/user/USB/roms" sh boot/tools/launch_neon_arm.sh
```

No internal Android partition is intentionally discovered. Real hardware and atypical Linux device topology require testing; do not assume every listed mount is safe without user approval. Cover art and metadata are not implemented by this milestone.


## Visual USB/SD drive picker

On an already-running graphical Linux system, opt into the new storage picker with:

```sh
RETROVERSE_DRIVE_PICKER=1 sh boot/tools/launch_neon_arm.sh
```

RetroVerse opens its title screen. Choose **Start** or **Offline Mode**, open **Game Library**, and use **Find drives**. The selector lists *candidate ROM directories from already-mounted removable devices*, and **Scan selected drive** is an explicit choice. Paths are rechecked against current removable-device candidates by the local server before scanning. The service never mounts a disk, writes to ROM files, edits saves, or accesses Android's internal storage intentionally.

This is still a Linux desktop prototype; GameBox boot, actual SD/USB enumeration, native file permissions and platform support are unverified. Never expose this localhost development service to a network or forward its port.
