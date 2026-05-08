# Scripts

Runnable helper scripts for inference, preprocessing, and release inspection.

## `run_openrouter.py`

OpenAI-compatible API runner. Works with OpenAI-style endpoints such as OpenRouter.

```bash
export OPENAI_API_KEY=your_key_here
python scripts/run_openrouter.py \
  --input examples/example.json \
  --output outputs/model_outputs.jsonl \
  --model mistralai/mistral-small-3.1-24b-instruct \
  --base-url https://openrouter.ai/api/v1 \
  --limit 1
```

## `run_gemini.py`

Gemini API runner.

```bash
export GEMINI_API_KEY=your_key_here
python scripts/run_gemini.py \
  --input examples/example.json \
  --output outputs/gemini_outputs.jsonl \
  --model gemini-2.0-flash \
  --limit 1
```

## `run_vllm.py`

Optional local inference through vLLM. Install `requirements-vllm.txt` only in a CUDA/PyTorch-compatible environment.

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

No-dependency data inventory helper.

```bash
python scripts/summarize_release_data.py --data-dir ../HuggingFace-Dataset/data
```
