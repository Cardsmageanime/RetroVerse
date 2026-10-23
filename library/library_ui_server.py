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

REPO=Path(__file__).resolve().parents[1]
class Handler(SimpleHTTPRequestHandler):
    rom_root=None
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(REPO),**kwargs)
    def do_GET(self):
        path=urlsplit(self.path).path
        if path=="/api/library":
            try:
                games,limited=discover(self.rom_root) if self.rom_root else ([],False)
                data={"format":"retroverse-library-v1","games":games,"count":len(games),"truncated":limited,"configured":bool(self.rom_root)}
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
    def log_message(self,*args):
        pass

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rom-root",type=Path,required=True,help="Explicit mounted ROM directory; never auto-detect internal storage")
    p.add_argument("--port",type=int,default=8769)
    a=p.parse_args()
    if not 1024<=a.port<=65535:p.error("Invalid port")
    root=a.rom_root.resolve(strict=True)
    if not root.is_dir():p.error("ROM root must be a directory")
    class LocalHandler(Handler):rom_root=root
    server=ThreadingHTTPServer(("127.0.0.1",a.port),LocalHandler)
    print(f"RetroVerse local library UI: http://127.0.0.1:{a.port}/",flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
if __name__=="__main__":main()
