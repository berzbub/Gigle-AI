"""
Network AI Server
=================
Exposes Gigle-AI multimodal capabilities over HTTP so any device on the
network can query text analysis, image description, and chat endpoints.

Usage::

    from gigle_ai.network.server import NetworkAIServer

    server = NetworkAIServer(host="0.0.0.0", port=5000)
    server.run()
"""

import json
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

from gigle_ai.ai.multimodal import MultimodalAI
from gigle_ai.utils.helpers import build_response

logger = logging.getLogger(__name__)


class _RequestHandler(BaseHTTPRequestHandler):
    """Internal HTTP request handler for the Network AI server."""

    ai: MultimodalAI  # set by NetworkAIServer before starting

    # ------------------------------------------------------------------
    # Routing helpers
    # ------------------------------------------------------------------

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}

    # ------------------------------------------------------------------
    # GET  /health
    # GET  /info
    # ------------------------------------------------------------------

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/health":
            self._send_json(200, {"status": "ok"})

        elif path == "/info":
            self._send_json(200, {
                "name": "Gigle-AI Network AI",
                "version": "0.1.0",
                "capabilities": ["text", "image", "chat"],
            })

        else:
            self._send_json(404, {"error": "Not found"})

    # ------------------------------------------------------------------
    # POST /analyze/text
    # POST /analyze/image
    # POST /chat
    # ------------------------------------------------------------------

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        body = self._read_json_body()

        if path == "/analyze/text":
            text = body.get("text", "")
            if not text:
                self._send_json(400, {"error": "Missing 'text' field"})
                return
            result = self.ai.analyze_text(text)
            self._send_json(200, build_response("text", result))

        elif path == "/analyze/image":
            image_data = body.get("image", "")
            if not image_data:
                self._send_json(400, {"error": "Missing 'image' field (base64)"})
                return
            result = self.ai.describe_image(image_data)
            self._send_json(200, build_response("image", result))

        elif path == "/chat":
            message = body.get("message", "")
            history = body.get("history", [])
            if not message:
                self._send_json(400, {"error": "Missing 'message' field"})
                return
            result = self.ai.chat(message, history)
            self._send_json(200, build_response("chat", result))

        else:
            self._send_json(404, {"error": "Not found"})

    def log_message(self, fmt: str, *args) -> None:  # noqa: ANN001
        logger.debug(fmt, *args)


class NetworkAIServer:
    """
    Lightweight HTTP server that makes multimodal AI available to every
    device on the local (or wide-area) network.

    Parameters
    ----------
    host:
        Interface to bind on.  ``"0.0.0.0"`` accepts connections from all
        network interfaces.
    port:
        TCP port to listen on (default ``5000``).
    ai:
        Optional pre-configured :class:`~gigle_ai.ai.multimodal.MultimodalAI`
        instance.  A default instance is created when *None*.
    """

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 5000,
        ai: MultimodalAI | None = None,
    ) -> None:
        self.host = host
        self.port = port
        self.ai = ai or MultimodalAI()
        self._server: HTTPServer | None = None
        self._thread: threading.Thread | None = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def run(self, *, threaded: bool = False) -> None:
        """Start the server.

        Parameters
        ----------
        threaded:
            When *True* the server runs in a daemon background thread so
            the calling code can continue executing (useful for testing).
            When *False* (default) the call blocks until the server is
            stopped.
        """
        # Inject the AI engine into the handler class
        handler_cls = type(
            "_BoundHandler",
            (_RequestHandler,),
            {"ai": self.ai},
        )
        self._server = HTTPServer((self.host, self.port), handler_cls)
        logger.info("Gigle-AI Network AI server listening on %s:%s", self.host, self.port)

        if threaded:
            self._thread = threading.Thread(
                target=self._server.serve_forever, daemon=True
            )
            self._thread.start()
        else:
            try:
                self._server.serve_forever()
            except KeyboardInterrupt:
                self.stop()

    def stop(self) -> None:
        """Gracefully shut down the server."""
        if self._server is not None:
            self._server.shutdown()
            logger.info("Gigle-AI Network AI server stopped.")
