#!/bin/sh
# Reproducible ARM64 kernel build helper. Does not create boot media.
set -eu
if [ "$#" -ne 2 ]; then echo "Usage: $0 KERNEL_SOURCE OUTPUT_DIRECTORY" >&2; exit 2; fi
SRC=$(cd "$1" && pwd -P)
mkdir -p "$2"
OUT=$(cd "$2" && pwd -P)
[ "$SRC" != "$OUT" ] || { echo "Output must differ from source" >&2; exit 2; }
[ -f "$SRC/Makefile" ] && [ -d "$SRC/arch/arm64" ] || { echo "Not an ARM64 kernel source tree" >&2; exit 2; }
command -v make >/dev/null
CROSS_COMPILE=${CROSS_COMPILE:-aarch64-linux-gnu-}
command -v "${CROSS_COMPILE}gcc" >/dev/null || { echo "Missing cross compiler: ${CROSS_COMPILE}gcc" >&2; exit 3; }
JOBS=${JOBS:-2}
case "$JOBS" in *[!0-9]*|'') echo "JOBS must be a positive integer" >&2; exit 2;; esac
[ "$JOBS" -gt 0 ] || exit 2
make -C "$SRC" O="$OUT" ARCH=arm64 CROSS_COMPILE="$CROSS_COMPILE" defconfig
make -C "$SRC" O="$OUT" ARCH=arm64 CROSS_COMPILE="$CROSS_COMPILE" -j"$JOBS" Image dtbs modules
[ -s "$OUT/arch/arm64/boot/Image" ] || { echo "Kernel Image missing" >&2; exit 4; }
echo "Kernel Image: $OUT/arch/arm64/boot/Image"
echo "DTBs are under $OUT/arch/arm64/boot/dts/"
echo "No DTB was selected or tested for the GameBox."
