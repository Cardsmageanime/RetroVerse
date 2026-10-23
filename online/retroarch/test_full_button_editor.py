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
    def test_analog_axes_two_players(self):
        players=[{"joypad_index":0,"axes":{"l_x":0,"l_y":1,"r_x":2,"r_y":3}},
                 {"joypad_index":1,"axes":{"l_x":3,"l_y":2,"r_x":1,"r_y":0}}]
        cfg=generate(players)
        self.assertIn('input_player1_l_x_plus_axis = "+0"',cfg)
        self.assertIn('input_player1_l_x_minus_axis = "-0"',cfg)
        self.assertIn('input_player2_r_y_plus_axis = "+0"',cfg)
        self.assertIn('input_player2_r_y_minus_axis = "-0"',cfg)
    def test_analog_validation(self):
        players=[{"joypad_index":0,"axes":{"l_x":0,"l_y":0}},
                 {"joypad_index":1,"axes":{"l_x":2}}]
        with self.assertRaises(ValueError):generate(players)
        players[0]["axes"]={"l_x":32}
        with self.assertRaises(ValueError):generate(players)
if __name__=="__main__":unittest.main()
