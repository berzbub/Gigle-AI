"""Tests for Gigle-AI utility helpers."""

import base64
import unittest
from pathlib import Path

from gigle_ai.utils.helpers import encode_image, decode_image, build_response


class TestEncodeImage(unittest.TestCase):

    def test_encode_bytes(self) -> None:
        raw = b"\xff\xd8\x00\x01"
        result = encode_image(raw)
        self.assertEqual(result, base64.b64encode(raw).decode())

    def test_encode_bytearray(self) -> None:
        raw = bytearray(b"\x89PNG\r\n\x1a\n")
        result = encode_image(raw)
        self.assertEqual(result, base64.b64encode(raw).decode())

    def test_encode_nonexistent_path_returns_as_is(self) -> None:
        fake_b64 = base64.b64encode(b"fake").decode()
        result = encode_image(fake_b64)
        self.assertEqual(result, fake_b64)

    def test_encode_path_object_reads_file(self) -> None:
        import tempfile, os
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"\xff\xd8\x00")
            name = f.name
        try:
            result = encode_image(Path(name))
            self.assertEqual(result, base64.b64encode(b"\xff\xd8\x00").decode())
        finally:
            os.unlink(name)


class TestDecodeImage(unittest.TestCase):

    def test_decode_valid(self) -> None:
        raw = b"\xff\xd8\x00\x01"
        encoded = base64.b64encode(raw).decode()
        self.assertEqual(decode_image(encoded), raw)

    def test_decode_invalid_raises(self) -> None:
        with self.assertRaises(ValueError):
            decode_image("not-valid!!!")


class TestBuildResponse(unittest.TestCase):

    def test_text_response(self) -> None:
        result = build_response("text", {"summary": "test"})
        self.assertEqual(result["type"], "text")
        self.assertEqual(result["result"]["summary"], "test")

    def test_image_response(self) -> None:
        result = build_response("image", {"description": "a dog"})
        self.assertEqual(result["type"], "image")

    def test_chat_response(self) -> None:
        result = build_response("chat", {"reply": "hi", "history": []})
        self.assertEqual(result["type"], "chat")
        self.assertEqual(result["result"]["reply"], "hi")


if __name__ == "__main__":
    unittest.main()
