#!/bin/sh
# RetroVerse user-space kiosk launcher for an already booted Linux desktop.
# Does not modify bootloader, firmware, disk partitions, or system services.
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(CDPATH= cd -- "$HERE/../.." && pwd)
PAGE="$ROOT/interface/title-screen/index.html"
# Keep the title screen as the first interactive page. The Neon Showcase remains
# reachable after selecting Start or Offline Mode.
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
if [ -n "${RETROVERSE_ROM_ROOT:-}" ]; then
  if [ ! -d "$RETROVERSE_ROM_ROOT" ]; then
    echo "Configured ROM directory unavailable: $RETROVERSE_ROM_ROOT" >&2
    exit 4
  fi
  # Start the loopback-only library service in the foreground; the browser
  # accesses it at localhost. No mounts or changes to Android are performed.
  python3 "$ROOT/library/library_ui_server.py" --rom-root "$RETROVERSE_ROM_ROOT" &
  SERVICE_PID=$!
  trap 'kill "$SERVICE_PID" 2>/dev/null || true' EXIT INT TERM
  "$BROWSER" --kiosk --no-first-run --disable-session-crashed-bubble "http://127.0.0.1:8769/"
  exit $?
fi
exec "$BROWSER" --kiosk --no-first-run --disable-session-crashed-bubble "file://$PAGE"
