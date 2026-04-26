"""
Multimodal AI Engine
====================
Core AI processing for Gigle-AI.  Handles text analysis, basic image
description, and multi-turn chat without requiring any heavy external
dependencies – making it easy to run on resource-constrained devices.

External AI back-ends (e.g. OpenAI, local GGUF models) can be plugged in
by sub-classing :class:`MultimodalAI` and overriding the relevant methods.
"""

from __future__ import annotations

import base64
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Simple keyword sets used by the built-in rule-based engine
# ---------------------------------------------------------------------------

_POSITIVE_WORDS = frozenset(
    ["good", "great", "excellent", "amazing", "wonderful", "fantastic",
     "happy", "love", "best", "awesome", "positive", "nice", "beautiful"]
)
_NEGATIVE_WORDS = frozenset(
    ["bad", "terrible", "awful", "horrible", "worst", "hate", "poor",
     "negative", "ugly", "disgusting", "dreadful", "failure"]
)

_GREETING_PATTERNS = re.compile(
    r"\b(hi|hello|hey|greetings|howdy|good\s+(morning|afternoon|evening))\b",
    re.IGNORECASE,
)
_QUESTION_PATTERNS = re.compile(r"\?")


class MultimodalAI:
    """
    Multimodal AI engine that processes text and images.

    Parameters
    ----------
    model_name:
        Identifier for the underlying model.  Currently only
        ``"builtin"`` (the default rule-based engine) is supported;
        future releases will support GGUF / API-backed models.
    """

    def __init__(self, model_name: str = "builtin") -> None:
        self.model_name = model_name
        logger.debug("MultimodalAI initialised with model '%s'", model_name)

    # ------------------------------------------------------------------
    # Text analysis
    # ------------------------------------------------------------------

    def analyze_text(self, text: str) -> dict[str, Any]:
        """
        Analyze *text* and return a structured result.

        Returns
        -------
        dict with keys:

        * ``summary`` – first sentence / short summary.
        * ``sentiment`` – ``"positive"``, ``"negative"``, or ``"neutral"``.
        * ``word_count`` – number of words.
        * ``is_question`` – whether the text appears to be a question.
        * ``language_hint`` – best-effort detected language tag.
        """
        if not isinstance(text, str) or not text.strip():
            raise ValueError("text must be a non-empty string")

        words = text.split()
        word_count = len(words)

        # Sentiment
        lower_words = {w.strip(".,!?;:\"'").lower() for w in words}
        pos_hits = len(lower_words & _POSITIVE_WORDS)
        neg_hits = len(lower_words & _NEGATIVE_WORDS)
        if pos_hits > neg_hits:
            sentiment = "positive"
        elif neg_hits > pos_hits:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        # Summary (first sentence, capped at 120 chars)
        first_sentence = re.split(r"[.!?]", text.strip())[0].strip()
        summary = first_sentence[:120] + ("…" if len(first_sentence) > 120 else "")

        # Question detection
        is_question = bool(_QUESTION_PATTERNS.search(text))

        # Language hint (very naive: assumes English unless non-ASCII > 20 %)
        non_ascii = sum(1 for c in text if ord(c) > 127)
        language_hint = "en" if non_ascii / max(len(text), 1) < 0.2 else "unknown"

        return {
            "summary": summary,
            "sentiment": sentiment,
            "word_count": word_count,
            "is_question": is_question,
            "language_hint": language_hint,
        }

    # ------------------------------------------------------------------
    # Image description
    # ------------------------------------------------------------------

    def describe_image(self, image_data: str) -> dict[str, Any]:
        """
        Describe the content of an image provided as a base64-encoded string.

        The built-in engine extracts basic metadata (size, format guess) and
        returns a placeholder description.  Sub-classes may override this
        method to call vision models.

        Parameters
        ----------
        image_data:
            Base64-encoded image bytes.

        Returns
        -------
        dict with keys ``description``, ``format_hint``, ``size_bytes``.
        """
        if not isinstance(image_data, str) or not image_data.strip():
            raise ValueError("image_data must be a non-empty base64 string")

        # Validate base64 and measure size
        try:
            raw = base64.b64decode(image_data, validate=True)
        except Exception as exc:
            raise ValueError("image_data is not valid base64") from exc

        size_bytes = len(raw)

        # Guess format from magic bytes
        format_hint = "unknown"
        if raw[:2] == b"\xff\xd8":
            format_hint = "jpeg"
        elif raw[:8] == b"\x89PNG\r\n\x1a\n":
            format_hint = "png"
        elif raw[:6] in (b"GIF87a", b"GIF89a"):
            format_hint = "gif"
        elif raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
            format_hint = "webp"
        elif raw[:4] in (b"\x00\x00\x00\x18", b"\x00\x00\x00\x1c"):
            format_hint = "mp4/mov"

        description = (
            f"Image received ({size_bytes} bytes, format: {format_hint}). "
            "Detailed vision analysis requires a vision-capable model."
        )

        return {
            "description": description,
            "format_hint": format_hint,
            "size_bytes": size_bytes,
        }

    # ------------------------------------------------------------------
    # Chat
    # ------------------------------------------------------------------

    def chat(
        self,
        message: str,
        history: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        """
        Generate a reply to *message* given the conversation *history*.

        Parameters
        ----------
        message:
            Latest user message.
        history:
            List of previous turns: ``[{"role": "user"|"assistant", "content": "..."}]``.

        Returns
        -------
        dict with keys ``reply`` (the assistant's response) and
        ``history`` (updated conversation history).
        """
        if not isinstance(message, str) or not message.strip():
            raise ValueError("message must be a non-empty string")

        history = list(history or [])

        # Produce a context-aware reply using simple heuristics
        reply = self._generate_reply(message, history)

        # Append this turn to history
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": reply})

        return {"reply": reply, "history": history}

    # ------------------------------------------------------------------
    # Internal reply generation (rule-based fallback)
    # ------------------------------------------------------------------

    def _generate_reply(
        self,
        message: str,
        history: list[dict[str, str]],
    ) -> str:
        msg_lower = message.lower().strip()

        if _GREETING_PATTERNS.search(msg_lower):
            return "Hello! I'm Gigle-AI. How can I assist you today?"

        if any(word in msg_lower for word in ("bye", "goodbye", "see you", "farewell")):
            return "Goodbye! Feel free to come back anytime."

        if any(word in msg_lower for word in ("thank", "thanks", "thx")):
            return "You're welcome! Is there anything else I can help with?"

        if "your name" in msg_lower or "who are you" in msg_lower:
            return (
                "I'm Gigle-AI, a multimodal AI assistant designed to work "
                "across multiple devices on your network."
            )

        if "what can you do" in msg_lower or "capabilities" in msg_lower:
            return (
                "I can analyze text (sentiment, summary, language), "
                "describe images, and hold multi-turn conversations – "
                "all accessible from any device on your network."
            )

        # Analyze the message and craft a reply
        analysis = self.analyze_text(message)
        if analysis["is_question"]:
            return (
                f"That's an interesting question. "
                f"(Detected sentiment: {analysis['sentiment']}, "
                f"{analysis['word_count']} words.) "
                "A more advanced model would provide a detailed answer."
            )

        return (
            f"I received your message ({analysis['word_count']} words, "
            f"sentiment: {analysis['sentiment']}). "
            "Connect a capable language model for richer responses."
        )
