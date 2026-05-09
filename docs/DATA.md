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
    *.jsonl                 # scored baseline/perturbed model outputs
    *.csv                   # compact score tables converted from spreadsheets
  perturbed_contents/
    *.jsonl                 # paper/review/rebuttal contents used by the experiments
    *.csv                   # compact count summaries converted from spreadsheets
dataset_manifest.csv        # path, size_bytes, sha256
dataset_manifest_summary.json
```

## Naming glossary

Most generated JSONL filenames encode the experiment condition:

```text
output_test_base_input_<review_type>_<prompt_setting>_overall_<n>_out.jsonl
test_<source>_<aspect>_perturbed_<review_type>_<prompt_setting>_overall_<n>.jsonl
Perturbed_sampled_<source>_<n>_perturb_<aspect>.jsonl
```

Where:

- `<source>` is usually `paper`, `review`, or `rebuttal`.
- `<aspect>` is the perturbed dimension, e.g. `soundness`, `presentation`, `contribution`, `tone`, `factual`, `conclusion`, or `completeness`.
- `<review_type>` is `review` or `meta-review`.
- `<prompt_setting>` is a prompt condition such as `template`, `dimension`, or `none`.
- `<n>` is the sample-size marker inherited from original experiment filenames. Some files with `517` in the name contain 508 rows after filtering/alignment; this is expected for the released artifacts.

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

## Data rights and license

The code repository is MIT licensed. Dataset artifacts are distributed through the Hugging Face dataset card, which should be treated as the canonical place for dataset terms, usage notes, and version history.

## Handling notes

- Do not add raw private review dumps, local OpenReview exports, API keys, or local filesystem paths.
- Keep executable analysis scripts in `analysis/`; data directories should contain data artifacts, not duplicate code.
- If data is regenerated, document the exact source snapshot and generation command in `docs/REPRODUCIBILITY.md`.
