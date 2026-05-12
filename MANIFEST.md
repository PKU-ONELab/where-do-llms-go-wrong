# Release Manifest

This manifest summarizes the public-facing code release. It does not make legal, licensing, or data-rights determinations for the companion dataset.

## Paper

**Where Do LLMs Go Wrong? Diagnosing Automated Peer Review via Aspect-Guided Multi-Level Perturbation**  
Jiatao Li, Yanheng Li, Xinyu Hu, Mingqi Gao, Xiaojun Wan. CIKM 2025.  
DOI: https://doi.org/10.1145/3746252.3761274

## Top-level files

- `README.md`: front-page overview, quickstart, usage commands, and BibTeX citation.
- `Makefile`: convenience commands, including `make quickstart`, `make demo-report`, `make smoke-test`, and `make summarize-data`.
- `pyproject.toml`: package metadata, console scripts, and single dependency entry point for uv and pip-compatible installs.
- `CITATION.cff`: machine-readable GitHub citation metadata.
- `CITATION.bib`: BibTeX citation for the CIKM 2025 paper.
- `LICENSE`: MIT license for repository code.
- `CONTRIBUTING.md`: community contribution guide for bugs, integrations, metrics, and PR checks.

## Directories

- `ai_reviewer_diagnostics/`: pip-installable diagnostic report package exposed as `ai-reviewer-diagnostics` and `ai-reviewer-report`.
- `scripts/`: wrappers and reusable CLIs for quickstart, inference, preprocessing, and data summary.
- `analysis/`: analysis scripts for annotation score artifacts.
- `examples/`: small runnable example inputs for quickstart, smoke-test, and toy diagnostic-report commands.
- `docs/`: getting-started, data, integration, reproducibility notes, and README teaser assets.
- `prompts/`: curated prompt JSONL files. Private working drafts, raw review/rebuttal samples, and Word-document prompt experiments are excluded from the public package.
- `data/`: pointer to the external Hugging Face dataset.
- `paper/`: paper citation pointer and official ACM DOI/PDF links. The ACM PDF is not redistributed in this repository.
- `.github/workflows/`: API-free smoke-test workflow for GitHub Actions.
- `.github/ISSUE_TEMPLATE/` and `.github/PULL_REQUEST_TEMPLATE.md`: community templates for bugs, integration requests, metric ideas, and PRs.

## Companion dataset

Dataset URL:

```text
https://huggingface.co/datasets/PKU-ONELab/ai-reviewer-diagnostic-data
```

It contains:

- `README.md`: Hugging Face dataset card.
- `.gitattributes`: Git LFS patterns.
- `dataset_manifest.csv`: file path, size, and SHA256 for each data artifact.
- `dataset_manifest_summary.json`: file count and total byte size.
- `data/content_pairs/` and `data/annotation_scores/`. The redundant perturbed-only view is intentionally excluded because `content_pairs.content_after` is canonical.

## User-facing first commands

```bash
python -m pip install ai-reviewer-diagnostics
ai-reviewer-diagnostics --demo --output-md outputs/demo_diagnostic_report.md
make quickstart
make demo-report
python -m pip install -e .
ai-reviewer-diagnostics --help
uv sync
uv run make smoke-test
uv run hf download PKU-ONELab/ai-reviewer-diagnostic-data --repo-type dataset --local-dir ai-reviewer-diagnostic-data
make summarize-data DATA_DIR=ai-reviewer-diagnostic-data/data
```

Equivalent direct commands:

```bash
uv run python scripts/quickstart.py
uv run ai-reviewer-diagnostics --baseline examples/system_outputs_baseline.jsonl --perturbed examples/system_outputs_perturbed_soundness.jsonl --condition paper/soundness --output-md outputs/demo_diagnostic_report.md
uv run python scripts/summarize_release_data.py --data-dir ai-reviewer-diagnostic-data/data
uv run python scripts/clean_openreview.py --input examples/openreview_comments_minimal.json --output outputs/openreview_conversations.json --forum-id forum_example --print-text
```

## Reuse and citation affordances

- Citation appears near the top of `README.md` and in both `CITATION.bib` and `CITATION.cff`.
- `make quickstart` works before dependency installation.
- `examples/` contains tiny schema fixtures rather than private benchmark data.
- The `ai-reviewer-diagnostics` package gives a public entry point for black-box review-system evaluation: baseline outputs plus paired perturbed outputs in, markdown/JSON diagnostic report out.
- `docs/INTEGRATIONS.md`, `scripts/README.md`, `analysis/README.md`, `prompts/README.md`, and `docs/` describe how to reuse each subsystem.
- Generated outputs are ignored and removable with `make clean`.
- Community-facing issue and PR templates guide users toward reproducible bug reports and useful integration requests.

## Maintenance notes

- Keep dataset redistribution wording and usage constraints in the Hugging Face dataset card rather than duplicating them here.
- If full artifact-evaluation reproduction is required, parameterize the remaining analysis scripts and add expected-output fixtures for every table/figure.
