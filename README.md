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

Tested with Python 3.11; use Python 3.10 or newer.

```bash
git clone https://github.com/JiataoLi/where-do-llms-go-wrong
cd where-do-llms-go-wrong
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-core.txt
```

### 2. Validate the example input without making an API call

```bash
python scripts/run_openrouter.py \
  --input examples/example.json \
  --output outputs/validate_openrouter.jsonl \
  --model mistralai/mistral-small-3.1-24b-instruct \
  --validate-only
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

### 3. Download and inspect the companion Hugging Face dataset

```bash
hf download jiataoli/ai-reviewer-diagnostic-data \
  --repo-type dataset \
  --local-dir ai-reviewer-diagnostic-data
python scripts/summarize_release_data.py --data-dir ai-reviewer-diagnostic-data/data
```

Expected output starts like this:

```text
Data directory: ai-reviewer-diagnostic-data/data
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
data/README.md        # explains the external Hugging Face data repo
Hugging Face dataset  # https://huggingface.co/datasets/jiataoli/ai-reviewer-diagnostic-data
  data/annotation_scores/   # scored model outputs, tables, figures, transition matrices
  data/perturbed_contents/  # perturbed paper/review/rebuttal JSONL artifacts
paper/README.md       # paper citation and official ACM DOI/PDF links
docs/                 # data/reproducibility/getting-started notes
```

For a fuller inventory, see `MANIFEST.md`.


## Data hosting

GitHub is kept lightweight for code, prompts, examples, docs, and citation metadata. Data artifacts are hosted separately on Hugging Face:

```text
https://huggingface.co/datasets/jiataoli/ai-reviewer-diagnostic-data
```

The dataset repo includes a dataset card, Git LFS patterns, a checksum manifest, and the `data/` artifact directory.

## Common usage patterns

### OpenAI-compatible / OpenRouter inference

```bash
export OPENROUTER_API_KEY=your_key_here
python scripts/run_openrouter.py \
  --input examples/example.json \
  --output outputs/model_outputs.jsonl \
  --model mistralai/mistral-small-3.1-24b-instruct \
  --base-url https://openrouter.ai/api/v1 \
  --api-key-env OPENROUTER_API_KEY \
  --workers 1
```

### Gemini inference

```bash
pip install -r requirements-core.txt
export GEMINI_API_KEY=your_key_here
python scripts/run_gemini.py \
  --input examples/example.json \
  --output outputs/gemini_outputs.jsonl \
  --model gemini-2.0-flash \
  --workers 1
```

### Optional local vLLM inference

`vllm` is intentionally kept out of the default install because it depends on your CUDA/PyTorch/GPU setup.

```bash
pip install -r requirements-vllm.txt
python scripts/run_vllm.py \
  --input examples/example.json \
  --output outputs/vllm_outputs.jsonl \
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

The analysis scripts operate on JSONL/XLSX artifacts after downloading the Hugging Face dataset locally. See `analysis/README.md` and `docs/REPRODUCIBILITY.md`.

## Documentation map

- `docs/GETTING_STARTED.md`: shortest path for a new user.
- `docs/DATA.md`: data contents, provenance notes, and redistribution warnings.
- `docs/REPRODUCIBILITY.md`: environment setup, smoke tests, and reproduction notes.
- `MANIFEST.md`: file inventory and release notes.
- `CITATION.bib` / `CITATION.cff`: citation metadata.

## Release status

This is a cleaned public-release candidate. The original raw folder contained local environments, temporary notebooks, zip archives, hard-coded local paths, and API-key scripts; those were excluded or rewritten. Runner scripts use environment variables for keys and CLI arguments for paths/models.

Code is MIT licensed in `LICENSE`. Data redistribution terms still need final rights confirmation before the Hugging Face dataset is made public.

## Contact

For questions about the paper or release, open a GitHub issue in the public repository once available.
