# Contributing

Thanks for helping make `ai-reviewer-diagnostics` useful beyond the original paper artifact.

This repository has two goals:

1. provide the official code, prompts, and reproducibility notes for the CIKM 2025 paper; and
2. provide a lightweight community tool for diagnosing automated peer-review systems on paired baseline/perturbed inputs.

## Good first contributions

- Add an example integration for a new automated review system.
- Improve JSONL schema validation or error messages.
- Add a report metric that is useful across systems, not tied to one private setup.
- Add documentation for a common workflow or failure mode.
- Report a dataset/file-naming issue with a minimal reproducer.

## Local setup

```bash
git clone https://github.com/PKU-ONELab/where-do-llms-go-wrong
cd where-do-llms-go-wrong
python -m pip install -e .
ai-reviewer-diagnostics --demo --output-md outputs/demo_diagnostic_report.md
```

For the full repository smoke test:

```bash
uv sync
uv run make smoke-test
```

The smoke test is API-free. It should not require GPUs, model downloads, private data, or provider keys.

## Development checks

Before opening a pull request, run:

```bash
git diff --check
python -m compileall -q ai_reviewer_diagnostics scripts analysis
python -m pip install -e . --no-deps
ai-reviewer-diagnostics --demo --output-md outputs/demo_diagnostic_report.md
make smoke-test
```

If you change package data, also check that the wheel includes the bundled demo fixtures:

```bash
uv build
python - <<'PY'
from pathlib import Path
import zipfile
wheel = next(Path('dist').glob('*.whl'))
with zipfile.ZipFile(wheel) as z:
    names = set(z.namelist())
required = {
    'ai_reviewer_diagnostics/report.py',
    'ai_reviewer_diagnostics/examples/system_outputs_baseline.jsonl',
    'ai_reviewer_diagnostics/examples/system_outputs_perturbed_soundness.jsonl',
}
missing = required - names
if missing:
    raise SystemExit(f'missing from wheel: {sorted(missing)}')
print('wheel package-data check OK:', wheel.name)
PY
```

Clean generated files before committing:

```bash
make clean
rm -rf build dist *.egg-info
```

## JSONL contract for tool integrations

The diagnostic CLI compares baseline and perturbed outputs by shared `id` values. A minimal row looks like:

```json
{"id":"paper_001","overall_score":8,"soundness_score":4,"final_decision":"Accept as Poster"}
```

Default score fields:

- `overall_score`
- `contribution_score`
- `soundness_score`
- `presentation_score`

Default decision field:

- `final_decision`

Use `--score-fields` and `--decision-field` for custom systems.

## Pull request guidelines

- Keep the default install lightweight. Do not add heavy ML/GPU packages to core dependencies.
- Keep optional dependencies lazy and documented.
- Do not add API keys, `.env` files, checkpoints, generated outputs, or private/local paths.
- Do not vendor whole upstream model/detector repositories.
- If a change affects public commands, update `README.md`, `docs/GETTING_STARTED.md`, `scripts/README.md`, and `MANIFEST.md` together.
- If a change affects dataset layout, update the Hugging Face dataset card and manifest generation notes.

## Citation

If you use this toolkit or dataset in a paper, cite the CIKM 2025 paper using `CITATION.bib` or `CITATION.cff`.
