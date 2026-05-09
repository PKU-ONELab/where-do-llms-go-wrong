# Data Documentation

The data artifacts live in the companion Hugging Face dataset, not in this GitHub repository:

```text
https://huggingface.co/datasets/jiataoli/ai-reviewer-diagnostic-data
```

They support the paper **Where Do LLMs Go Wrong? Diagnosing Automated Peer Review via Aspect-Guided Multi-Level Perturbation**.

## Download

```bash
uv run hf download jiataoli/ai-reviewer-diagnostic-data \
  --repo-type dataset \
  --local-dir ai-reviewer-diagnostic-data
```

## Directory structure

```text
data/
  annotation_scores/
    baseline__target-<review_type>__prompt-<prompt_setting>.jsonl
    perturbed__source-<source>__aspect-<aspect>__target-<review_type>__prompt-<prompt_setting>.jsonl
    summary__review-difference__sheet-*.csv
  perturbed_contents/
    content__source-<source>__aspect-<aspect>.jsonl
    summary__review-rebuttal-counts.csv

dataset_manifest.csv        # path, size_bytes, sha256
dataset_manifest_summary.json
```

## Naming glossary

Public filenames use a consistent `key-value` convention separated by double underscores:

```text
baseline__target-<review_type>__prompt-<prompt_setting>.jsonl
perturbed__source-<source>__aspect-<aspect>__target-<review_type>__prompt-<prompt_setting>.jsonl
content__source-<source>__aspect-<aspect>.jsonl
summary__<table-name>.csv
```

Where:

- `<source>` is usually `paper`, `review`, or `rebuttal`.
- `<aspect>` is the perturbed dimension, e.g. `soundness`, `presentation`, `contribution`, `tone`, `factual`, `conclusion`, or `completeness`.
- `<review_type>` is `review` or `meta-review`.
- `<prompt_setting>` is a prompt condition such as `template`, `dimension`, `none`, or `template-dimension`.

The original experiment filenames are kept out of the public release. Public files use cleaner names instead of internal run prefixes and sample-size markers.

## Common fields

`annotation_scores/*.jsonl` commonly contains:

| Field | Meaning |
| --- | --- |
| `id` | Example identifier for aligning baseline and perturbed artifacts. |
| `overall_score` | Overall predicted/extracted review score. |
| `soundness_score` | Aspect score for soundness, when present. |
| `presentation_score` | Aspect score for presentation, when present. |
| `contribution_score` | Aspect score for contribution, when present. |
| `final_decision` | Final decision label, when present. |

`perturbed_contents/*.jsonl` generally contains an `id` plus the paper, review, or rebuttal content used in the experiments. Some content files are byte-identical across aspect names because the same source content was reused across multiple aspect-level scoring conditions; the condition-specific filenames are retained for direct alignment with the original experiment outputs.

`*.csv` files are compact tabular summaries converted from spreadsheet artifacts for easier reuse.

## Quick inspection

```bash
uv run python scripts/summarize_release_data.py --data-dir ai-reviewer-diagnostic-data/data
```

This prints file counts, total size, JSONL row counts, sample JSON keys, and largest files without requiring pandas or other analysis dependencies.

## Toolkit use with a new review system

The diagnostic dataset is designed for black-box testing. A new system should produce JSONL outputs with the same `id` values as the baseline/perturbed inputs and with score/decision fields such as `overall_score`, `soundness_score`, or `final_decision`.

```json
{"id":"paper_001","overall_score":8,"soundness_score":4,"final_decision":"Accept as Poster"}
```

Then compare baseline and perturbed outputs with:

```bash
uv run ai-reviewer-diagnostics \
  --baseline outputs/my_system_baseline.jsonl \
  --perturbed outputs/my_system_soundness_perturbed.jsonl \
  --condition paper/soundness \
  --output-md reports/my_system_soundness_report.md
```

For files following the public naming convention in `annotation_scores/`, directory mode discovers matching baseline/perturbed pairs automatically:

```bash
uv run ai-reviewer-diagnostics \
  --scores-dir ai-reviewer-diagnostic-data/data/annotation_scores \
  --output-md reports/released_scores_report.md
```

## Data rights and license

The code repository is MIT licensed. Dataset artifacts are distributed through the Hugging Face dataset card, which should be treated as the canonical place for dataset terms, usage notes, and version history.

## Handling notes

- Do not add raw private review dumps, local OpenReview exports, API keys, or local filesystem paths.
- Keep executable analysis scripts in `analysis/`; data directories should contain data artifacts, not duplicate code.
- If data is regenerated, document the exact source snapshot and generation command in `docs/REPRODUCIBILITY.md`.
