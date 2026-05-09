# Reproducibility Notes

This repository is designed for fast reuse first, then deeper reproduction. Large experiment artifacts live in the companion Hugging Face dataset; the GitHub repository keeps code, prompts, examples, docs, and citation metadata lightweight.

## Tier 0: immediate quickstart

```bash
make quickstart
```

Guarantees:

- no package installation;
- no API keys;
- no GPU/model download;
- no dataset download;
- validates layout, example schemas, prompt files, and citation metadata;
- writes `outputs/quickstart/quickstart_summary.json`.

This is a schema and release-health demo, not a model result.

## Tier 1: API-free smoke test and report demo

```bash
uv sync
uv run make smoke-test
```

Equivalent direct commands:
```bash
uv run python scripts/quickstart.py
uv run ai-reviewer-diagnostics \
  --baseline examples/system_outputs_baseline.jsonl \
  --perturbed examples/system_outputs_perturbed_soundness.jsonl \
  --condition paper/soundness \
  --output-md outputs/demo_diagnostic_report.md \
  --output-json outputs/demo_diagnostic_report.json
uv run python -m compileall -q scripts analysis
uv run python -m json.tool examples/example.json >/dev/null
uv run python -m json.tool examples/openreview_comments_minimal.json >/dev/null
uv run python scripts/run_openrouter.py --input examples/example.json --output outputs/validate_openrouter.jsonl --model dummy --validate-only
uv run python scripts/run_gemini.py --input examples/example.json --output outputs/validate_gemini.jsonl --validate-only
uv run python scripts/run_vllm.py --input examples/example.json --output outputs/validate_vllm.jsonl --model-path dummy --validate-only
uv run python scripts/clean_openreview.py \
  --input examples/openreview_comments_minimal.json \
  --output outputs/openreview_conversations.json \
  --forum-id forum_example
```

Generated files go under `outputs/` and can be removed with `make clean`.

## Tier 2: dataset inspection

```bash
uv run hf download jiataoli/ai-reviewer-diagnostic-data \
  --repo-type dataset \
  --local-dir ai-reviewer-diagnostic-data
uv run python scripts/summarize_release_data.py --data-dir ai-reviewer-diagnostic-data/data --top-n 5
```

This checks the released artifact tree without pandas or model dependencies.

## Tier 3: diagnostic toolkit workflow for a new review system

Export your system's outputs on baseline inputs and paired perturbed inputs as JSONL with shared `id` values. At minimum, include one numeric score field or one decision field:

```json
{"id":"paper_001","overall_score":8,"soundness_score":4,"final_decision":"Accept as Poster"}
```

Then compare the pair:

```bash
uv run ai-reviewer-diagnostics \
  --baseline outputs/my_system_baseline.jsonl \
  --perturbed outputs/my_system_soundness_perturbed.jsonl \
  --condition paper/soundness \
  --output-md reports/my_system_soundness_report.md \
  --output-json reports/my_system_soundness_report.json
```

If you export files using the released score-artifact naming convention, use directory mode:

```bash
uv run ai-reviewer-diagnostics \
  --scores-dir ai-reviewer-diagnostic-data/data/annotation_scores \
  --output-md reports/released_scores_report.md
```

## Tier 4: model/API inference

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

Local vLLM:

```bash
uv sync --extra vllm
uv run python scripts/run_vllm.py \
  --input examples/example.json \
  --output outputs/vllm_outputs.jsonl \
  --model-path Qwen/Qwen2.5-72B-Instruct \
  --tensor-parallel-size 8 \
  --limit 1
```

## Tier 5: analysis

```bash
uv sync --extra analysis
uv run python scripts/summarize_release_data.py --data-dir ai-reviewer-diagnostic-data/data
```

Then use `analysis/` scripts on the downloaded annotation-score artifacts. Treat `ai-reviewer-diagnostic-data/data/annotation_scores/` as the canonical input directory and write new outputs under `outputs/analysis/`.

## Current release guarantees

The release has been checked for:

- zero-dependency quickstart;
- Python syntax validity in `scripts/` and `analysis/`;
- JSON validity for example inputs;
- API-free validation paths for OpenRouter, Gemini, and vLLM runners;
- a working toy diagnostic-report path for paired baseline/perturbed system outputs;
- a working OpenReview-cleaner smoke test on `examples/openreview_comments_minimal.json`;
- no obvious hard-coded API keys or local machine paths in text files;
- no tracked ACM PDF copy; `paper/README.md` links to the official DOI/PDF;
- curated prompt JSONL files are included; private Word prompt drafts and raw review/rebuttal samples are excluded from the public package;
- SHA256 checksums for the Hugging Face dataset artifacts via `dataset_manifest.csv`.

## Known limits

- The dataset is hosted separately on Hugging Face; treat the dataset card as canonical for dataset terms, usage notes, and version history.
- Remaining legacy analysis scripts are preserved from the experiment workflow and are not all fully parameterized CLIs; `ai-reviewer-diagnostics` is the public entry point for evaluating new system outputs.
- Formal artifact-evaluation reproduction would need exact model versions, prompt versions, source snapshots, and expected outputs for every table/figure.
