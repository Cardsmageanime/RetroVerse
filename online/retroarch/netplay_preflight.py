#!/usr/bin/env python3
"""Read-only local RetroArch netplay diagnostics; never opens firewall ports."""
import argparse
import hashlib
import json
from pathlib import Path
import socket
import sys

def sha256_file(path, chunk=1024 * 1024):
    p = Path(path)
    if not p.is_file():
        raise ValueError("File missing: " + str(p))
    hash_ = hashlib.sha256()
    with p.open("rb") as stream:
        while True:
            part = stream.read(chunk)
            if not part:
                break
            hash_.update(part)
    return hash_.hexdigest()

def check_peer(peer, port=55435, timeout=2.5):
    if not 1 <= port <= 65535:
        raise ValueError("Port must be between 1 and 65535")
    try:
        with socket.create_connection((peer, port), timeout=timeout):
            return {"reachable": True, "detail": "TCP port reachable; RetroArch session not verified"}
    except (OSError, ValueError) as exc:
        return {"reachable": False, "detail": type(exc).__name__ + "; check host, firewall and port"}

def report(core, content, peer=None, port=55435):
    result = {"core_sha256": sha256_file(core), "content_sha256": sha256_file(content),
              "core_file": Path(core).name, "content_file": Path(content).name,
              "port": port, "peer_test": None}
    if peer:
        result["peer_test"] = check_peer(peer, port)
    return result

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--core", required=True)
    p.add_argument("--content", required=True)
    p.add_argument("--peer", help="Other RetroArch host IP/DNS address (optional)")
    p.add_argument("--port", type=int, default=55435)
    a = p.parse_args(argv)
    if not 1 <= a.port <= 65535:
        p.error("Invalid port")
    try:
        print(json.dumps(report(a.core, a.content, a.peer, a.port), indent=2))
    except (OSError, ValueError) as exc:
        p.error(str(exc))
    return 0

if __name__ == "__main__":
    sys.exit(main())
