# Getting Started

This page is for someone who arrives from GitHub and wants to run something immediately.

## Fastest API-free path

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements-core.txt
make smoke-test
```

This validates the example inputs, compiles the Python files, checks that all inference runners can validate inputs without API/model calls, and runs the OpenReview-cleaner fixture.

## Download and inspect the data

```bash
hf download jiataoli/ai-reviewer-diagnostic-data \
  --repo-type dataset \
  --local-dir ai-reviewer-diagnostic-data
python scripts/summarize_release_data.py --data-dir ai-reviewer-diagnostic-data/data
```

Expected summary starts with the file count and artifact size, followed by JSONL row counts and largest files.

## Run one model call

OpenAI-compatible / OpenRouter:

```bash
export OPENROUTER_API_KEY=your_key_here
python scripts/run_openrouter.py \
  --input examples/example.json \
  --output outputs/model_outputs.jsonl \
  --model mistralai/mistral-small-3.1-24b-instruct \
  --base-url https://openrouter.ai/api/v1 \
  --api-key-env OPENROUTER_API_KEY \
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
- Need generated experiment artifacts? Download the Hugging Face dataset.
- Need analysis scripts? Start with `analysis/README.md`.
- Need citation? Use `CITATION.bib` or the BibTeX block in `README.md`.
