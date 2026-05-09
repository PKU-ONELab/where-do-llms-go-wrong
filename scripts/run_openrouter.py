"""Run chat-completion inference via an OpenAI-compatible API such as OpenRouter.

Example:
    export OPENROUTER_API_KEY=...
    uv run python scripts/run_openrouter.py \
        --input examples/example.json \
        --output outputs/example.jsonl \
        --model mistralai/mistral-small-3.1-24b-instruct \
        --base-url https://openrouter.ai/api/v1 \
        --api-key-env OPENROUTER_API_KEY

Input format: a JSON file containing a list of chat-message lists, e.g.
[[{"role": "user", "content": "..."}], ...]
"""

from __future__ import annotations

import argparse
import os
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from openai import OpenAI
from tqdm import tqdm

try:
    from chat_io import dump_jsonl, load_chat_batch
except ImportError:  # pragma: no cover - supports `python -m scripts.run_openrouter`
    from scripts.chat_io import dump_jsonl, load_chat_batch


def call_model(client: OpenAI, messages: list[dict[str, Any]], model: str, max_retries: int) -> str:
    last_error: Exception | None = None
    for retry in range(max_retries + 1):
        try:
            completion = client.chat.completions.create(model=model, messages=messages)
            return completion.choices[0].message.content or ""
        except Exception as exc:  # noqa: BLE001 - provider SDKs expose varied transient errors
            last_error = exc
            if retry >= max_retries:
                break
            wait = (2**retry) + random.uniform(0, 0.5)
            print(f"API error: {exc}; retrying in {wait:.1f}s", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError(f"Model call failed after {max_retries + 1} attempts: {last_error}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run an OpenAI-compatible chat-completion batch.")
    parser.add_argument("--input", required=True, help="JSON list of chat-message lists.")
    parser.add_argument("--output", required=True, help="Output JSONL path.")
    parser.add_argument("--model", required=True)
    parser.add_argument("--base-url", default=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    parser.add_argument("--api-key-env", default="OPENAI_API_KEY")
    parser.add_argument("--workers", type=int, default=1, help="Parallel requests. Use 1 for safest provider behavior.")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--max-retries", type=int, default=6)
    parser.add_argument("--validate-only", action="store_true", help="Validate input JSON and exit without calling the API.")
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

    client = OpenAI(base_url=args.base_url, api_key=api_key)

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
