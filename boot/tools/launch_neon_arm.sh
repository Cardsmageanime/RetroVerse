#!/bin/sh
# RetroVerse user-space kiosk launcher for an already booted Linux desktop.
# Does not modify bootloader, firmware, disk partitions, or system services.
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(CDPATH= cd -- "$HERE/../.." && pwd)
PAGE="$ROOT/interface/neon-showcase/index.html"
if [ ! -r "$PAGE" ]; then
  echo "RetroVerse UI missing: $PAGE" >&2
  exit 1
fi
if [ -z "${DISPLAY:-}" ] && [ -z "${WAYLAND_DISPLAY:-}" ]; then
  echo "A running X11/Wayland graphical session is required." >&2
  exit 2
fi
BROWSER=""
for candidate in chromium chromium-browser google-chrome; do
  if command -v "$candidate" >/dev/null 2>&1; then BROWSER="$candidate"; break; fi
done
if [ -z "$BROWSER" ]; then
  echo "Chromium is required for this prototype." >&2
  exit 3
fi
exec "$BROWSER" --kiosk --no-first-run --disable-session-crashed-bubble "file://$PAGE"
