"""Tests for gigle_ai.cli."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from gigle_ai.cli import build_parser, cmd_ask, main


class TestParser:
    def test_ask_command_parses_prompt(self):
        parser = build_parser()
        args = parser.parse_args(["-k", "my-key", "ask", "What", "is", "AI?"])
        assert args.command == "ask"
        assert args.prompt == ["What", "is", "AI?"]
        assert args.api_key == "my-key"

    def test_chat_command(self):
        parser = build_parser()
        args = parser.parse_args(["chat"])
        assert args.command == "chat"

    def test_no_command_returns_zero(self):
        with patch("gigle_ai.cli.GeminiClient"):
            assert main([]) == 0


class TestCmdAsk:
    def test_prints_response(self, capsys):
        client = MagicMock()
        client.generate.return_value = "Artificial intelligence is..."
        parser = build_parser()
        args = parser.parse_args(["ask", "What is AI?"])
        rc = cmd_ask(client, args)
        captured = capsys.readouterr()
        assert rc == 0
        assert "Artificial intelligence is..." in captured.out

    def test_returns_one_on_error(self, capsys):
        client = MagicMock()
        client.generate.side_effect = RuntimeError("API error")
        parser = build_parser()
        args = parser.parse_args(["ask", "fail"])
        rc = cmd_ask(client, args)
        assert rc == 1
        assert "Error" in capsys.readouterr().err


class TestMain:
    def test_missing_api_key_returns_one(self, monkeypatch, capsys):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        rc = main(["-k", "", "ask", "hello"])
        assert rc == 1

    def test_ask_end_to_end(self, monkeypatch, capsys):
        monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
        with patch("gigle_ai.cli.GeminiClient") as MockClient:
            instance = MockClient.return_value
            instance.generate.return_value = "42"
            rc = main(["ask", "What is the answer?"])
        assert rc == 0
        assert "42" in capsys.readouterr().out
