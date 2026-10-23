import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.request import urlopen
from urllib.error import HTTPError
from http.server import ThreadingHTTPServer
from library_ui_server import Handler
class DrivePickerTests(unittest.TestCase):
 def test_selection_requires_server_allowlist(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);(root/"test.nes").write_bytes(b"demo")
   class LocalHandler(Handler):
    rom_root=None
    allow_selection=True
   srv=ThreadingHTTPServer(("127.0.0.1",0),LocalHandler)
   thread=threading.Thread(target=srv.serve_forever,daemon=True);thread.start()
   base=f"http://127.0.0.1:{srv.server_port}"
   try:
    with patch("library_ui_server.discover_mounts",return_value=[str(root)]):
     with urlopen(base+"/api/drives") as response:
      self.assertEqual(json.load(response)["drives"],[str(root)])
     from urllib.parse import quote
     with urlopen(base+"/api/library?drive="+quote(str(root),safe="")) as response:
      self.assertEqual(json.load(response)["count"],1)
     with self.assertRaises(HTTPError) as e:urlopen(base+"/api/library?drive="+quote(str(root/"other"),safe=""))
     self.assertEqual(e.exception.code,400)
   finally:
    srv.shutdown();srv.server_close();thread.join(timeout=3)
 def test_disabled_picker_does_not_list(self):
  class Locked(Handler):
   rom_root=None
   allow_selection=False
  srv=ThreadingHTTPServer(("127.0.0.1",0),Locked)
  thread=threading.Thread(target=srv.serve_forever,daemon=True);thread.start()
  try:
   with urlopen(f"http://127.0.0.1:{srv.server_port}/api/drives") as response:
    self.assertEqual(json.load(response)["drives"],[])
  finally:
   srv.shutdown();srv.server_close();thread.join(timeout=3)
if __name__=="__main__":unittest.main()
