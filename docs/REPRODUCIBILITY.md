# Reproducibility Notes

This repository is a release candidate. It contains runnable inference wrappers, analysis scripts, prompts, selected data artifacts, and the paper PDF. It is optimized for easy reuse and citation; full artifact-evaluation-grade reproduction still requires final data-rights/provenance decisions.

## Environment setup

Core API runners:

```bash
python -m venv .venv
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

This creates `outputs/openreview_conversations.json` during the test. `outputs/` is ignored by Git and can be removed with `make clean`.

Equivalent direct commands:

```bash
python -m compileall -q scripts analysis
python -m json.tool examples/example.json >/dev/null
python -m json.tool examples/openreview_comments_minimal.json >/dev/null
python scripts/clean_openreview.py \
  --input examples/openreview_comments_minimal.json \
  --output outputs/openreview_conversations.json \
  --forum-id forum_example
python scripts/summarize_release_data.py --data-dir ../HuggingFace-Dataset/data --top-n 5
```

## API runner smoke tests

OpenAI-compatible API runner:

```bash
export OPENAI_API_KEY=your_key_here
python scripts/run_openrouter.py \
  --input examples/example.json \
  --output outputs/model_outputs.jsonl \
  --model mistralai/mistral-small-3.1-24b-instruct \
  --base-url https://openrouter.ai/api/v1 \
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
- A working OpenReview-cleaner smoke test on `examples/openreview_comments_minimal.json`.
- No obvious hard-coded API keys or local machine paths in text files.
- Scrubbed Office metadata for `.docx` prompt documents.

## Known gaps

TODO: Confirm data-rights and redistribution permissions before treating the included data artifacts as publishable.

TODO: Add exact model versions, prompt versions, data snapshots, and expected hashes for any formally reproduced experiment.

TODO: Convert remaining analysis scripts to fully parameterized CLIs if the final release is expected to regenerate every table and figure from scratch.

TODO: Add expected-output fixtures for analysis scripts where possible.
