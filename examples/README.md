# Examples

Tiny examples that make the repository runnable immediately after cloning.

## Files

- `example.json`: one chat-style prompt batch for API/local-LLM runners.
- `openreview_comments_minimal.json`: minimal OpenReview-style notes used by `scripts/clean_openreview.py`.
- `system_outputs_baseline.jsonl`: toy baseline scores/decisions from a hypothetical review system.
- `system_outputs_perturbed_soundness.jsonl`: paired toy outputs for a soundness-perturbed condition.

These fixtures are schema demonstrations, not benchmark data. They exist so new users can validate the code path without API keys, GPUs, or the companion dataset.

## Fast checks

```bash
make quickstart
make demo-report
make smoke-test
```

`make demo-report` writes `outputs/demo_diagnostic_report.md` and demonstrates the core toolkit workflow: compare a system's baseline outputs against paired perturbed outputs, then summarize score/decision shifts.

## Input schema for inference runners

The model runners expect a JSON list of chat-message lists:

```json
[
  [
    {"role": "system", "content": "You are a concise academic-review assistant."},
    {"role": "user", "content": "Summarize the review."}
  ]
]
```

Use `--validate-only` with any runner to check the schema without calling an API or loading a local model.

## Output schema for diagnostic reports

`ai-reviewer-diagnostics` expects JSONL rows with a shared `id` plus any score/decision fields you want to compare:

```json
{"id":"paper_001","overall_score":8,"soundness_score":4,"final_decision":"Accept as Poster"}
```

Run the toy report directly from a checkout, or use `ai-reviewer-diagnostics --demo` after pip install because the package bundles matching demo fixtures.


```bash
ai-reviewer-diagnostics \
  --baseline examples/system_outputs_baseline.jsonl \
  --perturbed examples/system_outputs_perturbed_soundness.jsonl \
  --condition paper/soundness \
  --output-md outputs/demo_diagnostic_report.md
```
