#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:?Rootfs path required}"
test -d "$ROOT"
test -x "$ROOT/sbin/init" -o -x "$ROOT/lib/systemd/systemd" -o -x "$ROOT/usr/lib/systemd/systemd"
test -s "$ROOT/etc/retroverse/release"
test -s "$ROOT/etc/passwd"
test -d "$ROOT/usr/lib" -o -d "$ROOT/lib"
test ! -e "$ROOT/usr/bin/qemu-aarch64-static"
file "$ROOT/bin/sh" | grep -qi 'symbolic link\|ARM aarch64\|ARM64' || true
test -f "$ROOT/etc/systemd/network/20-wired.network"
echo "Structural rootfs checks passed; no real ARM board boot verification."
