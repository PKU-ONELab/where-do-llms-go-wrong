# Examples

Tiny fixtures for quickstarts, smoke tests, and CLI demos. They are schema examples, not benchmark data.

| File | Used by |
| --- | --- |
| `example.json` | API/local inference runners in `--validate-only` mode |
| `openreview_comments_minimal.json` | `scripts/clean_openreview.py` smoke test |
| `system_outputs_baseline.jsonl` | diagnostic report demo |
| `system_outputs_perturbed_soundness.jsonl` | diagnostic report demo |

Run:

```bash
make quickstart
make demo-report
```

For real evaluation, run your review system on HF `content_pairs` rows and export JSONL outputs with shared `id` values plus score/decision fields. See [`../docs/INTEGRATIONS.md`](../docs/INTEGRATIONS.md).
