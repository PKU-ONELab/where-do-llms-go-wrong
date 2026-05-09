# Release Manifest

This manifest summarizes the public-facing code release. It does not make legal, licensing, or data-rights determinations for the companion dataset.

## Paper

**Where Do LLMs Go Wrong? Diagnosing Automated Peer Review via Aspect-Guided Multi-Level Perturbation**  
Jiatao Li, Yanheng Li, Xinyu Hu, Mingqi Gao, Xiaojun Wan. CIKM 2025.  
DOI: https://doi.org/10.1145/3746252.3761274

## Top-level files

- `README.md`: front-page overview, quickstart, usage commands, and BibTeX citation.
- `Makefile`: convenience commands, including `make quickstart`, `make smoke-test`, and `make summarize-data`.
- `requirements.txt`: compatibility install file for core runtime dependencies.
- `requirements-core.txt`: dependencies for API-based inference and Hugging Face download helpers.
- `requirements-analysis.txt`: dependencies for analysis scripts.
- `requirements-vllm.txt`: optional local vLLM dependencies.
- `CITATION.cff`: machine-readable GitHub citation metadata.
- `CITATION.bib`: BibTeX citation for the CIKM 2025 paper.
- `LICENSE`: MIT license for repository code.

## Directories

- `scripts/`: reusable CLIs for quickstart, inference, preprocessing, and data summary.
- `analysis/`: analysis scripts for annotation score artifacts.
- `examples/`: small runnable example inputs for quickstart and smoke-test commands.
- `docs/`: getting-started, data, and reproducibility notes.
- `prompts/`: curated prompt JSONL files. Private working drafts, raw review/rebuttal samples, and Word-document prompt experiments are excluded from the public package.
- `data/`: pointer to the external Hugging Face dataset.
- `paper/`: paper citation pointer and official ACM DOI/PDF links. The ACM PDF is not redistributed in this repository.
- `.github/workflows/`: API-free smoke-test workflow for GitHub Actions.

## Companion dataset

Dataset URL:

```text
https://huggingface.co/datasets/jiataoli/ai-reviewer-diagnostic-data
```

It contains:

- `README.md`: Hugging Face dataset card.
- `.gitattributes`: Git LFS patterns.
- `dataset_manifest.csv`: file path, size, and SHA256 for each data artifact.
- `dataset_manifest_summary.json`: file count and total byte size.
- `data/annotation_scores/` and `data/perturbed_contents/`.

## User-facing first commands

```bash
make quickstart
pip install -r requirements-core.txt
make smoke-test
hf download jiataoli/ai-reviewer-diagnostic-data --repo-type dataset --local-dir ai-reviewer-diagnostic-data
make summarize-data DATA_DIR=ai-reviewer-diagnostic-data/data
```

Equivalent direct commands:

```bash
python scripts/quickstart.py
python scripts/summarize_release_data.py --data-dir ai-reviewer-diagnostic-data/data
python scripts/clean_openreview.py --input examples/openreview_comments_minimal.json --output outputs/openreview_conversations.json --forum-id forum_example --print-text
```

## Reuse and citation affordances

- Citation appears near the top of `README.md` and in both `CITATION.bib` and `CITATION.cff`.
- `make quickstart` works before dependency installation.
- `examples/` contains tiny schema fixtures rather than private benchmark data.
- `scripts/README.md`, `analysis/README.md`, `prompts/README.md`, and `docs/` describe how to reuse each subsystem.
- Generated outputs are ignored and removable with `make clean`.

## Remaining public-release decisions

- Confirm final redistribution wording and usage constraints on the Hugging Face dataset card before broad announcement.
- If full artifact-evaluation reproduction is required, parameterize the remaining analysis scripts and add expected-output fixtures for every table/figure.
