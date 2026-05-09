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

## 2. Generate a toy diagnostic report

This demonstrates the central toolkit workflow without API keys or the companion dataset.

```bash
make demo-report
```

It compares `examples/system_outputs_baseline.jsonl` against `examples/system_outputs_perturbed_soundness.jsonl` and writes:

```text
outputs/demo_diagnostic_report.md
outputs/demo_diagnostic_report.json
```

Package-first equivalent:

```bash
python -m pip install "git+https://github.com/JiataoLi/where-do-llms-go-wrong.git"
ai-reviewer-diagnostics --demo --output-md outputs/demo_diagnostic_report.md
```

Expected package demo output:

```text
Compared 1 condition pair(s).
Wrote outputs/demo_diagnostic_report.md
```

For your own automated review system, export outputs with a shared `id` field plus score/decision fields:

```json
{"id":"paper_001","overall_score":8,"soundness_score":4,"final_decision":"Accept as Poster"}
```

Then run:

```bash
ai-reviewer-diagnostics \
  --baseline outputs/my_system_baseline.jsonl \
  --perturbed outputs/my_system_soundness_perturbed.jsonl \
  --condition paper/soundness \
  --output-md reports/my_system_soundness_report.md
```

## 3. Install lightweight dependencies

Dependencies live in `pyproject.toml`; `uv` is the recommended installer.

```bash
uv sync
```

Editable pip install for local development:

```bash
python -m pip install -e .
ai-reviewer-diagnostics --help
```

## 4. API-free smoke test

```bash
uv run make smoke-test
```

This compiles Python files, validates example inputs, checks that all inference runners can validate inputs without API/model calls, runs the diagnostic report demo, and runs the OpenReview-cleaner fixture.

## 5. Download and inspect the data

```bash
uv run hf download jiataoli/ai-reviewer-diagnostic-data \
  --repo-type dataset \
  --local-dir ai-reviewer-diagnostic-data
uv run python scripts/summarize_release_data.py --data-dir ai-reviewer-diagnostic-data/data
```

The summary prints file counts, artifact size, file types, JSONL row counts, sample keys, and largest files.

## 6. Evaluate released score artifacts in directory mode

If you download the Hugging Face dataset, the report generator can discover baseline/perturbed score pairs by filename:

```bash
uv run ai-reviewer-diagnostics \
  --scores-dir ai-reviewer-diagnostic-data/data/annotation_scores \
  --output-md reports/released_scores_report.md
```

This is also the pattern to follow for a new review system if you export its outputs using the same `baseline__...jsonl` and `perturbed__...jsonl` naming convention.

## 7. Run one model call

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

## 8. Use the OpenReview cleaner

```bash
uv run python scripts/clean_openreview.py \
  --input examples/openreview_comments_minimal.json \
  --output outputs/openreview_conversations.json \
  --forum-id forum_example \
  --print-text
```

## 9. Cite the work

Use `CITATION.bib`, `CITATION.cff`, or the BibTeX block in `README.md`. The DOI is:

```text
https://doi.org/10.1145/3746252.3761274
```

## Where to look next

- Need to evaluate a new review system? Start with [`docs/INTEGRATIONS.md`](INTEGRATIONS.md), the `ai-reviewer-diagnostics` CLI, and the example system-output JSONL files.
- Need prompts? Start with `prompts/base_prompt.jsonl` and `prompts/perturb_prompt.jsonl`.
- Need generated experiment artifacts? Download the Hugging Face dataset.
- Need script examples? Read `scripts/README.md`.
- Need analysis scripts? Start with `analysis/README.md`.
- Need reproduction limits and tiers? Read `docs/REPRODUCIBILITY.md`.
