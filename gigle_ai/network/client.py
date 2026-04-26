"""
Network AI Client
=================
A lightweight SDK that lets any device communicate with a
:class:`~gigle_ai.network.server.NetworkAIServer` running elsewhere on the
network.

Usage::

    from gigle_ai.network.client import NetworkAIClient

    client = NetworkAIClient("http://192.168.1.10:5000")

    # Analyze text
    result = client.analyze_text("What is artificial intelligence?")

    # Describe an image (pass raw bytes or a file path)
    result = client.analyze_image(open("photo.jpg", "rb").read())

    # Multi-turn chat
    result = client.chat("Hello!", history=[])
"""

import base64
import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


class NetworkAIError(Exception):
    """Raised when the server returns an error response."""


class NetworkAIClient:
    """
    HTTP client for the Gigle-AI Network AI server.

    Parameters
    ----------
    base_url:
        Full URL of the running :class:`~gigle_ai.network.server.NetworkAIServer`,
        e.g. ``"http://localhost:5000"`` or ``"http://192.168.1.10:5000"``.
    timeout:
        Socket timeout in seconds for all requests (default ``30``).
    """

    def __init__(self, base_url: str = "http://localhost:5000", timeout: int = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _post(self, endpoint: str, payload: dict) -> dict:
        url = f"{self.base_url}{endpoint}"
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            body = exc.read().decode(errors="replace")
            try:
                detail = json.loads(body).get("error", body)
            except json.JSONDecodeError:
                detail = body
            raise NetworkAIError(f"Server returned {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise NetworkAIError(f"Connection failed: {exc.reason}") from exc

    def _get(self, endpoint: str) -> dict:
        url = f"{self.base_url}{endpoint}"
        req = urllib.request.Request(url, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            raise NetworkAIError(f"Server returned {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise NetworkAIError(f"Connection failed: {exc.reason}") from exc

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def health(self) -> dict:
        """Return server health status."""
        return self._get("/health")

    def info(self) -> dict:
        """Return server metadata and capability list."""
        return self._get("/info")

    def analyze_text(self, text: str) -> dict:
        """
        Analyze *text* using the remote AI.

        Parameters
        ----------
        text:
            The plain-text input to process.

        Returns
        -------
        dict:
            ``{"type": "text", "result": {...}}``
        """
        if not text:
            raise ValueError("text must not be empty")
        return self._post("/analyze/text", {"text": text})

    def analyze_image(self, image: bytes | str | Path) -> dict:
        """
        Ask the remote AI to describe an image.

        Parameters
        ----------
        image:
            Raw image bytes, a base64-encoded string, or a :class:`pathlib.Path`
            / file-path string pointing to an image file on disk.

        Returns
        -------
        dict:
            ``{"type": "image", "result": {...}}``
        """
        if isinstance(image, (str, Path)):
            path = Path(image)
            if path.exists():
                image = path.read_bytes()
            else:
                # assume already base64-encoded
                encoded = image if isinstance(image, str) else image.decode()
                return self._post("/analyze/image", {"image": encoded})
        if isinstance(image, (bytes, bytearray)):
            image = base64.b64encode(image).decode()
        return self._post("/analyze/image", {"image": image})

    def chat(self, message: str, history: list[dict[str, Any]] | None = None) -> dict:
        """
        Send a chat message to the remote AI.

        Parameters
        ----------
        message:
            The user's message.
        history:
            Optional list of previous turns, each a dict with keys
            ``"role"`` (``"user"`` or ``"assistant"``) and ``"content"``.

        Returns
        -------
        dict:
            ``{"type": "chat", "result": {"reply": "...", "history": [...]}}``
        """
        if not message:
            raise ValueError("message must not be empty")
        return self._post("/chat", {"message": message, "history": history or []})
