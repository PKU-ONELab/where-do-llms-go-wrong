# Release Manifest

This manifest summarizes the public code-release candidate. It does not make legal, licensing, or data-rights determinations for the companion dataset.

## Paper

**Where Do LLMs Go Wrong? Diagnosing Automated Peer Review via Aspect-Guided Multi-Level Perturbation**  
Jiatao Li, Yanheng Li, Xinyu Hu, Mingqi Gao, Xiaojun Wan. CIKM 2025.  
DOI: https://doi.org/10.1145/3746252.3761274

## Top-level files

- `README.md`: front-page overview, quickstart, usage commands, and BibTeX citation.
- `Makefile`: convenience commands, including `make smoke-test` and `make summarize-data`.
- `requirements.txt`: compatibility install file for core runtime dependencies.
- `requirements-core.txt`: dependencies for API-based inference and Hugging Face download helpers.
- `requirements-analysis.txt`: dependencies for analysis scripts.
- `requirements-vllm.txt`: optional local vLLM dependencies.
- `CITATION.cff`: machine-readable GitHub citation metadata.
- `CITATION.bib`: BibTeX citation for the CIKM 2025 paper.
- `LICENSE`: MIT license for repository code.

## Directories

- `scripts/`: runnable inference, preprocessing, and data-summary CLIs.
- `analysis/`: analysis scripts for annotation score artifacts.
- `examples/`: small runnable example inputs for README commands.
- `docs/`: getting-started, data, and reproducibility notes.
- `prompts/`: prompt JSONL files and original prompt documents.
- `data/`: pointer to the external Hugging Face dataset.
- `paper/`: paper citation pointer and included PDF, subject to final publisher-rights check before public release.
- `.github/workflows/`: API-free smoke-test workflow for GitHub Actions.

## Companion dataset

Dataset URL:

```text
https://huggingface.co/datasets/jiataoli/ai-reviewer-diagnostic-data
```

Local dataset staging folder in this workspace:

```text
../HuggingFace-Dataset
```

It contains:

- `README.md`: Hugging Face dataset card.
- `.gitattributes`: Git LFS patterns.
- `dataset_manifest.csv`: file path, size, and SHA256 for each data artifact.
- `dataset_manifest_summary.json`: file count and total byte size.
- `data/annotation_scores/` and `data/perturbed_contents/`.

## User-facing first commands

```bash
make smoke-test
hf download jiataoli/ai-reviewer-diagnostic-data --repo-type dataset --local-dir ai-reviewer-diagnostic-data
make summarize-data DATA_DIR=ai-reviewer-diagnostic-data/data
```

Equivalent direct commands:

```bash
python scripts/summarize_release_data.py --data-dir ai-reviewer-diagnostic-data/data
python scripts/clean_openreview.py --input examples/openreview_comments_minimal.json --output outputs/openreview_conversations.json --forum-id forum_example --print-text
```

## Remaining public-release decisions

- Confirm redistribution rights and usage constraints for all files under the Hugging Face dataset, `prompts/original_prompts/`, and `paper/`.
- Confirm whether the included ACM paper PDF may be redistributed from GitHub; otherwise replace it with DOI/ACM/arXiv links only.
- If full artifact-evaluation reproduction is required, parameterize the remaining analysis scripts and add expected-output fixtures for every table/figure.
