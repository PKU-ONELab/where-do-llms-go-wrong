# Scripts

Small CLIs and wrappers used by the release. Generated outputs should go under `outputs/`.

## First commands

```bash
python scripts/quickstart.py
python -m ai_reviewer_diagnostics.report --demo --output-md outputs/demo.md
python scripts/summarize_release_data.py --data-dir ai-reviewer-diagnostic-data/data
```

## Script map

| Script | Purpose |
| --- | --- |
| `quickstart.py` | zero-dependency repo/schema/prompt sanity check |
| `summarize_release_data.py` | counts files, sizes, JSONL rows, and sample keys in a downloaded HF dataset |
| `clean_openreview.py` | converts a minimal OpenReview comments export into conversation JSON |
| `run_openrouter.py` | OpenAI-compatible/OpenRouter batch inference |
| `run_gemini.py` | Gemini batch inference |
| `run_vllm.py` | optional local vLLM batch inference |
| `generate_diagnostic_report.py` | backwards-compatible wrapper around `ai-reviewer-diagnostics` |

## Diagnostic report

```bash
ai-reviewer-diagnostics   --baseline examples/system_outputs_baseline.jsonl   --perturbed examples/system_outputs_perturbed_soundness.jsonl   --condition paper/soundness   --output-md outputs/demo_diagnostic_report.md
```

Directory mode for released score artifacts:

```bash
ai-reviewer-diagnostics   --scores-dir ai-reviewer-diagnostic-data/data/annotation_scores   --output-md outputs/released_scores_report.md
```

## Inference wrappers

```bash
export OPENROUTER_API_KEY=...
python scripts/run_openrouter.py --input examples/example.json --output outputs/openrouter.jsonl --model <model> --api-key-env OPENROUTER_API_KEY

export GEMINI_API_KEY=...
python scripts/run_gemini.py --input examples/example.json --output outputs/gemini.jsonl --model gemini-2.0-flash

python scripts/run_vllm.py --input examples/example.json --output outputs/vllm.jsonl --model-path <hf-or-local-model>
```

All runners support validation/dry-run style checks used by `make smoke-test`; run `--help` on a script for exact flags.
