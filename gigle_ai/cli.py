"""Command-line interface for Gigle-AI."""

from __future__ import annotations

import argparse
import sys

from gigle_ai.client import GeminiClient


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gigle-ai",
        description="Chat with Google Gemini from the command line.",
    )
    parser.add_argument(
        "-k",
        "--api-key",
        default=None,
        help="Google AI API key (overrides GEMINI_API_KEY env var).",
    )
    parser.add_argument(
        "-m",
        "--model",
        default=GeminiClient.DEFAULT_MODEL,
        help=f"Gemini model to use (default: {GeminiClient.DEFAULT_MODEL}).",
    )

    sub = parser.add_subparsers(dest="command")

    # ask — one-shot query
    ask_p = sub.add_parser("ask", help="Send a single prompt and print the response.")
    ask_p.add_argument("prompt", nargs="+", help="The prompt text.")

    # chat — interactive multi-turn session
    sub.add_parser("chat", help="Start an interactive multi-turn chat session.")

    return parser


def cmd_ask(client: GeminiClient, args: argparse.Namespace) -> int:
    prompt = " ".join(args.prompt)
    try:
        print(client.generate(prompt))
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


def cmd_chat(client: GeminiClient) -> int:
    print("Gigle-AI interactive chat (type 'exit' or 'quit' to leave).\n")
    client.start_chat()
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        if not user_input:
            continue
        try:
            response = client.chat(user_input)
            print(f"Gemini: {response}\n")
        except Exception as exc:  # noqa: BLE001
            print(f"Error: {exc}", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    try:
        client = GeminiClient(api_key=args.api_key, model=args.model)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.command == "ask":
        return cmd_ask(client, args)
    if args.command == "chat":
        return cmd_chat(client)

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
