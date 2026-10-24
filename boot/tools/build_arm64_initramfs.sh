#!/usr/bin/env bash
# Build an ARM64 static BusyBox initramfs, without touching removable/internal storage.
set -euo pipefail
if [[ $# -ne 2 ]]; then echo "Usage: $0 BUSYBOX_SOURCE OUTPUT_DIR" >&2; exit 2; fi
src="$(realpath "$1")"
out="$(realpath -m "$2")"
[[ -f "$src/Makefile" && -f "$src/Config.in" ]] || { echo "Not a BusyBox source tree: $src" >&2; exit 2; }
[[ "$out" != "$src" && "$out" != "$src/"* ]] || { echo "Output must be outside BusyBox source" >&2; exit 2; }
for cmd in make aarch64-linux-gnu-gcc aarch64-linux-gnu-readelf cpio gzip; do command -v "$cmd" >/dev/null || { echo "Missing: $cmd" >&2; exit 2; }; done
mkdir -p "$out"
out="$(realpath "$out")"
build="$out/busybox-build"
root="$out/rootfs"
mkdir -p "$build"
make -C "$src" O="$build" ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- defconfig
# Set static linking and cross compilation without relying on host BusyBox.
sed -i 's/^# CONFIG_STATIC is not set$/CONFIG_STATIC=y/; s/^CONFIG_STATIC=n$/CONFIG_STATIC=y/' "$build/.config"
if ! grep -qx 'CONFIG_STATIC=y' "$build/.config"; then echo 'CONFIG_STATIC option not enabled' >&2; exit 1; fi
make -C "$src" O="$build" ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- oldconfig </dev/null
make -C "$src" O="$build" ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -j"${JOBS:-4}"
test -x "$build/busybox"
aarch64-linux-gnu-readelf -h "$build/busybox" | grep -q 'Machine:.*AArch64'
if aarch64-linux-gnu-readelf -l "$build/busybox" | grep -q INTERP; then echo 'Not static; unexpected interpreter' >&2; exit 1; fi
# Explicit output staging; refuse overwriting a populated rootfs.
if [[ -e "$root/init" || -e "$root/bin/busybox" ]]; then
 echo "Refusing to overwrite populated rootfs: $root" >&2; exit 1
fi
mkdir -p "$root"/{bin,sbin,etc,proc,sys,dev,tmp,run,root}
cp "$build/busybox" "$root/bin/busybox"
# Never execute the AArch64 target binary on the x86_64 build host.
# The default BusyBox config contains ash and mount; install the needed applets only.
ln -s busybox "$root/bin/sh"
ln -s busybox "$root/bin/mount"
# Kernel executes /init directly; BusyBox ARM64 sh executes with no dynamic linker.
cat > "$root/init" <<'EOF'
#!/bin/sh
export PATH=/bin:/sbin:/usr/bin:/usr/sbin
/bin/mount -t devtmpfs devtmpfs /dev || echo "WARNING: devtmpfs mount failed"
/bin/mount -t proc proc /proc || echo "WARNING: proc mount failed"
/bin/mount -t sysfs sysfs /sys || echo "WARNING: sysfs mount failed"
echo "RetroVerse ARM64 early userspace diagnostic (not production)"
echo "No internal storage will be mounted."
exec /bin/sh </dev/console >/dev/console 2>&1
EOF
chmod 0755 "$root/init"
# /bin/sh and core applets must exist; don't package if not.
test -L "$root/bin/sh" && test -L "$root/bin/mount" || { echo "Missing BusyBox shell or mount applet" >&2; exit 1; }
archive="$out/retroverse-arm64-initramfs.cpio.gz"
( cd "$root"; find . -print0 | cpio --null -o -H newc --quiet | gzip -9 > "$archive" )
gzip -t "$archive"
echo "PASS AArch64 static BusyBox and initramfs: $archive"
echo "OFFLINE BUILD ONLY. NOT BOARD BOOT VERIFIED. DO NOT FLASH."
