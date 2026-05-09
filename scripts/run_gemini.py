"""Run Gemini inference for a JSON list of chat-style prompts.

Example:
    export GEMINI_API_KEY=...
    python scripts/run_gemini.py \
        --input examples/example.json \
        --output outputs/gemini.jsonl \
        --model gemini-2.0-flash
"""

from __future__ import annotations

import argparse
import os
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from tqdm import tqdm

try:
    from chat_io import dump_jsonl, load_chat_batch
except ImportError:  # pragma: no cover - supports `python -m scripts.run_gemini`
    from scripts.chat_io import dump_jsonl, load_chat_batch


def chat_to_text(messages: list[dict[str, Any]]) -> str:
    return "\n\n".join(str(message["content"]) for message in messages)


def call_model(client: Any, messages: list[dict[str, Any]], model: str, max_retries: int) -> str:
    prompt = chat_to_text(messages)
    last_error: Exception | None = None
    for retry in range(max_retries + 1):
        try:
            return client.models.generate_content(model=model, contents=[prompt]).text or ""
        except Exception as exc:  # noqa: BLE001 - provider SDKs expose varied transient errors
            last_error = exc
            if retry >= max_retries:
                break
            wait = (2**retry) + random.uniform(0, 0.5)
            print(f"API error: {exc}; retrying in {wait:.1f}s", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError(f"Gemini call failed after {max_retries + 1} attempts: {last_error}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Gemini generation over a chat-prompt batch.")
    parser.add_argument("--input", required=True, help="JSON list of chat-message lists.")
    parser.add_argument("--output", required=True, help="Output JSONL path.")
    parser.add_argument("--model", default="gemini-2.0-flash")
    parser.add_argument("--api-key-env", default="GEMINI_API_KEY")
    parser.add_argument("--workers", type=int, default=1, help="Parallel requests. Use 1 for safest provider behavior.")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--max-retries", type=int, default=6)
    parser.add_argument("--validate-only", action="store_true", help="Validate input JSON and exit without calling Gemini.")
    parser.add_argument("--continue-on-error", action="store_true", help="Write structured error rows instead of exiting on the first failed request.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    batch = load_chat_batch(args.input, args.limit)
    if args.validate_only:
        print(f"Validated {len(batch)} chat examples from {args.input}")
        return

    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        raise EnvironmentError(f"Missing API key environment variable: {args.api_key_env}")

    try:
        from google import genai
    except ImportError as exc:
        raise SystemExit("Missing dependency `google-genai`. Install with `uv sync`.") from exc

    client = genai.Client(api_key=api_key)

    def run_one(messages: list[dict[str, Any]]) -> dict[str, Any]:
        try:
            output = call_model(client, messages, args.model, args.max_retries)
            return {"input": messages, "output": output, "model": args.model, "error": None}
        except Exception as exc:  # noqa: BLE001 - preserve failed row for long batches
            if not args.continue_on_error:
                raise
            return {"input": messages, "output": None, "model": args.model, "error": str(exc)}

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        rows = list(tqdm(executor.map(run_one, batch), total=len(batch)))
    dump_jsonl(args.output, rows)

    failures = sum(1 for row in rows if row.get("error"))
    if failures:
        raise SystemExit(f"{failures} model calls failed; see {args.output}")


if __name__ == "__main__":
    main()
