# Getting Started

This page is for someone who arrives from GitHub and wants to run something immediately.

## 1. Zero-dependency quickstart

```bash
git clone https://github.com/JiataoLi/where-do-llms-go-wrong
cd where-do-llms-go-wrong
make quickstart
```

This validates the release layout, example schemas, prompt files, and citation metadata. It does not install packages, call an API, download models, or require the companion dataset.

Expected output:

```text
AI-reviewer diagnostic release quickstart: OK
Validated 1 chat example(s), 3 OpenReview note(s).
Prompt rows: base=9, perturb=7.
Wrote outputs/quickstart/quickstart_summary.json
```

The written file is a small schema/demo summary, not a model result.

## 2. Install lightweight dependencies

Dependencies live in `pyproject.toml`; `uv` is the recommended installer.

```bash
uv sync
```

Pip fallback:

```bash
python -m pip install -e .
```

## 3. API-free smoke test

```bash
uv run make smoke-test
```

This compiles Python files, validates example inputs, checks that all inference runners can validate inputs without API/model calls, and runs the OpenReview-cleaner fixture.

## 4. Download and inspect the data

```bash
uv run hf download jiataoli/ai-reviewer-diagnostic-data \
  --repo-type dataset \
  --local-dir ai-reviewer-diagnostic-data
uv run python scripts/summarize_release_data.py --data-dir ai-reviewer-diagnostic-data/data
```

The summary prints file counts, artifact size, file types, JSONL row counts, sample keys, and largest files.

## 5. Run one model call

OpenAI-compatible / OpenRouter:

```bash
export OPENROUTER_API_KEY=***
uv run python scripts/run_openrouter.py \
  --input examples/example.json \
  --output outputs/model_outputs.jsonl \
  --model mistralai/mistral-small-3.1-24b-instruct \
  --base-url https://openrouter.ai/api/v1 \
  --api-key-env OPENROUTER_API_KEY \
  --limit 1
```

Gemini:

```bash
export GEMINI_API_KEY=***
uv run python scripts/run_gemini.py \
  --input examples/example.json \
  --output outputs/gemini_outputs.jsonl \
  --model gemini-2.0-flash \
  --limit 1
```

## 6. Use the OpenReview cleaner

```bash
uv run python scripts/clean_openreview.py \
  --input examples/openreview_comments_minimal.json \
  --output outputs/openreview_conversations.json \
  --forum-id forum_example \
  --print-text
```

## 7. Cite the work

Use `CITATION.bib`, `CITATION.cff`, or the BibTeX block in `README.md`. The DOI is:

```text
https://doi.org/10.1145/3746252.3761274
```

## Where to look next

- Need prompts? Start with `prompts/base_prompt.jsonl` and `prompts/perturb_prompt.jsonl`.
- Need generated experiment artifacts? Download the Hugging Face dataset.
- Need script examples? Read `scripts/README.md`.
- Need analysis scripts? Start with `analysis/README.md`.
- Need reproduction limits and tiers? Read `docs/REPRODUCIBILITY.md`.
