"""HTTP integration tests of the real loopback Netplay controller.

Uses actual localhost HTTP requests and a mocked RetroArch subprocess;
no emulator, ROM, core, or gameplay server required.
"""
import http.client
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from netplay_ui_server import handler_factory
from http.server import ThreadingHTTPServer


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.token = "test-token-keep-local"
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), handler_factory(cls.token, 0))
        cls.port = cls.server.server_port
        # Factory must know the actual random ephemeral port.
        cls.server.RequestHandlerClass = handler_factory(cls.token, cls.port)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join(timeout=5)
        cls.server.server_close()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        core = Path(self.temp.name) / "test_core.so"
        content = Path(self.temp.name) / "test_game.rom"
        core.touch()
        content.touch()
        self.payload = {"mode": "host", "core": str(core), "content": str(content),
                        "retroarch": "retroarch", "port": 55435}

    def request(self, path, obj=None, method="POST", token=None, host=None, origin=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        data = json.dumps(obj).encode() if obj is not None else None
        headers = {"Host": host or f"127.0.0.1:{self.port}"}
        if data is not None:
            headers["Content-Type"] = "application/json"
        if token is not None:
            headers["X-RetroVerse-Token"] = token
        if origin is not None:
            headers["Origin"] = origin
        connection.request(method, path, body=data, headers=headers)
        response = connection.getresponse()
        result = response.read()
        code = response.status
        connection.close()
        return code, result

    def test_menu_routes_and_session_token(self):
        code, body = self.request("/", method="GET")
        self.assertEqual(code, 200)
        self.assertIn(b"RETROVERSE", body.upper())
        code, body = self.request("/netplay", method="GET")
        self.assertEqual(code, 200)
        self.assertIn(self.token.encode(), body)
        self.assertIn(b'Host', body)
        self.assertIn(b'Spectate', body)

    def test_preview_does_not_launch(self):
        with patch("netplay_ui_server.subprocess.Popen") as popen:
            status, body = self.request("/api/netplay/preview", self.payload, token=self.token)
            self.assertEqual(status, 200, body)
            self.assertIn("--host", json.loads(body)["command"])
            popen.assert_not_called()

    def test_launch_reaches_subprocess_without_shell(self):
        with patch("netplay_ui_server.subprocess.Popen") as popen:
            popen.return_value.pid = 741
            status, body = self.request("/api/netplay/launch", self.payload, token=self.token)
            self.assertEqual(status, 200, body)
            self.assertEqual(json.loads(body)["pid"], 741)
            args = popen.call_args.args[0]
            self.assertIsInstance(args, list)
            self.assertIn("--host", args)

    def test_missing_token_rejected(self):
        status, body = self.request("/api/netplay/launch", self.payload)
        self.assertEqual(status, 403)

    def test_wrong_origin_rejected(self):
        status, body = self.request("/api/netplay/launch", self.payload,
                                    token=self.token, origin="https://untrusted.example")
        self.assertEqual(status, 403)

    def test_wrong_host_rejected(self):
        status, body = self.request("/api/netplay/launch", self.payload,
                                    token=self.token, host="untrusted.example")
        self.assertEqual(status, 403)

    def test_invalid_game_rejected(self):
        self.payload["content"] = "/missing-game.rom"
        status, body = self.request("/api/netplay/preview", self.payload, token=self.token)
        self.assertEqual(status, 400)

    def test_does_not_serve_arbitrary_files(self):
        status, body = self.request("/../../README.md", method="GET")
        self.assertEqual(status, 404)

if __name__ == "__main__":
    unittest.main()
