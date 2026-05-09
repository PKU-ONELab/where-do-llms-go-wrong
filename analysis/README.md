# Analysis Scripts

These scripts support analysis of the annotation-score artifacts in the companion Hugging Face dataset:

```text
https://huggingface.co/datasets/jiataoli/ai-reviewer-diagnostic-data
```

Download the dataset first:

```bash
uv run hf download jiataoli/ai-reviewer-diagnostic-data \
  --repo-type dataset \
  --local-dir ai-reviewer-diagnostic-data
```

Install analysis dependencies:

```bash
uv sync --extra analysis
```

## Files

- `acc_ratio.py`: acceptance-ratio and decision-distribution analysis.
- `hyp_test_proportion_gap.py`: proportion-gap hypothesis tests.
- `hyp_test_proportion_gap_print.py`: print-oriented variant of proportion-gap tests.
- `hyp_test_simple_gap.py`: simple-gap hypothesis tests.
- `hyp_test_simple_gap_V2.py`: extended simple-gap analysis with agreement metrics.
- `hyp_test_simple_gap_V2_print.py`: print-oriented variant of the extended analysis.

## Usage note

The analysis scripts are preserved from the original experiment workflow. They expect to be run from, or pointed at, the directory containing the relevant JSONL score files. The most immediately reusable utility for new users is:

```bash
uv run python scripts/summarize_release_data.py --data-dir ai-reviewer-diagnostic-data/data
```

For exact reproduction, see `docs/REPRODUCIBILITY.md`. For new analysis work, prefer treating `ai-reviewer-diagnostic-data/data/annotation_scores/` as the canonical input directory and writing fresh outputs under `outputs/analysis/`.
