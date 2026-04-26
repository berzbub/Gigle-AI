"""Tests for the MultimodalAI engine."""

import base64
import unittest

from gigle_ai.ai.multimodal import MultimodalAI


class TestMultimodalAIText(unittest.TestCase):
    """Tests for text analysis."""

    def setUp(self) -> None:
        self.ai = MultimodalAI()

    def test_positive_sentiment(self) -> None:
        result = self.ai.analyze_text("This is a great and wonderful experience!")
        self.assertEqual(result["sentiment"], "positive")

    def test_negative_sentiment(self) -> None:
        result = self.ai.analyze_text("This is the worst and most terrible thing ever.")
        self.assertEqual(result["sentiment"], "negative")

    def test_neutral_sentiment(self) -> None:
        result = self.ai.analyze_text("The car drives down the road at noon.")
        self.assertEqual(result["sentiment"], "neutral")

    def test_word_count(self) -> None:
        result = self.ai.analyze_text("one two three four five")
        self.assertEqual(result["word_count"], 5)

    def test_is_question_true(self) -> None:
        result = self.ai.analyze_text("What time is it?")
        self.assertTrue(result["is_question"])

    def test_is_question_false(self) -> None:
        result = self.ai.analyze_text("The sky is blue today.")
        self.assertFalse(result["is_question"])

    def test_summary_capped_at_120_chars(self) -> None:
        long_text = "A" * 200 + ". Second sentence."
        result = self.ai.analyze_text(long_text)
        self.assertLessEqual(len(result["summary"]), 121)  # 120 + ellipsis char

    def test_language_hint_english(self) -> None:
        result = self.ai.analyze_text("Hello, how are you doing today?")
        self.assertEqual(result["language_hint"], "en")

    def test_empty_text_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.ai.analyze_text("")

    def test_whitespace_only_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.ai.analyze_text("   ")

    def test_non_string_raises(self) -> None:
        with self.assertRaises((ValueError, AttributeError)):
            self.ai.analyze_text(None)  # type: ignore[arg-type]


class TestMultimodalAIImage(unittest.TestCase):
    """Tests for image description."""

    def setUp(self) -> None:
        self.ai = MultimodalAI()

    def _b64(self, raw: bytes) -> str:
        return base64.b64encode(raw).decode()

    def test_jpeg_format_detected(self) -> None:
        fake_jpeg = self._b64(b"\xff\xd8" + b"\x00" * 18)
        result = self.ai.describe_image(fake_jpeg)
        self.assertEqual(result["format_hint"], "jpeg")

    def test_png_format_detected(self) -> None:
        fake_png = self._b64(b"\x89PNG\r\n\x1a\n" + b"\x00" * 12)
        result = self.ai.describe_image(fake_png)
        self.assertEqual(result["format_hint"], "png")

    def test_gif_format_detected(self) -> None:
        fake_gif = self._b64(b"GIF89a" + b"\x00" * 14)
        result = self.ai.describe_image(fake_gif)
        self.assertEqual(result["format_hint"], "gif")

    def test_unknown_format(self) -> None:
        fake_data = self._b64(b"\x00\x01\x02\x03" * 5)
        result = self.ai.describe_image(fake_data)
        self.assertEqual(result["format_hint"], "unknown")

    def test_size_bytes_correct(self) -> None:
        raw = b"\xff\xd8" + b"X" * 48
        result = self.ai.describe_image(self._b64(raw))
        self.assertEqual(result["size_bytes"], len(raw))

    def test_description_present(self) -> None:
        result = self.ai.describe_image(self._b64(b"\xff\xd8" + b"\x00" * 10))
        self.assertIn("description", result)
        self.assertIsInstance(result["description"], str)

    def test_invalid_base64_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.ai.describe_image("not-valid-base64!!!")

    def test_empty_string_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.ai.describe_image("")


class TestMultimodalAIChat(unittest.TestCase):
    """Tests for the chat / conversation feature."""

    def setUp(self) -> None:
        self.ai = MultimodalAI()

    def test_greeting_response(self) -> None:
        result = self.ai.chat("Hello!")
        self.assertIn("reply", result)
        self.assertIn("Gigle-AI", result["reply"])

    def test_farewell_response(self) -> None:
        result = self.ai.chat("Goodbye!")
        self.assertIn("Goodbye", result["reply"])

    def test_thanks_response(self) -> None:
        result = self.ai.chat("Thanks a lot!")
        self.assertIn("welcome", result["reply"].lower())

    def test_name_query(self) -> None:
        result = self.ai.chat("What is your name?")
        self.assertIn("Gigle-AI", result["reply"])

    def test_capabilities_query(self) -> None:
        result = self.ai.chat("What are your capabilities?")
        reply_lower = result["reply"].lower()
        self.assertIn("text", reply_lower)
        self.assertIn("image", reply_lower)

    def test_history_grows(self) -> None:
        result = self.ai.chat("Hello!", history=[])
        self.assertEqual(len(result["history"]), 2)
        result2 = self.ai.chat("And you?", history=result["history"])
        self.assertEqual(len(result2["history"]), 4)

    def test_question_reply(self) -> None:
        result = self.ai.chat("Why is the sky blue?")
        self.assertIn("question", result["reply"].lower())

    def test_empty_message_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.ai.chat("")

    def test_none_history_defaults_to_empty(self) -> None:
        result = self.ai.chat("Hi", history=None)
        self.assertIsInstance(result["history"], list)


if __name__ == "__main__":
    unittest.main()
