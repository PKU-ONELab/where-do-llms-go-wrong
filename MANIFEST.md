# Release Manifest

This manifest summarizes the repository contents and the known release-readiness TODOs. It does not make legal, licensing, or data-rights determinations.

## Paper

**Where Do LLMs Go Wrong? Diagnosing Automated Peer Review via Aspect-Guided Multi-Level Perturbation**  
Jiatao Li, Yanheng Li, Xinyu Hu, Mingqi Gao, Xiaojun Wan. CIKM 2025.  
DOI: https://doi.org/10.1145/3746252.3761274

## Top-level files

- `README.md`: front-page overview, quickstart, usage commands, and BibTeX citation.
- `Makefile`: convenience commands, including `make smoke-test` and `make summarize-data`.
- `requirements.txt`: compatibility install file for core runtime dependencies.
- `requirements-core.txt`: dependencies for API-based inference scripts.
- `requirements-analysis.txt`: dependencies for analysis scripts.
- `requirements-vllm.txt`: optional local vLLM dependencies.
- `CITATION.cff`: machine-readable GitHub citation metadata.
- `CITATION.bib`: BibTeX citation for the CIKM 2025 paper.
- `LICENSE_TODO.md`: license placeholder; replace before public archival release.

## Directories

- `scripts/`: runnable inference, preprocessing, and data-summary CLIs.
- `analysis/`: analysis scripts for annotation score artifacts.
- `examples/`: small runnable example inputs for README commands.
- `docs/`: getting-started, data, and reproducibility notes.
- `prompts/`: prompt JSONL files and original prompt documents.
- `../HuggingFace-Dataset/data/`: Hugging Face dataset release artifacts.
- `paper/`: paper PDF and citation pointer.

## User-facing entry points

Recommended first commands:

```bash
make smoke-test
make summarize-data
```

Equivalent direct commands:

```bash
python scripts/summarize_release_data.py --data-dir ../HuggingFace-Dataset/data
python scripts/clean_openreview.py --input examples/openreview_comments_minimal.json --output outputs/openreview_conversations.json --forum-id forum_example --print-text
```

## Known release TODOs

- TODO: Replace `LICENSE_TODO.md` with the final approved code license.
- TODO: Confirm redistribution rights and usage constraints for all files under `data/`, `prompts/original_prompts/`, and `paper/`.
- TODO: Replace `<REPO_URL>` and `<REPO_NAME>` placeholders in `README.md` once the public GitHub repository exists.
- TODO: Decide whether large generated artifacts should stay in Git, move to Git LFS, or be hosted on Hugging Face / Zenodo with checksums.
- TODO: Add final provenance, hashes, and expected outputs if the release becomes a formal artifact-evaluation package.
- TODO: Parameterize remaining analysis scripts if full end-to-end reproduction is required.
