"""No-game/no-network test coverage for the read-only netplay preflight."""
import hashlib
from pathlib import Path
import socket
import tempfile
import threading
import unittest
from unittest.mock import patch

from netplay_preflight import sha256_file, check_peer, report

class PreflightTests(unittest.TestCase):
    def test_identical_files_have_identical_fingerprint(self):
        with tempfile.TemporaryDirectory() as d:
            a=Path(d)/"test1.rom"; b=Path(d)/"test2.rom"
            a.write_bytes(b"test-fixture-not-a-game")
            b.write_bytes(a.read_bytes())
            self.assertEqual(sha256_file(a),sha256_file(b))
            self.assertEqual(sha256_file(a),hashlib.sha256(a.read_bytes()).hexdigest())
            b.write_bytes(b"mismatched-fixture")
            self.assertNotEqual(sha256_file(a),sha256_file(b))

    def test_reachability_when_tcp_listener_exists(self):
        listener=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.addCleanup(listener.close)
        listener.bind(("127.0.0.1",0));listener.listen(1)
        result=check_peer("127.0.0.1",listener.getsockname()[1])
        self.assertTrue(result["reachable"])

    def test_connection_failure_is_reported_not_crash(self):
        with patch("netplay_preflight.socket.create_connection",side_effect=ConnectionRefusedError()):
            result=check_peer("127.0.0.1",55435)
        self.assertFalse(result["reachable"])

    def test_invalid_port(self):
        with self.assertRaises(ValueError):
            check_peer("127.0.0.1",70000)

    def test_missing_file(self):
        with self.assertRaises(ValueError):
            sha256_file("/nonexistent-retroverse-test-file")

    def test_report_never_includes_file_data(self):
        with tempfile.TemporaryDirectory() as d:
            core=Path(d)/"core.so";game=Path(d)/"test.rom"
            core.write_bytes(b"local-core-fixture")
            game.write_bytes(b"fake-content-fixture")
            result=report(core,game)
            self.assertEqual(result["peer_test"],None)
            self.assertEqual(result["content_file"],"test.rom")
            self.assertEqual(len(result["content_sha256"]),64)

if __name__=="__main__":unittest.main()
