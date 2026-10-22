#!/usr/bin/env bash
set -euo pipefail
# Creates a read-only diagnostic initramfs. Never writes to a block device.
OUT="${1:?usage: build-initramfs.sh OUTPUT_DIRECTORY}"
test ! -e "$OUT" || { echo "Refusing existing output path" >&2; exit 2; }
command -v dpkg-deb >/dev/null
command -v cpio >/dev/null
command -v gzip >/dev/null
command -v readelf >/dev/null
mkdir -p "$OUT" "$OUT/rootfs"
ROOT="$OUT/rootfs"
cp "$(dirname "$0")/init" "$ROOT/init"
chmod 755 "$ROOT/init"
mkdir -p "$ROOT/bin" "$ROOT/sbin" "$ROOT/proc" "$ROOT/sys" "$ROOT/dev" "$ROOT/etc" "$ROOT/run" "$ROOT/tmp" "$ROOT/usr/bin"
PKG="$(find . -maxdepth 1 -name 'busybox-static_*_arm64.deb' -type f -print -quit)"
test -n "$PKG" || { echo "Missing downloaded arm64 busybox-static .deb" >&2; exit 2; }
dpkg-deb -x "$PKG" "$OUT/pkg"
BUSYBOX="$(find "$OUT/pkg" -type f -name busybox -print -quit)"
test -n "$BUSYBOX" && test -s "$BUSYBOX" || { echo "ARM64 BusyBox binary missing in package" >&2; exit 2; }
cp "$BUSYBOX" "$ROOT/bin/busybox"
readelf -h "$ROOT/bin/busybox" | grep -q 'Machine:.*AArch64'
if readelf -l "$ROOT/bin/busybox" | grep -q INTERP; then echo 'BusyBox not static' >&2; exit 2; fi
for c in sh mount mkdir echo uname cat ls dmesg sleep; do ln -s busybox "$ROOT/bin/$c"; done
( cd "$ROOT" && find . -print0 | LC_ALL=C sort -z | cpio --null -o -H newc 2>/dev/null | gzip -n -9 > "../RetroVerse-ARM64-DIAGNOSTIC-initramfs.cpio.gz" )
gzip -t "$OUT/RetroVerse-ARM64-DIAGNOSTIC-initramfs.cpio.gz"
sha256sum "$OUT/RetroVerse-ARM64-DIAGNOSTIC-initramfs.cpio.gz" > "$OUT/SHA256SUMS"
echo "Diagnostic initramfs built, NOT BOARD BOOT VERIFIED"
