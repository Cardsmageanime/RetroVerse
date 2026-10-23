"""Pure unit tests for RetroArch two-player binding snippets."""
import unittest
from controller_config import generate, DEFAULTS

class ControllerExportTests(unittest.TestCase):
    def setUp(self):
        self.players=[{"joypad_index":0,"buttons":dict(DEFAULTS)},{"joypad_index":1,"buttons":dict(DEFAULTS)}]
    def test_two_player_separation(self):
        text=generate(self.players)
        self.assertIn('input_player1_joypad_index = "0"',text)
        self.assertIn('input_player2_joypad_index = "1"',text)
        self.assertIn('input_player1_a_btn = "1"',text)
        self.assertIn('input_player2_up_btn = "12"',text)
    def test_same_device_rejected(self):
        self.players[1]["joypad_index"]=0
        with self.assertRaises(ValueError):generate(self.players)
    def test_invalid_button_rejected(self):
        self.players[0]["buttons"]["a"]="1\nconfig_save_on_exit = true"
        with self.assertRaises(ValueError):generate(self.players)
    def test_unknown_key_rejected(self):
        self.players[0]["buttons"]["shell"]=42
        with self.assertRaises(ValueError):generate(self.players)
    def test_requires_two_players(self):
        with self.assertRaises(ValueError):generate(self.players[:1])
    def test_no_unrequested_defaults(self):
        self.players[0]["buttons"]={"a":0}
        text=generate(self.players)
        self.assertNotIn("input_player1_b_btn",text)
if __name__=="__main__":unittest.main()
