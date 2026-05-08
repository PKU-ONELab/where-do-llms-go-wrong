"""Run Gemini inference for a JSON list of chat-style prompts.

Example:
    export GEMINI_API_KEY=...
    python scripts/run_gemini.py --input data/inputs/example.json --output outputs/gemini.jsonl
"""
import argparse, json, os, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tqdm import tqdm
from google import genai


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def dump_jsonl(path, rows):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')


def chat_to_text(messages):
    if isinstance(messages, list):
        return '\n\n'.join(str(m.get('content', m)) for m in messages)
    return str(messages)


def call_model(client, messages, model, max_retries=8):
    prompt = chat_to_text(messages)
    for retry in range(max_retries):
        try:
            return client.models.generate_content(model=model, contents=[prompt]).text
        except Exception as exc:
            wait = 2 ** retry
            print(f"API error: {exc}; retrying in {wait}s")
            time.sleep(wait)
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--model', default='gemini-2.0-flash')
    parser.add_argument('--api-key-env', default='GEMINI_API_KEY')
    parser.add_argument('--workers', type=int, default=8)
    parser.add_argument('--limit', type=int, default=None)
    args = parser.parse_args()

    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        raise EnvironmentError(f'Missing API key environment variable: {args.api_key_env}')

    client = genai.Client(api_key=api_key)
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
