# Data

The full release artifacts are hosted as a separate Hugging Face dataset, not committed directly to this GitHub code repository.

```text
https://huggingface.co/datasets/jiataoli/ai-reviewer-diagnostic-data
```

Download with the Hugging Face CLI:

```bash
hf download jiataoli/ai-reviewer-diagnostic-data \
  --repo-type dataset \
  --local-dir ai-reviewer-diagnostic-data
```

Then inspect it from this code repository:

```bash
python scripts/summarize_release_data.py --data-dir ai-reviewer-diagnostic-data/data
```

Keeping data on Hugging Face makes the GitHub repository lighter and gives the dataset its own card, citation, download statistics, and version history.
