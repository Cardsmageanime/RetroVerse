#!/usr/bin/env bash
set -euo pipefail
ROOTFS_DIR="${1:?rootfs artifacts dir required}"
KERNEL_DIR="${2:?kernel artifacts dir required}"
OUTPUT="${3:?output ext4 filename required}"
test ! -e "$OUTPUT" || { echo 'Refusing existing image' >&2; exit 2; }
command -v mkfs.ext4 >/dev/null
command -v e2fsck >/dev/null
command -v debugfs >/dev/null
ROOTFS_TAR="$(find "$ROOTFS_DIR" -type f -name 'retroverse-arm64-rootfs.tar.gz' -print -quit)"
MODULES_TAR="$(find "$KERNEL_DIR" -type f -name 'modules.tar.gz' -print -quit)"
test -s "$ROOTFS_TAR" && test -s "$MODULES_TAR" || { echo 'Missing pinned rootfs/modules tarballs' >&2; exit 2; }
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir "$TMP/root"
# Never trust archive paths: block absolute paths / .. traversal and symlinks outside archive.
python3 rootfs/check_tar_safety.py "$ROOTFS_TAR" "$MODULES_TAR"
tar -xzf "$ROOTFS_TAR" -C "$TMP/root" --no-same-owner --exclude="./dev/*" --exclude="dev/*"
tar -xzf "$MODULES_TAR" -C "$TMP/root" --no-same-owner --exclude="./dev/*" --exclude="dev/*"
test -e "$TMP/root/sbin/init" -o -e "$TMP/root/usr/lib/systemd/systemd"
test -d "$TMP/root/lib/modules" || test -d "$TMP/root/usr/lib/modules"
mkdir -p "$(dirname "$OUTPUT")"
# Use mkfs.ext4 -d to populate image without loop-mount or writing block devices.
SIZE_MIB="$(du -sm "$TMP/root" | awk '{print $1}')"
SIZE_MIB="$((SIZE_MIB + SIZE_MIB / 2 + 512))"
truncate -s "${SIZE_MIB}M" "$OUTPUT"
mkfs.ext4 -F -L RETROVERSE_ROOT -d "$TMP/root" "$OUTPUT"
e2fsck -fn "$OUTPUT"
echo 'Created ext4 partition image only; never a bootable SD image'
