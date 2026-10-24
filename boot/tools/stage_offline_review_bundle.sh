#!/usr/bin/env bash
# Offline-only archival staging. Never writes to devices or creates boot scripts.
set -euo pipefail
if [[ $# -ne 3 ]]; then
  echo "Usage: $0 ARM64_IMAGE INITRAMFS_CPIO_GZ OUTPUT_DIRECTORY" >&2
  exit 2
fi
kernel="$(realpath "$1")"
initramfs="$(realpath "$2")"
output="$(realpath -m "$3")"
[[ -f "$kernel" && -f "$initramfs" ]] || { echo "Missing input artifact" >&2; exit 2; }
for cmd in python3 sha256sum gzip cpio cmp; do
  command -v "$cmd" >/dev/null || { echo "Missing tool: $cmd" >&2; exit 2; }
done
[[ ! -e "$output" ]] || { echo "Refusing to overwrite existing output: $output" >&2; exit 2; }
python3 - "$kernel" <<'PY'
import pathlib, sys
with pathlib.Path(sys.argv[1]).open("rb") as image:
    image.seek(0x38)
    magic = image.read(4)
if magic != bytes.fromhex("41524d64"):
    raise SystemExit(f"Invalid ARM64 Linux Image header magic: got {magic.hex()}, expected 41524d64")
PY
gzip -t "$initramfs"
gzip -dc "$initramfs" | cpio -t 2>/dev/null | grep -qx 'init' || {
  echo "Missing /init in archive" >&2; exit 1;
}
mkdir -p "$output/artifacts"
cp -- "$kernel" "$output/artifacts/Image"
cp -- "$initramfs" "$output/artifacts/retroverse-arm64-initramfs.cpio.gz"
(
  cd "$output"
  sha256sum artifacts/Image artifacts/retroverse-arm64-initramfs.cpio.gz > SHA256SUMS
)
cat > "$output/NOT_BOOTABLE.txt" <<'EOF'
RETROVERSE - OFFLINE REVIEW BUNDLE ONLY

Contains an ARM64 kernel Image and an initramfs for offline inspection.
NO board-matched DTB, verified U-Boot configuration, SD loader or disk image.
DO NOT write to SD cards, flash devices or launch on Vayava hardware.
The research-only Franklin DTB is intentionally excluded.
Android/eMMC must remain untouched.
EOF
(
  cd "$output"
  sha256sum -c SHA256SUMS
)
cmp -s "$kernel" "$output/artifacts/Image"
cmp -s "$initramfs" "$output/artifacts/retroverse-arm64-initramfs.cpio.gz"
echo "PASS: offline review bundle created at $output"
echo "NOT BOOTABLE. DO NOT FLASH."
