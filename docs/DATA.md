# Data Documentation

This repository includes selected release artifacts under:

```text
<HF_DATASET_REPO>/data/
```

The artifacts support the paper **Where Do LLMs Go Wrong? Diagnosing Automated Peer Review via Aspect-Guided Multi-Level Perturbation**.

## Directory structure

```text
data/
  annotation_scores/
    *.jsonl                 # scored baseline/perturbed model outputs
    *.xlsx                  # compact score/count tables
    *.pdf, *.png            # generated figures
    *.txt                   # printed summary outputs
    pie_charts/             # decision-distribution plots
    transition_matrices/    # transition-matrix visualizations
  perturbed_contents/
    *.jsonl                 # perturbed paper/review/rebuttal contents
    *.xlsx                  # count summaries
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
- `<n>` is the approximate sample size used in the file naming from the original experiments.

## Quick inspection

```bash
python scripts/summarize_release_data.py --data-dir ../HuggingFace-Dataset/data
```

This prints file counts, total size, JSONL row counts, sample JSON keys, and largest files without requiring pandas or other analysis dependencies.

## Data-rights and release status

TODO: Confirm the data-rights status before public release. This document does not make any legal, privacy, licensing, or data-use determination.

TODO: Verify whether every JSONL, XLSX, PDF, PNG, TXT, prompt-derived artifact, and paper artifact may be redistributed publicly under the final repository license or whether separate terms apply.

TODO: Add final data provenance, collection dates, source terms, filtering criteria, anonymization/sanitization notes, and required attribution once those facts are confirmed.

## Handling notes

- Do not add raw private review dumps, local OpenReview exports, API keys, or local filesystem paths.
- Keep executable analysis scripts in `analysis/`; data directories should contain data artifacts, not duplicate code.
- If data is regenerated, document the exact source snapshot and generation command in `docs/REPRODUCIBILITY.md`.
- If public redistribution is uncertain, consider hosting only code/prompts first and moving data to a controlled release asset after rights review.
