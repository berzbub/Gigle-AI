"""Tests for gigle_ai.client."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from gigle_ai.client import GeminiClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_client(api_key: str = "fake-key", model: str = GeminiClient.DEFAULT_MODEL) -> GeminiClient:
    """Return a GeminiClient with the genai module mocked out."""
    with patch("gigle_ai.client.genai") as mock_genai:
        mock_genai.Client.return_value = MagicMock()
        client = GeminiClient(api_key=api_key, model=model)
    return client


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


class TestInit:
    def test_requires_api_key(self, monkeypatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        with pytest.raises(ValueError, match="API key"):
            with patch("gigle_ai.client.genai"):
                GeminiClient(api_key=None)

    def test_uses_env_variable(self, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "env-key")
        with patch("gigle_ai.client.genai") as mock_genai:
            mock_genai.Client.return_value = MagicMock()
            client = GeminiClient()
        assert client.model_name == GeminiClient.DEFAULT_MODEL

    def test_custom_model(self):
        client = _make_client(model="gemini-2.0-pro")
        assert client.model_name == "gemini-2.0-pro"


# ---------------------------------------------------------------------------
# One-shot generation
# ---------------------------------------------------------------------------


class TestGenerate:
    def test_returns_response_text(self):
        client = _make_client()
        mock_response = MagicMock()
        mock_response.text = "Hello, world!"
        client._client.models.generate_content.return_value = mock_response

        result = client.generate("Say hello")
        assert result == "Hello, world!"
        client._client.models.generate_content.assert_called_once_with(
            model=GeminiClient.DEFAULT_MODEL,
            contents="Say hello",
        )

    def test_raises_on_empty_prompt(self):
        client = _make_client()
        with pytest.raises(ValueError, match="empty"):
            client.generate("")

    def test_raises_on_whitespace_prompt(self):
        client = _make_client()
        with pytest.raises(ValueError, match="empty"):
            client.generate("   ")


# ---------------------------------------------------------------------------
# Streaming
# ---------------------------------------------------------------------------


class TestStream:
    def test_yields_chunks(self):
        client = _make_client()
        chunks = [MagicMock(text="Hello"), MagicMock(text=", "), MagicMock(text="world!")]
        client._client.models.generate_content_stream.return_value = iter(chunks)

        result = list(client.stream("Say hello"))
        assert result == ["Hello", ", ", "world!"]

    def test_raises_on_empty_prompt(self):
        client = _make_client()
        with pytest.raises(ValueError, match="empty"):
            list(client.stream(""))


# ---------------------------------------------------------------------------
# Multi-turn chat
# ---------------------------------------------------------------------------


class TestChat:
    def test_chat_returns_text(self):
        client = _make_client()
        mock_chat = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Nice to meet you!"
        mock_chat.send_message.return_value = mock_response
        client._client.chats.create.return_value = mock_chat

        result = client.chat("Hi there!")
        assert result == "Nice to meet you!"

    def test_chat_auto_starts_session(self):
        client = _make_client()
        mock_chat = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Auto-started"
        mock_chat.send_message.return_value = mock_response
        client._client.chats.create.return_value = mock_chat

        assert client._chat is None
        client.chat("Hello")
        assert client._chat is mock_chat

    def test_raises_on_empty_message(self):
        client = _make_client()
        with pytest.raises(ValueError, match="empty"):
            client.chat("")

    def test_reset_chat_clears_history(self):
        client = _make_client()
        mock_chat = MagicMock()
        client._client.chats.create.return_value = mock_chat
        client.start_chat()
        assert client._chat is mock_chat

        new_mock_chat = MagicMock()
        client._client.chats.create.return_value = new_mock_chat
        client.reset_chat()
        assert client._chat is new_mock_chat

