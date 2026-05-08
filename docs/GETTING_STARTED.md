# Getting Started

This page is for someone who arrives from GitHub and wants to know what they can run immediately.

## Fastest path

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-core.txt
python scripts/summarize_release_data.py --data-dir ../HuggingFace-Dataset/data
```

That command does not call any model API. It just verifies that the release data is present and summarizes file counts, JSONL row counts, and largest artifacts.

## Run one model call

OpenAI-compatible / OpenRouter:

```bash
export OPENAI_API_KEY=your_key_here
python scripts/run_openrouter.py \
  --input examples/example.json \
  --output outputs/model_outputs.jsonl \
  --model mistralai/mistral-small-3.1-24b-instruct \
  --base-url https://openrouter.ai/api/v1 \
  --limit 1
```

Gemini:

```bash
export GEMINI_API_KEY=your_key_here
python scripts/run_gemini.py \
  --input examples/example.json \
  --output outputs/gemini_outputs.jsonl \
  --model gemini-2.0-flash \
  --limit 1
```

## Use the OpenReview cleaner

```bash
python scripts/clean_openreview.py \
  --input examples/openreview_comments_minimal.json \
  --output outputs/openreview_conversations.json \
  --forum-id forum_example \
  --print-text
```

## Where to look next

- Need prompts? Start with `prompts/base_prompt.jsonl` and `prompts/perturb_prompt.jsonl`.
- Need generated experiment artifacts? Start with the Hugging Face dataset (`../HuggingFace-Dataset/data/` locally).
- Need analysis scripts? Start with `analysis/README.md`.
- Need citation? Use `CITATION.bib` or the BibTeX block in `README.md`.
