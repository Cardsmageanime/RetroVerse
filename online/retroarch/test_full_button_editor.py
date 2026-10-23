"""Check complete two-player button bindings are accepted by RetroArch overlay."""
import unittest
from controller_config import BUTTONS, DEFAULTS, generate
class FullEditorTests(unittest.TestCase):
    def test_all_sixteen_for_two_players(self):
        players=[{"joypad_index":0,"buttons":dict(DEFAULTS)},{"joypad_index":1,"buttons":dict(DEFAULTS)}]
        result=generate(players)
        for player in (1,2):
            for name in BUTTONS:
                self.assertIn(f'input_player{player}_{name}_btn = "{DEFAULTS[name]}"',result)
    def test_button_out_of_range_rejected(self):
        players=[{"joypad_index":0,"buttons":dict(DEFAULTS)},{"joypad_index":1,"buttons":dict(DEFAULTS)}]
        players[1]["buttons"]["r3"]=64
        with self.assertRaises(ValueError):generate(players)
if __name__=="__main__":unittest.main()
