"""Run local vLLM inference for a JSON list of chat-message lists.

Example:
    python scripts/run_vllm.py \
        --input examples/example.json \
        --output outputs/qwen.jsonl \
        --model-path Qwen/Qwen2.5-72B-Instruct \
        --tensor-parallel-size 8
"""

from __future__ import annotations

import argparse
from typing import Any

try:
    from chat_io import dump_jsonl, load_chat_batch
except ImportError:  # pragma: no cover - supports `python -m scripts.run_vllm`
    from scripts.chat_io import dump_jsonl, load_chat_batch


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run local vLLM chat generation over a prompt batch.")
    parser.add_argument("--input", required=True, help="JSON list of chat-message lists.")
    parser.add_argument("--output", required=True, help="Output JSONL path.")
    parser.add_argument("--model-path", required=True, help="Hugging Face model id or local model path.")
    parser.add_argument("--tensor-parallel-size", type=int, default=1)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--max-tokens", type=int, default=2048)
    parser.add_argument("--max-model-len", type=int, default=32768)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--validate-only", action="store_true", help="Validate input JSON and exit without loading vLLM.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    chat_batch = load_chat_batch(args.input, args.limit)
    if args.validate_only:
        print(f"Validated {len(chat_batch)} chat examples from {args.input}")
        return

    try:
        from transformers import AutoTokenizer
        from vllm import LLM, SamplingParams
    except ImportError as exc:
        raise SystemExit("Missing vLLM dependencies. Install with `uv sync --extra vllm`.") from exc

    tokenizer = AutoTokenizer.from_pretrained(args.model_path)
    prompts = tokenizer.apply_chat_template(chat_batch, tokenize=False, add_generation_prompt=True)
    llm = LLM(
        model=args.model_path,
        tensor_parallel_size=args.tensor_parallel_size,
        max_model_len=args.max_model_len,
    )
    llm.set_tokenizer(tokenizer)
    outputs = llm.generate(prompts, SamplingParams(temperature=args.temperature, max_tokens=args.max_tokens))
    rows: list[dict[str, Any]] = []
    for messages, sample in zip(chat_batch, outputs, strict=True):
        rows.append(
            {
                "input": messages,
                "output": [choice.text for choice in sample.outputs],
                "model": args.model_path,
                "error": None,
            }
        )
    dump_jsonl(args.output, rows)


if __name__ == "__main__":
    main()
