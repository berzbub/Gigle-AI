"""GeminiClient — a thin wrapper around the Google GenAI SDK."""

from __future__ import annotations

import os
from typing import Iterator, Optional

from google import genai


class GeminiClient:
    """A simple client for interacting with Google Gemini models.

    Parameters
    ----------
    api_key:
        Your Google AI API key.  When omitted the value of the
        ``GEMINI_API_KEY`` environment variable is used.
    model:
        Gemini model name to use (default: ``"gemini-2.0-flash"``).
    """

    DEFAULT_MODEL = "gemini-2.0-flash"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
    ) -> None:
        resolved_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not resolved_key:
            raise ValueError(
                "A Gemini API key is required.  Pass api_key= or set the "
                "GEMINI_API_KEY environment variable."
            )
        self._client = genai.Client(api_key=resolved_key)
        self._model_name = model
        self._chat = None

    # ------------------------------------------------------------------
    # One-shot generation
    # ------------------------------------------------------------------

    def generate(self, prompt: str) -> str:
        """Send a one-shot prompt and return the response text.

        Parameters
        ----------
        prompt:
            The text prompt to send to the model.

        Returns
        -------
        str
            The model's response text.
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt must not be empty.")
        response = self._client.models.generate_content(
            model=self._model_name,
            contents=prompt,
        )
        return response.text

    def stream(self, prompt: str) -> Iterator[str]:
        """Stream the response for a one-shot prompt, yielding text chunks.

        Parameters
        ----------
        prompt:
            The text prompt to send to the model.

        Yields
        ------
        str
            Successive text chunks from the model response.
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt must not be empty.")
        for chunk in self._client.models.generate_content_stream(
            model=self._model_name,
            contents=prompt,
        ):
            yield chunk.text

    # ------------------------------------------------------------------
    # Multi-turn chat
    # ------------------------------------------------------------------

    def start_chat(self) -> None:
        """Start a new multi-turn chat session."""
        self._chat = self._client.chats.create(model=self._model_name)

    def chat(self, message: str) -> str:
        """Send a message in the current chat session.

        A new session is started automatically if one is not already active.

        Parameters
        ----------
        message:
            The user message to send.

        Returns
        -------
        str
            The model's response text.
        """
        if not message or not message.strip():
            raise ValueError("Message must not be empty.")
        if self._chat is None:
            self.start_chat()
        response = self._chat.send_message(message)
        return response.text

    def reset_chat(self) -> None:
        """Clear the current chat history and start a fresh session."""
        self.start_chat()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def model_name(self) -> str:
        """The name of the underlying Gemini model in use."""
        return self._model_name

