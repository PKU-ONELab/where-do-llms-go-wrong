"""Run local vLLM inference for a JSON list of chat-message lists.

Example:
    python scripts/run_vllm.py \
        --input data/inputs/example.json \
        --output outputs/qwen.json \
        --model-path Qwen/Qwen2.5-72B-Instruct \
        --tensor-parallel-size 8
"""
import argparse, json
from pathlib import Path
from vllm import LLM, SamplingParams
from transformers import AutoTokenizer


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--model-path', required=True, help='HF model id or local model path')
    parser.add_argument('--tensor-parallel-size', type=int, default=1)
    parser.add_argument('--temperature', type=float, default=0.95)
    parser.add_argument('--max-tokens', type=int, default=8192)
    parser.add_argument('--max-model-len', type=int, default=131072)
    parser.add_argument('--limit', type=int, default=None)
    args = parser.parse_args()

    chat_batch = load_json(args.input)
    if args.limit is not None:
        chat_batch = chat_batch[:args.limit]

    tokenizer = AutoTokenizer.from_pretrained(args.model_path)
    prompts = tokenizer.apply_chat_template(chat_batch, tokenize=False, add_generation_prompt=True)
    llm = LLM(model=args.model_path, tensor_parallel_size=args.tensor_parallel_size, max_model_len=args.max_model_len)
    llm.set_tokenizer(tokenizer)
    outputs = llm.generate(prompts, SamplingParams(temperature=args.temperature, max_tokens=args.max_tokens))
    docs = [[choice.text for choice in sample.outputs] for sample in outputs]

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()
