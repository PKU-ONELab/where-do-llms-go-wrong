# Analysis

Scripts for inspecting released score artifacts and reproducing paper-style tables/figures. The main inputs are downloaded from Hugging Face:

```bash
hf download PKU-ONELab/ai-reviewer-diagnostic-data   --repo-type dataset   --local-dir ai-reviewer-diagnostic-data
```

Typical path:

```bash
uv sync --extra analysis
python scripts/summarize_release_data.py --data-dir ai-reviewer-diagnostic-data/data
```

Use `ai-reviewer-diagnostic-data/data/annotation_scores/` as the canonical input for released scoring outputs. Keep generated figures/tables under `outputs/analysis/` so they stay out of Git.

For the full tiered reproduction path, see [`../docs/REPRODUCIBILITY.md`](../docs/REPRODUCIBILITY.md).
