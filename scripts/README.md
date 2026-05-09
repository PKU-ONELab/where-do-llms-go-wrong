# Scripts

Reusable command-line tools for quickstart validation, inference, preprocessing, and data inspection.

## Fast path

```bash
make quickstart
make smoke-test
```

`make quickstart` is zero-dependency. `make smoke-test` requires `requirements-core.txt` and validates every runner without API/model calls.

## Input format for model runners

The inference runners expect a JSON list of chat-message lists:

```json
[
  [
    {"role": "system", "content": "You are a concise academic-review assistant."},
    {"role": "user", "content": "Summarize the review."}
  ]
]
```

Use `--validate-only` to check this format without calling an API or loading a model.

## `quickstart.py`

Zero-dependency release-health check.

```bash
python scripts/quickstart.py
```

It validates required files, example schemas, prompt JSONL files, and citation metadata, then writes `outputs/quickstart/quickstart_summary.json`.

## `run_openrouter.py`

OpenAI-compatible API runner. Works with OpenAI-style endpoints such as OpenRouter.

```bash
export OPENROUTER_API_KEY=***
python scripts/run_openrouter.py \
  --input examples/example.json \
  --output outputs/model_outputs.jsonl \
  --model mistralai/mistral-small-3.1-24b-instruct \
  --base-url https://openrouter.ai/api/v1 \
  --api-key-env OPENROUTER_API_KEY \
  --limit 1
```

## `run_gemini.py`

Gemini API runner.

```bash
export GEMINI_API_KEY=***
python scripts/run_gemini.py \
  --input examples/example.json \
  --output outputs/gemini_outputs.jsonl \
  --model gemini-2.0-flash \
  --limit 1
```

## `run_vllm.py`

Optional local inference through vLLM. Install `requirements-vllm.txt` only in a CUDA/PyTorch-compatible environment.

```bash
python scripts/run_vllm.py \
  --input examples/example.json \
  --output outputs/vllm_outputs.jsonl \
  --model-path Qwen/Qwen2.5-72B-Instruct \
  --tensor-parallel-size 8 \
  --limit 1
```

## `clean_openreview.py`

Extracts official-review and author-response conversations from an OpenReview comments JSON export.

```bash
python scripts/clean_openreview.py \
  --input examples/openreview_comments_minimal.json \
  --output outputs/openreview_conversations.json \
  --forum-id forum_example \
  --print-text
```

## `summarize_release_data.py`

No-dependency data inventory helper. Download the Hugging Face dataset first:

```bash
hf download jiataoli/ai-reviewer-diagnostic-data \
  --repo-type dataset \
  --local-dir ai-reviewer-diagnostic-data
python scripts/summarize_release_data.py --data-dir ai-reviewer-diagnostic-data/data
```
