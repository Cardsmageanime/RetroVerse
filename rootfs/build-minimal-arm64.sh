#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:?Provide new output directory}"
test ! -e "$ROOT" || { echo "Refusing to overwrite rootfs directory" >&2; exit 2; }
command -v debootstrap >/dev/null
command -v chroot >/dev/null
mkdir -p "$ROOT"
# ARM64 second-stage runs through binfmt/qemu-user-static on Ubuntu x86_64 CI.
debootstrap --arch=arm64 --foreign --variant=minbase --include=ca-certificates,iproute2,iputils-ping,ifupdown,netbase,openssh-server,udev,systemd-sysv,dbus,util-linux,kmod,initramfs-tools,procps,isc-dhcp-client bookworm "$ROOT" http://deb.debian.org/debian
cp /usr/bin/qemu-aarch64-static "$ROOT/usr/bin/qemu-aarch64-static"
chroot "$ROOT" /debootstrap/debootstrap --second-stage
# Avoid inherited runner DNS/network configuration.
cat > "$ROOT/etc/fstab" <<'FSTAB'
proc /proc proc defaults 0 0
tmpfs /tmp tmpfs mode=1777,nosuid,nodev 0 0
FSTAB
printf 'retroverse\n' > "$ROOT/etc/hostname"
cat > "$ROOT/etc/hosts" <<'HOSTS'
127.0.0.1 localhost
127.0.1.1 retroverse
::1 localhost ip6-localhost ip6-loopback
HOSTS
mkdir -p "$ROOT/etc/systemd/network" "$ROOT/etc/retroverse"
cat > "$ROOT/etc/systemd/network/20-wired.network" <<'NETWORK'
[Match]
Type=ether
[Network]
DHCP=yes
NETWORK
cat > "$ROOT/etc/retroverse/release" <<'RELEASE'
RETROVERSE_NAME="RetroVerse Systems Edition"
RETROVERSE_STAGE="arm64-minimal-rootfs"
RETROVERSE_BOOT_VERIFIED="no"
RELEASE
# Disable remote access until unique keys, login and firewall policy are designed.
rm -f "$ROOT/etc/ssh/ssh_host_"*
chroot "$ROOT" /bin/systemctl disable ssh 2>/dev/null || true
chroot "$ROOT" /bin/systemctl enable systemd-networkd 2>/dev/null || true
# Never ship emulator images with embedded builder emulation binary.
rm -f "$ROOT/usr/bin/qemu-aarch64-static"
# Keep root login locked by default; hardware console policy still requires design.
chroot "$ROOT" /usr/bin/passwd -l root >/dev/null
echo "Created minimal ARM64 root filesystem (not bootable on its own)."
