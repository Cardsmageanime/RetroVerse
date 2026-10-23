#!/usr/bin/env python3
"""Local-only RetroVerse UI with opt-in read-only library discovery."""
import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scan_library import discover
from removable_discovery import discover_mounts
from urllib.parse import parse_qs
import subprocess

REPO=Path(__file__).resolve().parents[1]
class Handler(SimpleHTTPRequestHandler):
    rom_root=None
    allow_selection=False
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(REPO),**kwargs)
    def do_GET(self):
        path=urlsplit(self.path).path
        if path=="/api/drives":
            try:
                roots=discover_mounts() if self.allow_selection else []
                self._send_json(200,{"drives":roots,"selectable":self.allow_selection})
            except (OSError,ValueError,subprocess.SubprocessError):
                self._send_json(503,{"error":"drive_discovery_unavailable"})
            return
        if path=="/api/library":
            try:
                choice=parse_qs(urlsplit(self.path).query).get("drive",[])
                root=self.rom_root
                if choice:
                    if not self.allow_selection or len(choice)!=1 or choice[0] not in discover_mounts():
                        self._send_json(400,{"error":"drive_not_available_or_not_approved"})
                        return
                    root=Path(choice[0])
                games,limited=discover(root) if root else ([],False)
                data={"format":"retroverse-library-v1","games":games,"count":len(games),"truncated":limited,"configured":bool(root)}
                raw=json.dumps(data).encode()
                self.send_response(200)
            except (ValueError,OSError):
                raw=b'{"error":"library_unavailable"}'
                self.send_response(503)
            self.send_header("Content-Type","application/json")
            self.send_header("Cache-Control","no-store")
            self.send_header("Content-Length",str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
            return
        if path=="/":
            self.send_response(302)
            self.send_header("Location","/interface/title-screen/index.html")
            self.end_headers()
            return
        elif path=="/showcase":
            self.path="/interface/neon-showcase/index.html"
        elif not path.startswith(("/interface/","/library/")):
            self.send_error(404)
            return
        return super().do_GET()
    def _send_json(self,code,data):
        raw=json.dumps(data).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type","application/json")
        self.send_header("Cache-Control","no-store")
        self.send_header("Content-Length",str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)
    def log_message(self,*args):
        pass

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rom-root",type=Path,help="Optional explicitly mounted ROM directory")
    p.add_argument("--enable-drive-picker",action="store_true",help="Enable browser selection of removable ROM folders")
    p.add_argument("--port",type=int,default=8769)
    a=p.parse_args()
    if not 1024<=a.port<=65535:p.error("Invalid port")
    root=a.rom_root.resolve(strict=True) if a.rom_root else None
    if root is not None and not root.is_dir():p.error("ROM root must be a directory")
    class LocalHandler(Handler):
        rom_root=root
        allow_selection=a.enable_drive_picker
    server=ThreadingHTTPServer(("127.0.0.1",a.port),LocalHandler)
    print(f"RetroVerse local library UI: http://127.0.0.1:{a.port}/",flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
if __name__=="__main__":main()
