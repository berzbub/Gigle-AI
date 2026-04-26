# Gigle-AI — Multimodal AI Multi-Device

**Gigle-AI** is a multimodal AI framework that exposes text analysis, image
description, and conversational AI capabilities over a lightweight HTTP server
so that *every device on your network* can benefit from shared AI intelligence.

---

## Features

| Capability | Description |
|---|---|
| 📝 Text analysis | Sentiment, summary, word count, question detection, language hint |
| 🖼️ Image description | Format detection, size metadata, pluggable vision back-end |
| 💬 Multi-turn chat | Context-aware conversation with history tracking |
| 🌐 Network AI server | Zero-dependency HTTP server – one machine hosts, all devices query |
| 📱 Multi-device client | Python SDK to reach the server from any device on the network |

---

## Quick Start

### 1 — Install

```bash
pip install -e .
```

### 2 — Start the Network AI server

```python
from gigle_ai.network.server import NetworkAIServer

server = NetworkAIServer(host="0.0.0.0", port=5000)
server.run()          # blocks; use run(threaded=True) in tests / scripts
```

### 3 — Connect from another device

```python
from gigle_ai.network.client import NetworkAIClient

client = NetworkAIClient("http://192.168.1.10:5000")

# Health check
print(client.health())           # {"status": "ok"}

# Analyze text
print(client.analyze_text("Gigle-AI is absolutely fantastic!"))
# {"type": "text", "result": {"sentiment": "positive", "word_count": 5, ...}}

# Describe an image (pass bytes or file path)
with open("photo.jpg", "rb") as f:
    print(client.analyze_image(f.read()))
# {"type": "image", "result": {"format_hint": "jpeg", "size_bytes": 43210, ...}}

# Multi-turn chat
resp = client.chat("Hello!")
print(resp["result"]["reply"])   # Hello! I'm Gigle-AI. How can I assist you today?

resp = client.chat("What can you do?", history=resp["result"]["history"])
print(resp["result"]["reply"])
```

---

## REST API Reference

### `GET /health`
Returns `{"status": "ok"}`.

### `GET /info`
Returns server metadata and capability list.

### `POST /analyze/text`
```json
{ "text": "Your input here" }
```
Response:
```json
{
  "type": "text",
  "result": {
    "summary": "Your input here",
    "sentiment": "neutral",
    "word_count": 3,
    "is_question": false,
    "language_hint": "en"
  }
}
```

### `POST /analyze/image`
```json
{ "image": "<base64-encoded image bytes>" }
```
Response:
```json
{
  "type": "image",
  "result": {
    "description": "Image received (43210 bytes, format: jpeg). ...",
    "format_hint": "jpeg",
    "size_bytes": 43210
  }
}
```

### `POST /chat`
```json
{
  "message": "What can you do?",
  "history": []
}
```
Response:
```json
{
  "type": "chat",
  "result": {
    "reply": "I can analyze text...",
    "history": [
      {"role": "user", "content": "What can you do?"},
      {"role": "assistant", "content": "I can analyze text..."}
    ]
  }
}
```

---

## Extending with a Capable Model

Sub-class `MultimodalAI` and override the methods you want to enhance:

```python
from gigle_ai.ai.multimodal import MultimodalAI
from gigle_ai.network.server import NetworkAIServer

class MyAI(MultimodalAI):
    def _generate_reply(self, message, history):
        # call your LLM here
        return my_llm.generate(message, history)

server = NetworkAIServer(ai=MyAI())
server.run()
```

---

## Running Tests

```bash
pip install pytest
pytest
```

---

## Project Structure

```
gigle_ai/
├── __init__.py
├── ai/
│   ├── __init__.py
│   └── multimodal.py       # MultimodalAI engine
├── network/
│   ├── __init__.py
│   ├── server.py           # NetworkAIServer
│   └── client.py           # NetworkAIClient
└── utils/
    ├── __init__.py
    └── helpers.py          # encode_image, decode_image, build_response

tests/
├── test_ai.py
├── test_network.py
└── test_utils.py
```

---

## License

Apache 2.0 – see [LICENSE](LICENSE).
