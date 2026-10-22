"""Checks for actual movement, scoring, snapshot and input validation."""
import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location("pong_engine",Path(__file__).with_name("pong_engine.py"))
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class GameplayTests(unittest.TestCase):
    def test_input_moves_paddle_and_stays_bounded(self):
        game=mod.Match()
        start=game.paddles[0]
        game.input(0,-1)
        game.step()
        self.assertLess(game.paddles[0],start)
        for _ in range(200):game.step()
        self.assertGreaterEqual(game.paddles[0],mod.PADDLE_H/2)
    def test_invalid_controls_rejected(self):
        game=mod.Match()
        with self.assertRaises(ValueError):game.input(9,1)
        with self.assertRaises(ValueError):game.input(0,20)
    def test_score_and_reset(self):
        game=mod.Match()
        game.ball_x=-20
        game.step()
        self.assertEqual(game.scores,[0,1])
        self.assertEqual(game.ball_x,mod.WIDTH/2)
    def test_snapshot_updates(self):
        game=mod.Match()
        before=game.state()
        game.step()
        after=game.state()
        self.assertEqual(after["tick"],before["tick"]+1)
        self.assertNotEqual(after["ball"],before["ball"])

if __name__=="__main__":unittest.main()
