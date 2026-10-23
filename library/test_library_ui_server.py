import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.request import urlopen
from http.server import ThreadingHTTPServer
from library_ui_server import Handler

class ServiceTests(unittest.TestCase):
 def test_local_library_endpoint(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);(root/"demo.nes").write_bytes(b"test")
   class LocalHandler(Handler):rom_root=root
   server=ThreadingHTTPServer(("127.0.0.1",0),LocalHandler)
   worker=threading.Thread(target=server.serve_forever,daemon=True)
   worker.start()
   try:
    with urlopen(f"http://127.0.0.1:{server.server_port}/api/library") as response:
     result=json.load(response)
    self.assertEqual(result["count"],1)
    self.assertEqual(result["games"][0]["system"],"NES")
    self.assertEqual(result["games"][0]["title"],"demo")
    self.assertTrue(result["configured"])
   finally:
    server.shutdown();server.server_close();worker.join(timeout=3)
if __name__=="__main__":unittest.main()
