---
name: Bug report
about: Report a reproducible problem with the CLI, docs, examples, or dataset workflow
title: "[Bug] "
labels: bug
assignees: ""
---

## What happened?

Describe the problem and what you expected instead.

## Minimal command

```bash
ai-reviewer-diagnostics --demo --output-md outputs/demo_diagnostic_report.md
```

Replace with the smallest command that reproduces your issue.

## Input shape

If the issue involves JSONL outputs, paste 1-3 anonymized rows:

```json
{"id":"paper_001","overall_score":8,"soundness_score":4,"final_decision":"Accept as Poster"}
```

## Environment

- OS:
- Python version:
- Install method: `pip install`, `pip install -e .`, `uv sync`, other:
- Package/repo version or commit:

## Logs / traceback

```text
paste logs here
```

## Checklist

- [ ] I tried `ai-reviewer-diagnostics --demo --output-md outputs/demo_diagnostic_report.md`.
- [ ] I removed private data, API keys, and reviewer-identifying information from this issue.
