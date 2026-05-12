# Where Do LLMs Go Wrong? Diagnosing Automated Peer Review

[![CI](https://github.com/PKU-ONELab/where-do-llms-go-wrong/actions/workflows/smoke-test.yml/badge.svg)](https://github.com/PKU-ONELab/where-do-llms-go-wrong/actions/workflows/smoke-test.yml)
[![PyPI](https://img.shields.io/pypi/v/ai-reviewer-diagnostics.svg)](https://pypi.org/project/ai-reviewer-diagnostics/)
[![Paper](https://img.shields.io/badge/CIKM-2025-blue)](https://doi.org/10.1145/3746252.3761274)
[![Dataset](https://img.shields.io/badge/Hugging%20Face-Dataset-yellow)](https://huggingface.co/datasets/PKU-ONELab/ai-reviewer-diagnostic-data)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Official repository for the CIKM 2025 paper **“Where Do LLMs Go Wrong? Diagnosing Automated Peer Review via Aspect-Guided Multi-Level Perturbation.”**

Use this repo to evaluate automated peer-review systems on paired original/perturbed inputs and generate aspect-level diagnostic reports. The data lives on [Hugging Face](https://huggingface.co/datasets/PKU-ONELab/ai-reviewer-diagnostic-data); the installable reporting CLI lives on [PyPI](https://pypi.org/project/ai-reviewer-diagnostics/).

![AI reviewer diagnostics workflow](https://huggingface.co/datasets/PKU-ONELab/ai-reviewer-diagnostic-data/resolve/main/assets/teaser.png)

## Start fast

Install the CLI and run the bundled demo. No dataset, API key, GPU, or model download is needed.

```bash
python -m pip install ai-reviewer-diagnostics
ai-reviewer-diagnostics --demo --output-md outputs/demo_diagnostic_report.md
```

Expected output:

```text
Compared 1 condition pair(s).
Wrote outputs/demo_diagnostic_report.md
```

For a repo checkout:

```bash
git clone https://github.com/PKU-ONELab/where-do-llms-go-wrong
cd where-do-llms-go-wrong
make quickstart
make demo-report
```

## What is included

| Need | Use |
| --- | --- |
| Diagnostic report CLI | `ai-reviewer-diagnostics` / `ai-reviewer-report` |
| Main paired perturbation data | [HF dataset](https://huggingface.co/datasets/PKU-ONELab/ai-reviewer-diagnostic-data) → `data/content_pairs/*.jsonl` |
| Released score artifacts | HF dataset → `data/annotation_scores/*.jsonl` |
| Prompt templates | [`prompts/`](prompts/) |
| API / local inference wrappers | [`scripts/`](scripts/) |
| Paper-analysis scripts | [`analysis/`](analysis/) |
| Reproduction notes | [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md) |

## Use the dataset

The primary dataset is before/after perturbation pairs:

```python
from datasets import load_dataset
pairs = load_dataset("PKU-ONELab/ai-reviewer-diagnostic-data", split="train")
print(pairs[0].keys())  # id, source, aspect, content_before, content_after
```

Download the full HF repo when you need manifests or score artifacts:

```bash
hf download PKU-ONELab/ai-reviewer-diagnostic-data   --repo-type dataset   --local-dir ai-reviewer-diagnostic-data
python scripts/summarize_release_data.py --data-dir ai-reviewer-diagnostic-data/data
```

`content_pairs/` is the canonical benchmark surface. `annotation_scores/` is for reproducing or auditing the paper’s released scoring outputs. The duplicated perturbed-only view is intentionally excluded because `content_pairs.content_after` already contains it.

## Evaluate your own review system

Export baseline and perturbed outputs as JSONL with shared `id` values and any score/decision fields:

```json
{"id":"paper_001","overall_score":8,"soundness_score":4,"final_decision":"Accept as Poster"}
```

Then run:

```bash
ai-reviewer-diagnostics   --baseline outputs/my_system_baseline.jsonl   --perturbed outputs/my_system_soundness_perturbed.jsonl   --condition paper/soundness   --output-md reports/my_system_soundness_report.md   --output-json reports/my_system_soundness_report.json
```

Directory mode works for released score files:

```bash
ai-reviewer-diagnostics   --scores-dir ai-reviewer-diagnostic-data/data/annotation_scores   --output-md reports/released_scores_report.md
```

The report summarizes score deltas, decision-change rates, and top decision transitions. See [`docs/INTEGRATIONS.md`](docs/INTEGRATIONS.md) for schemas and custom fields.

## Development commands

```bash
uv sync                    # default runtime deps
uv sync --extra analysis   # analysis deps
uv sync --extra vllm       # optional local GPU inference deps
uv run make smoke-test     # API-free checks
make clean                 # remove generated outputs
```

Inference wrappers:

```bash
python scripts/run_openrouter.py --input examples/example.json --output outputs/openrouter.jsonl --model <model> --api-key-env OPENROUTER_API_KEY
python scripts/run_gemini.py --input examples/example.json --output outputs/gemini.jsonl --model gemini-2.0-flash
python scripts/run_vllm.py --input examples/example.json --output outputs/vllm.jsonl --model-path <hf-or-local-model>
```

## Repository map

```text
ai_reviewer_diagnostics/  # pip package and diagnostic report CLI
scripts/                  # inference, preprocessing, quickstart, data-summary CLIs
analysis/                 # scripts for released score artifacts
examples/                 # tiny fixtures for demos/tests
prompts/                  # prompt templates
data/README.md            # pointer to HF dataset
docs/                     # data, integrations, reproducibility
paper/README.md           # DOI / citation pointer
```

## Citation

```bibtex
@inproceedings{li2025where,
  title     = {Where Do LLMs Go Wrong? Diagnosing Automated Peer Review via Aspect-Guided Multi-Level Perturbation},
  author    = {Li, Jiatao and Li, Yanheng and Hu, Xinyu and Gao, Mingqi and Wan, Xiaojun},
  booktitle = {Proceedings of the 34th ACM International Conference on Information and Knowledge Management (CIKM '25)},
  year      = {2025},
  publisher = {ACM},
  doi       = {10.1145/3746252.3761274},
  url       = {https://doi.org/10.1145/3746252.3761274}
}
```

Docs: [`GETTING_STARTED`](docs/GETTING_STARTED.md), [`DATA`](docs/DATA.md), [`REPRODUCIBILITY`](docs/REPRODUCIBILITY.md), [`INTEGRATIONS`](docs/INTEGRATIONS.md), [`CONTRIBUTING`](CONTRIBUTING.md).
