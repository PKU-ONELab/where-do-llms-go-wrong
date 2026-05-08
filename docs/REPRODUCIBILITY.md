# Reproducibility Notes

This repository contains runnable inference wrappers, analysis scripts, prompts, examples, citation metadata, and documentation for the CIKM 2025 paper. It is optimized for easy reuse and citation. Large experiment artifacts are hosted in the companion Hugging Face dataset.

## Environment setup

Core API runners require Python 3.10+ and are tested with Python 3.11:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements-core.txt
```

Analysis scripts:

```bash
pip install -r requirements-analysis.txt
```

Optional local vLLM inference:

```bash
pip install -r requirements-vllm.txt
```

Install vLLM only in an environment compatible with the target CUDA, PyTorch, and GPU setup.

## API-free smoke test

This is the recommended first test for new users:

```bash
make smoke-test
```

This creates files under `outputs/`. `outputs/` is ignored by Git and can be removed with `make clean`.

Equivalent direct commands:

```bash
python -m compileall -q scripts analysis
python -m json.tool examples/example.json >/dev/null
python -m json.tool examples/openreview_comments_minimal.json >/dev/null
python scripts/run_openrouter.py --input examples/example.json --output outputs/validate_openrouter.jsonl --model dummy --validate-only
python scripts/run_gemini.py --input examples/example.json --output outputs/validate_gemini.jsonl --validate-only
python scripts/run_vllm.py --input examples/example.json --output outputs/validate_vllm.jsonl --model-path dummy --validate-only
python scripts/clean_openreview.py \
  --input examples/openreview_comments_minimal.json \
  --output outputs/openreview_conversations.json \
  --forum-id forum_example
```

## Dataset inspection

```bash
hf download jiataoli/ai-reviewer-diagnostic-data \
  --repo-type dataset \
  --local-dir ai-reviewer-diagnostic-data
python scripts/summarize_release_data.py --data-dir ai-reviewer-diagnostic-data/data --top-n 5
```

## API runner smoke tests

OpenAI-compatible / OpenRouter runner:

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

Gemini runner:

```bash
export GEMINI_API_KEY=your_key_here
python scripts/run_gemini.py \
  --input examples/example.json \
  --output outputs/gemini_outputs.jsonl \
  --model gemini-2.0-flash \
  --limit 1
```

## Current release guarantees

The current release candidate has been checked for:

- Python syntax validity in `scripts/` and `analysis/`.
- JSON validity for example inputs.
- API-free validation paths for OpenRouter, Gemini, and vLLM runners.
- A working OpenReview-cleaner smoke test on `examples/openreview_comments_minimal.json`.
- No obvious hard-coded API keys or local machine paths in text files.
- Scrubbed Office metadata for `.docx` prompt documents.
- SHA256 checksums for the Hugging Face dataset artifacts via `dataset_manifest.csv`.

## Known limits

- Dataset redistribution rights and final dataset license must be confirmed before making the Hugging Face dataset public.
- Remaining analysis scripts are preserved from the experiment workflow and are not yet all fully parameterized CLIs.
- Formal artifact-evaluation reproduction would need exact model versions, prompt versions, source snapshots, and expected outputs for every table/figure.
