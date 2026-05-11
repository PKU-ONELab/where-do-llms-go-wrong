# Data

Large artifacts are hosted on Hugging Face, not committed to GitHub:

https://huggingface.co/datasets/leejamesssss/ai-reviewer-diagnostic-data

Quick use:

```bash
hf download leejamesssss/ai-reviewer-diagnostic-data   --repo-type dataset   --local-dir ai-reviewer-diagnostic-data
python scripts/summarize_release_data.py --data-dir ai-reviewer-diagnostic-data/data
```

Use `data/content_pairs/*.jsonl` first. Each row has `id`, `source`, `aspect`, `content_before`, and `content_after`. Released score artifacts live under `data/annotation_scores/` for reproduction/audit work.

See [`../docs/DATA.md`](../docs/DATA.md) and the HF dataset card for schema, manifest, rights, and citation notes.
