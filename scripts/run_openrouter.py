"""Run chat-completion inference via an OpenAI-compatible API such as OpenRouter.

Example:
    export OPENAI_API_KEY=...
    python scripts/run_openrouter.py \
        --input data/inputs/example.json \
        --output outputs/example.jsonl \
        --model mistralai/mistral-small-3.1-24b-instruct \
        --base-url https://openrouter.ai/api/v1

Input format: a JSON file containing a list of chat message lists, e.g.
[[{"role": "user", "content": "..."}], ...]
"""
import argparse, json, os, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List
from tqdm import tqdm
from openai import OpenAI


def load_json(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def dump_jsonl(path: str, rows: List[dict]):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')


def call_model(client: OpenAI, messages: List[dict], model: str, max_retries: int = 8):
    for retry in range(max_retries):
        try:
            completion = client.chat.completions.create(model=model, messages=messages)
            return completion.choices[0].message.content
        except Exception as exc:
            wait = 2 ** retry
            print(f"API error: {exc}; retrying in {wait}s")
            time.sleep(wait)
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True, help='JSON list of chat-message lists')
    parser.add_argument('--output', required=True, help='Output JSONL path')
    parser.add_argument('--model', required=True)
    parser.add_argument('--base-url', default=os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com/v1'))
    parser.add_argument('--api-key-env', default='OPENAI_API_KEY')
    parser.add_argument('--workers', type=int, default=8)
    parser.add_argument('--limit', type=int, default=None)
    args = parser.parse_args()

    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        raise EnvironmentError(f'Missing API key environment variable: {args.api_key_env}')

    client = OpenAI(base_url=args.base_url, api_key=api_key)
    batch = load_json(args.input)
    if args.limit is not None:
        batch = batch[:args.limit]

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        outputs = list(tqdm(
            ex.map(lambda messages: {'input': messages, 'output': call_model(client, messages, args.model)}, batch),
            total=len(batch)
        ))
    dump_jsonl(args.output, outputs)


if __name__ == '__main__':
    main()
