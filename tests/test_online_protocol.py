import unittest
from online.protocol import parse_message, InvalidMessage

class ProtocolTests(unittest.TestCase):
    def test_heartbeat(self):
        self.assertEqual(parse_message(b'{"v":1,"type":"heartbeat"}')["type"],"heartbeat")
    def test_chat(self):
        self.assertEqual(parse_message(b'{"v":1,"type":"chat","room":"public_12","text":"Hi"}')["text"],"Hi")
    def test_rejects_spoofed_identity(self):
        with self.assertRaises(InvalidMessage):
            parse_message(b'{"v":1,"type":"join_room","room":"room_1","is_admin":true}')
    def test_rejects_large_payload(self):
        with self.assertRaises(InvalidMessage):
            parse_message(b"x"*4097)
    def test_rejects_unknown_command(self):
        with self.assertRaises(InvalidMessage):
            parse_message(b'{"v":1,"type":"exec","room":"room_1"}')
    def test_rejects_missing_room(self):
        with self.assertRaises(InvalidMessage):
            parse_message(b'{"v":1,"type":"chat","text":"hello"}')
