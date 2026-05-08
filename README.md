# Where Do LLMs Go Wrong? Diagnosing Automated Peer Review

Code, prompts, and release artifacts for the CIKM 2025 paper:

> **Where Do LLMs Go Wrong? Diagnosing Automated Peer Review via Aspect-Guided Multi-Level Perturbation**  
> Jiatao Li, Yanheng Li, Xinyu Hu, Mingqi Gao, Xiaojun Wan. CIKM 2025.  
> DOI: https://doi.org/10.1145/3746252.3761274

This repository is designed to make the project easy to reuse and easy to cite. It includes:

- runnable API/local-LLM inference wrappers;
- prompt files for automated peer-review diagnosis;
- a prepared companion Hugging Face dataset folder for aspect-guided perturbation artifacts;
- analysis scripts for score/decision-change inspection;
- documentation for data provenance, reproducibility, and citation.

## Quick start

### 1. Clone and install the lightweight runner dependencies

```bash
git clone <REPO_URL>
cd <REPO_NAME>
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-core.txt
```

### 2. Run a one-example OpenAI-compatible smoke test

```bash
export OPENAI_API_KEY=your_key_here
python scripts/run_openrouter.py \
  --input examples/example.json \
  --output outputs/model_outputs.jsonl \
  --model mistralai/mistral-small-3.1-24b-instruct \
  --base-url https://openrouter.ai/api/v1 \
  --limit 1
```

The input format is a JSON list of chat-message lists:

```json
[
  [
    {"role": "system", "content": "You are a concise academic-review assistant."},
    {"role": "user", "content": "Summarize the main strengths and weaknesses of a paper submission in two short bullets."}
  ]
]
```

### 3. Inspect the companion Hugging Face dataset without installing heavy packages

```bash
python scripts/summarize_release_data.py --data-dir ../HuggingFace-Dataset/data
```

Expected output starts like this:

```text
Data directory: ../HuggingFace-Dataset/data
Files: 220
Total size: 265.32 MB
File types:
  .png: 167
  .jsonl: 43
```

### 4. Run the API-free smoke test

```bash
make smoke-test
```

This compiles Python files, validates example JSON, and runs the OpenReview-cleaner example. It creates `outputs/`, which is ignored by Git and can be removed with `make clean`.

### 5. Cite the paper

If this repository helps your work, please cite:

```bibtex
@inproceedings{li2025where,
  title     = {Where Do LLMs Go Wrong? Diagnosing Automated Peer Review via Aspect-Guided Multi-Level Perturbation},
  author    = {Li, Jiatao and Li, Yanheng and Hu, Xinyu and Gao, Mingqi and Wan, Xiaojun},
  booktitle = {Proceedings of the 34th ACM International Conference on Information and Knowledge Management (CIKM '25)},
  year      = {2025},
  publisher = {ACM},
  doi       = {10.1145/3746252.3761274}
}
```

A machine-readable citation is also provided in `CITATION.cff` and `CITATION.bib`.

## What is in this repository?

```text
scripts/              # runnable inference, preprocessing, and data-summary CLIs
analysis/             # analysis scripts for annotation-score artifacts
examples/             # tiny runnable examples used by README commands
prompts/              # JSONL prompts and original prompt documents
  base_prompt.jsonl
  perturb_prompt.jsonl
../HuggingFace-Dataset/data/ # local folder prepared for Hugging Face upload
  annotation_scores/  # scored model outputs, tables, figures, transition matrices
  perturbed_contents/ # perturbed paper/review/rebuttal JSONL artifacts
paper/CIKM.pdf        # paper copy
docs/                 # data/reproducibility/getting-started notes
```

For a fuller inventory, see `MANIFEST.md`.


## Data hosting choice

I recommend keeping GitHub for code/docs/prompts and Hugging Face for data. The local upload-ready dataset folder is:

```text
../HuggingFace-Dataset/
  README.md        # Hugging Face dataset card
  .gitattributes   # Git LFS patterns
  data/            # release artifacts
```

Recommended public dataset repo name:

```text
ai-reviewer-diagnostic-data
```

After the Hugging Face repo exists, replace `<HF_DATASET_REPO>` placeholders with:

```text
https://huggingface.co/datasets/<namespace>/ai-reviewer-diagnostic-data
```

## Common usage patterns

### OpenAI-compatible / OpenRouter inference

```bash
export OPENAI_API_KEY=your_key_here
python scripts/run_openrouter.py \
  --input examples/example.json \
  --output outputs/model_outputs.jsonl \
  --model mistralai/mistral-small-3.1-24b-instruct \
  --base-url https://openrouter.ai/api/v1 \
  --workers 8
```

### Gemini inference

```bash
pip install -r requirements-core.txt
export GEMINI_API_KEY=your_key_here
python scripts/run_gemini.py \
  --input examples/example.json \
  --output outputs/gemini_outputs.jsonl \
  --model gemini-2.0-flash \
  --workers 8
```

### Optional local vLLM inference

`vllm` is intentionally kept out of the default install because it depends on your CUDA/PyTorch/GPU setup.

```bash
pip install -r requirements-vllm.txt
python scripts/run_vllm.py \
  --input examples/example.json \
  --output outputs/vllm_outputs.json \
  --model-path Qwen/Qwen2.5-72B-Instruct \
  --tensor-parallel-size 8 \
  --limit 1
```

### Clean an OpenReview export into review/rebuttal conversations

```bash
python scripts/clean_openreview.py \
  --input examples/openreview_comments_minimal.json \
  --output outputs/openreview_conversations.json \
  --forum-id forum_example \
  --print-text
```

For your own data, replace `examples/openreview_comments_minimal.json` with an OpenReview comments export.

### Analysis dependencies

```bash
pip install -r requirements-analysis.txt
```

The analysis scripts currently operate on the JSONL/XLSX artifacts under `<HF_DATASET_REPO>/data/annotation_scores/`. See `docs/REPRODUCIBILITY.md` for known gaps and smoke tests.

## Documentation map

- `docs/GETTING_STARTED.md`: shortest path for a new user.
- `docs/DATA.md`: data contents, provenance TODOs, and redistribution warnings.
- `docs/REPRODUCIBILITY.md`: environment setup, smoke tests, and reproduction notes.
- `MANIFEST.md`: file inventory and release TODOs.
- `CITATION.bib` / `CITATION.cff`: citation metadata.

## Release status

This folder is a cleaned release candidate. The original raw folder contained local environments, temporary notebooks, zip archives, hard-coded local paths, and API-key scripts; those were excluded or rewritten. Runner scripts use environment variables for keys and CLI arguments for paths/models.

Before a public archival release, confirm:

1. Replace `LICENSE_TODO.md` with the intended code license.
2. Confirm redistribution rights and usage constraints for all data/prompt/paper artifacts.
3. Replace `<REPO_URL>` / `<REPO_NAME>` placeholders after creating the public repository.
4. Decide whether the 267 MB data payload should stay in Git, move to Git LFS, or be hosted on Hugging Face / Zenodo with checksums.

## Contact

For questions about the paper or release, open a GitHub issue in the public repository once available.
