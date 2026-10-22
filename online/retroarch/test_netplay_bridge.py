"""Tests for RetroArch command construction. No emulator or copyrighted games required."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
spec = importlib.util.spec_from_file_location("netplay_bridge",Path(__file__).with_name("netplay_bridge.py"))
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)

class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.core=Path(self.tmp.name)/"core.so"
        self.game=Path(self.tmp.name)/"test.rom"
        self.core.touch()
        self.game.touch()
    def build(self,mode,**kwargs):
        return bridge.build_command(mode,"retroarch",self.core,self.game,**kwargs)
    def test_host(self):
        cmd=self.build("host")
        self.assertIn("--host",cmd)
        self.assertIn("-L",cmd)
        self.assertEqual(cmd[-1],str(self.game.resolve()))
        self.assertNotIn("--connect",cmd)
    def test_join(self):
        cmd=self.build("join",peer="192.168.1.50",nick="RetroPlayer")
        self.assertEqual(cmd[cmd.index("--connect")+1],"192.168.1.50")
        self.assertEqual(cmd[cmd.index("--nick")+1],"RetroPlayer")
    def test_spectate(self):
        self.assertIn("--spectate",self.build("spectate",peer="gamebox.local"))
    def test_invalid_peer(self):
        for peer in ("https://example.com","host;echo","a b","user@host"):
            with self.subTest(peer=peer),self.assertRaises(ValueError):
                self.build("join",peer=peer)
    def test_invalid_content(self):
        with self.assertRaises(ValueError):
            bridge.build_command("host","retroarch",self.core,Path(self.tmp.name)/"absent")
    def test_requires_peer(self):
        with self.assertRaises(ValueError):
            self.build("join")
    def test_no_shell_execution(self):
        with patch.object(bridge.subprocess,"call",return_value=0) as call,patch.object(bridge.shutil,"which",return_value="/usr/bin/retroarch"):
            result=bridge.main(["host","--core",str(self.core),"--content",str(self.game)])
            self.assertEqual(result,0)
            self.assertIsInstance(call.call_args.args[0],list)
    def test_dry_run(self):
        with patch.object(bridge.subprocess,"call") as call:
            self.assertEqual(bridge.main(["host","--core",str(self.core),"--content",str(self.game),"--dry-run"]),0)
            call.assert_not_called()

if __name__=="__main__":unittest.main()
