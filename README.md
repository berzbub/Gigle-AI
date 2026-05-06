# Gigle-AI 🤖

A lightweight Python wrapper for Google's **Gemini** AI API, with an easy-to-use
library interface and an interactive CLI.

---

## Features

- 🔑 Simple API key setup via environment variable or constructor argument
- 💬 One-shot prompt generation
- 🌊 Streaming support for long responses
- 🗨️ Multi-turn chat sessions
- 🖥️ Command-line interface (`gigle-ai ask` / `gigle-ai chat`)
- ✅ Built on the current `google-genai` SDK (not the deprecated `google-generativeai`)

---

## Installation

```bash
pip install gigle-ai
```

Or, to install directly from source:

```bash
git clone https://github.com/berzbub/Gigle-AI.git
cd Gigle-AI
pip install -e ".[dev]"
```

---

## Quickstart

### Set your API key

Obtain a free API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
and export it:

```bash
export GEMINI_API_KEY="your-api-key-here"
```

### Python library

```python
from gigle_ai import GeminiClient

client = GeminiClient()  # uses GEMINI_API_KEY env var

# One-shot generation
answer = client.generate("Explain quantum computing in one paragraph.")
print(answer)

# Streaming
for chunk in client.stream("Write a short poem about the stars."):
    print(chunk, end="", flush=True)

# Multi-turn chat
client.start_chat()
print(client.chat("Hi! What can you help me with?"))
print(client.chat("Tell me a joke."))
```

You can also pass the API key and model name explicitly:

```python
client = GeminiClient(api_key="your-key", model="gemini-1.5-pro")
```

---

## CLI usage

After installation the `gigle-ai` command is available.

### Ask a single question

```bash
gigle-ai ask "What is the capital of France?"
```

### Start an interactive chat session

```bash
gigle-ai chat
```

### Specify a different model

```bash
gigle-ai --model gemini-1.5-pro ask "Summarise the Transformer architecture."
```

### Pass the API key inline

```bash
gigle-ai --api-key YOUR_KEY ask "Hello!"
```

Run `gigle-ai --help` for a full list of options.

---

## Running the tests

```bash
pip install -e ".[dev]"
python -m pytest
```

---

## Project structure

```
Gigle-AI/
├── gigle_ai/
│   ├── __init__.py   # Package entry point, exports GeminiClient
│   ├── client.py     # GeminiClient implementation
│   └── cli.py        # Command-line interface
├── tests/
│   ├── test_client.py
│   └── test_cli.py
├── pyproject.toml
├── README.md
└── LICENSE
```

---

## License

Licensed under the [Apache License 2.0](LICENSE).
