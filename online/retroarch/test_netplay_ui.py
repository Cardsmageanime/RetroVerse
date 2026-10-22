"""Test local Netplay UI request safety and command planning."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE=Path(__file__).parent
sys.path.insert(0,str(HERE))
spec=importlib.util.spec_from_file_location("netplay_ui_server",HERE/"netplay_ui_server.py")
ui=importlib.util.module_from_spec(spec)
spec.loader.exec_module(ui)

class NetplayUITests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.core=Path(self.tmp.name)/"test_core.so"
        self.game=Path(self.tmp.name)/"test_game.rom"
        self.core.touch(); self.game.touch()
        self.payload={"mode":"host","core":str(self.core),"content":str(self.game),"retroarch":"retroarch","port":55435}

    def test_host(self):
        self.assertIn("--host",ui.prepare(self.payload))

    def test_join(self):
        p=dict(self.payload,mode="join",peer="127.0.0.1")
        self.assertIn("--connect",ui.prepare(p))

    def test_spectate(self):
        p=dict(self.payload,mode="spectate",peer="127.0.0.1")
        self.assertIn("--spectate",ui.prepare(p))

    def test_no_arbitrary_fields(self):
        with self.assertRaises(ValueError):
            ui.prepare(dict(self.payload,extra="untrusted"))

    def test_no_shell_injection(self):
        with self.assertRaises(ValueError):
            ui.prepare(dict(self.payload,peer="example.org;bad",mode="join"))

    def test_static_files_exist(self):
        self.assertTrue(ui.NEON.is_file())
        self.assertTrue(ui.NETPLAY.is_file())
        self.assertIn("RETROVERSE_SESSION_TOKEN",ui.NETPLAY.read_text())

if __name__=="__main__": unittest.main()
