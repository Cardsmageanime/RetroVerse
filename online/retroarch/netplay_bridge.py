#!/usr/bin/env python3
"""RetroVerse bridge to RetroArch's native netplay command-line interface.

Launches RetroArch as a subprocess. It does NOT implement the netplay protocol.
No ROMs, cores, keys, account details, or firewall settings are distributed.
"""
import argparse
import ipaddress
from pathlib import Path
import re
import shutil
import subprocess
import sys
import json
import tempfile
from controller_config import generate

HOST_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.:-]{0,252}$")
NICK_RE = re.compile(r"^[A-Za-z0-9_ -]{1,32}$")

def validate_peer(value):
    if not value or not HOST_RE.fullmatch(value):
        raise ValueError("Peer must be a hostname or IP address (no URL, credentials or spaces)")
    if ":" in value:
        try:
            ipaddress.ip_address(value)
        except ValueError as exc:
            raise ValueError("IPv6 peers must be raw valid IPv6 addresses") from exc
    return value

def build_command(mode, binary, core, content, peer=None, port=55435, nick=None):
    if mode not in ("host", "join", "spectate"):
        raise ValueError("mode must be host, join or spectate")
    binary = str(binary)
    if not binary.strip():
        raise ValueError("RetroArch executable required")
    core, content = Path(core), Path(content)
    if not core.is_file():
        raise ValueError("The selected libretro core file does not exist")
    if not content.is_file():
        raise ValueError("The selected game content file does not exist")
    if not isinstance(port, int) or not 1 <= port <= 65535:
        raise ValueError("Invalid port")
    if mode in ("join", "spectate") and not peer:
        raise ValueError("Joining/spectating requires peer address")
    if peer:
        validate_peer(peer)
    if nick is not None and not NICK_RE.fullmatch(nick):
        raise ValueError("Nickname must be 1-32 simple characters")
    args = [binary, "-L", str(core.resolve())]
    if mode == "host":
        args.append("--host")
    else:
        args.extend(["--connect", peer])
        if mode == "spectate":
            args.append("--spectate")
    args.extend(["--port", str(port)])
    if nick:
        args.extend(["--nick", nick])
    args.append(str(content.resolve()))
    return args

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["host", "join", "spectate"])
    parser.add_argument("--core", required=True, help="Installed compatible libretro core .so/.dll/.dylib")
    parser.add_argument("--content", required=True, help="User-owned game file")
    parser.add_argument("--peer", help="Host IP/DNS name for joining or spectating")
    parser.add_argument("--port", type=int, default=55435)
    parser.add_argument("--nick")
    parser.add_argument("--retroarch", default="retroarch", help="RetroArch executable or path")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print planned command without launching")
    parser.add_argument("--controller-profiles", type=Path, help="Opt-in JSON file with two verified RetroArch device indices and button mappings")
    args = parser.parse_args(argv)
    try:
        cmd = build_command(args.mode, args.retroarch, args.core, args.content, args.peer, args.port, args.nick)
    except ValueError as exc:
        parser.error(str(exc))
    if args.controller_profiles:
        try:
            source = json.loads(args.controller_profiles.read_text(encoding="utf-8"))
            overlay = generate(source["players"])
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            parser.error("Invalid controller profiles: " + str(exc))
    else:
        overlay = None
    if args.dry_run:
        # shlex.join for readable POSIX output only. Actual launch is argv-based.
        import shlex
        if overlay is not None:
            print("Controller overlay validated; --appendconfig will be used at launch.")
        print(shlex.join(cmd))
        return 0
    if not (Path(args.retroarch).is_file() or shutil.which(args.retroarch)):
        parser.error("RetroArch executable not found")
    try:
        if overlay is not None:
            with tempfile.TemporaryDirectory(prefix="retroverse-netplay-") as tempdir:
                overlay_file = Path(tempdir) / "controllers.cfg"
                overlay_file.write_text(overlay, encoding="utf-8")
                cmd[1:1] = ["--appendconfig", str(overlay_file)]
                return subprocess.call(cmd)
        return subprocess.call(cmd)
    except OSError as exc:
        print(f"Failed to launch RetroArch: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
