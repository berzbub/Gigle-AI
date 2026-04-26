"""Tests for the Network AI server and client."""

import base64
import json
import threading
import unittest

from gigle_ai.network.server import NetworkAIServer
from gigle_ai.network.client import NetworkAIClient, NetworkAIError
from gigle_ai.ai.multimodal import MultimodalAI


def _free_port() -> int:
    """Return an available TCP port on localhost."""
    import socket
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class TestNetworkAIServerClient(unittest.TestCase):
    """Integration tests: server + client communicating over localhost."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.port = _free_port()
        cls.server = NetworkAIServer(host="127.0.0.1", port=cls.port)
        cls.server.run(threaded=True)
        cls.client = NetworkAIClient(f"http://127.0.0.1:{cls.port}")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.stop()

    # ------------------------------------------------------------------
    # GET endpoints
    # ------------------------------------------------------------------

    def test_health_returns_ok(self) -> None:
        resp = self.client.health()
        self.assertEqual(resp["status"], "ok")

    def test_info_contains_capabilities(self) -> None:
        resp = self.client.info()
        self.assertIn("capabilities", resp)
        self.assertIn("text", resp["capabilities"])
        self.assertIn("image", resp["capabilities"])
        self.assertIn("chat", resp["capabilities"])

    # ------------------------------------------------------------------
    # POST /analyze/text
    # ------------------------------------------------------------------

    def test_analyze_text_returns_result(self) -> None:
        resp = self.client.analyze_text("This is a great product!")
        self.assertEqual(resp["type"], "text")
        result = resp["result"]
        self.assertIn("sentiment", result)
        self.assertEqual(result["sentiment"], "positive")
        self.assertIn("word_count", result)
        self.assertEqual(result["word_count"], 5)

    def test_analyze_text_missing_field_returns_400(self) -> None:
        # The client validates before sending; empty text raises ValueError.
        with self.assertRaises((NetworkAIError, ValueError)):
            self.client.analyze_text("")

    # ------------------------------------------------------------------
    # POST /analyze/image
    # ------------------------------------------------------------------

    def test_analyze_image_returns_result(self) -> None:
        # Create a minimal valid JPEG magic bytes payload
        fake_jpeg = b"\xff\xd8" + b"\x00" * 18
        resp = self.client.analyze_image(fake_jpeg)
        self.assertEqual(resp["type"], "image")
        result = resp["result"]
        self.assertEqual(result["format_hint"], "jpeg")
        self.assertIn("description", result)

    def test_analyze_image_missing_field_returns_400(self) -> None:
        with self.assertRaises(NetworkAIError) as ctx:
            self.client.analyze_image(b"")
        self.assertIn("400", str(ctx.exception))

    # ------------------------------------------------------------------
    # POST /chat
    # ------------------------------------------------------------------

    def test_chat_returns_reply_and_history(self) -> None:
        resp = self.client.chat("Hello!")
        self.assertEqual(resp["type"], "chat")
        result = resp["result"]
        self.assertIn("reply", result)
        self.assertIn("history", result)
        self.assertTrue(len(result["history"]) >= 2)

    def test_chat_missing_message_returns_400(self) -> None:
        # The client validates before sending; empty message raises ValueError.
        with self.assertRaises((NetworkAIError, ValueError)):
            self.client.chat("")

    def test_chat_with_history(self) -> None:
        history = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello! How can I help?"},
        ]
        resp = self.client.chat("What can you do?", history=history)
        self.assertEqual(resp["type"], "chat")
        result = resp["result"]
        reply_lower = result["reply"].lower()
        # The AI describes its abilities (text, image, chat/conversations)
        self.assertTrue(
            any(word in reply_lower for word in ("text", "image", "analyze", "network", "device")),
            f"Expected ability description in reply, got: {result['reply']}",
        )
        # History should grow by 2 turns
        self.assertEqual(len(result["history"]), len(history) + 2)

    # ------------------------------------------------------------------
    # Unknown routes
    # ------------------------------------------------------------------

    def test_unknown_get_returns_404(self) -> None:
        import urllib.request
        import urllib.error
        url = f"http://127.0.0.1:{self.port}/does/not/exist"
        req = urllib.request.Request(url)
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req)
        self.assertEqual(ctx.exception.code, 404)


class TestNetworkAIClientValidation(unittest.TestCase):
    """Unit tests for NetworkAIClient input validation (no server needed)."""

    def setUp(self) -> None:
        self.client = NetworkAIClient("http://127.0.0.1:1")  # port 1 is never open

    def test_analyze_text_empty_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.client.analyze_text("")

    def test_chat_empty_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.client.chat("")

    def test_analyze_image_bytes_encodes(self) -> None:
        # Should raise NetworkAIError (connection refused), NOT ValueError
        with self.assertRaises(NetworkAIError):
            self.client.analyze_image(b"\xff\xd8\x00")

    def test_analyze_image_path_not_found_assumes_b64(self) -> None:
        # Non-existent path string → treated as b64 string → connection error
        with self.assertRaises(NetworkAIError):
            self.client.analyze_image("/nonexistent/image.jpg")


if __name__ == "__main__":
    unittest.main()
