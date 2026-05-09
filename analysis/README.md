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

- `acceptance_ratio_analysis.py`: acceptance-ratio and decision-distribution analysis.
- `hypothesis_tests_proportional_decision.py`: hypothesis tests with final decisions mapped to acceptance-rate proportions.
- `hypothesis_tests_ordinal_decision.py`: hypothesis tests with final decisions mapped to ordinal labels.
- `hypothesis_tests_ordinal_with_agreement.py`: extended ordinal-decision tests with agreement metrics.

The old print-only variants were intentionally removed because they duplicated the same tests with only extra p-value formatting.

## Usage note

The analysis scripts are preserved from the original experiment workflow. They expect to be run from, or pointed at, the directory containing the relevant JSONL score files. The most immediately reusable utility for new users is:

```bash
uv run python scripts/summarize_release_data.py --data-dir ai-reviewer-diagnostic-data/data
```

For exact reproduction, see `docs/REPRODUCIBILITY.md`. For new analysis work, prefer treating `ai-reviewer-diagnostic-data/data/annotation_scores/` as the canonical input directory and writing fresh outputs under `outputs/analysis/`. The analysis loaders support the public dataset filenames (`baseline__...`, `perturbed__...`) and the original experiment filenames for backward compatibility.
