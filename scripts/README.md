# Scripts

Reusable command-line tools for quickstart validation, inference, preprocessing, diagnostic report generation, and data inspection.

## Fast path

```bash
make quickstart
make demo-report
make smoke-test
```

`make quickstart` is zero-dependency. `make demo-report` demonstrates the diagnostic-toolkit path on toy paired outputs. `make smoke-test` requires the core dependencies from `pyproject.toml` and validates every runner without API/model calls.

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

## Installed CLI

After pip install, the package exposes:

```bash
ai-reviewer-diagnostics --help
ai-reviewer-report --help
ai-reviewer-diagnostics --demo --output-md outputs/demo_diagnostic_report.md
```

For integrating a new system, see [`docs/INTEGRATIONS.md`](../docs/INTEGRATIONS.md).

## Output format for diagnostic reports

`ai-reviewer-diagnostics` compares paired baseline/perturbed outputs from any automated review system. Each JSONL row must contain a shared `id`; score and decision fields are configurable.

```json
{"id":"paper_001","overall_score":8,"contribution_score":4,"soundness_score":4,"presentation_score":4,"final_decision":"Accept as Poster"}
```

Default compared score fields are `overall_score`, `contribution_score`, `soundness_score`, and `presentation_score`; default decision field is `final_decision`.

## `quickstart.py`

Zero-dependency release-health check.

```bash
uv run python scripts/quickstart.py
```

It validates required files, example schemas, prompt JSONL files, and citation metadata, then writes `outputs/quickstart/quickstart_summary.json`.

## `ai-reviewer-diagnostics`

Pip-installable, dependency-free diagnostic report generator for new or existing automated-review-system outputs. The legacy wrapper `scripts/generate_diagnostic_report.py` imports this package entry point for backward compatibility.

Explicit pair mode:

```bash
uv run ai-reviewer-diagnostics \
  --baseline examples/system_outputs_baseline.jsonl \
  --perturbed examples/system_outputs_perturbed_soundness.jsonl \
  --condition paper/soundness \
  --output-md outputs/demo_diagnostic_report.md \
  --output-json outputs/demo_diagnostic_report.json
```

Directory mode for files following the public dataset naming convention:

```bash
uv run ai-reviewer-diagnostics \
  --scores-dir ai-reviewer-diagnostic-data/data/annotation_scores \
  --output-md reports/released_scores_report.md
```

The markdown report includes score deltas, mean absolute shifts, decision-change rates, and top decision transitions. Use this when evaluating a new review system against the released paired perturbation benchmark.

## `run_openrouter.py`

OpenAI-compatible API runner. Works with OpenAI-style endpoints such as OpenRouter.

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

## `run_gemini.py`

Gemini API runner.

```bash
export GEMINI_API_KEY=***
uv run python scripts/run_gemini.py \
  --input examples/example.json \
  --output outputs/gemini_outputs.jsonl \
  --model gemini-2.0-flash \
  --limit 1
```

## `run_vllm.py`

Optional local inference through vLLM. Install the `vllm` optional dependency group only in a CUDA/PyTorch-compatible environment.

```bash
uv run python scripts/run_vllm.py \
  --input examples/example.json \
  --output outputs/vllm_outputs.jsonl \
  --model-path Qwen/Qwen2.5-72B-Instruct \
  --tensor-parallel-size 8 \
  --limit 1
```

## `clean_openreview.py`

Extracts official-review and author-response conversations from an OpenReview comments JSON export.

```bash
uv run python scripts/clean_openreview.py \
  --input examples/openreview_comments_minimal.json \
  --output outputs/openreview_conversations.json \
  --forum-id forum_example \
  --print-text
```

## `summarize_release_data.py`

No-dependency data inventory helper. Download the Hugging Face dataset first:

```bash
uv run hf download jiataoli/ai-reviewer-diagnostic-data \
  --repo-type dataset \
  --local-dir ai-reviewer-diagnostic-data
uv run python scripts/summarize_release_data.py --data-dir ai-reviewer-diagnostic-data/data
```
